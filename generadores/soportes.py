"""Soportes de MDF (sostenedor SG90, sostenedor del sensor capacitivo, sostenedor y base del motorreductor).

SG90 y sensor: tomados de soportes.dxf (Andriy, 14/11/2026). Motorreductor y base: plano MOT-02/MOT-03 del informe.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import plano
from plano import PdfPages, Circle, Rectangle, hoja, poly, dim, RED, PROYECTO
import matplotlib.pyplot as plt
import ezdxf

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "soportes") + "/"
os.makedirs(OUT, exist_ok=True)
F = "14/11/2026"
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")

# ---------- lectura del DXF (dos tiras de 50 de ancho)
ents = list(ezdxf.readfile(SRC).modelspace())
pls = [[(p[0], p[1]) for p in e.get_points()] for e in ents if e.dxftype() == "LWPOLYLINE"]
cir = [(e.dxf.center.x, e.dxf.center.y, e.dxf.radius) for e in ents if e.dxftype() == "CIRCLE"]
bb = lambda P: (min(x for x, _ in P), min(y for _, y in P), max(x for x, _ in P), max(y for _, y in P))
tiras = sorted([p for p in pls if bb(p)[2] - bb(p)[0] == 50], key=lambda p: bb(p)[0])

def pieza(t):
    x0, y0, x1, y1 = bb(t)
    dentro = lambda x, y: x0 < x < x1 and y0 < y < y1
    rects = [bb(p) for p in pls if p is not t and dentro(*p[0])]
    circs = [(x - x0, y - y0, r) for x, y, r in cir if dentro(x, y)]
    return dict(W=x1 - x0, H=y1 - y0, rects=[(a - x0, b - y0, c - x0, d - y0) for a, b, c, d in rects], circs=circs)

SRV, CAP = pieza(tiras[0]), pieza(tiras[1])
L_HOLES = [(x, y, 2.4) for x in (19.8, 36.0) for y in (17.0, 56.0)]
MOT = dict(W=50, H=210, rects=[(12.5, 162.2, 37.5, 166.2)],
           circs=[(25, 180, 5.9), (16, 180, 1.8), (34, 180, 1.8)] + L_HOLES)
BASE = dict(W=70, H=25, rects=[], circs=[])

def dibuja(ax, P, ox, oy, s):
    T = lambda x, y: (ox + x * s, oy + y * s)
    poly(ax, [(0, 0), (P["W"], 0), (P["W"], P["H"]), (0, P["H"])], ox, oy, s)
    for a, b, c, d in P["rects"]: poly(ax, [(a, b), (c, b), (c, d), (a, d)], ox, oy, s, fc="white")
    for x, y, r in P["circs"]: ax.add_patch(Circle(T(x, y), r * s, fc="white", ec=RED, lw=0.9))
    return T

def cotas_tira(ax, P, T, titulo):
    W, H = P["W"], P["H"]
    dim(ax, T(0, H), T(W, H), "50", 6)
    dim(ax, T(W, 0), T(W, H), f(H), 22, vert=True)
    lh = sorted({(x, y) for x, y, r in P["circs"] if abs(r - 2.4) < 0.01})
    xs = sorted({x for x, _ in lh}); ys = sorted({y for _, y in lh})
    dim(ax, T(0, 0), T(xs[0], 0), f(xs[0]), -5, fs=4.6)
    dim(ax, T(xs[0], 0), T(xs[1], 0), f(xs[1] - xs[0]), -5, fs=4.6)
    dim(ax, T(xs[1], 0), T(W, 0), f(W - xs[1]), -5, fs=4.6)
    # cadena vertical del lado izquierdo: agujeros L y elementos superiores
    top = [y for x, y, r in P["circs"] if r != 2.4] + [y for r in P["rects"] for y in (r[1], r[3])]
    chain = sorted(set([0] + ys + top + [H]))
    for a, b in zip(chain, chain[1:]): dim(ax, T(0, a), T(0, b), f(b - a), -6, vert=True, fs=4.4)
    ax.text(*T(xs[1] + 4, ys[0] - 2), "Ø4.8", fontsize=4.8, color=plano.BLUE)
    ax.text(*T(W / 2, -16), titulo, fontsize=6.8, ha="center", weight="bold")

def material(ax):
    ax.text(105, 262, "MATERIAL: MDF  —  ESPESOR 3 mm", fontsize=13, ha="center", weight="bold")

def h1(ax):
    ax.text(105, 276, "SOPORTES — MEDIDAS DE CADA PIEZA (mm)", fontsize=10, ha="center", weight="bold")
    material(ax)
    s = 1 / 1.25
    # 1 sostenedor SG90
    P = SRV; T = dibuja(ax, P, 40, 85, s)
    cotas_tira(ax, P, T, "1   SOSTENEDOR SG90 — 4 unidades")
    (a, b, c, d), = P["rects"]
    dim(ax, T(a, d), T(c, d), f(c - a), 3, fs=4.4)
    dim(ax, T(c, b), T(c, d), f(d - b), 3, vert=True, fs=4.4)
    ex = sorted(x for x, y, r in P["circs"] if r == 1.0)
    dim(ax, T(ex[0], b - 4), T(ex[1], b - 4), f(ex[1] - ex[0]), 0, fs=4.4)
    ax.text(*T(ex[1] + 1.5, d + 1), "Ø2", fontsize=4.8, color=plano.BLUE)
    # 2 sostenedor del sensor capacitivo
    P = CAP; T = dibuja(ax, P, 130, 85, s)
    cotas_tira(ax, P, T, "2   SOSTENEDOR SENSOR CAPACITIVO — 4 unidades")
    x, y, r = [c for c in P["circs"] if c[2] > 3][0]
    dim(ax, T(x - r, y + r), T(x + r, y + r), f"Ø{f(2 * r)}", 3, fs=4.6)
    dim(ax, T(0, y + r + 6), T(x, y + r + 6), f(x), 0, fs=4.4)
    ax.text(105, 64, "escala 1:1.25", fontsize=6, ha="center")

def h2(ax):
    ax.text(105, 276, "SOPORTES — MEDIDAS DE CADA PIEZA (mm)", fontsize=10, ha="center", weight="bold")
    material(ax)
    s = 1 / 1.25
    P = MOT; T = dibuja(ax, P, 45, 72, s)
    cotas_tira(ax, P, T, "3   SOSTENEDOR MOTORREDUCTOR — 1 unidad")
    (a, b, c, d), = P["rects"]
    dim(ax, T(a, b), T(c, b), f(c - a), -3, fs=4.4)
    dim(ax, T(c, b), T(c, d), f(d - b), 3, vert=True, fs=4.4)
    dim(ax, T(0, b - 6), T(a, b - 6), f(a), 0, fs=4.4)
    dim(ax, T(16, 180 + 8), T(34, 180 + 8), "18", 0, fs=4.4)
    dim(ax, T(25 - 5.9, 180 + 14), T(25 + 5.9, 180 + 14), "Ø11.8", 0, fs=4.4)
    ax.text(*T(36, 182), "Ø3.6", fontsize=4.8, color=plano.BLUE)
    # 4 base
    s2 = 1.0; T = dibuja(ax, BASE, 115, 150, s2)
    dim(ax, T(0, 25), T(70, 25), "70", 5); dim(ax, T(70, 0), T(70, 25), "25", 5, vert=True)
    ax.text(*T(35, -12), "4   BASE MOTORREDUCTOR — 1 unidad", fontsize=6.8, ha="center", weight="bold")
    ax.text(150, 128, "escala 1:1", fontsize=6, ha="center")
    ax.text(150, 122, "sostenedor: escala 1:1.25", fontsize=6, ha="center")

def notas():
    fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 210); ax.set_ylim(0, 297); ax.axis("off")
    ax.add_patch(Rectangle((10, 10), 190, 277, fill=False, lw=1.6))
    ax.text(105, 276, "SOPORTES DE MDF — NOTAS DE CORTE Y MONTAJE", fontsize=10, ha="center", weight="bold")
    material(ax)
    cols = [16, 66, 80, 140]
    filas = [("Pieza", "Cant.", "Medidas [mm]", "Función"),
             ("1 Sostenedor SG90", "4", "50 x 185; ventana 23 x 12.5;\n2 agujeros Ø2 a 27.5", "eleva el servo de topes y\ncompuertas sobre la faja"),
             ("2 Sostenedor sensor", "4", "50 x 150; agujero Ø22.6", "sostiene el sensor capacitivo\nM24 (S1 a S4)"),
             ("3 Sostenedor motorr.", "1", "50 x 210; Ø11.8 + 2 x Ø3.6 a 18;\nhueco 25 x 4", "sostiene el motorreductor\nde la faja (A1)"),
             ("4 Base motorr.", "1", "70 x 25", "entra en el hueco 25 x 4\ndel sostenedor 3"),
             ("Agujeros ángulo L", "4 c/u", "Ø4.8; 16.2 entre centros (horiz.);\n39 entre centros (vert.)", "2 ángulos en L por pieza\n(piezas 1, 2 y 3)")]
    y = 245
    for i, fila in enumerate(filas):
        for c, t in zip(cols, fila): ax.text(c, y, t, fontsize=6.6, va="top", weight="bold" if i == 0 else "normal")
        y -= 6 if i == 0 else 13
        ax.plot([15, 195], [y + 2.5] * 2, c="#bbb", lw=0.4)
    tx = ["Espesor de diseño: T = 3 mm.",
          "DXF (soportes.dxf): solo la capa CORTE; contorno y agujeros de las 4 piezas (una de cada una).",
          "Agujeros de ángulo L: centros a 17 y 56 del borde inferior, a 19.8 y 36 del borde izquierdo (14 del derecho).",
          "",
          "Montaje:",
          "1) SG90: insertar el servo por la ventana desde la cara frontal; las orejas apoyan sobre el MDF",
          "    y se fijan con tornillo y tuerca por los agujeros Ø2.",
          "2) Sensor: pasar el sensor M24 por el Ø22.6 y fijarlo con sus dos tuercas, una a cada lado del MDF.",
          "3) Motorreductor: insertar la BASE en el hueco de 25 x 4; centrar el motorreductor en el Ø11.8",
          "    y atornillarlo por los 2 agujeros Ø3.6.",
          "4) Atornillar los dos ángulos en L de cada pieza por los Ø4.8 y fijarlos a la estructura de la faja."]
    for i, t in enumerate(tx): ax.text(16, 155 - i * 6.5, t, fontsize=6.6, weight="bold" if t == "Montaje:" else "normal")
    return fig

with PdfPages(OUT + "soportes_planos.pdf") as pdf:
    hoja(pdf, "Soportes: SG90 y\nsensor capacitivo", "SOP-01", 1, 3, "1:1.25", 8, h1, fecha=F)
    hoja(pdf, "Soportes: sostenedor\ny base motorreductor", "SOP-02", 2, 3, "varias", 2, h2, fecha=F)
    fig = notas(); pdf.savefig(fig); plt.close(fig)

doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM; doc.layers.add("CORTE", color=1)
m = doc.modelspace()
def add(P, ox, oy):
    m.add_lwpolyline([(ox, oy), (ox + P["W"], oy), (ox + P["W"], oy + P["H"]), (ox, oy + P["H"])], close=True, dxfattribs={"layer": "CORTE"})
    for a, b, c, d in P["rects"]:
        m.add_lwpolyline([(ox + a, oy + b), (ox + c, oy + b), (ox + c, oy + d), (ox + a, oy + d)], close=True, dxfattribs={"layer": "CORTE"})
    for x, y, r in P["circs"]: m.add_circle((ox + x, oy + y), r, dxfattribs={"layer": "CORTE"})
add(SRV, 6, 6); add(CAP, 62, 6); add(MOT, 118, 6); add(BASE, 174, 6)
doc.saveas(OUT + "soportes.dxf")
print("ok", SRV["W"], SRV["H"], len(SRV["circs"]), CAP["H"], len(CAP["circs"]))
