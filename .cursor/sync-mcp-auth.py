#!/usr/bin/env python3
"""Write gitignored .cursor/mcp.json with Bearer from .cursor/.env. Do not commit the result."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV = ROOT / ".env"


def load_key() -> str:
    if not ENV.is_file():
        raise SystemExit(f"missing {ENV}")
    key = ""
    for raw in ENV.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "OBSIDIAN_API_KEY":
            key = value.strip().strip('"').strip("'")
    if not key:
        raise SystemExit("OBSIDIAN_API_KEY empty in .env")
    return key


def main() -> None:
    key = load_key()
    body = {
        "mcpServers": {
            "obsidian": {
                "url": "http://127.0.0.1:27123/mcp/",
                "headers": {"Authorization": f"Bearer {key}"},
            }
        }
    }
    text = json.dumps(body, indent=2) + "\n"
    (ROOT / "mcp.json").write_text(text)
    ppk = ROOT.parent / "PPK" / ".cursor" / "mcp.json"
    if ppk.parent.is_dir():
        ppk.write_text(text)
    print("wrote mcp.json (Authorization header present, not printed)")


if __name__ == "__main__":
    main()
