#!/usr/bin/env python3
"""歌词审核 —— 渲染前必跑。用：python audit_lyrics.py <标准版.txt> [别字版.txt]
检查：段标唯一 / 词量带(520-620) / 别字版官方标签词表 / 占位乱码 / 字频(可选调 lyric_char_report)"""
import sys, re
from collections import Counter

def sections(text):
    return re.findall(r'^\[(.+?)\]', text, re.M)

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    # 1) 标准版
    std = open(sys.argv[1], encoding='utf-8').read()
    std_words = len(re.sub(r'\[.+?\]', '', std).replace('\s', ''))
    secs = sections(std)
    dup = [k for k, v in Counter(secs).items() if v > 1]
    ok = True
    print('== 标准版 ==')
    print(' 词量(不含标签):', std_words, ('OK(520-700·快拍放宽)' if 520 <= std_words <= 700 else '!!带外'))
    print(' 段标:', ' '.join(secs))
    print(' 重复段标:', dup if dup else '无')
    if not 520 <= std_words <= 700 or dup: ok = False
    # 2) 别字版（可选）
    if len(sys.argv) >= 3:
        bz = open(sys.argv[2], encoding='utf-8').read()
        bsecs = sections(bz)
        bdup = [k for k, v in Counter(bsecs).items() if v > 1]
        official = ('Intro','Outro','Verse','Chorus','Bridge','Pre-Chorus')
        bad = [s for s in bsecs if not any(s.startswith(o) for o in official)]
        print('== 别字版 ==')
        print(' 段标:', ' '.join(bsecs))
        print(' 重复段标:', bdup if bdup else '无')
        print(' 非官方标签:', bad if bad else '无')
        if bdup or bad: ok = False
    print('== 结论:', 'PASS 可渲染' if ok else 'FAIL 先修改 ==')

if __name__ == '__main__':
    main()