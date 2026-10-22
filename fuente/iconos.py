# -*- coding: utf-8 -*-
"""Hace el logo pequeno que sale en la pestana del navegador (favicon).

Es la "J" de JATH en crema sobre el rojo del sitio, con la misma tipografia del
encabezado. Se guardan varios tamanos en la carpeta "iconos" y catalogo.py los copia
al sitio cada vez que se corre.
"""
import os

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "iconos")

ROJO = (193, 18, 31)      # --rojo
CREMA = (250, 247, 240)   # --crema

FUENTES = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]


def fuente(px):
    for ruta in FUENTES:
        if os.path.isfile(ruta):
            return ImageFont.truetype(ruta, px)
    raise SystemExit("no encontre una fuente en negrita")


def icono(lado):
    im = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    radio = int(lado * 0.22)
    d.rounded_rectangle((0, 0, lado - 1, lado - 1), radius=radio, fill=ROJO)

    # La J se dibuja con un tamano de fuente tal que la letra ocupe ~58% del alto.
    f = fuente(int(lado * 0.86))
    caja = d.textbbox((0, 0), "J", font=f)
    alto_letra = caja[3] - caja[1]
    objetivo = lado * 0.58
    f = fuente(max(8, int(f.size * objetivo / alto_letra)))
    caja = d.textbbox((0, 0), "J", font=f)
    x = (lado - (caja[2] - caja[0])) / 2 - caja[0]
    y = (lado - (caja[3] - caja[1])) / 2 - caja[1]
    d.text((x, y), "J", font=f, fill=CREMA)
    return im


def main():
    os.makedirs(SALIDA, exist_ok=True)
    for lado in (512, 180, 32, 16):
        im = icono(lado)
        im.save(os.path.join(SALIDA, "favicon-%d.png" % lado), "PNG", optimize=True)
        print("icono %dx%d" % (lado, lado))
    grande = icono(256)
    grande.save(os.path.join(SALIDA, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("favicon.ico")


if __name__ == "__main__":
    main()
