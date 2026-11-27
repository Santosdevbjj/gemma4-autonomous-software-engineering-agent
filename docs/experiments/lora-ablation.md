# LoRA ablation

**Status:** planned, not run.

First establish the sample-agent baseline. Then compare no adapter with a validated adapter trained only on permitted public training examples. Record base checkpoint hash, quantization, PEFT/Transformers versions, target module names, rank, alpha, dropout, sequence length, optimizer, steps, seed and hardware. Verify that the adapter loads in the Kaggle harness before running a benchmark. Do not claim improved capability from training loss alone.
