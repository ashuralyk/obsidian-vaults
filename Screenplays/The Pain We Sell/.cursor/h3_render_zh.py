#!/usr/bin/env python3
"""Turn the English H3 pastes into Chinese pastes and apply the story fixes.

Reads the last clean English checkpoint, not the half-translated working file.
"""

from __future__ import annotations

import importlib.util
import json
import re
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path("/Users/vimchain/Obsidian/Screenplays/The Pain We Sell/MiniMax H3.md")
CHECKPOINT = Path(
    "/Users/vimchain/Library/Application Support/Cursor/User/globalStorage/"
    "anysphere.cursor-commits/checkpoints/"
    "17f2209e-0c1b-4eb0-8009-c3fce60a9346/files/"
    "deb5fd74-2eeb-432f-a52a-db41964debb6"
)
CACHE_PATH = Path("/Users/vimchain/Obsidian/Screenplays/The Pain We Sell/.cursor/h3-bing-cache.json")
FIX_PATH = Path("/Users/vimchain/Obsidian/Screenplays/The Pain We Sell/.cursor/h3_to_zh.py")

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

MMZH = {
    "28": "二十八",
    "32": "三十二",
    "35": "三十五",
    "40": "四十",
    "50": "五十",
    "55": "五十五",
    "65": "六十五",
    "70": "七十",
    "75": "七十五",
    "85": "八十五",
    "100": "一百",
    "120": "一百二十",
}

SHOT_ZH = {
    "close-up": "近景",
    "medium shot": "中景",
    "medium close-up": "中近景",
    "close-up on the hands": "手部近景",
    "over-shoulder": "过肩镜头",
    "wide shot": "全景",
    "insert": "插入镜头",
    "subjective close-up": "主观近景",
    "subjective medium-full shot": "主观中全景",
    "subjective wide shot": "主观全景",
    "long shot": "远景",
    "subjective medium shot": "主观中景",
    "medium two-shot": "双人中景",
    "wide two-shot": "双人全景",
    "two-shot": "双人镜头",
    "over-shoulder medium close-up": "过肩中近景",
    "asymmetric two-shot": "不对称双人镜头",
    "medium close-up two-shot": "双人中近景",
    "subjective medium close-up": "主观中近景",
    "tight close-up": "紧近景",
    "side two-shot": "侧面双人镜头",
    "medium-full shot": "中全景",
    "two-shot medium": "双人中景",
    "side medium close-up": "侧面中近景",
    "frontal close-up": "正面近景",
    "three-quarter close-up": "四分之三侧面近景",
    "two-shot close-up": "双人近景",
    "medium close-up on the hands": "手部中近景",
    "subjective two-shot": "主观双人镜头",
    "subjective looking-down shot": "主观俯视",
    "subjective tight close-up": "主观紧近景",
    "side medium two-shot": "侧面双人中景",
    "medium shot on the hands": "手部中景",
    "tight close-up on the hands": "手部紧近景",
    "medium shot from the side": "侧面中景",
    "extreme close-up": "大特写",
    "close-up from an oblique side": "斜侧面近景",
    "over-shoulder close-up": "过肩近景",
    "medium-long shot": "中远景",
    "subjective shot": "主观镜头",
    "medium shot from the side and rear": "侧后中景",
    "over-shoulder medium-long shot": "过肩中远景",
}

HEIGHTS = [
    ("three-quarter view", "四分之三侧面"),
    ("shoulder height", "肩高"),
    ("chest height", "胸高"),
    ("table height", "桌面高度"),
    ("hand height", "手高"),
    ("head height", "头高"),
    ("looking down", "俯视"),
    ("eye level", "眼平"),
]

MOVES = {
    "locked off, no pan and no push-in": "固定机位，不摇，不推",
    "locked off with a sway of less than one degree, not handheld, no pan and no push-in": "固定机位，晃动小于一度，不是手持，不摇，不推",
    "locked off": "固定机位",
}

# Longest English first. Values are exact Chinese, never sent to the translator.
STOCK = [
    ("No brush touch, no melody, no musical pads.", "不要笔尖碰上画面，不要旋律，不要垫乐。"),
    ("No text other than `WHITE ROOM I` on the screen, no watermark, no logo.", "屏幕上除了 `WHITE ROOM I` 不要另加文字，不要水印，不要标志。"),
    ("No text, no watermark, no logo, no subtitles.", "不要另加文字，不要水印，不要标志，不要字幕。"),
    ("Do not veil the frame in gray fog, and do not change the color of her clothes.", "不要把画面罩成灰雾，也不要改衣服的颜色。"),
    ("Do not veil the frame in gray fog, and do not change the color of their clothes.", "不要把画面罩成灰雾，也不要改衣服的颜色。"),
    ("Do not veil the frame in gray fog. Do not change the color of the clothes.", "不要把画面罩成灰雾。不要改衣服的颜色。"),
    ("No teal-and-orange grade, no neon.", "不要青橙色调，不要霓虹。"),
    ("The motion is fluid and natural, with realistic physics, at 24fps.", "动作自然，物理真实，每秒二十四帧。"),
    ("Motion is fluid and natural, with realistic physics, at 24fps.", "动作自然，物理真实，每秒二十四帧。"),
    ("Fluid natural motion, realistic physics, 24fps.", "动作自然，物理真实，每秒二十四帧。"),
    ("Fluid natural motion, realistic rain, 24fps.", "动作自然，雨是真实的，每秒二十四帧。"),
    ("Fluid natural rain, realistic water, 24fps.", "雨是自然的，水是真实的，每秒二十四帧。"),
    ("No morphing, no facial drift, no clothing changes.", "不要变形，不要五官漂移，不要换衣服。"),
    ("No morphing, no person entering, no change of place.", "不要变形，不要有人走进来，不要换地方。"),
    ("photorealistic skin with visible pores and natural subsurface scattering, fine film grain", "真人实拍，皮肤能看见毛孔，细胶片颗粒"),
    ("The eye lands first on", "眼睛先落在"),
    ("The eye goes first to", "眼睛先落到"),
    ("The eye lands on", "眼睛落在"),
    ("muted saturation, moderate contrast", "饱和度压低，反差中等"),
    ("Maintain perfect consistency throughout —", "从头到尾保持一致："),
    ("No science-fiction color.", "不要科幻色。"),
    ("No melody, no musical pads.", "不要旋律，不要垫乐。"),
    ("No text, no watermark, no logo.", "不要另加文字，不要水印，不要标志。"),
    ("Do not veil the frame in gray fog.", "不要把画面罩成灰雾。"),
    ("Do not change the color of her clothes.", "不要改衣服的颜色。"),
    ("Do not change the color of his clothes.", "不要改衣服的颜色。"),
    ("Do not change the color of their clothes.", "不要改衣服的颜色。"),
    ("Do not change the color of the clothes.", "不要改衣服的颜色。"),
    ("No teal-and-orange grade.", "不要青橙色调。"),
    ("No teal-and-orange.", "不要青橙色调。"),
    ("side-back light", "侧逆光"),
    ("warm summer rain", "暖的夏日暴雨"),
    ("muted saturation", "饱和度压低"),
    ("Lighting:", "光："),
    ("Color grade:", "色彩："),
    ("Realistic physics, 24fps.", "物理真实，每秒二十四帧。"),
    ("photorealistic, fine film grain", "真人实拍，细胶片颗粒"),
    ("fine film grain", "细胶片颗粒"),
    ("white high brightness", "亮明"),
    ("gray-white brightness", "浅灰亮度"),
    ("white brightness", "亮明"),
    ("from the left edge of the frame", "从画面左边缘伸进画来"),
    ("from the right edge of the frame", "从画面右边缘伸进画来"),
    ("from the lower edge of the frame", "从画面下边缘伸进画来"),
    ("from the upper edge of the frame", "从画面上边缘伸进画来"),
    ("the left edge of the frame", "画面左边缘"),
    ("the right edge of the frame", "画面右边缘"),
    ("the lower edge of the frame", "画面下边缘"),
    ("the upper edge of the frame", "画面上边缘"),
    ("toward screen right", "朝画面右侧"),
    ("toward screen left", "朝画面左侧"),
    ("on screen left", "在画面左侧"),
    ("on screen right", "在画面右侧"),
    ("screen left", "画面左侧"),
    ("screen right", "画面右侧"),
    ("the left of the frame", "画面左侧"),
    ("the right of the frame", "画面右侧"),
    ("left of the frame", "画面左侧"),
    ("right of the frame", "画面右侧"),
]


def load_fix_shot():
    spec = importlib.util.spec_from_file_location("h3fix", FIX_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.fix_shot


class Bing:
    def __init__(self, cache: dict[str, str] | None = None, lock: threading.Lock | None = None) -> None:
        self.cache = cache if cache is not None else {}
        self.lock = lock or threading.Lock()
        self.ig = ""
        self.key = ""
        self.token = ""
        self.refresh()

    def refresh(self) -> None:
        req = urllib.request.Request("https://www.bing.com/translator", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", "replace")
        self.ig = re.search(r'IG:"([^"]+)"', html).group(1)
        self.key, self.token, _ = re.search(
            r'params_AbusePreventionHelper\s*=\s*\[(\d+),"([^"]+)",(\d+)\]', html
        ).groups()

    def save(self) -> None:
        with self.lock:
            CACHE_PATH.write_text(json.dumps(self.cache, ensure_ascii=False))

    def raw(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        with self.lock:
            cached = self.cache.get(text)
        if cached is not None:
            return cached
        if not re.search(r"[A-Za-z]", text):
            with self.lock:
                self.cache[text] = text
            return text
        last = None
        for attempt in range(4):
            try:
                data = urllib.parse.urlencode(
                    {
                        "fromLang": "en",
                        "to": "zh-Hans",
                        "text": text,
                        "token": self.token,
                        "key": self.key,
                    }
                ).encode()
                url = f"https://www.bing.com/ttranslatev3?isVertical=1&&IG={self.ig}&IID=translator.5028"
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "User-Agent": UA,
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": "https://www.bing.com/translator",
                    },
                )
                with urllib.request.urlopen(req, timeout=40) as resp:
                    body = json.loads(resp.read().decode())
                out = body[0]["translations"][0]["text"].strip()
                if out:
                    with self.lock:
                        self.cache[text] = out
                    return out
            except Exception as exc:  # noqa: BLE001
                last = exc
                time.sleep(1.5 * (attempt + 1))
                try:
                    self.refresh()
                except Exception:
                    time.sleep(2)
        raise RuntimeError(f"translate failed: {last}")

    def translate(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        parts = re.split(r"(SZX\d+ZXS|QZX\d+ZXQ|TZX\d+ZXZ)", text)
        out = []
        buf = ""

        def flush(chunk: str) -> None:
            chunk = chunk.strip()
            if not chunk:
                return
            if len(chunk) <= 850:
                out.append(self.raw(chunk))
                return
            sentences = re.split(r"(?<=[.!?])\s+", chunk)
            cur = ""
            for sent in sentences:
                if cur and len(cur) + len(sent) > 850:
                    out.append(self.raw(cur))
                    cur = sent
                else:
                    cur = (cur + " " + sent).strip()
            if cur:
                out.append(self.raw(cur))

        for part in parts:
            if re.fullmatch(r"SZX\d+ZXS|QZX\d+ZXQ|TZX\d+ZXZ", part or ""):
                flush(buf)
                buf = ""
                out.append(part)
            else:
                buf += part
        flush(buf)
        return "".join(out)


def protect_quotes(text: str, store: dict[str, str]) -> str:
    def sub_q(m: re.Match) -> str:
        key = f"QZX{len(store)}ZXQ"
        store[key] = m.group(0)
        return key

    text = re.sub(r'"[^"]*"', sub_q, text)

    def sub_t(m: re.Match) -> str:
        key = f"TZX{len(store)}ZXZ"
        store[key] = m.group(0)
        return key

    return re.sub(r"`[^`]*`", sub_t, text)


BRIGHT = [
    (r"(?:at )?a light-gray brightness", "浅灰亮度"),
    (r"(?:at )?light-gray brightness", "浅灰亮度"),
    (r"(?:at )?a deep-gray brightness", "深灰亮度"),
    (r"(?:at )?deep-gray brightness", "深灰亮度"),
    (r"(?:at )?a near-black brightness", "阴暗"),
    (r"(?:at )?near-black brightness", "阴暗"),
    (r"(?:at )?a high brightness", "亮明"),
    (r"high brightness", "亮明"),
    (r"is light-gray brightness", "是浅灰亮度"),
    (r"is a deep-gray brightness", "是深灰亮度"),
    (r"is a light-gray brightness", "是浅灰亮度"),
]


def apply_brightness(text: str, store: dict[str, str]) -> str:
    for pattern, zh in BRIGHT:
        def repl(match: re.Match, zh=zh) -> str:
            key = f"SZX{len(store)}ZXS"
            store[key] = zh
            return key

        text = re.sub(pattern, repl, text)
    return text


def apply_stock(text: str, store: dict[str, str]) -> str:
    text = apply_brightness(text, store)
    for eng, zh in sorted(STOCK, key=lambda item: len(item[0]), reverse=True):
        if eng not in text:
            continue
        key = f"SZX{len(store)}ZXS"
        store[key] = zh
        text = text.replace(eng, key)
    return text


def assign_figures(binding: str) -> tuple[str | None, str | None]:
    she: set[str] = set()
    he: set[str] = set()
    current = None
    for sent in re.split(r"(?<=[.])\s+", binding):
        found = re.search(r"Image (\d+)", sent)
        if found:
            current = found.group(1)
        if not current:
            continue
        if re.search(r"\b(woman|girl)\b", sent, re.I) or re.match(r"She is\b", sent):
            she.add(current)
        if re.search(r"\bman\b", sent, re.I) or re.match(r"He is\b", sent):
            he.add(current)
    return (next(iter(she)) if len(she) == 1 else None, next(iter(he)) if len(he) == 1 else None)


_ADJ = (
    r"(?:left|right|wet|clean|dry|small|other|own|free|open|closed|painted|bare|"
    r"fine|narrow|broad|upper|lower|front|soft|silver|black|yellow|gray|grey|red|"
    r"raw|empty|full|same|little|thin|thick|neat|ordinary|reading|work|home|long|"
    r"short|visible|clear|sealed|bright|dark|pale|cold|warm|foreground)\s+"
)
_NOUNS = (
    r"face|faces|eye|eyes|hand|hands|wrist|wrists|mouth|shoulder|shoulders|cuff|cuffs|"
    r"clothes|clothing|hair|gaze|jaw|finger|fingers|thumb|arm|arms|back|head|body|"
    r"voice|laugh|paint|height|forehead|cheek|cheeks|lip|lips|neck|knee|foot|feet|"
    r"palm|palms|nail|nails|collar|sleeve|badge|glasses|cardigan|dress|shirt|coat|"
    r"skin|profile|chin|brow|lashes|lash|tooth|teeth|elbow|hip|waist|chest|pocket|"
    r"phone|build|pose|ear|ears|nose|forearm|forearms|ankle|ankles|heel|heels|toe|"
    r"toes|knuckle|knuckles|throat|temple|temples|cheekbone|cheekbones|vein|veins|"
    r"sleeve|sleeves|lap|spine"
)


def _possessive(number: str):
    pattern = re.compile(rf"(?:{_ADJ}){{0,3}}(?:{_NOUNS})\b", re.I)

    def repl(match: re.Match) -> str:
        rest = match.string[match.end():].lstrip()
        if pattern.match(rest):
            return f"图{number}的"
        return f"图{number}"

    return repl


def apply_figures(text: str, binding: str) -> str:
    she, he = assign_figures(binding)
    if she:
        text = re.sub(r"\bherself\b", f"图{she}自己", text)
        text = re.sub(r"\b[Hh]ers\b", f"图{she}的", text)
        text = re.sub(r"\b[Hh]er\b", _possessive(she), text)
        text = re.sub(r"\b[Ss]he\b", f"图{she}", text)
    if he:
        text = re.sub(r"\bhimself\b", f"图{he}自己", text)
        text = re.sub(r"\bhim\b", f"图{he}", text)
        text = re.sub(r"\b[Hh]is\b", _possessive(he), text)
        text = re.sub(r"\b[Hh]e\b", f"图{he}", text)
    return text


def apply_blinks(text: str) -> str:
    text = re.sub(
        r"Where eyes are visible, (图\d+) blinks naturally(?:, not held open)?\.",
        r"能看见眼睛时，\1自然地眨眼，不要一直睁着。",
        text,
    )
    text = re.sub(
        r"Where eyes are visible, they blink naturally(?:, not held open)?\.",
        "能看见眼睛时，自然地眨眼，不要一直睁着。",
        text,
    )
    text = re.sub(
        r"(图\d+)的 eyes blink naturally(?:, and are not held open|, not held open)?\.",
        r"\1的眼睛自然地眨眼，不要一直睁着。",
        text,
    )
    text = re.sub(
        r"(图\d+)的 eyes stay open and do not blink\.",
        r"\1的眼睛一直睁着，不要眨眼。",
        text,
    )
    text = re.sub(r"(图\d+)的 eyes do not blink\.", r"\1的眼睛不要眨眼。", text)
    return text


def restore(text: str, store: dict[str, str]) -> str:
    for key in sorted(store, key=len, reverse=True):
        text = text.replace(key, store[key])
    return text


def paras_of(paste: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", paste.strip()) if p.strip()]


def render_camera(line: str, bing: Bing) -> tuple[str, str]:
    match = re.match(
        r"Cinematic (.+?), 16:9, (.+?)(?:, no zoom)?, (\d+)mm lens(?:, no zoom)?, (.+)$",
        line.strip(),
        re.S,
    )
    if not match or match.group(1) not in SHOT_ZH:
        return "", bing.translate(line)
    shot, mid, mm, focus = match.groups()
    focus = focus.strip().rstrip(".")
    height, move = "", mid.strip()
    for eng, zh in HEIGHTS:
        if move.startswith(eng):
            height = zh
            move = move[len(eng):].lstrip(" ,")
            break
    move_zh = MOVES.get(move) or bing.translate(move)
    if focus.startswith("focus on "):
        focus_zh = bing.translate("The focus is on " + focus[len("focus on "):])
    elif focus.endswith(" in focus"):
        focus_zh = bing.translate("The focus is on " + focus[: -len(" in focus")])
    else:
        focus_zh = bing.translate(focus)
    focus_zh = focus_zh.replace("重点是", "焦点在").replace("焦点是", "焦点在")
    body = f"{height}{SHOT_ZH[shot]}，{MMZH[mm]}毫米，{move_zh}，不拉焦距。{focus_zh}"
    return mm, body


def render_sound(para: str, bing: Bing) -> tuple[str, str]:
    match = re.match(r"Duration (\d+) seconds\.\s*(.*)", para.strip(), re.S)
    if not match:
        return "", bing.translate(para)
    return match.group(1), bing.translate(match.group(2))


def polish(text: str) -> str:
    pieces = re.split(r'("[^"]*"|`[^`]*`)', text)
    merged = []
    for index, piece in enumerate(pieces):
        if index % 2 == 0:
            piece = piece.replace(".", "。")
        merged.append(piece)
    text = "".join(merged)
    text = re.sub(r"图\s+(\d+)", r"图\1", text)
    text = text.replace("仅锁定", "只锁定")
    text = text.replace("只锁住", "只锁定")
    text = text.replace("浅灰色亮度", "浅灰亮度")
    text = text.replace("深灰色亮度", "深灰亮度")
    text = text.replace("电影感", "真人实拍")
    text = text.replace("油漆", "颜料")
    text = text.replace("伞缘", "伞沿")
    text = re.sub(r"\ba\s*(?=浅灰亮度|深灰亮度|阴暗|亮明)", "", text)
    text = text.replace("保持在浅灰", "保持浅灰")
    text = text.replace("保持在深灰", "保持深灰")
    text = text.replace("而不是整体构图", "不锁定构图")
    text = text.replace("而不是构图", "不锁定构图")
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if paragraph and paragraph[-1] not in "。！？":
            paragraph += "。"
        if paragraph:
            paragraphs.append(paragraph)
    text = "\n\n".join(paragraphs)
    if "不要旋律" not in text:
        text = text.rstrip() + "不要旋律，不要垫乐。"
    return text.strip()


def translate_paste(sid: str, paste: str, bing: Bing, fix_shot) -> str:
    paste = fix_shot(sid, paste)
    store: dict[str, str] = {}
    paste = apply_stock(paste, store)
    paste = protect_quotes(paste, store)
    blocks = paras_of(paste)
    if len(blocks) < 3:
        raise RuntimeError(f"{sid} has {len(blocks)} paragraphs")
    binding = blocks[1]
    paste = "\n\n".join(blocks)
    paste = apply_figures(paste, binding)
    paste = apply_blinks(paste)
    paste = re.sub(r"Image (\d+)", r"图\1", paste)
    paste = apply_stock(paste, store)
    blocks = paras_of(paste)
    _, camera = render_camera(blocks[0], bing)
    dur, sound = render_sound(blocks[-1], bing)
    middle = [bing.translate(block) for block in blocks[1:-1]]
    head = f"{dur}秒，16:9，真人实拍。{camera}" if dur else camera
    parts = [head, *middle, sound]
    return polish(restore("\n\n".join(p.strip() for p in parts if p.strip()), store))


def structural(text: str) -> str:
    text = text.replace(
        "日期：2026年10月7日（按分镜与剧本重写可贴入）",
        "日期：2026年10月8日（可贴入改为中文，并按分镜与剧本改正动作）",
    )
    text = text.replace(
        "| A-Note     | 抖动手写两行：`You have one sentence.` / `Tell Naomi the red dot is hers.` |",
        "| A-Note     | 抖动手写两行：`你有一句话。` / `告诉 Naomi，红点是她的。`                   |",
    )
    text = text.replace(
        "| 5A 工作室对峙     | 5A.1–5A.40  | 40      |",
        "| 5A 工作室对峙     | 5A.1–5A.40（无 5A.10、5A.21） | 38 |",
    )
    text = text.replace("| **合计**          |             | **169** |", "| **合计**          |             | **167** |")
    text = text.replace("| 5A.10  | 75  | 七十五毫米   |\n", "")
    text = text.replace("| 5A.21  | 65  | 六十五毫米   |\n", "")
    text = text.replace(
        "0:03–0:06 Claire 向画右半步，Gabriel 手从画左伸入将扣腕。",
        "0:03–0:06 Claire 向画右迈出很小的一步，伸手抓住 Gabriel 的手，把他往雨里带。他不拿伞。",
    )
    text = text.replace(
        "- **人物动作** Claire 中速带笑；Gabriel 伞下不动只伸手。",
        "- **人物动作** Claire 中速带笑，伸手抓住 Gabriel 的手；Gabriel 在伞下，不拿伞，被她拽向雨。",
    )
    text = text.replace(
        "**不要做：** 不要让图4的手碰到或抓住手腕；不要露出图4的正脸；不要让图4走进雨里；不要拥抱；不要把图1的脸拍成满框；不要推近。",
        "**不要做：** 不要让图4拿着伞；不要露出图4的正脸；不要让图4自己走进雨里；不要停在指尖靠近却不抓住；不要拥抱；不要把图1的脸拍成满框；不要推近。",
    )
    old_31 = "**素材：** 图1＝P-Naomi-31；图2＝P-Attendant；图3＝L-Counter。\n\n**可贴入：**\n\n```text\nCinematic wide two-shot"
    new_31 = "**素材：** 图1＝P-Naomi-31；图2＝P-Attendant；图3＝L-Counter；图4＝A-Box。\n\n**可贴入：**\n\n```text\nCinematic wide two-shot"
    if text.count(old_31) != 1:
        raise RuntimeError(f"3.1 asset row count {text.count(old_31)}")
    text = text.replace(old_31, new_31)
    old_b11 = "**素材：** 图1＝A-WRI；图2＝L-Kitchen；图3＝P-Claire-36。"
    new_b11 = "**素材：** 图1＝A-WRI；图2＝L-Kitchen；图3＝P-Claire-36；图4＝P-Naomi-13。"
    if text.count(old_b11) != 1:
        raise RuntimeError(f"5B.11 asset row count {text.count(old_b11)}")
    text = text.replace(old_b11, new_b11)
    text = re.sub(
        r"\n### 5A\.10　8秒　七十五毫米　全能参考　16:9\n.*?(?=\n### 5A\.11　)",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\n### 5A\.21　9秒　六十五毫米　全能参考　16:9\n.*?(?=\n### 5A\.22　)",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace("### 5A.22　10秒　四十毫米", "### 5A.22　14秒　四十毫米")
    text = text.replace("| 5A.10  | Naomi", "| 5A.9   | Naomi")
    text = text.replace("| 5A.21  | Naomi", "| 5A.22  | Naomi")
    return text


def main() -> None:
    fix_shot = load_fix_shot()
    text = structural(CHECKPOINT.read_text())
    if "### 5A.10" in text or "### 5A.21" in text:
        raise RuntimeError("extra shots were not removed")
    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}
    lock = threading.Lock()
    workers = [Bing(cache, lock) for _ in range(4)]
    matches = list(re.finditer(r"```text\n(.*?)```", text, flags=re.S))
    jobs = []
    for index, match in enumerate(matches):
        heading = text.rfind("\n### ", 0, match.start())
        sid = re.match(r"\n### ([0-9][0-9A-Z.]*M?)", text[heading:]).group(1)
        jobs.append((index, sid, match.group(1)))
    print(f"shots {len(jobs)} cache {len(cache)}", flush=True)
    results: dict[int, str] = {}

    def run_job(job: tuple[int, str, str]) -> tuple[int, str]:
        index, sid, paste = job
        zh = translate_paste(sid, paste, workers[index % 4], fix_shot)
        return index, zh

    done = 0
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(run_job, job) for job in jobs]
        for future in as_completed(futures):
            index, zh = future.result()
            results[index] = zh
            done += 1
            if done % 10 == 0 or done == len(jobs):
                workers[0].save()
                print(f"{done}/{len(jobs)} cache {len(cache)}", flush=True)
    pieces = []
    pos = 0
    for index, match in enumerate(matches):
        pieces.append(text[pos:match.start()])
        pieces.append("```text\n" + results[index] + "\n```")
        pos = match.end()
    pieces.append(text[pos:])
    out = "".join(pieces)
    ROOT.write_text(out)
    workers[0].save()
    print("wrote", ROOT, "chars", len(out))


if __name__ == "__main__":
    main()
