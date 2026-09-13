#!/usr/bin/env bash
# Local REST API helper. Matches
# https://github.com/coddingtonbear/obsidian-local-rest-api/blob/main/README.md
set -euo pipefail

BASE="${OBSIDIAN_REST_URL:-https://127.0.0.1:27124}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT="${OBSIDIAN_REST_CACERT:-$SCRIPT_DIR/../certs/obsidian-local-rest-api.crt}"

usage() {
  cat >&2 <<'EOF'
usage: rest.sh METHOD PATH [body]

GET / needs no API key (server status).
Everything else needs OBSIDIAN_API_KEY (Bearer). Do not read plugin data.json.

examples:
  rest.sh GET /
  rest.sh GET /vault/
  rest.sh GET /vault/Maps/知识库地图.md
  rest.sh POST '/search/simple/?query=第二大脑&contextLength=80'
  rest.sh POST /search/ '{"==":[{"var":"frontmatter.type"},"concept"]}'
  rest.sh POST /open/Maps/知识库地图.md
  rest.sh PATCH /vault/Daily/2026-09-12.md '{"targetType":"heading","target":["流水"],"operation":"append","content":"- item"}'
EOF
  exit 1
}

if [[ $# -lt 2 ]]; then
  usage
fi

method="$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')"
path="$2"
shift 2
[[ "$path" == /* ]] || path="/$path"
url="${BASE}${path}"

body=""
if [[ $# -gt 0 ]]; then
  body="$1"
fi

curl_base=(curl -sS --fail-with-body)
if [[ -f "$CERT" ]]; then
  curl_base+=(--cacert "$CERT")
else
  curl_base+=(-k)
fi

headers=()
need_auth=1
if [[ "$method" == GET && ( "$path" == "/" || "$path" == "/obsidian-local-rest-api.crt" ) ]]; then
  need_auth=0
fi

# Cursor Agent shells often lack ~/.zshrc. Never print the value.
if [[ -z "${OBSIDIAN_API_KEY:-}" ]]; then
  OBSIDIAN_API_KEY="$(
    zsh --no-rcs -c 'source "$HOME/.zshrc" >/dev/null 2>&1; printf %s "${OBSIDIAN_API_KEY-}"' 2>/dev/null || true
  )"
fi

if [[ "$need_auth" -eq 1 ]]; then
  if [[ -z "${OBSIDIAN_API_KEY:-}" ]]; then
    echo "OBSIDIAN_API_KEY is not set. Copy the key from Obsidian → Settings → Local REST API with MCP. Do not read plugin data.json." >&2
    exit 2
  fi
  headers+=(-H "Authorization: Bearer ${OBSIDIAN_API_KEY}")
fi

if [[ -n "$body" ]]; then
  content_type="${REST_CONTENT_TYPE:-}"
  if [[ -z "$content_type" ]]; then
    if [[ "$path" == "/search/" || "$path" == "/search" ]]; then
      content_type="application/vnd.olrapi.jsonlogic+json"
    elif [[ "$method" == PATCH ]]; then
      content_type="application/json"
    else
      content_type="text/markdown"
    fi
  fi
  headers+=(-H "Content-Type: ${content_type}")
  if [[ ${#headers[@]} -gt 0 ]]; then
    "${curl_base[@]}" -X "$method" "${headers[@]}" --data "$body" "$url"
  else
    "${curl_base[@]}" -X "$method" --data "$body" "$url"
  fi
else
  if [[ ${#headers[@]} -gt 0 ]]; then
    "${curl_base[@]}" -X "$method" "${headers[@]}" "$url"
  else
    "${curl_base[@]}" -X "$method" "$url"
  fi
fi

echo
