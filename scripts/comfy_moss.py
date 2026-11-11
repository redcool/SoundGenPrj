#!/usr/bin/env python3
"""comfy_moss.py — 用本机 ComfyUI 的 MOSS-Image 生成 1K 图
用法:
  python comfy_moss.py --prompt "..." [--negative "..."] [--steps 28] [--cfg 4.5] [--seed 42]
                       [--width 1024] [--height 1024] [--out H:/path/name]
环境: ComfyUI 必须运行在 127.0.0.1:8188
模型: diffusion_models/moss_image_sft_int8_convrot.safetensors
      text_encoders/qwen3.5_9b_w4a8_gptq.safetensors (CLIP type: moss_image)
      vae/flux2-vae.safetensors (Flux2 latent)
"""
import argparse, json, os, time, uuid, urllib.request

HOST = "http://127.0.0.1:8188"
UNET = "moss_image_sft_int8_convrot.safetensors"
CLIP = "qwen3.5_9b_w4a8_gptq.safetensors"
VAE  = "flux2-vae.safetensors"

def api(path, payload=None):
    url = HOST + path
    if payload is None:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def build(a):
    return {
      "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
      "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "moss_image", "device": "default"}},
      "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
      "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": a.prompt}},
      "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": a.negative}},
      "6": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": a.width, "height": a.height, "batch_size": 1}},
      "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": a.seed, "steps": a.steps, "cfg": a.cfg,
             "sampler_name": a.sampler, "scheduler": a.scheduler, "positive": ["4", 0], "negative": ["5", 0],
             "latent_image": ["6", 0], "denoise": 1.0}},
      "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
      "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": a.prefix}},
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--negative", default="text, watermark, logo, blurry, low quality, distorted anatomy, extra limbs")
    p.add_argument("--steps", type=int, default=28)
    p.add_argument("--cfg", type=float, default=4.5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--width", type=int, default=1024)
    p.add_argument("--height", type=int, default=1024)
    p.add_argument("--sampler", default="euler")
    p.add_argument("--scheduler", default="simple")
    p.add_argument("--prefix", default="moss_test")
    p.add_argument("--out", default="")
    a = p.parse_args()

    wf = build(a)
    cid = str(uuid.uuid4())
    t0 = time.time()
    res = api("/prompt", {"prompt": wf, "client_id": cid})
    pid = res.get("prompt_id")
    print("prompt_id:", pid)
    while True:
        time.sleep(3)
        h = api("/history/" + pid)
        if pid in h:
            entry = h[pid]
            outs = entry.get("outputs", {})
            imgs = []
            for node in outs.values():
                imgs += node.get("images", [])
            print("done in %.0fs" % (time.time() - t0))
            for im in imgs:
                src = os.path.join(r"H:\AI\ComfyUI_windows_portable\ComfyUI\output", im.get("subfolder", ""), im["filename"])
                print("image:", src)
                if a.out:
                    import shutil
                    os.makedirs(os.path.dirname(a.out), exist_ok=True)
                    shutil.copyfile(src, a.out)
                    print("copied ->", a.out)
            break
        if time.time() - t0 > 1800:
            print("TIMEOUT")
            break

if __name__ == "__main__":
    main()
