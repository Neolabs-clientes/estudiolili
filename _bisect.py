#!/usr/bin/env python3
"""Bisecciona styles.css: encuentra las reglas que hacen invisible el texto."""
from PIL import Image
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/"

def brillo(f):
    im = Image.open(f).convert("L")
    d = list(im.getdata())
    return sum(1 for q in d if q > 150) / len(d) * 100

def prueba(pg, keep, total, etiqueta):
    """Deja solo las reglas de 'keep' (indices) y mide."""
    pg.goto(URL, wait_until="load", timeout=60000)
    pg.wait_for_timeout(2000)
    pg.evaluate("""([keep]) => {
      const s = [...document.styleSheets].find(x => (x.href || '').includes('styles.css'));
      if (!s) return 0;
      const rules = [...s.cssRules];
      // borrar de atras hacia delante las que no estan en keep
      for (let i = rules.length - 1; i >= 0; i--) {
        if (!keep.includes(i) && !(rules[i].type === 3)) { try { s.deleteRule(i); } catch (e) {} }
      }
      return keep.length;
    }""", [keep])
    pg.wait_for_timeout(700)
    f = f"/tmp/bisect-{etiqueta}.png"
    pg.screenshot(path=f)
    return brillo(f)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1200, "height": 800})
    pg.goto(URL, wait_until="load", timeout=60000)
    total = pg.evaluate("""() => {
      const s = [...document.styleSheets].find(x => (x.href || '').includes('styles.css'));
      return s ? s.cssRules.length : -1;
    }""")
    print("reglas totales:", total)
    idx = list(range(total))
    # mitades
    for nombre, keep in [("primera_mitad", idx[:total // 2]), ("segunda_mitad", idx[total // 2:])]:
        v = prueba(pg, keep, total, nombre)
        print(f"{nombre}: {len(keep)} reglas -> brillo {round(v, 2)}%")
    b.close()
