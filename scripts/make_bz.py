#!/usr/bin/env python3
"""make_bz.py — 正常版 lyric → 别字版（段标英文化 + 逐字同音易字）
用法: python make_bz.py <lyric.txt> [out_bz.txt]
规则:
  1) 中文段标 [verse 1，...] → [Verse] / [Verse 2] / [Chorus] / [Chorus 2] / [Bridge] / [Outro]
  2) 段标里的表演提示（情绪/节奏/乐器/人声）一律丢弃（模型会唱出来）
  3) 按 EASY 表做逐字同音替换（难读字→同音常用字），不改语义核心词
"""
import re, sys, os

EASY = {
    "翚": "辉", "骊": "梨", "诡": "鬼", "浞": "捉", "豷": "意",
    "嚭": "匹", "虢": "国", "缒": "坠", "佚": "义", "氾": "凡",
    "缯": "增", "邾": "朱", "郤": "细", "郢": "影", "鄢": "焉",
    "隗": "伟", "嬖": "必", "睢": "虽", "姒": "四", "囏": "艰",
    "釐": "厘", "婺": "务", "郏": "夹", "莒": "举", "邳": "批",
    "妘": "云", "斟鄩": "真寻", "斟灌": "真贯", "昆吾": "昆吴",
    "豢": "换", "沬": "昧", "砭": "边", "弭": "米", "汭": "锐",
    "皋": "高", "谗": "缠", "诡": "鬼", "鄢": "焉", "郾": "眼", "郯": "谈",
    "亳": "伯", "甬": "勇", "邗": "寒", "耆": "其", "黎": "犁",
}

def convert_tag(line: str) -> str:
    m = re.match(r"^\[([^\]]+)\]$", line.strip())
    if not m:
        return line
    body = m.group(1)
    name = re.split(r"[，,]", body)[0].strip()
    low = name.lower()
    if low.startswith("spoken") or low.startswith("intro"):
        return "[Intro]"
    if low.startswith("verse") or low.startswith("verse"):
        num = re.search(r"(\d+)", name)
        return "[Verse]" if (not num or num.group(1) == "1") else "[Verse %s]" % num.group(1)
    if low.startswith("chorus"):
        num = re.search(r"(\d+)", name)
        return "[Chorus]" if (not num or num.group(1) == "1") else "[Chorus %s]" % num.group(1)
    if low.startswith("bridge"):
        return "[Bridge]"
    if low.startswith("outro"):
        return "[Outro]"
    if low.startswith("prechorus") or low.startswith("pre"):
        return "[PreChorus]"
    return "[Verse]"

def easy(text: str) -> str:
    for k, v in EASY.items():
        text = text.replace(k, v)
    return text

def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"_lyric\.txt$", "_v1_bz_lyrics.txt", src)
    out = []
    for line in open(src, encoding="utf-8").read().split("\n"):
        s = line.rstrip()
        if re.match(r"^\[[^\]]+\]$", s.strip()):
            out.append(convert_tag(s))
        else:
            out.append(easy(s))
    open(dst, "w", encoding="utf-8").write("\n".join(out))
    print("bz:", dst)

if __name__ == "__main__":
    main()