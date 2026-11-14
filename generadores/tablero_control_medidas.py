"""Tablero de control (START/STOP + ESP32): una sola hoja de medidas, desde tablero_control.dxf."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import plano
from plano import PdfPages, Circle, Rectangle, hoja, poly, dim, RED, BLUE
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import ezdxf

D = os.path.join(os.path.dirname(__file__), "..", "tablero_control") + "/"
m = ezdxf.readfile(D + "tablero_control.dxf").modelspace()
circ = [(e.dxf.center.x, e.dxf.center.y, e.dxf.radius) for e in m if e.dxftype() == "CIRCLE"]
corte = [[(p[0], p[1]) for p in e.get_points("xy")] for e in m if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "CORTE"]
grab = [[(p[0], p[1]) for p in e.get_points("xy")] for e in m if e.dxf.layer == "GRABADO"]
bb = lambda P: (min(x for x, _ in P), min(y for _, y in P), max(x for x, _ in P), max(y for _, y in P))
placa = max(corte, key=lambda P: bb(P)[2]); W, H = bb(placa)[2], bb(placa)[3]
ranuras = sorted([bb(P) for P in corte if P is not placa], key=lambda b: b[1])
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")

def dibuja(ax, ox, oy, s, x0=0, y0=0, solo=None):
    T = lambda x, y: (ox + (x - x0) * s, oy + (y - y0) * s)
    if solo is None:
        poly(ax, [(0, 0), (W, 0), (W, H), (0, H)], ox, oy, s)
        verts, codes = [], []
        for P in grab:
            for i, p in enumerate(P):
                verts.append(T(*p)); codes.append(Path.MOVETO if i == 0 else Path.LINETO)
            verts.append(T(*P[0])); codes.append(Path.CLOSEPOLY)
        ax.add_patch(PathPatch(Path(verts, codes), fc="#555", ec="none"))
    else:
        poly(ax, [T(solo[0], solo[1]), T(solo[2], solo[1]), T(solo[2], solo[3]), T(solo[0], solo[3])], 0, 0)
    for x, y, r in circ:
        if solo and not (solo[0] < x < solo[2] and solo[1] < y < solo[3]): continue
        ax.add_patch(Circle(T(x, y), r * s, fc="white", ec=RED, lw=0.9))
    for a, b, c, d in ranuras: poly(ax, [T(a, b), T(c, b), T(c, d), T(a, d)], 0, 0, fc="white")
    return T

def lamina(ax):
    ax.text(105, 276, "TABLERO DE CONTROL — MEDIDAS (mm)", fontsize=10, ha="center", weight="bold")
    ax.text(105, 262, "MATERIAL: MDF  —  ESPESOR 3 mm", fontsize=13, ha="center", weight="bold")
    s = 0.7; ox, oy = 35, 140
    T = dibuja(ax, ox, oy, s)
    bot = sorted({(x, y, r) for x, y, r in circ if r > 2.5}, key=lambda c: (-c[1], c[0]))
    (xb, y1, rb), (xl, _, rl) = bot[0], bot[1]
    y2 = bot[2][1]
    dim(ax, T(0, H), T(W, H), f(W), 12)
    dim(ax, T(0, H), T(xb, H), f(xb), 5, fs=4.8); dim(ax, T(xb, H), T(xl, H), f(xl - xb), 5, fs=4.8)
    dim(ax, T(W, 0), T(W, H), f(H), 14, vert=True)
    dim(ax, T(W, 0), T(W, y2), f(y2), 6, vert=True, fs=4.8); dim(ax, T(W, y2), T(W, y1), f(y1 - y2), 6, vert=True, fs=4.8)
    dim(ax, T(xb - rb, y1 + rb + 2), T(xb + rb, y1 + rb + 2), f"Ø{f(2 * rb)}", 0, fs=4.6)
    dim(ax, T(xl - rl, y1 + rl + 5), T(xl + rl, y1 + rl + 5), f"Ø{f(2 * rl)}", 0, fs=4.4)
    gx = min(bb(P)[0] for P in grab)
    dim(ax, T(0, y1 - 8), T(gx, y1 - 8), f(gx), 0, fs=4.4)
    gs = [P for P in grab if bb(P)[1] > (y1 + y2) / 2]; gb = (min(bb(P)[1] for P in gs), max(bb(P)[3] for P in gs))
    dim(ax, T(gx - 3, gb[0]), T(gx - 3, gb[1]), f(gb[1] - gb[0]), -2, vert=True, fs=4.2)
    # zona ESP32 en la vista general: posición de la ranura inferior
    a, b, c, d = ranuras[0]
    dim(ax, T(0, 0), T(0, b), f(b), -5, vert=True, fs=4.6)
    dim(ax, T(0, 0), T(a, 0), f(a), -5, fs=4.6)
    ax.text(*T(W / 2, -15), "1   TABLERO DE CONTROL — 1 unidad — escala 1:1.43", fontsize=7, ha="center", weight="bold")
    # detalle ESP32 (1.6:1)
    zona = (10, 22, 66, 58); s2 = 1.3; ox2, oy2 = 69, 64
    T2 = dibuja(ax, ox2, oy2, s2, zona[0], zona[1], solo=zona)
    hs = sorted({(x, y) for x, y, r in circ if r < 2})
    hx = sorted({x for x, _ in hs}); hy = sorted({y for _, y in hs}); rh = [r for *_, r in circ if r < 2][0]
    dim(ax, T2(hx[0], hy[1]), T2(hx[1], hy[1]), f(hx[1] - hx[0]), 9, fs=4.8)
    dim(ax, T2(hx[1], hy[0]), T2(hx[1], hy[1]), f(hy[1] - hy[0]), 10, vert=True, fs=4.8)
    dim(ax, T2(hx[0] - rh, hy[0] - 4), T2(hx[0] + rh, hy[0] - 4), f"Ø{f(2 * rh)}", -2, fs=4.4)
    a, b, c, d = ranuras[0]; a2, b2, c2, d2 = ranuras[1]
    dim(ax, T2(a, b), T2(c, b), f(c - a), -6, fs=4.8)
    dim(ax, T2(c, b), T2(c, d), f(d - b), 4, vert=True, fs=4.4)
    dim(ax, T2(zona[0], (b + d) / 2), T2(zona[0], (b2 + d2) / 2), f((b2 + d2) / 2 - (b + d) / 2), -4, vert=True, fs=4.6)
    dim(ax, T2(hx[0], d2 + 6), T2(a, d2 + 6), f(a - hx[0]), 0, fs=4.4)
    ax.text(ox2 + (zona[2] - zona[0]) * s2 / 2, oy2 - 9, "DETALLE ZONA ESP32 — escala 1.3:1", fontsize=6.5, ha="center", weight="bold")

with PdfPages(D + "tablero_control_planos.pdf") as pdf:
    hoja(pdf, "Tablero de control", "TAB-01", 1, 1, "1:1.43 / 1.3:1", 1, lamina, fecha="14/11/2026")
print("ok", W, H, ranuras)
