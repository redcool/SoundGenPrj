# -*- coding: utf-8 -*-
"""歌词字频筛查 v1 —— 为"别字版"提供易错/生僻候选与同音建议。
用法：python lyric_char_report.py <歌词文件>...
- 输出：每字出现次数；易错字命中（含同音替换建议）；常见多音字标注。
- 全量字频判定需外部频率表：若存在 input/external/现代汉语字频.txt（每行"字 频率排名"），启用"低频标注"；
  否则仅做"易错/多音筛查"（不宣称全字频）。
- 标准版歌词永不因本工具改动；替换决策由 agent 人工复核。"""
import sys, os
from collections import Counter

SUGGEST = {
    "谗": "缠", "谄": "产", "郢": "影", "纫": "认", "芷": "纸", "颛": "专", "顼": "须",
    "虺": "悔", "雊": "垢", "罔": "网", "齲": "取", "醢": "海", "脯": "铺",
    "醨": "离", "餔": "补", "槁": "稿", "耒": "累", "臿": "插", "徭": "遥",
    "玦": "决", "黻": "福", "冕": "勉", "畎": "犬",
}
DUOYIN = "长行还为强重朝曲藏得乐数降便干只中空监传处舍率冠盛切称教坊觉间相处着的分别度量号了难兴倒好觉着调把报名弹单还分看省供载横转传圈切臊龟折拳薄漂相任禁闷便中间夹拓沓钻攒倒衬攒行称传圈和了"

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    # 外部全量字频表（可选）
    freq = {}
    fx = os.path.join("input", "external", "现代汉语字频.txt")
    if os.path.exists(fx):
        for line in open(fx, encoding="utf-8"):
            parts = line.split()
            if len(parts) >= 2:
                freq[parts[0]] = parts[1]
    has_freq = bool(freq)
    for path in sys.argv[1:]:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            print("读不到:", path, e); continue
        chars = [c for c in text if '\u4e00' <= c <= '\u9fff']
        cnt = Counter(chars)
        print("=== %s  汉字 %d / 去重 %d%s ===" % (
            path.split(chr(92))[-1], len(chars), len(cnt),
            "  [全量字频:启用]" if has_freq else "  [易错/多音筛查模式]"))
        print("--- 易错/生僻候选（有建议=可入别字版；标准版不动）---")
        hits = [(c, n) for c, n in cnt.items() if c in SUGGEST]
        if hits:
            for c, n in sorted(hits, key=lambda kv: -kv[1]):
                print("  %s ×%d  → 建议: %s" % (c, n, SUGGEST[c]))
        else:
            print("  （无命中）")
        print("--- 常用多音字（确认读音后再决定是否需替换）---")
        dy = [(c, n) for c, n in cnt.items() if c in DUOYIN and c not in SUGGEST]
        if dy:
            for c, n in sorted(dy, key=lambda kv: -kv[1]):
                print("  %s ×%d" % (c, n))
        else:
            print("  （无）")
        if has_freq:
            print("--- 低频字（出现于全量字频表 80000 名以后 或 未收录）---")
            low = [(c, n) for c, n in cnt.items() if freq.get(c, "999999") >= "80000"]
            for c, n in low: print("  %s ×%d" % (c, n))
        print()

if __name__ == "__main__":
    main()
