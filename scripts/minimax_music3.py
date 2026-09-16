"""MiniMax Music 3 歌曲生成（云端 API）。
Key 从工程根 config.json 的 minimax.api_key 读取，可 --api-key 覆盖。
用法示例：
  python scripts/minimax_music3.py --caption "melodic death metal, electric pipa..." --lyrics lyrics.txt --out songs/m3_demo
  python scripts/minimax_music3.py --caption-file caption.txt --duration 8
"""
import argparse, json, os, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_comfy import load_config


def api_call(cfg, path, payload, headers=None):
    base = (cfg.get("minimax", {}) or {}).get("base_url") or "https://api.minimaxi.com/v1"
    key = (cfg.get("minimax", {}) or {}).get("api_key") or ""
    h = {"Content-Type": "application/json", "Authorization": "Bearer " + key}
    if headers:
        h.update(headers)
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode(), headers=h)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser(description="MiniMax Music 3 生成歌曲")
    ap.add_argument("--caption", default=None, help="音乐描述/结构化 caption 文本")
    ap.add_argument("--caption-file", default=None, help="caption 文本文件")
    ap.add_argument("--lyrics", default=None, help="歌词文件（可选，带 [Verse]/[Chorus] 标签更佳）")
    ap.add_argument("--title", default="", help="歌曲标题")
    ap.add_argument("--model", default=None, help="模型，默认读 config.minimax.model")
    ap.add_argument("--api-key", default=None, help="API Key，覆盖 config")
    ap.add_argument("--out", default="output/audio/music3", help="输出文件（不带扩展名）")
    ap.add_argument("--duration", default=None, help="时长（秒/分钟，如 480 或 8，若 API 支持）")
    args = ap.parse_args()

    cfg = load_config()
    mm = cfg.get("minimax", {}) or {}
    key = args.api_key or mm.get("api_key") or ""
    if not key:
        sys.exit("错误：未配置 MiniMax API Key。请在 config.json 的 minimax.api_key 填写（platform.minimaxi.com 控制台创建）。")
    if args.api_key:
        mm = dict(mm); mm["api_key"] = key
        cfg["minimax"] = mm

    caption = args.caption
    if args.caption_file:
        caption = open(args.caption_file, encoding="utf-8").read().strip()
    if not caption:
        sys.exit("错误：需要 --caption 或 --caption-file")
    lyrics = ""
    if args.lyrics:
        lyrics = open(args.lyrics, encoding="utf-8").read().strip()

    model = args.model or mm.get("model") or "music-01-latest"
    payload = {"model": model, "text": caption, "song_title": args.title}
    if lyrics:
        payload["lyrics"] = lyrics
    if args.duration:
        payload["duration"] = args.duration

    print("提交 Music3 任务: model =", model)
    try:
        resp = api_call(cfg, "/music", payload)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:1500]
        except Exception:
            pass
        sys.exit("提交失败 HTTP %s: %s" % (e.code, body))
    print("响应:", json.dumps(resp, ensure_ascii=False)[:600])

    file_id = resp.get("file_id") or resp.get("data", {}).get("file_id")
    if not file_id:
        sys.exit("未取到 file_id，请按响应调整参数（可能模型名/字段契约不同）: " + json.dumps(resp, ensure_ascii=False)[:800])

    # 轮询下载：尝试 /files/{id}/content 与 /files/{id}/download 两种路径
    out = args.out if args.out.endswith((".mp3", ".wav", ".flac")) else args.out + ".mp3"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    t0 = time.time()
    while time.time() - t0 < 900:
        time.sleep(8)
        for path in ("/files/%s/content" % file_id, "/files/%s/download" % file_id):
            try:
                base = mm.get("base_url") or "https://api.minimaxi.com/v1"
                req = urllib.request.Request(base + path, headers={"Authorization": "Bearer " + key})
                with urllib.request.urlopen(req, timeout=120) as r:
                    ct = r.headers.get("Content-Type", "")
                    data = r.read()
                if ct.startswith("audio") or data[:4] == b"ID3" or data[:4] == b"\xff\xfb" or data[:4] == b"RIFF":
                    with open(out, "wb") as f:
                        f.write(data)
                    print("下载完成 ->", out, "(%.1f MB)" % (len(data) / 1048576))
                    return
                # 非音频 → 可能 JSON（还在生成或有 url 字段）
                j = json.loads(data.decode())
                url = j.get("url") or j.get("download_url") or (j.get("data") or {}).get("url")
                if url:
                    with urllib.request.urlopen(url, timeout=300) as r2:
                        with open(out, "wb") as f:
                            f.write(r2.read())
                    print("下载完成(url) ->", out)
                    return
                if j.get("status") in ("failed", "error"):
                    print("任务失败:", json.dumps(j, ensure_ascii=False)[:400]); return
            except urllib.error.HTTPError as e:
                if e.code in (404, 400):
                    continue
            except Exception as e:
                pass
        print("[%ds] 等待生成..." % int(time.time() - t0), flush=True)
    print("超时：90 分钟未取到结果，file_id = %s（可稍后手动下载）" % file_id)


if __name__ == "__main__":
    main()
