import sys, re, os
raw = open(r"H:\Works\SoundGenPrj\tmp\yue2cpp\pilot.raw", "wb")
import urllib.request
req = urllib.request.Request("http://127.0.0.1:8091/job?id=f49774b9918e82e2&result=1")
data = urllib.request.urlopen(req, timeout=60).read()
open(r"H:\Works\SoundGenPrj\tmp\yue2cpp\pilot.raw","wb").write(data)
B = b"--yue2-batch-boundary"
parts = data.split(B)
outdir = r"H:\Works\SoundGenPrj\tmp\yue2cpp\parts"
os.makedirs(outdir, exist_ok=True)
idx = 0
for p in parts:
    if p.startswith(b"\r\n"): p = p[2:]
    if p.startswith(b"--"): continue  # closing
    if not p.strip(): continue
    head, sep, body = p.partition(b"\r\n\r\n")
    hd = head.decode("utf-8", "ignore")
    fn = ""
    m = re.search(r'filename="([^"]+)"', hd)
    if m: fn = m.group(1)
    ct = re.search(r'Content-Type: ([^\r\n]+)', hd)
    ctv = ct.group(1).strip() if ct else "?"
    if not fn: fn = "part%d.%s" % (idx, "txt")
    fn2 = os.path.join(outdir, fn)
    # trim trailing boundary CRLF
    if body.endswith(b"\r\n"): body = body[:-2]
    open(fn2, "wb").write(body)
    print("PART %d: name=%s type=%s size=%d" % (idx, fn, ctv, len(body)))
    idx += 1
print("parts_dir=", outdir)
