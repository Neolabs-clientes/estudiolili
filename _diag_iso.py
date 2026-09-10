#!/usr/bin/env python3
"""Aisla la causa: ¿fuente web? ¿filtros/backdrop-filter? ¿transformaciones?"""
from PIL import Image
from playwright.sync_api import sync_playwright

def brillo(f):
    im = Image.open(f).convert("L")
    d = list(im.getdata())
    return round(sum(1 for q in d if q > 150) / len(d) * 100, 2), max(d)

CASOS = {
    "base": "",
    "fuente_sistema": "*{font-family:Georgia,serif !important}",
    "sin_filtros": "*{backdrop-filter:none !important;filter:none !important;-webkit-backdrop-filter:none !important}",
    "sin_blend": "*{mix-blend-mode:normal !important}",
    "sin_animacion": "*{opacity:1 !important;transform:none !important}",
    "todo_junto": "*{font-family:Georgia,serif !important;backdrop-filter:none !important;filter:none !important;mix-blend-mode:normal !important;opacity:1 !important;transform:none !important}",
}

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    for nombre, css in CASOS.items():
        pg = b.new_page(viewport={"width": 1200, "height": 800})
        pg.goto("http://127.0.0.1:8899/", wait_until="load", timeout=60000)
        pg.wait_for_timeout(3500)
        if css:
            pg.add_style_tag(content=css)
            pg.wait_for_timeout(900)
        f = f"/tmp/iso-{nombre}.png"
        pg.screenshot(path=f)
        pg.close()
        pc, mx = brillo(f)
        print(f"{nombre:16} -> px claros: {pc:6} %  max: {mx}")
    b.close()
