# THE PAIN WE SELL — 道具

对应交付稿：`Screenplay.md`（同目录）。

只收两件都满足的东西：它推动情节，而且会在不同场次里被拿来对照，外形或文字一变，前后就对不上。只出现一次、对白已经说清、或换一件也不影响因果的物件不进这张表。

参考图比例按状态数走：**一种状态** → 1:1，正面直拍，物件居中；**两种状态**（同一物件前后对照）→ 合并成**一条**提示词，**2:1**，左格状态一、右格状态二，两格同大、同尺度、同一外形轮廓；**三种状态** → 一条提示词，**3:1**，三等分竖屏。背景均为纯中灰无缝摄影棚，无手、无人。MidJourney 提示词是标注为 prompt 的一整段英文，只描述物体与画面，不写剧情。

WHITE ROOM 系列锁的是**无装饰框的绷框画布正面**：观众看见的是布面上的画，不是装裱、不是玻璃。角上的署名和湿漆都画在**布面**上。

画面上的字以剧本原文为准，生成错了只改字，不改外形。红点全片只有一个位置：偏高，小而准，像夜里惊醒后第一眼会去看的地方；I 完成态、IX、灰画布三处的红点**比例位置必须一致**。若版本不认 `--raw`，删掉这个词再生成。

---

## 红点与三块必须互相对上的画

系列的秘密是同一个红点。厨房里母亲按练习板点上 WHITE ROOM I，画廊里每幅白画靠边缘都有这一点，工作室墙上的 WHITE ROOM IX 窗边也是这一点，Naomi 后来在灰画布上点的也是这一点。Gabriel 要能在 IX 和那块灰画布之间看出「同一位置」。

点的规则固定为：偏高，像夜里惊醒后第一眼会去看的地方。小，准。全片不要每幅各点各的。

**WHITE ROOM IX（实物，两套状态）：**

- 六年前的衣橱里：下角是未干的黑漆半签名 `C. BENN`，刷子在橱底。红点已经在。
- 当下的工作室墙上：同一幅画，下角被一块较新、较平的白盖住。清晨他用调色刀揭开，露出同一个 `C. BENN`，然后停手，不补成 `BENNETT`。

拍卖厅屏幕上的是 **WHITE ROOM I**，署名仍是 **Gabriel Mora**。它不进拍的是 IX。图录若入画，只能是 I–VIII，不能把 IX 写进去。

I 到 VIII 共用完成态；厨房未完成与完成态在**同一条 2:1** 里左右对照。IX 衣橱半签与工作室白盖也在**同一条 2:1** 里对照。灰画布一条 2:1：左格他找不到点时的纯灰，右格她点上之后的同一块。刷子是衣橱地面陈设，不单做道具图。

**MidJourney · WHITE ROOM I（厨房未完成 | 完成态）**

```prompt
One 2:1 image, two equal vertical panels, same unframed stretched canvas size and proportions in both panels, straight-on front view, gray margin around the full image, seamless pure medium-gray studio, even soft light, no hands, photoreal object photograph. Left panel, in-progress state: almost-white minimalist empty room with a metal bed rail painted, sheets at the foot unfinished, raw underpainting visible, no red dot, no signature, no text. Right panel, finished state: the same canvas and same room layout, bed rail complete, neatly folded white sheets at the foot, one tiny sharp red circle high in the upper third near the painting edge, lower corner black paint handwriting exactly Gabriel Mora. No window, no figure in either panel. --ar 2:1 --raw --stylize 50
```

**MidJourney · WHITE ROOM IX（衣橱半签 | 工作室白盖）**

```prompt
One 2:1 image, two equal vertical panels, the same unframed stretched canvas and the same painting composition in both panels, straight-on front view, gray margin around the full image, seamless pure medium-gray studio, even soft light, no hands, photoreal object photograph. Both panels: almost-white empty room with one simple window, no bed rail, one tiny sharp red circle beside the window high in the upper third, same dot size and height band as the finished Room I right panel. Left panel, closet state: lower corner glossy wet black paint, letters stop at C. BENN, paint looks wet. Right panel, studio state: lower corner covered by a newer flatter white paint patch, slightly different white from the field, no letters visible. --ar 2:1 --raw --stylize 50
```

**MidJourney · 灰画布**

```prompt
One 2:1 image, two equal panels, same unframed stretched canvas, front face only, gray gesso primer, no painted room, no bed, no window, no signature, gray studio, no hands, photoreal. Canvas gray must read as gesso, not the backdrop. Left: blank gesso, no red dot. Right: the same canvas with one tiny sharp red circle high in the upper third, same proportional placement as the White Room dots. --ar 2:1 --raw --stylize 50
```

---

## 记忆三件套

柜台交出的透明盒里只有三样，而且是同一套走到结尾：

- **黑色玻璃纺锤。** 指节大小，唯一一份。舱里装头带看记忆；工作室另用薄型播放器，仍是这根纺锤。
- **银色头带。** 额前薄带，**不是丝带**。外侧面 **`06/11`**，额心 **一个圆孔** 装纺锤；参考图屏不亮。
- **封口信封与卡片。** 柜台封着；卡片一句：`Ask me where the red dot goes.`

摘录时间：`3:36:02`–`3:48:10`。头带日期：`06/11`。

- **透明盒。** 掀盖 clamshell，约 **14×10×4 cm**，厚壁透明塑料，全片同一只。参考图只锁盒子的两个视图，盒内不放三件套。
- **头带、纺锤各一条。** 头带额心只有一个空的圆孔，孔径对着纺锤腰身，参考图里不放入纺锤。纺锤单独锁外形，腰身能塞进那个圆孔。播放器不进这两张图。

头带、纺锤、信封、卡片各 **1:1**；透明盒 **一条 2:1 两视图**。

**MidJourney · 透明盒（合盖正面 | 开盖空腔）**

```prompt
One 2:1 image, two equal panels, the same empty clear plastic clamshell, about fourteen by ten by four centimeters, hinged on one long edge, thick clear walls, no label, gray studio, no hands, photoreal. Left: closed, straight-on front. Right: lid open, three-quarter view into the empty cavity, same box. Nothing inside either panel. --ar 2:1 --raw --stylize 50
```

**MidJourney · 银色头带**

```prompt
One thin silver forehead band lying flat, outer face up, two centimeters wide, not a ribbon, not headphones, no head, no hands, gray studio, photoreal, 1:1. Display dark. The only text is "06/11". One empty circular hole in the center of the band, large enough to seat a knuckle-sized spindle, hole clearly open, nothing inserted. No second hole. --ar 1:1 --raw --stylize 50
```

**MidJourney · 黑色玻璃纺锤**

```prompt
One knuckle-sized spindle of opaque black glass, lathe-turned, glossy, no logo, no text, gray studio, no hands, photoreal, 1:1. Narrow waist sized to fit a round hole in a thin band, shown alone, not inserted. --ar 1:1 --raw --stylize 50
```

**MidJourney · 封口信封**

```prompt
Small plain white envelope, flap sealed, blank front, no stamp or address. One 1:1, front view, gray studio, no hands, photoreal. --ar 1:1 --raw --stylize 50
```

**MidJourney · 卡片**

```prompt
One small off-white paper card, front view, centered, gray studio, no hands, photoreal. Large legible handwritten capital letters. The only text on the card is "Ask me where the red dot goes." No second line, no printed type. --ar 1:1 --raw --stylize 50
```

---

## 纸条

完整死亡记忆里展开后才能读；观影舱第一次只看见已经在烧的纸，不给读。勘景用无字纸，字以左格为准。火是拍摄动作，两格都不画烧痕。

银幕上是英文两行，与 Naomi 的英文复述 “one sentence” 以及盒内卡片的英文一致。动作行里的中文是读本，不印上纸。提示词里这两行必须放在英文双引号中，生成器才会把它当成要写上纸的字。字大，手抖，不得添句：

`You have one sentence.`  
`Tell Naomi the red dot is hers.`

**MidJourney · 纸条（有字 | 无字）**

```prompt
One 2:1 image, two equal panels, the same intact white paper sheet, no burn, gray studio, no hands, photoreal. Left panel only: large shaky handwritten capitals in exactly two lines. Line one text: "You have one sentence." Line two text: "Tell Naomi the red dot is hers." Right panel: blank paper, no text, no letters, no words. --ar 2:1 --raw --stylize 50
```

---

## 十二分钟的案卷

Naomi 从公寓带到工作室的是同一本手风琴夹，标签 `BENNETT, C. -- 06/11`。里面被引用的时间不能改：Gabriel 进门 `12:22`，报警 `12:34`，中间双圈 `12 MIN?`。她在工作室里口头重复的就是这三行。

时间线在夹内。这张参考只锁合上的夹和封面标签，避免外封面出现另一套时间。

**MidJourney**

```prompt
One closed thick accordion expansion file folder, front cover toward camera, manila or board color, metal accordion spine visible at the side, not open, no papers sticking out. Neat printed label on the front cover. The only text on the label is "BENNETT, C. -- 06/11". No other words or times on the cover. One 1:1 image, straight-on front view, folder centered, gray margin. Seamless pure medium-gray studio, even soft light, no hands, photoreal object photograph. --ar 1:1 --raw --stylize 50
```

---

## 黄伞

开场镜头在伞下向外看。扣下不卖的 3C 就是这段。结尾 Naomi 说「I was holding the umbrella」时，观众要能对上这把黄伞。伞不需要再出现一次。参考图锁同一把撑开的伞：左格伞面朝外，右格从伞底往上看，对应开场在伞下的视角。

**MidJourney · 黄伞（伞面 | 伞底）**

```prompt
One 2:1 image, two equal panels, the same open umbrella, bright saturated yellow canopy, not green, not orange, metal ribs visible, simple straight handle, dry, no rain, no person, gray studio, photoreal. Left: exterior of the canopy toward camera, handle pointing down. Right: underside of that same canopy, looking up into the yellow fabric and ribs, same handle. --ar 2:1 --raw --stylize 50
```
