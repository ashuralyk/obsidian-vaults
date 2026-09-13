# Obsidian 知识库

Vault 在 [`PPK/`](PPK/)。用 Cursor **打开 `PPK` 文件夹**，这样 `AGENTS.md`、`.cursor/skills` 与 `.cursor/mcp.json` 才会作为项目约定生效。

## 已具备

- 分层目录：Inbox / Daily / Sources / Concepts / Maps / Areas / Projects / Outputs
- Agent 写入纪律：`PPK/AGENTS.md` 对 **Cursor 与 Obsidian Copilot** 共用（Obsidian 开着时经 vault/REST 读写，避免两边直写同一文件互相覆盖）
- 本地访问：已装 **Local REST API with MCP**（[官方 README](https://github.com/coddingtonbear/obsidian-local-rest-api/blob/main/README.md)）

```sh
# 探活，无需 API key（Obsidian 需开着）
curl -k https://127.0.0.1:27124/
```

读笔记、搜索、MCP 需要 Bearer。在 **Settings → Local REST API with MCP** 复制 API key，写入环境变量 `OBSIDIAN_API_KEY`（不要让 Agent 读插件 `data.json`）。项目 MCP 配置在 `.cursor/mcp.json`，指向 `http://127.0.0.1:27123/mcp/`（HTTP，避开自签证书）。HTTPS `27124` 仍可用于 REST（`curl -k`）。

## 不要改

Obsidian 社区插件、`.obsidian/plugins/`、vault 根目录 `PPK/copilot/`。本初始化不建立 Git 仓库。
