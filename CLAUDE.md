# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not a code project** — there is no build, lint, or test toolchain. It is an Obsidian vault workspace with two layers:

- **Workspace root (`Obsidian/`)** — the Cursor workspace. Holds `AGENTS.md` (workspace memory / learned preferences), `.agents/skills/` (screenplay + video-prompt production skills), `.cursor/rules/` (model-routing rules), and `Screenplays/` (film projects).
- **`PPK/`** — the actual Obsidian vault (vault name `PPK`), a knowledge base. Holds `PPK/AGENTS.md` (the agent contract, shared by Cursor and Obsidian Copilot), `Meta/schema.md` (note schema), `Maps/`, `Concepts/`, `Sources/`, `Inbox/`, etc., and its own `.agents/skills/` (vault workflow skills).

There is a nested `PPK/CLAUDE.md` that is just a pointer (`@AGENTS.md`) — do **not** overwrite it. This root `CLAUDE.md` is the workspace-level guide.

## Commands (Obsidian REST / CLI)

There is no code to run. The "toolchain" is the Obsidian Local REST API with MCP plugin. Obsidian must be running.

```sh
# Health probe — no API key. Success ⇒ Obsidian is running ⇒ use REST/MCP, never direct file writes.
curl -k https://127.0.0.1:27124/

# REST helper (vault-relative paths, omit the PPK/ prefix)
PPK/.agents/skills/obsidian-api/scripts/rest.sh GET /
PPK/.agents/skills/obsidian-api/scripts/rest.sh GET /vault/Maps/知识库地图.md
PPK/.agents/skills/obsidian-api/scripts/rest.sh POST '/search/simple/?query=第二大脑&contextLength=80'
PPK/.agents/skills/obsidian-api/scripts/rest.sh PATCH /vault/Daily/2026-09-12.md '{"targetType":"heading","target":["流水"],"operation":"append","content":"- item"}'

# CLI fallback — ONLY when REST health fails (Obsidian closed / plugin off)
obsidian vault="PPK"
```

- REST base `https://127.0.0.1:27124` (HTTPS, `curl -k`); MCP bridge at `http://127.0.0.1:27123/mcp/`.
- Auth is `Authorization: Bearer $OBSIDIAN_API_KEY` (env var only; copy the key from **Obsidian → Settings → Local REST API with MCP**, never read plugin `data.json`).
- REST/MCP paths are **vault-relative** (`Maps/foo.md`). If the workspace is opened at the parent `Obsidian/`, filesystem paths use the `PPK/` prefix.
- There is no `/periodic/` route — daily notes are `Daily/YYYY-MM-DD.md`.

## Big-picture architecture

### Dual-agent consistency (the single most important constraint)

The vault is edited by **both** Cursor (filesystem + REST) and the Obsidian **Copilot** plugin (in-app). The authoritative store is the Obsidian vault's markdown, not a disk cache. `PPK/AGENTS.md` is the contract both agents follow.

- When `curl -k https://127.0.0.1:27124/` succeeds, **all knowledge-note reads/writes go through REST or MCP** (`PUT`/`PATCH` `/vault/...`). Do **not** write `.md` files under `PPK/Inbox|Daily|Sources|Concepts|Maps|Areas|Projects|Outputs` directly with the filesystem — it races with Copilot and un-saved editor buffers.
- One agent writes one file at a time; read before write; `PATCH` with `ifMatch` where possible; on `409` re-read rather than overwrite.
- Only when the REST probe fails: fall back to the `obsidian` CLI, then plain file reads (and say you did not use live search).

### Forbidden paths (do not create/modify/delete/rename)

- `.obsidian/community-plugins.json`, `.obsidian/core-plugins.json`, `.obsidian/plugins/` (incl. `git`, `copilot`, `obsidian-local-rest-api` and any `data.json`)
- Vault-root `PPK/copilot/` (Copilot's workspace, incl. its `skills/`)
- `PPK/.claude/`, `PPK/.opencode/` (Copilot-synced skill copies)
- Do not read the REST plugin `data.json` for the API key.

### Skills — one copy each, in `.agents/skills/`

Skills live only under `.agents/skills/` (workspace root for production skills; `PPK/.agents/skills/` for vault workflow). Do **not** duplicate them into `.cursor/skills/` or `copilot/skills/`.

**Workspace production skills** (`.agents/skills/`, route by task):
- `screenplay-development` — idea → full screenplay with runtime lock, scoring/rewrite, and 3 synced attachments (character bios, shoot locations, props). Must ask Markdown vs Fountain before drafting. Key-prop "keep it whole" rule (转折/揭秘/高潮 must come from character choice, not combining/disassembling props).
- `storyboard-development` — screenplay → storyboard/shot-list with dual scoring.
- `minimax-h3-prompt` / `seedance-prompt` — video prompt generation (see routing below).

**PPK vault workflow skills** (`PPK/.agents/skills/`): `obsidian-api` (REST/MCP I/O), `ingest`, `query-vault`, `synthesize`, `graph-health`.

### Video prompt model routing

Video/short-film prompts are model-specific and must not be conflated:

- **MiniMax H3 / H3 Max / 海螺 / Hailuo / MiniMax Design** → `minimax-h3-prompt` skill. 4–15 s integer clips (H3 Max 5–15 s), product formula (duration + ratio + 图N binding + subject/scene/motion/sound), three input modes. No cross-clip memory — each clip is a standalone paste.
- **Seedance / 即梦 / 火山方舟** → `seedance-prompt` skill. Official structured prompt, 30 s per-shot ceiling, integer-second continuous timestamps, identity lock (people/places/props) across segments.
- If the user did not name a model, ask which one — do not default.

Shared hard rules across both (from `.cursor/rules/*.mdc` and the skills): characters/locations/hero-props are identity-locked and named; a phone in a frontal shot shows only its back (cut over-shoulder to read the screen); "no music" must ban melody and pads, not just 「无 BGM」; inner states are visible micro-expressions.

### PPK note schema (read `PPK/Meta/schema.md` before writing notes)

- Entry point: `PPK/Maps/知识库地图.md` — start retrieval/routing from maps and typed notes, not the whole vault.
- Note `type`: `inbox | daily | source | concept | moc | area | project | output`, each mapped to a directory (`Concepts/`, `Maps/`, `Outputs/briefings/`, …). Required YAML: `type`, `status` (`seedling | evergreen | archived`), `updated` (`YYYY-MM-DD`), `aliases`, and `tags` containing `#type/<type>`.
- `[[wikilink]]` edges are typed and allow-listed (`source→concept`, `daily→concept|area|project`, `concept→concept` only for real relations, `moc→members`, `area→…`, `output→cited`). No daily↔daily meshes or graph-decoration links.
- **多源互证 (multi-source corroboration, hard rule):** when a later source makes a similar claim, you must record it — deepen the existing concept if the mechanism matches, else create a new linked concept. Never skip because "something similar already exists." Search is to merge empty same-name shells, not to block new angles.
- Templates in `PPK/Meta/templates/`.

### Writing voice

All note prose, briefings, and user-facing explanations use the **mentor voice**: fluent, complete Chinese sentences, judgment first then reasons, no telegram fragments / keyword dumps / AI boilerplate. Sources are usually English — understand first, then write in Chinese as a first language (not sentence-level translation). This is codified in `.cursor/rules/note-prose.mdc` and `Meta/schema.md`「正文文笔与整理口吻」.

### Screenplay project layout

`Screenplays/<ProjectName>/`: `Screenplay.md` (Brief at top + body), `Characters.md`, `Scenes.md`, `Assets.md`, storyboard drafts as `Storyboard - Draft N.md` (keep prior drafts; each revision is a new draft), `Audit/` for development audits. Video prompts go in a separate file (e.g. `MiniMax H3.md`), not inside the storyboard draft.

## Further reading

- `AGENTS.md` — workspace memory: the full learned-preferences list, detailed per-skill rules, and the H3/Seedance constraints. Treat it as authoritative and load it when doing screenplay/video work.
- `PPK/AGENTS.md` — the nested knowledge-base agent contract (read/write consistency, workflow routing).
- `PPK/Meta/schema.md` — note types, allowed edges, multi-source corroboration, prose rules.
- `README.md` — setup notes (vault layout, REST endpoints, don't-touch list).
