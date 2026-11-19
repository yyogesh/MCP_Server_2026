"""Generic explorer for any stdio MCP server.

Usage:
  uv run explore.py -- <server command> [args...]
  uv run explore.py --call TOOL '<json args>' -- <server command>
  uv run explore.py --read URI -- <server command>
  uv run explore.py --prompt NAME '<json args>' -- <server command>
"""

import argparse
import asyncio
import json
import os
import sys

from mcp import Client, MCPError, StdioServerParameters


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    # Everything after "--" is the server command; the rest are our options.
    if "--" not in sys.argv or sys.argv.index("--") == len(sys.argv) - 1:
        sys.exit(__doc__)
    split = sys.argv.index("--")
    parser = argparse.ArgumentParser(usage=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--call", nargs=2, metavar=("TOOL", "JSON"))
    group.add_argument("--read", metavar="URI")
    group.add_argument("--prompt", nargs=2, metavar=("NAME", "JSON"))
    return parser.parse_args(sys.argv[1:split]), sys.argv[split + 1 :]


def json_arg(text: str) -> dict:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as e:
        sys.exit(f"Invalid JSON arguments: {e}")
    return value if isinstance(value, dict) else sys.exit("JSON arguments must be an object, e.g. '{}'")


def content_text(item) -> str:
    # Text items print as-is; other kinds (image, audio, blob...) as a placeholder.
    text = getattr(item, "text", None)
    return text if text is not None else f"<{getattr(item, 'type', type(item).__name__)} content>"


async def overview(client: Client) -> None:
    info, caps = client.server_info, client.server_capabilities
    print("== Server:", " ".join(filter(None, (info.name, info.version))) if info else "(unknown)")
    if client.instructions:
        print(client.instructions.strip())

    if caps.tools:
        print("\n== Tools")
        for tool in (await client.list_tools()).tools:
            desc = (tool.description or "").strip().splitlines()
            print(f"- {tool.name}: {desc[0] if desc else ''}")
            required = tool.input_schema.get("required", []) if tool.input_schema else []
            print(f"    required: {', '.join(required) or '(none)'}")
            # Show only annotation hints the server actually set.
            notes = tool.annotations.model_dump() if tool.annotations else {}
            if hints := {k: v for k, v in notes.items() if k.endswith("_hint") and v is not None}:
                print("    hints: " + ", ".join(f"{k}={v}" for k, v in hints.items()))

    if caps.resources:
        print("\n== Resources")
        for res in (await client.list_resources()).resources:
            print(f"- {res.uri} ({res.name})")
        print("\n== Resource templates")
        for tmpl in (await client.list_resource_templates()).resource_templates:
            print(f"- {tmpl.uri_template} ({tmpl.name})")

    if caps.prompts:
        print("\n== Prompts")
        for prompt in (await client.list_prompts()).prompts:
            args = ", ".join(a.name + ("" if a.required else "?") for a in prompt.arguments or [])
            print(f"- {prompt.name}({args})")


async def run(opts: argparse.Namespace, command: list[str]) -> int:
    # Pass the full environment so variables like TRIPMATE_DB reach the server.
    server = StdioServerParameters(command=command[0], args=command[1:], env=dict(os.environ))
    async with Client(server) as client:
        # Catch server errors here; outside the client they arrive wrapped in task-group errors.
        try:
            await act(client, opts)
        except MCPError as e:
            print(f"Server error: {e}", file=sys.stderr)
            return 1
    return 0


async def act(client: Client, opts: argparse.Namespace) -> None:
    if opts.call:
        result = await client.call_tool(*opts.call)
        print(f"is_error: {result.is_error}")
        for item in result.content:
            print(content_text(item))
        if result.structured_content is not None:
            print("structured:", json.dumps(result.structured_content, indent=2))
    elif opts.read:
        for item in (await client.read_resource(opts.read)).contents:
            print(content_text(item))
    elif opts.prompt:
        result = await client.get_prompt(*opts.prompt)
        for msg in result.messages:
            print(f"[{msg.role}] {content_text(msg.content)}")
    else:
        await overview(client)


def main() -> None:
    opts, command = parse_args()
    for pair in filter(None, (opts.call, opts.prompt)):  # validate JSON before starting the server
        pair[1] = json_arg(pair[1])
    sys.exit(asyncio.run(run(opts, command)))


if __name__ == "__main__":
    main()
