"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gemma4_agent.data.audit import audit_dataset
from gemma4_agent.data.trajectories import prepare_sft
from gemma4_agent.evaluation.metrics import score_predictions
from gemma4_agent.packaging.archive import build_archive


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="gemma4-agent")
    sub = root.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Audit task, graph and embedding metadata")
    audit.add_argument("--tasks", type=Path, required=True)
    audit.add_argument("--graphs", type=Path)
    audit.add_argument("--embeddings", type=Path)
    audit.add_argument("--output", type=Path, required=True)

    sft = sub.add_parser("prepare-sft", help="Prepare public issue/patch pairs")
    sft.add_argument("--tasks", type=Path, required=True)
    sft.add_argument("--output", type=Path, required=True)
    sft.add_argument("--split", choices=("train",), default="train")
    sft.add_argument("--seed", type=int, default=17)
    sft.add_argument("--max-examples", type=int)

    score = sub.add_parser("score", help="Aggregate a prediction JSONL file")
    score.add_argument("--predictions", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)

    package = sub.add_parser("package", help="Create a safe submission ZIP")
    package.add_argument("--source", type=Path, required=True)
    package.add_argument("--output", type=Path, required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "audit":
        result = audit_dataset(args.tasks, args.graphs, args.embeddings)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    elif args.command == "prepare-sft":
        count = prepare_sft(args.tasks, args.output, args.seed, args.max_examples)
        print(f"Wrote {count} examples to {args.output}")
    elif args.command == "score":
        result = score_predictions(args.predictions)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    elif args.command == "package":
        build_archive(args.source, args.output)
        print(f"Created {args.output}")


if __name__ == "__main__":
    main()
