#!/usr/bin/env python3
"""One-pass: strip D# only inside **可贴入** / **不要做** blocks (leave 分镜对照)."""
import re
from pathlib import Path

H3 = Path(__file__).resolve().parents[1] / "MiniMax H3.md"
from sanitize_h3_paste import strip_d_camera_codes  # noqa: E402


def main():
    lines = H3.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    mode = None
    buf: list[str] = []

    def flush():
        nonlocal buf, mode
        if not buf:
            return
        body = "".join(buf)
        if mode == "paste":
            out.append(strip_d_camera_codes(body.strip()) + "\n\n")
        elif mode == "dont":
            line = body.strip()
            if line.startswith("**不要做：**"):
                _, rest = line.split("**不要做：**", 1)
                out.append(f"**不要做：** {strip_d_camera_codes(rest.strip())}\n\n")
            else:
                out.append(strip_d_camera_codes(body) + "\n")
        buf = []
        mode = None

    for line in lines:
        if line.startswith("**可贴入：**"):
            flush()
            mode = "paste"
            out.append(line)
            continue
        if line.startswith("**不要做：**"):
            flush()
            mode = "dont"
            buf = [line]
            continue
        if mode == "paste":
            if line.startswith("**") or line.startswith("### "):
                flush()
                out.append(line)
            else:
                buf.append(line)
            continue
        if mode == "dont":
            if line.startswith("### ") or (
                line.startswith("**") and not line.startswith("**不要做")
            ):
                flush()
                out.append(line)
            else:
                buf.append(line)
            continue
        out.append(line)
    flush()
    H3.write_text("".join(out), encoding="utf-8")
    print("stripped D# in paste/dont blocks:", H3)


if __name__ == "__main__":
    main()
