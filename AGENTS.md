## Learned User Preferences

- Knowledge should enter and leave this vault through AI agents; stored notes still need meaningful structure and graph links, not an unstructured dump.
- Notes, briefings, and any organized explanation to the user should sound like a mentor: fluent, readable prose with complete sentences; no telegram-style fragments, keyword dumps, or generic AI cadence. Lead with judgment, then reasons; mark tradeoffs and failure modes without lecture.
- Prefer discuss-then-ingest: explore and challenge an idea first, then select, refine, and write only the durable remainder after the user agrees to save.
- When absorbing books or other sources, treat them as `source` notes plus atomic `concept` notes (short excerpts and processed understanding), not a wholesale paste of the original.
- Keep the vault scalable across books from multiple domains; avoid per-book knowledge silos. When a later book covers a similar idea, always落盘 the new angle—deepen the existing concept with multi-source corroboration if the mechanism matches, or create a linked concept if the mechanism differs; never skip because something “similar” already exists. Cross-era, cross-genre agreement raises a concept’s reference value.
- The user also edits the vault via the Obsidian Copilot plugin; Cursor and Copilot writes must stay consistent.

## Learned Workspace Facts

- This Cursor workspace is an Obsidian vault; the AI knowledge-base layout, skills, and schema live under `PPK/`.
- Vault-root `AGENTS.md` is workspace memory for continual learning. `PPK/AGENTS.md` is the nested knowledge-base agent contract—do not use it as this file or overwrite it for memory updates.
- Do not modify or delete already-installed community plugins (Git, Copilot, Local REST API with MCP) or their directories; adding plugins is allowed only when asked.
- Do not touch the Copilot-created `copilot/` folder (including skills inside it).
- Cursor should talk to a running Obsidian via Local REST API / MCP rather than bypassing it with raw filesystem edits on knowledge notes.
