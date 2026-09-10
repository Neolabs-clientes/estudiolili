#!/usr/bin/env python3
"""QA real de la demo con Chromium: contenido, errores de consola, red y capturas."""
import json, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://neolabs-clientes.github.io/lili-nails-demo/"
VP = [("desktop", {"width": 1440, "height": 1000}, 1, False, False),
      ("movil", {"width": 390, "height": 844}, 3, True, True)]

CHECK = """() => {
  const gl = document.getElementById('gl');
  let webgl = false;
  try { const c = document.createElement('canvas'); webgl = !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) {}
  const vis = el => el ? getComputedStyle(el).visibility + '/' + getComputedStyle(el).opacity : 'n/a';
  return {
    title: document.title,
    bodyClass: document.body.className,
    altoTotal: document.body.scrollHeight,
    ancho: window.innerWidth,
    hero: (document.querySelector('.hero__title') || {}).innerText || '',
    secciones: document.querySelectorAll('section').length,
    servicios: document.querySelectorAll('.card').length,
    pasos: document.querySelectorAll('.step').length,
    tipos: document.querySelectorAll('.type').length,
    fotosGaleria: document.querySelectorAll('.shot').length,
    faqs: document.querySelectorAll('.faq__item').length,
    waBubble: (document.getElementById('wa-bubble') || {}).href || '',
    waNav: (document.querySelector('.nav__cta') || {}).href || '',
    canvas: gl ? gl.width + 'x' + gl.height : 'sin-canvas',
    webglSoportado: webgl,
    loaderVisible: vis(document.getElementById('loader')),
    desbordamientoH: document.documentElement.scrollWidth > window.innerWidth + 2,
    scrollW: document.documentElement.scrollWidth
  };
}"""

out = {}
with sync_playwright() as p:
    browser = p.chromium.launch(args=["--enable-unsafe-swiftshader", "--use-gl=swiftshader", "--no-sandbox"])
    for name, vp, dsf, mobile, touch in VP:
        ctx = browser.new_context(viewport=vp, device_scale_factor=dsf, is_mobile=mobile, has_touch=touch,
                                  user_agent=None if not mobile else "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        page = ctx.new_page()
        cons, fails = [], []
        page.on("console", lambda m: cons.append(m.type + ": " + m.text[:160]) if m.type == "error" else None)
        page.on("pageerror", lambda e: cons.append("pageerror: " + str(e)[:160]))
        page.on("requestfailed", lambda r: fails.append(r.url.split("/")[-1][:60] + " :: " + str(r.failure)[:60]))
        page.goto(URL, wait_until="load", timeout=70000)
        page.wait_for_timeout(5000)
        info = page.evaluate(CHECK)
        page.screenshot(path="/tmp/qa-%s.png" % name)
        page.screenshot(path="/tmp/qa-%s-full.png" % name, full_page=True)
        out[name] = {"info": info, "errores": cons[:10], "fallosRed": fails[:10]}
        ctx.close()
    browser.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
