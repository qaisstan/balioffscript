#!/usr/bin/env python3
"""Social share cards.

Builds a 1200x630 image per page so links shared in WhatsApp, Instagram DMs,
Facebook or LinkedIn show a proper preview instead of a cropped portrait.

Run:  python3 make_cards.py     (needs Pillow: python3 -m pip install --user pillow)

Kept out of build.py so the build itself stays dependency-free. Re-run it
after adding pages or changing titles; existing cards are left alone.
"""
from PIL import Image, ImageDraw, ImageFont
import os, re, textwrap

INK=(22,25,29); PAPER=(253,253,252); SEAL=(138,44,38); SLATE=(76,84,94); RULE=(232,230,225)
W, H = 1200, 630
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets", "og")

def font(px, bold=False, mono=False):
    paths = (["/System/Library/Fonts/Supplemental/Courier New Bold.ttf"] if mono else
             ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
              "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"] if bold else
             ["/System/Library/Fonts/Supplemental/Georgia.ttf"])
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, px)
            except Exception: pass
    return ImageFont.load_default()

portrait = Image.open(os.path.join(ROOT, "assets", "kai.jpg")).convert("RGB")

def card(title, out):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    pw = 420
    p = portrait.resize((pw, int(pw * portrait.height / portrait.width)), Image.LANCZOS)
    if p.height < H:
        p = p.resize((int(H * p.width / p.height), H), Image.LANCZOS)
    p = p.crop((0, 0, pw, H))
    im.paste(p, (W - pw, 0), Image.linear_gradient("L").rotate(90).resize((pw, H)))
    d.rectangle([0, 0, 10, H], fill=SEAL)
    d.text((64, 56), "BALI OFF SCRIPT", font=font(22, mono=True), fill=SLATE)
    # Shrink the type when a title needs more than three lines.
    size = 58
    lines = textwrap.wrap(title, width=26)
    if len(lines) > 3:
        size = 46; lines = textwrap.wrap(title, width=33)
    lines = lines[:4]
    f = font(size, bold=True)
    y = 150 if len(lines) < 4 else 128
    for ln in lines:
        d.text((64, y), ln, font=f, fill=INK); y += int(size * 1.24)
    d.line([(64, H - 96), (W - 460, H - 96)], fill=RULE, width=2)
    d.text((64, H - 74), "balioffscript.com", font=font(24, mono=True), fill=SLATE)
    im.save(out, quality=88, optimize=True)

def main():
    os.makedirs(OUT, exist_ok=True)
    card("Straight answers on buying, building and renting in Bali",
         os.path.join(OUT, "default.jpg"))
    made = 1
    for fn in sorted(os.listdir(os.path.join(ROOT, "content"))):
        if not fn.endswith(".md"): continue
        raw = open(os.path.join(ROOT, "content", fn), encoding="utf-8").read()
        fm = raw.split("---")[1]
        t = re.search(r"^title:\s*(.+)$", fm, re.M) or re.search(r"^question:\s*(.+)$", fm, re.M)
        card(t.group(1).strip(), os.path.join(OUT, fn[:-3] + ".jpg"))
        made += 1
    print(f"{made} cards written to assets/og/")

if __name__ == "__main__":
    main()
