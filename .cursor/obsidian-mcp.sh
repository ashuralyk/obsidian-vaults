#!/usr/bin/env bash
# stdio bridge: Cursor HTTP MCP does not load .cursor/.env (envFile is stdio-only).
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "obsidian-mcp: missing $ENV_FILE" >&2
  exit 1
fi
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
if [[ -z "${OBSIDIAN_API_KEY:-}" ]]; then
  echo "obsidian-mcp: OBSIDIAN_API_KEY is empty in $ENV_FILE" >&2
  exit 1
fi
export AUTH_HEADER="Bearer ${OBSIDIAN_API_KEY}"
exec npx --yes mcp-remote "http://127.0.0.1:27123/mcp/" --allow-http --header "Authorization:${AUTH_HEADER}"
