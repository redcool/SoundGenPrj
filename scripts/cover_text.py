#!/usr/bin/env python3
"""cover_text.py — 封面标题精排（书法字体 + 金属渐变 + 描边）· 只写标题
用法:
  python cover_text.py --src base.png --out cover.png --title "恶名之歌·春秋" --font STXINGKA --size 160 --style gold
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = {
    "xingkai": r"C:\Windows\Fonts\STXINGKA.TTF",
    "hupo":    r"C:\Windows\Fonts\STHUPO.TTF",
    "lishu":   r"C:\Windows\Fonts\STLITI.TTF",
    "shuti":   r"C:\Windows\Fonts\FZSTK.TTF",
    "kai":     r"C:\Windows\Fonts\STKAITI.TTF",
    "hei":     r"C:\Windows\Fonts\msyhbd.ttc",
}

GRAD = {
    "gold":   [(255, 236, 160), (214, 168, 60), (255, 248, 205), (176, 122, 32)],
    "red":    [(255, 210, 170), (206, 62, 40), (240, 150, 90), (128, 24, 16)],
    "steel":  [(240, 244, 250), (150, 165, 180), (225, 232, 240), (95, 108, 124)],
}

def gradient_text(size, text, font, colors, stroke=(0,0,0), stroke_w=6):
    W, H = size
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    bbox = md.textbbox((0,0), text, font=font, stroke_width=stroke_w)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (W-tw)//2 - bbox[0]
    y = (H-th)//2 - bbox[1]
    md.text((x,y), text, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)

    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    n = len(colors)
    for i in range(H):
        t = i/(H-1)*(n-1)
        k = int(t); f = t-k
        c1 = colors[min(k, n-1)]; c2 = colors[min(k+1, n-1)]
        gd.line([(0,i),(W,i)], fill=tuple(int(c1[j]+(c2[j]-c1[j])*f) for j in range(3)))

    out = Image.new("RGBA", (W,H), (0,0,0,0))
    out.paste(grad, (0,0), mask)

    # 描边层（黑）
    ring = Image.new("RGBA", (W,H), (0,0,0,0))
    rd = ImageDraw.Draw(ring)
    rd.text((x,y), text, font=font, fill=stroke+(235,), stroke_width=stroke_w, stroke_fill=stroke+(235,))
    # 阴影
    sh = ring.filter(ImageFilter.GaussianBlur(8))
    return sh, ring, out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--font", default="xingkai")
    p.add_argument("--size", type=int, default=160)
    p.add_argument("--style", default="gold")
    p.add_argument("--stroke", type=int, default=7)
    p.add_argument("--pos", default="center", choices=["center","top","bottom"])
    p.add_argument("--y", type=float, default=-1, help="标题中心纵向位置 0-1，默认按 pos")
    a = p.parse_args()

    base = Image.open(a.src).convert("RGBA")
    W, H = base.size
    font = ImageFont.truetype(FONTS[a.font], a.size)
    colors = GRAD[a.style]

    layer = Image.new("RGBA", (W,H), (0,0,0,0))
    sh, ring, grad = gradient_text((W,H), a.title, font, colors, stroke_w=a.stroke)
    layer = Image.alpha_composite(layer, sh)
    layer = Image.alpha_composite(layer, ring)
    layer = Image.alpha_composite(layer, grad)

    # 纵向定位：把文字层整体上移/下移
    cy = a.y if a.y >= 0 else (0.18 if a.pos=="top" else (0.82 if a.pos=="bottom" else 0.5))
    # 计算文字实际中心
    md = ImageDraw.Draw(Image.new("L",(W,H),0))
    bbox = md.textbbox((0,0), a.title, font=font, stroke_width=a.stroke)
    ty = (bbox[1]+bbox[3])/2
    shift = int(cy*H - ty)
    layer = layer.transform((W,H), Image.AFFINE, (1,0,0, 0,1,-shift), resample=Image.BICUBIC)

    out = Image.alpha_composite(base, layer).convert("RGB")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    out.save(a.out, quality=95)
    w800 = os.path.join(os.path.dirname(a.out), os.path.basename(a.out).replace(".png","_800.png"))
    out.resize((800,800), Image.LANCZOS).save(w800, quality=95)
    print("saved:", a.out)

if __name__ == "__main__":
    main()
