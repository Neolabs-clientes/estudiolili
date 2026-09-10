#!/usr/bin/env python3
"""Diagnostico de capturas: control blanco + estadisticas de la captura real."""
from PIL import Image
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 800, "height": 400})
    pg.set_content("<body style='background:#ffffff;margin:0'><h1 style='color:#000;font:700 40px sans-serif'>CONTROL BLANCO</h1></body>")
    pg.wait_for_timeout(700)
    pg.screenshot(path="/tmp/control-blanco.png")
    b.close()

im = Image.open("/tmp/control-blanco.png").convert("L")
d = list(im.getdata())
print("CONTROL BLANCO -> max:", max(d), "media:", round(sum(d) / len(d), 1), "| % >200:", round(sum(1 for q in d if q > 200) / len(d) * 100, 1))

for f in ["/tmp/v-hero.png", "/tmp/v-galeria.png", "/tmp/v-lili.png"]:
    im = Image.open(f).convert("L")
    d = list(im.getdata())
    print(f.split("/")[-1], "-> max:", max(d), "media:", round(sum(d) / len(d), 1), "| % >100:", round(sum(1 for q in d if q > 100) / len(d) * 100, 2))
