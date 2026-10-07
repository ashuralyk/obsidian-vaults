#!/usr/bin/env python3
"""Strip screenplay-only labels from H3 可贴入/不要做; use 图N from **素材** line."""
import re
from pathlib import Path

H3 = Path(__file__).resolve().parents[1] / "MiniMax H3.md"

# Spoken / on-screen text: keep inside these wrappers
DIALOGUE_RE = re.compile(r"\u300c[^\u300d]+\u300d|\"[^\"]+\"|'[^']+'|`[^`]+`")

SCENE_NAME_PATTERNS = [
    r"哈德逊河滨步道",
    r"曼哈顿记忆交易所",
    r"Gabriel\s*工作室",
    r"Naomi\s*公寓",
    r"拍卖行?",
    r"观影舱",
    r"布鲁克林",
    r"哥伦比亚大学",
    r"WHITE\s*ROOM\s*[IVX0-9]+",
    r"《White Rooms》",
]

ASSET_CODE_RE = re.compile(
    r"图(\d+)＝([A-Za-z0-9\-]+(?:\([^)]*\))?)"
)


def split_protected(text: str) -> list[tuple[str, bool]]:
    """Split into (segment, is_protected) where protected = dialogue/quotes."""
    parts: list[tuple[str, bool]] = []
    last = 0
    for m in DIALOGUE_RE.finditer(text):
        if m.start() > last:
            parts.append((text[last : m.start()], False))
        parts.append((m.group(0), True))
        last = m.end()
    if last < len(text):
        parts.append((text[last:], False))
    return parts


def build_fig_map(assets_line: str) -> dict[str, str]:
    """Map role tokens → 图N from **素材** upload order."""
    fig_map: dict[str, str] = {}
    entries = ASSET_CODE_RE.findall(assets_line)
    for n, code in entries:
        fig = f"图{n}"
        code_u = code.upper()
        if code_u.startswith("P-CLAIRE") or "CLAIRE" in code_u:
            fig_map["Claire"] = fig
            fig_map["claire"] = fig
            fig_map["母亲"] = fig
        if code_u.startswith("P-GABRIEL") or "GABRIEL" in code_u:
            fig_map["Gabriel"] = fig
            fig_map["gabriel"] = fig
            fig_map["继父"] = fig
        if code_u.startswith("P-NAOMI") or code_u.startswith("P-HAND"):
            fig_map["Naomi"] = fig
            fig_map["naomi"] = fig
            fig_map["女孩"] = fig
            fig_map["小手"] = fig
            fig_map["当下"] = fig  # weak
        if code_u.startswith("P-MARGOT") or "MARGOT" in code_u:
            fig_map["Margot"] = fig
            fig_map["margot"] = fig
        if code_u.startswith("P-ATTENDANT") or "ATTENDANT" in code_u:
            fig_map["Attendant"] = fig
            fig_map["attendant"] = fig
        if code_u.startswith("L-"):
            fig_map["__LOC__"] = fig  # generic location slot
        if code_u.startswith("A-UMBRELLA"):
            fig_map["黄伞"] = fig
            fig_map["伞"] = fig
        if code_u.startswith("A-FILE"):
            fig_map["案卷"] = fig
        if code_u.startswith("A-PHONE"):
            fig_map["手机"] = fig
    return fig_map


def replace_names(segment: str, fig_map: dict[str, str]) -> str:
    if not segment.strip():
        return segment
    out = segment
    # Remove asset codes in paste body
    out = re.sub(r"图\d+＝[^；。\n]+[；。]?", "", out)
    out = re.sub(r"P-[A-Za-z0-9\-]+", "", out)
    out = re.sub(r"L-[A-Za-z0-9\-]+", "", out)
    out = re.sub(r"A-[A-Za-z0-9\-]+", "", out)
    out = re.sub(r"(?<=[。；\s])图\d+。(?=\s*图\d+。|按时间|摄影机|$)", "", out)
    out = re.sub(r"图\d+。(?=按时间)", "", out)

    loc = fig_map.get("__LOC__")
    for pat in SCENE_NAME_PATTERNS:
        out = re.sub(pat, loc if loc else "场景参考图", out, flags=re.I)

    # Phrases from storyboard bans
    out = re.sub(r"Claire/Gabriel", "各绑定图内人物", out)
    out = re.sub(r"成年\s*Naomi", "图内成年人", out)
    out = re.sub(r"当下\s*Naomi", "图内当下人物", out)

    # Named characters → 图N (longer names first)
    for name in ("Gabriel Mora", "Claire Bennett", "Naomi Bennett", "Margot Rey"):
        if name.split()[0] in fig_map:
            out = out.replace(name, fig_map[name.split()[0]])
        else:
            out = re.sub(re.escape(name), "图内人物", out)

    for name in ("Gabriel", "Claire", "Naomi", "Margot", "Attendant"):
        if name in fig_map:
            out = re.sub(rf"\b{name}\b", fig_map[name], out)
            out = out.replace(name, fig_map[name])  # Chinese context no word boundary

    if "Gabriel" in out and "Gabriel" not in fig_map:
        out = out.replace("Gabriel", "伞下只露袖口与肩的人")
    if "Claire" in out and "Claire" not in fig_map:
        out = out.replace("Claire", "图1")
    if "Naomi" in out and "Naomi" not in fig_map:
        out = out.replace("Naomi", "图1")

    out = re.sub(r"图(\d+)只锁定这位(男子|女子)[^。]*。", r"图\1只锁定外形，不参考姿势。", out)
    out = re.sub(
        r"图(\d+)只锁定[^。]{0,40}?(?:\d+岁|四十八|三十四|五十四)[^。]*。",
        r"图\1只锁定外形，不参考姿势。",
        out,
    )
    out = re.sub(r"图(\d+)只锁定[^：]+：图", r"图\1只锁定外形，不参考姿势。图", out)
    out = re.sub(r"(?<=[。；\s])图(\d+)。(?=[^只])", "", out)
    out = re.sub(r"三十四岁，约一百[^。]+。", "", out)
    out = re.sub(r"约一百[六七八九十]+厘米[^。]*。", "", out)

    out = re.sub(r"。{2,}", "。", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out


def strip_d_camera_codes(text: str) -> str:
    """Remove project-internal D# camera labels from H3 paste (not meaningful to the model)."""
    out = text
    # 远景，D1，头高 → 远景，头高
    out = re.sub(r"，\s*D\d+[A-Z]?\s*，", "，", out)
    out = re.sub(r"，\s*D\d+[A-Z]?\s+", "，", out)
    # 中全景 D2 50mm → 中全景（焦距已在片头）
    out = re.sub(r"(\S+)\s+D\d+[A-Z]?\s+\d+mm", r"\1", out)
    out = re.sub(r"\s+D\d+[A-Z]?\s+\d+mm", "", out)
    out = re.sub(r"\bD\d+[A-Z]?\s+", "", out)
    out = re.sub(r"\bD\d+[A-Z]?\b", "", out)
    out = re.sub(r"换到\s*后", "换到新机位侧后", out)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"，{2,}", "，", out)
    out = re.sub(r"，\s*，", "，", out)
    return out.strip()


def sanitize_text(text: str, assets_line: str) -> str:
    fig_map = build_fig_map(assets_line)
    chunks = split_protected(text)
    rebuilt = []
    for seg, prot in chunks:
        rebuilt.append(seg if prot else replace_names(seg, fig_map))
    return strip_d_camera_codes("".join(rebuilt))


def process_file():
    text = H3.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    current_assets = ""
    in_paste = False
    in_dont = False
    paste_buf: list[str] = []
    dont_buf: list[str] = []

    def flush_paste():
        nonlocal paste_buf
        if paste_buf:
            body = "".join(paste_buf).strip()
            out.append(sanitize_text(body, current_assets) + "\n\n")
            paste_buf = []

    def flush_dont():
        nonlocal dont_buf
        if dont_buf:
            body = "".join(dont_buf).strip()
            if body.startswith("**不要做：**"):
                prefix, rest = body.split("**不要做：**", 1)
                rest = sanitize_text(rest.strip(), current_assets)
                out.append(f"**不要做：** {rest}\n\n")
            else:
                out.append(sanitize_text(body, current_assets) + "\n")
            dont_buf = []

    while i < len(lines):
        line = lines[i]
        if line.startswith("**素材：**"):
            flush_paste()
            flush_dont()
            in_paste = in_dont = False
            current_assets = line.replace("**素材：**", "").strip()
            out.append(line)
            i += 1
            continue
        if line.startswith("**可贴入：**"):
            flush_paste()
            flush_dont()
            in_paste = True
            in_dont = False
            out.append(line)
            i += 1
            continue
        if line.startswith("**不要做：**"):
            flush_paste()
            in_paste = False
            in_dont = True
            dont_buf = [line]
            i += 1
            continue
        if in_paste:
            if line.startswith("**") or line.startswith("### "):
                flush_paste()
                in_paste = False
                out.append(line)
            else:
                paste_buf.append(line)
            i += 1
            continue
        if in_dont:
            if line.startswith("### ") or (
                line.startswith("**") and not line.startswith("**不要做")
            ):
                flush_dont()
                in_dont = False
                out.append(line)
            else:
                dont_buf.append(line)
            i += 1
            continue
        out.append(line)
        i += 1
    flush_paste()
    flush_dont()
    H3.write_text("".join(out), encoding="utf-8")
    print("sanitized", H3)


if __name__ == "__main__":
    process_file()
