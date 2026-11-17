#!/usr/bin/env python3
"""
Генерує превʼю мода в корені проєкту:
  preview.png (1280x720) - обовʼязкове для публікації в Steam Workshop (Mindustry перевіряє його при публікації);
  icon.png    (256x256)  - значок у списку модів (якщо його немає, гра бере preview.png).
Спрайти беруться з gen_sprites.py, тож превʼю завжди збігається з реальними текстурами.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites as g

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def render(item, scale):
    base, top, parts = item
    comp = top.copy()
    for p in parts:
        img, (cx, cy), flip = p[0], p[1], p[2]
        rot = p[3] if len(p) > 3 else 0
        if rot:
            img = img.rotate(rot, expand=True, resample=Image.NEAREST)
        g.paste_c(comp, img, cx, cy, flip=flip and rot == 0)
    frame = base.copy()
    frame.alpha_composite(g.outline_img(comp))
    return frame.resize((frame.width * scale, frame.height * scale), Image.NEAREST)


def background(w, h, tint):
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        k = y / h
        c = (int(18 + 14 * k), int(20 + 14 * k), int(26 + 16 * k), 255)
        for x in range(w):
            px[x, y] = c
    # сітка малюється на окремому шарі й змішується (інакше напівпрозорі лінії замінюють піксель)
    grid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(grid)
    for x in range(0, w, 32):
        d.line([(x, 0), (x, h)], fill=(255, 255, 255, 12))
    for y in range(0, h, 32):
        d.line([(0, y), (w, y)], fill=(255, 255, 255, 12))
    img.alpha_composite(grid)
    return img


def glow(canvas, cx, cy, r, color):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (90,))
    layer = layer.filter(ImageFilter.GaussianBlur(r / 2.2))
    canvas.alpha_composite(layer)


def center_text(d, text, cx, y, font, fill):
    w = d.textlength(text, font=font)
    d.text((cx - w / 2 + 3, y + 3), text, font=font, fill=(0, 0, 0, 160))
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def main():
    items = [("NEXUS Volt", g.volt(), (79, 195, 255)),
             ("NEXUS Frostbite", g.frostbite(), (158, 230, 255)),
             ("NEXUS Titan", g.titan(), (255, 138, 46))]
    # ---------- preview.png 1280x720 ----------
    W, H = 1280, 720
    img = background(W, H, None)
    d = ImageDraw.Draw(img)
    scale = 4
    sizes = [it[1][0].width * scale for it in items]
    gap = 70
    x = (W - (sum(sizes) + gap * 2)) // 2
    cy = 430
    for (label, item, col), sz in zip(items, sizes):
        glow(img, x + sz // 2, cy, sz // 2 + 40, col)
        sprite = render(item, scale)
        img.alpha_composite(sprite, (x, cy - sprite.height // 2))
        center_text(d, label, x + sz // 2, cy + sprite.height // 2 + 22, ImageFont.truetype(FONT, 30), (235, 240, 250, 255))
        x += sz + gap
    center_text(d, "NEXUS: Advanced Arsenal", W // 2, 56, ImageFont.truetype(FONT, 76), (255, 255, 255, 255))
    center_text(d, "Original turrets for Mindustry", W // 2, 150, ImageFont.truetype(FONT, 32), (255, 190, 110, 255))
    img.convert("RGB").save(os.path.join(ROOT, "preview.png"))
    # ---------- icon.png 256x256 ----------
    ic = background(256, 256, None)
    glow(ic, 128, 128, 110, (255, 138, 46))
    spr = render(items[2][1], 2)
    ic.alpha_composite(spr, ((256 - spr.width) // 2, (256 - spr.height) // 2))
    ic.convert("RGB").save(os.path.join(ROOT, "icon.png"))
    print("OK: preview.png 1280x720, icon.png 256x256")


if __name__ == "__main__":
    main()
