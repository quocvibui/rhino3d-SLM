#!/usr/bin/env python3
"""
rhino_coder — Local Rhino3D code generation & execution CLI.

Connects a locally-served fine-tuned model (via mlx_lm.server) to Rhino 8
through the rhino-mcp TCP socket. Auto-executes generated code and
automatically retries on errors.

Usage:
    1. Start the model server:  ./serve.sh
    2. Start Rhino listener:    Load server.py in Rhino 8
    3. Run this CLI:            python rhino_coder.py

Commands:
    /quit, /exit   Exit the REPL
    /clear         Clear conversation history
    /run <code>    Send Python code directly to Rhino (skip model)
    /retry         Regenerate last response
    /history       Show conversation history
"""

import json
import re
import socket
import sys
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_URL = "http://localhost:8080/v1/chat/completions"
# Must match the model ID reported by mlx_lm.server (/v1/models)
MODEL_NAME = "training/models/rhino-coder-fused"

RHINO_HOST = "localhost"
RHINO_PORT = 54321
SOCKET_TIMEOUT = 30
RECV_CHUNK_SIZE = 8192

SYSTEM_PROMPT = (
    "You are an expert Rhino3D Python programmer. "
    "Write clean, working scripts using rhinoscriptsyntax and RhinoCommon. "
    "Include all necessary imports. Only output code, no explanations unless asked."
)

MAX_TOKENS = 2048
TEMPERATURE = 0.1
MAX_RETRIES = 3  # auto-retry limit on execution errors

# ---------------------------------------------------------------------------
# Rhino TCP communication (same protocol as rhino-mcp/tools/utils.py)
# ---------------------------------------------------------------------------

def send_to_rhino(command_type: str, params: dict | None = None) -> dict:
    """Send a JSON command to Rhino's TCP socket and return the response."""
    if params is None:
        params = {}

    command = {"type": command_type, "params": params}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(SOCKET_TIMEOUT)
        sock.connect((RHINO_HOST, RHINO_PORT))
        sock.sendall(json.dumps(command).encode("utf-8"))

        chunks = []
        while True:
            chunk = sock.recv(RECV_CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                data = b"".join(chunks)
                response = json.loads(data.decode("utf-8"))
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        sock.close()

        if not chunks:
            raise ConnectionError("Empty response from Rhino")

        data = b"".join(chunks)
        response = json.loads(data.decode("utf-8"))

        if response.get("status") == "error":
            return {"ok": False, "error": response.get("message", "Unknown error")}

        return {"ok": True, "result": response.get("result", {})}

    except ConnectionRefusedError:
        return {"ok": False, "error": "Cannot connect to Rhino. Is the listener running?"}
    except socket.timeout:
        return {"ok": False, "error": "Rhino connection timed out."}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def execute_in_rhino(code: str) -> dict:
    """Execute Python code in Rhino via the TCP socket."""
    return send_to_rhino("execute_python_code", {"code": code})

# ---------------------------------------------------------------------------
# Model API (OpenAI-compatible, served by mlx_lm.server)
# ---------------------------------------------------------------------------

def chat_completion(messages: list[dict], temperature: float | None = None) -> str:
    """Call the local model's chat completion endpoint."""
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": temperature if temperature is not None else TEMPERATURE,
        "stop": ["<|im_end|>", "<|endoftext|>"],
    }).encode("utf-8")

    req = urllib.request.Request(
        MODEL_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            # Clean up any residual special tokens
            content = re.sub(r"<\|im_end\|>.*", "", content, flags=re.DOTALL).strip()
            return content
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Cannot reach model server at {MODEL_URL}. Is ./serve.sh running?\n{e}"
        )

# ---------------------------------------------------------------------------
# Code extraction
# ---------------------------------------------------------------------------

def extract_code(text: str) -> str | None:
    """Extract Python code from the model response.

    Handles:
    - ```python ... ``` fenced blocks
    - ``` ... ``` generic fenced blocks
    - Raw code (if the response looks like pure code)
    """
    # Try fenced code blocks first
    pattern = r"```(?:python)?\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return "\n\n".join(m.strip() for m in matches)

    # If the response looks like raw code (has imports or rs. calls)
    lines = text.strip().split("\n")
    code_indicators = ["import ", "rs.", "Rhino.", "scriptcontext", "def ", "for ", "="]
    code_lines = [l for l in lines if any(ind in l for ind in code_indicators)]
    if len(code_lines) > len(lines) * 0.5:
        return text.strip()

    return None

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def show_code(code: str):
    """Print code in a bordered box."""
    print(f"\033[90m{'─' * 50}\033[0m")
    for line in code.split("\n"):
        print(f"  \033[32m{line}\033[0m")
    print(f"\033[90m{'─' * 50}\033[0m")


def show_result(result: dict):
    """Print Rhino execution result."""
    if result["ok"]:
        msg = result["result"].get("message", "Code executed.")
        output = result["result"].get("output", "")
        print(f"\033[32m  OK: {msg}\033[0m")
        if output:
            print(f"  {output}")
    else:
        print(f"\033[31m  ERROR: {result['error']}\033[0m")

# ---------------------------------------------------------------------------
# Core loop: generate → execute → retry on error
# ---------------------------------------------------------------------------

def generate_and_execute(history: list[dict]) -> None:
    """Generate code from the model, execute in Rhino, auto-retry on errors."""

    # --- Generate ---
    print(f"\033[33m  Generating...\033[0m", end="", flush=True)
    try:
        response = chat_completion(history)
    except ConnectionError as e:
        print(f"\r\033[31m  {e}\033[0m")
        return
    print(f"\r\033[K", end="")  # clear line

    history.append({"role": "assistant", "content": response})

    code = extract_code(response)
    if code is None:
        print(response)
        return

    show_code(code)

    # --- Execute + auto-retry loop ---
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\033[33m  Executing in Rhino...{f' (retry {attempt}/{MAX_RETRIES})' if attempt > 1 else ''}\033[0m")
        result = execute_in_rhino(code)
        show_result(result)

        if result["ok"]:
            return  # success — done

        # --- Error: ask model to fix ---
        if attempt == MAX_RETRIES:
            print(f"\033[31m  Gave up after {MAX_RETRIES} attempts.\033[0m")
            return

        error_msg = (
            f"ERROR when running this code:\n```python\n{code}\n```\n"
            f"Error message: {result['error']}\n\n"
            f"You MUST use a completely different approach. Do NOT repeat the same code.\n"
            f"Rhino API reference:\n"
            f"- Ring/torus: rs.AddTorus(base_point, major_radius, minor_radius)\n"
            f"- Pipe: rs.AddPipe(curve_id, ...) — requires an existing curve GUID\n"
            f"- Sphere: rs.AddSphere(center, radius)\n"
            f"- Box: rs.AddBox([8 corner points])\n"
            f"- Cylinder: rs.AddCylinder(base, height, radius)\n"
            f"- Cone: rs.AddCone(base, height, radius)\n"
            f"- Circle: rs.AddCircle(plane, radius)\n"
            f"- Line: rs.AddLine(start, end)\n"
            f"Write the corrected code. Only output code."
        )
        history.append({"role": "user", "content": error_msg})

        # Increase temperature on retries to avoid repeating the same bad output
        retry_temp = min(TEMPERATURE + attempt * 0.3, 0.9)
        print(f"\033[33m  Fixing (attempt {attempt + 1}/{MAX_RETRIES})...\033[0m", end="", flush=True)
        try:
            fix_response = chat_completion(history, temperature=retry_temp)
        except ConnectionError as e:
            print(f"\r\033[31m  {e}\033[0m")
            return
        print(f"\r\033[K", end="")

        history.append({"role": "assistant", "content": fix_response})

        fix_code = extract_code(fix_response)
        if fix_code is None:
            print(f"  Model response (no code found):")
            print(f"  {fix_response}")
            return

        show_code(fix_code)
        code = fix_code  # use the fixed code in the next iteration

# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def print_banner():
    print()
    print("  rhino-coder  —  Local Rhino3D Code Generation")
    print("  ──────────────────────────────────────────────")
    print("  Model server:  localhost:8080 (mlx_lm.server)")
    print("  Rhino socket:  localhost:54321")
    print(f"  Auto-execute:  ON  (max {MAX_RETRIES} retries on error)")
    print()
    print("  Commands: /quit  /clear  /run <code>  /retry  /history")
    print()


def main():
    print_banner()

    history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    last_user_msg: str | None = None

    while True:
        try:
            user_input = input("\033[36mrhino>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        # --- Commands ---
        if user_input in ("/quit", "/exit"):
            print("Bye!")
            break

        if user_input == "/clear":
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            last_user_msg = None
            print("  History cleared.")
            continue

        if user_input == "/history":
            for msg in history[1:]:  # skip system
                role = msg["role"]
                content = msg["content"][:120] + ("..." if len(msg["content"]) > 120 else "")
                print(f"  [{role}] {content}")
            continue

        if user_input.startswith("/run "):
            code = user_input[5:].strip()
            if not code:
                print("  Usage: /run <python code>")
                continue
            show_code(code)
            result = execute_in_rhino(code)
            show_result(result)
            continue

        if user_input == "/retry":
            if last_user_msg is None:
                print("  Nothing to retry.")
                continue
            # Remove last assistant + user messages
            if len(history) >= 2 and history[-1]["role"] == "assistant":
                history.pop()
            if len(history) >= 2 and history[-1]["role"] == "user":
                history.pop()
            user_input = last_user_msg
            # Fall through to normal processing

        # --- Generate → execute → auto-retry ---
        last_user_msg = user_input
        history.append({"role": "user", "content": user_input})
        generate_and_execute(history)


if __name__ == "__main__":
    main()
