"""Whisper 从（人声轨/混音）提取歌词，输出带时间轴 txt。"""
import argparse, os
import torch
import numpy as np
import soundfile as sf
import torchaudio.functional as taf
from transformers import pipeline
from lib_comfy import cfg

MODEL_DIR = cfg("whisper_model_dir") or r"H:\AI\ComfyUI_windows_portable\whisper_models\whisper-small"

def main():
    ap = argparse.ArgumentParser(description="Whisper 歌词提取")
    ap.add_argument("--audio", required=True, help="输入音频（建议先用 separate.py 得到 vocals.flac）")
    ap.add_argument("--lang", default="en", help="语言代码，如 en / zh")
    ap.add_argument("--out", default=None, help="输出 txt 路径（默认与音频同名）")
    args = ap.parse_args()

    out = args.out or os.path.splitext(args.audio)[0] + "_lyrics.txt"
    pipe = pipeline("automatic-speech-recognition", model=MODEL_DIR, device=0,
                    chunk_length_s=30, batch_size=8,
                    generate_kwargs={"language": args.lang, "task": "transcribe"})
    # whisper tokenizer 无 pad_token，设置后 pipeline 才能批处理（否则报 ValueError）
    pipe.tokenizer.pad_token_id = pipe.model.config.eos_token_id
    wav, sr = sf.read(args.audio, dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    wav16 = taf.resample(torch.from_numpy(wav), sr, 16000).numpy()
    result = pipe(wav16, return_timestamps=True)
    lines = []
    for c in result.get("chunks", []):
        ts = c.get("timestamp") or (0, 0)
        t0 = ts[0] if isinstance(ts[0], (int, float)) else 0.0
        t1 = ts[1] if isinstance(ts[1], (int, float)) else t0
        lines.append("[%6.1f - %6.1f] %s" % (t0, t1, c.get("text", "").strip()))
    txt = chr(10).join(lines)
    with open(out, "w", encoding="utf-8") as f:
        f.write(txt)
    print("lyrics ->", out)
    print(txt)

if __name__ == "__main__":
    main()
