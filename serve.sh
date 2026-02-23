#!/bin/bash
# Serve the fine-tuned Rhino coder model via mlx_lm.server
# Provides an OpenAI-compatible API on localhost:8080
#
# Usage: ./serve.sh [--adapter]
#   --adapter  Use base model + adapter (less RAM, same quality)
#   (default)  Use fused model

set -e
cd "$(dirname "$0")"

VENV=training/venv/bin/python
FUSED_MODEL=training/models/rhino-coder-fused
BASE_MODEL=training/models/codeqwen-7b-4bit
ADAPTER=training/adapters/rhino-lora
PORT=8080

if [ "$1" = "--adapter" ]; then
    echo "Serving base model + LoRA adapter on http://localhost:$PORT"
    echo "Model:   $BASE_MODEL"
    echo "Adapter: $ADAPTER"
    echo ""
    $VENV -m mlx_lm server \
        --model "$BASE_MODEL" \
        --adapter-path "$ADAPTER" \
        --port $PORT
else
    echo "Serving fused model on http://localhost:$PORT"
    echo "Model: $FUSED_MODEL"
    echo ""
    $VENV -m mlx_lm server \
        --model "$FUSED_MODEL" \
        --port $PORT
fi
