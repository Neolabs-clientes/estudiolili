#!/usr/bin/env python3
"""Descarga fotos de Pexels por ID, verifica que son JPEG reales y genera WebP."""
import urllib.request, os, sys
from PIL import Image

OUT = os.path.expanduser("~/clients/lili-nails/assets/fotos")
os.makedirs(OUT, exist_ok=True)

# (id pexels, nombre destino)
FOTOS = [
    (9393756, "gal-01"),   # rojas con anillos dorados
    (34997574, "gal-02"),  # francesa con anillos
    (13427498, "gal-03"),  # perla + manicura
    (17471373, "gal-04"),  # manos con diseno
    (15491630, "gal-05"),  # acrilicas blanco con corazones
    (13867817, "gal-06"),  # colgante + manicura
    (13106159, "gal-07"),  # manos sobre denim
    (16795889, "gal-08"),  # acrilicas verano
    (16795889, "gal-08b"),
    (22668317, "proc-01"), # manicura en el salon
    (6135675,  "proc-02"), # procedimiento
    (3738377,  "proc-03"), # guantes negros, tratamiento
    (3738378,  "proc-04"), # banera de manos spa
]

def get(pid, name):
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1800&fm=jpg"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    ok_hdr = raw[:2] == b"\xff\xd8"
    jpg = os.path.join(OUT, name + ".jpg")
    open(jpg, "wb").write(raw)
    im = Image.open(jpg)
    w, h = im.size
    webp = os.path.join(OUT, name + ".webp")
    im.convert("RGB").save(webp, "WEBP", quality=86)
    return ok_hdr, (pid, name, w, h, len(raw)//1024, os.path.getsize(webp)//1024)

seen = set()
for pid, name in FOTOS:
    if name in seen:
        continue
    seen.add(name)
    try:
        print(get(pid, name))
    except Exception as e:
        print("FALLO", pid, name, str(e)[:80])
