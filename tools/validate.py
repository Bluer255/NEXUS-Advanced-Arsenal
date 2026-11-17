#!/usr/bin/env python3
"""Перевірка: hjson <-> текстури <-> локалізація (розміри, назви, ключі)."""
import os, re, sys
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SPR = os.path.join(ROOT, "sprites", "blocks", "turrets")
errors = []
BUNDLES = ["bundle.properties", "bundle_en.properties", "bundle_uk_UA.properties", "bundle_ru.properties"]
bundles = {b: open(os.path.join(ROOT, "bundles", b), encoding="utf-8").read() for b in BUNDLES}
for fn, (w, h) in (("preview.png", (1280, 720)), ("icon.png", (256, 256))):
    pth = os.path.join(ROOT, fn)
    if not os.path.exists(pth): errors.append(f"НЕМАЄ {fn} у корені моду")
    elif Image.open(pth).size != (w, h): errors.append(f"{fn}: {Image.open(pth).size}, очікується {(w, h)}")
for f in sorted(os.listdir(os.path.join(ROOT, "content", "blocks", "turrets"))):
    src = open(os.path.join(ROOT, "content", "blocks", "turrets", f), encoding="utf-8").read()
    bid = f.rsplit(".", 1)[0]
    size = int(re.search(r"^size:\s*(\d+)", src, re.M).group(1))
    px = size * 32
    # обов'язкові регіони DrawTurret + регіони частин
    need = {bid: (px, px), bid + "-base": (px, px), bid + "-heat": (px, px), bid + "-preview": (px, px)}
    for suffix in re.findall(r'type:\s*RegionPart,\s*suffix:\s*"([^"]+)"', src):
        need[bid + suffix] = None  # розмір довільний
    for name, dim in need.items():
        p = os.path.join(SPR, name + ".png")
        if not os.path.exists(p):
            errors.append(f"НЕМАЄ текстури: {name}.png (потрібна для {f})"); continue
        im = Image.open(p)
        if im.mode != "RGBA": errors.append(f"{name}.png не RGBA")
        if dim and im.size != dim: errors.append(f"{name}.png: {im.size}, очікується {dim}")
        if not im.getbbox(): errors.append(f"{name}.png порожня")
        print(f"  ok {name}.png {im.size}")
    for bn, bt in bundles.items():
        for k in ("name", "description", "details"):
            m = re.search(rf"^block\.nexus-arsenal-{re.escape(bid)}\.{k}=(.+)$", bt, re.M)
            if not m or not m.group(1).strip():
                errors.append(f"{bn}: немає/порожній ключ block.nexus-arsenal-{bid}.{k}")
# жодних зайвих PNG
used = set()
for f in os.listdir(SPR): used.add(f)
print("Помилки:" if errors else "Усе узгоджено.")
for e in errors: print(" -", e)
sys.exit(1 if errors else 0)
