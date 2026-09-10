#!/usr/bin/env python3
"""Control: ¿el headless pinta texto claro sobre fondo oscuro? ¿Y un JPEG?"""
from PIL import Image
from playwright.sync_api import sync_playwright

HTML = """<body style="background:#120b10;margin:0">
<h1 style="color:#fbf7f4;font:700 90px Georgia,serif;padding:40px">TEXTO CLARO DE PRUEBA</h1>
<img src="http://127.0.0.1:8899/assets/fotos/gal-01.webp" style="width:420px;margin-left:40px">
</body>"""

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1200, "height": 700})
    pg.set_content(HTML, wait_until="load")
    pg.wait_for_timeout(1800)
    pg.screenshot(path="/tmp/control-oscuro.png")
    b.close()

im = Image.open("/tmp/control-oscuro.png").convert("L")
d = list(im.getdata())
print("CONTROL OSCURO -> max:", max(d), "| % >150:", round(sum(1 for q in d if q > 150) / len(d) * 100, 2), "| % >60:", round(sum(1 for q in d if q > 60) / len(d) * 100, 2))
