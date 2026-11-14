"""Compuerta de la tolva y puertitas de servo: láminas de medidas desde Compuerta_puerta_servo.dxf."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import plano
from plano import PdfPages, Rectangle, hoja, poly, dim, BLUE
import matplotlib.pyplot as plt
import ezdxf

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "compuerta_puerta_servo") + "/"
os.makedirs(OUT, exist_ok=True)
F = "14/11/2026"
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")

pls = [[(p[0], p[1]) for p in e.get_points("xy")] for e in ezdxf.readfile(SRC).modelspace() if e.dxftype() == "LWPOLYLINE"]
bb = lambda P: (min(x for x, _ in P), min(y for _, y in P), max(x for x, _ in P), max(y for _, y in P))
outs = sorted([p for p in pls if bb(p)[2] - bb(p)[0] > 10], key=lambda P: bb(P)[0])
def pieza(o):
    x0, y0, x1, y1 = bb(o)
    s = [p for p in pls if p is not o and bb(p)[0] > x0 and bb(p)[2] < x1 and bb(p)[1] > y0 and bb(p)[3] < y1][0]
    cx = (x0 + x1) / 2
    sh = lambda P: [(x - cx, y - y0) for x, y in P]
    return sh(o), sh(s), (x1 - x0, y1 - y0), bb(s)[1] - y0          # contorno, ranura, tamaño, inicio de ranura
CMP = pieza(outs[0]); P115, P125, P185 = sorted([pieza(o) for o in outs[1:]], key=lambda p: p[2][1])
RB, WR, WT, LS, R = 3.65, 5.2, 4.3, 19.8, 7.0

def material(ax):
    ax.text(105, 262, "MATERIAL: MDF  —  ESPESOR 3 mm", fontsize=13, ha="center", weight="bold")

def cabecera(ax):
    ax.text(105, 276, "COMPUERTA Y PUERTITAS DEL SERVO — MEDIDAS DE CADA PIEZA (mm)", fontsize=9.5, ha="center", weight="bold")
    material(ax)

def tira(ax, P, ox, oy, s, titulo, disco=None):
    C, S, (W, H), ys = P
    T = lambda x, y: (ox + x * s, oy + y * s)
    poly(ax, C, ox, oy, s); poly(ax, S, ox, oy, s, fc="white")
    eje = ys + RB
    dim(ax, T(-R, H if not disco else H - 2 * disco), T(R, H if not disco else H - 2 * disco), "14", 4 if not disco else -4, fs=4.8)
    dim(ax, T(R if not disco else disco, 0), T(R if not disco else disco, H), f(H), 14, vert=True)
    dim(ax, T(-R, 0), T(-R, eje), f(eje), -5, vert=True, fs=4.6)
    dim(ax, T(-R, 0), T(-R, ys), f(ys), -11, vert=True, fs=4.4)
    if disco:
        dim(ax, T(-disco, H - disco), T(disco, H - disco), f"Ø{f(2 * disco)}", 0, fs=4.8)
        dim(ax, T(disco, eje), T(disco, H - disco), f(H - disco - eje), 7, vert=True, fs=4.6)
    ax.text(*T(R + 1, 2), "R7", fontsize=4.8, color=BLUE)
    ax.text(*T(0, -9), titulo, fontsize=6.3, ha="center", weight="bold")

def h1(ax):
    cabecera(ax)
    tira(ax, CMP, 60, 120, 1.0, "1   COMPUERTA — 1 unidad — 1:1", disco=19)
    # detalle de la ranura (4:1)
    s = 4; ox, oy = 150, 120
    C, S, _, ys = P125
    T = lambda x, y: (ox + x * s, oy + (y - ys - RB) * s)
    poly(ax, [(x, y) for x, y in S], ox, oy - (ys + RB) * s, s, fc="white")
    yt = ys + LS
    dim(ax, T(-RB, ys + RB), T(RB, ys + RB), "Ø7.3", -17, fs=4.8)
    dim(ax, T(RB + 2, ys), T(RB + 2, yt), f(LS), 5, vert=True, fs=4.8)
    yr = ys + RB + (RB ** 2 - (WR / 2) ** 2) ** 0.5
    dim(ax, T(-WR / 2, yr), T(WR / 2, yr), f(WR), 0, fs=4.4)
    dim(ax, T(-WT / 2, yt), T(WT / 2, yt), f(WT), 5, fs=4.6)
    ax.text(ox, oy - 26, "DETALLE RANURA DEL BRAZO SG90\n(igual en todas las piezas) — 4:1", fontsize=6, ha="center", weight="bold")

def h2(ax):
    cabecera(ax)
    s = 1.0
    tira(ax, P115, 45, 65, s, "2   PUERTITA 115 — 2 unid.")
    tira(ax, P185, 105, 65, s, "3   PUERTITA 185 — 1 unid.")
    tira(ax, P125, 165, 65, s, "4   PUERTITA 125 — 2 unid.")
    ax.text(105, 52, "escala 1:1", fontsize=6, ha="center")

def notas():
    fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 210); ax.set_ylim(0, 297); ax.axis("off")
    ax.add_patch(Rectangle((10, 10), 190, 277, fill=False, lw=1.6))
    ax.text(105, 276, "COMPUERTA Y PUERTITAS DEL SERVO — NOTAS DE CORTE Y MONTAJE", fontsize=9.5, ha="center", weight="bold")
    material(ax)
    cols = [16, 62, 76, 136]
    filas = [("Pieza", "Cant.", "Medidas [mm]", "Función"),
             ("1 Compuerta", "1", "94 x 38; disco Ø38; mango 14;\neje a 8.65 de la punta", "tapa el agujero Ø35 de la\ntolva (A5)"),
             ("2 Puertita 115", "2", "115 x 14; eje a 25 de la punta", "tope de frascos sobre la faja"),
             ("3 Puertita 185", "1", "185 x 14; eje a 25 de la punta", "tope de frascos sobre la faja"),
             ("4 Puertita 125", "2", "125 x 14; eje a 47 de la punta", "tope de frascos sobre la faja"),
             ("Ranura brazo SG90", "1 c/u", "Ø7.3; largo 19.8; brazo 5.2 → 4.3", "aloja el brazo simple del SG90")]
    y = 245
    for i, fila in enumerate(filas):
        for c, t in zip(cols, fila): ax.text(c, y, t, fontsize=6.6, va="top", weight="bold" if i == 0 else "normal")
        y -= 6 if i == 0 else 12
        ax.plot([15, 195], [y + 2.5] * 2, c="#bbb", lw=0.4)
    tx = ["Espesor de diseño: T = 3 mm. Punta redondeada R7 en todas las piezas.",
          "Ranura del brazo: brazo SG90 medido (eje Ø7.1, largo 19.6, 5.01 en la raíz y 4.1 en la punta) + 0.1 de holgura por lado.",
          "El centro del círculo Ø7.3 es el eje de giro del servo.",
          "DXF (Compuerta_puerta_servo.dxf): solo la capa CORTE; una pieza de cada tipo.",
          "",
          "Montaje:",
          "1) Encajar el brazo del SG90 en la ranura y fijarlo con su tornillo central; si queda flojo, una gota de pegamento.",
          "2) Antes de montar, llevar el servo a 0° y colocar la pieza en su posición abierta.",
          "3) Compuerta: el disco Ø38 cubre el agujero Ø35 de la tapa de abajo de la tolva; gira por debajo de ella.",
          "4) Puertitas: se apoyan en la guía de MDF, que absorbe el empuje del frasco; el servo solo las gira."]
    for i, t in enumerate(tx): ax.text(16, 160 - i * 6.5, t, fontsize=6.4, weight="bold" if t == "Montaje:" else "normal")
    return fig

with PdfPages(OUT + "compuerta_puerta_servo_planos.pdf") as pdf:
    hoja(pdf, "Compuerta de la tolva", "CPS-01", 1, 2, "1:1 / 4:1", 1, h1, fecha=F)
    hoja(pdf, "Puertitas del servo", "CPS-02", 2, 2, "1:1", 5, h2, fecha=F)
    fig = notas(); pdf.savefig(fig); plt.close(fig)
print("ok", CMP[2], CMP[3], P115[2], P115[3], P185[2], P185[3], P125[2], P125[3])
