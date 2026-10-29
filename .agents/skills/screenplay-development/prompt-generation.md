# 参考图提示词（剧本配套产出物）

剧本技能在 `Characters.md`、`Scenes.md`、`Assets.md` 中可选交付 **参考图生成提示词**。与剧本正文、Brief 分离：提示词只锁外形与空间，不写剧情。

## 分类与路由

| 分类 ID | 名称 | 状态 | 用于 |
| --- | --- | --- | --- |
| `ref-mj` | **MidJourney** | 已实现 | 人物 sheet、勘景、英雄道具参考图 |
| `ref-gpt-image` | **ChatGPT Image2** | **占位** | 同上职责；语法待产品定稿后补，勿与 MJ 混写一条 |

**何时用哪一类**

- 用户或阶段 0 契约指定 **MidJourney** → 本文件下文 **MidJourney 规则**；**参考图不写任何 MJ 参数**，画幅、画质与风格用英文句子描述。
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

- 每个 `` ```prompt `` 为 **两段英文**（形象段 + 风格段，中间空一行）；**参考图不写任何 MJ 参数**；画幅不写进 prompt（界面设置），画质、风格与负面词写进句子。
- **不写**：角色名（剧本专名）、情节、场号、情绪解读；只写画面必须有什么。
- **纸面/标签原文**：用英文 **双引号**（如 `"06/11"`、`"Ask me where the red dot goes."`），否则模型不会当字来画。
- **背景（硬）**：人物（`Characters.md`）与道具（`Assets.md`）**同样**强调**纯色底**——默认 **纯白 seamless cyclorama**（`Seamless pure white cyclorama, wall and floor the same pure white`；风格段前置）；**禁止**灰棚、彩色棚、渐变棚、场景底、桌面／地面杂物当背景。勘景（`Scenes.md`）不套此白棚规则，但同样 **无人无脸**。
- **打光（硬）**：人物与道具参考图一律**无打光状态**——风格段写 `unlit flat ambient, no key light, no rim light, no dramatic studio lighting`（可紧接纯白底之后）；禁止 soft key／rim／三点光／戏剧棚光。主体自发光（如眼灯、屏显）属**形象态**，写在形象段，不算打光。勘景不受此条约束。
- 写清尺寸、材质、explicit negatives，防漂移。

### 参数规则（硬）

- **参考图（Characters / Scenes / Assets）零参数**：不在句末追加任何 MJ 参数；画幅不写进 prompt（界面设置），画质、风格、负面词写进英文句子。
- **关键帧**（由 `storyboard-development` 负责）：只保留 `--no` 负面参数，默认 `--no photorealistic, 3D render, anime`；`--ar`、`--raw`、`--stylize` 等一律不写；画幅不写进 prompt，风格写进句子。
- 参数不能替代画面描述；生成时在模型界面设置比例与画质。

### 资产提示两段式（硬）

`Characters.md` / `Scenes.md` / `Assets.md` 的每条 prompt 固定两段，中间空一行：

1. **形象段**：只写主体长什么样、穿什么、什么姿态、画面里有什么；**一图只含一态**；不写画风、渲染、背景光、负面词。
2. **风格段**：只写画风、线条、上色、材质、背景、光线与负面项；不引入新的主体内容。

- 两段都是英文完整句子；不写角色名、剧情、场号、画幅比例、MJ 参数。
- 风格段可在同一文件内复用，但必须与形象段一致；不要把风格词塞回形象段。
- 关键帧提示不适用本规则；关键帧保持一段，只保留 `--no`。

## MidJourney — 人物（Characters.md）

**硬规则：纯色底。** 与道具相同：风格段必须以纯白 seamless cyclorama 开头（wall and floor the same pure white）；`no gray backdrop, no colored backdrop`；禁止灰棚／彩色棚／场景底。
**硬规则：无打光。** 与道具相同：风格段用 `unlit flat ambient, no key light, no rim light, no dramatic studio lighting`；禁止 soft key／rim／戏剧棚光。

- **单人正视图**（画幅在界面设置，不写进 prompt）：全身正面，头到脚；**同一人**同脸同发同衣。
- 正视图 = full-body front shot；人物居中，留头顶与脚下空间；**不生成**背面、侧面、脸部特写或多视图拼贴。
- **普通人比例**，非模特；`arms at hips` 或 `arms down`，空手。
- **未成年**：不写具体年龄数字；MJ 易拦 photoreal 全身时，中文说明可改实拍 wardrobe，不硬逼 sheet。
- 易歧义角色写明性别（如 `Man, adult`）。
- 工牌/布标等 **剧本原文** 可写 `exactly …`。
- 仅手出场、不出镜角色：**不设** MJ 块。

## MidJourney — 道具（Assets.md）

**硬规则：纯色底（同人物）。** 道具参考图与人物 sheet **同一套纯色底要求**：风格段前置 `Seamless pure white cyclorama, wall and floor the same pure white, no gray backdrop, no colored backdrop`；禁止灰棚、彩色棚、渐变棚、柜台／橱窗／场景底当背景；单物居中，背景不抢识别。
**硬规则：无打光（同人物）。** 风格段写 `unlit flat ambient, no key light, no rim light, no dramatic studio lighting`；禁止 soft key／rim／戏剧棚光。眼灯／屏显等自发光只写进形象段的该态，不算打光。

**硬规则：每态独立。** 每个可辨视觉状态＝独立资产条目＝独立一条 `` ```prompt ``；**一图只画一态**。禁止把多状态混合产出在一张图上；禁止 `one image, two/three equal panels`、`Left panel` / `Right panel` 等拼贴写法。

| 条目 | 画布比例（界面设置，不写进 prompt） | 写法 |
| --- | --- | --- |
| 任一单态 | 默认 1:1 | 正面（或该态所需视角）居中；整物可读 |

- 同一英雄道具有多种状态时：在 `Assets.md` 用**分条标题**（可同组下列出），每条各自完整两段式英文 prompt（形象＋风格）。公共外形句可复用，但**状态差异必须写清且单独成块**。
- 多状态示例（各自一条，勿拼盘）：盒·合盖；盒·开盖空腔；纸条·有字；纸条·无字；画布·无点；画布·有点；伞·伞面；伞·伞底。
- WHITE ROOM = **无框绷框画布正面**（布面颜料）；红点 **偏高、小、准**，跨 I / IX / 灰画布 **比例一致**（各态仍分条）。
- 头带与纺锤 **分两条单幅**（画幅界面设置）；头带额心 **一个空圆孔**，纺锤单独、腰身可入孔，**图内不安装**（安装关系写中文，正片/H3 负责）。
- 画廊等 **勘景不在 MJ 画具体画作** 时，Scenes 侧用空白画布；画作细节只在 Assets 画布条目。

## MidJourney — 场景（Scenes.md）

- **一条单帧大全景**（极广角 / 读全室；画幅在界面设置，不写进 prompt），**不要**三视图拼贴、不要 16:27 分格。
- 无人、无脸；勘景不摆英雄道具细节（道具有独立 Assets 图）。
- 中文说明可写全片调色倾向；英文 prompt 保持简洁 `photoreal, low saturation, medium contrast` + 本空间光线与陈设。

## 维护

项目范例：`Screenplays/The Pain We Sell/` 下 `Characters.md`、`Scenes.md`、`Assets.md`。

规则变更时同步本文件与 `storyboard-development/prompt-generation.md` 中的交叉引用。分镜技能另可选产出按镜关键镜帧（默认 **Nano Banana**，备选 **GPT Image**；文件 `Storyboard-Keyframes.md`，每镜一张开镜首帧构图静帧，含本镜资产表；**不再默认 MidJourney**）；职责是构图而非身份 sheet / 勘景 / 道具——身份锁定仍以本页三附件为准（三附件参考图可继续 MidJourney）。
