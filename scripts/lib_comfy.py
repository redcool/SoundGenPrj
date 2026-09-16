"""ComfyUI / FL-YuE2 API 封装：构建节点链、提交、轮询、取结果。
服务地址默认 http://127.0.0.1:8188，可在工程根 config.json 的 comfyui_url 修改。
"""
import json, os, time, uuid, urllib.request

DEFAULT_URL = "http://127.0.0.1:8188"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 工程根（含 config.json）
_CONFIG_PATH = os.path.join(_ROOT, "config.json")

_DEFAULTS = {
    "comfyui_url": DEFAULT_URL,
    "ffmpeg": "ffmpeg",
    "python": "python",
    "yue2_node_path": "",
    "whisper_model_dir": "",
    "demucs_model_dir": "",
}


def load_config():
    cfg = dict(_DEFAULTS)
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except OSError:
        pass  # 无 config.json 时用默认值
    return cfg


_CFG = load_config()
BASE = _CFG["comfyui_url"] or DEFAULT_URL


def cfg(key, default=""):
    """取 config 项，空字符串/缺项时回退 default。"""
    v = _CFG.get(key)
    return v if v else default


def build_chain(style, lyrics, planning, seed, abc, max_duration, prefix,
                guidance=1.0, acoustic_steps=32, temperature=1.0, top_p=0.95,
                top_k=100, repetition_penalty=1.2):
    """标准 5 节点链：Loader → Plan → Render → Decode → SaveAudioAdvanced。"""
    plan_inputs = {"music_model": ["1", 0], "style": style, "lyrics": lyrics,
                   "planning": planning, "seed": seed}
    if abc:
        plan_inputs["score_abc"] = abc
    return {
        "1": {"class_type": "FL_YuE2_ModelLoader", "inputs": {"download_missing": False}},
        "2": {"class_type": "FL_YuE2_Plan", "inputs": plan_inputs},
        "3": {"class_type": "FL_YuE2_Render", "inputs": {
            "music_model": ["1", 0], "composition": ["2", 0], "max_duration": max_duration,
            "acoustic_steps": acoustic_steps, "temperature": temperature, "top_p": top_p,
            "top_k": top_k, "repetition_penalty": repetition_penalty, "guidance": guidance}},
        "4": {"class_type": "FL_YuE2_Decode", "inputs": {
            "audio_decoder": ["1", 1], "music_latents": ["3", 0], "tile_frames": 1024}},
        "5": {"class_type": "SaveAudioAdvanced", "inputs": {
            "audio": ["4", 0], "filename_prefix": prefix, "format": "flac"}},
    }


def submit(prompt, base=BASE):
    req = urllib.request.Request(base + "/prompt",
        data=json.dumps({"prompt": prompt, "client_id": str(uuid.uuid4())}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read().decode())
    pid = resp.get("prompt_id")
    if not pid:
        raise RuntimeError("submit failed: " + json.dumps(resp, ensure_ascii=False)[:1500])
    return pid


def wait(pid, timeout=7200, base=BASE, poll=20):
    """轮询 history 直到 success/error。返回 outputs dict。"""
    t0 = time.time(); last = ""
    while time.time() - t0 < timeout:
        time.sleep(poll)
        try:
            with urllib.request.urlopen(base + "/history/" + pid, timeout=30) as r:
                hist = json.loads(r.read().decode())
        except Exception:
            continue
        if pid not in hist:
            continue
        entry = hist[pid]; st = entry.get("status", {})
        cur = st.get("status_str") or ""
        if cur and cur != last:
            print("[%ds] %s" % (int(time.time() - t0), cur)); last = cur
        if cur == "success":
            return entry.get("outputs", {})
        if cur == "error":
            msgs = " | ".join(json.dumps(m, ensure_ascii=False)[:400] for m in st.get("messages", [])[-3:])
            raise RuntimeError("execution error: " + msgs)
    raise TimeoutError("timeout waiting for " + pid)


def report(outputs):
    """打印 Render 状态与音频路径。"""
    print("Render text:", outputs.get("3", {}).get("text"))
    audio = outputs.get("5", {}).get("audio") or []
    for a in audio:
        print("audio:", a.get("subfolder", ""), a.get("filename", ""))
