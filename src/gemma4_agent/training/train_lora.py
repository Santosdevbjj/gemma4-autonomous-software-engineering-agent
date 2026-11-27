"""Explicit LoRA SFT runner for curated issue->patch JSONL pairs.

This starter recipe must be run and evaluated against the exact model and harness
before it can be treated as a competition-ready training configuration.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class EncodedExample:
    input_ids: list[int]
    labels: list[int]


def load_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row: Any = json.loads(line)
        if not isinstance(row, dict) or not row.get("prompt") or not row.get("completion"):
            raise ValueError(f"Invalid prompt/completion on line {index}")
        rows.append({"prompt": str(row["prompt"]), "completion": str(row["completion"])})
    if not rows:
        raise ValueError("Training file contains no examples")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model", required=True, help="Exact local base model ID/path")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=8192)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--alpha", type=int, default=32)
    parser.add_argument(
        "--target-modules", default="q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"
    )
    args = parser.parse_args()

    try:
        import torch
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
    except ImportError as exc:
        raise SystemExit(
            "Install optional training dependencies with: pip install -e '.[training]'"
        ) from exc

    if not torch.cuda.is_available():
        raise SystemExit(
            "CUDA is required for this starter recipe; no model was loaded or downloaded."
        )
    rows = load_rows(args.data)
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    examples: list[EncodedExample] = []
    for row in rows:
        user = {"role": "user", "content": row["prompt"]}
        assistant = {"role": "assistant", "content": row["completion"]}
        prefix = tokenizer.apply_chat_template([user], tokenize=True, add_generation_prompt=True)
        full = tokenizer.apply_chat_template(
            [user, assistant], tokenize=True, add_generation_prompt=False
        )
        if full[: len(prefix)] != prefix:
            raise ValueError("Chat template prompt is not a token prefix of the full conversation")
        full = full[: args.max_length]
        labels = [-100] * min(len(prefix), len(full)) + full[len(prefix) :]
        if any(token != -100 for token in labels):
            examples.append(EncodedExample(full, labels))
    if not examples:
        raise ValueError("No examples fit max-length with completion tokens")

    class Dataset(torch.utils.data.Dataset):
        def __len__(self) -> int:
            return len(examples)

        def __getitem__(self, index: int) -> dict[str, list[int]]:
            item = examples[index]
            return {"input_ids": item.input_ids, "labels": item.labels}

    def collate(items: list[dict[str, list[int]]]) -> dict[str, Any]:
        ids = [torch.tensor(item["input_ids"], dtype=torch.long) for item in items]
        labels = [torch.tensor(item["labels"], dtype=torch.long) for item in items]
        input_ids = torch.nn.utils.rnn.pad_sequence(
            ids, batch_first=True, padding_value=tokenizer.pad_token_id
        )
        target = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True, padding_value=-100)
        lengths = torch.tensor([len(item["input_ids"]) for item in items], dtype=torch.long)
        attention_mask = torch.arange(input_ids.shape[1]).unsqueeze(0) < lengths.unsqueeze(1)
        return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": target}

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        local_files_only=True,
        device_map="auto",
    )
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model = get_peft_model(
        model,
        LoraConfig(
            r=args.rank,
            lora_alpha=args.alpha,
            lora_dropout=0.05,
            target_modules=[
                item.strip() for item in args.target_modules.split(",") if item.strip()
            ],
            task_type="CAUSAL_LM",
        ),
    )
    training = TrainingArguments(
        output_dir=str(args.output),
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        logging_steps=1,
        save_strategy="epoch",
        report_to="none",
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        gradient_checkpointing=True,
        remove_unused_columns=False,
    )
    trainer = Trainer(model=model, args=training, train_dataset=Dataset(), data_collator=collate)
    trainer.train()
    args.output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output, safe_serialization=True)
    tokenizer.save_pretrained(args.output)
    print(f"Saved adapter candidate to {args.output}; evaluate it before promotion.")


if __name__ == "__main__":
    main()
