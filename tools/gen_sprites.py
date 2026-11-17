#!/usr/bin/env python3
"""
Генератор піксель-арт спрайтів NEXUS: Advanced Arsenal (Етап 2: Volt, Frostbite, Titan).

Правила Mindustry, яких тут дотримано:
  * 1 клітинка = 32 px, тож розмір 2 -> 64x64, розмір 3 -> 96x96.
  * Верхня частина турелі та частини (RegionPart) повернуті "вгору" (ствол дивиться на північ).
  * Центр обертання = центр полотна. Зсуви частин у hjson (x, y) = пікселі / 4.
  * Контури верхніх регіонів гра малює сама, тому вони тут не обводяться.
  * -heat спрайти білі: гра фарбує їх у heatColor турелі (адитивне змішування).
Запуск: python3 tools/gen_sprites.py  (результат у sprites/blocks/turrets/)
"""
import math, os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites", "blocks", "turrets")
os.makedirs(OUT, exist_ok=True)


def C(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


class Pal:
    def __init__(self, dk, lo, mid, hi, sp):
        self.dk, self.lo, self.mid, self.hi, self.sp = map(C, (dk, lo, mid, hi, sp))


METAL = Pal("#1f1f27", "#383843", "#52525e", "#7b7b89", "#a9a9b8")
DARK = Pal("#15151b", "#24242d", "#34343f", "#4d4d5a", "#6a6a79")
ORG = Pal("#7a3412", "#c4541c", "#ff8a2e", "#ffc56b", "#fff0c0")
BLU = Pal("#0d3f66", "#1d7fbf", "#4fc3ff", "#a8ecff", "#eaffff")
ICE = Pal("#3a78a6", "#7cc0e8", "#bfe6fa", "#e8f8ff", "#ffffff")
COP = Pal("#5b3418", "#945a2e", "#c98a52", "#f0b27a", "#ffe2bd")
WHITE = C("#ffffff")


def new(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def reg_poly(cx, cy, r, n, rot=0.0):
    return [(cx + r * math.cos(math.radians(rot + 360 / n * i)),
             cy + r * math.sin(math.radians(rot + 360 / n * i))) for i in range(n)]


def shrink(pts, k):
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts]


def poly(d, pts, pal, inset=0.86):
    """Багатокутник із фаскою: темний контур, світла верхня-ліва і темна нижня-права грані."""
    d.polygon(pts, fill=pal.mid, outline=pal.dk)
    inner = shrink(pts, inset)
    n = len(inner)
    for i in range(n):
        a, b = inner[i], inner[(i + 1) % n]
        nx, ny = (b[1] - a[1]), -(b[0] - a[0])  # нормаль назовні (для обходу за годинниковою)
        light = -(nx) - (ny)
        d.line([a, b], fill=pal.hi if light > 0 else pal.lo, width=1)


def brect(d, box, pal):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=pal.mid, outline=pal.dk)
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=pal.hi)
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 1)], fill=pal.hi)
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1)], fill=pal.lo)
    d.line([(x1 - 1, y0 + 1), (x1 - 1, y1 - 1)], fill=pal.lo)


def disc(d, cx, cy, r, pal):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=pal.dk)
    d.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], fill=pal.lo)
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2.5, cy + r - 2.5], fill=pal.mid)
    d.ellipse([cx - r + 3, cy - r + 3, cx + r - 5, cy + r - 5], fill=pal.hi)


def glow(d, cx, cy, r, pal):
    """Світна сфера: концентричні кільця від темного до білого."""
    for rr, col in ((r, pal.dk), (r - 1, pal.lo), (r * 0.72, pal.mid), (r * 0.48, pal.hi), (r * 0.22, pal.sp)):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)


def bolt(d, x, y, pal=METAL):
    d.rectangle([x, y, x + 2, y + 2], fill=pal.lo)
    d.point((x, y), fill=pal.sp)


def make_base(size, trim):
    """Квадратна база з фасками, болтами й кольоровим кантом."""
    img, d = new(size, size)
    c = 5 if size <= 64 else 7
    pts = [(1 + c, 1), (size - 2 - c, 1), (size - 2, 1 + c), (size - 2, size - 2 - c),
           (size - 2 - c, size - 2), (1 + c, size - 2), (1, size - 2 - c), (1, 1 + c)]
    poly(d, pts, DARK, 0.93)
    m = 6 if size <= 64 else 8
    inner = [(m, m), (size - m - 1, m), (size - m - 1, size - m - 1), (m, size - m - 1)]
    d.polygon(inner, fill=DARK.lo, outline=DARK.dk)
    # кольоровий кант по периметру внутрішньої виїмки
    d.rectangle([m + 1, m + 1, size - m - 2, size - m - 2], outline=trim.lo)
    for x, y in ((3, 3), (size - 6, 3), (3, size - 6), (size - 6, size - 6)):
        bolt(d, x, y, METAL)
    return img


def outline_img(img, col=C("#4a4863")):
    """Лише для превʼю: імітація контуру, який гра малює навколо турелі."""
    w, h = img.size
    big = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    out = big.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0:
                        out[x, y] = col
                        break
    big.alpha_composite(img)
    return big


def paste_c(dst, part, cx, cy, flip=False):
    if flip:
        part = part.transpose(Image.FLIP_LEFT_RIGHT)
    dst.alpha_composite(part, (int(round(cx - part.width / 2)), int(round(cy - part.height / 2))))


def white_of(img):
    """Біла копія форми зображення (для -heat)."""
    r = Image.new("RGBA", img.size, (0, 0, 0, 0))
    r.paste(WHITE, mask=img.split()[3])
    return r


def save(img, name):
    img.save(os.path.join(OUT, name + ".png"))


# ======================================================================
# VOLT 64x64 -- реактор + котушки + дві сталеві "рогатки" випромінювача
# ======================================================================
def volt():
    S = 64
    top, d = new(S, S)
    heat, h = new(S, S)
    # корпус: восьмикутник
    poly(d, reg_poly(32, 38, 22, 8, 22.5), METAL)
    # передній зубець-перемичка
    brect(d, (20, 12, 43, 18), DARK)
    # дві "рогатки" випромінювача
    for x0 in (21, 36):
        brect(d, (x0, 3, x0 + 7, 28), METAL)
        d.rectangle([x0 + 2, 3, x0 + 5, 5], fill=BLU.mid)       # світний кінчик
        d.point((x0 + 3, 3), fill=BLU.sp)
        h.rectangle([x0 + 2, 3, x0 + 5, 7], fill=WHITE)
    # енергетична дуга між рогатками
    d.rectangle([30, 6, 33, 27], fill=BLU.dk)
    d.line([(31, 6), (31, 27)], fill=BLU.mid)
    d.line([(32, 6), (32, 27)], fill=BLU.hi)
    h.line([(31, 8), (31, 27)], fill=WHITE)
    h.line([(32, 8), (32, 27)], fill=WHITE)
    # реактор
    d.ellipse([21, 27, 43, 49], fill=METAL.dk)
    d.ellipse([22, 28, 42, 48], fill=METAL.mid)
    d.ellipse([24, 30, 40, 46], fill=BLU.dk)
    glow(d, 32, 38, 7, BLU)
    for i in range(8):  # насічки на кільці
        a = math.radians(45 * i + 22)
        x, y = 32 + 10 * math.cos(a), 38 + 10 * math.sin(a)
        d.rectangle([x - 1, y - 1, x, y], fill=METAL.hi)
    h.ellipse([24, 30, 40, 46], outline=WHITE)
    # задні радіатори
    for x0 in (20, 36):
        brect(d, (x0, 54, x0 + 8, 59), DARK)
        for yy in (56, 58):
            d.line([(x0 + 1, yy), (x0 + 6, yy)], fill=DARK.dk)
    # заклепки
    for x, y in ((17, 26), (45, 26), (17, 50), (45, 50)):
        d.point((x, y), fill=METAL.sp)
        d.point((x + 1, y + 1), fill=METAL.dk)

    # котушка 12x28
    coil, c = new(12, 28)
    brect(c, (1, 0, 10, 27), METAL)
    for y in range(3, 25, 3):
        c.line([(2, y), (9, y)], fill=COP.mid)
        c.line([(2, y + 1), (9, y + 1)], fill=COP.hi if (y // 3) % 2 else COP.lo)
    c.rectangle([4, 1, 7, 2], fill=BLU.mid)
    c.rectangle([4, 25, 7, 26], fill=BLU.mid)
    coil_heat, ch = new(12, 28)
    ch.rectangle([4, 1, 7, 2], fill=WHITE)
    ch.rectangle([4, 25, 7, 26], fill=WHITE)

    prev = make_base(S, BLU)
    prev_top = top.copy()
    for sx in (-1, 1):
        paste_c(prev_top, coil, 32 + sx * 14, 32)

    save(make_base(S, BLU), "volt-base")
    save(top, "volt")
    save(heat, "volt-heat")
    save(prev_top, "volt-preview")
    save(coil, "volt-coil")
    save(coil_heat, "volt-coil-heat")
    return prev, top, [(coil, (32 - 14, 32), False), (coil, (32 + 14, 32), True)]


# ======================================================================
# FROSTBITE 64x64 -- шестикутна крижана оболонка, кріоядро, кристалічний ствол
# ======================================================================
def frostbite():
    S = 64
    top, d = new(S, S)
    heat, h = new(S, S)
    poly(d, reg_poly(32, 40, 22, 6, 30), ICE)
    # темні опорні балки
    for ang in (90, 210, 330):
        a = math.radians(ang)
        d.line([(32, 41), (32 + 20 * math.cos(a), 41 + 20 * math.sin(a))], fill=METAL.mid, width=3)
        d.line([(32, 41), (32 + 20 * math.cos(a), 41 + 20 * math.sin(a))], fill=METAL.hi, width=1)
    # кріоядро
    d.ellipse([22, 31, 42, 51], fill=METAL.dk)
    d.ellipse([23, 32, 41, 50], fill=ICE.lo)
    glow(d, 32, 41, 7.5, BLU)
    h.ellipse([24, 33, 40, 49], outline=WHITE)
    # кристалічні "зубці" спереду
    for x in (18, 26, 38, 46):
        d.polygon([(x, 20), (x + 3, 14), (x + 6, 20)], fill=ICE.hi, outline=ICE.lo)
    # задній радіатор
    brect(d, (24, 58, 40, 62), DARK)

    # кристал-ствол 16x40
    cr, c = new(16, 40)
    pts = [(8, 0), (14, 8), (14, 30), (8, 39), (2, 30), (2, 8)]
    c.polygon(pts, fill=ICE.mid, outline=ICE.dk)
    c.polygon([(8, 1), (13, 8), (13, 30), (8, 38)], fill=ICE.lo)           # права темна грань
    c.polygon([(8, 1), (3, 8), (3, 30), (8, 38)], fill=ICE.hi)             # ліва світла грань
    c.line([(8, 1), (8, 38)], fill=ICE.sp)                                  # гребінь
    c.line([(3, 12), (13, 12)], fill=ICE.mid)
    c.line([(3, 24), (13, 24)], fill=ICE.mid)
    c.rectangle([6, 1, 9, 3], fill=BLU.hi)                                  # кінчик
    cr_heat, ch = new(16, 40)
    ch.polygon([(8, 1), (12, 8), (12, 20), (8, 20), (4, 20), (4, 8)], fill=WHITE)

    # бічний кристал 10x22
    sh, s = new(10, 22)
    s.polygon([(5, 0), (9, 6), (8, 20), (5, 21), (2, 20), (1, 6)], fill=ICE.mid, outline=ICE.dk)
    s.polygon([(5, 1), (8, 7), (7, 19), (5, 20)], fill=ICE.lo)
    s.polygon([(5, 1), (2, 7), (3, 19), (5, 20)], fill=ICE.hi)
    s.line([(5, 1), (5, 20)], fill=ICE.sp)

    prev = make_base(S, BLU)
    prev_top = top.copy()
    for sx, rot in ((-1, 10), (1, -10)):
        r = sh.rotate(rot, expand=True, resample=Image.NEAREST)
        paste_c(prev_top, r, 32 + sx * 22, 30, flip=(sx < 0) and False)
    paste_c(prev_top, cr, 32, 22)

    save(make_base(S, BLU), "frostbite-base")
    save(top, "frostbite")
    save(heat, "frostbite-heat")
    save(prev_top, "frostbite-preview")
    save(cr, "frostbite-crystal")
    save(cr_heat, "frostbite-crystal-heat")
    save(sh, "frostbite-shard")
    return prev, top, [(sh, (32 - 22, 30), True, 10), (sh, (32 + 22, 30), False, -10), (cr, (32, 22), False, 0)]


# ======================================================================
# TITAN 96x96 -- масивний корпус, подовжений ствол, бронеплити, помаранчеві вставки
# ======================================================================
def titan():
    S = 96
    top, d = new(S, S)
    heat, h = new(S, S)
    body = [(30, 26), (66, 26), (80, 40), (82, 66), (72, 86), (24, 86), (14, 66), (16, 40)]
    poly(d, body, METAL, 0.9)
    poly(d, shrink(body, 0.72), DARK, 0.9)
    # помаранчеві вставки по боках
    for x0 in (23, 70):
        d.rectangle([x0, 42, x0 + 3, 76], fill=ORG.dk)
        d.rectangle([x0 + 1, 43, x0 + 2, 75], fill=ORG.mid)
        d.line([(x0 + 1, 43), (x0 + 1, 75)], fill=ORG.hi)
        h.rectangle([x0 + 1, 43, x0 + 2, 75], fill=WHITE)
    # люк по центру
    disc(d, 48, 58, 10, METAL)
    d.ellipse([42, 52, 54, 64], fill=DARK.dk)
    d.ellipse([44, 54, 52, 62], outline=ORG.mid)
    h.ellipse([44, 54, 52, 62], outline=WHITE)
    # посадочне кільце ствола
    d.ellipse([33, 18, 63, 48], fill=METAL.dk)
    d.ellipse([34, 19, 62, 47], fill=METAL.lo)
    d.ellipse([34, 19, 62, 47], outline=ORG.lo)
    h.ellipse([34, 19, 62, 47], outline=WHITE)
    # казенна частина зі щілинами охолодження і виїмкою під ромб
    brect(d, (32, 70, 64, 90), DARK)
    d.rectangle([40, 73, 56, 86], fill=ORG.dk)                              # виїмка під світний ромб
    for yy in (74, 78, 82, 86):
        for x0 in (34, 58):
            d.line([(x0, yy), (x0 + 4, yy)], fill=ORG.mid)
            h.line([(x0, yy), (x0 + 4, yy)], fill=WHITE)
    # заклепки
    for x, y in ((22, 34), (72, 34), (20, 70), (74, 70), (30, 82), (64, 82)):
        bolt(d, x, y)

    # ствол 28x68
    br, b = new(28, 68)
    brect(b, (3, 0, 24, 11), METAL)                                         # дульне гальмо
    for x0 in (7, 19):
        b.rectangle([x0, 3, x0 + 1, 8], fill=DARK.dk)
    brect(b, (7, 11, 20, 50), METAL)                                        # вал
    for y in (17, 29, 41):
        brect(b, (5, y, 22, y + 3), METAL)                                  # кільця жорсткості
    b.line([(13, 13), (13, 48)], fill=ORG.mid)                              # світна жилка
    b.line([(14, 13), (14, 48)], fill=ORG.dk)
    brect(b, (3, 50, 24, 67), DARK)                                         # казенний кожух
    b.rectangle([5, 56, 22, 58], fill=ORG.mid)
    b.line([(5, 56), (22, 56)], fill=ORG.hi)
    br_heat, bh = new(28, 68)
    bh.line([(13, 13), (14, 48)], fill=WHITE)
    bh.line([(14, 13), (14, 48)], fill=WHITE)
    bh.rectangle([5, 56, 22, 58], fill=WHITE)
    bh.rectangle([8, 3, 9, 8], fill=WHITE)
    bh.rectangle([18, 3, 19, 8], fill=WHITE)

    # бронеплита 18x40
    pl, p = new(18, 40)
    poly(p, [(3, 0), (15, 4), (17, 36), (9, 39), (1, 36), (1, 4)], METAL, 0.88)
    p.rectangle([8, 9, 10, 31], fill=ORG.mid)
    p.line([(8, 9), (8, 31)], fill=ORG.hi)
    pl_heat, ph = new(18, 40)
    ph.rectangle([8, 9, 10, 31], fill=WHITE)

    prev = make_base(S, ORG)
    prev_top = top.copy()
    for sx in (-1, 1):
        paste_c(prev_top, pl, 48 + sx * 36, 46, flip=(sx < 0))
    paste_c(prev_top, br, 48, 34)

    save(make_base(S, ORG), "nx-titan-base")
    save(top, "nx-titan")
    save(heat, "nx-titan-heat")
    save(prev_top, "nx-titan-preview")
    save(br, "nx-titan-barrel")
    save(br_heat, "nx-titan-barrel-heat")
    save(pl, "nx-titan-plate")
    save(pl_heat, "nx-titan-plate-heat")
    return prev, top, [(pl, (48 - 36, 46), True, 0), (pl, (48 + 36, 46), False, 0), (br, (48, 34), False, 0)]


def contact_sheet(items, scale=4):
    """Превʼю в стилі гри (база + контурована турель) для візуальної перевірки."""
    sheet = Image.new("RGBA", (sum(i[0].width for i in items) * scale + 40 * (len(items) + 1),
                               max(i[0].height for i in items) * scale + 80), C("#2a2d33"))
    x = 40
    for base, top, parts in items:
        comp = top.copy()
        for p in parts:
            img, (cx, cy), flip = p[0], p[1], p[2]
            rot = p[3] if len(p) > 3 else 0
            if rot:
                img = img.rotate(rot, expand=True, resample=Image.NEAREST)
            paste_c(comp, img, cx, cy, flip=flip and rot == 0)
        frame = base.copy()
        frame.alpha_composite(outline_img(comp))
        big = frame.resize((frame.width * scale, frame.height * scale), Image.NEAREST)
        sheet.alpha_composite(big, (x, 40))
        x += big.width + 40
    sheet.save(os.path.join(OUT, "..", "..", "..", "tools", "preview_sheet.png"))


if __name__ == "__main__":
    contact_sheet([volt(), frostbite(), titan()], scale=3)
    print("OK:", sorted(os.listdir(OUT)))
