#!/usr/bin/env python3
"""text_overlay.py — 给封面底图精确叠加中文标题（PIL）
用法:
  python text_overlay.py --src base.png --out cover.png --title "恶名之歌·春秋"      --subtitle "弑君者与佞幸" --tag "Vol.1 · 12 曲" [--title-size 110] [--pos top|bottom]
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"

def draw_text_with_shadow(draw, xy, text, font, fill, shadow=(0,0,0,190), offset=(3,3)):
    x, y = xy
    draw.text((x+offset[0], y+offset[1]), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--subtitle", default="")
    p.add_argument("--tag", default="")
    p.add_argument("--title-size", type=int, default=110)
    p.add_argument("--color", default="#E8D8B0")
    p.add_argument("--band", action="store_true", help="顶部加半透明压暗条，提高可读性")
    a = p.parse_args()

    img = Image.open(a.src).convert("RGBA")
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)

    if a.band:
        d.rectangle([0, 0, W, int(H*0.30)], fill=(0,0,0,120))

    tf = ImageFont.truetype(BOLD, a.title_size)
    sf = ImageFont.truetype(REG, int(a.title_size*0.42))
    tg = ImageFont.truetype(REG, int(a.title_size*0.30))

    # 标题居中
    bbox = d.textbbox((0,0), a.title, font=tf)
    tw = bbox[2]-bbox[0]; th = bbox[3]-bbox[1]
    ty = int(H*0.10)
    draw_text_with_shadow(d, ((W-tw)//2, ty), a.title, tf, a.color)

    y = ty + th + int(a.title_size*0.45)
    if a.subtitle:
        b2 = d.textbbox((0,0), a.subtitle, font=sf); w2 = b2[2]-b2[0]
        draw_text_with_shadow(d, ((W-w2)//2, y), a.subtitle, sf, "#D8C79A")
        y += int(a.title_size*0.75)
    if a.tag:
        b3 = d.textbbox((0,0), a.tag, font=tg); w3 = b3[2]-b3[0]
        draw_text_with_shadow(d, ((W-w3)//2, y), a.tag, tg, "#B9A87F")

    out = Image.alpha_composite(img, overlay).convert("RGB")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    out.save(a.out, quality=95)
    w800 = os.path.join(os.path.dirname(a.out), os.path.basename(a.out).replace(".png", "_800.png"))
    out.resize((800,800), Image.LANCZOS).save(w800, quality=95)
    print("saved:", a.out)
    print("saved:", w800)

if __name__ == "__main__":
    main()
