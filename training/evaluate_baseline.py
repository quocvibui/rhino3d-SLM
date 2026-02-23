#!/usr/bin/env python3
"""Phase 2.3: Run 10 eval prompts through the base model (no fine-tuning).
Saves outputs to training/results/baseline_outputs.jsonl
"""

import json
import random
from pathlib import Path
from mlx_lm import load, generate

ROOT = Path(__file__).resolve().parent
MODEL_PATH = str(ROOT / "models" / "codeqwen-7b-4bit")
EVAL_PATH = ROOT / "data" / "valid.jsonl"
OUTPUT_DIR = ROOT / "results"
OUTPUT_PATH = OUTPUT_DIR / "baseline_outputs.jsonl"

SYSTEM_PROMPT = (
    "You are an expert Rhino3D Python programmer. "
    "Write clean, working scripts using rhinoscriptsyntax and RhinoCommon. "
    "Include all necessary imports. Only output code, no explanations unless asked."
)

N_SAMPLES = 10
SEED = 42
MAX_TOKENS = 1024


def main():
    # Pick 10 diverse examples from eval set
    random.seed(SEED)
    with open(EVAL_PATH) as f:
        eval_data = [json.loads(line) for line in f if line.strip()]

    samples = random.sample(eval_data, min(N_SAMPLES, len(eval_data)))

    print(f"Loading model from {MODEL_PATH} ...")
    model, tokenizer = load(MODEL_PATH)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for i, sample in enumerate(samples):
        instruction = sample["messages"][1]["content"]
        reference = sample["messages"][2]["content"]

        # Build chat prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": instruction},
        ]
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        print(f"\n[{i+1}/{N_SAMPLES}] {instruction[:80]}...")
        output = generate(
            model, tokenizer, prompt=prompt, max_tokens=MAX_TOKENS, verbose=False
        )

        result = {
            "instruction": instruction,
            "reference": reference,
            "baseline_output": output,
        }
        results.append(result)
        print(f"  Output length: {len(output)} chars")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nSaved {len(results)} baseline outputs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
