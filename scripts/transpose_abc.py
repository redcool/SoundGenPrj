"""谱面转调 transpose_abc：把 YuE2 兼容 ABC 谱面的 K: 与全部音符半音整体平移。

用法:
  python scripts/transpose_abc.py --abc in.abc --semitones 2 --out out.abc

说明:
  - 支持升降记号(#/b)、八度(高音 , 低音 ')、时值数字
  - 和弦记号(引号内)不转（YuE2 和弦符号由模型解释，转旋律即可）
  - 平移到目标调: --to-key "A minor" (同时保持大/小调性质)
"""
import argparse, re

_NOTE_VAL = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_VAL_NOTE = {v: n for n, v in _NOTE_VAL.items()}
# 黑键(半音数) -> 用升号拼写的字母 (1:C# 3:D# 6:F# 8:G# 10:A#)
_BLACK = {1: ("C", "#"), 3: ("D", "#"), 6: ("F", "#"), 8: ("G", "#"), 10: ("A", "#")}


def _transpose_note(m, st):
    note_raw = m.group(1)      # 字母(可能小写=高八度)
    acc = m.group(2) or ""     # #/b
    octv = m.group(3) or ""    # , 或 '
    num = m.group(4) or ""     # 时值数字
    rest = m.group(5) or ""    # 剩余(- / = 等)
    upper = note_raw.upper()
    pc = _NOTE_VAL[upper] + (1 if acc == "#" else -1 if acc == "b" else 0)
    midi = pc + 60
    if note_raw.islower():
        midi += 12  # 小写字母本身即高八度
    if "'" in octv:
        midi += 12 * octv.count("'")
    if "," in octv:
        midi -= 12 * octv.count(",")
    new = midi + st
    # clamp 到两个八度内（很少需要超过）
    while new < 24:
        new += 12
    while new > 108:
        new -= 12
    pc = new % 12
    if pc in _BLACK:
        letter, acc_new = _BLACK[pc]
    else:
        letter = _VAL_NOTE[pc]
        acc_new = ""
    # 基准八度:C4=60 -> 对应 new//12==5;小写时表示高一八度
    octv_new = ""
    oct_dist = new // 12 - 5  # 相对 60(C4)
    if oct_dist > 0:
        octv_new = "'" * oct_dist
    elif oct_dist < 0:
        octv_new = "," * (-oct_dist)
    return "%s%s%s%s%s" % (letter, acc_new, octv_new, num, rest)


def transpose_abc(text, semitones):
    """对非注释、非头部(K:/M:/L: 行单独处理K:)的旋律行音符整体平移。"""
    out = []
    note_re = re.compile(r"([A-Ga-g])([#b]?)([,']*)([0-9/]*)([/=^_~]?)")
    for ln in text.split("\n"):
        s = ln.strip()
        # 只处理 K: 行与含音符的乐谱行；跳过指令行
        if s.startswith("%") or s.startswith("K:") or s.startswith("X:") or s.startswith("T:") or s.startswith("M:") or s.startswith("L:") or s.startswith("Q:") or s.startswith("V:"):
            if s.startswith("K:"):
                # 转调 K:（如 K:C -> K:D）
                k = s[2:].strip()
                m = re.match(r"([A-Ga-g])([#b]?)([mM]inor|maj|m)?", k)
                if m:
                    base = m.group(1).upper()
                    acc = m.group(2) or ""
                    mode = m.group(3) or ""
                    pc = _NOTE_VAL[base] + (1 if acc == "#" else -1 if acc == "b" else 0)
                    npc = (pc + semitones) % 12
                    if npc in _BLACK:
                        nb, nacc = _BLACK[npc]
                    else:
                        nb = _VAL_NOTE[npc]
                        nacc = ""
                    nmode = "m" if mode in ("m", "minor") else ""
                    out.append("K:%s%s%s" % (nb, nacc, nmode))
                else:
                    out.append(s)
            else:
                out.append(s)
        else:
            out.append(note_re.sub(lambda m, st=semitones: _transpose_note(m, st), ln))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="ABC 谱面整体转调")
    ap.add_argument("--abc", required=True, help="输入 ABC 文件")
    ap.add_argument("--semitones", type=int, default=0, help="平移半音数(正=升)")
    ap.add_argument("--to-key", default=None, help="目标调式(如 'D'/'A minor')，与 --semitones 二选一")
    ap.add_argument("--out", required=True, help="输出 ABC 文件")
    args = ap.parse_args()

    with open(args.abc, encoding="utf-8") as f:
        text = f.read()
    st = args.semitones
    if args.to_key:
        m = re.match(r"([A-Ga-g])([#b]?)(m|maj|minor)?$", args.to_key.strip())
        if not m:
            raise SystemExit("--to-key 格式应为如 'D' 或 'A minor'")
        base = m.group(1).upper(); acc = m.group(2) or ""; mode = m.group(3) or ""
        from_note = None
        km = re.search(r"K:(\S+)", text)
        if km:
            kk = km.group(1)
            mm = re.match(r"([A-Ga-g])([#b]?)", kk)
            if mm:
                from_note = _NOTE_VAL[mm.group(1).upper()] + (1 if mm.group(2) == "#" else -1 if mm.group(2) == "b" else 0)
        target = _NOTE_VAL[base] + (1 if acc == "#" else -1 if acc == "b" else 0)
        if from_note is None:
            raise SystemExit("无法解析原调 K:")
        st = (target - from_note) % 12
        if st > 6:
            st -= 12
    out = transpose_abc(text, st)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    print("transposed by %+d semitones -> %s" % (st, args.out))


if __name__ == "__main__":
    main()
