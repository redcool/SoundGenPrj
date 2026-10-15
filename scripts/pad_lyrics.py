#!/usr/bin/env python3
"""词长补齐工具（历史摇滚系列）——把歌词文件补足到目标字符数。

背景：中文演唱实测 ≈2.2 字/秒；4:00 安全线 ≈ 530 字，稳妥线 570 字。
用法（scripts 目录下执行）：
  python pad_lyrics.py <master.txt> [<clean.txt>] [--min-chars 570]
  - master：带 [] 小节标记的正式词稿
  - clean ：喂给生成引擎的纯词文件（可省略）
补足方式：取第一个 "[Chorus...]" 块（跳过 Pre-Chorus），循环追加到达标。
"""
import argparse, os, re

def body_count(text):
    return len(re.sub(r"[\s\u3000]", "", "\n".join(
        l for l in text.splitlines() if not l.strip().startswith("["))))

def extract_chorus(master):
    blocks = re.findall(r"\[Chorus[^\]]*\]\n((?:[^\[\n][^\n]*\n?)+)", master)
    if not blocks:
        return None
    return [l.rstrip() for l in blocks[0].splitlines() if l.strip()]

def main():
    ap = argparse.ArgumentParser(description="pad lyrics to min chars")
    ap.add_argument("master")
    ap.add_argument("clean", nargs="?", default=None)
    ap.add_argument("--min-chars", type=int, default=570)
    a = ap.parse_args()
    master = open(a.master, encoding="utf-8").read()
    chorus = extract_chorus(master)
    if not chorus:
        print("WARN: no [Chorus] block in", a.master)
        return
    guard = 0
    while body_count(master) < a.min_chars and guard < 8:
        master = master.rstrip("\n") + "\n\n[Chorus · 齐唱尾]\n" + "\n".join(chorus) + "\n"
        guard += 1
    open(a.master, "w", encoding="utf-8").write(master)
    if a.clean and os.path.exists(a.clean):
        clean = open(a.clean, encoding="utf-8").read()
        if guard:
            clean = clean.rstrip("\n") + "\n\n" + "\n\n".join(("\n".join(chorus) for _ in range(guard))) + "\n"
            open(a.clean, "w", encoding="utf-8").write(clean)
    print(os.path.basename(a.master), "->", body_count(master), "chars (min", a.min_chars, ")")

if __name__ == "__main__":
    main()
