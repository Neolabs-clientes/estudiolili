import json, sys
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=angle"])
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    errs = []
    pg.on("console", lambda m: errs.append(m.text[:120]) if m.type == "error" else None)
    pg.goto(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899/", wait_until="load")
    pg.wait_for_timeout(2600)
    pg.evaluate("document.querySelector('.cert').scrollIntoView({block:'center'})")
    pg.wait_for_timeout(1400)
    info = pg.evaluate("""() => {
      const c = document.querySelector('.cert');
      if (!c) return {ok:false};
      const im = c.querySelector('img');
      const r = c.getBoundingClientRect();
      return {ok:true, nat: [im.naturalWidth, im.naturalHeight], box: [Math.round(r.width), Math.round(r.height)],
              cap: (c.querySelector('.cert__cap')||{}).textContent,
              overflow: document.documentElement.scrollWidth > window.innerWidth + 1};
    }""")
    pg.evaluate("document.querySelector('.cert').click()")
    pg.wait_for_timeout(900)
    lb = pg.evaluate("""() => {const l=document.getElementById('lightbox'), i=document.getElementById('lightbox-img');
      return {abierto: !l.hasAttribute('hidden'), src: i.getAttribute('src'), nat: i.naturalWidth};}""")
    pg.evaluate("document.querySelector('.cert').scrollIntoView({block:'center'})")
    pg.wait_for_timeout(700)
    pg.screenshot(path="/tmp/cert-local.png")
    print("CERT:", json.dumps(info, ensure_ascii=False))
    print("VISOR:", json.dumps(lb, ensure_ascii=False))
    print("ERRORES JS:", errs[:3])
    b.close()
