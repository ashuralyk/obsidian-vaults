# REST vs MCP (official plugin README)

Source: https://github.com/coddingtonbear/obsidian-local-rest-api/blob/main/README.md

## REST endpoints

| Endpoint | Methods | Notes |
| --- | --- | --- |
| `/` | GET | Status; **no auth** |
| `/vault/{path}` | GET PUT PATCH POST DELETE | File CRUD; GET heading via `/vault/{file}/heading/{Name}` |
| `/active/` | GET PUT PATCH POST DELETE | File currently open in Obsidian |
| `/search/simple/` | POST | Query string `query`, optional `contextLength` |
| `/search/` | POST | Body JsonLogic; `Content-Type: application/vnd.olrapi.jsonlogic+json` |
| `/commands/` | GET | List commands |
| `/commands/{commandId}/` | POST | Run a command |
| `/tags/` | GET | Tags + counts |
| `/open/{path}` | POST | Open in Obsidian UI |
| `/mcp/` | GET POST | MCP Streamable HTTP; Bearer required |
| `/obsidian-local-rest-api.crt` | GET | Local CA; **no auth** |

`PATCH /vault/{path}` JSON body (current format, not deprecated headers):

```json
{
  "targetType": "heading",
  "target": ["流水"],
  "operation": "append",
  "content": "- 一行"
}
```

Frontmatter: `"targetType": "frontmatter", "target": "status", "operation": "replace", "value": "evergreen"`.

Do not send `Markdown-Patch-Version: 1` or `Target-Type` headers unless debugging legacy clients.

## MCP tools (same server)

`search_simple`, `search_query`, `vault_list`, `vault_read`, `vault_read_binary`, `vault_write`, `vault_write_binary`, `vault_append`, `vault_patch`, `vault_delete`, `vault_move`, `vault_copy`, `vault_get_document_map`, `active_file_get_path`, `tag_list`, `command_list`, `command_execute`, `open_file`.

Prefer these when the Cursor MCP server `obsidian` is connected. Knowledge-graph writes still follow `Meta/schema.md`.

TLS: REST over HTTPS `27124` needs the plugin CA or `curl -k`. Cursor MCP is HTTP `http://127.0.0.1:27123/mcp/` (enabled in plugin UI). Agent must not edit plugin settings files.

## Cursor `mcp.json`

Project file: `.cursor/mcp.json` (see vault copy). Key via env `OBSIDIAN_API_KEY`, never committed, never read from `data.json`.
