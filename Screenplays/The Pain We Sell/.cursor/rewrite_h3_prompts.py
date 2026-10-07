#!/usr/bin/env python3
"""Rewrite MiniMax H3.md paste blocks from Storyboard.md + Screenplay.md.

Paste text follows the H3 product formula: one coherent Chinese paragraph,
图N bindings, this shot's light, event order, original dialogue and screen text.
Crew names and P-/L-/A-/D codes stay in 素材 and 分镜对照 only.
"""
from __future__ import annotations

import re
from pathlib import Path

from h3_performable import fix_frame_words, fix_unfinished, human_brightness

ROOT = Path(__file__).resolve().parents[1]
SB_PATH = ROOT / "Storyboard.md"
H3_PATH = ROOT / "MiniMax H3.md"
SP_PATH = ROOT / "Screenplay.md"

HEIGHT = {
    "P-Naomi-31": 168,
    "P-Naomi-31-off": 168,
    "P-Naomi-13": 145,
    "P-Naomi-22": 165,
    "P-Gabriel-54": 183,
    "P-Gabriel-54-suit": 183,
    "P-Gabriel-34": 183,
    "P-Claire-34": 170,
    "P-Claire-36": 170,
    "P-Claire-45": 168,
    "P-Claire-48": 168,
    "P-Margot": 162,
    "P-Auctioneer": 175,
}

FAMILY = {
    "NAOMI": "Naomi",
    "GABRIEL": "Gabriel",
    "CLAIRE": "Claire",
    "MARGOT": "Margot",
    "ATTENDANT": "Attendant",
    "AUCTIONEER": "Auctioneer",
    "HAND": "Naomi",
}

FEMALE_FAM = {"NAOMI", "CLAIRE", "MARGOT", "HAND"}
MALE_FAM = {"GABRIEL", "ATTENDANT", "AUCTIONEER"}

SCENE_HEADS = [
    ("1.1", "## 第1场　哈德逊河滨步道·日（二十年前）"),
    ("2.1", "## 第2场　公寓·夜"),
    ("3.1", "## 第3场　买方柜台·夜"),
    ("4.1", "## 第4场　观影舱与短记忆·夜"),
    ("5A.1", "## 第5A场　工作室·夜"),
    ("5B.1M", "## 第5B场　完整观看与抉择"),
    ("6.1", "## 第6场　工作室余波与清晨"),
    ("7.1", "## 第7场　拍卖行走廊·傍晚"),
    ("8.1", "## 第8场　拍卖厅"),
    ("9.1", "## 第9场　河岸·夜"),
]

# Append a reference only when a body part is actually in frame and unbound.
EXTRA_ASSETS = {
    "1.2": [("P-Gabriel-34", "hand")],
    "4.5M": [("P-Gabriel-54", "hand")],
    "5A.30": [("P-Gabriel-54", "face")],
}

DUR_NOTE = {
    "1.5": "分镜 3 秒。H3 最短 4 秒，只把伞推出之后的停顿加长，动作不变。",
    "2.7": "分镜 3 秒。H3 最短 4 秒，只把离桌之后的停顿加长，动作不变。",
    "6.6": "分镜 3 秒。H3 最短 4 秒，只把停住的那一下加长，动作不变。",
    "5B.2M": "分镜 10 秒。对白按正常语速说不完，本条写成 15 秒。",
    "5B.46": "分镜 6 秒。对白按正常语速说不完，本条写成 15 秒。",
}

DROP_BITS = (
    "罪名尚未成立",
    "法律权属完成",
    "暗示太迟",
    "供下一镜冲出",
    "呼应第9场",
    "呼应第 9 场",
    "绿色母题首次出现",
    "作者权被无声提出",
    "缺席被钉回纸面",
)


def family_of(code: str) -> str:
    u = code.upper()
    for key in ("ATTENDANT", "AUCTIONEER", "GABRIEL", "CLAIRE", "MARGOT", "NAOMI", "HAND"):
        if key in u:
            return key
    return ""


def parse_storyboard(text: str) -> dict[str, dict]:
    shots: dict[str, dict] = {}
    blocks = re.split(r"(?=^##### 镜 )", text, flags=re.M)
    for block in blocks:
        m = re.match(r"##### 镜 ([0-9A-Za-z.M]+) · (D\S+) · (\d+)秒", block)
        if not m:
            continue
        fields: dict[str, str] = {}
        parts = re.split(r"\*\*(.+?)\*\*\s*\n", block)
        it = iter(parts[1:])
        for key, val in zip(it, it):
            fields[key.split("（")[0].strip()] = val.strip()
        shots[m.group(1)] = {
            "d": m.group(2),
            "sb_dur": int(m.group(3)),
            "fields": fields,
        }
    return shots


def field(shot: dict, *names: str) -> str:
    fields = shot["fields"]
    for name in names:
        if name in fields and fields[name] and "待" not in fields[name][:6]:
            return fields[name]
    return ""


def parse_h3(text: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    matches = list(re.finditer(r"(?m)^### ([0-9A-Za-z.M]+)　(\d+)秒　(.+?)毫米", text))
    for i, m in enumerate(matches):
        shot = m.group(1)
        if shot in out:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[m.start():end]
        am = re.search(r"\*\*素材：\*\*\s*(.+)", block)
        pm = re.search(r"\*\*可贴入：\*\*\s*\n+(.+?)(?=\n\*\*不要做)", block, re.S)
        assets = []
        if am:
            for n, code, note in re.findall(
                r"图(\d+)＝([A-Za-z0-9\-]+)(?:（([^）]*)）)?", am.group(1)
            ):
                assets.append({"n": int(n), "code": code, "note": note or ""})
        out[shot] = {
            "dur": int(m.group(2)),
            "mm": m.group(3),
            "assets": assets,
            "paste": pm.group(1).strip() if pm else "",
        }
    return out


def parse_screenplay(text: str) -> list[tuple[str, str, bool]]:
    lines: list[tuple[str, str, bool]] = []
    speaker = ""
    off = False
    buf: list[str] = []

    def flush():
        nonlocal buf
        if speaker and buf:
            raw = " ".join(x.strip() for x in buf if x.strip())
            raw = re.sub(r"\s+", " ", raw)
            if raw:
                lines.append((speaker, raw, off))
        buf = []

    for line in text.splitlines():
        m = re.match(r"^\*\*([^*]+)\*\*", line.strip())
        if m:
            flush()
            label = m.group(1).strip()
            off = "O.S." in label or "O.S" in label
            name = re.sub(r"\s*_\([^)]*\)_", "", label)
            name = re.sub(r"\s*\([^)]*\)", "", name).strip()
            speaker = {
                "YOUNG NAOMI": "Naomi",
                "MOM": "Claire",
                "AUCTIONEER": "Auctioneer",
                "ATTENDANT": "Attendant",
            }.get(name.upper(), name.title() if name.isupper() else name)
            if speaker.upper() == "ATTENDANT":
                speaker = "Attendant"
            continue
        if line.strip().startswith(">"):
            buf.append(line.strip().lstrip(">").strip())
            continue
        if line.strip().startswith("**") or line.startswith("## "):
            flush()
            speaker = ""
    flush()
    return lines


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9']+", "", s.lower())


def extract_deliveries(paste: str) -> list[tuple[str, str, bool, bool]]:
    """Return (pre, quote, off, silent), keeping the first readable copy of each line."""
    items = []
    seen: set[str] = set()
    for m in re.finditer(r"「([^」»]*?)(?:」|»)", paste):
        quote = m.group(1).strip()
        key = re.sub(r"[^a-z0-9]", "", quote.lower())
        if not key or key in seen:
            continue
        if " " not in quote and len(quote) > 18 and re.search(r"[a-z][A-Z]", quote):
            continue
        seen.add(key)
        pre = paste[max(0, m.start() - 140) : m.start()]
        cut = max(pre.rfind("」"), pre.rfind("。"), pre.rfind("\n"), pre.rfind("»"))
        pre = pre[cut + 1 :]
        off = "画外" in pre or "口型闭合" in pre or "不见口型" in pre
        silent = "无声" in pre or "不出声" in pre or "不要配人声" in pre
        items.append((pre, quote, off, silent))
    return items


def match_speaker(quote: str, pool: list, cursor: list) -> tuple[str, bool, str]:
    """Match a shot line to the next screenplay line. Return speaker, offscreen, canonical text."""
    nq = norm(quote)
    if len(nq) < 2:
        return "", False, quote
    window = pool[cursor[0] : cursor[0] + 12]
    for i, (speaker, line, off) in enumerate(window):
        nl = norm(line)
        if not nl:
            continue
        exact = nl == nq or nl.startswith(nq) or (len(nq) >= 8 and nq.startswith(nl))
        loose = len(nq) >= 10 and (nq in nl or nl in nq)
        if exact or loose:
            cursor[0] = cursor[0] + i + 1
            # Keep the shot's wording when it is a readable excerpt of a longer speech.
            canonical = line if (nl == nq or len(line) <= len(quote) + 8) else quote
            if " " not in quote and " " in line and nq in nl:
                canonical = line
            return speaker, off, canonical
    return "", False, quote


def fig_for_speaker(speaker: str, assets: list[dict]) -> str:
    want = {
        "Naomi": "NAOMI",
        "Gabriel": "GABRIEL",
        "Claire": "CLAIRE",
        "Margot": "MARGOT",
        "Attendant": "ATTENDANT",
        "Auctioneer": "AUCTIONEER",
    }.get(speaker, "")
    if not want:
        return ""
    hits = [a for a in assets if family_of(a["code"]) == want]
    if len(hits) == 1:
        return f"图{hits[0]['n']}"
    if want == "NAOMI":
        hits = [a for a in assets if family_of(a["code"]) == "HAND"]
        if len(hits) == 1:
            return f"图{hits[0]['n']}"
    return ""


def clean_delivery(pre: str, quote: str, speaker_fig: str, off: bool, silent: bool) -> str:
    known = {
        "gabriellookatthatriver": ("语气带着雨里的笑，语调收到最后一个词", "river"),
    }
    stress = ""
    sm = re.search(r"只重读\s*([A-Za-z']+)", pre)
    if sm and sm.group(1).lower() not in {"名字"}:
        stress = f"，只重读 {sm.group(1)}"
    elif re.search(r"只重读\s*名字", pre):
        stress = "，只重读名字"
    else:
        stress = "，整句不加重"
    tone = ""
    tm = re.search(r"语气[^，。:：]{0,22}", pre)
    if tm:
        tone = "，" + tm.group(0)
    key = norm(quote)
    if key in known and "语气" not in tone:
        tone = "，" + known[key][0]
        if known[key][1]:
            stress = f"，只重读 {known[key][1]}"
    if norm(quote) == norm("These are mine."):
        who = speaker_fig or "画面里的人"
        return f"{who}不出声，口型清晰可读为：「{quote}」。不要配人声"
    if silent:
        who = speaker_fig or "画面里的人"
        return f"{who}不出声，口型清晰可读为：「{quote}」。不要配人声"
    if off or not speaker_fig:
        if speaker_fig and off:
            return f"画外由{speaker_fig}出声，画面里的人不开口，口型闭合，语速正常{tone}{stress}：「{quote}」"
        if off or "画外" in pre:
            return f"画外有人说话，画面里的人不开口，口型闭合，语速正常{tone}{stress}：「{quote}」"
    who = speaker_fig or "画面里的人"
    return f"{who}开口，语速正常{tone}{stress}：「{quote}」"


def bind_sentence(asset: dict, kind: str, shot_text: str) -> str:
    n = asset["n"]
    code = asset["code"]
    note = asset.get("note") or ""
    if note:
        note = note.strip().replace("只借", "只借用")
        if note.startswith("只锁") and not note.startswith("只锁定") and not note.startswith("只借用"):
            note = "只锁定" + note[2:]
        tail = "" if ("不参考" in note or "不锁" in note) else "，不参考构图"
        if note.startswith("本镜"):
            return f"图{n}这一镜{note[2:]}{tail}。"
        if note.startswith("只"):
            return f"图{n}{note}{tail}。"
        return f"图{n}只锁定{note}{tail}。"
    if kind == "hand":
        if code.endswith("-34"):
            return f"图{n}这一镜只使用袖口、肩和伸进来的手，不露出正脸，不参考姿势和背景。"
        return f"图{n}这一镜只锁定手和袖口，手从画面右下进入，不露出脸，不参考姿势和背景。"
    if kind == "face":
        return f"图{n}只锁定这张人物参考的脸、身材和衣服，不参考姿势，不参考背景，不参考构图。"
    fam = family_of(code)
    if code.startswith("P-") or fam:
        if fam == "HAND":
            return f"图{n}只锁定一只女孩的手，不露出脸，不参考构图。"
        if re.search(r"肩背|肩后|后脑", shot_text):
            return f"图{n}这一镜只见肩背或后脑，不露出可辨认的正脸，不参考姿势。"
        return f"图{n}只锁定这张人物参考的脸、身材和衣服，不参考姿势，不参考背景，不参考构图。"
    if code.startswith("L-"):
        extra = ""
        if re.search(r"俯视|顶视|反打|主观俯", shot_text):
            extra = "这一镜是俯视或反打，沿用这张场景图的空间结构，不要另造一个房间。"
        return f"图{n}只锁定这张场景参考的空间结构和材质，不锁机位，不参考构图。{extra}"
    if code.startswith("A-Phone"):
        return f"图{n}只锁定手机的外形。要读屏幕就只拍屏幕那一面；正脸旁边只许看见背壳，不要把界面画到背壳上。"
    if code.startswith("A-"):
        return f"图{n}只锁定这件道具的外形，不参考它在画面里的位置，不参考构图。"
    return f"图{n}只锁定参考图的外形，不参考构图。"


def height_sentence(assets: list[dict], kinds: dict[int, str]) -> str:
    known = []
    unknown = []
    for a in assets:
        if not a["code"].startswith("P-") or family_of(a["code"]) == "HAND":
            continue
        cm = HEIGHT.get(a["code"])
        if cm and kinds.get(a["n"]) != "hand":
            known.append((a["n"], cm))
        elif kinds.get(a["n"]) != "hand":
            unknown.append(a["n"])
    if len(known) >= 2:
        bits = [f"图{n}身高约{cm}厘米" for n, cm in known]
        return "，".join(bits) + "。同框时保持这个身高差，不要把身体拉成一样高。"
    if len(known) == 1 and unknown:
        n, cm = known[0]
        return f"图{n}身高约{cm}厘米。同框的另一个人按参考图的身高，不要把两个人拉成一样高。"
    return ""


def tidy(s: str) -> str:
    s = s.replace("**", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"，{2,}", "，", s)
    s = re.sub(r"。{2,}", "。", s)
    s = re.sub(r"，。", "。", s)
    s = re.sub(r"。，", "。", s)
    s = re.sub(r"（\s*）", "", s)
    s = re.sub(r"\s*([，。；])", r"\1", s)
    s = re.sub(r"([，。]){2,}", r"\1", s)
    return s.strip()


def protect_sub(text: str, fn) -> str:
    pat = re.compile(r"`[^`]*`|「[^」]*」")
    out = []
    last = 0
    for m in pat.finditer(text):
        out.append(fn(text[last : m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(fn(text[last:]))
    return "".join(out)


def apply_names(text: str, assets: list[dict]) -> str:
    # Longer surface names first. Only people who are actually bound.
    repls: list[tuple[str, str]] = []
    for a in assets:
        fig = f"图{a['n']}"
        fam = family_of(a["code"])
        if fam == "NAOMI":
            repls += [("Naomi Bennett", fig), ("Young Naomi", fig), ("Naomi", fig)]
        elif fam == "HAND":
            repls += [("女孩小手", fig), ("小手", fig), ("女孩的手", fig)]
        elif fam == "GABRIEL":
            repls += [("Gabriel Mora", fig), ("Gabriel", fig)]
        elif fam == "CLAIRE":
            repls += [("Claire Bennett", fig), ("Claire", fig)]
        elif fam == "MARGOT":
            repls += [("Margot Rey", fig), ("Margot", fig)]
        elif fam == "ATTENDANT":
            repls += [("Attendant", fig), ("工作人员", fig)]
        elif fam == "AUCTIONEER":
            repls += [("Auctioneer", fig), ("拍卖师", fig)]
    # de-dup, longer first
    repls = sorted(set(repls), key=lambda x: len(x[0]), reverse=True)

    def repl(seg: str) -> str:
        for src, dst in repls:
            seg = seg.replace(src, dst)
        return seg

    return protect_sub(text, repl)


def strip_production(text: str) -> str:
    def scrub(seg: str) -> str:
        seg = re.sub(r"，?\s*D\d+[A-Z]?\s*，?", "，", seg)
        seg = re.sub(r"\bD\d+[A-Z]?\b", "", seg)
        seg = re.sub(r"\d+\s*mm", "", seg, flags=re.I)
        seg = seg.replace("远端长焦感", "远处")
        seg = seg.replace("长焦感", "")
        seg = re.sub(r"短焦|中焦|长焦", "", seg)
        seg = re.sub(r"0:\d\d[–-]0:\d\d\s*", "", seg)
        seg = re.sub(r"硬切自\s*[0-9A-Za-z.]+[，；]?", "", seg)
        seg = re.sub(r"上一镜|下一镜|第\s*\d+\s*场", "", seg)
        seg = re.sub(r"（第一眼：([^）]+)）", r"，视线落在\1", seg)
        seg = re.sub(r"第一眼：", "视线先落在", seg)
        seg = re.sub(r"第一眼", "视线先落在", seg)
        seg = re.sub(r"视觉主意：", "", seg)
        seg = re.sub(r"光意图：", "", seg)
        seg = re.sub(r"不眨的眼睛", "钉住的视线", seg)
        seg = seg.replace("POV ", "主观镜头")
        seg = seg.replace("POV", "主观镜头")
        seg = seg.replace("主观镜头 在", "主观镜头在")
        seg = seg.replace("（非手持）", "，不是手持")
        seg = seg.replace("供冲出", "")
        seg = seg.replace("<1°", "不到一度")
        for bit in DROP_BITS:
            seg = seg.replace(bit, "")
        seg = re.sub(r"Gabriel\s*视点", "主观", seg)
        seg = re.sub(r"Gabriel\s*眼高主观", "眼高主观", seg)
        seg = re.sub(r"Naomi\s*视线主观", "主观", seg)
        seg = re.sub(r"留在画外的\s*Gabriel", "留在画外的人", seg)
        seg = re.sub(r"Gabriel\s*留在画外", "另一个人留在画外", seg)
        seg = re.sub(r"Naomi\s*留在[^，。]{0,12}画外", "另一个人留在画外", seg)
        seg = re.sub(r"问\s*Claire", "问起那个人", seg)
        return seg

    return protect_sub(text, scrub)


def parse_idea(raw: str) -> tuple[str, str, str]:
    raw = raw.strip()
    if not raw:
        return "", "", ""
    if "视觉主意" in raw or "光意图" in raw:
        idea = eye = light = ""
        m = re.search(r"视觉主意：(.+?)(?:；第一眼：|；光意图：|$)", raw)
        if m:
            idea = m.group(1).strip()
        m = re.search(r"第一眼：([^；]+)", raw)
        if m:
            eye = m.group(1).strip()
        m = re.search(r"光意图：(.+)$", raw)
        if m:
            light = m.group(1).strip()
        return idea, eye, light
    # Scene 1 compact: 主意；第一眼x；光
    parts = [p.strip() for p in re.split(r"[；;]", raw) if p.strip()]
    idea, eye, light = "", "", ""
    for p in parts:
        if p.startswith("第一眼"):
            eye = re.sub(r"^第一眼", "", p).strip()
        elif not idea:
            idea = p
        else:
            light = (light + "，" + p).strip("，") if light else p
    return idea, eye, light


def eyes_visible(text: str) -> bool:
    if re.search(r"无脸|不见持伞者脸|不露出脸|不露出可辨认|无可见人|肩背|肩后|后脑|只见手|手部", text):
        return False
    if re.search(r"脸|眼睛|双人", text):
        return True
    if re.search(r"中景|近景|全景", text) and re.search(r"图\d", text):
        if re.search(r"俯视|颈|指尖|手部|肩背|肩后|无脸", text) and not re.search(r"眼睛", text):
            return False
        return True
    return False


def dead_or_freeze(text: str) -> bool:
    return bool(re.search(r"快门|冻结|已死|没有呼吸|眼皮不动", text))


def scrub_unbound(text: str) -> str:
    """Offscreen names become directions. Letters on a prop stay next to 名字."""

    def scrub(seg: str) -> str:
        seg = re.sub(r"滑入\s*Naomi\s*一侧", "滑向镜头这一侧", seg)
        seg = re.sub(r"Attendant\s*一侧", "柜台对面", seg)
        seg = re.sub(r"抵达\s*Naomi\s*区域", "抵达镜头这一侧", seg)
        seg = re.sub(r"画右的\s*Gabriel", "画右画外", seg)
        seg = re.sub(r"从\s*Gabriel\s*一侧", "从画面一侧", seg)
        seg = re.sub(r"抬到\s*Naomi", "抬向画外", seg)
        seg = re.sub(r"面向画外\s*Naomi", "面向画外", seg)
        seg = re.sub(r"画外\s*Naomi", "画外", seg)
        seg = re.sub(r"Naomi\s*画外", "画外有人", seg)
        seg = re.sub(r"Gabriel\s*的手", "一只手", seg)
        seg = re.sub(r"Naomi\s*的名字", "纸上写着的名字 Naomi", seg)
        seg = re.sub(r"成年(图\d+)", r"\1", seg)
        seg = re.sub(r"唯一买方\s*Naomi Bennett", "买方一栏", seg)
        seg = re.sub(r"Naomi Bennett", "买方姓名", seg)
        seg = re.sub(r"(?<!名字 )\bNaomi\b", "", seg)
        seg = re.sub(r"\bGabriel\b", "", seg)
        seg = re.sub(r"\bAttendant\b", "", seg)
        seg = re.sub(r"\bClaire\b", "", seg)
        seg = re.sub(r"\bMargot\b", "", seg)
        return seg

    return protect_sub(text, scrub)


def drop_spoken_backticks(text: str, quotes: list[str]) -> str:
    keys = {re.sub(r"[^a-z0-9]", "", q.lower()) for q in quotes if q}

    def drop(seg: str) -> str:
        def repl(m: re.Match) -> str:
            inner = m.group(1)
            key = re.sub(r"[^a-z0-9]", "", inner.lower())
            if key and key in keys:
                return ""
            return m.group(0)

        return re.sub(r"`([^`]*)`", repl, seg)

    # Backticks are the protected form, so drop them on the raw text.
    return drop(text)


def sound_bed(picture: str, sound_field: str) -> str:
    src = picture + sound_field
    bits = []
    if re.search(r"暴雨|雨幕|雨里", src):
        bits.append("暴雨")
    if "笑" in sound_field:
        bits.append("笑")
    if re.search(r"火|燃", src):
        bits.append("火燃")
    if re.search(r"水响|水槽|水流", src):
        bits.append("水声")
    if re.search(r"掌声|鼓掌", src):
        bits.append("掌声")
    if re.search(r"手机.*震|震动", src):
        bits.append("手机震动")
    if re.search(r"纸", src) and "纸" not in "".join(bits):
        bits.append("纸声")
    if re.search(r"风", src) and "暴雨" not in bits:
        bits.append("风声")
    if re.search(r"切黑", picture):
        return "风、水和远处车声，画面切黑时这些声音一起停"
    if not bits:
        if sound_field and "无对白" not in sound_field and "待" not in sound_field:
            cleaned = re.sub(r"0:\d\d[–-]0:\d\d", "", sound_field)
            cleaned = re.sub(r"「.*?」", "", cleaned)
            cleaned = re.sub(r"可选.*", "", cleaned)
            cleaned = tidy(cleaned).strip("。；")
            if cleaned and len(cleaned) < 40 and not re.search(r"Claire|Gabriel|Naomi|图\d", cleaned):
                return cleaned
        return "现场的环境声和动作声"
    return "、".join(bits)


def build_bans(ban_raw: str, assets: list[dict], picture: str, pov: bool, screen: bool) -> str:
    items: list[str] = []
    if ban_raw and "待补" not in ban_raw:
        raw = ban_raw
        raw = raw.replace("Claire/Gabriel 全身", "两个成人的全身")
        raw = raw.replace("Claire/Gabriel", "这两个人")
        raw = re.sub(r"当下\s*Naomi", "第三个成年人", raw)
        raw = re.sub(r"成年\s*Naomi", "成年人的正脸", raw)
        raw = apply_names(strip_production(raw), assets)
        for bit in re.split(r"[、，；;]", raw):
            bit = tidy(bit).strip("。 ")
            if bit and not bit.startswith("不要"):
                bit = "不要" + bit
            if not bit or "待" in bit:
                continue
            if re.search(r"\b(Claire|Gabriel|Naomi|Margot|Attendant|Auctioneer|D\d|P-|L-|A-)\b", bit):
                continue
            if bit not in items:
                items.append(bit)
    if not any("旋律" in x or "配乐" in x for x in items):
        items.append("不要旋律，不要垫乐")
    if not any("字幕" in x for x in items):
        if screen:
            items.append("不要翻译画面上的原文，不要另加字幕")
        else:
            items.append("不要另加字幕")
    if any(a["code"].startswith("P-") for a in assets) and not any("脸" in x or "衣服" in x for x in items):
        items.append("不要改已绑定人物的脸和衣服")
    if pov and not any("反拍" in x or "正脸" in x for x in items):
        items.append("不要反拍主观镜头主人的脸")
    if re.search(r"手机|屏幕", picture) and re.search(r"脸|近景", picture):
        items.append("不要让正脸和屏幕上的字同框")
    dedup = []
    for x in items:
        if x in ("配乐", "配乐煽情"):
            x = "不要旋律，不要垫乐"
        if x and x not in dedup:
            dedup.append(x)
    must = [x for x in dedup if "旋律" in x or "字幕" in x]
    rest = [x for x in dedup if x not in must]
    if not any("旋律" in x for x in must):
        must.append("不要旋律，不要垫乐")
    if not any("字幕" in x for x in must):
        must.append("不要另加字幕")
    room = 6 - len(must)
    return "；".join(rest[: max(room, 0)] + must) + "。"


def prose_body(picture: str, camera: str, action: str, idea: str, eye: str) -> str:
    chunks = []
    for src in (picture, camera, action):
        src = tidy(src)
        if src and src not in "".join(chunks):
            chunks.append(src.strip("。"))
    body = "。".join(c for c in chunks if c)
    idea = tidy(idea)
    if idea and idea not in body and body not in idea:
        # keep the visual priority when it adds a relation the picture line lacks
        if len(idea) > 8:
            body = (body + "。" + idea.strip("。")).strip("。")
    eye = tidy(eye).strip("。")
    eye = re.sub(r"^视线先落在", "", eye)
    if eye and "视线" not in eye and len(eye) > 1:
        body = body.rstrip("。") + f"。视线先落在{eye}"
    return body


def build_paste(shot_id: str, h3: dict, sb: dict, deliveries: list[str], spoken: list[str] | None = None) -> str:
    assets = h3["assets"]
    picture_raw = field(sb, "画面")
    camera_raw = field(sb, "摄影机")
    action_raw = field(sb, "人物动作")
    sound_raw = field(sb, "声音")
    idea_raw, eye_raw, light_raw = parse_idea(field(sb, "主意·第一眼·光"))
    visible = " ".join([picture_raw, camera_raw, action_raw, idea_raw, eye_raw, light_raw])

    kinds = {}
    for code, kind in EXTRA_ASSETS.get(shot_id, []):
        # already appended in prepare()
        pass
    for a in assets:
        if a.get("kind"):
            kinds[a["n"]] = a["kind"]

    picture_raw = drop_spoken_backticks(picture_raw, spoken or [])
    picture = apply_names(strip_production(picture_raw), assets)
    camera = apply_names(strip_production(camera_raw), assets)
    action = apply_names(strip_production(action_raw), assets)
    idea = apply_names(strip_production(idea_raw), assets)
    eye = apply_names(strip_production(eye_raw), assets)
    light = apply_names(strip_production(light_raw), assets)

    # pronouns when only one woman / one man is bound
    females = [a for a in assets if family_of(a["code"]) in FEMALE_FAM and kinds.get(a["n"]) != "hand"]
    males = [a for a in assets if family_of(a["code"]) in MALE_FAM and kinds.get(a["n"]) != "hand"]

    def pronouns(seg: str) -> str:
        if len(females) == 1:
            seg = re.sub(r"(?<!图)她(?!们)", f"图{females[0]['n']}", seg)
        if len(males) == 1:
            seg = re.sub(r"(?<!图)他(?!们)", f"图{males[0]['n']}", seg)
        return seg

    picture, camera, action, idea, eye, light = map(pronouns, (picture, camera, action, idea, eye, light))

    pov = bool(re.search(r"主观|视点", visible + picture))
    screen = bool(re.search(r"`[^`]+`", picture_raw) or re.search(r"屏幕|可读", visible))

    binds = []
    for a in assets:
        binds.append(bind_sentence(a, kinds.get(a["n"], ""), visible + picture))
    height = height_sentence(assets, kinds)
    if shot_id == "1.2":
        height = "图1身高约170厘米，图4身高约183厘米。不要把两个人拉成一样高。"

    body = prose_body(picture, camera, action, idea, eye)
    if pov and "不要反拍" not in body:
        body += "。这是主观镜头，不要反拍镜头主人的脸"
    if re.search(r"右下", visible) and "右下" not in body:
        body += "。手从画面右下进入"
    if re.search(r"头带|播放器|光碟", visible):
        body += "。播放界面只显示索引、文件名、进度和抽象光，不播放能认出的记忆画面"
    if re.search(r"手机|屏幕", visible) and re.search(r"脸", visible) and "同框" not in body:
        if re.search(r"过肩|暗前景|插入", visible):
            body += "。脸只留在暗处或前景，可读的字在屏幕上，不要让正脸和屏幕字一样清楚"
        else:
            body += "。不要让正脸和屏幕上的字出现在同一格"

    blink = ""
    joined = picture + idea
    if dead_or_freeze(visible):
        blink = "快门或停住之后，眼皮不要再动。"
    elif eyes_visible(joined) and not re.search(r"不见持伞者脸|不露出脸|无可见人", joined):
        blink = "能看见眼睛的人自然眨眼，不要一直睁着。"

    light_s = ""
    if light:
        light_s = human_brightness(light)

    bed = sound_bed(picture_raw + " " + sound_raw, sound_raw)
    if re.search(r"无对白|无配乐与对白", sound_raw) and not deliveries:
        speech = "没有对白。"
    elif deliveries:
        speech = "".join(d if d.endswith("。") else d + "。" for d in deliveries)
    else:
        speech = ""

    # 1.4 may carry the tail of the previous line as sound, without naming the previous shot.
    if shot_id == "1.4":
        speech = "开场可以带进一个词 river 的尾音，本镜不见人，也不见口型。"

    dur = h3["dur"]
    mm = h3["mm"]
    parts = [
        f"{dur}秒、16:9视频。焦距{mm}毫米，固定不许变焦。真人实拍。",
        light_s,
        "".join(binds),
        height,
        tidy(body) + ("。" if body and not tidy(body).endswith("。") else ""),
        blink,
        f"声音是{bed}。{speech}只保留现场说话、环境音和动作音，不要旋律，不要垫乐。",
    ]
    text = tidy("".join(p for p in parts if p))
    text = text.replace("声音是现场的环境声和动作声。没有对白。", "声音只有现场的环境声和动作声，没有对白。")
    text = scrub_unbound(text)
    text = fix_frame_words(text)
    text, _unfinished_ban = fix_unfinished(text)
    text = tidy(text)
    return text


def prepare_assets(h3_shot: dict, shot_id: str) -> None:
    assets = h3_shot["assets"]
    existing = {a["code"] for a in assets}
    n = max((a["n"] for a in assets), default=0)
    for code, kind in EXTRA_ASSETS.get(shot_id, []):
        if code in existing:
            for a in assets:
                if a["code"] == code:
                    a["kind"] = kind
            continue
        n += 1
        assets.append({"n": n, "code": code, "note": "", "kind": kind})
        existing.add(code)
    for a in assets:
        a.setdefault("kind", "")


def asset_line(assets: list[dict]) -> str:
    bits = []
    for a in assets:
        note = f"（{a['note']}）" if a.get("note") else ""
        bits.append(f"图{a['n']}＝{a['code']}{note}")
    return "；".join(bits) + "。"


def contrast_block(sb: dict) -> str:
    lines = []
    labels = [
        ("画面", "画面"),
        ("摄影机", "摄影机"),
        ("人物动作", "人物动作"),
        ("声音", "声音"),
        ("主意·第一眼·光", "主意·第一眼·光"),
        ("禁止出现", "禁止出现"),
    ]
    for key, title in labels:
        val = field(sb, key)
        if not val:
            continue
        val = re.sub(r"\s+", " ", val).strip()
        lines.append(f"- **{title}** {val}")
    return "\n".join(lines)


def qa_paste(shot: str, paste: str, dont: str) -> list[str]:
    bad = []
    protected = " ".join(re.findall(r"`[^`]*`|「[^」]*」", paste))
    stripped = re.sub(r"`[^`]*`|「[^」]*」", "", paste + "\n" + dont)
    stripped = re.sub(r"名字 Naomi", "名字", stripped)
    for pat, msg in (
        (r"\b(Claire|Gabriel|Naomi|Margot|Attendant|Auctioneer)\b", "人名"),
        (r"\b[PLA]-[A-Za-z0-9\-]+", "代号"),
        (r"\bD\d+", "机位号"),
        (r"0:\d\d", "时间码"),
        (r"短焦|中焦|长焦", "焦段范围词"),
        (r"第一眼与光|视觉主意|光意图", "分镜标签"),
        (r"图内人物|场景参考图|袖口与肩的人", "清洗残片"),
    ):
        if re.search(pat, stripped):
            m = re.search(pat, stripped)
            bad.append(f"{shot} {msg}: {m.group(0)}")
    if "不要旋律" not in paste or "不要垫乐" not in paste:
        bad.append(f"{shot} 缺旋律垫乐禁令")
    if "16:9" not in paste or "不许变焦" not in paste:
        bad.append(f"{shot} 缺规格")
    if "图" not in paste:
        bad.append(f"{shot} 没有图N")
    return bad


def main() -> None:
    sb = parse_storyboard(SB_PATH.read_text(encoding="utf-8"))
    h3 = parse_h3(H3_PATH.read_text(encoding="utf-8"))
    pool = parse_screenplay(SP_PATH.read_text(encoding="utf-8"))
    cursor = [0]
    preamble = H3_PATH.read_text(encoding="utf-8").split("## 第1场")[0]
    preamble = preamble.replace(
        "日期：2026年10月7日（分镜 Draft 6 同步）",
        "日期：2026年10月7日（按分镜与剧本重写可贴入）",
    )
    preamble = preamble.replace(
        "一条成片对应一镜；每条含 **分镜对照**（与 Storyboard 同步）与 **可贴入**（按对照压缩成 H3 公式，尽可能还原画面与运镜）。",
        "一条成片对应一镜。每条含 **分镜对照**（给人看，保留人名和机位号）和 **可贴入**（整段中文，只写这一镜的光、绑定、动作、镜头和声音）。",
    )
    preamble = preamble.replace(
        "- **记忆场：** 物理视点属于该镜素材里绑定为「男子/视点人物」外形的那张图（常为图2），不给该人物客观反应镜，也不出现绑定为「当下女子」外形的参考图。记忆场中他的手固定从画面右下进入。\n",
        "- **记忆场：** 主观镜头不反拍镜头主人的脸。他的手若入画，从画面右下进入，并用图N锁这只手。\n",
    )
    preamble = preamble.replace(
        "- **眨眼：** 每个镜头里，凡能看见眼睛的活人，不论是谁，有自然的眨眼即可，不要死盯不眨。死者、冻结画面、只见手或后脑、无人脸的镜头不要为眨眼改构图或让死人眨眼。\n- **光影：** 光影自己承担叙事张力，按本镜已写的明暗切开关系、权力和距离。不要用平光把人物拍平，不要靠配乐或字幕补情绪。\n",
        "- **眨眼：** 这一镜能看见眼睛，才写自然眨眼。只见手、后脑、肩背或没有脸的镜头不写眨眼。快门停住之后眼皮不动。\n- **光影：** 可贴入只写这一镜的明暗，不写全片总谱，也不写「按本镜已写的亮度」这类说明。\n",
    )

    heads = dict(SCENE_HEADS)
    order = []
    for m in re.finditer(r"(?m)^### ([0-9A-Za-z.M]+)　", H3_PATH.read_text(encoding="utf-8")):
        if m.group(1) not in order:
            order.append(m.group(1))

    index_rows = []
    problems = []
    blocks = [preamble.rstrip() + "\n\n"]

    for shot_id in order:
        if shot_id not in sb or shot_id not in h3:
            problems.append(f"missing {shot_id}")
            continue
        prepare_assets(h3[shot_id], shot_id)
        assets = h3[shot_id]["assets"]
        raw_del = extract_deliveries(h3[shot_id]["paste"])
        deliveries = []
        spoken = []
        for pre, quote, off_pre, silent in raw_del:
            if shot_id == "1.4":
                continue
            speaker, off_sp, canonical = match_speaker(quote, pool, cursor)
            off = off_sp or off_pre
            fig = fig_for_speaker(speaker, assets)
            if not fig:
                mfig = re.search(r"图\d+", pre)
                if mfig and any(k in pre for k in ("开口", "接", "出声")):
                    fig = mfig.group(0)
            if not fig:
                people = [
                    a for a in assets
                    if a["code"].startswith("P-")
                    and family_of(a["code"]) != "HAND"
                    and a.get("kind") != "hand"
                ]
                if len(people) == 1 and not off:
                    fig = f"图{people[0]['n']}"
            # A person standing in the shot is not offscreen just because an earlier pass said 画外.
            if fig and not off_sp:
                off = False
            line = canonical if " " in canonical or len(canonical) <= len(quote) else quote
            deliveries.append(clean_delivery(pre, line, fig, off, silent))
            spoken.append(line)
            stress = ""
            sm = re.search(r"只重读\s*([A-Za-z']+)", pre)
            if sm:
                stress = sm.group(1)
            tone = ""
            tm = re.search(r"语气[^，。:：]{0,18}", pre)
            if tm:
                tone = tm.group(0)
            who = speaker or "画外"
            index_rows.append((shot_id, who, line, tone, stress))

        paste = build_paste(shot_id, h3[shot_id], sb[shot_id], deliveries, spoken)
        ban = build_bans(
            field(sb[shot_id], "禁止出现"),
            assets,
            field(sb[shot_id], "画面"),
            "主观" in paste or "视点" in field(sb[shot_id], "画面"),
            "`" in field(sb[shot_id], "画面") or "屏幕" in field(sb[shot_id], "画面"),
        )
        if "碰到皮肤之前停住" in paste and "不要让手碰到" not in ban:
            ban = ban.rstrip("。") + "；不要让手碰到或抓住。"
        if "不要伸进画里" in paste and "不要让手伸进" not in ban:
            ban = ban.rstrip("。") + "；不要让手伸进画面。"
        problems.extend(qa_paste(shot_id, paste, ban))

        if shot_id in heads:
            blocks.append(heads[shot_id] + "\n\n")
        note = DUR_NOTE.get(shot_id, "")
        header = f"### {shot_id}　{h3[shot_id]['dur']}秒　{h3[shot_id]['mm']}毫米　全能参考　16:9\n\n"
        if note:
            header += note + "\n\n"
        contrast = contrast_block(sb[shot_id])
        piece = (
            header
            + "**分镜对照：**\n\n"
            + (contrast + "\n\n" if contrast else "")
            + f"**素材：** {asset_line(assets)}\n\n"
            + "**可贴入：**\n\n"
            + paste
            + "\n\n"
            + f"**不要做：** {ban}\n\n"
        )
        blocks.append(piece)

    # dialogue index for humans — names allowed
    idx = ["## 对白索引\n", "给人对照。可贴入里仍用图N说明谁开口。每句最多一个重读词。\n", "| 镜号 | 说话人 | 原文 | 语气 | 重读 |", "| --- | --- | --- | --- | --- |"]
    for shot_id, who, quote, tone, stress in index_rows:
        q = quote.replace("|", "/")
        idx.append(f"| {shot_id} | {who} | {q} | {tone} | {stress or '不加重'} |")
    blocks.append("\n".join(idx) + "\n")

    H3_PATH.write_text("".join(blocks), encoding="utf-8")
    print(f"shots {len(order)} problems {len(problems)} screenplay cursor {cursor[0]}/{len(pool)}")
    for p in problems[:80]:
        print(p)
    if len(problems) > 80:
        print(f"... {len(problems) - 80} more")


if __name__ == "__main__":
    main()
