#!/usr/bin/env python3
"""Prueba decisiva: la misma pagina sin JS, y sin WebGL."""
from PIL import Image
from playwright.sync_api import sync_playwright

def medir(f):
    im = Image.open(f).convert("L")
    d = list(im.getdata())
    return round(sum(1 for q in d if q > 150) / len(d) * 100, 2), max(d)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    # A) sin JavaScript
    ctx = b.new_context(viewport={"width": 1200, "height": 800}, java_script_enabled=False)
    pg = ctx.new_page()
    pg.goto("http://127.0.0.1:8899/", wait_until="load", timeout=60000)
    pg.wait_for_timeout(2500)
    pg.screenshot(path="/tmp/iso-sinjs.png")
    ctx.close()
    print("sin JS    ->", medir("/tmp/iso-sinjs.png"))
    # B) JS activo pero el modulo WebGL bloqueado
    ctx2 = b.new_context(viewport={"width": 1200, "height": 800})
    pg2 = ctx2.new_page()
    pg2.route("**/scene.js", lambda r: r.abort())
    pg2.goto("http://127.0.0.1:8899/", wait_until="load", timeout=60000)
    pg2.wait_for_timeout(3500)
    pg2.screenshot(path="/tmp/iso-sinwebgl.png")
    ctx2.close()
    print("sin scene ->", medir("/tmp/iso-sinwebgl.png"))
    b.close()
