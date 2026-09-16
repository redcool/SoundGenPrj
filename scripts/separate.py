"""Demucs 人声分离：no_vocals.flac（伴奏）+ vocals.flac（人声）。"""
import argparse, os
import numpy as np
import torch
import soundfile as sf
import torchaudio.functional as taf
import yaml
from demucs.hf import load_safetensors_model
from demucs.apply import BagOfModels, apply_model
from lib_comfy import cfg

MODEL_DIR = cfg("demucs_model_dir") or r"H:\AI\ComfyUI_windows_portable\demucs_models\htdemucs"

def load_bag():
    with open(os.path.join(MODEL_DIR, "htdemucs.yaml")) as f:
        cfg = yaml.safe_load(f)
    models = [load_safetensors_model(os.path.join(MODEL_DIR, sig + ".safetensors")) for sig in cfg["models"]]
    bom = BagOfModels(models, cfg.get("weights"), cfg.get("segment"))
    bom = bom.to("cuda" if torch.cuda.is_available() else "cpu").eval()
    return bom

def separate(src, out_dir, bom):
    os.makedirs(out_dir, exist_ok=True)
    wav, sr = sf.read(src, dtype="float32")
    if wav.ndim == 1:
        wav = np.stack([wav, wav], -1)
    wav = wav.T
    if sr != 44100:
        wav = taf.resample(torch.from_numpy(wav), sr, 44100).numpy()
    ref = wav.mean(0); scale = ref.std()
    mix = torch.from_numpy((wav - ref.mean()) / scale)[None].to(next(bom.parameters()).device)
    with torch.no_grad():
        sources = apply_model(bom, mix, shifts=1, split=True, overlap=0.25, progress=True, num_workers=0)
    arr = (sources[0].cpu().numpy() * scale) + ref.mean()
    sf.write(os.path.join(out_dir, "no_vocals.flac"), (arr[0] + arr[1] + arr[2]).T, 44100)
    sf.write(os.path.join(out_dir, "vocals.flac"), arr[3].T, 44100)
    print("separated ->", out_dir)

def main():
    ap = argparse.ArgumentParser(description="Demucs 人声分离")
    ap.add_argument("--input", required=True, help="输入 flac/wav")
    ap.add_argument("--out", required=True, help="输出目录（自动建目录，写入 no_vocals.flac / vocals.flac）")
    args = ap.parse_args()
    bom = load_bag()
    separate(args.input, args.out, bom)

if __name__ == "__main__":
    main()
