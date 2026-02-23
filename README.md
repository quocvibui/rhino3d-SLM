# Rhino3d-SLM

Fine-tuned Qwen2.5-Coder-7B for Rhino3D Python scripting, served locally on Apple Silicon with live code execution in Rhino 8.

## Why Fine-Tune?

The base Qwen2.5-Coder-7B is a strong general code model, but it doesn't know Rhino's APIs. On 10 held-out Rhino scripting tasks:

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-----------|------------|-------|
| Avg code lines | 11.9 | 8.2 | -3.7 (more concise) |
| Avg code chars | 427 | 258 | -40% less bloat |

Both pass syntax checks and include Rhino imports — the difference is whether the code actually *works*:

- **Base model hallucinates APIs** — invents `Rhino.Commands.Command.AddPoint()`, `rs.filter.surface`, `rg.PipeSurface.Create()` — none of these exist
- **Fine-tuned uses correct APIs** — `rs.CurveAreaCentroid()`, `rs.AddPipe()`, `rs.GetObject("...", 8)` with the right filter constants
- **Base model over-engineers** — wraps simple tasks in unnecessary functions and verbose comments
- **Fine-tuned matches reference style** — several outputs are near-identical to the reference solutions

Example — *"How do I find the centroid of a closed curve?"*:

```python
# BASE MODEL — wrong (averages control points, not area centroid)
def find_centroid(curve_id):
    points = rs.CurvePoints(curve_id)
    centroid = [0, 0, 0]
    for point in points:
        centroid[0] += point[0]
        centroid[1] += point[1]
        centroid[2] += point[2]
    centroid[0] /= len(points)
    return centroid

# FINE-TUNED — correct, concise
crv = rs.GetObject('Select closed curve', 4)
if crv and rs.IsCurveClosed(crv):
    centroid = rs.CurveAreaCentroid(crv)
    if centroid:
        rs.AddPoint(centroid[0])
```

The base model doesn't know `rs.CurveAreaCentroid` exists, so it reinvents centroid computation incorrectly. The fine-tuned model knows the API and uses it.

## Architecture

```
rhino_coder.py (interactive REPL)
    ↓ HTTP POST (OpenAI-compatible API)
mlx_lm.server (localhost:8080, fine-tuned Qwen2.5-Coder-7B)
    ↓ generates Python code
rhino_coder.py (extract code + auto-retry on error)
    ↓ JSON over TCP (localhost:54321)
server.py in Rhino 8 → exec(code) with rs, Rhino, System, math
```

## Quick Start

### Prerequisites

- macOS with Apple Silicon (M-series) — required for MLX
- Rhino 8
- Python 3.10+

### 1. Start the Rhino listener

First, follow the set up in my [rhino3d-mcp](https://github.com/quocvibui/rhino3d-mcp) project.
Open Rhino 8 and run `server.py` via Rhino's Python editor (`EditPythonScript`). This starts the TCP listener on port 54321.

### 2. Serve the model

```bash
./serve.sh              # fused model (default)
./serve.sh --adapter    # base model + LoRA adapter (less RAM)
```

Serves an OpenAI-compatible API on `localhost:8080`.

### 3. Run the CLI

```bash
python rhino_coder.py
```

REPL commands: `/quit` `/clear` `/run <code>` `/retry` `/history`

The CLI sends your prompt to the model, extracts the generated code, executes it in Rhino, and auto-retries up to 3 times on errors with increasing temperature.

## Training

Fine-tunes [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) (4-bit) using LoRA via [MLX-LM](https://github.com/ml-explore/mlx-examples).

```bash
# Set up training venv
cd training
python3.11 -m venv venv
source venv/bin/activate
pip install mlx-lm

# Format dataset (from data/processed/pairs.jsonl)
python format_dataset.py

# Train (2 epochs, ~9,108 iters, ~1.2h on M2 Max)
./train.sh
```

| Param | Value |
|-------|-------|
| Base model | Qwen2.5-Coder-7B-Instruct (4-bit) |
| Method | LoRA (rank 8, 16/28 layers) |
| Batch size | 1 |
| Learning rate | 1e-5 |
| Sequence length | 2,048 tokens |
| Iterations | 13,662 |
| Val loss | 0.184 |
| Training time | ~1.2h on M2 Max |
| Fused model size | 14 GB |
| Adapter size | 660 MB |

## Dataset

5,060 instruction-code pairs for Rhino3D Python scripting, sourced from:

| Source | Count |
|--------|-------|
| RhinoCommon API docs | 1,355 |
| RhinoScriptSyntax source | 926 |
| Official samples | 93 |
| Synthetic generation | 187 |
| Backlabeled GitHub | 1 |

## Data Pipeline

```bash
# Scrape sources
python data/scripts/parse_docs.py
python scripts/scrape_github.py
python scripts/scrape_discourse.py

# Generate synthetic data
python scripts/generate_synthetic_v2.py

# Clean and merge
python data/scripts/clean_dataset.py
python data/scripts/merge_and_validate.py

# Format for training
python training/format_dataset.py
```

## Ports

| Service | Port |
|---------|------|
| Model server (mlx_lm) | 8080 |
| Rhino TCP listener | 54321 |
