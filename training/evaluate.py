#!/usr/bin/env python3
"""Phase 4.1: Run eval prompts through the fine-tuned model (with LoRA adapter).
Uses the same 10 samples as baseline for direct comparison.
Saves outputs to training/results/finetuned_outputs.jsonl
"""

import json
import random
from pathlib import Path
from mlx_lm import load, generate

ROOT = Path(__file__).resolve().parent
MODEL_PATH = str(ROOT / "models" / "codeqwen-7b-4bit")
ADAPTER_PATH = str(ROOT / "adapters" / "rhino-lora")
EVAL_PATH = ROOT / "data" / "valid.jsonl"
OUTPUT_DIR = ROOT / "results"
OUTPUT_PATH = OUTPUT_DIR / "finetuned_outputs.jsonl"

SYSTEM_PROMPT = (
    "You are an expert Rhino3D Python programmer. "
    "Write clean, working scripts using rhinoscriptsyntax and RhinoCommon. "
    "Include all necessary imports. Only output code, no explanations unless asked."
)

N_SAMPLES = 10
SEED = 42
MAX_TOKENS = 1024


def clean_output(text: str) -> str:
    """Strip trailing garbage after the first <|im_end|> or repetition."""
    # Cut at first <|im_end|> token
    if "<|im_end|>" in text:
        text = text[:text.index("<|im_end|>")]
    # Cut at first <|endoftext|> token
    if "<|endoftext|>" in text:
        text = text[:text.index("<|endoftext|>")]
    return text.rstrip()


def main():
    # Same seed & sampling as baseline for direct comparison
    random.seed(SEED)
    with open(EVAL_PATH) as f:
        eval_data = [json.loads(line) for line in f if line.strip()]

    samples = random.sample(eval_data, min(N_SAMPLES, len(eval_data)))

    print(f"Loading model from {MODEL_PATH}")
    print(f"Loading adapter from {ADAPTER_PATH}")
    model, tokenizer = load(MODEL_PATH, adapter_path=ADAPTER_PATH)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for i, sample in enumerate(samples):
        instruction = sample["messages"][1]["content"]
        reference = sample["messages"][2]["content"]

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

        output = clean_output(output)

        result = {
            "instruction": instruction,
            "reference": reference,
            "finetuned_output": output,
        }
        results.append(result)
        print(f"  Output length: {len(output)} chars")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nSaved {len(results)} fine-tuned outputs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
