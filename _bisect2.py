#!/usr/bin/env python3
"""Biseccion fina: con las reglas base (0-107) siempre activas, busca la regla culpable."""
from PIL import Image
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/"
BASE = list(range(0, 108))
CAND = list(range(108, 217))

def brillo(f):
    im = Image.open(f).convert("L")
    d = list(im.getdata())
    return sum(1 for q in d if q > 150) / len(d) * 100

def prueba(pg, keep, tag):
    pg.goto(URL, wait_until="load", timeout=60000)
    pg.wait_for_timeout(1800)
    pg.evaluate("""([keep]) => {
      const s = [...document.styleSheets].find(x => (x.href || '').includes('styles.css'));
      if (!s) return;
      const rules = [...s.cssRules];
      for (let i = rules.length - 1; i >= 0; i--) {
        if (!keep.includes(i) && rules[i].type !== 3) { try { s.deleteRule(i); } catch (e) {} }
      }
    }""", [keep])
    pg.wait_for_timeout(600)
    f = f"/tmp/fine-{tag}.png"
    pg.screenshot(path=f)
    return brillo(f)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1200, "height": 800})
    print("control (0-107 solas):", round(prueba(pg, BASE, "base"), 2), "%")
    lo, hi = 0, len(CAND)          # rango de candidatas
    while hi - lo > 1:
        mid = (lo + hi) // 2
        keep = BASE + CAND[:mid]   # base + las primeras 'mid' candidatas
        v = prueba(pg, keep, f"{mid}")
        print(f"candidatas 0..{mid-1} ({len(keep)} reglas) -> {round(v,2)}%")
        if v < 1.0:                # texto invisible: la culpable esta en este bloque
            hi = mid
        else:
            lo = mid
    print("regla culpable (indice en styles.css):", CAND[hi - 1] if hi > 0 else CAND[0])
    b.close()
