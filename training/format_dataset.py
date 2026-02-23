#!/usr/bin/env python3
"""Phase 1 of TODO5: Format pairs.jsonl → chat format, split train/eval, sanity check."""

import json
import random
import ast
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent          # training/
DATA_DIR = ROOT / "data"
PAIRS = ROOT.parent / "data" / "processed" / "pairs.jsonl"

SYSTEM_PROMPT = (
    "You are an expert Rhino3D Python programmer. "
    "Write clean, working scripts using rhinoscriptsyntax and RhinoCommon. "
    "Include all necessary imports. Only output code, no explanations unless asked."
)

RHINO_MARKERS = [
    "rhinoscriptsyntax", "Rhino.", "rhino3dm",
    "scriptcontext", "ghpythonlib", "Grasshopper",
]

SEED = 42
EVAL_FRAC = 0.10


def to_chat(entry: dict) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": entry["instruction"]},
            {"role": "assistant", "content": entry["code"]},
        ]
    }


def has_rhino_import(code: str) -> bool:
    return any(m in code for m in RHINO_MARKERS)


def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 chars per token."""
    return len(text) // 4


def main():
    # --- Load ---
    entries = []
    with open(PAIRS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    print(f"Loaded {len(entries)} pairs from {PAIRS.name}")

    # --- Convert to chat format ---
    chat_entries = [to_chat(e) for e in entries]

    # --- Save full chat-formatted file ---
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    chat_path = DATA_DIR / "chat_formatted.jsonl"
    with open(chat_path, "w", encoding="utf-8") as f:
        for ce in chat_entries:
            f.write(json.dumps(ce, ensure_ascii=False) + "\n")
    print(f"Wrote {len(chat_entries)} → {chat_path.name}")

    # --- Shuffle & split ---
    random.seed(SEED)
    indices = list(range(len(chat_entries)))
    random.shuffle(indices)

    split = int(len(indices) * (1 - EVAL_FRAC))
    train_idx = indices[:split]
    eval_idx = indices[split:]

    train_entries = [chat_entries[i] for i in train_idx]
    eval_entries = [chat_entries[i] for i in eval_idx]

    # MLX-lm expects files named train.jsonl, valid.jsonl, and test.jsonl
    train_path = DATA_DIR / "train.jsonl"
    valid_path = DATA_DIR / "valid.jsonl"

    for path, data in [(train_path, train_entries), (valid_path, eval_entries)]:
        with open(path, "w", encoding="utf-8") as f:
            for ce in data:
                f.write(json.dumps(ce, ensure_ascii=False) + "\n")
    print(f"Train: {len(train_entries)} → {train_path.name}")
    print(f"Eval:  {len(eval_entries)} → {valid_path.name}")

    # --- Sanity checks ---
    print("\n" + "=" * 60)
    print("SANITY CHECKS")
    print("=" * 60)

    # Check 1: no empty fields
    empty_inst = sum(1 for e in entries if not e["instruction"].strip())
    empty_code = sum(1 for e in entries if not e["code"].strip())
    print(f"Empty instructions: {empty_inst}")
    print(f"Empty code fields:  {empty_code}")

    # Check 2: Rhino imports
    no_import = sum(1 for e in entries if not has_rhino_import(e["code"]))
    print(f"Missing Rhino import: {no_import} ({100*no_import/len(entries):.1f}%)")

    # Check 3: no exact dupes between train and eval
    def msg_key(ce):
        return (ce["messages"][1]["content"], ce["messages"][2]["content"])

    train_keys = set(msg_key(e) for e in train_entries)
    eval_keys = set(msg_key(e) for e in eval_entries)
    overlap = train_keys & eval_keys
    print(f"Train-eval overlap:  {len(overlap)} duplicates")

    # Check 4: lengths and token estimates
    inst_lens = [len(e["instruction"]) for e in entries]
    code_lens = [len(e["code"]) for e in entries]
    total_tokens = sum(estimate_tokens(e["instruction"] + e["code"]) for e in entries)
    total_tokens += len(entries) * estimate_tokens(SYSTEM_PROMPT)

    print(f"\nAvg instruction length: {sum(inst_lens)/len(inst_lens):.0f} chars")
    print(f"Avg code length:        {sum(code_lens)/len(code_lens):.0f} chars")
    print(f"Total token estimate:   {total_tokens:,}")
    print(f"Avg tokens per example: {total_tokens//len(entries):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
