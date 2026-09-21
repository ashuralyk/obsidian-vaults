---
name: synthesize
description: Writes vault-backed briefings and decision memos into Outputs/. Use when the user wants a topic briefing, status synthesis, options/tradeoffs memo, or a decision record grounded in existing notes.
---

# Synthesize

Read `query-vault` / `obsidian-api` first so the piece is grounded. Do not write into `copilot/`.

Voice: mentor tone—fluent, readable Chinese (or the note’s language), judgment first then reasons. No telegram lists as body text, no keyword dumps, no generic AI wrap-ups. English sources are understood first, then rewritten in Chinese as a first language, not translated sentence by sentence. Follow `Meta/schema.md`「正文文笔与整理口吻」and `.cursor/rules/note-prose.mdc`.

## Briefing → `Outputs/briefings/<标题>.md`

Template: `Meta/templates/briefing.md`. `type: output`, tags `#type/output` `#output/briefing`.

Structure: 结论 → 展开. 链接 / 引用 must `[[wikilink]]` every concept and source you used.

## Decision → `Outputs/decisions/<标题>.md`

Template: `Meta/templates/decision.md`. Tags include `#output/decision`.

Structure: 要决定什么 → 选项 → 取舍 → 结论. Link evidence notes. If evidence is missing, say so in the memo instead of fabricating.

## After write

- Add the new file to `Outputs/briefings/简报说明.md` or `Outputs/decisions/决策说明.md` 成员 list.
- Optionally `POST /open/{path}` so it appears in Obsidian.
