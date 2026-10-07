"""Turn storyboard shorthand in an H3 paste into sentences a video model can stage.

Frame words, unfinished actions, and exposure labels (浅灰 / 亮明) stay in the
crew contrast block. The paste must say where the light falls and where a
gesture stops.
"""

from __future__ import annotations

import re

_LEVELS = (
    ("亮明偏绿", "bright_green"),
    ("亮明", "bright"),
    ("浅灰", "light_gray"),
    ("深灰", "dark_gray"),
    ("阴暗", "dim"),
    ("灰白", "gray_white"),
    ("黑", "black"),
    ("白", "white"),
)

_GRAY_WORDS = ("浅灰", "深灰", "阴暗", "灰白")
_PERSON = re.compile(r"图\d+|人物|脸|手(?!机)|她|两人|主体|人群|(?<!过)肩|眼睛|双脸")


def _clean(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def _norm(subj: str, kind: str | None = None) -> str:
    name = _clean(subj).strip("的仍")
    name = name.replace("前景肩", "前景的肩")
    fixed = {
        "纸": "纸面",
        "河": "河面",
        "伞": "黄伞",
        "画": "白画",
        "人脸": "脸",
        "眼神光": "眼睛里的高光",
        "盒体": "盒子",
        "城市点光": "城市的点光",
        "厅内金色": "厅内的金色光",
        "前区金色": "前区的金色光",
        "六月日光": "六月的日光",
        "过肩前景": "过肩的前景",
        "中间地面": "中间的地面",
        "窗外": "窗外",
        "远端脸": "远处的脸",
        "双脸": "两张脸",
        "板": "板面",
        "白": "白色部分",
        "侧光": "侧光",
        "绿光": "绿色的光",
        "火": "火",
        "桌": "桌面",
    }
    if name in fixed:
        if name == "画" and kind not in (None, "white"):
            return "画"
        return fixed[name]
    name = name.replace("同为", "")
    name = re.sub(r"(图\d+)脸", r"\1的脸", name)
    name = re.sub(r"(图\d+)肩", r"\1的肩", name)
    name = re.sub(r"(图\d+)前景的肩", r"\1前景的肩", name)
    if name.endswith("冷"):
        name = name[:-1]
    return name or "画面"


def _person(name: str) -> bool:
    if "高光" in name:
        return False
    return bool(_PERSON.search(name))


def _place(name: str) -> str:
    if name.endswith("脸") or name.endswith("眼睛"):
        return f"打在{name}上的光"
    if name.endswith("手") or name.endswith("肩"):
        return f"打在{name}上的光"
    if _person(name):
        return f"打在{name}身上的光"
    return ""


def _on(name: str, label: str) -> str:
    if name in ("字", "纺锤") and "黑" in label:
        return f"{name}保持黑色"
    if "高光" in name:
        return f"{name}保持{label}"
    if label == "更暗":
        place = _place(name)
        if place:
            return f"{place}更暗"
        if name in ("四周", "周围", "背景", "环境", "后排"):
            return f"{name}更暗"
        return f"{name}保持阴暗"
    place = _place(name)
    if place:
        return f"{place}保持{label}"
    return f"{name}保持{label}"


def _dim_label(kind: str) -> str:
    return {
        "light_gray": "浅灰亮度",
        "dark_gray": "深灰亮度",
        "dim": "更暗",
        "black": "接近全黑的亮度",
        "gray_white": "灰白亮度",
    }[kind]


def _render_level(name: str, kind: str, rim: str | None, compared: str | None) -> str:
    cold = _clean(name).endswith("冷")
    name = _norm(name, kind)
    if rim == "cool":
        if _person(name):
            return f"打在{name}身上的冷侧逆光保持浅灰亮度"
        return f"{name}上的冷侧逆光保持浅灰亮度"
    if rim == "rim" and kind in ("light_gray", "dark_gray", "dim", "black", "gray_white"):
        label = _dim_label(kind if kind != "gray_white" else "gray_white")
        if name.endswith("脸"):
            return f"打在{name}上的侧逆光保持{label}"
        if _person(name):
            return f"打在{name}身上的侧逆光保持{label}"
        return f"{name}上的侧逆光保持{label}"
    if kind == "bright_green":
        core = f"{name}保持发亮的绿色"
        return f"{core}，比{compared}更亮" if compared else core
    if kind == "white":
        core = f"{name}保持冷白色的高亮度" if cold else f"{name}保持白色的高亮度"
        return f"{core}，比{compared}更亮" if compared else core
    if kind == "gray_white":
        return f"{name}的光保持灰白亮度"
    if kind == "bright":
        target = compared or "周围"
        place = _place(name)
        if place:
            return f"{place}比{target}更亮"
        return f"{name}比{target}更亮"
    label = _dim_label(kind)
    return _on(name, label)


def _parse_segment(seg: str):
    seg = _clean(seg).replace("同为", "")
    if not seg:
        return None
    if seg in ("不显示记忆图像", "无记忆图像"):
        return ("memory",)
    if "最强反差" in seg:
        return ("contrast",)
    if "吞掉轮廓" in seg:
        return ("swallow", seg)
    if "勾开肩线" in seg:
        cool = "冷" in seg
        return ("rim_shoulder", cool)
    if "压暗" in seg:
        return ("press",)
    if "同级" in seg and "浅灰" in seg:
        return ("same",)
    if "保留红" in seg:
        return ("keep_red", seg)
    if "红点" in seg and "最强" in seg:
        return ("red_dot",)
    if any(token in seg for token in ("走入", "进入", "升至")) and any(
        token in seg for token in ("浅灰", "深灰", "亮明")
    ):
        return ("transition", seg)
    if seg == "冻结时轻降饱和":
        return ("desat",)
    if seg == "唯一饱和高对比":
        return ("sat",)
    if "全黑" in seg:
        return ("door_black", seg)
    if "亮黄" in seg:
        return ("yellow", seg.replace("亮黄", ""))
    rim = None
    body = seg
    if "冷侧逆光" in body:
        rim = "cool"
        body = body.replace("冷侧逆光", "")
    elif "侧逆光" in body:
        rim = "rim"
        body = body.replace("侧逆光", "")
    if body.endswith("亮") and "亮明" not in body and "亮黄" not in seg:
        return ("level", body[:-1], "bright", rim)
    for token, kind in _LEVELS:
        if body.endswith(token):
            return ("level", body[: -len(token)], kind, rim)
    for token, kind in _LEVELS:
        if token in body:
            return ("level", body.replace(token, "", 1), kind, rim)
    return ("raw", seg)


def _transition(seg: str) -> str:
    match = re.match(
        r"(.+?)(?:从|由)(亮明|浅灰|深灰|阴暗)(?:走入|进入|局部升至|升至)(浅灰|深灰|亮明)",
        _clean(seg),
    )
    if not match:
        return seg
    who, start, end = match.group(1), match.group(2), match.group(3)
    who = _norm(who)
    words = {"亮明": "较亮", "浅灰": "浅灰亮度", "深灰": "深灰亮度", "阴暗": "更暗"}
    if "升" in seg:
        place = f"{who}上" if who.endswith("脸") else f"{who}身上"
        return f"打在{place}的光从{words[start]}局部升到{words[end]}"
    if start == "亮明":
        return f"{who}从较亮的光走进{words[end]}里"
    place = f"{who}上" if who.endswith("脸") else f"{who}身上"
    return f"打在{place}的光从{words[start]}走进{words[end]}"


def human_brightness(clause: str) -> str:
    """Rewrite one exposure clause. Input may include the label prefix."""
    text = clause.strip().strip("。")
    text = re.sub(r"^这一镜的光是", "", text)
    raw_parts = [part.strip() for part in re.split(r"[、，；]", text) if part.strip()]
    parsed = [item for item in (_parse_segment(part) for part in raw_parts) if item]

    dim_names = []
    for item in parsed:
        if item[0] == "level" and item[2] in ("light_gray", "dark_gray", "dim", "black"):
            dim_names.append(_norm(item[1], item[2]))

    bits: list[str] = []
    for item in parsed:
        kind = item[0]
        if kind == "memory":
            bits.append("屏幕上不要出现记忆里的画面")
        elif kind == "contrast":
            bits.append("这块的反差最强")
        elif kind == "swallow":
            bits.append("白墙亮到把轮廓吞掉")
        elif kind == "rim_shoulder":
            bits.append("冷的侧逆光把肩线从暗里勾出来" if item[1] else "侧逆光把肩线从暗里勾出来")
        elif kind == "press":
            bits.append("周围再压暗")
        elif kind == "same":
            bits.append("两张脸上的光保持同样的浅灰亮度")
        elif kind == "keep_red":
            inner = item[1].replace("并保留红色", "").replace("保留红色", "")
            inner_parsed = _parse_segment(inner)
            if inner_parsed and inner_parsed[0] == "level":
                bits.append(_render_level(inner_parsed[1], inner_parsed[2], inner_parsed[3], None))
            bits.append("红色留在笔尖上")
        elif kind == "red_dot":
            bits.append("红点是画面里最亮的一点")
        elif kind == "transition":
            bits.append(_transition(item[1]))
        elif kind == "desat":
            bits.append("画面冻结时饱和略降")
        elif kind == "sat":
            bits.append("这一镜的饱和更高，对比更强")
        elif kind == "door_black":
            if "门" in item[1]:
                bits.append("门合上之后，画面落到全黑")
            else:
                bits.append(f"{_norm(item[1])}落到全黑")
        elif kind == "yellow":
            umbrella = _norm(item[1], "white") or "黄伞"
            other = dim_names[0] if dim_names else "周围"
            bits.append(f"{umbrella}比{other}更亮，并保持黄色")
        elif kind == "level":
            compared = dim_names[0] if item[2] in ("bright", "white", "bright_green") and dim_names else None
            if compared and _norm(item[1], item[2]) == compared:
                compared = dim_names[1] if len(dim_names) > 1 else None
            bits.append(_render_level(item[1], item[2], item[3], compared))
        else:
            if item[1] == "人群含混":
                bits.append("人群看不清，只留成一片")
            else:
                bits.append(item[1])

    sentence = "，".join(bits)
    sentence = re.sub(r"，+", "，", sentence).strip("，")

    gray = any(word in text for word in _GRAY_WORDS)
    person = bool(_PERSON.search(text)) or "双脸" in text
    figs = list(dict.fromkeys(re.findall(r"图\d+", text)))
    bans: list[str] = []
    if gray or (person and "黑" in text and "字黑" not in text):
        bans.append("不要把画面罩成灰雾")
    bare_person = bool(re.search(r"人物|(?<!图)脸|手(?!机)|她|两人|主体|人群|眼睛|双脸", text))
    if person and (gray or any(token in text for token in ("浅灰", "深灰", "阴暗", "黑"))):
        if figs and not bare_person:
            bans.append(f"不要改{'和'.join(figs)}衣服的颜色")
        else:
            bans.append("不要改衣服的颜色")
    if "亮黄" in text or "黄色" in sentence:
        bans.append("不要改黄伞的黄色")
    if "偏绿" in text or "绿色" in sentence:
        bans.append("不要把绿色改掉")
    if "金色" in text:
        bans.append("不要把金色改掉")
    if "红" in text and any(token in text for token in ("红点", "红笔", "保留红")):
        bans.append("不要把红色改掉")
    if "纺锤" in text and "黑" in text:
        bans.append("不要把纺锤改成别的颜色")

    # door-black and pure object black should not grow a fog sentence by themselves
    if text in ("门合后全黑", "衣橱黑") or (not gray and "黑" in text and not person):
        bans = [ban for ban in bans if ban != "不要把画面罩成灰雾"]

    if bans:
        sentence += "。" + "，也".join(bans) if False else "。" + bans[0]
        if len(bans) > 1:
            sentence += "，也" + "，也".join(bans[1:])
    if not sentence.endswith("。"):
        sentence += "。"
    sentence = sentence.replace("。。", "。")
    return sentence


def fix_frame_words(paste: str) -> str:
    """Replace crew frame-direction words. Leave 白画 and existing 画面左/右 intact."""
    protected = paste.replace("白画", "\u0001")
    replacements = (
        ("从画右下", "从画面右下边缘"),
        ("从画左下", "从画面左下边缘"),
        ("从画下", "从画面下边缘"),
        ("向画右", "朝画面右侧"),
        ("向画左", "朝画面左侧"),
        ("画右画外", "画面右侧的画外"),
        ("画左画外", "画面左侧的画外"),
        ("松握在画下", "松握在画面下方"),
        ("握在画下", "握在画面下方"),
    )
    for src, dst in replacements:
        protected = protected.replace(src, dst)
    protected = re.sub(r"(?<!面)画左", "画面左侧", protected)
    protected = re.sub(r"(?<!面)画右", "画面右侧", protected)
    return protected.replace("\u0001", "白画")


def fix_unfinished(paste: str) -> tuple[str, str | None]:
    """Stop gestures before contact. Returns paste and an extra ban, if any."""
    extra = None
    old = "手从画面右下边缘伸向图1颈部，接触尚未发生。"
    new = "手从画面右下边缘伸向图1的颈部，指尖靠近颈部，在碰到皮肤之前停住。"
    if old in paste:
        paste = paste.replace(old, new)
        extra = "不要让手碰到或抓住颈部"
    elif "接触尚未发生" in paste:
        paste = paste.replace("接触尚未发生", "在碰到皮肤之前停住")
        extra = "不要让手碰到或抓住"
    if "一只手尚未进入" in paste:
        paste = paste.replace("一只手尚未进入", "一只手还停在画面外，不要伸进画里")
        extra = "不要让手伸进画面"
    paste = paste.replace("Gabriel从话筒", "从话筒")
    if "半步" in paste:
        paste = paste.replace("半步", "很小的一步，迈完就停")
    if "将扣腕" in paste:
        paste = paste.replace("将扣腕", "靠近手腕，在碰到皮肤之前停住")
        extra = extra or "不要让手碰到或抓住手腕"
    return paste, extra
