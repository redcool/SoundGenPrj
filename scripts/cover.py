"""Cover：保留旋律（锁定谱面）换歌词/换风格重新演绎。"""
import argparse, os
from lib_comfy import build_chain, submit, wait, report

def main():
    ap = argparse.ArgumentParser(description="YuE2 旋律保留 cover")
    ap.add_argument("--abc", required=True, help="原谱面 ABC 文件")
    ap.add_argument("--style", required=True, help="新风格描述")
    ap.add_argument("--lyrics", default=None, help="新歌词文件（可选，纯器乐 cover 省略）")
    ap.add_argument("--seed", type=int, default=831301)
    ap.add_argument("--duration", type=int, default=420)
    ap.add_argument("--prefix", default="audio/YuE2/cover")
    args = ap.parse_args()

    abc = open(args.abc, encoding="utf-8").read()
    lyrics = open(args.lyrics, encoding="utf-8").read().strip() if args.lyrics else ""
    # 锁谱面（full）+ 固定旋律；换 seed/style/歌词即得到新演绎
    prompt = build_chain(args.style, lyrics, "full", args.seed, abc, args.duration, args.prefix)
    pid = submit(prompt)
    print("prompt_id:", pid)
    outputs = wait(pid)
    report(outputs)

if __name__ == "__main__":
    main()
