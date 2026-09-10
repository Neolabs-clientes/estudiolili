#!/usr/bin/env python3
"""Histograma real de las capturas: ¿hay texto dibujado?"""
from PIL import Image

for f in ["/tmp/v-sin-capas.png", "/tmp/v-hero.png", "/tmp/v-galeria.png"]:
    im = Image.open(f).convert("RGB")
    w, h = im.size
    # zona del titular (aprox) y zona general
    crop = im.crop((int(w * 0.05), int(h * 0.15), int(w * 0.6), int(h * 0.6))).convert("L")
    hist = crop.histogram()
    total = sum(hist)
    claro = sum(hist[150:]) / total * 100
    medio = sum(hist[60:150]) / total * 100
    print(f.split("/")[-1], "| px claros(>150):", round(claro, 2), "% | medios(60-150):", round(medio, 2), "% | max:", max(hist), "en nivel", hist.index(max(hist)))
    # colores dominantes de toda la imagen
    small = im.resize((60, 40))
    col = sorted(small.getcolors(9999), reverse=True)[:3]
    print("   dominantes:", [(c[1], c[0]) for c in col])
