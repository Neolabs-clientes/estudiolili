#!/usr/bin/env python3
"""Compara el brillo de la mitad derecha (donde vive el efecto) antes y despues."""
from PIL import Image

def masa(f, x0f, x1f):
    im = Image.open(f).convert("L")
    w, h = im.size
    im = im.crop((int(w * x0f), 0, int(w * x1f), h))
    d = list(im.getdata())
    n = len(d)
    claros = sum(1 for p in d if p > 120)
    return round(100.0 * claros / n, 2), max(d), n

for etiqueta, f in [("ANTES", "/tmp/v-hero.png"), ("DESPUES", "/tmp/c-desktop.png")]:
    der = masa(f, 0.5, 1.0)
    izq = masa(f, 0.0, 0.5)
    print(f"{etiqueta:8s} mitad derecha: {der[0]}% claros (max {der[1]}, {der[2]} px) | mitad izquierda: {izq[0]}%")
