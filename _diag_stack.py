#!/usr/bin/env python3
"""¿Qué hay encima del titular? Diagnostico de apilamiento real."""
import json
from playwright.sync_api import sync_playwright

JS = """() => {
  const t = document.querySelector('.hero__title');
  const r = t.getBoundingClientRect();
  const cx = Math.round(r.left + Math.min(r.width / 2, 200));
  const cy = Math.round(r.top + r.height / 2);
  const stack = document.elementsFromPoint(cx, cy).slice(0, 6).map(e => (e.tagName + '.' + String(e.className).slice(0, 30)).trim());
  const cs = getComputedStyle(t);
  const body = getComputedStyle(document.body);
  return {
    punto: [cx, cy],
    rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
    pila: stack,
    titulo: { color: cs.color, op: cs.opacity, vis: cs.visibility, z: cs.zIndex, font: cs.fontSize, ff: cs.fontFamily.slice(0, 40), mix: cs.mixBlendMode },
    body: { bg: body.backgroundColor, bgImg: body.backgroundImage.slice(0, 60), clase: document.body.className },
    canvasSize: (() => { const c = document.getElementById('gl'); return c ? [c.width, c.height, getComputedStyle(c).zIndex, getComputedStyle(c).opacity] : null; })(),
    grain: (() => { const g = document.querySelector('.grain'); const s = getComputedStyle(g); return { z: s.zIndex, op: s.opacity, mix: s.mixBlendMode, bg: s.background.slice(0, 50) }; })(),
    loader: (() => { const l = document.getElementById('loader'); const s = getComputedStyle(l); return { vis: s.visibility, op: s.opacity, z: s.zIndex, bg: s.backgroundColor }; })(),
    fuentes: Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family).slice(0, 5)
  };
}"""

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto("http://127.0.0.1:8899/", wait_until="load", timeout=70000)
    pg.wait_for_timeout(5000)
    print(json.dumps(pg.evaluate(JS), ensure_ascii=False, indent=1))
    # captura sin grain ni canvas, para aislar
    pg.evaluate("document.querySelector('.grain').style.display='none'; const c=document.getElementById('gl'); if(c) c.style.display='none';")
    pg.wait_for_timeout(500)
    pg.screenshot(path="/tmp/v-sin-capas.png")
    b.close()
print("captura: /tmp/v-sin-capas.png")
