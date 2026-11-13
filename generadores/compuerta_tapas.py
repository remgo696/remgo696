"""Compuerta corredera del soporte de tapas: bandeja + piñón/cremallera + guía + repisa del SG90.

Ejes (mm): z perpendicular a la pared de 120 (z = 0 cara exterior, z < 0 hacia afuera),
x a lo largo de la pared (ranura de 60 centrada en x = 0). Bandeja dibujada en posición CERRADA.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from plano import *  # noqa
import ezdxf

OUT = os.path.join(os.path.dirname(__file__), "..", "compuerta_tapas") + "/"
os.makedirs(OUT, exist_ok=True)

# ---- engranaje: módulo 2, 20°
M, Z, PA = 2.0, 24, math.radians(20)
RP = M * Z / 2; RA = RP + M; RF = RP - 1.25 * M; RB = RP * math.cos(PA); P = math.pi * M
XP = 31.0                      # línea primitiva de la cremallera
PX, PZ = XP + RP, -76.0        # centro del piñón = eje del servo
STROKE = 70.0                  # recorrido de la bandeja

def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

inv = lambda a: math.tan(a) - a
def psi(r):                    # semiángulo del diente al radio r
    r = max(r, RB)
    return math.pi / (2 * Z) + inv(PA) - inv(math.acos(RB / r))

def pinon():
    pts = []
    rs = [RF] + [RB + (RA - RB) * i / 12 for i in range(13)]
    for k in range(Z):
        c = 2 * math.pi * k / Z
        flank = [(r, c - psi(r)) for r in rs]
        pts += [(r * math.cos(a), r * math.sin(a)) for r, a in flank]
        a0, a1 = c - psi(RA), c + psi(RA)
        pts += [(RA * math.cos(a0 + (a1 - a0) * i / 4), RA * math.sin(a0 + (a1 - a0) * i / 4)) for i in range(1, 4)]
        pts += [(r * math.cos(c + psi(r)), r * math.sin(c + psi(r))) for r, _ in reversed(flank)]
        b0, b1 = c + psi(RF), c + 2 * math.pi / Z - psi(RF)
        pts += [(RF * math.cos(b0 + (b1 - b0) * i / 4), RF * math.sin(b0 + (b1 - b0) * i / 4)) for i in range(1, 4)]
    return pts

# ---- ranura del brazo SG90 (medida: eje Ø7.1, largo 19.6, brazo 5.01 -> 4.1; +0.1 por lado)
RB_H, WR, WT, LS = 3.65, 5.2, 4.3, 19.8
RT = WT / 2; YT = -RB_H + LS - RT
def ranura_brazo():
    yr = math.sqrt(RB_H ** 2 - (WR / 2) ** 2); a = math.degrees(math.atan2(yr, WR / 2))
    return [(WR / 2, yr)] + arc(0, YT, RT, 0, 180, 16) + [(-WR / 2, yr)] + arc(0, 0, RB_H, 180 - a, 360 + a, 40)[1:-1]

# ---- bandeja (coordenadas: x, u = z en posición cerrada)
TIP, TAIL, XL, XR = 72.5, -90.0, -34.0, 28.5     # punta en la ranura opuesta; cola; borde izq. de la cola; raíz de la cremallera
HW = 29.0                                         # medio ancho de la parte que entra (58)
def bandeja():
    pts = [(-HW, TIP), (HW, TIP), (HW, 0), (XR, 0), (XR, -1)]
    hw = lambda x: P / 4 - (x - XP) * math.tan(PA)
    u = -1.0; k = 0
    while True:
        uc = -1 - (k + 0.5) * P - 0.3
        if uc - hw(XR) < -86: break
        pts += [(XR, uc + hw(XR)), (XP + M, uc + hw(XP + M)), (XP + M, uc - hw(XP + M)), (XR, uc - hw(XR))]
        k += 1
    pts += [(XR, TAIL), (XL, TAIL), (XL, 0), (-HW, 0)]
    return pts, k

BAND, NT = bandeja()

# ---- guía y soportes (planta x-z)
BASE = (-40.0, -170.0, 125.0, 170.0)                              # x, z, ancho, largo
RAIL_L = (-40.0, -170.0, 5.5, 168.0)                              # riel izquierdo (z hasta -2)
TAPA_L = (-40.0, -170.0, 13.0, 168.0)                             # tapa guía izquierda
RAIL_R = [(33.5, -170.0, 6.5, 62.0), (33.5, -44.0, 6.5, 41.0)]    # rieles derechos (fuera del piñón)
TAPA_R = [(24.0, -170.0, 16.0, 62.0), (24.0, -44.0, 16.0, 41.0)]
TOPE = (-34.0, -170.0, 67.5, 7.0)                                 # tope de fin de carrera (abierta)
REP = (40.0, -125.0, 32.0, 109.0)                                 # repisa del servo
BLQ = [(40.0, -125.0, 32.0, 15.0), (40.0, -31.0, 32.0, 15.0)]     # bloques bajo la repisa (3 capas c/u)
SERVO_C = PZ + 5.35                                               # centro del cuerpo del SG90 (eje desplazado 5.35)
VENT = (PX - 6.25, SERVO_C - 11.5, 12.5, 23.0)
OREJAS = [(PX, SERVO_C - 13.75), (PX, SERVO_C + 13.75)]
CART = [(0, 0), (60, 0), (0, 40)]                                 # cartela: 60 bajo la base, 40 en la pared

def rp(r): x, z, w, h = r; return [(x, z), (x + w, z), (x + w, z + h), (x, z + h)]

# ======================= PDF =======================
def lam_piezas(ax):
    ax.text(105, 279, "COMPUERTA CORREDERA DE TAPAS — PIEZAS (MDF 3 mm) — cotas en mm", fontsize=8.6, ha="center", weight="bold", color=GR)
    # 2 piñón (1:1)
    cx, cy = 45, 232
    poly(ax, pinon(), cx, cy, 1); poly(ax, ranura_brazo(), cx, cy, 1, fc="white")
    dim(ax, (cx - RA, cy - RA), (cx + RA, cy - RA), f"Ø{2 * RA:g} ext.", -4, fs=4.8)
    dim(ax, (cx - RP, cy + RA), (cx + RP, cy + RA), f"Ø{2 * RP:g} primitivo", 4, fs=4.8)
    ax.text(cx + RA + 2, cy + 8, f"m = 2\nz = {Z}\n20°", fontsize=5, color=BLUE)
    dim(ax, (cx - 5, cy - RB_H), (cx - 5, cy + YT + RT), "19.8", -2, vert=True, fs=4.2)
    ax.text(cx, cy - RA - 12, "2  PIÑÓN (x1) — 1:1", fontsize=6.3, ha="center", weight="bold", color=GR)
    # 3 repisa (1:1.67)
    s = 0.6; rx, rz = 92, 196
    R = lambda x, z: (rx + (x - REP[0]) * s, rz + (z - REP[1]) * s)
    poly(ax, [R(40, -125), R(72, -125), R(72, -16), R(40, -16)], 0, 0)
    vx, vz, vw, vh = VENT
    poly(ax, [R(vx, vz), R(vx + vw, vz), R(vx + vw, vz + vh), R(vx, vz + vh)], 0, 0, fc="white")
    for x, z in OREJAS: ax.add_patch(Circle(R(x, z), 1.0 * s, fc="white", ec=RED, lw=0.7))
    dim(ax, R(40, -125), R(72, -125), "32", -4, fs=4.6)
    dim(ax, R(72, -125), R(72, -16), "109", 4, vert=True, fs=4.6)
    dim(ax, R(vx, -16), R(vx + vw, -16), "12.5", 3, fs=4.2)
    dim(ax, R(40, -16), R(vx, -16), f"{vx - 40:.2f}", 7, fs=4.2)
    dim(ax, R(40, -125), R(40, vz), f"{vz + 125:.2f}", -3, vert=True, fs=4.2)
    dim(ax, R(40, vz), R(40, vz + vh), "23", -3, vert=True, fs=4.2)
    dim(ax, R(PX, OREJAS[0][1]), R(PX, OREJAS[1][1]), "27.5", -9, vert=True, fs=4.2)
    ax.text(rx + 10, rz - 12, "3  REPISA SG90 (x1) — 1:1.67\n2 agujeros Ø2", fontsize=5.6, ha="center", weight="bold", color=GR)
    # 4 base (1:2.5)
    s = 0.4; bx, bz = 140, 196
    poly(ax, [(bx, bz), (bx + 125 * s, bz), (bx + 125 * s, bz + 170 * s), (bx, bz + 170 * s)], 0, 0)
    dim(ax, (bx, bz), (bx + 50, bz), "125", -4, fs=4.6); dim(ax, (bx + 50, bz), (bx + 50, bz + 68), "170", 4, vert=True, fs=4.6)
    ax.text(bx + 25, bz - 12, "4  BASE (x1) — 1:2.5", fontsize=5.8, ha="center", weight="bold", color=GR)
    # 1 bandeja (1:1.67)
    s = 0.6; ox, oy = 48, 80 - TAIL * s
    poly(ax, BAND, ox, oy, s)
    T = lambda x, u: (ox + x * s, oy + u * s)
    dim(ax, T(-HW, TIP), T(HW, TIP), "58", 4, fs=4.8)
    dim(ax, T(XL, TAIL), T(XP + M, TAIL), "67", -4, fs=4.8)
    dim(ax, T(XL, 0), T(-HW, 0), "5", -3, fs=4.2)
    dim(ax, T(XL, TAIL), T(XL, TIP), "162.5", -11, vert=True, fs=4.8)
    dim(ax, T(-HW, 0), T(-HW, TIP), "72.5", -5, vert=True, fs=4.6)
    dim(ax, T(XR, 0), T(XR, TAIL), "90", -3, vert=True, fs=4.2)
    dim(ax, T(XP + M, -1), T(XP + M, -86), f"cremallera m2 · {NT} dientes", 5, vert=True, fs=4.2)
    ax.text(ox, 70, "1  BANDEJA (x1) — 1:1.67", fontsize=6, ha="center", weight="bold", color=GR)
    # 11 cartela (1:2)
    poly(ax, CART, 100, 80, 0.5)
    dim(ax, (100, 80), (130, 80), "60", -4, fs=4.5); dim(ax, (100, 80), (100, 100), "40", -4, vert=True, fs=4.5)
    ax.text(115, 70, "11  CARTELA (x2) — 1:2", fontsize=5.8, ha="center", weight="bold", color=GR)
    # tiras
    tx, ty = 140, 172
    ax.text(tx, ty, "TIRAS (ancho x largo, mm)", fontsize=6, weight="bold", color=GR)
    tiras = [("5", "riel izquierdo", "5.5 x 168", 1), ("6", "tapa guía izquierda", "13 x 168", 1),
             ("7", "riel derecho", "6.5 x 62  y  6.5 x 41", "1+1"), ("8", "tapa guía derecha", "16 x 62  y  16 x 41", "1+1"),
             ("9", "tope fin de carrera", "67.5 x 7", 1), ("10", "bloque (3 capas)", "32 x 15", 6)]
    for k, (n, d, m, c) in enumerate(tiras):
        y = ty - 7 - k * 6
        ax.text(tx, y, n, fontsize=5.4); ax.text(tx + 6, y, d, fontsize=5.4); ax.text(tx + 6, y - 2.6, f"{m}   (x{c})", fontsize=5, color=BLUE)

def lam_armado(ax):
    ax.text(105, 279, "ARMADO — VISTA SUPERIOR (cerrada) Y CORTE LATERAL — escala 1:2", fontsize=8.6, ha="center", weight="bold", color=GR)
    s = 0.5; ox, oy = 95, 233
    T = lambda x, z: (ox + x * s, oy + z * s)
    ax.add_patch(Rectangle(T(-60, 0), 120 * s, 3 * s, fc="#ddd", ec="k", lw=0.8))
    ax.add_patch(Rectangle(T(-60, 71), 120 * s, 3 * s, fc="#ddd", ec="k", lw=0.8))
    for xx in (-37.35, 34.25): ax.add_patch(Rectangle(T(xx, 3), 3.1 * s, 68 * s, fc="#ddd", ec="k", lw=0.6))
    poly(ax, rp(BASE), *T(0, 0), s, fc="#fbf6ee", ec="k", lw=0.6)
    poly(ax, BAND, *T(0, 0), s, fc=FILL, lw=0.8)
    for r in [RAIL_L, TOPE] + RAIL_R + BLQ: poly(ax, rp(r), *T(0, 0), s, fc="#e7d3b0", ec="k", lw=0.5)
    poly(ax, pinon(), *T(PX, PZ), s, fc="#cfe0f3", ec=BLUE, lw=0.6)
    poly(ax, ranura_brazo(), *T(PX, PZ), s, fc="white", ec=BLUE, lw=0.5)
    ax.add_patch(Rectangle(T(*VENT[:2]), VENT[2] * s, VENT[3] * s, fc="none", ec="k", lw=0.6))
    dim(ax, T(-40, -170), T(85, -170), "125", -5)
    dim(ax, T(85, -170), T(85, 0), "170", 5, vert=True)
    dim(ax, T(0, 0), T(PX, 0), f"{PX:g}", -9, fs=4.6)
    dim(ax, T(-60, -170), T(-60, PZ), f"{170 + PZ:g}", -4, vert=True, fs=4.6)
    ax.text(*T(-60, 36), "columna\nde tapas", fontsize=5, ha="right", va="center")
    ax.text(*T(PX + 30, PZ), "piñón /\neje SG90", fontsize=5, color=BLUE, va="center")
    # corte lateral
    s2 = 0.5; cx, cy = 95, 108
    C = lambda z, y: (cx + z * s2, cy + (y - 56.5) * s2)
    ax.add_patch(Rectangle(C(0, 0), 3 * s2, 118 * s2, fc="#ddd", ec="k", lw=0.7))
    ax.add_patch(Rectangle(C(71, 0), 3 * s2, 118 * s2, fc="#ddd", ec="k", lw=0.7))
    ax.add_patch(Rectangle(C(-170, 53.5), 170 * s2, 3 * s2, fc="#fbf6ee", ec="k", lw=0.6))
    ax.add_patch(Rectangle(C(-90, 56.5), (90 + TIP) * s2, 3 * s2, fc=FILL, ec=RED, lw=0.8))
    ax.add_patch(Rectangle(C(PZ - RA, 56.5), 2 * RA * s2, 3 * s2, fc="#cfe0f3", ec=BLUE, lw=0.6))
    for z0 in (-125, -31): ax.add_patch(Rectangle(C(z0, 56.5), 15 * s2, 9 * s2, fc="#e7d3b0", ec="k", lw=0.5))
    ax.add_patch(Rectangle(C(-125, 65.5), 109 * s2, 3 * s2, fc="#e7d3b0", ec="k", lw=0.6))
    ax.add_patch(Rectangle(C(SERVO_C - 11.25, 68.5), 22.5 * s2, 22 * s2, fc="#eee", ec="k", lw=0.6))
    poly(ax, [(0, 0), (-60, 0), (0, -40)], *C(0, 53.5), s2, fc="#e7d3b0", ec="k", lw=0.5)
    for k in range(2): ax.add_patch(Rectangle(C(3.5, 59.5 + 20 * k), 67 * s2, 20 * s2, fc="none", ec="k", lw=0.4))
    ax.text(*C(37, 69.5), "tapa Ø67 x 20", fontsize=4.6, ha="center", va="center")
    ax.text(*C(SERVO_C, 80), "SG90", fontsize=5, ha="center")
    dim(ax, C(-140, 56.5), C(-140, 65.5), "9", -3, vert=True, fs=4.5)
    dim(ax, C(74, 0), C(74, 56.5), "56.5", 4, vert=True, fs=4.5)
    dim(ax, C(-90, 53.5), C(TIP, 53.5), "162.5", -21, fs=4.6)
    notas = ["Recorrido de la bandeja: 70 mm (piñón Ø48 primitivo, giro ≈ 167°).",
             "Cerrada: la punta entra 1.5 mm en la ranura de la pared opuesta y el escalón de 5 mm de la cola tope contra la pared.",
             "Abierta: la cola choca con el tope (9) a 3 mm del final de la carrera.",
             "El peso de las tapas apoya en las dos ranuras de la columna; el SG90 solo mueve la bandeja.",
             "Bloques (10): 3 capas pegadas = 9 mm; ajustar con arandelas hasta que el brazo quede dentro del piñón.",
             "Base, rieles, tapas guía, tope y cartelas: cola blanca. La base apoya contra la pared de 120 bajo la ranura."]
    for i, t in enumerate(notas): ax.text(16, 73 - i * 4.2, t, fontsize=5.2, color=GR)

with PdfPages(OUT + "compuerta_tapas_planos.pdf") as pdf:
    hoja(pdf, "Compuerta corredera\nde tapas: piezas", "CTA-01", 1, 2, "varias", "13 piezas", lam_piezas)
    hoja(pdf, "Compuerta corredera\nde tapas: armado", "CTA-02", 2, 2, "1:2", "—", lam_armado)

# ======================= DXF (piezas 1:1) =======================
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
doc.layers.add("CORTE", color=1); doc.layers.add("TEXTO", color=5)
msp = doc.modelspace()
def add(pts, ox, oy):
    msp.add_lwpolyline([(ox + x, oy + y) for x, y in pts], close=True, dxfattribs={"layer": "CORTE"})
def lbl(t, x, y): msp.add_text(t, height=3, dxfattribs={"layer": "TEXTO"}).set_placement((x, y))
add(BAND, 40, 95); lbl("1 BANDEJA", 30, 0)
add(pinon(), 110, 30); add(ranura_brazo(), 110, 30); lbl("2 PINON", 95, 0)
add([(0, 0), (32, 0), (32, 109), (0, 109)], 145, 5)
add(rp((VENT[0] - 40 + 145, VENT[1] + 125 + 5, VENT[2], VENT[3])), 0, 0)
for x, z in OREJAS: msp.add_circle((x - 40 + 145, z + 125 + 5), 1.0, dxfattribs={"layer": "CORTE"})
lbl("3 REPISA", 145, 117)
add([(0, 0), (125, 0), (125, 170), (0, 170)], 185, 5); lbl("4 BASE", 230, 178)
x = 320
for nombre, w, h, c in [("5", 5.5, 168, 1), ("6", 13, 168, 1), ("7", 6.5, 62, 1), ("7", 6.5, 41, 1),
                        ("8", 16, 62, 1), ("8", 16, 41, 1)]:
    add([(0, 0), (w, 0), (w, h), (0, h)], x, 5); lbl(nombre, x, h + 8); x += w + 5
add([(0, 0), (67.5, 0), (67.5, 7), (0, 7)], 320, 185); lbl("9", 390, 186)
for i in range(6): add([(0, 0), (32, 0), (32, 15), (0, 15)], 185 + (i % 3) * 37, 185 + (i // 3) * 20)
lbl("10 BLOQUES x6", 185, 228)
for i in range(2): add(CART, 300 + i * 65, 200)
lbl("11 CARTELAS", 300, 245)
doc.saveas(OUT + "compuerta_tapas.dxf")
print("ok", NT, "dientes; Ø", 2 * RA, "giro", math.degrees(STROKE / RP))
