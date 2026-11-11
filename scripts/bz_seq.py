#!/usr/bin/env python3
"""bz_seq.py — 别字版生成（顺序编号，不去重、不改正文）
用法: python bz_seq.py <lyric.txt> <out_bz.txt>
规则:
  * 每个段标按出现顺序编号: verse 1→[Verse], verse 2→[Verse 2] ...
  * chorus 依次 → [Chorus], [Chorus 2], [Chorus 3] ...（重复副歌也保留，只编号）
  * bridge → [Bridge]; 乱曰/outro/ending → [Outro]; spoken/intro → [Intro]
  * 正文逐字保留，仅做同音易字（EASY 表）
"""
import re, sys
from make_bz import EASY

def easy(text):
    for k, v in EASY.items():
        text = text.replace(k, v)
    return text

def main():
    src, dst = sys.argv[1], sys.argv[2]
    lines = open(src, encoding="utf-8").read().split("\n")
    vi = ci = 0
    out = []
    for ln in lines:
        m = re.match(r"^\[([^\]]+)\]$", ln.strip())
        if m:
            body = m.group(1).strip()
            head = body.split("·")[0].split("，")[0].strip().lower()
            if head.startswith("verse"):
                vi += 1
                tag = "[Verse]" if vi == 1 else "[Verse %d]" % vi
            elif head.startswith("chorus"):
                ci += 1
                tag = "[Chorus]" if ci == 1 else "[Chorus %d]" % ci
            elif head.startswith("bridge"):
                tag = "[Bridge]"
            elif head.startswith("outro") or head.startswith("乱曰") or head.startswith("ending"):
                tag = "[Outro]"
            elif head.startswith("intro") or head.startswith("spoken"):
                tag = "[Intro]"
            else:
                vi += 1
                tag = "[Verse %d]" % vi
            out.append(tag)
        else:
            out.append(easy(ln))
    open(dst, "w", encoding="utf-8").write("\n".join(out))
    print("bz_seq:", dst, "| verse", vi, "| chorus", ci)

if __name__ == "__main__":
    main()
