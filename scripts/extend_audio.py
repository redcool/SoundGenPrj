"""音频续写 extend_audio：分析原曲 → 同风格（同调性）生成续段 → 拼接 → 交付。

用法:
  python scripts/extend_audio.py \
      --input inputSound/一夫当关.mp3 \
      --target-duration 480 \
      --out output/yue2/一夫当关_续写版 \
      [--style "可选风格覆盖"] [--seed 831001] [--crossfade 0.5] [--format mp3] [--bitrate 320]

流程: 分析(analyze_audio) → style(自动/覆盖) → 续段生成(planning full, key 写入 style)
      → concat/crossfade 拼接 → 交付格式转换。
风格缺省时由分析自动构建："Epic instrumental ... <bpm> BPM, in <key> ... 续写段落与原曲风格一致"。
"""
import argparse, json, os, time
from lib_comfy import (
    build_chain, submit, wait, report, cfg,
    analyze_audio, engine_audio_path, join_audio, to_delivery,
)

# 缺省风格模板：高位能量 / 史诗 / 无词续写；bpm/key 动态填充
STYLE_TEMPLATE = (
    "Epic instrumental {mood}, {bpm} BPM, in the key of {key}, "
    "powerful driving rhythm, heavy distorted electric guitars and pounding drums, "
    "no vocals, clean modern production, a strong continuation section that matches "
    "the existing piece in tempo, key and energy"
)
MOOD_POOL = ["heavy rock/metal", "orchestral metal", "power metal", "cinematic rock"]


def auto_style(a, mood_index=0):
    mood = MOOD_POOL[mood_index % len(MOOD_POOL)]
    key = a["key"] if a["key"] != "unknown" else "C major"
    bpm = a["bpm"] if a["bpm"] else 140
    return STYLE_TEMPLATE.format(mood=mood, bpm=round(bpm), key=key)


def main():
    ap = argparse.ArgumentParser(description="音频续写：原曲+同风格续段拼接延长")
    ap.add_argument("--input", required=True, help="原始音频")
    ap.add_argument("--target-duration", type=int, default=480, help="目标总长(秒)，默认 480")
    ap.add_argument("--out", required=True, help="输出前缀（自动加 _ext.mp3 等）")
    ap.add_argument("--style", default=None, help="续段风格描述（覆盖自动构建）")
    ap.add_argument("--seed", type=int, default=831001)
    ap.add_argument("--crossfade", type=float, default=0.5, help="拼接交叉淡化秒数(0=直拼)")
    ap.add_argument("--mood-index", type=int, default=0, help="自动风格气氛模板下标")
    ap.add_argument("--format", default="mp3", choices=["mp3", "flac", "wav", "ogg", "opus"])
    ap.add_argument("--bitrate", type=int, default=320)
    ap.add_argument("--no-analysis", action="store_true", help="跳过分析(直接由 --style 驱动)")
    ap.add_argument("--planning", default="full", choices=["full", "melody", "off"])
    ap.add_argument("--prefix", default="audio/YuE2/yfg_ext", help="引擎输出前缀")
    args = ap.parse_args()

    # 1) 分析原曲
    a = analyze_audio(args.input)
    print("[1/5] 原曲分析:", json.dumps({k: a[k] for k in ("duration", "bpm", "key", "rms_db")}, ensure_ascii=False))
    if args.no_analysis:
        style = args.style or "Epic instrumental continuation, matching the source, no vocals"
    else:
        style = args.style or auto_style(a, args.mood_index)
    print("[2/5] 续段 style:", style)

    # 2) 计算续段时长（目标 - 原曲，留一点余量）
    orig_dur = a["duration"]
    seg_duration = max(30, args.target_duration - int(orig_dur))
    print("[3/5] 续段目标时长:", seg_duration, "s（总目标", args.target_duration, "s）")

    # 3) 生成续段
    prompt = build_chain(style, "", args.planning, args.seed, None, seg_duration, args.prefix)
    pid = submit(prompt)
    print("prompt_id:", pid)
    outputs = wait(pid)
    report(outputs)
    audio_meta = (outputs.get("5", {}).get("audio") or [])
    if not audio_meta:
        raise RuntimeError("generation produced no audio")
    seg_file = engine_audio_path(audio_meta[0].get("subfolder", ""), audio_meta[0].get("filename", ""))
    print("[4/5] 续段文件:", seg_file)

    # 4) 拼接（原曲 + 续段）
    out_wav = args.out + "_joined.wav"
    join_audio([args.input, seg_file], out_wav, crossfade=args.crossfade)
    print("[5/5] 已拼接:", out_wav)

    # 5) 交付格式
    if args.format == "flac":
        final = args.out + ".flac"
        to_delivery(out_wav, final, "flac")
    elif args.format == "wav":
        final = out_wav
    else:
        final = args.out + "." + args.format
        to_delivery(out_wav, final, args.format, args.bitrate)
    try:
        os.remove(out_wav)
    except OSError:
        pass
    print("交付:", final)
    print("总长≈ %.1f s = %d:%02d" % (orig_dur + seg_duration + (args.crossfade if args.crossfade else 0),
                                       int(orig_dur + seg_duration) // 60, int(orig_dur + seg_duration) % 60))


if __name__ == "__main__":
    main()
