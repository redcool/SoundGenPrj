"""本地 ComfyUI MiniMax Music3 生成歌曲（ComfyUI 核心自带节点）。
链路：UNETLoader(DiT) + CLIPLoader(minimax) + VAELoader(DAV)
     -> MiniMaxMusic3TextEncode(caption/lyrics/seed/max_duration/cfg/topk)
     -> EmptyMiniMaxMusic3LatentAudio -> KSampler -> VAEDecodeAudio -> SaveAudio

工作流（注意：实测「不同时长同 seed 旋律全变」，抽卡时长必须=定稿时长）：
  1) probe：N 个 seed × <目标时长> 快速采样试旋律（时长小则快；如定稿 300s 则抽卡也用 300s）
  2) final：同 seed × 同目标时长生成（music3 上限 360s）
  ※ 若 ComfyUI 以 --disable-cuda-graphs 启动，60s 预筛→300s 定稿法可能恢复（待验证）

用法：
  python scripts/music3_generate.py --caption-file input/captions/x.txt --lyrics input/lyrics/x.txt --mode probe --prefix audio/YuE2/m3_probe
  python scripts/music3_generate.py --caption-file ... --lyrics ... --mode final --seed 831105 --duration 300 --prefix audio/YuE2/m3_final
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_comfy import load_config, submit, wait, report

MAX_SECONDS = 360.0
PROBE_SECONDS = 60.0
DEFAULT_SEEDS = [831104, 831105, 831106, 831107]

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

def show(outputs):
    for a in (outputs.get("9", {}).get("audio") or []):
        print("  audio:", (a.get("subfolder") + "/" if a.get("subfolder") else "") + a.get("filename", ""))

def main():
    ap = argparse.ArgumentParser(description="本地 MiniMax Music3 生成/抽卡")
    ap.add_argument("--caption", default=None, help="caption 文本（二选一）")
    ap.add_argument("--caption-file", default=None, help="caption 文件（推荐，工程 input/captions/）")
    ap.add_argument("--lyrics", default=None, help="歌词文件（推荐带 [Verse]/[Chorus] 标签）")
    ap.add_argument("--mode", choices=["probe", "final"], default="final", help="probe=60s×多seed抽卡；final=指定seed完整版")
    ap.add_argument("--seeds", default="", help="probe 模式 seed 列表，逗号分隔（默认 831104,831105,831106,831107）")
    ap.add_argument("--seed", type=int, default=None, help="final 模式使用的 seed")
    ap.add_argument("--duration", type=float, default=None, help="final 模式时长秒（默认 config，上限 360）")
    ap.add_argument("--prefix", default="audio/YuE2/music3", help="输出文件名前缀（probe 自动追加 _seedN）")
    args = ap.parse_args()

    caption = args.caption
    if args.caption_file:
        caption = open(args.caption_file, encoding="utf-8").read().strip()
    if not caption:
        sys.exit("错误：需要 --caption 或 --caption-file")
    lyrics = open(args.lyrics, encoding="utf-8").read().strip() if args.lyrics else ""
    cfg = load_config()

    if args.mode == "probe":
        seeds = [int(x) for x in args.seeds.split(",") if x.strip()] or DEFAULT_SEEDS
        print("=== probe：%d 个 seed × %.0fs ===" % (len(seeds), PROBE_SECONDS), flush=True)
        pids = []
        for s in seeds:  # 全部提交，ComfyUI 按队列顺次执行
            p = build(cfg, caption, lyrics, s, PROBE_SECONDS, args.prefix + ("_seed%d" % s))
            pid = submit(p)
            print("submitted seed", s, "->", pid, flush=True)
            pids.append((s, pid))
        t0 = time.time()
        for s, pid in pids:
            print("--- waiting seed", s, flush=True)
            outs = wait(pid)
            print("seed %d 完成 (%.0fs)：" % (s, time.time() - t0), flush=True)
            show(outs); print(flush=True)
        print("=== 请试听这 %d 个 60s 版，记住喜欢的 seed，再 --mode final --seed N --duration 300 ===" % len(seeds))
        sys.exit(0)

    # final
    seed = args.seed if args.seed is not None else int((cfg.get("music3") or {}).get("seed", 831104))
    dur = args.duration if args.duration is not None else float((cfg.get("music3") or {}).get("max_duration", 300))
    print("=== final：seed %d × %.0fs ===" % (seed, dur), flush=True)
    p = build(cfg, caption, lyrics, seed, dur, args.prefix)
    pid = submit(p)
    print("prompt_id:", pid, flush=True)
    outs = wait(pid)
    show(outs)
    sys.exit(0)

if __name__ == "__main__":
    main()
