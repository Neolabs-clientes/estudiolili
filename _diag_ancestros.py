#!/usr/bin/env python3
"""Recorre los ancestros del titular mostrando opacidad, visibilidad, clip y tamaño."""
import json
from playwright.sync_api import sync_playwright

JS = """() => {
  const out = [];
  let el = document.querySelector('.hero__title');
  while (el && el !== document.documentElement) {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    out.push({
      el: el.tagName + '.' + String(el.className || '').slice(0, 28),
      op: cs.opacity, vis: cs.visibility, disp: cs.display,
      clip: cs.clipPath, ov: cs.overflow, pos: cs.position, z: cs.zIndex,
      rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      h: cs.height, maxh: cs.maxHeight
    });
    el = el.parentElement;
  }
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1200, "height": 800})
    pg.goto("http://127.0.0.1:8899/", wait_until="load", timeout=60000)
    pg.wait_for_timeout(4000)
    for fila in pg.evaluate(JS):
        print(json.dumps(fila, ensure_ascii=False))
    # ¿pinta algo si quitamos el canvas del hero por completo?
    pg.evaluate("const b=document.querySelector('.hero__bg'); if(b) b.remove();")
    pg.wait_for_timeout(600)
    pg.screenshot(path="/tmp/iso-sin-bg.png")
    b.close()

from PIL import Image
im = Image.open("/tmp/iso-sin-bg.png").convert("L")
d = list(im.getdata())
print("sin hero__bg -> px claros:", round(sum(1 for q in d if q > 150) / len(d) * 100, 2), "% max:", max(d))
