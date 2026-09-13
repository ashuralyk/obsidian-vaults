#!/usr/bin/env python3
"""stdio <-> Obsidian Local REST API Streamable HTTP. Reads key from .env only.

Cursor speaks MCP stdio: one JSON-RPC object per newline, no Content-Length.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent
URL = "http://127.0.0.1:27123/mcp/"
ENV = DIR / ".env"


def load_key() -> str:
    if not ENV.is_file():
        raise SystemExit(f"obsidian-mcp: missing {ENV}")
    key = ""
    for raw in ENV.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "OBSIDIAN_API_KEY":
            key = value.strip().strip('"').strip("'")
    if not key:
        raise SystemExit("obsidian-mcp: OBSIDIAN_API_KEY empty")
    return key


def read_message() -> dict | None:
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        return json.loads(line)


def write_message(obj: dict) -> None:
    data = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()
    if b"\n" in data:
        raise SystemExit("obsidian-mcp: JSON contained a newline")
    sys.stdout.buffer.write(data + b"\n")
    sys.stdout.buffer.flush()


def parse_body(raw: bytes, content_type: str) -> dict | None:
    if not raw:
        return None
    if "text/event-stream" in content_type:
        for block in raw.decode().split("\n\n"):
            for line in block.splitlines():
                if line.startswith("data:"):
                    return json.loads(line[5:].strip())
        return None
    return json.loads(raw.decode())


def main() -> None:
    key = load_key()
    session: str | None = None
    while True:
        msg = read_message()
        if msg is None:
            break
        payload = json.dumps(msg, separators=(",", ":")).encode()
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if session:
            headers["mcp-session-id"] = session
        req = urllib.request.Request(URL, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                sid = resp.headers.get("mcp-session-id")
                if sid:
                    session = sid
                parsed = parse_body(resp.read(), resp.headers.get("Content-Type", ""))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode(errors="replace")
            if "id" in msg:
                write_message(
                    {
                        "jsonrpc": "2.0",
                        "id": msg["id"],
                        "error": {
                            "code": -32000,
                            "message": f"HTTP {exc.code}: {err_body[:500]}",
                        },
                    }
                )
            else:
                print(f"obsidian-mcp: HTTP {exc.code}: {err_body[:200]}", file=sys.stderr)
            continue
        except Exception as exc:
            if "id" in msg:
                write_message(
                    {
                        "jsonrpc": "2.0",
                        "id": msg["id"],
                        "error": {"code": -32000, "message": str(exc)[:500]},
                    }
                )
            else:
                print(f"obsidian-mcp: {exc}", file=sys.stderr)
            continue
        if parsed is None:
            continue
        if "id" in msg:
            write_message(
                parsed if "jsonrpc" in parsed else {**parsed, "jsonrpc": "2.0", "id": msg["id"]}
            )


if __name__ == "__main__":
    main()
