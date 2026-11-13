"""PostToolUse hook: protect the TripMate MCP server after each Edit/Write.

Exit 0 = OK. Exit 2 = block; the message on stderr is shown to Claude.
"""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

# Project root: from Claude Code, or two levels above this script.
ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def writes_to_stderr(call: ast.Call) -> bool:
    # True if the call has file=sys.stderr.
    return any(
        kw.arg == "file" and ast.unparse(kw.value) == "sys.stderr" for kw in call.keywords
    )


# Read the hook payload and get the edited file.
payload = json.load(sys.stdin)
file_path = payload.get("tool_input", {}).get("file_path", "")
path = Path(file_path).resolve() if file_path else None

# Only check .py files under src/.
if not path or path.suffix != ".py" or not path.is_relative_to(ROOT / "src"):
    sys.exit(0)

# Check 1: no print() calls that write to stdout.
try:
    tree = ast.parse(path.read_text(encoding="utf-8"))
except SyntaxError:
    tree = None  # The import check below will report the syntax error.
if tree:
    bad = [
        n.lineno
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "print"
        and not writes_to_stderr(n)
    ]
    if bad:
        fail(
            f"{path.name}: print() to stdout on line(s) {bad}. "
            "stdout carries MCP messages over stdio, so printing there breaks the server. "
            "Use print(..., file=sys.stderr) or logging instead."
        )

# Check 2: the server module must still import.
result = subprocess.run(
    ["uv", "run", "python", "-c", "import tripmate.app"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    fail(f"Importing tripmate.app failed after editing {path.name}:\n{result.stderr.strip()}")

sys.exit(0)
