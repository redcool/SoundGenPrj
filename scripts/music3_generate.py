"""本地 ComfyUI MiniMax Music3 生成歌曲（ComfyUI 核心自带节点）。
链路：UNETLoader(DiT) + CLIPLoader(minimax) + VAELoader(DAV)
     -> MiniMaxMusic3TextEncode(caption/lyrics/seed/max_duration/cfg/topk)
     -> EmptyMiniMaxMusic3LatentAudio -> KSampler -> VAEDecodeAudio -> SaveAudio
说明：时长上限 = 9000 帧 / 25fps = 360 秒（模型可提前结束）。
用法：
  python scripts/music3_generate.py --caption-file input/captions/x.txt --lyrics input/lyrics/x.txt --prefix audio/YuE2/m3_song --duration 180
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_comfy import load_config, submit, wait, report

MAX_SECONDS = 360.0

def build(cfg, caption, lyrics, seed, duration, prefix):
    m3 = cfg.get("music3", {}) or {}
    dit = m3.get("dit") or "minimax_music3_dit_fp16.safetensors"
    te = m3.get("text_encoder") or "minimax_music3_text_encoder_pruned_int8_convrot.safetensors"
    dav = m3.get("dav") or "minimax_music3_dav.safetensors"
    cfg_scale = float(m3.get("cfg_scale", 1.5))
    top_k = int(m3.get("top_k", 50))
    dur = min(MAX_SECONDS, max(1.0, float(duration)))
    enc = {
        "clip": ["2", 0], "caption": caption, "lyrics": lyrics or "", "seed": seed,
        "max_duration": dur, "cfg_scale": cfg_scale, "top_k": top_k,
    }
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": dit, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": te, "type": "minimax"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": dav}},
        "4": {"class_type": "MiniMaxMusic3TextEncode", "inputs": dict(enc)},
        "5": {"class_type": "MiniMaxMusic3TextEncode", "inputs": dict(enc, caption="", lyrics="", seed=seed)},
        "6": {"class_type": "EmptyMiniMaxMusic3LatentAudio", "inputs": {"seconds": dur, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "seed": seed, "steps": 32, "cfg": cfg_scale,
            "sampler_name": "euler", "scheduler": "simple",
            "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "denoise": 1.0}},
        "8": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveAudio", "inputs": {"audio": ["8", 0], "filename_prefix": prefix}},
    }

def main():
    ap = argparse.ArgumentParser(description="本地 MiniMax Music3 生成歌曲")
    ap.add_argument("--caption", default=None, help="caption 文本（二选一）")
    ap.add_argument("--caption-file", default=None, help="caption 文件（推荐，工程 input/captions/）")
    ap.add_argument("--lyrics", default=None, help="歌词文件（推荐带 [Verse]/[Chorus] 标签）")
    ap.add_argument("--seed", type=int, default=831104)
    ap.add_argument("--duration", type=float, default=None, help="目标秒数，上限 360（config.music3.max_duration 优先）")
    ap.add_argument("--prefix", default="audio/YuE2/music3", help="输出文件名前缀")
    args = ap.parse_args()

    caption = args.caption
    if args.caption_file:
        caption = open(args.caption_file, encoding="utf-8").read().strip()
    if not caption:
        sys.exit("错误：需要 --caption 或 --caption-file")
    lyrics = open(args.lyrics, encoding="utf-8").read().strip() if args.lyrics else ""

    cfg = load_config()
    dur = args.duration if args.duration is not None else float((cfg.get("music3") or {}).get("max_duration", 180))
    prompt = build(cfg, caption, lyrics, args.seed, dur, args.prefix)
    pid = submit(prompt)
    print("prompt_id:", pid)
    outputs = wait(pid)
    report(outputs)
    audio = outputs.get("9", {}).get("audio") or []
    for a in audio:
        print("audio:", a.get("subfolder", ""), a.get("filename", ""))

if __name__ == "__main__":
    main()
