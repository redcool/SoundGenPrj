"""音频分析 CLI：BPM / 调性 / 频带 / 人声占比 / 时长，输出 JSON 或可读文本。

用法:
  python scripts/analyze_audio.py --input inputSound/一夫当关.mp3
  python scripts/analyze_audio.py --input x.mp3 --json --out analysis.json
"""
import argparse, json, os
from lib_comfy import analyze_audio, cfg


def main():
    ap = argparse.ArgumentParser(description="分析一段音频的特征(BPM/调性/频带/响度)")
    ap.add_argument("--input", required=True, help="输入音频")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--out", default=None, help="JSON 保存路径(可选)")
    args = ap.parse_args()

    a = analyze_audio(args.input)
    if args.json or args.out:
        body = json.dumps(a, ensure_ascii=False, indent=2)
        print(body)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(body)
    else:
        print("时长: %.1fs | 采样率: %d | 声道: %d" % (a["duration"], a["sample_rate"], a["channels"]))
        print("BPM: %.1f | 调性: %s | 响度: %.1f dBFS" % (a["bpm"], a["key"], a["rms_db"]))
        b = a["band_pct"]
        print("频带: 低频 %.1f%% / 中频 %.1f%% / 高频 %.1f%%" % (b["lo"], b["mid"], b["hi"]))


if __name__ == "__main__":
    main()
