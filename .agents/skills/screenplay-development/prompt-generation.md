# 参考图提示词（剧本配套产出物）

剧本技能在 `Characters.md`、`Scenes.md`、`Assets.md` 中可选交付 **参考图生成提示词**。与剧本正文、Brief 分离：提示词只锁外形与空间，不写剧情。

## 分类与路由

| 分类 ID | 名称 | 状态 | 用于 |
| --- | --- | --- | --- |
| `ref-mj` | **MidJourney** | 已实现 | 人物 sheet、勘景、英雄道具参考图 |
| `ref-gpt-image` | **ChatGPT Image2** | **占位** | 同上职责；语法待产品定稿后补，勿与 MJ 混写一条 |

**何时用哪一类**

- 用户或阶段 0 契约指定 **MidJourney** → 本文件下文 **MidJourney 规则**；参数 `--ar` / `--raw` / `--stylize 50`。
- 指定 **ChatGPT Image2** → 只写占位块：`<!-- TODO: ChatGPT Image2 — 待产品语法锁定；职责同 MidJourney 对应条目 -->`，并保留中文勘景说明；不要臆造 API 字段。
- 未指定且 **产出提示词=开** → 默认 **MidJourney**。

视频类提示词（Seedance / H3）由 `storyboard-development` 与各自技能负责，不写进三份附件。

## 产出开关（与阶段 0 联动）

在阶段 0 记录：

```text
产出参考图提示词：开 | 关
参考图分类（可多选）：MidJourney | ChatGPT Image2
```

- **关**：三份附件只有中文说明，不出现 `` ```prompt `` 代码块。
- **开**：在每条需要参考图的条目下增加对应分类的提示词块；文件 intro 可保留中文规则，**prompt _fence 内语言按分类**（MJ 为英文整段）。

同步或重写附件时，若开关为开，检查提示词与正文、道具表、连续性一致。

## MidJourney — 通用

- 每个 `` ```prompt `` 为 **一整段英文**，段末 `--ar … --raw --stylize 50`（不认 `--raw` 则删）。
- **不写**：角色名（剧本专名）、情节、场号、情绪解读；只写画面必须有什么。
- **纸面/标签原文**：用英文 **双引号**（如 `"06/11"`、`"Ask me where the red dot goes."`），否则模型不会当字来画。
- 背景：人物/道具 → 纯中灰无缝棚、均匀光；勘景同样 **无人无脸**。
- 写清 **尺寸、材质、explicit negatives**，防漂移。

## MidJourney — 人物（Characters.md）

- **4:3 三分屏**：左全身正面 | 中全身背面 | 右栏上脸正特写、下脸侧特写；**同一人**同脸同发同衣。
- 全身 panel = full/wide shot；脸 = tight close-up。
- **普通人比例**，非模特；`arms at hips` 或 `arms down`，空手。
- **未成年**：不写具体年龄数字；MJ 易拦 photoreal 全身时，中文说明可改实拍 wardrobe，不硬逼 sheet。
- 易歧义角色写明性别（如 `Man, adult`）。
- 工牌/布标等 **剧本原文** 可写 `exactly …`。
- 仅手出场、不出镜角色：**不设** MJ 块。

## MidJourney — 道具（Assets.md）

| 状态数 | 比例 | 写法 |
| --- | --- | --- |
| 1 | 1:1 | 正面居中 |
| 2（同物） | 2:1 | **一条**提示词，左右等分、同尺度 |
| 3（同物） | 3:1 | 一条，三等分 |

- WHITE ROOM = **无框绷框画布正面**（布面颜料）；红点 **偏高、小、准**，跨 I / IX / 灰画布 **比例一致**。
- 多状态示例：盒（合盖 | 开盖空腔）、纸条（有字 | 无字）、画布（无点 | 有点）、伞（伞面 | 伞底）。
- 头带与纺锤 **分两条 1:1**；头带额心 **一个空圆孔**，纺锤单独、腰身可入孔，**图内不安装**（安装关系写中文，正片/H3 负责）。
- 画廊等 **勘景不在 MJ 画具体画作** 时，Scenes 侧用空白画布；画作细节只在 Assets 画布条目。

## MidJourney — 场景（Scenes.md）

- **一条 16:9 单帧**大全景（极广角 / 读全室），**不要**三视图拼贴、不要 16:27 分格。
- 无人、无脸；勘景不摆英雄道具细节（道具有独立 Assets 图）。
- 中文说明可写全片调色倾向；英文 prompt 保持简洁 `photoreal, low saturation, medium contrast` + 本空间光线与陈设。

## 维护

项目范例：`Screenplays/The Pain We Sell/` 下 `Characters.md`、`Scenes.md`、`Assets.md`。

规则变更时同步本文件与 `storyboard-development/prompt-generation.md` 中的交叉引用。
