---
name: minimax-h3-prompt
description: Writes MiniMax H3 / H3 Max / 海螺 / Hailuo / MiniMax Design video prompts using the official product formula (duration, ratio, four elements, three input modes, 图N/视频N/音频N binding). Use when the user mentions MiniMax H3, H3 Max, 海螺 AI, Hailuo, 全能参考, 首尾帧, T2VA, I2VA, FL2VA, Ref2VA, or H3-Context-IR. Do not use Seedance templates for these jobs.
---

# MiniMax H3 提示词

写任何 MiniMax H3 / 海螺 / Hailuo / MiniMax Design 提示词之前，先读本技能与 [reference.md](reference.md)。禁止套用 Seedance 的整数秒分镜模板。

权威来源：

- 产品手册：[MiniMax H3 模型 - 使用手册](https://vrfi1sk8a0.feishu.cn/wiki/FIWjwgL33ipnkekzk30crmKUnIh)
- 规格与入口：[视频生成](https://platform.minimaxi.com/docs/guides/video-generation)
- 案例：[H3 亮点功能示例](https://platform.minimaxi.com/docs/guides/video-prompt)
- 英文结构化改写（仅 Context-IR / API）：[base](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md) / [ref](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)

## 模型分流

- MiniMax H3、H3 Max、海螺、Hailuo、MiniMax Design、全能参考、首尾帧 → 本技能。
- Seedance、即梦、火山方舟 → `seedance-prompt`。
- 用户没点名模型时，先问用哪套；不要默认写成 Seedance。

H3 默认产出 **4–15 秒一条成片**，不是 30 秒一段再向后延长。H3 Max 为 5–15 秒。时长只接受整数。

## 硬约束

1. 把模型当成视听一体的内容生产者：画面、动作、镜头、对白、音效、BGM 写在同一条提示词里。
2. 先定模式，再写词。文生、首/尾帧、全能参考的素材角色不同，不要混用 `first_frame` 与 `reference_image`。
3. 提示词用完整中文句子，不要堆英文关键词。台词、歌词、屏幕上的字保留原文，不要翻译。
4. 有参考素材时，按上传顺序写成 `图1 / 图2 / 视频1 / 音频1`，并写清参考的是外形、场景、道具、动作、运镜、节奏、音色还是整段声音。不要只在图上写人名，提示词里却直接用人名。
5. 一条提示词只装得下一件主事件。15 秒里不要塞预告片式多场戏。
6. 负向控制写具体、可观察的画面或声音，不要空泛的「高质量 / cinematic / 精美」。
7. 默认交付 **可直接贴进海螺 / MiniMax Design 的整段中文提示词**。只有用户明确要 Context-IR 或 API 英文改写时，才改用英文三字段 / 六字段。

## 整体公式

```
[规格] 时长 + 画幅 + 画质意图
[绑定] 图N / 视频N / 音频N 各负责什么、不负责什么
[主体] 谁或什么，外形锁定
[场景] 在哪，光线、材质、风格、气质
[运动] 按时间顺序发生的一件事，含人物反应
[镜头] 景别、机位、运镜；需要时才写幅度和速度
[声音] 环境音、动作音、台词原文、BGM 或明确不要配乐
```

可贴入的成稿把以上内容收成连贯段落，不要输出成标签列表。规格和绑定放在最前。

## 四个要素

| 要素 | 写什么 | 失败写法 |
| --- | --- | --- |
| 主体 | 外貌、服装、体态、关键道具；有图则绑图，无图则写死不可改的规格 | 「一个美女」「那个年轻人」 |
| 场景 | 空间结构、时间、光线、材质、风格（电影感、真人实拍、2D、3D、粘土、水彩、胶片、国风等） | 只写「高级质感」 |
| 运动 | 从哪个状态到哪个状态，谁对什么做了什么 | 并列一堆互不衔接的动作 |
| 声音 | 环境、物体、口型内对白、画外音、角色能听见的音乐、观众才能听见的 BGM | 完全不写声音，或把对白写进 BGM |

镜头不是第五个标签，而是把运动落到画面上的方法。细则见 [reference.md](reference.md)。

## 三类模式

先判断入口，再写提示词。

| 模式 | 素材 | 提示词重点 |
| --- | --- | --- |
| 文生视频 | 只有文本 | 从零建立主体、场景、运动、声音；画幅必填，不能写自适应 |
| 图生视频 | 文本 + 首帧和/或尾帧 | 不要复述静帧。首帧：从图里的状态往前发展；尾帧：先写合理前史，最后落到图；首尾帧：写中间路径，优先一镜插值 |
| 全能参考 | 文本 + 图/视频/音频，合计 ≤12 个文件 | 每条素材只承担一种职责。外形用图，动作用视频，音色用音频。写明「参考什么、不参考什么」 |

素材上限（全能参考）：图 ≤9，视频 ≤3 且总时长 ≤15 秒，音频 ≤3 且总时长 ≤15 秒。单段视频/音频 2–15 秒。

## 每次必须输出

1. **模式与规格**：文生 / 首帧 / 尾帧 / 首尾帧 / 全能参考；时长；画幅。
2. **素材清单**：无素材则写「纯文本直出」。
3. **可贴入提示词**：一整段中文，开头含时长与画幅，随后绑定、故事、镜头、声音。
4. **不要做**：3–6 条，针对换脸、换装、跑题、多场戏、乱加字幕或乱加 BGM。

用户只给模糊题材时，先问模式、时长、画幅、有无参考，再写词。不要直接开写。

## 检查

交付前按 [reference.md](reference.md) 的检查表过一遍。与飞书手册或开放平台文档冲突时，以官网文档为准。
