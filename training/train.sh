#!/bin/bash
# LoRA fine-tuning: Qwen2.5-Coder-7B on Rhino3D dataset
# 2 epochs (~9,108 iters), ~1.2 hours on M2 Max
# Previous run NaN'd at epoch 3 with lr=2e-5. Reduced to 2 epochs + lr=1e-5.
# Usage: ./training/train.sh

set -e

cd "$(dirname "$0")/.."

VENV=training/venv/bin/python
MODEL=training/models/codeqwen-7b-4bit
DATA=training/data
ADAPTER=training/adapters/rhino-lora

echo "Starting LoRA training..."
echo "Model:    $MODEL"
echo "Data:     $DATA"
echo "Adapter:  $ADAPTER"
echo "Iters:    9108 (2 epochs)"
echo ""

$VENV -m mlx_lm lora \
  --model "$MODEL" \
  --train \
  --data "$DATA" \
  --batch-size 1 \
  --num-layers 16 \
  --iters 9108 \
  --learning-rate 1e-5 \
  --adapter-path "$ADAPTER" \
  --val-batches 10 \
  --steps-per-eval 500 \
  --steps-per-report 100 \
  --save-every 1000

echo ""
echo "Training complete! Adapter saved to $ADAPTER"
