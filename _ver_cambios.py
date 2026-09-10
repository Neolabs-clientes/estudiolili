#!/usr/bin/env python3
"""Verifica los cambios pedidos: sin foto en el hero, efecto mas pequeno y legible."""
import json
from PIL import Image
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/"

def brillo(im, box=None):
    if box: im = im.crop(box)
    im = im.convert("L")
    d = list(im.getdata())
    n = len(d)
    return round(100.0 * sum(1 for p in d if p > 140) / n, 2), max(d)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader"])
    for name, vp in [("desktop", {"width": 1440, "height": 1000}), ("movil", {"width": 390, "height": 844})]:
        ctx = b.new_context(viewport=vp, device_scale_factor=1, is_mobile=(name == "movil"))
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
        pg.goto(URL, wait_until="load", timeout=60000)
        pg.wait_for_timeout(5000)
        info = pg.evaluate("""() => {
          const hero = document.querySelector('.hero');
          const imgsHero = hero ? Array.from(hero.querySelectorAll('img')).map(i=>i.getAttribute('src')) : ['(sin hero)'];
          const t = document.querySelector('.hero__title');
          const r = t.getBoundingClientRect();
          const card = document.querySelector('.card');
          return {
            imagenesEnHero: imgsHero,
            heroAlto: Math.round(hero.getBoundingClientRect().height),
            titulo: {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)},
            claseCuerpo: document.body.className,
            canvas: document.getElementById('gl') ? document.getElementById('gl').width + 'x' + document.getElementById('gl').height : 'none'
          };
        }""")
        pg.screenshot(path=f"/tmp/c-{name}.png")
        im = Image.open(f"/tmp/c-{name}.png")
        t = info["titulo"]
        # banda donde vive el titular
        banda = (max(0, t["x"] - 20), max(0, t["y"] - 20), min(vp["width"], t["x"] + t["w"] + 20), min(vp["height"], t["y"] + t["h"] + 20))
        gen, _ = brillo(im)
        tex, mx = brillo(im, banda)
        print(f"[{name}] px claros totales: {gen}% | en el titular: {tex}% (max {mx})")
        print(f"[{name}] imagenes dentro del hero: {info['imagenesEnHero']}")
        print(f"[{name}] titulo en pantalla: {t} | body: {info['claseCuerpo']} | canvas: {info['canvas']}")
        print(f"[{name}] errores JS: {errs[:2] if errs else 'ninguno'}")
        ctx.close()
    b.close()
