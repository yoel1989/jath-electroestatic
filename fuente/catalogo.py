# -*- coding: utf-8 -*-
"""Arma el catalogo vivo de JATH ELECTROESTATIC: paleta real de 48 colores, equipos y cotizador
que manda el pedido por WhatsApp.

No es el PDF en una pagina. La diferencia esta en que aqui los colores son datos y no una
foto: se pueden buscar, copiar el codigo, y agregar a una peticion. Y la peticion se manda
sola por WhatsApp.

De donde sale cada cosa:

- Los 48 colores salen de las dos cartas impresas: el hex se midio del cuadro de cada uno, y
  el nombre, que la carta trae impreso al lado, se leyo del rotulo. Los pocos nombres que no
  se pudieron leer con seguridad quedan marcados en COLORES.txt para que el cliente los
  confirme.
- Las 15 fotos de equipos salen del PDF. Los nombres son provisionales: el folleto no rotula
  ninguna, asi que se deducen de la silueta y de la taxonomia que el propio folleto lista en
  la hoja 2. NOMBRES.txt queda al lado para corregirlos en un minuto.
- Los servicios, la mision, la vision, el contacto y las redes se copian del texto del PDF.
  No se inventa nada: si el PDF no trae direccion, el sitio tampoco.

Los nombres de los equipos y de los colores se pueden sobreescribir sin tocar este codigo:
NOMBRES.txt para los equipos y COLORES.txt para los colores. Si hay un renglon como
"03 | Cabina de curado" o "07 | GRIS TORNADO GOFRADO", gana lo de ahi.
"""
import json
import os
import shutil
from datetime import date
from html import escape

import pymupdf
from PIL import Image, ImageChops

# catalogo.py vive en la subcarpeta "fuente" del sitio: lo que genera va a la carpeta de
# arriba, junto a index.html, para que todo quede en una sola carpeta.
AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.dirname(AQUI)
TMP = os.environ["LOCALAPPDATA"] + r"\Temp\opencode"

# El PDF del cliente va dentro de "fuente". Si no esta, se busca en el Escritorio.
ORIGEN = os.path.join(AQUI, "Portafolio de servicios JATH ELECTROESTATIC.pdf")
if not os.path.isfile(ORIGEN):
    ORIGEN = r"C:\Users\yoooe\OneDrive\Desktop\Portafolio de servicios JATH ELECTROESTATIC.pdf"

# Fotos originales que pone el cliente (la seccion de trabajos). Se copian al sitio tal cual.
FOTOS_CLIENTE = os.path.join(AQUI, "fotos-originales")

# Las fotos crudas recortadas del PDF. Viven aqui para no depender de la carpeta temporal.
CACHE_EQUIPOS = os.path.join(AQUI, "equipos")

WHATSAPP = "573187724163"          # Colombia: 57 + 318 772 4163

# --------------------------------------------------------------------- los equipos
# provisional True = el nombre se dedujo de la forma de la foto, no de un rotulo.
# El numero es el orden de lectura de la hoja: la 5 va en 4 x 3 y la 6 es 1 ancha y 2 abajo.
EQUIPOS = [
    # hoja 6, los tres equipos grandes
    (6, 1, "Cabina de pintura con sistema de filtrado", "Equipos de aplicación", True),
    (6, 2, "Pistola electrostática", "Equipos de aplicación", True),
    (6, 3, "Horno de curado", "Equipos de aplicación", True),
    # hoja 5, los doce repuestos, en el orden en que los pone la propia hoja 2
    (5, 1, "Filtro de aire", "Boquillas, filtros y mangueras", True),
    (5, 2, "Boquilla electrostática", "Boquillas, filtros y mangueras", True),
    (5, 3, "Manguera", "Boquillas, filtros y mangueras", True),
    (5, 4, "Filtro de aire", "Boquillas, filtros y mangueras", True),
    (5, 5, "Controlador electrostático", "Controladores y piezas electrónicas", True),
    (5, 6, "Controlador electrostático", "Controladores y piezas electrónicas", True),
    (5, 7, "Set de piezas eléctricas", "Controladores y piezas electrónicas", True),
    (5, 8, "Set de piezas eléctricas", "Controladores y piezas electrónicas", True),
    (5, 9, "Kit de mantenimiento", "Kits de mantenimiento", True),
    (5, 10, "Kit de mantenimiento", "Kits de mantenimiento", True),
    (5, 11, "Kit de boquillas", "Kits de mantenimiento", True),
    (5, 12, "Kit de filtros", "Kits de mantenimiento", True),
]

# Todo lo de aqui esta copiado palabra por palabra del PDF. Si el PDF no trae direccion, el
# sitio tampoco: inventar un dato de contacto es peor que no tener el dato.
QUIEN_SOMOS = ("En JATH ELECTROESTATIC somos especialistas en soluciones de recubrimiento "
               "electrostático. Ofrecemos pinturas y equipos de alta calidad, respaldados por "
               "asesoría técnica personalizada y un servicio confiable. Nuestro compromiso es "
               "garantizar acabados duraderos y profesionales, convirtiéndonos en aliados "
               "estratégicos de la industria.")

MISION = ("Proveer pinturas y equipos de pintura electrostática que optimicen los procesos de "
          "recubrimiento industrial, garantizando eficiencia, sostenibilidad y resultados "
          "superiores. Acompañamos a nuestros clientes con asesoría técnica especializada y "
          "soluciones personalizadas que impulsan la productividad y competitividad.")

VISION = ("Ser reconocidos en el mercado como líderes en soluciones de pintura electrostática, "
          "destacándonos por la innovación, la calidad y el compromiso con la sostenibilidad. "
          "Aspiramos a transformar la industria del recubrimiento, promoviendo tecnologías "
          "limpias y eficientes que contribuyan al desarrollo responsable y al éxito de "
          "nuestros clientes.")

DIFERENCIADORES = [
    ("Más de 10 años de experiencia", "Trayectoria en el mercado."),
    ("Asesoría personalizada", "Un asesor que conoce su caso."),
    ("Productos de alto rendimiento", "Pinturas y equipos de calidad."),
    ("Entrega ágil en Bogotá y alrededores", ""),
]

# Productos: tres bloques, cada uno con su lista. Es la hoja 2 tal cual.
PRODUCTOS = [
    ("Pinturas electrostáticas en polvo", [
        "Amplia gama de colores y acabados (mate, brillante, texturizado).",
        "Alta resistencia a la corrosión y al desgaste.",
        "Opciones ecológicas y libres de solventes.",
    ]),
    ("Equipos de aplicación electrostática", [
        "Pistolas de pintura electrostática de última generación.",
        "Cabinas de pintura con sistemas de filtrado.",
        "Hornos de curado para acabados duraderos.",
    ]),
    ("Repuestos y accesorios", [
        "Boquillas, filtros y mangueras.",
        "Controladores y piezas electrónicas.",
        "Kits de mantenimiento para equipos.",
    ]),
]

# Servicios: el nombre y los detalles tambien son de la hoja 2, sin cambiar ni una palabra.
SERVICIOS = [
    ("Asesoría técnica especializada",
     ["Selección de equipos y pinturas según la necesidad del cliente."]),
    ("Capacitación en procesos de aplicación electrostática",
     ["Acompañamiento al equipo de trabajo en la puesta en marcha."]),
    ("Instalación y mantenimiento",
     ["Montaje de cabinas y hornos.", "Servicio técnico preventivo y correctivo."]),
    ("Optimización de procesos",
     ["Consultoría para mejorar eficiencia y reducir costos.",
      "Implementación de soluciones sostenibles y seguras."]),
]

CONTACTO = {
    "ubicacion": "Bogotá D.C, Colombia",
    "whatsapp": "3187724163",
    "horario": "Lunes a Viernes 8:00am - 6:00pm",
    "redes": [
        ("Instagram", "@jathelectroestatic"),
        ("Facebook", "jathelectroestatic"),
        ("YouTube", "@jathelectroestatic"),
        ("TikTok", "jathelectroestatic"),
    ],
    "lema": "¡Confía en los expertos en pintura!",
}

# -------------------------------------------------------------- nombres de la carta
# Los 48 cuadros de las dos cartas, con el nombre que trae impreso cada uno. La terna
# (carta, fila, columna) dice donde esta el cuadro en la carta; el hex se midio del propio
# cuadro; el nombre se leyo del rotulo con OCR. El OCR acierta casi siempre, pero no
# siempre: los nombres que no se pudieron leer con seguridad van marcados con True, y el
# cliente los corrige en COLORES.txt, al lado del sitio. Carta 3 es la foto que el sitio
# guarda como carta-1.jpg, y la carta 4 como carta-2.jpg.
COLORES_CARTA = [
    # (carta, fila, col, hex, nombre impreso, revisar)
    (3, 1, 1, "#0A342A", "VERDE LISO BTE", False),
    (3, 1, 2, "#9D623D", "MADERA 0316 LISO", True),
    (3, 1, 3, "#A1302E", "MADERA 0316 LISO", True),
    (3, 1, 4, "#6C282B", "MADERA LISO", True),
    (3, 2, 1, "#A67544", "CARAMELO LISO", False),
    (3, 2, 2, "#848A8A", "ALUMINIO LISO BTE", False),
    (3, 2, 3, "#A5ACAB", "ALUMINIO GOFRADO", False),
    (3, 2, 4, "#7A8081", "GRIS TORNADO LISO BTE", False),
    (3, 3, 1, "#979894", "GRIS TORNADO GOFRADO", False),
    (3, 3, 2, "#BDA77C", "GOFRADO", True),
    (3, 3, 3, "#5B7377", "GRIS CRUZ GOFRADO", False),
    (3, 3, 4, "#607379", "GRIS CRUZ MICROTEX", False),
    (3, 4, 1, "#383939", "GRIS NOPAL GOFRADO", False),
    (3, 4, 2, "#91948D", "GRIS NOPAL MICROTEX", False),
    (3, 4, 3, "#293436", "NEGRO LISO BTE", False),
    (3, 4, 4, "#2C3234", "NEGRO GOFRADO", False),
    (3, 5, 1, "#283031", "NEGRO MATE", False),
    (3, 5, 2, "#3D4244", "NEGRO MICROTEX", False),
    (3, 5, 3, "#1E2628", "NEGRO GOFRADO GRUESO", False),
    (3, 5, 4, "#3B4144", "PLATA MARTILLADO", False),
    (3, 6, 1, "#181815", "COBRE MARTILLADO", False),
    (3, 6, 2, "#1D201A", "BRONCE MARTILLADO", False),
    (3, 6, 3, "#997D39", "DORADO LISO BTE", False),
    (3, 6, 4, "#7D7055", "LACA AMARILLA", True),
    (4, 1, 1, "#E7F1F2", "BLANCO MICROTEX", False),
    (4, 1, 2, "#E2EDED", "BLANCO MENTA LISO BTE", False),
    (4, 1, 3, "#E4EFF6", "BLANCO MENTA GOFRADO", False),
    (4, 1, 4, "#E8EDEE", "BLANCO GOFRADO", True),
    (4, 2, 1, "#ECDEC3", "ALMENDRA LISO BTE", False),
    (4, 2, 2, "#EAE1C5", "ALMENDRA GOFRADO", False),
    (4, 2, 3, "#EFE3C3", "BEIS GOFRADO", False),
    (4, 2, 4, "#EAAA0D", "AMARILLO LISO BTE", False),
    (4, 3, 1, "#E25327", "NARANJA LISO BTE", False),
    (4, 3, 2, "#DD5D34", "NARANJA GOFRADO", False),
    (4, 3, 3, "#BA2337", "ROJO LISO BTE", False),
    (4, 3, 4, "#AE1428", "ROJO GOFRADO", False),
    (4, 4, 1, "#541C28", "VINO LISO BTE", False),
    (4, 4, 2, "#D0326D", "FUCSIA MAGENTA LISO BTE", False),
    (4, 4, 3, "#7C649D", "LILA LISO BTE", False),
    (4, 4, 4, "#271941", "MORADO LISO BTE", True),
    (4, 5, 1, "#0573BC", "AZUL CARIBE LISO", False),
    (4, 5, 2, "#1A7B89", "AZUL MARINO LISO BTE", False),
    (4, 5, 3, "#0D3884", "AZUL 5002 LISO BTE", True),
    (4, 5, 4, "#03347A", "AZUL 5003 GOFRADO", True),
    (4, 6, 1, "#051A40", "AZUL COLOMBIA LISO BTE", True),
    (4, 6, 2, "#1D254F", "AZUL MICROTEX", False),
    (4, 6, 3, "#469D39", "VERDE MENTA LISO BTE", False),
    (4, 6, 4, "#025030", "VERDE COLOMBIA LISO BTE", True),
]

# El acabado es lo ultimo del nombre, y es lo que agrupa los filtros del sitio. Se saca del
# nombre en vez de escribirlo aparte, para que si el cliente corrige un nombre en COLORES.txt
# el filtro se acomode solo. El orden importa: "GOFRADO GRUESO" antes que "GOFRADO", y
# "LISO BTE" antes que "LISO".
ACABADOS = [
    ("GOFRADO GRUESO", "Gofrado grueso"),
    ("GOFRADO", "Gofrado"),
    ("MICROTEX", "Microtex"),
    ("MARTILLAD", "Martillado"),
    ("MATE", "Mate"),
    ("LISO BTE", "Liso brillante"),
    ("LISO", "Liso"),
]


def acabado(nombre):
    """El acabado del color, sacado de su nombre impreso."""
    arriba = nombre.upper()
    for clave, etiqueta in ACABADOS:
        if clave in arriba:
            return etiqueta
    return "Sin acabado"


def hex_a_rgb(cadena):
    """De "#A02F2D" a (160, 47, 45)."""
    cadena = cadena.lstrip("#")
    return int(cadena[0:2], 16), int(cadena[2:4], 16), int(cadena[4:6], 16)


# ------------------------------------------------------------------------- armado
def Equipos_ordenados():
    """Los 15 con su indice 1..15 y su foto, en el orden en que se muestran."""
    salida = []
    for i, (hoja, foto, nombre, categoria, provisional) in enumerate(EQUIPOS, 1):
        salida.append({
            "id": i, "nombre": nombre, "categoria": categoria,
            "hoja": hoja, "foto": foto, "provisional": provisional,
            "archivo": "fotos/equipo-%02d.jpg" % i,
        })
    return salida


def ajustes_de_nombres():
    """NOMBRES.txt sobreescribe los nombres provisionales. Se lee si existe.

    Devuelve {numero: (nombre, provisional)}. El renglon que todavia lleva "<- provisional" es
    un nombre que el cliente no ha confirmado: se usa igual, pero el sitio lo sigue marcando.
    Cuando el cliente lo confirme y borre la nota, la marca desaparece. Se lee de la carpeta
    del sitio, que es donde LEEME.txt le dice al cliente que lo edite, no de la carpeta de
    este script. Y nunca se vuelve a escribir si ya existe: si se regenerara en cada corrida,
    lo que el cliente corrigiera se perderia en la segunda vez que se armara el sitio.
    """
    ruta = os.path.join(DESTINO, "NOMBRES.txt")
    if not os.path.isfile(ruta):
        return {}
    cambios = {}
    with open(ruta, encoding="utf-8-sig") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "|" not in linea:
                continue
            num, _, nombre = linea.partition("|")
            # La plantilla marca los dudosos con " <- provisional" al final. Eso es una nota
            # para leerlo, no parte del nombre: si no se quita, el sitio mostraria
            # "Horno de curado <- provisional" como si fuera el nombre del equipo. La
            # comparacion va sobre una copia en minusculas para no destrozar las mayusculas
            # del nombre, que se recorta del original. Si la nota sigue ahi, el nombre se usa
            # igual, pero el sitio lo sigue marcando: el cliente aun no lo confirma.
            plano = nombre.rstrip()
            provisional = plano.lower().endswith("<- provisional")
            if provisional:
                plano = plano[:-len("<- provisional")]
            nombre = plano.strip()
            if not nombre:
                continue
            try:
                cambios[int(num.strip())] = (nombre, provisional)
            except ValueError:
                continue
    return cambios


def _mancha(ancho, alto, cx, cy, radio, tope, curva=2.0, al_reves=False):
    """Un circulo suave en escala de grises, para las luces y las sombras del fondo.

    Se dibuja chico (96 x 96) y se estira con BICUBIC: el desenfoque sale del propio estirado,
    asi no hay que pasear 1,5 millones de pixeles en Python. cx, cy y radio van en fraccion
    de la ALTURA, para que el circulo no salga ovalado en una foto apaisada.
    """
    lado = 96
    m = Image.new("L", (lado, lado), 0)
    p = m.load()
    aspecto = ancho / float(alto)
    for j in range(lado):
        for i in range(lado):
            dx = ((i + 0.5) / lado - cx) * aspecto
            dy = (j + 0.5) / lado - cy
            d = ((dx * dx) + (dy * dy)) ** 0.5 / radio
            v = 0.0 if d >= 1.0 else (1.0 - d) ** curva
            if al_reves:
                v = 1.0 - v
            p[i, j] = int(round(v * tope))
    return m.resize((ancho, alto), Image.BICUBIC)


def fondo_de_la_escena(ruta):
    """La pared de la cabina que va de fondo en la cinta del encabezado.

    Antes esta foto era la de la cabina del taller, pero en esa foto se ven los equipos del
    fondo y el cliente pidio quitarlos. Se pinta una pared vacia: degradado calido, la luz del
    techo arriba, el piso abajo, las esquinas un poco mas oscuras y algo de grano, para que no
    se vea como un degradado de pantalla. El velo del CSS la aclara despues.

    El CSS la recorta con object-fit: cover y de la imagen solo se ve la franja del 30% al 60%
    del alto: ahi es donde caen la luz, la pared y el filo del piso. Como es una pared lisa con
    grano, 1280 px de ancho alcanzan y pesa bastante menos que la version de 1536.
    """
    ancho, alto = 1280, 854
    tira = Image.new("RGB", (1, 320))
    q = tira.load()
    for i in range(320):
        t = i / 319.0
        if t < 0.55:                      # la pared
            k = t / 0.55
            c = (232 + (205 - 232) * k, 226 + (198 - 226) * k, 217 + (187 - 217) * k)
        elif t < 0.66:                    # la luz cae antes de llegar al piso
            k = (t - 0.55) / 0.11
            c = (205 + (186 - 205) * k, 198 + (178 - 198) * k, 187 + (167 - 187) * k)
        else:                             # el piso
            k = (t - 0.66) / 0.34
            c = (174 + (166 - 174) * k, 166 + (158 - 166) * k, 155 + (147 - 155) * k)
        q[0, i] = (int(round(c[0])), int(round(c[1])), int(round(c[2])))
    im = tira.resize((ancho, alto), Image.BICUBIC)

    luz = _mancha(ancho, alto, 0.32, 0.20, 0.62, 30)
    im = ImageChops.add(im, Image.merge("RGB", (luz, luz, luz)))

    # Las esquinas oscuras: es lo que hace que la pared se lea como un cuarto y no como un
    # degradado plano. Suave: en una cinta tan apaisada una viñeta fuerte se ve como una
    # mancha sucia en las puntas.
    vig = _mancha(ancho, alto, 0.5, 0.45, 1.12, 18, curva=1.4, al_reves=True)
    im = ImageChops.subtract(im, Image.merge("RGB", (vig, vig, vig)))

    # Grano: el ruido viene centrado en 128, que es el punto neutro de "overlay", asi que
    # sube y baja el tono sin cambiar el color de la pared.
    ruido = Image.effect_noise((ancho, alto), 9).convert("RGB")
    im = ImageChops.overlay(im, ruido)

    im.save(ruta, "JPEG", quality=80, optimize=True, progressive=True)
    print("   fondo del encabezado: pared de cabina vacia, sin los equipos del taller")


def svg_reja():
    """La reja de tubo cuadrado que se esta pintando en el encabezado.

    Se arma con codigo y no escrita a mano porque cada tubo lleva cuatro piezas (la cara, el
    brillo del filo de arriba, la sombra del filo de abajo y, si va parado, los dos cantos) y
    con ocho tubos eso seria un laberinto de rectangulos: aqui la lista de tubos manda y el
    resto sale sola.

    Lo que la hace ver como metal y no como cuatro barras planas:
      - el brillo y la sombra van DOS veces, una debajo de la pintura (que es el volumen del
        tubo) y otra encima (que es la luz del cuarto), para que la parte ya pintada conserve
        el relieve en vez de quedar como una calcomania;
      - las soldaduras de los cruces y de los cuatro rincones del marco;
      - los pernos de las esquinas, con su hueco y su brillo;
      - el gancho de la linea de donde cuelga.
    """
    # x, y, ancho, alto, parado (1 = vertical)
    tubos = [
        (12, 24, 176, 17, 0),     # marco de arriba
        (12, 151, 176, 17, 0),    # marco de abajo
        (12, 24, 17, 144, 1),     # marco izquierdo
        (171, 24, 17, 144, 1),    # marco derecho
        (55, 41, 12, 110, 1),     # barrote
        (94, 41, 12, 110, 1),     # barrote
        (133, 41, 12, 110, 1),    # barrote
        (29, 90, 142, 12, 0),     # travesano
    ]

    def caja(x, y, a, h, r=1.4):
        return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g"/>'
                % (x, y, a, h, r))

    def punto(cx, cy, r, dx=0.0, dy=0.0):
        return '<circle cx="%g" cy="%g" r="%g"/>' % (cx + dx, cy + dy, r)

    # Cada tubo va con sus filos pegados al lado, no todos los filos juntos al final: asi,
    # cuando un tubo cruza a otro, el que va encima le tapa los filos al de abajo y no quedan
    # rayas claras cruzadas sobre la cara del vecino. El orden de la lista es el orden de
    # profundidad: el ultimo queda delante.
    def brillo(x, y, a, h, parado):
        t = ['<rect x="%g" y="%g" width="%g" height="%g" rx="1" fill="#FFFFFF" opacity=".2"/>'
             % (x + 1, y + 1, a - 2, 2.1)]
        if parado:
            t.append('<rect x="%g" y="%g" width="%g" height="%g" rx=".7" fill="#FFFFFF"'
                     ' opacity=".2"/>' % (x + 1, y + 2.8, 1.5, h - 5.6))
        return "".join(t)

    def sombra(x, y, a, h, parado):
        t = ['<rect x="%g" y="%g" width="%g" height="%g" rx="1" fill="#000000" opacity=".18"/>'
             % (x + 1, y + h - 3.2, a - 2, 2.2)]
        if parado:
            t.append('<rect x="%g" y="%g" width="%g" height="%g" rx=".7" fill="#000000"'
                     ' opacity=".18"/>' % (x + a - 2.5, y + 2.8, 1.5, h - 5.6))
        return "".join(t)

    cuerpo = []
    for x, y, a, h, parado in tubos:
        cuerpo.append("<g>" + caja(x, y, a, h) + sombra(x, y, a, h, parado)
                      + brillo(x, y, a, h, parado) + "</g>")
    cuerpo = "".join(cuerpo)

    # Los cordones de soldadura: donde los barrotes y el travesano se sueldan al marco, mas
    # los cuatro rincones. Van apenas mas claros que el tubo, como se ve una soldadura
    # despues de pulida.
    suelda = []
    for x in (55, 94, 133):
        suelda.append(caja(x - 1.8, 39.2, 15.6, 3.6, 1.8))
        suelda.append(caja(x - 1.8, 149.2, 15.6, 3.6, 1.8))
    suelda.append(caja(27.2, 88.2, 3.8, 15.6, 1.8))
    suelda.append(caja(169.0, 88.2, 3.8, 15.6, 1.8))
    for cx, cy in ((29, 41), (171, 41), (29, 151), (171, 151)):
        suelda.append('<rect x="%g" y="%g" width="3.8" height="3.8" rx="1.7"'
                      ' transform="rotate(45 %g %g)"/>' % (cx - 1.9, cy - 1.9, cx, cy))
    suelda = "".join(suelda)

    rincones = ((20.5, 32.5), (179.5, 32.5), (20.5, 159.5), (179.5, 159.5))
    pernos = "".join(punto(cx, cy, 4) for cx, cy in rincones)
    huecos = "".join(punto(cx, cy, 2.5) for cx, cy in rincones)
    luces = "".join(punto(cx, cy, 0.9, -0.9, -1.1) for cx, cy in rincones)

    plantilla = """<svg class="escena-pieza" viewBox="0 0 200 176" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id="acero" gradientUnits="userSpaceOnUse" x1="0" y1="16" x2="0" y2="176">
            <stop offset="0" stop-color="#C4C9CC"/>
            <stop offset=".26" stop-color="#A2A8AC"/>
            <stop offset=".62" stop-color="#7E8488"/>
            <stop offset="1" stop-color="#545A5E"/>
          </linearGradient>
          <linearGradient id="pintura-color" gradientUnits="userSpaceOnUse" x1="0" y1="24" x2="0" y2="168">
            <stop offset="0" stop-color="#0573BC"/>
            <stop offset=".2" stop-color="#00A896"/>
            <stop offset=".4" stop-color="#469D39"/>
            <stop offset=".6" stop-color="#EAAA0D"/>
            <stop offset=".8" stop-color="#E25327"/>
            <stop offset="1" stop-color="#D0326D"/>
          </linearGradient>
          <linearGradient id="pintura-fade" gradientUnits="userSpaceOnUse" x1="14" y1="0" x2="196" y2="0">
            <stop offset="0" stop-color="#FFFFFF" stop-opacity="1"/>
            <stop offset=".34" stop-color="#FFFFFF" stop-opacity=".95"/>
            <stop offset=".5" stop-color="#FFFFFF" stop-opacity=".5"/>
            <stop offset=".63" stop-color="#FFFFFF" stop-opacity="0"/>
          </linearGradient>
          <mask id="mascara-pintura">
            <rect x="0" y="0" width="200" height="176" fill="url(#pintura-fade)"/>
          </mask>
          <g id="cuerpo">@CUERPO@</g>
        </defs>
        <g fill="none" stroke="#9BA1A5" stroke-width="3">
          <circle cx="100" cy="5.4" r="4.6"/>
        </g>
        <g fill="url(#acero)">
          <rect x="95.8" y="8" width="8.4" height="22" rx="1.6"/>
          <rect x="80" y="14.6" width="40" height="8.4" rx="4.2"/>
        </g>
        <use href="#cuerpo" fill="url(#acero)"/>
        <g fill="url(#acero)" stroke="#FFFFFF" stroke-opacity=".22" stroke-width=".7">@SUELDA@</g>
        <g fill="url(#acero)">@PERNOS@</g>
        <g fill="#4C5154" opacity=".85">@HUECOS@</g>
        <g fill="#FFFFFF" opacity=".45">@LUCES@</g>
        <use href="#cuerpo" fill="url(#pintura-color)" mask="url(#mascara-pintura)"/>
      </svg>"""
    for marca, valor in (("@CUERPO@", cuerpo), ("@SUELDA@", suelda),
                         ("@PERNOS@", pernos), ("@HUECOS@", huecos),
                         ("@LUCES@", luces)):
        plantilla = plantilla.replace(marca, valor)
    return plantilla


def copiar_fotos(doc):
    """Las 15 fotos de equipos, las 2 cartas y las fotos de trabajos del cliente.

    Solo se borran los archivos que genera este script. Las fotos que el cliente ponga
    en la carpeta "fotos" del sitio (trabajos, taller, etc.) no se tocan.
    """
    for sub, hechos in (("fotos", ("escena.jpg", "pistola.jpg")),
                        ("cartas", ("carta-1.jpg", "carta-2.jpg"))):
        d = os.path.join(DESTINO, sub)
        os.makedirs(d, exist_ok=True)
        for n in os.listdir(d):
            if n.startswith("equipo-") or n in hechos:
                try:
                    os.remove(os.path.join(d, n))
                except OSError:
                    pass

    # Las fotos de la seccion de trabajos las pone el cliente en la carpeta "fotos"
    # que esta al lado de este script. Se copian tal cual, sin retocarlas.
    if os.path.isdir(FOTOS_CLIENTE):
        for n in sorted(os.listdir(FOTOS_CLIENTE)):
            if not n.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            origen = os.path.join(FOTOS_CLIENTE, n)
            destino = os.path.join(DESTINO, "fotos", n)
            # Nunca se pisa una foto que ya esta en el sitio y es mas nueva: el cliente
            # puede haberla reemplazado ahi mismo. Solo se copia si falta o si la de la
            # carpeta del proyecto cambio despues.
            if os.path.exists(destino) and os.path.getmtime(destino) >= os.path.getmtime(origen):
                continue
            shutil.copy2(origen, destino)
            print("   foto de trabajos:", n)

    equipos = Equipos_ordenados()
    medidas = {}
    ruta_eq = os.path.join(CACHE_EQUIPOS, "equipos.json")
    if os.path.isfile(ruta_eq):
        with open(ruta_eq, encoding="utf-8") as f:
            for m in json.load(f):
                medidas[(m["hoja"], m["foto"])] = m

    def cruda_de(hoja, foto):
        base = os.path.join(CACHE_EQUIPOS, "eq_%d_%d" % (hoja, foto))
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            if os.path.isfile(base + ext):
                return base + ext
        raise SystemExit("no se encontro la foto de la hoja %d, foto %d" % (hoja, foto))

    for e in equipos:
        im = Image.open(cruda_de(e["hoja"], e["foto"])).convert("RGB")
        im.thumbnail((800, 800), Image.LANCZOS)
        im.save(os.path.join(DESTINO, e["archivo"]), "JPEG", quality=82,
                optimize=True, progressive=True)
        m = medidas.get((e["hoja"], e["foto"]))
        if m:
            e["forma"] = {"prop": m["proporcion"], "solidez": m["solidez"],
                          "piezas": m["piezas"]}

    # El fondo de la cinta ya no es la foto de la cabina: en esa foto se ven los equipos del
    # taller al fondo y el cliente pidio quitarlos. Ahora se dibuja una pared vacia.
    fondo_de_la_escena(os.path.join(DESTINO, "fotos", "escena.jpg"))

    # La pistola del encabezado es la foto real del folleto, no un dibujo: la de la ficha que
    # el cliente rotula "Pistola electrostática". Va entera, sin recortar, y en el CSS lleva
    # mix-blend-mode: multiply. Como el fondo de la foto es claro, el multiply lo funde con la
    # pared que va debajo y no se ve el rectangulo: solo queda la pistola con su sombra. De las
    # dos fichas que el cliente llama igual (04 y 14) se usa la 14 porque su fondo es parejo;
    # el de la 04 tiene manchas y el multiply las dejaria a la vista.
    pistola = Image.open(cruda_de(5, 11)).convert("RGB")
    pistola.thumbnail((700, 700), Image.LANCZOS)
    pistola.save(os.path.join(DESTINO, "fotos", "pistola.jpg"), "JPEG", quality=86,
                 optimize=True, progressive=True)
    print("   pistola del encabezado: hoja 5 foto 11, la foto real de la ficha 14")

    # Las cartas impresas: para que el cliente compare el color de pantalla con el de papel.
    for num, nombre in ((3, "carta-1.jpg"), (4, "carta-2.jpg")):
        pg = doc[num - 1]
        for t in pg.get_images(full=True):
            for r in pg.get_image_rects(t[0]):
                if r.width > 400:
                    e = doc.extract_image(t[0])
                    cruda = os.path.join(TMP, "cat_%d.%s" % (num, e["ext"]))
                    with open(cruda, "wb") as f:
                        f.write(e["image"])
                    im = Image.open(cruda).convert("RGB")
                    im.thumbnail((1400, 1400), Image.LANCZOS)
                    im.save(os.path.join(DESTINO, "cartas", nombre), "JPEG",
                            quality=82, optimize=True, progressive=True)
                    break
    return equipos


def ajustes_de_colores():
    """COLORES.txt sobreescribe los nombres que salieron del OCR. Se lee si existe.

    Devuelve {numero: (nombre, revisar)}. El renglon que todavia lleva "<- revisar" es un
    nombre que el cliente no ha confirmado: se usa igual, pero el sitio lo sigue marcando.
    Cuando el cliente lo confirme y borre la nota, la marca desaparece. Igual que NOMBRES.txt,
    el archivo se lee de la carpeta del sitio y nunca se reescribe, para no perder lo que el
    cliente haya corregido.
    """
    ruta = os.path.join(DESTINO, "COLORES.txt")
    if not os.path.isfile(ruta):
        return {}
    cambios = {}
    with open(ruta, encoding="utf-8-sig") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "|" not in linea:
                continue
            num, _, nombre = linea.partition("|")
            plano = nombre.rstrip()
            revisar = plano.lower().endswith("<- revisar")
            if revisar:
                plano = plano[:-len("<- revisar")]
            nombre = plano.strip()
            if not nombre:
                continue
            try:
                cambios[int(num.strip())] = (nombre.upper(), revisar)
            except ValueError:
                continue
    return cambios


def cargar_colores():
    """Los 48 colores de la carta, con el nombre impreso que trae cada cuadro."""
    ajustes = ajustes_de_colores()
    salida = []
    for n, (carta, fila, col, hexa, nombre, revisar) in enumerate(COLORES_CARTA, 1):
        if n in ajustes:
            nombre, revisar = ajustes[n]
            if nombre != COLORES_CARTA[n - 1][4]:
                print("   color corregido a mano: %02d  %s" % (n, nombre))
        r, g, b = hex_a_rgb(hexa)
        salida.append({
            "id": n, "hex": hexa, "rgb": [r, g, b],
            "rgb_texto": "RGB(%d, %d, %d)" % (r, g, b),
            "nombre": nombre, "acabado": acabado(nombre), "revisar": revisar,
            "carta": carta, "fila": fila, "col": col,
        })
    return salida


# ------------------------------------------------------------------------- el sitio
# HTML, CSS y JS van como literales y se escriben tal cual, sin pasarles % ni .format: los
# llaves del CSS y del JS se comerian el formato. Lo unico que se inyecta es datos.js.
HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JATH ELECTROESTATIC</title>
<meta name="description" content="Pinturas electrostáticas en polvo, equipos, repuestos y servicios. Arma tu cotización y envíala por WhatsApp.">
<meta name="referrer" content="no-referrer">
<link rel="preload" as="image" href="fotos/escena.jpg" fetchpriority="high">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="favicon-180.png">
<script>
/* Al recargar con F5 el navegador devuelve la pagina al punto donde estaba, y parece que
   no se actualizo nada. Aqui se empieza de nuevo arriba y se limpia la seccion de la
   direccion, para ver los cambios desde el principio. */
(function () {
  try {
    var n = performance.getEntriesByType('navigation')[0];
    if (!n || n.type !== 'reload') return;
    // Se quita la seccion de la direccion: si no, al volver arriba el enlace del menu a esa
    // misma seccion ya no responde (la direccion no cambia y el navegador no salta).
    if (location.hash) {
      try {
        history.replaceState(null, '', location.href.replace(/#.*$/, ''));
      } catch (e) {
        try { location.hash = ''; } catch (e2) {}
      }
    }
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    var raiz = document.documentElement;
    function arriba() {
      var antes = raiz.style.scrollBehavior;
      raiz.style.scrollBehavior = 'auto';
      window.scrollTo(0, 0);
      raiz.style.scrollBehavior = antes;
    }
    arriba();
    document.addEventListener('DOMContentLoaded', arriba);
    window.addEventListener('load', function () {
      arriba();
      requestAnimationFrame(function () { requestAnimationFrame(arriba); });
    });
  } catch (e) {}
})();
</script>
<link rel="stylesheet" href="estilo.css">
</head>
<body>

<header class="cabecera">
  <a class="marca" href="#portada">
    <span class="marca-sigla">JATH</span>
    <span class="marca-nombre">Electroestatic</span>
  </a>
  <nav class="menu">
    <a href="#colores">Colores</a>
    <a href="#equipos">Equipos</a>
    <a href="#servicios">Servicios</a>
    <a href="#trabajos">Trabajos</a>
    <a href="#contacto">Contacto</a>
  </nav>
  <button class="btn btn-rojo" id="abrir-cotizacion">Cotizar</button>
</header>

<main>

  <section class="portada" id="portada">
    <div class="escena">
      <img class="escena-foto" src="fotos/escena.jpg" alt="" aria-hidden="true" fetchpriority="high" decoding="async">
      <div class="escena-velo"></div>
      <div class="escena-chorro" aria-hidden="true">
        <div class="escena-abanico"></div>
        <div class="escena-polvo" id="escena-polvo"></div>
        <img class="escena-pistola" src="fotos/pistola.jpg" alt="" decoding="async">
      </div>
      <!--ESCENA-PIEZA-->
      <p class="escena-pie">Aplicación electrostática en polvo</p>
    </div>
    <p class="antetitulo">Bogotá D.C, Colombia</p>
    <h1>Confíe en los expertos<span>en pintura electrostática</span></h1>
    <p class="bajada" id="portada-bajada"><!--QUIENES--></p>
    <div class="portada-acciones">
      <button class="btn btn-rojo btn-grande" data-ir="colores">Ver carta de colores</button>
      <button class="btn btn-linea btn-grande" data-ir="equipos">Ver productos</button>
    </div>
    <ul class="cifras" id="cifras"></ul>
  </section>

  <section class="bloque" id="quienes">
    <p class="antetitulo">Quiénes somos</p>
    <h2>Aliados estratégicos de la industria</h2>
    <div class="dos-columnas">
      <article class="tarjeta tarjeta-mision" tabindex="0" role="region" aria-label="Misión corporativa">
        <div class="tarjeta-cabecera">
          <div class="tarjeta-icono" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
          </div>
          <div>
            <span class="tarjeta-etiqueta">Nuestro propósito</span>
            <h3>Misión</h3>
          </div>
        </div>
        <p class="parrafo" id="mision"></p>
      </article>
      <article class="tarjeta tarjeta-vision" tabindex="0" role="region" aria-label="Visión corporativa">
        <div class="tarjeta-cabecera">
          <div class="tarjeta-icono" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          </div>
          <div>
            <span class="tarjeta-etiqueta">Hacia dónde vamos</span>
            <h3>Visión</h3>
          </div>
        </div>
        <p class="parrafo" id="vision"></p>
      </article>
    </div>
    <ul class="diferenciadores" id="diferenciadores"></ul>
  </section>

  <section class="bloque" id="trabajos">
    <div class="bloque-cab">
      <p class="antetitulo">Experiencia y Aplicaciones</p>
      <h2>Trabajos en pintura electrostática</h2>
      <p class="parrafo">Más de una década de acabados duraderos en piezas metálicas, perfiles arquitectónicos, autopartes, mobiliario y estructuras industriales.</p>
    </div>
    <div class="galeria-trabajos" id="galeria-trabajos"></div>
  </section>

  <section class="bloque" id="productos">
    <p class="antetitulo">Productos</p>
    <h2>Qué vendemos</h2>
    <p class="parrafo">Pinturas, equipos y repuestos para el recubrimiento electrostático.</p>
    <div class="productos" id="lista-productos"></div>
  </section>

  <section class="bloque" id="colores">
    <p class="antetitulo">Carta de colores</p>
    <h2>Elija sus colores</h2>
    <p class="aviso">
      El color de una pantalla no es el color de una pintura. Antes de decidir, pida una
      muestra física: <a href="#cartas">ver la carta impresa</a>.
    </p>
    <div class="filtros" id="filtros-color"></div>
    <div class="buscador">
      <input type="search" id="buscar-color" placeholder="Buscar por nombre o código, por ejemplo VERDE o A02F2D" autocomplete="off">
    </div>
    <div class="rejilla-colores" id="rejilla-colores"></div>
    <p class="vacio" id="color-vacio" hidden>No hay ningún color con ese código.</p>
  </section>

  <section class="bloque" id="cartas">
    <p class="antetitulo">Carta impresa</p>
    <h2>Así se ven en el papel</h2>
    <p class="parrafo">Estas son las dos cartas tal como se imprimen. El tono en papel es el bueno.</p>
    <div class="cartas">
      <button class="carta" data-carta="cartas/carta-1.jpg"><img src="cartas/carta-1.jpg" width="1070" height="1294" alt="Carta de colores, primera parte" loading="lazy" decoding="async"></button>
      <button class="carta" data-carta="cartas/carta-2.jpg"><img src="cartas/carta-2.jpg" width="1191" height="1400" alt="Carta de colores, segunda parte" loading="lazy" decoding="async"></button>
    </div>
  </section>

  <section class="bloque" id="equipos">
    <p class="antetitulo">Equipos y repuestos</p>
    <h2>Lo que fabricamos y reparamos</h2>
    <div class="filtros" id="filtros-equipo"></div>
    <div class="rejilla-equipos" id="rejilla-equipos"></div>
  </section>

  <section class="bloque" id="servicios">
    <p class="antetitulo">Servicios</p>
    <h2>No solo le vendemos, le acompañamos</h2>
    <div class="servicios" id="lista-servicios"></div>
  </section>

</main>

<footer class="bloque pie-pagina" id="contacto">
  <p class="antetitulo">Contáctenos</p>
  <h2 id="lema">Hablemos</h2>
  <div id="contacto-datos"></div>
</footer>

<a class="wa-fijo" id="wa-fijo" href="#" target="_blank" rel="noopener noreferrer" aria-label="Escribir por WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.127.558 4.126 1.532 5.859L.054 23.428a.5.5 0 0 0 .612.612l5.568-1.478A11.944 11.944 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.891 0-3.667-.523-5.183-1.432l-.361-.215-3.744.993.993-3.744-.216-.361A9.944 9.944 0 0 1 2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
</a>

<div class="barra" id="barra" hidden>
  <button class="barra-info" data-abrir-cotizacion>
    <span class="barra-cuenta" id="barra-cuenta">0</span>
    <span class="barra-texto" id="barra-texto">items en su cotización</span>
  </button>
  <button class="btn btn-rojo" data-abrir-cotizacion>Revisar y enviar</button>
</div>

<div class="velo" id="velo" hidden></div>

<aside class="cajon" id="cajon" hidden aria-label="Su cotización">
  <header class="cajon-cab">
    <h2>Su cotización</h2>
    <button class="cerrar" id="cerrar-cajon" aria-label="Cerrar">&#10005;</button>
  </header>
  <div class="cajon-cuerpo">
    <div id="cajon-vacio" class="cajon-vacio">
      <p>Aún no ha agregado nada.</p>
      <p class="cajon-pista">Toque el <b>+</b> de un color o de un equipo y aparecerá aquí.</p>
    </div>
    <ul class="cajon-lista" id="cajon-lista"></ul>
    <label class="campo">
      <span>Comentario para el asesor</span>
      <textarea id="nota" rows="3" placeholder="Por ejemplo: necesito la entrega en Chía, y una demostración de la pistola."></textarea>
    </label>
    <p class="cajon-aviso">No publicamos precios: se los cotizamos según su proyecto.</p>
    <p class="cajon-aviso" id="cajon-riesgo" hidden>La cotización es una solicitud, no un pedido en firme.</p>
  </div>
  <footer class="cajon-pie">
    <a class="btn btn-rojo" id="boton-whatsapp" href="#" target="_blank" rel="noopener noreferrer">Enviar por WhatsApp</a>
  </footer>
</aside>

<div class="lupa" id="lupa" hidden>
  <div class="velo" data-cerrar-lupa></div>
  <div class="lupa-caja">
    <button class="cerrar lupa-cerrar" data-cerrar-lupa aria-label="Cerrar">&#10005;</button>
    <div class="lupa-color" id="lupa-color"></div>
    <div class="lupa-info">
      <p class="lupa-familia" id="lupa-familia"></p>
      <h3 class="lupa-hex" id="lupa-hex"></h3>
      <p class="lupa-rgb" id="lupa-rgb"></p>
      <p class="lupa-nota" id="lupa-nota"></p>
      <div class="lupa-acciones">
        <button class="btn btn-linea" id="lupa-copiar">Copiar código</button>
        <button class="btn btn-rojo" id="lupa-agrregar">Agregar a la cotización</button>
      </div>
    </div>
  </div>
</div>

<div class="avisos" id="avisos" aria-live="polite"></div>


<div class="cobertura-modal" id="modal-cobertura" hidden>
  <div class="velo" data-cerrar-cobertura></div>
  <div class="cobertura-caja">
    <header class="cobertura-cab">
      <div>
        <span class="cobertura-antetitulo">Logística y Despachos JATH</span>
        <h2>Zonas de Entrega y Cobertura</h2>
      </div>
      <button class="cerrar" data-cerrar-cobertura aria-label="Cerrar">&#10005;</button>
    </header>

    <div class="cobertura-cuerpo">
      <div class="cobertura-tarjetas">
        <div class="cobertura-tarjeta cobertura-tarjeta-local">
          <div class="cobertura-badge">⚡ Entrega el mismo día</div>
          <h3>Bogotá D.C. y Alrededores</h3>
          <p>Despacho inmediato para pedidos confirmados en la mañana. Cobertura directa en la capital y municipios de la Sabana:</p>
          <ul class="cobertura-lista">
            <li>Bogotá D.C. (todas las localidades industriales y comerciales)</li>
            <li>Soacha, Mosquera, Funza, Madrid, Facatativá</li>
            <li>Chía, Cota, Cajicá, Zipaquirá, Tocancipá</li>
          </ul>
          <div class="cobertura-tiempo"><strong>Tiempo estimado:</strong> Entre 2 y 5 horas en el mismo día hábil.</div>
        </div>

        <div class="cobertura-tarjeta cobertura-tarjeta-nacional">
          <div class="cobertura-badge">🇨🇴 Cobertura Nacional</div>
          <h3>Envíos a toda Colombia</h3>
          <p>Despachos diarios de pinturas electrostáticas en polvo, equipos de aplicación y repuestos con embalaje reforzado:</p>
          <ul class="cobertura-lista">
            <li>Medellín, Cali, Barranquilla, Bucaramanga</li>
            <li>Eje Cafetero, Cartagena, Cúcuta, Ibagué, Neiva</li>
            <li>Cualquier municipio con transporte de carga o mensajería</li>
          </ul>
          <div class="cobertura-tiempo"><strong>Tiempo estimado:</strong> 24 a 48 horas según ciudad de destino.</div>
        </div>
      </div>

      <div class="cobertura-mapa-contenedor">
        <div class="cobertura-mapa-cab">
          <h4>Red de distribución desde Bogotá hacia todo el territorio nacional</h4>
          <span class="mapa-leyenda"><i class="pin-pulso"></i> Centro de operaciones (Bogotá D.C.)</span>
        </div>
        <svg class="mapa-colombia" viewBox="0 0 500 450" aria-label="Mapa de cobertura de distribución nacional">
          <defs>
            <radialGradient id="grad-bogota" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#2D8A4E" stop-opacity="0.9"/>
              <stop offset="100%" stop-color="#2D8A4E" stop-opacity="0"/>
            </radialGradient>
            <filter id="glow-pin" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur"/>
              <feComposite in="SourceGraphic" in2="blur" operator="over"/>
            </filter>
          </defs>
          <path class="mapa-silueta" d="M 230 35 C 250 40, 270 50, 280 75 C 290 85, 275 110, 260 120 C 265 140, 290 155, 305 180 C 320 200, 310 230, 295 250 C 310 270, 350 280, 390 285 C 410 320, 370 350, 340 370 C 310 395, 280 435, 265 440 C 250 430, 230 390, 210 370 C 180 340, 160 300, 150 260 C 140 230, 160 210, 175 180 C 180 150, 200 130, 195 100 C 190 70, 210 50, 230 35 Z"/>
          
          <line class="mapa-ruta" x1="240" y1="225" x2="225" y2="70"/>
          <line class="mapa-ruta" x1="240" y1="225" x2="265" y2="155"/>
          <line class="mapa-ruta" x1="240" y1="225" x2="195" y2="175"/>
          <line class="mapa-ruta" x1="240" y1="225" x2="180" y2="270"/>
          <line class="mapa-ruta" x1="240" y1="225" x2="195" y2="225"/>
          <line class="mapa-ruta" x1="240" y1="225" x2="275" y2="245"/>
          <line class="mapa-ruta" x1="240" y1="225" x2="210" y2="305"/>

          <g class="mapa-nodo" transform="translate(225, 70)">
            <circle r="4.5" fill="#0573BC"/>
            <text x="8" y="4" class="mapa-ciudad">Barranquilla / Cartagena</text>
          </g>
          <g class="mapa-nodo" transform="translate(265, 155)">
            <circle r="4.5" fill="#0573BC"/>
            <text x="8" y="4" class="mapa-ciudad">Bucaramanga</text>
          </g>
          <g class="mapa-nodo" transform="translate(195, 175)">
            <circle r="5" fill="#0573BC"/>
            <text x="-8" y="4" text-anchor="end" class="mapa-ciudad">Medellín</text>
          </g>
          <g class="mapa-nodo" transform="translate(195, 225)">
            <circle r="4.5" fill="#0573BC"/>
            <text x="-8" y="4" text-anchor="end" class="mapa-ciudad">Eje Cafetero</text>
          </g>
          <g class="mapa-nodo" transform="translate(180, 270)">
            <circle r="5" fill="#0573BC"/>
            <text x="-8" y="4" text-anchor="end" class="mapa-ciudad">Cali</text>
          </g>
          <g class="mapa-nodo" transform="translate(275, 245)">
            <circle r="4" fill="#0573BC"/>
            <text x="8" y="4" class="mapa-ciudad">Llanos Orientales</text>
          </g>
          <g class="mapa-nodo" transform="translate(210, 305)">
            <circle r="4" fill="#0573BC"/>
            <text x="-8" y="4" text-anchor="end" class="mapa-ciudad">Huila / Tolima</text>
          </g>

          <circle cx="240" cy="225" r="28" fill="url(#grad-bogota)" class="mapa-pulso"/>
          <circle cx="240" cy="225" r="8" fill="#2D8A4E" stroke="#FFFFFF" stroke-width="2.5" filter="url(#glow-pin)"/>
          <circle cx="240" cy="225" r="3" fill="#FFFFFF"/>
          <g transform="translate(240, 212)">
            <rect x="-85" y="-22" width="170" height="20" rx="10" fill="#2D8A4E"/>
            <text x="0" y="-8" text-anchor="middle" fill="#FFFFFF" font-size="10" font-weight="700">★ BOGOTÁ (Mismo Día)</text>
          </g>
        </svg>
      </div>

      <div class="cobertura-pie">
        <a class="btn btn-rojo" target="_blank" rel="noopener noreferrer" id="btn-cobertura-wa">Consultar flete o envío por WhatsApp &rarr;</a>
        <button class="btn btn-linea" data-cerrar-cobertura>Cerrar</button>
      </div>
    </div>
  </div>
</div>
<script src="datos.js"></script>
<script src="app.js"></script>
</body>
</html>
"""


ESTILO = r"""/* JATH Electroestatic - catalogo vivo
   Los tres colores del folleto: crema de fondo, carbon de texto y un solo rojo de acento.
   El sitio esta pensado primero para el celular, porque es como lo van a abrir: desde el
   enlace que les mandan por WhatsApp. */

:root {
  --crema:   #FAF7F0;
  --papel:   #FFFFFF;
  --carbon:  #212121;
  --rojo:    #C1121F;
  --rojo-osc:#8E0C16;
  --linea:   #E5DFD3;
  --gris:    #6E6862;
  --gris-claro:#9A948D;
  --sombra:  0 1px 2px rgba(33,33,33,.05), 0 8px 24px rgba(33,33,33,.06);
  --radio:   14px;
  --ancho:   1120px;
  --barra:   62px;
}

* { box-sizing: border-box; }
[hidden] { display: none !important; }

html { scroll-behavior: smooth; scroll-padding-top: 92px; }

body {
  margin: 0;
  background: var(--crema);
  color: var(--carbon);
  font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  /* 74 px de mas para que el boton fijo de WhatsApp no tape el pie. */
  padding-bottom: calc(var(--barra) + 74px);
}
body.sin-barra { padding-bottom: 74px; }

h1, h2, h3 { line-height: 1.15; margin: 0 0 .5em; letter-spacing: -.02em; font-weight: 700; }
h1 { font-size: clamp(2.1rem, 6.2vw, 4rem); }
h2 { font-size: clamp(1.55rem, 3.6vw, 2.4rem); }
h3 { font-size: 1.06rem; }
p  { margin: 0 0 1em; }
a  { color: var(--rojo); }

.bloque, .portada { max-width: var(--ancho); margin: 0 auto; padding: 0 20px; }
.bloque { padding-top: 76px; padding-bottom: 8px; }

.antetitulo {
  text-transform: uppercase; letter-spacing: .16em; font-size: .74rem;
  font-weight: 700; color: var(--rojo); margin: 0 0 12px;
}
.parrafo { color: var(--gris); max-width: 62ch; }
.dos-columnas { display: grid; gap: 20px; grid-template-columns: 1fr; margin-top: 26px; }
@media (min-width: 760px) { .dos-columnas { grid-template-columns: 1fr 1fr; } }

/* ------------------------------------------------------------------ botones */
.btn {
  font: inherit; font-weight: 600; cursor: pointer;
  border: 1px solid transparent; border-radius: 999px;
  padding: 11px 20px; text-decoration: none; display: inline-block;
  transition: transform .12s ease, background .15s ease, box-shadow .15s ease;
}
.btn:active { transform: translateY(1px); }
.btn-grande { padding: 15px 28px; font-size: 1.02rem; }
.btn-rojo  { background: var(--rojo); color: #fff; }
.btn-rojo:hover { background: var(--rojo-osc); }
.btn-linea { background: transparent; color: var(--carbon); border-color: var(--linea); }
.btn-linea:hover { background: var(--papel); border-color: #D2C9B8; }
.cerrar {
  font: inherit; font-size: 1.1rem; line-height: 1; cursor: pointer;
  background: transparent; border: 0; color: var(--gris); padding: 8px;
}

/* ------------------------------------------------------------------ cabecera */
.cabecera {
  position: sticky; top: 0; z-index: 40;
  display: flex; align-items: center; gap: 18px;
  padding: 11px 20px;
  background: rgba(250,247,240,.88);
  backdrop-filter: saturate(150%) blur(12px);
  border-bottom: 1px solid var(--linea);
}
.marca { display: flex; flex-direction: column; text-decoration: none; color: inherit; margin-right: auto; }
.marca-sigla { font-size: .68rem; letter-spacing: .22em; font-weight: 800; color: var(--rojo); }
.marca-nombre { font-size: .95rem; font-weight: 700; }
.menu { display: flex; gap: 22px; }
.menu a { color: var(--gris); text-decoration: none; font-size: .93rem; font-weight: 600; }
.menu a:hover { color: var(--rojo); }
/* En el celular el menu baja a una segunda linea y se reparte a lo ancho: las secciones
   tienen que verse siempre, no solo en el computador. */
@media (max-width: 899px) {
  .cabecera { flex-wrap: wrap; row-gap: 2px; padding: 9px 18px 0; }
  .menu {
    order: 3; flex: 1 0 100%; gap: 6px;
    justify-content: space-between;
    padding: 2px 0 9px;
  }
  .menu a { font-size: .85rem; padding: 8px 0; }
  html { scroll-padding-top: 120px; }
}

/* ------------------------------------------------------------------ portada */
/* La escena va antes del titulo: la cinta con la pared de la cabina de fondo, la foto real de
   la pistola (la del folleto, ficha 14) disparando un abanico de pintura y, al frente, la reja
   de tubo cuadrado que recibe el chorro. Mide 190 px: la version anterior medía 120 y el
   chorro apenas se leía, pero mas alta que esto empuja el titular fuera del primer
   pantallazo. El fondo lleva un zoom lentisimo para que la cinta no se sienta quieta. */
.escena {
  position: relative; overflow: hidden; isolation: isolate;
  height: 190px; margin: 0 0 28px;
  border: 1px solid var(--linea); border-radius: 12px;
  background: #EFEBE3;
  /* El ancho de la pieza manda: de aqui salen el tamano de la estructura y donde termina el
     chorro, asi que la pintura siempre choca contra la cara de la pieza. */
  --ancho-pieza: 168px;
}

.escena-foto {
  position: absolute; inset: 0; width: 100%; height: 100%;
  object-fit: cover; object-position: 50% 45%;
  animation: deriva 40s ease-in-out infinite alternate;
}
@keyframes deriva {
  from { transform: scale(1.05) translate3d(0, 0, 0); }
  to   { transform: scale(1.13) translate3d(-1.4%, -1%, 0); }
}

/* El velo aclara el fondo para que el titular siga mandando. Con la pared vacia en vez de la
   foto de la cabina se puede bajar: ya no hay nada que tapar y asi la cinta no queda lavada. */
.escena-velo {
  position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(250,247,240,.40) 0%, rgba(250,247,240,.16) 45%,
                           rgba(250,247,240,.28) 100%);
}

/* Todo el chorro cuelga de este punto: a 27% del ancho y 56% del alto sale la pistola hacia
   la izquierda y el abanico hacia la derecha. El chorro no se estira hasta el borde sino que
   se mete 22 px dentro de la pieza, que va encima: asi la pintura choca contra el metal y no
   lo atraviesa. */
.escena-chorro {
  position: absolute; left: 27%; right: calc(4% + var(--ancho-pieza) - 22px);
  top: 56%; height: 0;
}

/* El cono visible: un triangulo con degradado que se abre desde la boquilla hasta la pieza. */
.escena-abanico {
  position: absolute; left: 0; right: 0; top: -76px; height: 152px;
  background:
    linear-gradient(90deg, transparent 0%, rgba(239,235,227,0.3) 60%, rgba(239,235,227,0.85) 100%),
    linear-gradient(180deg,
      rgba(5, 115, 188, 0.32) 0%,
      rgba(0, 168, 150, 0.30) 18%,
      rgba(70, 157, 57, 0.30) 36%,
      rgba(234, 170, 13, 0.34) 54%,
      rgba(226, 83, 39, 0.34) 72%,
      rgba(193, 18, 31, 0.34) 88%,
      rgba(208, 50, 109, 0.32) 100%
    );
  -webkit-mask-image: linear-gradient(90deg, #000 0%, rgba(0,0,0,0.65) 50%, transparent 100%);
  mask-image: linear-gradient(90deg, #000 0%, rgba(0,0,0,0.65) 50%, transparent 100%);
  -webkit-clip-path: polygon(0 50%, 100% 0, 100% 100%);
  clip-path: polygon(0 50%, 100% 0, 100% 100%);
  pointer-events: none;
}

/* La pistola es la foto del folleto, entera y sin recortar. Con multiply su fondo claro se
   funde con la pared que va debajo y no se ve el rectangulo de la foto: solo
   queda la pistola, con su propia sombra. El brightness/contrast sube el blanco de la foto a
   255 para que el fondo no deje un rectangulo apenas mas oscuro, y el translate la corre para
   que la boquilla (96% del ancho y 37% del alto de la foto) caiga justo en el origen del
   chorro; el origen de la rotacion es esa misma boquilla, asi que al inclinarla no se
   despega del chorro. */
.escena-pistola {
  position: absolute; right: 100%; top: 0; width: 210px; height: auto;
  transform: translate(4%, -37%) rotate(-4deg);
  transform-origin: 96% 37%;
  mix-blend-mode: multiply;
  filter: brightness(1.08) contrast(1.06);
  -webkit-mask-image: linear-gradient(90deg, rgba(0,0,0,0) 0, #000 4%, #000 95%, rgba(0,0,0,0) 100%);
  mask-image: linear-gradient(90deg, rgba(0,0,0,0) 0, #000 4%, #000 95%, rgba(0,0,0,0) 100%);
  pointer-events: none;
}

/* La reja que se esta pintando: marco, tres barrotes y un travesano, con las soldaduras y los
   pernos metidos en el dibujo (ver svg_reja). Va despues del chorro para quedar por encima, y
   por eso la pintura se corta en su cara izquierda, que es la que queda teñida de rojo. */
.escena-pieza {
  position: absolute; right: 4%; top: 56%; transform: translateY(-50%);
  width: var(--ancho-pieza); height: calc(var(--ancho-pieza) * .88);
  filter: drop-shadow(0 10px 14px rgba(33,33,33,.32));
  pointer-events: none;
}

/* Las gotas: cada <i> cruza el abanico de 0% a 100% abriendose en cono. Las medidas las pone
   app.js: --x0 el arranque escalonado, --dy la altura final, --dur el tiempo, --ret el retraso
   (en negativo, para que el chorro ya este en marcha al abrir) y --tam el tamano de la gota. */
.escena-polvo { position: absolute; left: 0; right: 0; top: 0; height: 0; }

/* La gota crece un poco al alejarse y se apaga al final, como la nube de pintura. El tamano
   base lo pone --tam y el recorrido vertical --dy, que es media abertura del abanico. */
.escena-polvo i {
  position: absolute; left: 0; top: 0;
  width: calc(4.5px * var(--tam, 1)); height: calc(4.5px * var(--tam, 1));
  border-radius: 50%;
  background: var(--color-gota, var(--rojo));
  box-shadow: 0 0 6px var(--sombra-gota, rgba(193,18,31,.55));
  opacity: 0;
  animation: polvo var(--dur, 2s) linear infinite;
  animation-delay: var(--ret, 0s);
}
@keyframes polvo {
  0%   { transform: translate3d(var(--x0, 0px), 0, 0) scale(.4); opacity: 0; }
  12%  { opacity: .95; }
  55%  { transform: translate3d(calc(var(--recorrido, 600px) * .55 + var(--x0, 0px) / 2), calc(var(--dy, 0px) * .55), 0) scale(1); opacity: .85; }
  100% { transform: translate3d(var(--recorrido, 600px), var(--dy, 0px), 0) scale(1.5); opacity: 0; }
}

/* Cuando la cinta sale de pantalla se congelan sus animaciones: no se gasta bateria moviendo
   gotas que nadie ve. app.js pone la clase al entrar y salir del primer pantallazo. */
.escena-quieta .escena-foto,
.escena-quieta .escena-polvo i { animation-play-state: paused; }

/* El pie va arriba a la derecha y no abajo: abajo a la derecha ahora esta la estructura que se
   pinta, y el rotulo se perderia encima del metal. */
.escena-pie {
  position: absolute; right: 12px; top: 9px; margin: 0;
  font-size: .6rem; text-transform: uppercase; letter-spacing: .14em;
  font-weight: 700; color: #6E6862;
  text-shadow: 0 1px 0 rgba(250,247,240,.9);
}
@media (max-width: 620px) {
  .escena { height: 150px; --ancho-pieza: 112px; }
  .escena-chorro { left: 42%; }
  .escena-abanico { top: -58px; height: 116px; }
  .escena-pistola { width: 150px; }
  .escena-pie { font-size: .54rem; letter-spacing: .1em; right: 8px; }
}

.portada { padding-top: 34px; padding-bottom: 12px; }
.portada .antetitulo { margin-bottom: 18px; }
.portada h1 span { display: block; color: var(--rojo); }
.portada .bajada { font-size: 1.1rem; color: var(--gris); max-width: 54ch; }
.portada-acciones { display: flex; flex-wrap: wrap; gap: 12px; margin: 26px 0 34px; }
.cifras {
  list-style: none; display: grid; grid-template-columns: repeat(2, 1fr); gap: 1px;
  padding: 0; margin: 30px 0 0; background: var(--linea);
  border: 1px solid var(--linea); border-radius: var(--radio); overflow: hidden;
  box-shadow: var(--sombra);
}
@media (min-width: 720px) { .cifras { grid-template-columns: repeat(4, 1fr); } }
.cifras li {
  position: relative; background: var(--papel); padding: 22px 18px 18px;
  cursor: pointer; user-select: none;
  display: flex; flex-direction: column;
  transition: transform .18s cubic-bezier(.2,.8,.4,1), box-shadow .2s ease, background .2s ease;
}
.cifras li:hover {
  transform: translateY(-4px);
  z-index: 2;
  box-shadow: 0 10px 24px var(--cifra-sombra, rgba(33,33,33,.12));
  background: linear-gradient(180deg, rgba(255,255,255,.98) 0%, rgba(250,247,240,.6) 100%);
}
.cifras li:active,
.cifras li.cifra-activa {
  transform: translateY(-1px) scale(0.98);
  box-shadow: 0 4px 12px var(--cifra-sombra, rgba(33,33,33,.14));
}
.cifras li:focus-visible {
  outline: 2px solid var(--cifra-color, var(--rojo));
  outline-offset: -2px;
  z-index: 3;
}
.cifras li:nth-child(1) { --cifra-color: #0573BC; --cifra-sombra: rgba(5,115,188,.24); }
.cifras li:nth-child(2) { --cifra-color: #2D8A4E; --cifra-sombra: rgba(45,138,78,.24); }
.cifras li:nth-child(3) { --cifra-color: #D96B27; --cifra-sombra: rgba(217,107,39,.24); }
.cifras li:nth-child(4) { --cifra-color: #C1121F; --cifra-sombra: rgba(193,18,31,.24); }
.cifras li::after {
  content: ""; position: absolute; top: 0; left: 18px; width: 38px; height: 3px;
  background: var(--cifra-color, var(--rojo)); border-radius: 0 0 3px 3px;
  transition: width .2s ease;
}
.cifras li:hover::after {
  width: 56px;
}
.cifras b {
  display: block; font-size: clamp(1.9rem, 5vw, 2.5rem); line-height: 1;
  font-weight: 800; color: var(--cifra-color, var(--carbon)); letter-spacing: -.03em;
  font-variant-numeric: tabular-nums;
  transition: transform .18s ease;
}
.cifras li:hover b {
  transform: scale(1.04);
  transform-origin: left bottom;
}
.cifras span {
  display: block; margin-top: 7px; font-size: .7rem; text-transform: uppercase;
  letter-spacing: .13em; font-weight: 700; color: var(--gris);
  margin-bottom: auto;
}
.cifra-accion {
  display: inline-flex; align-items: center; gap: 4px;
  margin-top: 14px; font-size: .74rem; font-weight: 600;
  color: var(--cifra-color, var(--carbon));
  opacity: .78;
  transition: opacity .15s ease, transform .15s ease;
}
.cifra-accion i {
  font-style: normal; font-size: .88rem; line-height: 1;
  transition: transform .2s ease;
}
.cifras li:hover .cifra-accion {
  opacity: 1;
}
.cifras li:hover .cifra-accion i {
  transform: translateX(4px);
}

/* ------------------------------------------------------------------ tarjetas (Misión y Visión) */
.tarjeta {
  position: relative;
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: var(--radio);
  padding: 26px 24px;
  box-shadow: var(--sombra);
  transition: transform .22s cubic-bezier(.2,.8,.4,1), box-shadow .22s ease, border-color .22s ease;
  overflow: hidden;
}
.tarjeta::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px;
  background: var(--linea);
  transition: height .2s ease;
}
.tarjeta-mision {
  --tarjeta-color: #0573BC;
  --tarjeta-sombra: rgba(5, 115, 188, 0.16);
}
.tarjeta-mision::before {
  background: linear-gradient(90deg, #0573BC, #00A896);
}
.tarjeta-vision {
  --tarjeta-color: #2D8A4E;
  --tarjeta-sombra: rgba(45, 138, 78, 0.16);
}
.tarjeta-vision::before {
  background: linear-gradient(90deg, #2D8A4E, #84CC16);
}
.tarjeta:hover {
  transform: translateY(-4px);
  border-color: var(--tarjeta-color, #D2C9B8);
  box-shadow: 0 14px 32px var(--tarjeta-sombra, rgba(33,33,33,.12));
}
.tarjeta:hover::before {
  height: 6px;
}
.tarjeta-cabecera {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 16px;
}
.tarjeta-icono {
  width: 44px; height: 44px; border-radius: 12px;
  display: grid; place-items: center;
  flex-shrink: 0;
  transition: transform .25s ease;
}
.tarjeta-mision .tarjeta-icono {
  background: rgba(5, 115, 188, 0.1);
  color: #0573BC;
}
.tarjeta-vision .tarjeta-icono {
  background: rgba(45, 138, 78, 0.1);
  color: #2D8A4E;
}
.tarjeta:hover .tarjeta-icono {
  transform: scale(1.1) rotate(4deg);
}
.tarjeta-etiqueta {
  display: block; font-size: .68rem; text-transform: uppercase;
  letter-spacing: .14em; font-weight: 700; color: var(--tarjeta-color, var(--gris));
  margin-bottom: 2px;
}
.tarjeta h3 {
  margin: 0; font-size: 1.3rem; color: var(--carbon);
}
.tarjeta .parrafo {
  line-height: 1.62; font-size: .95rem; margin: 0;
}

/* ------------------------------------------------------------------ diferenciadores */
.diferenciadores {
  list-style: none; display: grid; gap: 14px; padding: 0; margin: 26px 0 0;
  grid-template-columns: 1fr;
}
@media (min-width: 680px) {
  .diferenciadores { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 960px) {
  .diferenciadores { grid-template-columns: repeat(4, 1fr); }
}

.diferenciadores li {
  position: relative;
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: var(--radio);
  padding: 20px 18px;
  cursor: pointer; user-select: none;
  display: flex; flex-direction: column;
  transition: transform .2s cubic-bezier(.2,.8,.4,1), border-color .2s ease, box-shadow .2s ease, background .2s ease;
  box-shadow: var(--sombra);
  overflow: hidden;
}

.diferenciadores li:nth-child(1) { --dif-color: #C1121F; --dif-sombra: rgba(193,18,31,.20); --dif-fondo: rgba(193,18,31,.08); }
.diferenciadores li:nth-child(2) { --dif-color: #0573BC; --dif-sombra: rgba(5,115,188,.20); --dif-fondo: rgba(5,115,188,.08); }
.diferenciadores li:nth-child(3) { --dif-color: #D96B27; --dif-sombra: rgba(217,107,39,.20); --dif-fondo: rgba(217,107,39,.08); }
.diferenciadores li:nth-child(4) { --dif-color: #2D8A4E; --dif-sombra: rgba(45,138,78,.20); --dif-fondo: rgba(45,138,78,.08); }

.diferenciadores li::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
  background: var(--dif-color, var(--rojo));
  opacity: .85;
  transition: width .2s ease, opacity .2s ease;
}

.diferenciadores li:hover {
  transform: translateY(-4px);
  border-color: var(--dif-color, var(--linea));
  box-shadow: 0 12px 28px var(--dif-sombra, rgba(33,33,33,.12));
  background: linear-gradient(180deg, #FFFFFF 0%, rgba(250,247,240,.75) 100%);
}

.diferenciadores li:hover::before {
  width: 6px;
  opacity: 1;
}

.diferenciadores li:active,
.diferenciadores li.diferenciador-activo {
  transform: translateY(-1px) scale(0.98);
}

.diferenciadores li:focus-visible {
  outline: 2px solid var(--dif-color, var(--rojo));
  outline-offset: -2px;
}

.dif-cabecera {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}

.dif-icono {
  width: 40px; height: 40px; border-radius: 10px;
  display: grid; place-items: center;
  background: var(--dif-fondo, rgba(193,18,31,.08));
  color: var(--dif-color, var(--rojo));
  flex-shrink: 0;
  transition: transform .25s ease, background .25s ease;
}

.diferenciadores li:hover .dif-icono {
  transform: scale(1.12) rotate(3deg);
}

.dif-numero {
  font-size: .78rem; font-weight: 800; letter-spacing: .08em;
  color: var(--dif-color, var(--gris-claro));
  opacity: .65;
}

.dif-titulo {
  display: block; font-size: .98rem; font-weight: 700;
  color: var(--carbon); line-height: 1.25;
  margin-bottom: 4px;
}

.dif-desc {
  display: block; font-weight: 400; color: var(--gris);
  font-size: .84rem; line-height: 1.35;
  margin-top: auto;
}

.dif-pista {
  display: inline-flex; align-items: center; gap: 4px;
  margin-top: 10px; font-size: .72rem; font-weight: 600;
  color: var(--dif-color, var(--carbon));
  opacity: 0;
  transform: translateY(4px);
  transition: opacity .18s ease, transform .18s ease;
}

.diferenciadores li:hover .dif-pista {
  opacity: .95;
  transform: translateY(0);
}

.aviso { background: #FBF3E2; border: 1px solid #EBDCBE; border-left: 3px solid #D9A21B; border-radius: 8px; padding: 12px 15px; font-size: .9rem; color: #6B5423; }
.vacio { color: var(--gris); padding: 24px 0; }

/* ------------------------------------------------------------------ filtros */
.filtros { display: flex; flex-wrap: wrap; gap: 8px; margin: 22px 0 14px; }
.chip {
  font: inherit; font-size: .86rem; font-weight: 600; cursor: pointer;
  background: var(--papel); color: var(--gris);
  border: 1px solid var(--linea); border-radius: 999px; padding: 7px 14px;
}
.chip:hover { border-color: #CFC5B2; }
.chip[aria-pressed="true"] { background: var(--carbon); border-color: var(--carbon); color: #fff; }
.buscador { margin: 0 0 20px; }
.buscador input {
  font: inherit; width: 100%; max-width: 340px; padding: 11px 15px;
  border: 1px solid var(--linea); border-radius: 10px; background: var(--papel); color: var(--carbon);
}
.buscador input:focus { outline: 2px solid var(--rojo); outline-offset: 1px; }

/* ------------------------------------------------------------------ colores */
.rejilla-colores { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)); }
.muestra {
  background: var(--papel); border: 1px solid var(--linea); border-radius: 12px;
  overflow: hidden; box-shadow: var(--sombra);
}
.muestra-color { height: 104px; border-bottom: 1px solid var(--linea); }
.muestra-datos { padding: 9px 10px 11px; }
.muestra-nombre { font-weight: 700; font-size: .82rem; line-height: 1.25; margin-bottom: 3px; }
.muestra-hex { font: 600 .72rem/1.2 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; letter-spacing: .02em; color: var(--gris-claro); }
.muestra-revisar { font-size: .64rem; color: var(--rojo); margin: 2px 0 6px; }
.muestra-acciones { display: flex; gap: 6px; }
.muestra-acciones button {
  font: inherit; font-size: .78rem; font-weight: 600; cursor: pointer;
  border: 1px solid var(--linea); background: var(--crema); color: var(--carbon);
  border-radius: 8px; padding: 5px 8px; flex: 1;
}
.muestra-acciones .agregar { background: var(--carbon); border-color: var(--carbon); color: #fff; }
.muestra-acciones .agregar:hover { background: #000; }
.muestra-elegida { border-color: var(--rojo); box-shadow: 0 0 0 2px var(--rojo) inset; }

/* ------------------------------------------------------------------ cartas */
.cartas { display: grid; gap: 16px; grid-template-columns: 1fr; margin-top: 20px; }
@media (min-width: 780px) { .cartas { grid-template-columns: 1fr 1fr; } }
.carta { padding: 0; border: 1px solid var(--linea); border-radius: var(--radio); overflow: hidden; background: var(--papel); cursor: zoom-in; box-shadow: var(--sombra); }
.carta img { display: block; width: 100%; height: auto; }

/* ------------------------------------------------------------------ equipos */
.rejilla-equipos { display: grid; gap: 14px; grid-template-columns: repeat(auto-fill, minmax(198px, 1fr)); }
.equipo { background: var(--papel); border: 1px solid var(--linea); border-radius: var(--radio); overflow: hidden; box-shadow: var(--sombra); display: flex; flex-direction: column; }
.equipo-foto { background: var(--crema); aspect-ratio: 1 / 1; }
.equipo-foto img { width: 100%; height: 100%; object-fit: contain; display: block; }
.equipo-cuerpo { padding: 11px 12px 13px; display: flex; flex-direction: column; flex: 1; }
.equipo-cat { font-size: .68rem; text-transform: uppercase; letter-spacing: .1em; color: var(--rojo); font-weight: 700; }
.equipo-nombre { font-weight: 600; font-size: .96rem; margin: 4px 0 10px; }
.equipo-acciones { display: flex; gap: 6px; margin-top: auto; }
.equipo-acciones button {
  font: inherit; font-size: .8rem; font-weight: 600; cursor: pointer;
  border: 1px solid var(--linea); background: var(--crema); color: var(--carbon);
  border-radius: 8px; padding: 7px 6px; flex: 1;
}
.equipo-acciones .agregar { background: var(--carbon); border-color: var(--carbon); color: #fff; }
.equipo-acciones .agregar:hover { background: #000; }
.provisional { font-size: .68rem; color: var(--gris-claro); margin-top: -6px; margin-bottom: 10px; }

/* ------------------------------------------------------------------ servicios */
/* ------------------------------------------------------------------ productos */
.productos {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr;
  margin-top: 28px;
}
@media (min-width: 700px) { .productos { grid-template-columns: repeat(3, 1fr); } }

.producto {
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: var(--radio);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: relative;
  overflow: hidden;
  cursor: default;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  box-shadow: var(--sombra);
}
.producto::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: var(--prod-color, var(--rojo));
  border-radius: var(--radio) var(--radio) 0 0;
}
.producto:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 8px rgba(33,33,33,.06), 0 16px 40px rgba(33,33,33,.10);
  border-color: var(--prod-color, var(--rojo));
}

/* Cabecera: icono circular + etiqueta de categoria */
.producto-cab {
  display: flex;
  align-items: center;
  gap: 12px;
}
.producto-icono {
  width: 48px; height: 48px;
  border-radius: 12px;
  background: var(--prod-fondo, rgba(193,18,31,.07));
  border: 1px solid var(--prod-sombra, rgba(193,18,31,.18));
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: var(--prod-color, var(--rojo));
  transition: background .18s ease, color .18s ease;
}
.producto:hover .producto-icono {
  background: var(--prod-color, var(--rojo));
  color: #fff;
}
.producto-etiqueta {
  font-size: .71rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--prod-color, var(--rojo));
  background: var(--prod-fondo, rgba(193,18,31,.07));
  border: 1px solid var(--prod-sombra, rgba(193,18,31,.18));
  border-radius: 999px;
  padding: 3px 10px;
}

/* Titulo */
.producto-titulo {
  font-size: 1.04rem;
  margin: 0;
  line-height: 1.25;
}

/* Lista de caracteristicas con punto de color */
.producto-chips {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 7px;
  flex: 1;
}
.producto-chip {
  font-size: .875rem;
  color: var(--gris);
  padding-left: 18px;
  position: relative;
  line-height: 1.4;
}
.producto-chip::before {
  content: '';
  position: absolute;
  left: 0; top: 7px;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--prod-color, var(--rojo));
  opacity: .55;
}

/* Pie con boton de accion */
.producto-pie {
  margin-top: auto;
  padding-top: 6px;
}
.btn-producto {
  font: inherit;
  font-size: .875rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--prod-sombra, rgba(193,18,31,.25));
  border-radius: 999px;
  padding: 9px 18px;
  background: var(--prod-fondo, rgba(193,18,31,.07));
  color: var(--prod-color, var(--rojo));
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background .15s ease, color .15s ease, transform .12s ease;
  width: 100%;
  justify-content: center;
}
.btn-producto:hover {
  background: var(--prod-color, var(--rojo));
  color: #fff;
  border-color: var(--prod-color, var(--rojo));
}
.btn-producto:active { transform: translateY(1px); }

/* ------------------------------------------------------------------ servicios */
.servicios {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr;
  margin-top: 28px;
}
@media (min-width: 600px) { .servicios { grid-template-columns: 1fr 1fr; } }

.servicio {
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: var(--radio);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: relative;
  overflow: hidden;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  box-shadow: var(--sombra);
}
.servicio::after {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: var(--srv-color, var(--rojo));
  border-radius: var(--radio) 0 0 var(--radio);
}
.servicio:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(33,33,33,.06), 0 14px 36px rgba(33,33,33,.10);
  border-color: var(--srv-color, var(--rojo));
}

/* Cabecera: numero + icono + etiqueta */
.servicio-cab {
  display: flex;
  align-items: center;
  gap: 10px;
}
.servicio-numero {
  font-size: .68rem;
  font-weight: 800;
  letter-spacing: .06em;
  color: var(--srv-color, var(--rojo));
  opacity: .5;
  min-width: 22px;
}
.servicio-icono {
  width: 44px; height: 44px;
  border-radius: 11px;
  background: var(--srv-fondo, rgba(193,18,31,.07));
  border: 1px solid var(--srv-sombra, rgba(193,18,31,.20));
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: var(--srv-color, var(--rojo));
  transition: background .18s ease, color .18s ease;
}
.servicio:hover .servicio-icono {
  background: var(--srv-color, var(--rojo));
  color: #fff;
}
.servicio-etiqueta {
  font-size: .69rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--srv-color, var(--rojo));
  background: var(--srv-fondo, rgba(193,18,31,.07));
  border: 1px solid var(--srv-sombra, rgba(193,18,31,.20));
  border-radius: 999px;
  padding: 3px 10px;
}

/* Titulo */
.servicio-titulo {
  font-size: 1.02rem;
  margin: 0;
  line-height: 1.3;
}

/* Lista de detalles con punto de color */
.servicio-chips {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}
.servicio-chip {
  font-size: .875rem;
  color: var(--gris);
  padding-left: 17px;
  position: relative;
  line-height: 1.4;
}
.servicio-chip::before {
  content: '';
  position: absolute;
  left: 0; top: 7px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--srv-color, var(--rojo));
  opacity: .5;
}

/* Pie con boton */
.servicio-pie {
  margin-top: auto;
  padding-top: 4px;
}
.btn-servicio {
  font: inherit;
  font-size: .85rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--srv-sombra, rgba(193,18,31,.25));
  border-radius: 999px;
  padding: 9px 18px;
  background: var(--srv-fondo, rgba(193,18,31,.07));
  color: var(--srv-color, var(--rojo));
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  transition: background .15s ease, color .15s ease, transform .12s ease;
  width: 100%;
  justify-content: center;
}
.btn-servicio:hover {
  background: var(--srv-color, var(--rojo));
  color: #fff;
  border-color: var(--srv-color, var(--rojo));
}
.btn-servicio:active { transform: translateY(1px); }

/* ------------------------------------------------------------------ contacto */

/* Panel de datos */
.contacto-datos-principal {
  display: grid;
  gap: 10px;
}
@media (min-width: 600px) {
  .contacto-datos-principal { grid-template-columns: repeat(3, 1fr); }
}

/* Tarjeta individual de dato */
.dato {
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
  box-shadow: var(--sombra);
}
.dato:hover {
  border-color: var(--dato-color, var(--rojo));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33,33,33,.08);
}
.dato-cab {
  display: flex;
  align-items: center;
  gap: 7px;
}
.dato-icono {
  display: flex;
  align-items: center;
  color: var(--dato-color, var(--rojo));
  flex-shrink: 0;
}
.dato-rotulo {
  font-size: .70rem;
  text-transform: uppercase;
  letter-spacing: .10em;
  color: var(--gris-claro);
  font-weight: 700;
}
.dato-valor {
  font-size: 1rem;
  font-weight: 600;
  color: var(--carbon);
  text-decoration: none;
  word-break: break-all;
}
a.dato-valor:hover { color: var(--dato-color, var(--rojo)); }

/* Titulo de redes */
.contacto-redes-titulo {
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .14em;
  color: var(--gris-claro);
  margin: 4px 0 2px;
}

/* Grid de redes sociales */
.contacto-redes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
@media (min-width: 500px) { .contacto-redes { grid-template-columns: repeat(4, 1fr); } }

.red-social {
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: 12px;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  color: var(--carbon);
  transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease, background .18s ease;
  cursor: pointer;
  box-shadow: var(--sombra);
}
.red-social:hover {
  background: var(--red-color, var(--rojo));
  border-color: var(--red-color, var(--rojo));
  color: #fff;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(33,33,33,.14);
}
.red-icono {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px; height: 36px;
  border-radius: 9px;
  background: rgba(0,0,0,.05);
  color: var(--red-color, var(--carbon));
  transition: background .18s ease, color .18s ease;
}
.red-social:hover .red-icono {
  background: rgba(255,255,255,.20);
  color: #fff;
}
.red-nombre {
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .04em;
}
.red-handle {
  font-size: .71rem;
  color: var(--gris);
  text-align: center;
  word-break: break-all;
}
.red-social:hover .red-handle { color: rgba(255,255,255,.8); }

/* ------------------------------------------------------------------ pie */
/* El pie ES la seccion de contacto: mismo ancho que las secciones, con la linea
   arriba y aire abajo. */
.pie-pagina {
  border-top: 1px solid var(--linea);
  margin-top: 80px;
  padding-top: 56px;
  padding-bottom: 48px;
}

/* ------------------------------------------------------------------ whatsapp fijo */
/* Sube solo cuando aparece la barra del carrito, para no taparla. */
.wa-fijo {
  position: fixed;
  right: 20px;
  bottom: calc(18px + var(--barra));
  z-index: 44;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: #25D366;
  color: #fff;
  display: grid;
  place-items: center;
  box-shadow: 0 8px 22px rgba(33,33,33,.26);
  transition: transform .15s ease, background .15s ease, box-shadow .15s ease;
}
body.sin-barra .wa-fijo { bottom: 18px; }
.wa-fijo:hover { background: #1EBE5A; transform: translateY(-2px); box-shadow: 0 10px 26px rgba(33,33,33,.32); }
.wa-fijo:active { transform: translateY(0); }
.wa-fijo svg { width: 30px; height: 30px; display: block; }
@media (max-width: 620px) {
  .wa-fijo { right: 14px; width: 52px; height: 52px; }
  .wa-fijo svg { width: 27px; height: 27px; }
}

/* ------------------------------------------------------------------ barra inferior */
.barra {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 45;
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px calc(10px + env(safe-area-inset-bottom));
  background: rgba(33,33,33,.97); color: #fff;
  box-shadow: 0 -4px 20px rgba(33,33,33,.18);
}
.barra-info { display: flex; align-items: center; gap: 10px; background: transparent; border: 0; color: #fff; font: inherit; cursor: pointer; margin-right: auto; text-align: left; padding: 4px; }
.barra-cuenta { background: var(--rojo); color: #fff; border-radius: 999px; min-width: 28px; height: 28px; display: grid; place-items: center; font-weight: 700; font-size: .9rem; padding: 0 8px; }
.barra-texto { font-size: .88rem; color: #E8E2D6; }
.barra .btn-rojo { background: var(--rojo); }
.barra .btn-rojo:hover { background: #E0252F; }
.barra .btn-linea { color: #fff; border-color: #4A453F; }

/* ------------------------------------------------------------------ capas */
.velo { position: fixed; inset: 0; z-index: 50; background: rgba(33,33,33,.55); backdrop-filter: blur(2px); }

.cajon {
  position: fixed; z-index: 60; background: var(--crema);
  display: flex; flex-direction: column;
  left: 0; right: 0; bottom: 0; max-height: 88vh; border-radius: 18px 18px 0 0;
  box-shadow: 0 -10px 40px rgba(33,33,33,.25);
}
@media (min-width: 780px) {
  .cajon { left: auto; top: 0; width: 430px; max-height: none; border-radius: 0; box-shadow: -10px 0 40px rgba(33,33,33,.2); }
}
.cajon-cab { display: flex; align-items: center; padding: 16px 18px; border-bottom: 1px solid var(--linea); }
.cajon-cab h2 { font-size: 1.14rem; margin: 0; }
.cajon-cab .cerrar { margin-left: auto; }
.cajon-cuerpo { flex: 1; overflow-y: auto; padding: 14px 18px 18px; }
.cajon-vacio { text-align: center; padding: 40px 10px; color: var(--gris); }
.cajon-pista { font-size: .88rem; color: var(--gris-claro); }
.cajon-lista { list-style: none; margin: 0 0 18px; padding: 0; display: flex; flex-direction: column; gap: 9px; }
.cajon-lista li { display: flex; align-items: center; gap: 11px; background: var(--papel); border: 1px solid var(--linea); border-radius: 10px; padding: 9px 11px; }
.cajon-muestra { width: 38px; height: 38px; border-radius: 7px; border: 1px solid var(--linea); flex: none; }
.cajon-foto { width: 38px; height: 38px; object-fit: contain; background: var(--crema); border-radius: 7px; flex: none; }
.cajon-txt { flex: 1; min-width: 0; }
.cajon-nom { font-weight: 600; font-size: .92rem; }
.cajon-det { font-size: .76rem; color: var(--gris-claro); }
.cantidad { display: flex; align-items: center; gap: 2px; flex: none; }
.cantidad button { font: inherit; width: 28px; height: 28px; border: 1px solid var(--linea); background: var(--crema); border-radius: 7px; cursor: pointer; color: var(--carbon); font-weight: 700; }
.cantidad span { min-width: 24px; text-align: center; font-weight: 700; font-size: .92rem; }
.cajon-quitar { font: inherit; font-size: 1rem; background: transparent; border: 0; color: var(--gris-claro); cursor: pointer; padding: 4px; flex: none; }
.cajon-quitar:hover { color: var(--rojo); }
.campo { display: block; margin-bottom: 14px; }
.campo span { display: block; font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--gris); margin-bottom: 6px; }
.campo textarea { font: inherit; width: 100%; padding: 10px 12px; border: 1px solid var(--linea); border-radius: 10px; background: var(--papel); resize: vertical; color: var(--carbon); }
.campo textarea:focus { outline: 2px solid var(--rojo); outline-offset: 1px; }
.cajon-aviso { font-size: .8rem; color: var(--gris-claro); margin: 0 0 8px; }
.cajon-pie { display: flex; gap: 10px; padding: 14px 18px calc(14px + env(safe-area-inset-bottom)); border-top: 1px solid var(--linea); background: var(--crema); }
.cajon-pie .btn { flex: 1; text-align: center; }

/* ------------------------------------------------------------------ lupa de color */
.lupa { position: fixed; inset: 0; z-index: 60; display: grid; place-items: center; padding: 20px; }
.lupa-caja {
  position: relative; z-index: 61; background: var(--crema);
  border-radius: 16px; overflow: hidden; width: 100%; max-width: 460px;
  box-shadow: 0 20px 60px rgba(33,33,33,.3); max-height: 90vh; overflow-y: auto;
}
.lupa-cerrar { position: absolute; top: 8px; right: 8px; z-index: 2; background: rgba(250,247,240,.85); border-radius: 999px; }
.lupa-color { height: 200px; border-bottom: 1px solid var(--linea); }
.lupa-info { padding: 20px; }
.lupa-familia { font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; color: var(--rojo); font-weight: 700; margin: 0 0 6px; }
.lupa-hex { font: 700 1.6rem/1.1 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; margin: 0 0 4px; }
.lupa-rgb { color: var(--gris); margin: 0 0 12px; font-size: .94rem; }
.lupa-nota { font-size: .84rem; color: var(--gris-claro); margin: 0 0 16px; }
.lupa-acciones { display: flex; flex-wrap: wrap; gap: 10px; }
.lupa-acciones .btn { flex: 1; text-align: center; min-width: 150px; }

/* ------------------------------------------------------------------ avisos */
.avisos { position: fixed; left: 50%; bottom: calc(var(--barra) + 16px); transform: translateX(-50%); z-index: 70; display: flex; flex-direction: column; gap: 8px; align-items: center; pointer-events: none; }
.aviso-flotante { background: var(--carbon); color: #fff; padding: 11px 18px; border-radius: 999px; font-size: .88rem; font-weight: 600; box-shadow: 0 8px 24px rgba(33,33,33,.28); }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  * { transition: none !important; }
  /* La escena se queda quieta y con el polvo quieto: si alguien pidio menos movimiento, no se
     le muestra ni el zoom de la foto ni el chorro. */
  .escena-foto { animation: none; transform: scale(1.07); }
  .escena-polvo { display: none; }
}

/* ------------------------------------------------------------------ galería de trabajos */
.galeria-trabajos {
  display: grid; gap: 20px; grid-template-columns: 1fr;
  margin-top: 26px;
}
@media (min-width: 600px) {
  .galeria-trabajos { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 980px) {
  .galeria-trabajos { grid-template-columns: repeat(3, 1fr); }
}

.tarjeta-trabajo {
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: var(--radio);
  overflow: hidden;
  box-shadow: var(--sombra);
  display: flex; flex-direction: column;
  transition: transform .22s cubic-bezier(.2,.8,.4,1), box-shadow .22s ease, border-color .22s ease;
}
.tarjeta-trabajo:hover {
  transform: translateY(-5px);
  border-color: #D2C9B8;
  box-shadow: 0 16px 36px rgba(33,33,33,.12);
}

.trabajo-foto-wrap {
  position: relative; width: 100%; aspect-ratio: 16 / 11;
  background: #181A1D; overflow: hidden;
}
.trabajo-foto-wrap img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform .4s ease;
}
.tarjeta-trabajo:hover .trabajo-foto-wrap img {
  transform: scale(1.05);
}
.trabajo-badge {
  position: absolute; top: 10px; right: 10px;
  font-size: .62rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em;
  background: rgba(22,24,28,.82); color: #FFF;
  padding: 4px 9px; border-radius: 999px;
  backdrop-filter: blur(4px); border: 1px solid rgba(255,255,255,.15);
}

.trabajo-info {
  padding: 18px 20px;
  display: flex; flex-direction: column; flex: 1;
}
.trabajo-categoria {
  font-size: .68rem; text-transform: uppercase; letter-spacing: .12em;
  font-weight: 700; color: var(--rojo); margin-bottom: 4px;
}
.trabajo-titulo {
  font-size: 1.06rem; font-weight: 700; color: var(--carbon); margin: 0;
}

/* ------------------------------------------------------------------ modal de cobertura */
.cobertura-modal {
  position: fixed; inset: 0; z-index: 60;
  display: grid; place-items: center; padding: 20px;
}
.cobertura-caja {
  position: relative; z-index: 61; background: var(--crema);
  border-radius: 18px; width: 100%; max-width: 820px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 20px 60px rgba(33,33,33,.3);
  display: flex; flex-direction: column;
}
.cobertura-cab {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 22px 24px 16px; border-bottom: 1px solid var(--linea);
  position: sticky; top: 0; background: var(--crema); z-index: 2;
}
.cobertura-antetitulo {
  font-size: .72rem; text-transform: uppercase; letter-spacing: .14em;
  font-weight: 700; color: #2D8A4E; display: block; margin-bottom: 2px;
}
.cobertura-cab h2 {
  margin: 0; font-size: 1.35rem; color: var(--carbon);
}

.cobertura-cuerpo {
  padding: 22px 24px;
}
.cobertura-tarjetas {
  display: grid; gap: 16px; grid-template-columns: 1fr;
  margin-bottom: 20px;
}
@media (min-width: 680px) {
  .cobertura-tarjetas { grid-template-columns: 1fr 1fr; }
}

.cobertura-tarjeta {
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: 14px;
  padding: 20px;
  box-shadow: var(--sombra);
  position: relative;
}
.cobertura-tarjeta-local {
  border-top: 4px solid #2D8A4E;
}
.cobertura-tarjeta-nacional {
  border-top: 4px solid #0573BC;
}
.cobertura-badge {
  display: inline-block; font-size: .7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .08em;
  padding: 3px 10px; border-radius: 999px; margin-bottom: 10px;
}
.cobertura-tarjeta-local .cobertura-badge {
  background: rgba(45,138,78,.12); color: #2D8A4E;
}
.cobertura-tarjeta-nacional .cobertura-badge {
  background: rgba(5,115,188,.12); color: #0573BC;
}
.cobertura-tarjeta h3 {
  margin: 0 0 8px; font-size: 1.15rem; color: var(--carbon);
}
.cobertura-tarjeta p {
  font-size: .86rem; color: var(--gris); line-height: 1.45; margin: 0 0 10px;
}
.cobertura-lista {
  list-style: none; padding: 0; margin: 0 0 12px; font-size: .82rem; color: var(--carbon);
}
.cobertura-lista li {
  position: relative; padding-left: 16px; margin-bottom: 4px;
}
.cobertura-lista li::before {
  content: "•"; position: absolute; left: 2px; color: var(--rojo); font-weight: 700;
}
.cobertura-tiempo {
  font-size: .8rem; padding: 8px 12px; background: rgba(250,247,240,.9);
  border-radius: 8px; color: var(--gris);
}
.cobertura-tiempo strong {
  color: var(--carbon);
}

.cobertura-mapa-contenedor {
  background: var(--papel);
  border: 1px solid var(--linea);
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 20px;
}
.cobertura-mapa-cab {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  margin-bottom: 12px; gap: 8px;
}
.cobertura-mapa-cab h4 {
  margin: 0; font-size: .92rem; color: var(--carbon);
}
.mapa-leyenda {
  font-size: .75rem; color: var(--gris); display: flex; align-items: center; gap: 6px;
}
.pin-pulso {
  width: 8px; height: 8px; border-radius: 50%; background: #2D8A4E; display: inline-block;
  box-shadow: 0 0 0 4px rgba(45,138,78,.25);
}

.mapa-colombia {
  width: 100%; max-height: 290px; display: block; margin: 0 auto;
}
.mapa-silueta {
  fill: #F5EFEB; stroke: #D8CEC4; stroke-width: 1.5;
}
.mapa-ruta {
  stroke: #2D8A4E; stroke-width: 1.8; stroke-dasharray: 4, 3; opacity: .75;
  animation: ruta-dash 2s linear infinite;
}
@keyframes ruta-dash {
  to { stroke-dashoffset: -14; }
}
.mapa-pulso {
  animation: pulso-hub 2.2s ease-out infinite;
  transform-origin: 240px 225px;
}
@keyframes pulso-hub {
  0% { transform: scale(.6); opacity: 0.9; }
  100% { transform: scale(1.6); opacity: 0; }
}
.mapa-ciudad {
  font-size: 10px; font-weight: 600; fill: #4A453F;
}

.cobertura-pie {
  display: flex; flex-wrap: wrap; gap: 12px; justify-content: flex-end;
  padding-top: 14px; border-top: 1px solid var(--linea);
}
"""


APP = r"""/* JATH Electroestatic - catalogo vivo
   Corre sin internet y sin servidor: todo esta en archivos sueltos al lado. Por eso nada de
   fetch ni de modulos, y el boton de WhatsApp es un enlace normal. */
(function () {
  'use strict';

  var D = window.DATOS;
  // La clave cambio de nombre cuando la marca se corrigio. Si se dejara la misma, un cliente
  // que todavia tenga la cotizacion guardada de la version anterior veria sus items viejos
  // mezclados con los nuevos, sin saber de donde salieron.
  var CLAVE = 'jath-electroestatic-cotizacion-v1';
  var WA = 'https://wa.me/' + D.contacto.whatsapp_numero;

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var colorPorId = {}, equipoPorId = {};
  D.colores.forEach(function (c) { colorPorId[c.id] = c; });
  D.equipos.forEach(function (e) { equipoPorId[e.id] = e; });

  var dispararChorroPistola = null;

  // ---------------------------------------------------------------- escena del encabezado
  // La pistola dispara un abanico de pintura: cada gota es un div vacio que cruza la cinta de
  // 0% a 100% abriendose en cono. Se hacen con codigo y no como HTML escrito a mano porque los
  // parametros son aleatorios: asi la nube no se ve como una hilera de puntos identicos. Los
  // retrasos van en negativo para que el chorro ya este en marcha al cargar la pagina.
  (function escena() {
    var caja = $('#escena-polvo');
    if (!caja) return;
    var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (quieto) return;
    // La abertura se mide en pantalla en vez de escribirse a mano: asi la nube copia el
    // abanico dibujado en CSS, y no se sale de la cinta en celular ni queda raquitica en
    // pantalla ancha.
    var cono = document.querySelector('.escena-abanico');
    var medio = (cono ? cono.getBoundingClientRect().height : 156) / 2;
    var N = 72;
    // Paleta de varios colores vivos de pintura electrostática
    var paleta = [
      { hex: '#0573BC', rgb: '5, 115, 188' },   // Azul Caribe
      { hex: '#469D39', rgb: '70, 157, 57' },   // Verde Menta
      { hex: '#EAAA0D', rgb: '234, 170, 13' },  // Amarillo Liso
      { hex: '#E25327', rgb: '226, 83, 39' },   // Naranja Liso
      { hex: '#C1121F', rgb: '193, 18, 31' },   // Rojo Liso
      { hex: '#D0326D', rgb: '208, 50, 109' },  // Fucsia Magenta
      { hex: '#7C649D', rgb: '124, 100, 157' }, // Lila
      { hex: '#00A896', rgb: '0, 168, 150' },   // Turquesa
      { hex: '#C99E32', rgb: '201, 158, 50' },  // Dorado
      { hex: '#0D3884', rgb: '13, 56, 132' }    // Azul Cobalto
    ];
    for (var i = 0; i < N; i++) {
      var p = document.createElement('i');
      // --x0 escalona la salida para que la boquilla escupa ancho desde el primer instante y
      // --dy es la altura a la que llega la gota al final, repartida dentro del abanico.
      var x0 = Math.random() * 20;
      var dy = (Math.random() * 2 - 1) * medio * 0.9;
      var dur = 1.4 + Math.random() * 1.3;
      var col = paleta[i % paleta.length];
      p.style.setProperty('--x0', x0.toFixed(1) + 'px');
      p.style.setProperty('--dy', dy.toFixed(1) + 'px');
      p.style.setProperty('--dur', dur.toFixed(2) + 's');
      p.style.setProperty('--tam', (0.45 + Math.random() * 0.8).toFixed(2));
      p.style.setProperty('--ret', (-Math.random() * dur).toFixed(2) + 's');
      p.style.setProperty('--color-gota', col.hex);
      p.style.setProperty('--sombra-gota', 'rgba(' + col.rgb + ', 0.65)');
      caja.appendChild(p);
    }

    // El ancho del abanico se mide y se guarda en --recorrido: la animacion mueve las gotas
    // con transform (no con left), y asi el navegador no recalcula la pagina en cada cuadro.
    // Si cambia el tamano de la ventana se vuelve a medir.
    function medirRecorrido() {
      caja.style.setProperty('--recorrido', caja.clientWidth + 'px');
    }
    medirRecorrido();
    var espera = null;
    window.addEventListener('resize', function () {
      if (espera) return;
      espera = window.setTimeout(function () { espera = null; medirRecorrido(); }, 200);
    });

    // Fuera de pantalla no se anima nada: la cinta queda congelada mientras se lee el resto.
    var cinta = document.querySelector('.escena');
    if (cinta && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entradas) {
        cinta.classList.toggle('escena-quieta', !entradas[0].isIntersecting);
      }, { rootMargin: '120px' }).observe(cinta);
    }

    // Disparador de ráfagas personalizadas desde la pistola
    dispararChorroPistola = function (colorObj, cantidad) {
      if (!caja) return;
      var total = cantidad || 26;
      for (var k = 0; k < total; k++) {
        (function () {
          var p = document.createElement('i');
          var dy = (Math.random() * 2 - 1) * medio * 0.95;
          var dur = 0.9 + Math.random() * 0.8;
          var c = colorObj || paleta[Math.floor(Math.random() * paleta.length)];
          p.style.setProperty('--x0', (Math.random() * 15).toFixed(1) + 'px');
          p.style.setProperty('--dy', dy.toFixed(1) + 'px');
          p.style.setProperty('--dur', dur.toFixed(2) + 's');
          p.style.setProperty('--tam', (0.65 + Math.random() * 0.85).toFixed(2));
          p.style.setProperty('--ret', '0s');
          p.style.setProperty('--color-gota', c.hex);
          p.style.setProperty('--sombra-gota', c.sombra || ('rgba(' + (c.rgb || '193,18,31') + ', 0.85)'));
          caja.appendChild(p);
          window.setTimeout(function () {
            if (p.parentNode) p.parentNode.removeChild(p);
          }, (dur + 0.1) * 1000);
        }());
      }
    };

    // Al hacer clic en la pistola o en la escena, dispara una ráfaga multicolor
    var escenaEl = document.querySelector('.escena');
    if (escenaEl) {
      escenaEl.style.cursor = 'pointer';
      escenaEl.title = 'Haga clic para disparar una ráfaga multicolor';
      escenaEl.addEventListener('click', function () {
        dispararChorroPistola(null, 24);
      });
    }
  }());

  // ---------------------------------------------------------------- memoria
  // En file:// el navegador a veces no deja guardar, y no es motivo para que el sitio
  // deje de funcionar: se intenta y, si falla, sigue igual mientras esta abierto.
  function cargar() {
    try {
      var s = window.localStorage.getItem(CLAVE);
      return s ? JSON.parse(s) : [];
    } catch (e) { return []; }
  }
  function guardar(items) {
    try { window.localStorage.setItem(CLAVE, JSON.stringify(items)); } catch (e) {}
  }

  var carrito = cargar();

  function sumar(tipo, id) {
    for (var i = 0; i < carrito.length; i++) {
      if (carrito[i].tipo === tipo && carrito[i].id === id) {
        carrito[i].cantidad += 1;
        return;
      }
    }
    carrito.push({ tipo: tipo, id: id, cantidad: 1 });
  }
  function restar(tipo, id) {
    for (var i = 0; i < carrito.length; i++) {
      if (carrito[i].tipo === tipo && carrito[i].id === id) {
        carrito[i].cantidad -= 1;
        if (carrito[i].cantidad <= 0) carrito.splice(i, 1);
        return;
      }
    }
  }
  function quitar(tipo, id) {
    carrito = carrito.filter(function (i) { return !(i.tipo === tipo && i.id === id); });
  }
  function total() {
    return carrito.reduce(function (s, i) { return s + i.cantidad; }, 0);
  }

  // ---------------------------------------------------------------- avisos
  var reloj = null;
  function avisar(texto) {
    var caja = $('#avisos');
    // Un aviso a la vez. Antes se apilaban: cada temporizador quitaba solo el suyo, asi que
    // agregar cinco cosas seguidas dejaba cinco avisos pegados en la pantalla.
    caja.innerHTML = '';
    var n = document.createElement('div');
    n.className = 'aviso-flotante';
    n.textContent = texto;
    caja.appendChild(n);
    if (reloj) window.clearTimeout(reloj);
    reloj = window.setTimeout(function () {
      if (n.parentNode) n.parentNode.removeChild(n);
    }, 2400);
  }

  // ---------------------------------------------------------------- textos del folleto
  $('#mision').textContent = D.mision;
  $('#vision').textContent = D.vision;
  $('#portada-bajada').textContent = D.quienes_somos;
  $('#lema').textContent = D.contacto.lema;

  // Las cifras de la portada cuentan solas al abrir, menos para quien pidio menos movimiento.
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function contarCifra(nodo, numero, cola) {
    if (quieto || numero < 2) { nodo.textContent = numero + cola; return; }
    var t0 = null;
    function paso(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / 900);
      nodo.textContent = Math.round(numero * (1 - Math.pow(1 - k, 3))) + cola;
      if (k < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }
  var cifras = $('#cifras');
  cifras.innerHTML = '';
  var itemsCifras = [
    {
      cifra: '48',
      titulo: 'colores en la carta',
      accion: 'Ver carta',
      destino: 'colores',
      color: { hex: '#0573BC', rgb: '5, 115, 188', sombra: 'rgba(5, 115, 188, 0.28)' }
    },
    {
      cifra: '15',
      titulo: 'equipos y repuestos',
      accion: 'Ver equipos',
      destino: 'equipos',
      color: { hex: '#2D8A4E', rgb: '45, 138, 78', sombra: 'rgba(45, 138, 78, 0.28)' }
    },
    {
      cifra: '4',
      titulo: 'líneas de servicio',
      accion: 'Ver servicios',
      destino: 'servicios',
      color: { hex: '#D96B27', rgb: '217, 107, 39', sombra: 'rgba(217, 107, 39, 0.28)' }
    },
    {
      cifra: '10+',
      titulo: 'años de experiencia',
      accion: 'Conózcanos',
      destino: 'quienes',
      color: { hex: '#C1121F', rgb: '193, 18, 31', sombra: 'rgba(193, 18, 31, 0.28)' }
    }
  ];

  itemsCifras.forEach(function (c) {
    var li = document.createElement('li');
    li.setAttribute('role', 'button');
    li.setAttribute('tabindex', '0');
    li.setAttribute('title', 'Haga clic para ver ' + c.titulo);
    li.style.setProperty('--cifra-color', c.color.hex);
    li.style.setProperty('--cifra-sombra', c.color.sombra);

    var b = document.createElement('b');
    var s = document.createElement('span');
    var acc = document.createElement('small');
    acc.className = 'cifra-accion';
    acc.innerHTML = c.accion + ' <i aria-hidden="true">&rarr;</i>';

    var partes = /^(\d+)(.*)$/.exec(c.cifra);
    b.textContent = c.cifra;
    s.textContent = c.titulo;
    li.appendChild(b);
    li.appendChild(s);
    li.appendChild(acc);
    cifras.appendChild(li);

    contarCifra(b, parseInt(partes[1], 10), partes[2]);

    function activarCifra() {
      if (dispararChorroPistola) {
        dispararChorroPistola(c.color, 32);
      }
      contarCifra(b, parseInt(partes[1], 10), partes[2]);
      li.classList.add('cifra-activa');
      window.setTimeout(function () {
        li.classList.remove('cifra-activa');
      }, 350);

      var destinoEl = document.getElementById(c.destino);
      if (destinoEl) {
        destinoEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    li.addEventListener('click', activarCifra);
    li.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activarCifra();
      }
    });
  });

  // Modal de cobertura y zonas de despacho
  function abrirModalCobertura() {
    var modal = $('#modal-cobertura');
    if (!modal) return;
    var btnWa = $('#btn-cobertura-wa');
    if (btnWa) {
      var msg = encodeURIComponent('Hola JATH Electroestatic, me gustaría consultar tiempos de entrega y flete para mi ciudad.');
      btnWa.href = 'https://wa.me/' + D.contacto.whatsapp_numero + '?text=' + msg;
    }
    modal.hidden = false;
  }
  function cerrarModalCobertura() {
    var modal = $('#modal-cobertura');
    if (modal) modal.hidden = true;
  }
  $$('[data-cerrar-cobertura]').forEach(function (btn) {
    btn.addEventListener('click', cerrarModalCobertura);
  });

  var dif = $('#diferenciadores');
  var datosDif = [
    {
      tipo: 'experiencia',
      titulo: (D.diferenciadores[0] && D.diferenciadores[0][0]) || 'Más de 10 años de experiencia',
      desc: (D.diferenciadores[0] && D.diferenciadores[0][1]) || 'Trayectoria y solidez garantizada en el mercado.',
      pista: 'Ver fotos de trabajos',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',
      color: { hex: '#C1121F', rgb: '193, 18, 31' },
      aviso: 'Conozca nuestros trabajos y aplicaciones en pintura electrostática.'
    },
    {
      tipo: 'asesor',
      titulo: (D.diferenciadores[1] && D.diferenciadores[1][0]) || 'Asesoría personalizada',
      desc: (D.diferenciadores[1] && D.diferenciadores[1][1]) || 'Un asesor técnico que conoce su caso.',
      pista: 'Contactar por WhatsApp',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
      color: { hex: '#0573BC', rgb: '5, 115, 188' },
      aviso: 'Conectando con un asesor técnico por WhatsApp...'
    },
    {
      tipo: 'productos',
      titulo: (D.diferenciadores[2] && D.diferenciadores[2][0]) || 'Productos de alto rendimiento',
      desc: (D.diferenciadores[2] && D.diferenciadores[2][1]) || 'Pinturas y equipos de calidad superior.',
      pista: 'Ver catálogo de productos',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
      color: { hex: '#D96B27', rgb: '217, 107, 39' },
      aviso: 'Explorando la línea de pinturas y equipos de aplicación.'
    },
    {
      tipo: 'entrega',
      titulo: (D.diferenciadores[3] && D.diferenciadores[3][0]) || 'Entrega ágil en Bogotá y alrededores',
      desc: (D.diferenciadores[3] && D.diferenciadores[3][1]) || 'Mismo día en Bogotá y cobertura a nivel nacional.',
      pista: 'Ver mapa de cobertura',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13" rx="1"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
      color: { hex: '#2D8A4E', rgb: '45, 138, 78' },
      aviso: 'Abriendo mapa de cobertura y zonas de despacho...'
    }
  ];

  dif.innerHTML = '';
  datosDif.forEach(function (d, idx) {
    var li = document.createElement('li');
    li.setAttribute('role', 'button');
    li.setAttribute('tabindex', '0');
    li.setAttribute('aria-label', d.titulo + ': ' + d.desc + '. ' + d.pista);
    li.style.setProperty('--dif-color', d.color.hex);
    li.style.setProperty('--dif-sombra', 'rgba(' + d.color.rgb + ', 0.22)');
    li.style.setProperty('--dif-fondo', 'rgba(' + d.color.rgb + ', 0.08)');

    var cab = document.createElement('div');
    cab.className = 'dif-cabecera';
    cab.innerHTML = '<div class="dif-icono" aria-hidden="true">' + d.icono + '</div><span class="dif-numero">0' + (idx + 1) + '</span>';

    var tit = document.createElement('strong');
    tit.className = 'dif-titulo';
    tit.textContent = d.titulo;

    var desc = document.createElement('span');
    desc.className = 'dif-desc';
    desc.textContent = d.desc;

    var pis = document.createElement('small');
    pis.className = 'dif-pista';
    pis.innerHTML = d.pista + ' <i aria-hidden="true">&rarr;</i>';

    li.appendChild(cab);
    li.appendChild(tit);
    li.appendChild(desc);
    li.appendChild(pis);
    dif.appendChild(li);

    function activarDif() {
      if (dispararChorroPistola) {
        dispararChorroPistola(d.color, 28);
      }
      li.classList.add('diferenciador-activo');
      window.setTimeout(function () {
        li.classList.remove('diferenciador-activo');
      }, 300);
      avisar(d.aviso);

      // Acciones solicitadas para cada tarjeta
      if (d.tipo === 'experiencia') {
        var secTrabajos = document.getElementById('trabajos');
        if (secTrabajos) secTrabajos.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else if (d.tipo === 'asesor') {
        var msg = encodeURIComponent('Hola JATH Electroestatic, me contacto desde la web y solicito asesoría personalizada para un proyecto.');
        window.open('https://wa.me/' + D.contacto.whatsapp_numero + '?text=' + msg, '_blank', 'noopener');
      } else if (d.tipo === 'productos') {
        var secProductos = document.getElementById('productos');
        if (secProductos) secProductos.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else if (d.tipo === 'entrega') {
        abrirModalCobertura();
      }
    }

    li.addEventListener('click', activarDif);
    li.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activarDif();
      }
    });
  });

  // Renderizar galería de trabajos
  var galeriaTrabajos = $('#galeria-trabajos');
  if (galeriaTrabajos) {
    var listaTrabajos = [
      {
        titulo: 'Estructuras y Rejas Metálicas',
        categoria: 'Arquitectónico & Seguridad',
        foto: 'fotos/trabajo-01.jpg'
      },
      {
        titulo: 'Perfiles de Aluminio',
        categoria: 'Ventanería & Fachadas',
        foto: 'fotos/trabajo-02.jpg'
      },
      {
        titulo: 'Autopartes y Rines de Aleación',
        categoria: 'Sector Automotriz',
        foto: 'fotos/trabajo-03.jpg'
      },
      {
        titulo: 'Gabinetes Eléctricos y Racks',
        categoria: 'Equipos Electrónicos',
        foto: 'fotos/trabajo-04.jpg'
      },
      {
        titulo: 'Mobiliario Comercial y Estantería',
        categoria: 'Diseño & Retail',
        foto: 'fotos/trabajo-05.jpg'
      },
      {
        titulo: 'Maquinaria y Tuberías Pesadas',
        categoria: 'Sector Industrial',
        foto: 'fotos/trabajo-06.jpg'
      }
    ];

    galeriaTrabajos.innerHTML = '';
    listaTrabajos.forEach(function (tr) {
      var art = document.createElement('article');
      art.className = 'tarjeta-trabajo';

      var wrap = document.createElement('div');
      wrap.className = 'trabajo-foto-wrap';
      wrap.innerHTML = '<img src="' + tr.foto + '" alt="' + tr.titulo + '" loading="lazy" decoding="async"><span class="trabajo-badge">Muestra referencial</span>';

      var info = document.createElement('div');
      info.className = 'trabajo-info';
      info.innerHTML = '<span class="trabajo-categoria">' + tr.categoria + '</span>' +
        '<h3 class="trabajo-titulo">' + tr.titulo + '</h3>';

      art.appendChild(wrap);
      art.appendChild(info);
      galeriaTrabajos.appendChild(art);
    });
  }

  // Interactividad en tarjetas de Misión y Visión
  var tMision = $('.tarjeta-mision');
  if (tMision) {
    tMision.style.cursor = 'pointer';
    tMision.addEventListener('click', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: '#0573BC', rgb: '5, 115, 188' }, 26);
      avisar('Misión JATH: eficiencia y resultados superiores en recubrimiento industrial.');
    });
  }
  var tVision = $('.tarjeta-vision');
  if (tVision) {
    tVision.style.cursor = 'pointer';
    tVision.addEventListener('click', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: '#2D8A4E', rgb: '45, 138, 78' }, 26);
      avisar('Visión JATH: liderazgo en tecnologías limpias y sostenibles.');
    });
  }

  // Metadatos extendidos por categoria de producto
  var metaProductos = [
    {
      icono: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/></svg>',
      color: { hex: '#C1121F', rgb: '193,18,31' },
      accion: 'Ver los 48 colores',
      destino: 'colores',
      etiqueta: '48 colores disponibles'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
      color: { hex: '#0573BC', rgb: '5,115,188' },
      accion: 'Ver equipos',
      destino: 'equipos',
      etiqueta: '15 equipos y repuestos'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
      color: { hex: '#2D8A4E', rgb: '45,138,78' },
      accion: 'Cotizar repuestos',
      destino: 'cotizacion',
      etiqueta: 'Envio nacional'
    }
  ];

  var pro = $('#lista-productos');
  D.productos.forEach(function (p, idx) {
    var meta = metaProductos[idx] || { icono: '', color: { hex: '#C1121F', rgb: '193,18,31' }, accion: 'Ver mas', destino: '', etiqueta: '' };
    var art = document.createElement('article');
    art.className = 'producto';
    art.setAttribute('tabindex', '0');
    art.setAttribute('role', 'region');
    art.style.setProperty('--prod-color', meta.color.hex);
    art.style.setProperty('--prod-sombra', 'rgba(' + meta.color.rgb + ', 0.18)');
    art.style.setProperty('--prod-fondo', 'rgba(' + meta.color.rgb + ', 0.07)');

    // Cabecera: icono + etiqueta de categoria
    var cab = document.createElement('div');
    cab.className = 'producto-cab';
    var icoWrap = document.createElement('div');
    icoWrap.className = 'producto-icono';
    icoWrap.setAttribute('aria-hidden', 'true');
    icoWrap.innerHTML = meta.icono;
    var etq = document.createElement('span');
    etq.className = 'producto-etiqueta';
    etq.textContent = meta.etiqueta;
    cab.appendChild(icoWrap);
    cab.appendChild(etq);
    art.appendChild(cab);

    // Titulo
    var h = document.createElement('h3');
    h.className = 'producto-titulo';
    h.textContent = p[0];
    art.appendChild(h);

    // Chips de caracteristicas
    var chips = document.createElement('ul');
    chips.className = 'producto-chips';
    p[1].forEach(function (t) {
      var li = document.createElement('li');
      li.className = 'producto-chip';
      li.textContent = t;
      chips.appendChild(li);
    });
    art.appendChild(chips);

    // Boton de accion
    var pie = document.createElement('div');
    pie.className = 'producto-pie';
    var btn = document.createElement('button');
    btn.className = 'btn btn-producto';
    btn.innerHTML = meta.accion + ' <i aria-hidden="true">&rarr;</i>';
    btn.addEventListener('click', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 24);
      if (meta.destino === 'cotizacion') {
        var btnCot = $$('[data-abrir-cotizacion]')[0];
        if (btnCot) btnCot.click();
      } else {
        var sec = document.getElementById(meta.destino);
        if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
    pie.appendChild(btn);
    art.appendChild(pie);

    // Hover: disparo suave de chorro
    art.addEventListener('mouseenter', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 12);
    });

    pro.appendChild(art);
  });

  // Metadatos extendidos por servicio
  var metaServicios = [
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
      color: { hex: '#0573BC', rgb: '5,115,188' },
      etiqueta: 'Consultoria',
      numero: '01'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
      color: { hex: '#D96B27', rgb: '217,107,39' },
      etiqueta: 'Capacitacion',
      numero: '02'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
      color: { hex: '#2D8A4E', rgb: '45,138,78' },
      etiqueta: 'Instalacion',
      numero: '03'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
      color: { hex: '#7C649D', rgb: '124,100,157' },
      etiqueta: 'Optimizacion',
      numero: '04'
    }
  ];

  var srv = $('#lista-servicios');
  D.servicios.forEach(function (s, i) {
    var meta = metaServicios[i] || { icono: '', color: { hex: '#C1121F', rgb: '193,18,31' }, etiqueta: 'Servicio', numero: '0' + (i+1) };
    var art = document.createElement('article');
    art.className = 'servicio';
    art.setAttribute('tabindex', '0');
    art.style.setProperty('--srv-color', meta.color.hex);
    art.style.setProperty('--srv-sombra', 'rgba(' + meta.color.rgb + ', 0.20)');
    art.style.setProperty('--srv-fondo',  'rgba(' + meta.color.rgb + ', 0.07)');

    // Cabecera: numero + icono + etiqueta
    var cab = document.createElement('div');
    cab.className = 'servicio-cab';

    var num = document.createElement('span');
    num.className = 'servicio-numero';
    num.textContent = meta.numero;

    var icoWrap = document.createElement('div');
    icoWrap.className = 'servicio-icono';
    icoWrap.setAttribute('aria-hidden', 'true');
    icoWrap.innerHTML = meta.icono;

    var etq = document.createElement('span');
    etq.className = 'servicio-etiqueta';
    etq.textContent = meta.etiqueta;

    cab.appendChild(num);
    cab.appendChild(icoWrap);
    cab.appendChild(etq);
    art.appendChild(cab);

    // Titulo
    var h = document.createElement('h3');
    h.className = 'servicio-titulo';
    h.textContent = s[0];
    art.appendChild(h);

    // Chips de detalle
    if (s[1] && s[1].length) {
      var chips = document.createElement('ul');
      chips.className = 'servicio-chips';
      s[1].forEach(function (t) {
        var li = document.createElement('li');
        li.className = 'servicio-chip';
        li.textContent = t;
        chips.appendChild(li);
      });
      art.appendChild(chips);
    }

    // Boton agregar a cotizacion
    var pie = document.createElement('div');
    pie.className = 'servicio-pie';
    var b = document.createElement('button');
    b.className = 'btn btn-servicio agregar';
    b.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Agregar a la cotizaci\u00f3n';
    b.addEventListener('click', function () {
      sumar('servicio', i);
      pintarCarrito();
      avisar('"' + s[0] + '" agregada');
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 18);
    });
    pie.appendChild(b);
    art.appendChild(pie);

    // Hover: disparo suave
    art.addEventListener('mouseenter', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 10);
    });

    srv.appendChild(art);
  });

  // ---------------------------------------------------------------- contacto
  var icoContacto = {
    ubicacion: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    whatsapp:  '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.127.558 4.126 1.532 5.859L.054 23.428a.5.5 0 0 0 .612.612l5.568-1.478A11.944 11.944 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.891 0-3.667-.523-5.183-1.432l-.361-.215-3.744.993.993-3.744-.216-.361A9.944 9.944 0 0 1 2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>',
    horario:   '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    instagram: '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>',
    facebook:  '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.235 2.686.235v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.268h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/></svg>',
    youtube:   '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/></svg>',
    tiktok:    '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>'
  };

  var colorRedes = {
    instagram: '#E1306C',
    facebook:  '#1877F2',
    youtube:   '#FF0000',
    tiktok:    '#010101'
  };

  function linea(rotulo, valor, href, tipoIcono, colorIcono) {
    var d = document.createElement('div');
    d.className = 'dato';
    if (colorIcono) {
      d.style.setProperty('--dato-color', colorIcono);
      d.style.setProperty('--dato-fondo', colorIcono.replace(')', ', 0.08)').replace('rgb', 'rgba').replace('#', 'rgba(').replace('rgba(#', 'rgba('));
    }

    var cab = document.createElement('div');
    cab.className = 'dato-cab';

    if (tipoIcono && icoContacto[tipoIcono]) {
      var ico = document.createElement('span');
      ico.className = 'dato-icono';
      ico.setAttribute('aria-hidden', 'true');
      ico.innerHTML = icoContacto[tipoIcono];
      cab.appendChild(ico);
    }

    var rot = document.createElement('span');
    rot.className = 'dato-rotulo';
    rot.textContent = rotulo;
    cab.appendChild(rot);
    d.appendChild(cab);

    var val = document.createElement(href ? 'a' : 'strong');
    val.className = 'dato-valor';
    if (href) { val.href = href; val.target = '_blank'; val.rel = 'noopener noreferrer'; }
    val.textContent = valor;
    d.appendChild(val);
    return d;
  }

  // URLs de redes sociales
  var urlsRedes = {
    'Instagram': 'https://instagram.com/jathelectroestatic',
    'Facebook':  'https://facebook.com/jathelectroestatic',
    'YouTube':   'https://youtube.com/@jathelectroestatic',
    'TikTok':    'https://tiktok.com/@jathelectroestatic'
  };

  var cd = $('#contacto-datos');

  // Datos principales
  var datosPrin = document.createElement('div');
  datosPrin.className = 'contacto-datos-principal';
  datosPrin.appendChild(linea('Ubicaci\u00f3n', D.contacto.ubicacion, null, 'ubicacion', '#C1121F'));
  datosPrin.appendChild(linea('WhatsApp', D.contacto.whatsapp, 'https://wa.me/' + D.contacto.whatsapp_numero, 'whatsapp', '#25D366'));
  datosPrin.appendChild(linea('Horario', D.contacto.horario, null, 'horario', '#0573BC'));
  cd.appendChild(datosPrin);

  // Redes sociales
  if (D.contacto.redes && D.contacto.redes.length) {
    var redesTit = document.createElement('p');
    redesTit.className = 'contacto-redes-titulo';
    redesTit.textContent = 'S\u00edguenos';
    cd.appendChild(redesTit);

    var redesGrid = document.createElement('div');
    redesGrid.className = 'contacto-redes';
    D.contacto.redes.forEach(function (r) {
      var nombre = r[0];
      var tipoKey = nombre.toLowerCase();
      var color = colorRedes[tipoKey] || '#6E6862';
      var url = urlsRedes[nombre] || null;
      var btn = document.createElement(url ? 'a' : 'div');
      btn.className = 'red-social';
      btn.style.setProperty('--red-color', color);
      if (url) { btn.href = url; btn.target = '_blank'; btn.rel = 'noopener noreferrer'; }

      var icoSpan = document.createElement('span');
      icoSpan.className = 'red-icono';
      icoSpan.setAttribute('aria-hidden', 'true');
      icoSpan.innerHTML = icoContacto[tipoKey] || '';

      var nomSpan = document.createElement('span');
      nomSpan.className = 'red-nombre';
      nomSpan.textContent = nombre;

      var handleSpan = document.createElement('span');
      handleSpan.className = 'red-handle';
      handleSpan.textContent = r[1];

      btn.appendChild(icoSpan);
      btn.appendChild(nomSpan);
      btn.appendChild(handleSpan);
      redesGrid.appendChild(btn);
    });
    cd.appendChild(redesGrid);
  }

  // ---------------------------------------------------------------- colores
  var acabadoActual = 'todos';
  var busqueda = '';

  function pintarFiltrosColor() {
    var caja = $('#filtros-color');
    caja.innerHTML = '';
    var lista = [{ nombre: 'todos', cuenta: D.colores.length }];
    D.acabados.forEach(function (a) {
      lista.push({ nombre: a, cuenta: D.colores.filter(function (c) { return c.acabado === a; }).length });
    });
    lista.forEach(function (a) {
      if (!a.cuenta) return;
      var b = document.createElement('button');
      b.className = 'chip';
      b.type = 'button';
      b.setAttribute('aria-pressed', String(acabadoActual === a.nombre));
      b.textContent = a.nombre === 'todos' ? 'Todos' : a.nombre + ' (' + a.cuenta + ')';
      b.addEventListener('click', function () {
        acabadoActual = a.nombre;
        pintarFiltrosColor();
        pintarColores();
      });
      caja.appendChild(b);
    });
  }

  function enCotizacion(tipo, id) {
    return carrito.some(function (i) { return i.tipo === tipo && i.id === id; });
  }

  function pintarColores() {
    var rej = $('#rejilla-colores');
    rej.innerHTML = '';
    var q = busqueda.replace(/^#/, '').toUpperCase();
    var lista = D.colores.filter(function (c) {
      if (acabadoActual !== 'todos' && c.acabado !== acabadoActual) return false;
      if (!q) return true;
      return c.nombre.toUpperCase().indexOf(q) >= 0
          || c.acabado.toUpperCase().indexOf(q) >= 0
          || c.hex.replace('#', '').toUpperCase().indexOf(q) === 0;
    });
    $('#color-vacio').hidden = lista.length > 0;
    lista.forEach(function (c) {
      var art = document.createElement('article');
      art.className = 'muestra' + (enCotizacion('color', c.id) ? ' muestra-elegida' : '');

      var bloque = document.createElement('div');
      bloque.className = 'muestra-color';
      bloque.style.background = c.hex;
      art.appendChild(bloque);

      var datos = document.createElement('div');
      datos.className = 'muestra-datos';
      var nom = document.createElement('div');
      nom.className = 'muestra-nombre';
      nom.textContent = c.nombre;
      var hex = document.createElement('div');
      hex.className = 'muestra-hex';
      hex.textContent = c.hex + ' · ' + c.acabado;
      var acc = document.createElement('div');
      acc.className = 'muestra-acciones';

      var ver = document.createElement('button');
      ver.type = 'button';
      ver.textContent = 'Ver';
      ver.addEventListener('click', function () { abrirLupa(c); });

      var add = document.createElement('button');
      add.type = 'button';
      add.className = 'agregar';
      add.textContent = enCotizacion('color', c.id) ? 'Agregado' : '+ Agregar';
      add.addEventListener('click', function () {
        sumar('color', c.id);
        pintarColores();
        pintarCarrito();
        avisar(c.hex + ' agregado');
      });

      acc.appendChild(ver);
      acc.appendChild(add);
      datos.appendChild(nom);
      datos.appendChild(hex);
      if (c.revisar) {
        var rev = document.createElement('div');
        rev.className = 'muestra-revisar';
        rev.textContent = 'nombre por confirmar';
        datos.appendChild(rev);
      }
      datos.appendChild(acc);
      art.appendChild(datos);
      rej.appendChild(art);
    });
  }

  $('#buscar-color').addEventListener('input', function (e) {
    busqueda = e.target.value;
    pintarColores();
  });

  // ---------------------------------------------------------------- lupa de color
  var lupaActual = null;
  function abrirLupa(c) {
    lupaActual = c;
    $('#lupa-color').style.background = c.hex;
    $('#lupa-familia').textContent = c.nombre;
    $('#lupa-hex').textContent = c.hex;
    $('#lupa-rgb').textContent = c.acabado + ' · ' + c.rgb_texto;
    $('#lupa-nota').textContent =
      'Color ' + c.hex + ' de la carta ' + (c.carta === 3 ? '1' : '2') +
      ', fila ' + c.fila + ', columna ' + c.col + ', acabado ' + c.acabado +
      '. El código se lo puede dar a cualquier proveedor de powder coating.';
    $('#lupa-agrregar').textContent = enCotizacion('color', c.id) ? 'Agregar otra vez' : 'Agregar a la cotización';
    // Mirar una carta impresa esconde este boton, asi que hay que volverlo a mostrar. Si no,
    // despues de mirar una carta el boton quedaba muerto para el resto de la sesion.
    $('#lupa-agrregar').hidden = false;
    $('#lupa').hidden = false;
  }
  function cerrarLupa() { $('#lupa').hidden = true; lupaActual = null; }
  $$('[data-cerrar-lupa]').forEach(function (b) { b.addEventListener('click', cerrarLupa); });
  $('#lupa-agrregar').addEventListener('click', function () {
    if (!lupaActual) return;
    sumar('color', lupaActual.id);
    pintarColores();
    pintarCarrito();
    avisar(lupaActual.hex + ' agregado');
    cerrarLupa();
  });
  $('#lupa-copiar').addEventListener('click', function () {
    if (!lupaActual) return;
    copiar(lupaActual.hex + '  ' + lupaActual.rgb_texto);
  });

  // ---------------------------------------------------------------- equipos
  var catActual = 'todas';
  function pintarFiltrosEquipo() {
    var caja = $('#filtros-equipo');
    caja.innerHTML = '';
    var cats = [{ nombre: 'todas', cuenta: D.equipos.length }];
    D.equipos.forEach(function (e) {
      var c = null;
      for (var i = 0; i < cats.length; i++) { if (cats[i].nombre === e.categoria) c = cats[i]; }
      if (c) c.cuenta += 1; else cats.push({ nombre: e.categoria, cuenta: 1 });
    });
    cats.forEach(function (c) {
      var b = document.createElement('button');
      b.className = 'chip';
      b.type = 'button';
      b.setAttribute('aria-pressed', String(catActual === c.nombre));
      b.textContent = c.nombre === 'todas' ? 'Todos' : c.nombre + ' (' + c.cuenta + ')';
      b.addEventListener('click', function () {
        catActual = c.nombre;
        pintarFiltrosEquipo();
        pintarEquipos();
      });
      caja.appendChild(b);
    });
  }

  function tarjetaEquipo(e) {
    var art = document.createElement('article');
    art.className = 'equipo';

    var foto = document.createElement('div');
    foto.className = 'equipo-foto';
    var img = document.createElement('img');
    img.src = e.archivo;
    img.alt = e.nombre;
    img.loading = 'lazy';
    img.decoding = 'async';
    foto.appendChild(img);
    art.appendChild(foto);

    var cuerpo = document.createElement('div');
    cuerpo.className = 'equipo-cuerpo';
    var cat = document.createElement('div');
    cat.className = 'equipo-cat';
    cat.textContent = e.categoria;
    var nom = document.createElement('div');
    nom.className = 'equipo-nombre';
    nom.textContent = e.nombre;
    cuerpo.appendChild(cat);
    cuerpo.appendChild(nom);
    if (e.provisional) {
      var pr = document.createElement('div');
      pr.className = 'provisional';
      pr.textContent = 'Nombre provisional';
      cuerpo.appendChild(pr);
    }

    var acc = document.createElement('div');
    acc.className = 'equipo-acciones';
    var add = document.createElement('button');
    add.type = 'button';
    add.className = 'agregar';
    add.textContent = enCotizacion('equipo', e.id) ? 'Agregado' : '+ Agregar';
    add.addEventListener('click', function () {
      sumar('equipo', e.id);
      pintarEquipos();
      pintarCarrito();
      avisar('"' + e.nombre + '" agregado');
    });
    acc.appendChild(add);
    cuerpo.appendChild(acc);
    art.appendChild(cuerpo);
    return art;
  }

  function pintarEquipos() {
    var rej = $('#rejilla-equipos');
    rej.innerHTML = '';
    D.equipos.filter(function (e) {
      return catActual === 'todas' || e.categoria === catActual;
    }).forEach(function (e) { rej.appendChild(tarjetaEquipo(e)); });
  }

  // ---------------------------------------------------------------- carta impresa
  $$('.carta').forEach(function (b) {
    b.addEventListener('click', function () {
      abrirLupa({
        hex: 'Carta impresa', rgb_texto: b.getAttribute('data-carta'),
        nombre: 'Carta impresa', acabado: 'Así se ve en el papel', carta: 3, fila: 0, col: 0
      });
      var img = new Image();
      img.src = b.getAttribute('data-carta');
      $('#lupa-color').style.background = '#fff url("' + b.getAttribute('data-carta') + '") center/contain no-repeat';
      $('#lupa-hex').textContent = 'Carta impresa';
      $('#lupa-rgb').textContent = 'Tono real de la muestra';
      $('#lupa-nota').textContent =
        'Esta es la carta tal como se imprime. El color de pantalla no es confiable: pida una muestra física.';
      $('#lupa-agrregar').hidden = true;
    });
  });

  // ---------------------------------------------------------------- cotizador
  function nombreDe(item) {
    if (item.tipo === 'color')  { var c = colorPorId[item.id];  return c ? c.nombre : 'Color'; }
    if (item.tipo === 'equipo') { var e = equipoPorId[item.id]; return e ? e.nombre : 'Equipo'; }
    return D.servicios[item.id] ? D.servicios[item.id][0] : 'Servicio';
  }
  function detalleDe(item) {
    if (item.tipo === 'color')  { var c = colorPorId[item.id];  return c ? c.rgb_texto : ''; }
    if (item.tipo === 'equipo') { var e = equipoPorId[item.id]; return e ? e.categoria : ''; }
    return 'Servicio';
  }

  function pintarCarrito() {
    var ul = $('#cajon-lista');
    ul.innerHTML = '';
    $('#cajon-vacio').hidden = carrito.length > 0;

    carrito.forEach(function (item) {
      var li = document.createElement('li');

      if (item.tipo === 'color') {
        var m = document.createElement('div');
        m.className = 'cajon-muestra';
        m.style.background = colorPorId[item.id].hex;
        li.appendChild(m);
      } else if (item.tipo === 'equipo') {
        var im = document.createElement('img');
        im.className = 'cajon-foto';
        im.src = equipoPorId[item.id].archivo;
        im.alt = '';
        li.appendChild(im);
      }

      var txt = document.createElement('div');
      txt.className = 'cajon-txt';
      var n = document.createElement('div');
      n.className = 'cajon-nom';
      n.textContent = nombreDe(item);
      var d = document.createElement('div');
      d.className = 'cajon-det';
      d.textContent = detalleDe(item);
      txt.appendChild(n);
      txt.appendChild(d);
      li.appendChild(txt);

      var can = document.createElement('div');
      can.className = 'cantidad';
      var menos = document.createElement('button');
      menos.type = 'button';
      menos.textContent = '−';
      menos.setAttribute('aria-label', 'Quitar uno');
      var num = document.createElement('span');
      num.textContent = String(item.cantidad);
      var mas = document.createElement('button');
      mas.type = 'button';
      mas.textContent = '+';
      mas.setAttribute('aria-label', 'Agregar uno');
      menos.addEventListener('click', function () {
        restar(item.tipo, item.id); pintarCarrito(); pintarColores(); pintarEquipos();
      });
      mas.addEventListener('click', function () {
        sumar(item.tipo, item.id); pintarCarrito(); pintarColores(); pintarEquipos();
      });
      can.appendChild(menos);
      can.appendChild(num);
      can.appendChild(mas);
      li.appendChild(can);

      var x = document.createElement('button');
      x.className = 'cajon-quitar';
      x.type = 'button';
      x.textContent = '×';
      x.setAttribute('aria-label', 'Quitar ' + nombreDe(item));
      x.addEventListener('click', function () {
        quitar(item.tipo, item.id); pintarCarrito(); pintarColores(); pintarEquipos();
      });
      li.appendChild(x);
      ul.appendChild(li);
    });

    var t = total();
    var barra = $('#barra');
    barra.hidden = t === 0;
    $('#abrir-cotizacion').hidden = t === 0;
    document.body.classList.toggle('sin-barra', t === 0);
    $('#barra-cuenta').textContent = String(t);
    $('#barra-texto').textContent = t === 1 ? 'item en su cotización' : 'items en su cotización';
    $('#boton-whatsapp').classList.toggle('btn-rojo', t > 0);
    $('#cajon-riesgo').hidden = t === 0;

    guardar(carrito);
  }

  function mensaje() {
    var l = [];
    l.push('Hola. Quiero cotizar lo siguiente con JATH ELECTROESTATIC:');
    l.push('');
    var cols = carrito.filter(function (i) { return i.tipo === 'color'; });
    var eqs  = carrito.filter(function (i) { return i.tipo === 'equipo'; });
    var svs  = carrito.filter(function (i) { return i.tipo === 'servicio'; });

    if (cols.length) {
      l.push('*COLORES* (nombre y código de la carta)');
      cols.forEach(function (i) {
        var c = colorPorId[i.id];
        l.push('• ' + c.nombre + '  ' + c.hex + '  ' + c.rgb_texto + '  x' + i.cantidad);
      });
      l.push('');
    }
    if (eqs.length) {
      l.push('*EQUIPOS Y REPUESTOS*');
      eqs.forEach(function (i) {
        l.push('• ' + equipoPorId[i.id].nombre + '  x' + i.cantidad +
               '  (' + equipoPorId[i.id].categoria + ')');
      });
      l.push('');
    }
    if (svs.length) {
      l.push('*SERVICIOS*');
      svs.forEach(function (i) {
        l.push('• ' + D.servicios[i.id][0] + '  x' + i.cantidad);
      });
      l.push('');
    }
    var nota = $('#nota').value.trim();
    if (nota) { l.push('*COMENTARIO*'); l.push(nota); l.push(''); }

    l.push('Enviado desde el catálogo de JATH ELECTROESTATIC.');
    return l.join('\n');
  }

  function pintarEnlaces() {
    var txt = mensaje();
    var href = WA + '?text=' + encodeURIComponent(txt);
    $('#boton-whatsapp').href = href;
    $('#wa-fijo').href = WA;
  }
  $('#nota').addEventListener('input', pintarEnlaces);

  function copiar(txt) {
    function ok() { avisar('Copiado: ' + txt); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(ok, function () { respaldo(txt, ok); });
    } else { respaldo(txt, ok); }
  }
  function respaldo(txt, ok) {
    var ta = document.createElement('textarea');
    ta.value = txt;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); ok(); } catch (e) { avisar('No se pudo copiar'); }
    document.body.removeChild(ta);
  }
  // ---------------------------------------------------------------- cajon
  function abrirCajon() {
    $('#cajon').hidden = false;
    $('#velo').hidden = false;
    pintarCarrito();
    pintarEnlaces();
  }
  function cerrarCajon() { $('#cajon').hidden = true; $('#velo').hidden = true; }
  $('#abrir-cotizacion').addEventListener('click', abrirCajon);
  $('#cerrar-cajon').addEventListener('click', cerrarCajon);
  $$('[data-abrir-cotizacion]').forEach(function (b) { b.addEventListener('click', abrirCajon); });
  $('#velo').addEventListener('click', cerrarCajon);
  $$('[data-ir]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = document.getElementById(b.getAttribute('data-ir'));
      if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (!$('#lupa').hidden) { cerrarLupa(); return; }
    if (!$('#cajon').hidden) cerrarCajon();
  });

  // ---------------------------------------------------------------- arranque
  pintarFiltrosColor();
  pintarColores();
  pintarFiltrosEquipo();
  pintarEquipos();
  pintarCarrito();
  pintarEnlaces();
}());
"""


# ------------------------------------------------------------------------- main
LEEME = """JATH Electroestatic - Catalogo y cotizador
===================================

Abra  index.html  con doble clic. Funciona sin internet.

Que hay adentro
--------------
  index.html     la pagina
  estilo.css     los colores y el diseno
  app.js         la logica
  datos.js       LOS DATOS: colores, equipos, servicios, contacto
  fotos/         los equipos, la escena y las fotos de trabajos
  cartas/        las dos cartas de colores impresas
  NOMBRES.txt    los nombres de los 15 equipos, para corregir
  COLORES.txt    los nombres de los 48 colores, para corregir
  fuente/        las herramientas para regenerar el sitio (no hace falta abrirla)

Las fotos de la seccion de trabajos
-----------------------------------
Son seis y se llaman  trabajo-01.jpg ... trabajo-06.jpg. Estan en  fotos/ . Para cambiarlas,
ponga la foto nueva con el mismo nombre y el mismo formato.

Como se cambia el nombre de un equipo o de un color
---------------------------------------------------
Abra  NOMBRES.txt  (equipos) o  COLORES.txt  (colores). Cada linea dice:

    numero | nombre que usted quiera poner

Por ejemplo:

    3 | Cabina de pintura con blowers
    7 | Gris Tornado Gofrado

Guarde el archivo y vuelva a correr  catalogo.py  en la terminal:

    cd "C:/Users/yoooe/OneDrive/Desktop/JATH Electroestatic - Catalogo"
    python fuente/catalogo.py

Se actualiza index.html y las demas. No hay que tocar nada mas.

De donde salen los colores
--------------------------
Los 48 codigos se midieron de la pintura real de las dos cartas impresas. Los nombres son los
que la carta trae impresos al lado: se leyeron del rotulo, y los pocos que no se alcanzaron a
leer con seguridad estan marcados en COLORES.txt con " <- revisar". Confirmelos contra la carta.

Los nombres de los equipos son PROVISIONALES. El folleto no rotula ninguna foto, asi que
se dedujeron de la forma del objeto. Corrigalos en NOMBRES.txt.
"""


def main():
    cambios = ajustes_de_nombres()
    colores = cargar_colores()
    if len(colores) != 48:
        print("aviso: salieron %d colores, no 48" % len(colores))

    os.makedirs(DESTINO, exist_ok=True)

    # El logo pequeno de la pestana del navegador. Se genera con iconos.py y aqui solo se
    # copia al sitio, para que sobreviva a cada regeneracion.
    iconos = os.path.join(AQUI, "iconos")
    if os.path.isdir(iconos):
        for n in sorted(os.listdir(iconos)):
            if n.startswith("favicon"):
                shutil.copy2(os.path.join(iconos, n), os.path.join(DESTINO, n))

    doc = pymupdf.open(ORIGEN)
    equipos = copiar_fotos(doc)
    doc.close()

    for e in equipos:
        if e["id"] in cambios:
            e["nombre"], e["provisional"] = cambios[e["id"]]
            print("   nombre corregido a mano: %02d  %s" % (e["id"], e["nombre"]))

    acabados = []
    for c in colores:
        if c["acabado"] not in acabados:
            acabados.append(c["acabado"])
    # El orden de los acabados es el de la carta, no el en que aparecieron, para que los
    # filtros siempre salgan en el mismo orden y no salten al recargar.
    orden = [etiqueta for _, etiqueta in ACABADOS] + ["Sin acabado"]
    acabados.sort(key=lambda a: orden.index(a) if a in orden else 99)

    datos = {
        "quienes_somos": QUIEN_SOMOS,
        "mision": MISION,
        "vision": VISION,
        "diferenciadores": [list(d) for d in DIFERENCIADORES],
        "productos": [list(p) for p in PRODUCTOS],
        "servicios": [list(s) for s in SERVICIOS],
        "acabados": acabados,
        "colores": colores,
        "equipos": equipos,
        "contacto": {
            "ubicacion": CONTACTO["ubicacion"],
            "whatsapp": CONTACTO["whatsapp"],
            "whatsapp_numero": WHATSAPP,
            "horario": CONTACTO["horario"],
            "redes": [list(r) for r in CONTACTO["redes"]],
            "lema": CONTACTO["lema"],
        },
        "generado": date.today().isoformat(),
    }

    def escribir(nombre, texto, bom=False):
        # Los .txt llevan BOM a proposito: el Bloc de notas de Windows no siempre adivina que
        # son UTF-8, y si los guarda con otra codina los acentos se vuelven basura y el sitio
        # queda con el texto roto.
        cod = "utf-8-sig" if bom else "utf-8"
        with open(os.path.join(DESTINO, nombre), "w", encoding=cod) as f:
            f.write(texto)

    # La reja del encabezado se arma con codigo (ver svg_reja) y se mete aqui: en el HTML va
    # solo la marca, para no tener que escribir a mano los treinta y pico rectangulos. La
    # presentacion tambien va escrita desde ya: si la llenara app.js despues, el titular y los
    # botones saltarian de sitio en el primer pintado (eso cuenta como CLS).
    escribir("index.html", HTML.replace("<!--ESCENA-PIEZA-->", svg_reja())
             .replace("<!--QUIENES-->", escape(QUIEN_SOMOS)))
    escribir("estilo.css", ESTILO)
    escribir("app.js", APP)
    escribir("LEEME.txt", LEEME, bom=True)
    escribir("datos.js", "var DATOS = " +
             json.dumps(datos, ensure_ascii=False, indent=1) + ";\n")

    # El archivo de nombres se escribe solo la primera vez. Despues es del cliente: si se
    # regenerara en cada corrida, cualquier correccion suya se perderia.
    ruta_nombres = os.path.join(DESTINO, "NOMBRES.txt")
    if not os.path.isfile(ruta_nombres):
        lineas = ["# Nombres de los equipos. Cambie lo que este despues de la barra y guarde.",
                  "# La proxima vez que corra catalogo.py, lo de aqui gana.",
                  "# Numero = posicion en el sitio (1-3 son los equipos de la hoja 6,",
                  "# 4-15 los doce repuestos de la hoja 5).",
                  "#"]
        for e in equipos:
            linea = "%02d | %s" % (e["id"], e["nombre"])
            lineas.append(linea + ("          <- provisional" if e["provisional"] else ""))
        escribir("NOMBRES.txt", "\n".join(lineas) + "\n", bom=True)
    else:
        print("   NOMBRES.txt ya existe: se respeta lo que el cliente corrigio")

    # El archivo de nombres de color tambien es del cliente: se escribe solo la primera vez.
    ruta_colores = os.path.join(DESTINO, "COLORES.txt")
    if not os.path.isfile(ruta_colores):
        lineas = ["# Nombres de los 48 colores, como salen impresos en las dos cartas.",
                  "# Cambie lo que este despues de la barra y guarde. La proxima vez que",
                  "# corra catalogo.py, lo de aqui gana sobre lo que leyo el OCR.",
                  "# Numero = posicion del color en el sitio (1-24 son los de la carta 1,",
                  "# 25-48 los de la carta 2).",
                  "# Los que llevan ' <- revisar' son los que el OCR no alcanzo a leer con",
                  "# seguridad: compruebelos contra la carta impresa.",
                  "#"]
        for c in colores:
            linea = "%02d | %s" % (c["id"], c["nombre"])
            lineas.append(linea + ("          <- revisar" if c["revisar"] else ""))
        escribir("COLORES.txt", "\n".join(lineas) + "\n", bom=True)
    else:
        print("   COLORES.txt ya existe: se respeta lo que el cliente corrigio")

    tam = 0
    for raiz, _, archivos in os.walk(DESTINO):
        for a in archivos:
            tam += os.path.getsize(os.path.join(raiz, a))

    print("carpeta: %s" % DESTINO)
    print("  %d colores, %d equipos, %d acabados, %d servicios"
          % (len(colores), len(equipos), len(acabados), len(SERVICIOS)))
    print("  peso total: %.1f MB" % (tam / 1048576.0))
    print("  abra index.html con doble clic")


if __name__ == "__main__":
    main()
