"""文生曲 / 文生歌：style(描述) + 可选 lyrics → 生成歌曲。"""
import argparse, sys, os
from lib_comfy import build_chain, submit, wait, report

def main():
    ap = argparse.ArgumentParser(description="YuE2 文本生成音乐/歌曲")
    ap.add_argument("--style", required=True, help="风格描述（英/中）")
    ap.add_argument("--lyrics", help="歌词文件路径")
    ap.add_argument("--no-lyrics", action="store_true", help="纯器乐模式")
    ap.add_argument("--planning", default="full", choices=["full", "melody", "off"])
    ap.add_argument("--seed", type=int, default=831001)
    ap.add_argument("--duration", type=int, default=360, help="最大秒数")
    ap.add_argument("--prefix", default="audio/YuE2/generated", help="输出文件名前缀")
    ap.add_argument("--guidance", type=float, default=1.0)
    args = ap.parse_args()

    lyrics = ""
    if args.lyrics:
        with open(args.lyrics, encoding="utf-8") as f:
            lyrics = f.read().strip()
    elif not args.no_lyrics:
        print("提示：未提供歌词且未 --no-lyrics，按纯器乐处理。如果需要歌曲请提供歌词文件。")

    prompt = build_chain(args.style, lyrics, args.planning, args.seed, None,
                         args.duration, args.prefix, guidance=args.guidance)
    pid = submit(prompt)
    print("prompt_id:", pid)
    outputs = wait(pid)
    report(outputs)

if __name__ == "__main__":
    main()
