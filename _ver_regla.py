#!/usr/bin/env python3
"""Muestra las reglas 185-196 de styles.css (tal como las ve el navegador)."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page()
    pg.goto("http://127.0.0.1:8899/", wait_until="load", timeout=60000)
    out = pg.evaluate("""() => {
      const s = [...document.styleSheets].find(x => (x.href || '').includes('styles.css'));
      const r = [...s.cssRules];
      return r.slice(183, 197).map((x, i) => (183 + i) + ' [' + x.type + '] ' + (x.selectorText || x.cssText.slice(0, 40)) + ' => ' + x.cssText.slice(0, 220));
    }""")
    for l in out:
        print(l)
        print("-")
    b.close()
