---
name: query-vault
description: Answers questions from this Obsidian vault with explicit note citations. Use when the user asks what the vault knows, to find notes, to explain a topic from existing knowledge, or to retrieve related concepts/sources.
---

# Query vault

## Steps

1. Load `obsidian-api`. `GET /` first (no API key). Prefer REST so the host CLI permission prompt is not required.
2. If REST is up and `OBSIDIAN_API_KEY` is set (or the Cursor MCP server `obsidian` is connected — same plugin):
   - `POST /search/simple/` with the user's terms
   - Optionally JsonLogic on `POST /search/`
   - `GET /vault/{path}` for full notes
3. If REST health fails: official CLI `obsidian vault="PPK"` (needs host/`all` permissions).
4. If REST and CLI both fail, or vault routes return 401 without a key: say so, then grep/read files. Skip `copilot/`, `.obsidian/`, `.cursor/`, `.claude/`, `.agents/`, `.opencode/`.

Start from `Maps/知识库地图.md` and area notes when the question is broad.

Answer in 中文 unless the user writes otherwise. Use a mentor voice: fluent, readable prose; judgment first, then reasons. No telegram-style dumps or AI boilerplate. Sources may be English; the answer is Chinese writing, not a translation. See `Meta/schema.md`「正文文笔与整理口吻」。

End with **引用** — vault-relative paths of notes you actually used.

Do not invent notes. If the vault has no support, say 库中尚无，并建议用 ingest 补哪类笔记。
