---
name: obsidian-api
description: Accesses this Obsidian vault through the Local REST API with MCP at https://127.0.0.1:27124 (health check) and /mcp/ (Cursor MCP). Use when searching the vault, listing/reading notes via Obsidian, opening a file in the app, patching a heading, or when REST/MCP vs filesystem fallback matters. Never reads plugin data.json.
---

# Obsidian Local REST API with MCP

Plugin is already installed. Do not edit `.obsidian/plugins/` or `data.json`.

Official docs: https://github.com/coddingtonbear/obsidian-local-rest-api/blob/main/README.md  
Interactive API: https://coddingtonbear.github.io/obsidian-local-rest-api/

Same host, two interfaces (same capabilities):

| URL | Auth | Role |
| --- | --- | --- |
| `https://127.0.0.1:27124/` | none | REST health (`status`, `authenticated`) |
| `https://127.0.0.1:27124/vault/` etc. | `Authorization: Bearer $OBSIDIAN_API_KEY` | REST |
| `http://127.0.0.1:27123/mcp/` | Bearer | MCP (Cursor `.cursor/mcp.json`) |

HTTP `127.0.0.1:27123` is enabled (plugin UI). Cursor MCP uses a stdio bridge (`.cursor/obsidian-mcp.sh` + `.cursor/.env`) because HTTP MCP cannot load `envFile`. HTTPS `27124` remains for REST (`curl -k`).

There is **no** core `/periodic/` route. Daily notes are `Daily/YYYY-MM-DD.md` via `/vault/...`.

## Config

- `OBSIDIAN_API_KEY` — from **Settings → Local REST API with MCP**. Env only.
- `OBSIDIAN_REST_URL` — default `https://127.0.0.1:27124`
- Helper: [scripts/rest.sh](scripts/rest.sh) (uses [certs/obsidian-local-rest-api.crt](certs/obsidian-local-rest-api.crt) like official `--cacert`)

REST paths are vault-relative (`Maps/知识库地图.md`). If Cursor opened the parent `Obsidian/` folder, filesystem paths still use `PPK/`.

## Workflow

**优先 REST，避免官方 CLI 每次要宿主机权限。**

1. `rest.sh GET /` — no key. This is the probe. If it succeeds, stay on REST (or MCP on the same plugin if the Cursor `obsidian` server is connected). Do **not** call `obsidian vault="PPK"` while REST is up.
2. If `authenticated` is false, vault routes need `OBSIDIAN_API_KEY`. If the key is missing, say so; do not read `data.json`.
3. REST discovery and I/O (MCP equivalents in parentheses when connected):
   - `POST /search/simple/?query=...&contextLength=120` → MCP `search_simple`
   - `POST /search/` JsonLogic → MCP `search_query`
   - `GET /vault/` / `GET /vault/{path}` → `vault_list` / `vault_read`
   - `GET /tags/` → `tag_list`
   - `POST /open/{path}` → `open_file`
   - writes: `PUT`/`PATCH` `/vault/{path}` → `vault_write` / `vault_patch` / `vault_append`
4. **Only if step 1 fails** (Obsidian closed, plugin off, or `127.0.0.1:27124` unreachable): official CLI `obsidian vault="PPK"` with host/`all` permissions. If CLI also fails, grep/read files and say you did not use live search. Skip `copilot/`, `.obsidian/`, `.cursor/`, `.claude/`, `.agents/`, `.opencode/`.
5. **Obsidian 开着且 REST 通时，知识笔记的创建/修改必须走 REST `PUT`/`PATCH` `/vault/{path}` 或 MCP。** 不要用 Cursor 的文件写入工具直接改 `Inbox/`、`Daily/`、`Sources/`、`Concepts/`、`Maps/`、`Areas/`、`Projects/`、`Outputs/` 下的 `.md`（会和 Copilot / 未保存编辑器互相覆盖）。`.cursor/` 仍用文件系统。追加用 JSON `PATCH`（可带 `ifMatch`），避免整文件重写。Heading `PATCH` 若 404，改为 `GET` 全文、改字符串、再 `PUT`。
6. Binary attachments: REST `/vault/` raw bytes, or MCP `vault_read_binary` / `vault_write_binary` (≤ 1 MiB). Do not round-trip binaries through `vault_read`.

Endpoint and MCP tool tables: [reference.md](reference.md).

## JsonLogic by type

Content-Type: `application/vnd.olrapi.jsonlogic+json`

```json
{ "==": [{ "var": "frontmatter.type" }, "concept"] }
```

If 400, `POST /search/simple/?query=tag:#type/concept`.

## Examples

```bash
# health — same as: curl https://127.0.0.1:27124/ with the plugin CA
PPK/.cursor/skills/obsidian-api/scripts/rest.sh GET /

export OBSIDIAN_API_KEY=...   # Settings → Local REST API with MCP
PPK/.cursor/skills/obsidian-api/scripts/rest.sh GET /vault/
PPK/.cursor/skills/obsidian-api/scripts/rest.sh POST '/search/simple/?query=第二大脑&contextLength=80'
PPK/.cursor/skills/obsidian-api/scripts/rest.sh GET '/vault/Maps/知识库地图.md'
```
