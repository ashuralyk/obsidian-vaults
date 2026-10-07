#!/usr/bin/env python3
"""Sync MiniMax H3.md paste blocks with Storyboard.md Draft 6 shot bodies."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SB = ROOT / "Storyboard.md"
H3 = ROOT / "MiniMax H3.md"

MM_CN = {
    28: "二十八", 32: "三十二", 35: "三十五", 40: "四十", 50: "五十",
    55: "五十五", 65: "六十五", 70: "七十", 75: "七十五", 85: "八十五",
    100: "一百", 120: "一百二十",
}

SCENE_TONE = {
    "1": "暖夏雨：伞下深灰偏暖，雨幕发亮",
    "2": "夜间工作冷白：纸浅灰，四周阴暗，屏幕冷白，禁止暖黄家居滤镜",
    "3": "白墙白光，人物压平，几乎无色",
    "4": "冷黑舱内，界面冷白",
    "4M_gallery": "香槟暖，白墙白",
    "4M_bed": "冷黑，火为唯一暖源",
    "5A": "高窗冷侧光，灰墙灰布",
    "5B_gallery": "香槟暖，白墙白",
    "5B_kitchen": "日窗自然偏暖，红点唯一高饱和",
    "5B_grad": "六月日光，明亮、饱和偏低",
    "5B_death": "冷黑，禁止夜戏发白",
    "5B_studio": "去暖的灰天光",
    "6": "清晨白或灰天光",
    "7": "冷走廊对假金厅门",
    "8": "前区假金、后排与侧墙冷灰",
    "9": "冷黑加绿河，不恢复暖和谐",
}


def scene_tone_for(shot: str) -> str:
    if shot.startswith("1."):
        if shot == "1.4":
            return SCENE_TONE["1"] + "；河面绿色反光占主体"
        if shot == "1.5":
            return SCENE_TONE["1"] + "；本镜以手与黄伞为主，河绿不得占满画框"
        return SCENE_TONE["1"] + "；本镜河面若入画也不得呈绿色"
    if shot.startswith("2."):
        return SCENE_TONE["2"]
    if shot.startswith("3."):
        return SCENE_TONE["3"]
    if shot.startswith("4."):
        if "M" in shot and shot <= "4.2M":
            return SCENE_TONE["4M_gallery"]
        if "M" in shot:
            return SCENE_TONE["4M_bed"]
        return SCENE_TONE["4"]
    if shot.startswith("5A."):
        return SCENE_TONE["5A"]
    if shot.startswith("5B."):
        if "M" in shot:
            n = float(re.sub(r"[^\d.]", "", shot.split("M")[0].split(".")[-1]) or "0")
            if n <= 8:
                return SCENE_TONE["5B_gallery"]
            if n <= 17:
                return SCENE_TONE["5B_kitchen"]
            if n <= 24:
                return SCENE_TONE["5B_grad"]
            if n <= 35:
                return SCENE_TONE["5B_death"]
        return SCENE_TONE["5B_studio"]
    if shot.startswith("6."):
        return SCENE_TONE["6"]
    if shot.startswith("7."):
        return SCENE_TONE["7"]
    if shot.startswith("8."):
        return SCENE_TONE["8"]
    if shot.startswith("9."):
        return SCENE_TONE["9"]
    return "真人实拍，低饱和，中等反差"


def parse_storyboard(text: str) -> dict[str, dict[str, str]]:
    shots: dict[str, dict[str, str]] = {}
    current = None
    label = None
    buf: list[str] = []

    def flush_label():
        nonlocal label, buf
        if current and label:
            shots[current][label] = "\n".join(buf).strip()
        buf = []

    for line in text.splitlines():
        m = re.match(r"^##### 镜 ([0-9A-Za-z\.M]+) · (D[0-9]+) · (.+)$", line)
        if m:
            flush_label()
            current = m.group(1).strip()
            shots[current] = {
                "_d": m.group(2),
                "_dur_sb": m.group(3).strip(),
            }
            label = None
            continue
        if not current:
            continue
        if line.startswith("##### ") or line.startswith("## 第"):
            flush_label()
            current = None
            label = None
            continue
        if line.strip() == "---":
            flush_label()
            continue
        hm = re.match(r"^\*\*(.+?)\*\*\s*$", line.strip())
        if hm:
            flush_label()
            label = hm.group(1)
            continue
        if label:
            buf.append(line.rstrip())
    flush_label()
    return shots


def parse_h3_mm(header_line: str) -> tuple[int, int, str]:
    # ### 1.1　6秒　二十八毫米　全能参考　16:9
    m = re.match(r"^### ([0-9A-Za-z\.M]+)　(\d+)秒　(.+?)毫米", header_line)
    if not m:
        return 0, 6, "五十"
    shot, dur, mm_cn = m.group(1), int(m.group(2)), m.group(3)
    mm_rev = {v: k for k, v in MM_CN.items()}
    mm = mm_rev.get(mm_cn, 50)
    return mm, dur, mm_cn


def extract_block_parts(block: str) -> dict:
    parts = {
        "header": "",
        "note": "",
        "assets": "",
        "paste": "",
        "dont": "",
        "rest": "",
    }
    lines = block.splitlines()
    if not lines:
        return parts
    parts["header"] = lines[0]
    i = 1
    while i < len(lines) and not lines[i].startswith("**"):
        if lines[i].strip():
            parts["note"] += lines[i] + "\n"
        i += 1
    while i < len(lines):
        if lines[i].startswith("**分镜对照：**"):
            i += 1
            while i < len(lines) and not lines[i].startswith("**"):
                i += 1
            continue
        if lines[i].startswith("**素材：**"):
            parts["assets"] = lines[i].replace("**素材：**", "").strip()
            i += 1
            continue
        if lines[i].startswith("**可贴入：**"):
            i += 1
            paste_lines = []
            while i < len(lines) and not lines[i].startswith("**不要做：**"):
                paste_lines.append(lines[i])
                i += 1
            parts["paste"] = "\n".join(paste_lines).strip()
            continue
        if lines[i].startswith("**不要做：**"):
            i += 1
            dont_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("### "):
                dont_lines.append(lines[i])
                i += 1
            parts["dont"] = "\n".join(dont_lines).strip()
            continue
        i += 1
    return parts


def is_placeholder(s: str) -> bool:
    return not s or "待" in s or s.startswith("（待")


def storyboard_digest(sb: dict[str, str]) -> str:
    picture_keys = [k for k in sb if k.startswith("画面")]
    picture_keys.sort(key=lambda k: ("（" not in k, k))
    keys = ["衔接·入"] + picture_keys + [
        "摄影机", "人物动作", "摄影机·人物·声音", "声音",
        "主意·第一眼·光", "需要注意", "禁止出现", "衔接·出",
    ]
    lines = []
    seen_pic = False
    for k in keys:
        if k.startswith("画面"):
            if seen_pic:
                continue
            seen_pic = True
            val = pick_picture(sb)
            if not val or is_placeholder(val):
                continue
            lines.append(f"- **画面** {val}")
            continue
        if k in sb and sb[k] and not is_placeholder(sb[k]):
            lines.append(f"- **{k}** {sb[k]}")
    return "\n".join(lines)


def pick_picture(sb: dict[str, str]) -> str:
    for k in sb:
        if k.startswith("画面"):
            if not is_placeholder(sb[k]):
                return sb[k]
    return sb.get("画面", "")


def pick_camera_action_sound(sb: dict[str, str]) -> tuple[str, str, str]:
    cam = sb.get("摄影机", "")
    act = sb.get("人物动作", "")
    snd = sb.get("声音", "")
    combo = sb.get("摄影机·人物·声音", "")
    if is_placeholder(cam) and combo and not is_placeholder(combo):
        return combo, "", ""
    return cam, act, snd


def expand_asset_bindings(assets: str, old_paste: str) -> str:
    """Prefer legacy 图N只锁定 sentences; else expand compact 素材 line."""
    binds = re.findall(r"图\d+只[^。]+。", old_paste)
    if binds:
        return "".join(binds)
    if not assets:
        return ""
    out = []
    for seg in re.split(r"[；;]", assets):
        seg = seg.strip()
        m = re.match(r"图(\d+)＝([^（]+)（([^）]+)）", seg)
        if m:
            n, _code, role = m.groups()
            role = role.replace("只锁", "锁定").strip()
            if not role.startswith("锁"):
                role = "锁定" + role
            out.append(f"图{n}只{role}，不参考构图或人物。")
        elif seg.startswith("图"):
            out.append(seg + "。")
    return "".join(out)


def extract_dialogue_from_paste(paste: str) -> str:
    """Pull only dialogue delivery lines from legacy paste, not whole paragraph."""
    m = re.search(
        r"(图[0-9][^。]*?语速[^。]*?「[A-Za-z0-9 .,!?'\"]+」[^。]*。?)",
        paste,
    )
    if m:
        return m.group(1).strip()
    m = re.search(r"[^。]*「[A-Za-z][^」]+」[^。]*。?", paste)
    if m and "只锁定" not in m.group(0)[:20]:
        return m.group(0).strip()
    return ""


STANDARD_MIDDLE = (
    "凡能看见眼睛的活人有自然的眨眼即可，不要死盯不眨。"
    "已死的人眼皮不动；快门冻结后不要眨眼；"
    "只见手、后脑、物件或空景时不要为了眨眼而露出脸。"
    "光影自带叙事张力，明暗按本镜已写的亮度切开人物与空间的权力和距离，"
    "禁止用平光把关系抹平，禁止靠配乐或字幕补情绪。"
)


def build_paste(
    shot: str,
    h3_dur: int,
    mm: int,
    mm_cn: str,
    assets: str,
    sb: dict[str, str],
    old_paste: str,
) -> str:
    tone = scene_tone_for(shot)
    pic = pick_picture(sb)
    cam, act, snd = pick_camera_action_sound(sb)
    idea = sb.get("主意·第一眼·光", "")
    if idea.startswith("视觉主意："):
        idea = idea.replace("视觉主意：", "").strip()

    # Detailed timed picture from Draft 6 scene 1 style
    has_timed = "0:00" in pic or "0:01" in pic

    parts = [
        f"{h3_dur}秒、16:9视频。焦距{mm_cn}毫米，固定不许变焦。",
        f"本镜色调是{tone}。{STANDARD_MIDDLE}真人实拍。",
    ]
    bind = expand_asset_bindings(assets, old_paste)
    if bind:
        parts.append(bind)

    motion_bits = []
    if has_timed:
        motion_bits.append(f"按时间展开：{pic}")
    elif pic:
        motion_bits.append(pic)
    if cam and not is_placeholder(cam):
        motion_bits.append(f"摄影机：{cam}")
    if act and not is_placeholder(act):
        motion_bits.append(f"人物：{act}")
    if idea:
        motion_bits.append(f"第一眼与光：{idea}")

    if not motion_bits and old_paste:
        core = old_paste
        for pat in [
            r"^\d+秒、16:9视频。",
            r"焦距.+?固定不许变焦。",
            r"本镜色调是.+?。",
            STANDARD_MIDDLE,
            r"真人实拍[^。]*。",
        ]:
            core = re.sub(pat, "", core)
        core = re.sub(r"图\d+只锁定[^。]+。", "", core)
        core = re.sub(r"图\d+只[^。]+。", "", core)
        dlg_strip = extract_dialogue_from_paste(core)
        if dlg_strip:
            core = core.replace(dlg_strip, "")
        core = core.strip()
        if core:
            motion_bits.append(core)

    parts.append(" ".join(motion_bits))

    if snd and not is_placeholder(snd):
        parts.append(
            f"声音：{snd.rstrip('。')}。只保留现场说话、环境音和动作音，不要旋律、不要垫乐。"
        )
    else:
        parts.append("只保留环境音与动作音，不要旋律、不要垫乐。")

    dlg = extract_dialogue_from_paste(old_paste)
    combined = "".join(parts)
    if dlg and dlg not in combined and "「" not in (snd or ""):
        parts.append(dlg)
    elif snd and "「" in snd and "语速" not in combined:
        # storyboard quoted line — add delivery hint if legacy had one
        legacy_dlg = extract_dialogue_from_paste(old_paste)
        if legacy_dlg and "语速" in legacy_dlg:
            parts.append(legacy_dlg)

    note = sb.get("需要注意", "")
    ban = sb.get("禁止出现", "")
    ban_bits = []
    if ban and not is_placeholder(ban):
        ban_bits.append(ban.replace("；", "，"))
    if note and not is_placeholder(note) and "勿" in note:
        ban_bits.append(note)
    if ban_bits:
        parts.append("不要：" + "；".join(dict.fromkeys(ban_bits)) + "。")

    seam_in = sb.get("衔接·入", "")
    if seam_in and not is_placeholder(seam_in) and has_timed:
        parts.insert(2, f"入镜：{seam_in}")

    text = "".join(parts)
    text = text.replace("。。", "。")
    return text


def build_dont(sb: dict[str, str], old_dont: str) -> str:
    ban = sb.get("禁止出现", "")
    if ban and not is_placeholder(ban):
        items = re.split(r"[；;、]", ban)
        items = [x.strip() for x in items if x.strip()]
        base = old_dont.split("；") if old_dont else []
        merged = []
        for x in items + base:
            x = x.strip().rstrip("。")
            if x and x not in merged and "待补" not in x:
                merged.append(x)
        return "；".join(merged[:8]) + "。" if merged else old_dont
    return old_dont


def main():
    sb_text = SB.read_text(encoding="utf-8")
    h3_text = H3.read_text(encoding="utf-8")
    shots = parse_storyboard(sb_text)

    # split H3 into preamble + blocks
    block_re = re.compile(r"(?m)^### ([0-9A-Za-z\.M]+)　")
    matches = list(block_re.finditer(h3_text))
    if not matches:
        raise SystemExit("no H3 blocks found")

    out = [h3_text[: matches[0].start()]]
    # update preamble reference
    preamble = out[0]
    preamble = preamble.replace("Storyboard.md` Draft 5", "Storyboard.md` Draft 6")
    preamble = preamble.replace(
        "日期：2026年10月5日",
        "日期：2026年10月7日（分镜 Draft 6 同步）",
    )
    if "分镜对照" not in preamble:
        preamble = preamble.replace(
            "一条成片对应一镜。",
            "一条成片对应一镜；每条含 **分镜对照**（与 Storyboard 同步）与 **可贴入**（按对照压缩成 H3 公式，尽可能还原画面与运镜）。",
        )
    out[0] = preamble

    for idx, m in enumerate(matches):
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(h3_text)
        block = h3_text[start:end].rstrip() + "\n\n"
        header_line = block.splitlines()[0]
        shot = re.match(r"^### ([0-9A-Za-z\.M]+)", header_line).group(1)
        mm, h3_dur, mm_cn = parse_h3_mm(header_line)
        parts = extract_block_parts(block)
        sb = shots.get(shot, {})

        digest = storyboard_digest(sb)
        new_paste = build_paste(
            shot, h3_dur, mm, mm_cn, parts["assets"], sb, parts["paste"]
        )
        new_dont = build_dont(sb, parts["dont"])

        rebuilt = [header_line, ""]
        if parts["note"].strip():
            rebuilt.append(parts["note"].rstrip())
            rebuilt.append("")
        if digest:
            rebuilt.append("**分镜对照：**")
            rebuilt.append("")
            rebuilt.append(digest)
            rebuilt.append("")
        if parts["assets"]:
            rebuilt.append(f"**素材：** {parts['assets']}")
            rebuilt.append("")
        rebuilt.append("**可贴入：**")
        rebuilt.append("")
        rebuilt.append(new_paste)
        rebuilt.append("")
        rebuilt.append(
            "**不要做：** "
            + (new_dont if new_dont else (parts["dont"] or "换脸换装；加配乐；加字幕。"))
        )
        rebuilt.append("")
        out.append("\n".join(rebuilt) + "\n")

    # tail after last block (dialogue table etc.)
    last_end = matches[-1].start()
    tail_start = h3_text.find("\n## ", last_end)
    if tail_start == -1:
        tail_start = len(h3_text)
    # find section after last ### block content - use end of last block from original
    last_block_end = matches[-1].start()
    # scan for ## 台词索引 or similar after shots
    tail_m = re.search(r"\n## 台词索引", h3_text[last_end:])
    if tail_m:
        out.append(h3_text[last_end + tail_m.start() :])
    else:
        out.append(h3_text[last_end:])

    result = out[0] + "".join(out[1:])
    # fix delivery check line
    result = result.replace(
        "每条都有时长、16:9、具体焦距、本镜色调",
        "每条都有分镜对照、时长、16:9、具体焦距、本镜色调",
    )
    H3.write_text(result, encoding="utf-8")
    print(f"Updated {H3.name}: {len(shots)} storyboard shots, {len(matches)} H3 blocks")


if __name__ == "__main__":
    main()
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(Path(__file__).parent / "sanitize_h3_paste.py")],
        check=True,
    )
