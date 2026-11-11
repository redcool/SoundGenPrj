#!/usr/bin/env python3
"""fix_legacy_tags.py — 修正旧版歌词：段标规范化 + 副歌去重(<=3)
用法: python fix_legacy_tags.py <in_lyric.txt> <out_lyric.txt>
规则:
  * [Verse 1 · 说明 · 情绪] → [verse N，情绪/说明，中，编钟+鼓，男声]
  * 重复的同类副歌只保留前 3 个（第1个 chorus / 第2 chorus 2 / 第3 chorus 3）
  * [乱曰 · ...] → [outro，...]
  * 空行与正文原样保留
"""
import re, sys

def parse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    blocks, cur = [], None
    for ln in lines:
        if re.match(r"^\[[^\]]+\]$", ln.strip()):
            cur = {"raw": ln.strip(), "body": []}
            blocks.append(cur)
        else:
            if cur is None:
                cur = {"raw": "", "body": []}
                blocks.append(cur)
            cur["body"].append(ln)
    return blocks

def classify(raw):
    s = raw.strip("[]").strip()
    head = s.split("·")[0].split("，")[0].strip().lower()
    note = ""
    parts = [p.strip() for p in s.split("·")]
    if len(parts) > 1:
        note = "·".join(parts[1:])
    if head.startswith("verse"):
        return "verse", note
    if head.startswith("chorus"):
        return "chorus", note
    if head.startswith("bridge"):
        return "bridge", note
    if head.startswith("outro") or head.startswith("乱曰") or head.startswith("ending"):
        return "outro", note
    if head.startswith("intro") or head.startswith("spoken"):
        return "intro", note
    return "verse", note

def main():
    src, dst = sys.argv[1], sys.argv[2]
    blocks = parse(src)
    vi = ci = 0
    out = []
    kept_chorus = 0
    for b in blocks:
        raw = b["raw"]
        body = "\n".join(b["body"]).strip("\n")
        if not raw:
            if body.strip():
                out.append(body)
            continue
        kind, note = classify(raw)
        if kind == "verse":
            vi += 1
            tag = "[verse %d，%s，中，编钟+鼓，男声]" % (vi, note or "叙")
        elif kind == "chorus":
            kept_chorus += 1
            if kept_chorus > 3:
                continue  # 丢弃多余副歌（同文垫段）
            ci += 1
            tag = "[chorus]" if ci == 1 else "[chorus %d]" % ci
            tag = tag.replace("[chorus", "[chorus") 
            tag = ("[chorus，%s，中快，鼓+弦乐+齐唱，男声]" % (note or "合")) if ci == 1 else ("[chorus %d，%s，中快，鼓+弦乐+齐唱，男声]" % (ci, note or "合"))
        elif kind == "bridge":
            tag = "[bridge，%s，慢，古琴]" % (note or "转")
        elif kind == "outro":
            tag = "[outro，%s，中，编钟+齐唱]" % (note or "结")
        else:
            tag = "[spoken，%s，散，编钟，男中音]" % (note or "引")
        out.append(tag)
        if body.strip():
            out.append(body)
        out.append("")
    text = "\n".join(out).rstrip() + "\n"
    open(dst, "w", encoding="utf-8").write(text)
    print("fixed:", dst, "| verses", vi, "| chorus kept", min(kept_chorus, 3))

if __name__ == "__main__":
    main()
