---
name: graph-health
description: Audits this Obsidian vault for orphan notes, missing typed links, duplicate concepts, and Maps that should exist. Use when the user asks about graph health, orphans, duplicate ideas, missing MOCs, or to tidy the knowledge graph.
---

# Graph health

Scan markdown under the vault root. **Skip**: `copilot/`, `.obsidian/`, `.cursor/`, `.claude/`, `.agents/`, `.opencode/`, `Meta/templates/`.

## Checks

1. **Untyped** — missing `type:` or `#type/<type>`
2. **Wrong folder** — e.g. `concept` not under `Concepts/`
3. **Orphans** — no `[[wikilink]]` in or out (ignore pure folder-说明 notes if they are linked from `Maps/知识库地图.md`)
4. **Illegal edges** — daily↔daily, source↔source with no reason, links that are not in the schema allow-list
5. **Concepts without sources** — flag if the idea clearly came from a clip/book but has no `### 来源`
6. **Duplicate concepts** — similar titles / aliases
7. **Missing MOC** — several notes in a theme with no `Maps/` or `Areas/` hub

REST `GET /tags/` and simple search can help; if REST is down, say so and use file scan.

## Report format

- 严重：未类型化、禁区被改动、目录错误
- 建议：缺边、该建的 MOC、疑似重复
- 不要自动大改；列出建议路径，经用户同意再用 ingest 纪律修补
