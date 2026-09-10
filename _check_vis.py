#!/usr/bin/env python3
"""Comprueba si el contenido se ve de verdad: opacidades calculadas + brillo de la captura."""
import json, sys
from PIL import Image
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://neolabs-clientes.github.io/lili-nails-demo/"
SHOT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/qa-desktop.png"

# 1) brillo de la captura
im = Image.open(SHOT).convert("L")
w, h = im.size
top = im.crop((0, 0, w, int(h * 0.75)))
px = list(top.getdata())
mean = sum(px) / len(px)
dark = sum(1 for p in px if p < 40) / len(px)
print("captura:", w, "x", h, "| brillo medio(arriba):", round(mean, 1), "| % casi-negro:", round(dark * 100, 1))

# 2) opacidades reales en el navegador
CHECK = """() => {
  const sel = ['.hero__title', '.hero__text', '.chips', '.hero__figure', '.hero__actions',
               '#servicios h2', '#servicios .card', '#rusa .step', '#galeria .shot', '#lili .about__copy', '.footer__col'];
  const out = {};
  sel.forEach(s => {
    const el = document.querySelector(s);
    if (!el) { out[s] = 'NO EXISTE'; return; }
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    out[s] = { op: cs.opacity, vis: cs.visibility, tr: cs.transform.slice(0, 26), y: Math.round(r.top), alto: Math.round(r.height) };
  });
  out['scrollTotal'] = document.body.scrollHeight;
  return out;
}"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(URL, wait_until="load", timeout=70000)
    pg.wait_for_timeout(5000)
    print(json.dumps(pg.evaluate(CHECK), ensure_ascii=False, indent=1))
    pg.screenshot(path="/tmp/qa-hero2.png")
    # scroll a la galeria y captura
    pg.evaluate("document.querySelector('#galeria').scrollIntoView()")
    pg.wait_for_timeout(2500)
    pg.screenshot(path="/tmp/qa-galeria.png")
    b.close()
print("capturas: /tmp/qa-hero2.png /tmp/qa-galeria.png")
