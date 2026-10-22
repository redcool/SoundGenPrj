"""文生曲 / 文生歌：style(描述) + 可选 lyrics → 生成歌曲，自动保存四件套。

规则（docs/歌曲生成规则.md）：
  1. 默认中文发声 —— 未指定语言时，style 自动追加 Mandarin Chinese vocals；
  2. 保存四件套 —— 音频(mp3) + 歌词(.lyrics.txt) + ABC 曲谱(.score.abc) + 曲谱 HTML(.html)。
"""
import argparse, sys, os
from lib_comfy import build_chain, submit, wait, report, save_song_package, cfg, engine_audio_path

CHINESE_STYLE_HINT = "Mandarin Chinese vocals"


def main():
    ap = argparse.ArgumentParser(description="YuE2 文本生成音乐/歌曲（规则: 默认中文 + 四件套保存）")
    ap.add_argument("--style", required=True, help="风格描述（英/中）")
    ap.add_argument("--lyrics", help="歌词文件路径")
    ap.add_argument("--no-lyrics", action="store_true", help="纯器乐模式")
    ap.add_argument("--planning", default="full", choices=["full", "melody", "off"])
    ap.add_argument("--seed", type=int, default=831001)
    ap.add_argument("--duration", type=int, default=360, help="最大秒数")
    ap.add_argument("--prefix", default="audio/YuE2/generated", help="引擎输出文件名前缀")
    ap.add_argument("--guidance", type=float, default=1.0)
    ap.add_argument("--out", default=None, help="交付前缀（默认 output/yue2/<basename>）")
    ap.add_argument("--format", default="mp3", choices=["mp3", "flac", "wav", "ogg", "opus"])
    ap.add_argument("--bitrate", type=int, default=192)
    ap.add_argument("--no-save-package", action="store_true", help="关闭四件套保存（仅交付音频）")
    ap.add_argument("--abc", default=None, help="锁谱生成：传入 ABC 谱面文件（planning 需 full/melody）")
    args = ap.parse_args()

    lyrics = ""
    if args.lyrics:
        with open(args.lyrics, encoding="utf-8") as f:
            lyrics = f.read().strip()
    elif not args.no_lyrics:
        print("提示：未提供歌词且未 --no-lyrics，按纯器乐处理。如果需要歌曲请提供歌词文件。")

    # 规则1：未指明语言时默认中文发声
    style = args.style
    lang_lower = style.lower()
    if not args.no_lyrics and not any(k in lang_lower for k in (
            "chinese", "mandarin", "english", "中文", "mandarin chinese vocals")):
        style = style.strip() + ", " + CHINESE_STYLE_HINT
    print("style:", style)

    abc = None
    if args.abc:
        with open(args.abc, encoding="utf-8") as f:
            abc = f.read().strip()
    prompt = build_chain(style, lyrics, args.planning, args.seed, abc,
                         args.duration, args.prefix, guidance=args.guidance)
    pid = submit(prompt)
    print("prompt_id:", pid)
    outputs = wait(pid)
    report(outputs)

    # 定位引擎 flac
    audio_meta = (outputs.get("5", {}).get("audio") or [])
    if not audio_meta:
        raise RuntimeError("generation produced no audio")
    engine_flac = engine_audio_path(audio_meta[0].get("subfolder", ""), audio_meta[0].get("filename", ""))
    print("引擎输出:", engine_flac)

    # 规则2：交付四件套（默认开启）
    if args.no_save_package:
        print("已跳过四件套保存（--no-save-package）")
        return
    os.makedirs("output/yue2", exist_ok=True)
    if not args.out:
        base = os.path.basename(engine_flac).rsplit("_", 1)[0].rsplit(".", 1)[0]
        args.out = os.path.join("output", "yue2", "generated_" + base)
    print("保存四件套 ->", args.out)
    paths = save_song_package(args, outputs, engine_flac, lyrics_path=args.lyrics)
    for k, v in paths.items():
        if v:
            print("  %-7s %s" % (k, v))


if __name__ == "__main__":
    main()