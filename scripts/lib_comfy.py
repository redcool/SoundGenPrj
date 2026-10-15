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

# ---- 以下为扩展工具: 音频分析 / 拼接 / 格式交付 (2026-09-21) ----
import subprocess as _sp
import math as _math

# Krumhansl-Schmuckler key profiles (归一化后使用)
_KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def analyze_audio(path, sample_seconds=30):
    """分析一段音频：时长/采样率/BPM/调性/频带分布/响度。纯 numpy 实现，无新依赖。"""
    try:
        import soundfile as sf
        import numpy as np
    except ImportError as e:
        raise RuntimeError("need soundfile+numpy: %s" % e)

    info = sf.info(path)
    w, sr = sf.read(path, dtype="float32")
    if w.ndim > 1:
        w = w.mean(axis=1)
    dur = len(w) / sr
    total_rms = float(np.sqrt(np.mean(w ** 2)))

    # ---- BPM: 降采样到 8kHz, 前 sample_seconds 秒, FFT 自相关 ----
    import scipy.signal
    seg = w[: int(sr * min(sample_seconds, dur))]
    ws = scipy.signal.resample_poly(seg, 8000, sr)[: int(24 * 8000)]
    ws = ws - ws.mean()
    n = len(ws)
    if n > 2:
        spec = np.fft.rfft(ws * np.hanning(n))
        autoc = np.fft.irfft(np.abs(spec) ** 2)
        autoc = autoc[:n] / (autoc[0] + 1e-9)
        lo, hi = int(0.4 * 8000), int(2.0 * 8000)
        smooth = np.convolve(autoc[lo:hi], np.ones(5) / 5, mode="same")
        lag = lo + int(np.argmax(smooth))
        bpm = 60.0 * 8000 / lag
        # 倍频矫正: BPM 落在 60-180 区间
        while bpm > 180:
            bpm /= 2
        while bpm < 60:
            bpm *= 2
    else:
        bpm = 0.0

    # ---- 调性: chroma 直方图 + KS 模板打分 ----
    key, root_pc = "unknown", -1
    if n > 2:
        freqs = np.fft.rfftfreq(n, 1 / 8000)
        mag = np.abs(spec)
        # 只看音级区(80-2000Hz) 转 chroma
        sel = (freqs >= 80) & (freqs <= 2000)
        fr, mg = freqs[sel], mag[sel]
        if len(fr) > 0:
            pc = np.round(12 * np.log2(fr / 440.0) + 69) % 12  # closest pitch class
            chroma = np.zeros(12)
            for i in range(len(fr)):
                chroma[int(pc[i])] += mg[i] ** 2
            chroma = chroma / (chroma.sum() + 1e-9)
            best, best_s = None, -1e9
            maj = np.array(_KS_MAJOR) / sum(_KS_MAJOR)
            minr = np.array(_KS_MINOR) / sum(_KS_MINOR)
            for r in range(12):
                for name, prof in (("maj", maj), ("min", minr)):
                    s = float(np.dot(chroma, np.roll(prof, r)))
                    if s > best_s:
                        best_s = s
                        best = "%s%s" % (_NOTE_NAMES[r], name)
                        root_pc = r
            key = best if best is not None else "unknown"

    # ---- 频带分布 ----
    raw = np.fft.rfft(seg * np.hanning(len(seg))[: len(seg)]) if len(seg) > 1 else np.array([0.0])
    fr_all = np.fft.rfftfreq(len(seg), 1 / sr) if len(seg) > 1 else np.array([0.0])
    e = np.abs(raw) ** 2
    band = {"lo": 0.0, "mid": 0.0, "hi": 0.0}
    ok = (fr_all > 0) & np.isfinite(e)
    tot = e[ok].sum() + 1e-9
    band["lo"] = float(e[(fr_all >= 60) & (fr_all < 250)].sum() / tot * 100)
    band["mid"] = float(e[(fr_all >= 250) & (fr_all < 2000)].sum() / tot * 100)
    band["hi"] = float(e[fr_all >= 2000].sum() / tot * 100)

    return {
        "path": path,
        "duration": round(dur, 2),
        "sample_rate": sr,
        "channels": info.channels,
        "bpm": round(bpm, 1),
        "key": key,
        "root_pitch_class": root_pc,
        "rms_db": round(20 * _math.log10(total_rms + 1e-9), 1) if total_rms > 0 else -99,
        "band_pct": band,
    }


def engine_audio_path(subfolder, filename):
    """把 ComfyUI 输出的 (subfolder, filename) 转成绝对路径。"""
    out_root = cfg("comfyui_output_dir") or os.path.join(os.path.dirname(os.path.dirname(BASE.replace("http://", ""))), "output")
    # BASE 不可靠时回退默认路径
    if not os.path.isdir(out_root):
        out_root = r"H:\AI\ComfyUI_windows_portable\ComfyUI\output"
    if subfolder:
        out_root = os.path.join(out_root, subfolder.replace("/", os.sep).replace("\\", os.sep))
    return os.path.join(out_root, filename)


def join_audio(files, out_path, crossfade=0.0, resample=44100):
    """拼接多段音频(同参数): crossfade=0 直接 concat; >0 用 acrossfade 两两叠接。返回输出路径。"""
    ffmpeg = cfg("ffmpeg") or "ffmpeg"
    if crossfade and crossfade > 0:
        # acrossfade 需要每段转为统一采样率,两两交叉
        tmp = []
        for i, f in enumerate(files):
            t = out_path + ".seg%d.wav" % i
            _sp.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", f,
                     "-ar", str(resample), "-ac", "2", t], check=True)
            tmp.append(t)
        cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
        for t in tmp:
            cmd += ["-i", t]
        flt = ""
        for i in range(len(tmp) - 1):
            if flt:
                flt += ","
            flt += "[%d:a][%d:a]acrossfade=d=%f:c1=tri:c2=tri[a%d]" % (i, i + 1, crossfade, i)
        cmd += ["-filter_complex", flt, "-map", "[a%d]" % (len(tmp) - 2),
                "-ar", str(resample), "-ac", "2", out_path]
        _sp.run(cmd, check=True)
        for t in tmp:
            try:
                os.remove(t)
            except OSError:
                pass
    else:
        lst = out_path + ".concat.txt"
        with open(lst, "w", encoding="utf-8") as f:
            for p in files:
                f.write("file '%s'\n" % p.replace("'", "'\\''"))
        _sp.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
                 "-safe", "0", "-i", lst, "-ar", str(resample), "-ac", "2", out_path], check=True)
        try:
            os.remove(lst)
        except OSError:
            pass
    return out_path


def to_delivery(src, out_path, fmt="mp3", bitrate=320):
    """转交付格式(默认 mp3 320k)，复用 ffmpeg（与 tools/convert_audio.ps1 同语义）。"""
    ffmpeg = cfg("ffmpeg") or "ffmpeg"
    codec = {"mp3": "libmp3lame", "ogg": "libvorbis", "opus": "libopus",
             "flac": "flac", "wav": "pcm_s16le"}.get(fmt.lower(), "")
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", src]
    if codec:
        cmd += ["-codec:a", codec]
    if fmt.lower() in ("mp3", "ogg", "opus"):
        cmd += ["-b:a", "%dk" % bitrate]
    cmd.append(out_path)
    _sp.run(cmd, check=True)
    return out_path


def extract_score_abc(outputs):
    """从 history outputs 的 Plan 节点(节点2) 提取 score_abc。

    节点2(FL_YuE2_Plan) 输出键为 "text"（history 中是顶层，node API 里是 ui.text），
    text[0] = "Score limit reached; ...\n<abc>" 或 "<abc>" 或 "Direct generation - no symbolic score."
    返回 abc 全文；无谱面时返回 ""。
    """
    try:
        n2 = outputs.get("2", {}) or {}
        # 兼容两种结构: {"text": [...]} 与 {"ui": {"text": [...]}}
        text = n2.get("text") or (n2.get("ui", {}) or {}).get("text", []) or []
        raw = text[0] if text else ""
    except Exception:
        return ""
    if not raw:
        return ""
    if raw.startswith("Score limit reached;"):
        idx = raw.find("\n")
        raw = raw[idx + 1:] if idx >= 0 else ""
    if "Direct generation" in raw or "no symbolic score" in raw:
        return ""
    return raw.strip()


def render_sheet_html(abc_path, out_html, title):
    """调用 tools/abc-render 渲染曲谱 HTML。返回 out_html 或抛错。"""
    import subprocess as _sp2
    node = "node"
    script = os.path.join(_ROOT, "tools", "abc-render", "render_sheet.mjs")
    if not os.path.exists(script):
        raise FileNotFoundError(script)
    _sp2.run([node, script, abc_path, out_html, title], check=True, cwd=os.path.dirname(script))
    return out_html


def save_song_package(args_ns, outputs, engine_flac, lyrics_path=None):
    """按 docs/歌曲生成规则.md 保存四件套:
    out_dir/<name>.mp3(转换), .lyrics.txt, .score.abc, .html；返回各路径 dict。
    args_ns 需含: out(前缀) / format / bitrate / style / seed / duration / planning。
    """
    import subprocess as _sp3
    out = args_ns.out
    out_dir = os.path.dirname(os.path.abspath(out))
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.basename(out)
    paths = {"mp3": "", "lyrics": "", "abc": "", "html": ""}

    # 1) 交付音频
    fmt = getattr(args_ns, "format", "mp3")
    bitrate = getattr(args_ns, "bitrate", 320)
    if fmt == "flac":
        final = out + ".flac"
        to_delivery(engine_flac, final, "flac")
    elif fmt == "wav":
        final = out + ".wav"
        to_delivery(engine_flac, final, "wav")
    else:
        final = out + "." + fmt
        to_delivery(engine_flac, final, fmt, bitrate)
    paths["mp3"] = final

    # 2) 歌词
    if lyrics_path and os.path.exists(lyrics_path):
        lp = out + ".lyrics.txt"
        import shutil
        shutil.copyfile(lyrics_path, lp)
        paths["lyrics"] = lp

    # 3) ABC + 4) HTML
    abc = extract_score_abc(outputs)
    if abc:
        abc_path = out + ".score.abc"
        with open(abc_path, "w", encoding="utf-8") as f:
            f.write(abc)
        paths["abc"] = abc_path
        try:
            paths["html"] = render_sheet_html(abc_path, out + ".html", name)
        except Exception as e:
            print("[warn] 曲谱 HTML 渲染失败:", e)
    return paths


