#!/usr/bin/env python3
"""yue-server (yue2.cpp / YuE2-Studio 引擎) 渲染助手
用法: python yue_render.py --lyrics <file> --style "<style>" --seed N --out-prefix <path>
产出: <prefix>.mp3 (48k stereo) + <prefix>.abc + <prefix>.json (元数据)
"""
import argparse, json, time, re, os, urllib.request, urllib.parse
HOST = "http://127.0.0.1:8091"
def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyrics", required=True)
    ap.add_argument("--style", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-prefix", required=True)
    a = ap.parse_args()
    lyrics = open(a.lyrics, encoding="utf-8").read()
    body = json.dumps({"id": "sg_" + os.path.basename(a.out_prefix).replace("\\", "_")[:40], "style": a.style, "lyrics": lyrics, "seed": a.seed}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request(HOST + "/synth", data=body, headers={"Content-Type": "application/json"})
    jid = json.loads(urllib.request.urlopen(req, timeout=60).read())["id"]
    print("job:", jid)
    # poll
    while True:
        time.sleep(4)
        try:
            u = HOST + "/job?id=" + urllib.parse.quote(jid) + "&result=1"
            with urllib.request.urlopen(u, timeout=30) as r:
                ct = r.headers.get("Content-Type", "")
                data = r.read()
            if not ct.startswith("multipart") and ct.startswith("application/json"):
                err = json.loads(data.decode("utf-8", "ignore"))
                raise SystemExit("job error: " + str(err)[:200])
            break
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
    print("done in %.0fs, type=%s" % (time.time() - t0, ct))
    # parse multipart
    mp = re.split(rb"\r?\n--yue2-batch-boundary", data)
    outjson, outmp3 = a.out_prefix + ".json", a.out_prefix + ".mp3"
    for p in mp:
        if not p.startswith(b"\r\n"): p = b"\r\n" + p
        head, _, b = p.partition(b"\r\n\r\n")
        h = head.decode("utf-8", "ignore")
        fn = re.search(r'filename="([^"]+)"', h)
        ctm = re.search(r"Content-Type: ([^\r\n]+)", h)
        ctv = ctm.group(1).strip() if ctm else ""
        body = (b or b"")
        if body.endswith(b"\r\n"): body = body[:-2]
        if "audio" in ctv:
            open(outmp3, "wb").write(body)
            print("mp3:", outmp3, len(body))
        elif "json" in ctv:
            open(outjson, "w", encoding="utf-8").write(body.decode("utf-8", "ignore"))
            meta = json.loads(body.decode("utf-8", "ignore"))
            abc = meta.get("abc", "")
            if abc:
                open(a.out_prefix + ".abc", "w", encoding="utf-8").write(abc)
                print("abc:", a.out_prefix + ".abc", len(abc))
    # 标准化：mp3 → 192kbps/48kHz（原 128k 备份），并留 32bit 母带（若服务端有 flac）
    try:
        import subprocess
        subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",r"H:\\Works\\SoundGenPrj\\scripts\\audio_norm.ps1","-Path",outmp3], check=False)
    except Exception as e:
        print("norm skip:", e)
    print("OK", outmp3)
if __name__ == "__main__":
    run()