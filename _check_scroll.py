#!/usr/bin/env python3
"""Recorre la pagina haciendo scroll y comprueba que TODO el contenido acaba visible."""
import json
from PIL import Image
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/"
CHECK = """() => {
  const out = [];
  document.querySelectorAll('.reveal').forEach(el => {
    const cs = getComputedStyle(el);
    if (parseFloat(cs.opacity) < 0.06) {
      out.push({ sel: (el.className || '').slice(0, 44), y: Math.round(el.getBoundingClientRect().top + window.scrollY) });
    }
  });
  return out;
}"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(URL, wait_until="load", timeout=70000)
    pg.wait_for_timeout(4500)
    pg.screenshot(path="/tmp/v-hero.png")
    total = pg.evaluate("document.body.scrollHeight")
    y = 0
    while y < total - 1000:
        y += 900
        pg.evaluate(f"window.scrollTo(0,{y})")
        pg.wait_for_timeout(700)
    pg.wait_for_timeout(1200)
    print("altura total:", total)
    print("invisibles tras recorrer TODO:", json.dumps(pg.evaluate(CHECK), ensure_ascii=False))
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('#galeria').scrollIntoView()")
    pg.wait_for_timeout(1500)
    pg.screenshot(path="/tmp/v-galeria.png")
    pg.evaluate("document.querySelector('#lili').scrollIntoView()")
    pg.wait_for_timeout(1500)
    pg.screenshot(path="/tmp/v-lili.png")
    pg.evaluate("document.querySelector('#reserva').scrollIntoView()")
    pg.wait_for_timeout(1500)
    pg.screenshot(path="/tmp/v-reserva.png")
    b.close()

for f in ["/tmp/v-hero.png", "/tmp/v-galeria.png", "/tmp/v-lili.png", "/tmp/v-reserva.png"]:
    im = Image.open(f).convert("L")
    w, h = im.size
    px = list(im.getdata())
    bright = sum(1 for q in px if q > 150) / len(px) * 100
    print(f.split('/')[-1], w, "x", h, "| % pixeles claros (texto/contenido):", round(bright, 2))
