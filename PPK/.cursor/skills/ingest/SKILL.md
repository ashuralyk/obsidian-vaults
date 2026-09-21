---
name: ingest
description: Turns chat thoughts, web articles, PDFs/books, and daily life into typed Obsidian notes. Use when the user wants to save an idea, clip a URL or article, capture a book/PDF, write or extract from a daily note, or promote Inbox items into Sources/Concepts.
---

# Ingest

Follow `Meta/schema.md` and templates in `Meta/templates/`. Do not write into `copilot/` or `.obsidian/plugins/`. If `GET /` succeeds, create/update notes via REST/MCP (`obsidian-api`), not Cursor file writes — Copilot may be editing the same vault.

## Shared steps

1. Pick `type` and folder. Never drop untyped files at vault root.
2. Copy the matching template, fill YAML (`updated` today, `#type/<type>`). Prose must read like a mentor: fluent, complete sentences, no telegram fragments, keyword dumps, or AI boilerplate; see `.cursor/rules/note-prose.mdc` and `Meta/schema.md`「正文文笔与整理口吻」。来源多为英文时，先理解原意，再按中文作为第一语言来写，不要做英译中。
3. Put allowed `[[wikilink]]` in the 链接 section (and only allowed edges).
4. Update the relevant `area` / `moc` member list when you created a lasting note.
5. Search first (`obsidian-api` REST or MCP `search_simple`). If an existing concept shares the same mechanism, update that note: add the new source, write a `多源互证` section with the new angle, and tag `#corroboration/multi-source` when two or more sources agree. If the topic is related but the mechanism or lens differs, create a new concept and link it. Never skip落盘 because a “similar” note already exists; only skip empty same-title duplicates with no new angle. See `Meta/schema.md`「多源互证」。

## Chat thoughts

- If messy or mixed: `Inbox/` then promote.
- If it is one idea: `Concepts/<中文标题>.md` (`concept`). Atomic: one file, one concept.
- Link related concepts only when the relation is real (定义 / 依赖 / 对立).

## Web article

- One `Sources/<标题>.md` (`source`): URL, 摘录, 出处. Not a long interpretation.
- Distill into `Concepts/` notes; `source` → those concepts.
- Do not paste the full article if a short excerpt + URL is enough.

## PDF / book

- Original file → `Sources/attachments/` (only if the user provided a file to store).
- Companion `source` note in `Sources/` with authors / 摘录. 摘录可保留英文原文；理解与评述用中文写作，不是对译。
- Understanding → `Concepts/`, linked from the source. 概念正文按中文作为第一语言组织，不要把英文句式搬进中文。

## Daily life

- Append to `Daily/YYYY-MM-DD.md` (`daily` template). Create the file if missing (`GET /vault/Daily/YYYY-MM-DD.md`). Core REST has no `/periodic/` (that is a separate plugin extension). Prefer `PATCH` append under heading `流水`.
- After the log: extract to `concept` / `area` / `project` and link **from the daily note**. Do not link dailies to each other.

## Inbox promotion

Empty promoted items out of `Inbox/`. Update `Inbox/收件箱.md` member list if you linked it.
