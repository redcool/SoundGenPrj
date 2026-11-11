#!/usr/bin/env python3
"""make_style.py — 按五段式生成 YuE2 style 描述
用法示例:
  python make_style.py --genre "Chinese wuxia rock" --mood "mid-slow and restrained" \
    --bpm 96 --rhythm "half-time drums with a slow build" \
    --instruments "solo guqin and xun under distant war drums, crackling electric pipa, tolling bianzhong" \
    --vocal "low male lead, hushed and close-mic, aged and story-worn" \
    --production "dry, roomy, unprocessed" --out song_style.txt
"""
import argparse

def build(a):
    parts = []
    head = a.genre.strip()
    if a.mood:
        head += ", " + a.mood.strip()
    parts.append(head)
    tempo = "%d bpm" % a.bpm
    if a.rhythm:
        tempo += ", " + a.rhythm.strip()
    parts.append(tempo)
    if a.instruments:
        parts.append(a.instruments.strip())
    if a.vocal:
        parts.append(a.vocal.strip())
    prod = []
    if a.production:
        prod.append(a.production.strip() + " production")
    prod.append("Mandarin Chinese vocals")
    parts.append(", ".join(prod))
    text = "; ".join(p for p in parts if p)
    if a.extra:
        text += "; " + a.extra.strip()
    return text

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--genre", required=True)
    p.add_argument("--mood", default="")
    p.add_argument("--bpm", type=int, required=True)
    p.add_argument("--rhythm", default="")
    p.add_argument("--instruments", default="")
    p.add_argument("--vocal", default="")
    p.add_argument("--production", default="")
    p.add_argument("--extra", default="")
    p.add_argument("--out", default="")
    a = p.parse_args()
    text = build(a)
    print(text)
    print("words:", len(text.split()))
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text + "\n")
        print("saved:", a.out)

if __name__ == "__main__":
    main()
