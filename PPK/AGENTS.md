# PPK 知识库（所有 Agent 共用）

本文件是 **Cursor** 与 **Obsidian Copilot** 共用的同一份契约。两边都在改这一座 vault：知识内容、目录、frontmatter 和 `[[wikilink]]` 必须保持一致。原则上，人不手改笔记。

细则见 [[笔记范式]]（`Meta/schema.md`）。Cursor 的流程在 `.cursor/skills/`；Copilot 的流程在 `copilot/skills/`（**互不改对方的技能目录**）。

## 先读

1. `Meta/schema.md` — 类型、目录、允许的边、**多源互证**、**正文文笔与整理口吻**
2. `Maps/知识库地图.md` — 入口
3. 写任何知识笔记之前，先搜索再动笔：同名空壳要合并，**新来源的新角度必须落盘**，不得因“库里已有类似概念”而省略

## 多源互证（摘要）

同一类别知识可从不同书、不同时代获得不同解读。机制相同则加深既有概念并写「多源互证」；机制不同则新建并链接。跨书互证提高参考价值。完整规则以 `Meta/schema.md` 为准。

## 整理口吻（摘要）

落盘、简报、决策，以及面向用户的整理与问答，一律用 mentor 口吻：通畅易读，先判断后理由；禁止电报体、关键词堆砌和 AI 套话。来源多为英文时，先吃透原意，再按中文作为第一语言来写，不要做英译中。完整规则见 `Meta/schema.md`「正文文笔与整理口吻」。

## 禁区（两边都不得创建 / 修改 / 删除 / 重命名）

- `.obsidian/community-plugins.json`、`.obsidian/core-plugins.json`、`.obsidian/plugins/`
- vault 根 `copilot/`（Copilot 工作区）
- `.claude/`、`.agents/`、`.opencode/`（Copilot 同步的技能副本）
- `.cursor/`（Cursor 规则与技能；Copilot 不要改）

不要从 REST 插件 `data.json` 读取 API key。Cursor 只用环境变量 `OBSIDIAN_API_KEY`。

## 路径

- **Vault 根**：含 `Inbox/`、`Concepts/` 的本文件夹。
- **REST / Copilot CLI / wikilink**：一律使用 vault 相对路径，例如 `Concepts/某概念.md`（不要带 `PPK/`）。
- **Cursor 工作区若是上一级 `Obsidian/`**：只有用文件系统工具时才加 `PPK/` 前缀。走 REST/MCP 时仍不带 `PPK/`。

## 一致性：同一座 vault、两种入口

权威存储是 **Obsidian vault 里的 markdown**，不是 Cursor 的磁盘缓存，也不是 Copilot 的对话上下文。

| 场景 | 读 | 写知识笔记 |
| --- | --- | --- |
| Obsidian 开着（Copilot 可能同时在跑） | 用 **Local REST API / MCP**（Cursor）或 **Obsidian CLI / 应用内工具**（Copilot），以运行中的索引为准 | **必须经 Obsidian**：Cursor 用 `PUT`/`PATCH` `/vault/...` 或 MCP `vault_write` / `vault_patch`；Copilot 用 CLI/`vault` 写入。禁止 Cursor 用编辑器直写 `.md` 去抢 Copilot 未保存缓冲区 |
| Obsidian 未开 | Cursor 可读文件；Copilot 不可用 | 仅 Cursor 可写文件；下次打开 Obsidian 后以磁盘为准 |

探活：`GET https://127.0.0.1:27124/`（无需 key）。通了就表示 Obsidian 在跑，此时 **禁止对知识笔记做旁路文件系统写入**。

### 并发

- **同一文件同一时刻只有一个 Agent 写。** 先 `GET /vault/{path}`（或 Copilot 读盘/CLI）再改；用 REST `PATCH` 时尽量带 `ifMatch`（来自 document map 的 `version`）。遇到 409 或冲突则重新读取，不要覆盖。
- 不要两边同时「全文重写」同一篇。追加日记用 heading `PATCH`/`daily:append`，不要整文件 PUT。
- 新建前用 `POST /search/simple/` 或 Copilot 搜索：已有同名或 `aliases` 则更新旧笔记，不新建第二篇空壳；若新来源提供新角度，必须写入该笔记的多源互证或新建相关概念。
- 改完后把 `updated:` 写成当天。需要对方立刻看见时，Cursor 可 `POST /open/{path}`。

### 分工（避免双写技能）

- Cursor 不维护、不复制、不「同步」`copilot/skills/`。
- Copilot 不维护 `.cursor/skills/`，但 **必须遵守本文件与 `Meta/schema.md`**（类型、目录、链接纪律）。
- 知识只进 `Inbox/`、`Daily/`、`Sources/`、`Concepts/`、`Maps/`、`Areas/`、`Projects/`、`Outputs/`，模板用 `Meta/templates/`。不要在 vault 根或 `copilot/` 下落知识笔记。

## 工作流（Cursor）

| 用户意图 | Skill |
| --- | --- |
| 调用搜索 / 打开 / 经 Obsidian 读写 | `obsidian-api` |
| 对话想法、网页、PDF、日记入库 | `ingest` |
| 对着库问答 | `query-vault` |
| 简报、决策备忘 | `synthesize` |
| 孤儿、缺边、重复、该建的 MOC | `graph-health` |

Copilot：用自己的 vault/CLI 技能完成同等意图，但产出形状必须与 schema 相同。

输出：简报写入 `Outputs/briefings/`；决策写入 `Outputs/decisions/`；问答必须列出引用笔记的 vault 相对路径。整理与问答同样遵守 mentor 口吻。

REST/MCP：Bearer `OBSIDIAN_API_KEY`；失败则说明原因。Obsidian 开着却改走旁路写文件，视为破坏一致性。无核心 `/periodic/` 路由；日记是 `Daily/YYYY-MM-DD.md`。
