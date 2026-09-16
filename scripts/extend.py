"""谱面扩展：按段落复制把谱面拉长到目标小节数（默认 ~300 小节 ≈ 8 分钟），可选清零 Vocal。"""
import argparse, os, sys, re
from lib_comfy import build_chain, submit, wait, report, cfg
sys.path.insert(0, cfg("yue2_node_path") or r"H:\AI\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-FL-YuE2")
from yue2.abc_score import parse

NOTE_RE = re.compile(r"[A-Ga-g]([,'0-9]*?)([0-9]*)(-?)")

def zero_vocal_line(line):
    parts = line.split('"')
    for i in range(0, len(parts), 2):
        parts[i] = NOTE_RE.sub(lambda m: "z" + m.group(2), parts[i])
    return '"'.join(parts)

def split_sections(abc_text):
    header, sections, cur, cur_name = [], [], None, None
    for ln in abc_text.split("\n"):
        if ln.startswith("% "):
            if cur is not None:
                sections.append((cur_name, cur))
            cur_name = ln[2:].strip(); cur = []
        elif cur is None:
            header.append(ln)
        else:
            cur.append(ln)
    if cur is not None:
        sections.append((cur_name, cur))
    return header, sections

def bars_of(block_text):
    return len(parse(block_text).voices["Ins"].bars)

def build_extended(header, sections, target_bars, zero_vocals):
    by = {nm: blk for nm, blk in sections}
    order = [nm for nm, _ in sections]
    # 构造重复布局：原序 + 在第一个 interlude 之后重复 interlude，在最后重复 verse+chorus
    seq = []
    for nm in order:
        seq.append((nm, by[nm]))
    # 追加单位：取 verse 与 chorus（若存在）成组复制
    units = [("verse", by["verse"])] if "verse" in by else []
    if "chorus" in by:
        units.append(("chorus", by["chorus"]))
    base = sum(bars_of("\n".join(header + ["% " + nm] + blk)) for nm, blk in seq)
    k = 0
    while base + k * 40 < target_bars and k < 6:
        k += 1
    for _ in range(k):
        for nm, blk in units:
            seq.append((nm, blk))
    # 结尾 interlude（如有）收束
    if "interlude" in by:
        seq.append(("interlude", by["interlude"]))
    tot = sum(bars_of("\n".join(header + ["% " + nm] + blk)) for nm, blk in seq)
    out = list(header)
    vocal_mode = False
    for nm, blk in seq:
        out.append("% " + nm)
        for ln in blk:
            if ln.startswith("V: Vocal"):
                vocal_mode = True; out.append(ln)
            elif ln.startswith("V: Ins"):
                vocal_mode = False; out.append(ln)
            else:
                out.append(zero_vocal_line(ln) if (zero_vocals and vocal_mode) else ln)
    abc = "\n".join(out)
    parse(abc)  # 校验
    return abc, tot

def main():
    ap = argparse.ArgumentParser(description="YuE2 谱面扩展生成")
    ap.add_argument("--abc", required=True, help="源 ABC 谱面文件")
    ap.add_argument("--style", required=True)
    ap.add_argument("--lyrics", default=None)
    ap.add_argument("--seed", type=int, default=831201)
    ap.add_argument("--target-bars", type=int, default=300)
    ap.add_argument("--duration", type=int, default=520)
    ap.add_argument("--zero-vocals", action="store_true", help="器乐版清零 Vocal")
    ap.add_argument("--prefix", default="audio/YuE2/extended")
    args = ap.parse_args()

    abc_text = open(args.abc, encoding="utf-8").read()
    header, sections = split_sections(abc_text)
    abc, tot = build_extended(header, sections, args.target_bars, args.zero_vocals)
    print("extended bars:", tot, "~%.0fs" % (tot * 4 * 60 / 150))
    lyrics = ""
    if args.lyrics:
        lyrics = open(args.lyrics, encoding="utf-8").read().strip()
    prompt = build_chain(args.style, lyrics, "full", args.seed, abc, args.duration, args.prefix)
    pid = submit(prompt)
    print("prompt_id:", pid)
    outputs = wait(pid)
    report(outputs)

if __name__ == "__main__":
    main()
