"""Primer piso del tablero de automatización: base MDF 230 x 180 x 3 (mm), escala 1:1 en el DXF."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import plano
from plano import PdfPages, Rectangle, Circle, hoja
import ezdxf

# estilo del pedido: fondo blanco, líneas negras
plano.RED = plano.BLUE = plano.GR = "black"; plano.FILL = "white"
dim = plano.dim

OUT = os.path.join(os.path.dirname(__file__), "..", "tablero_piso1") + "/"
os.makedirs(OUT, exist_ok=True)
BW, BH, T, SO = 230, 180, 3, 10
AV = "PARA REVISIÓN — NO APTO PARA CORTE"

# ---- ángulos L (dato medido): 2 por ángulo, Ø5; 100 entre ángulos; 23 de borde superior a borde inferior -> 18 entre centros
DL = 5.0; LX = [65.0, 165.0]; LY = [170.0, 152.0]
# ---- módulos (x0, y0 = esquina inferior izquierda). Agujeros relativos a esa esquina.
MODS = [
    dict(n="XL4015", x=60, y=112, w=44, h=21, z=None, d=3.4,          # 2 agujeros en diagonal a 37 entre centros
         holes=[(4.5, 4.5), (39.5, 16.5)], fuente="medido: 44 x 21, 2 agujeros Ø3 en diagonal a 37 (35 x 12, a 4.5 de los bordes)"),
    dict(n="L298N", x=118, y=100, w=43, h=43, z=28, d=3.4,
         holes=[(3, 3), (40, 3), (3, 40), (40, 40)], fuente="43 x 43 x 28, agujeros Ø3 a 37 x 37 (Makerguides; I-CubeX; Ø3 medido)"),
    dict(n="XL4016", x=20, y=36, w=64, h=47, z=26, d=3.4,
         holes=[(1.5, 1.5), (62.5, 1.5), (1.5, 45.5), (62.5, 45.5)], fuente="medido: 64 x 47, 4 agujeros Ø3 en rectángulo 61 x 44; alto 26 (Envistia)"),
    dict(n="PCA9685", x=140, y=55, w=62.5, h=25, z=3, d=3.4,
         holes=[], fuente="medido: 62.5 x 25, 4 agujeros Ø3 — POSICIÓN POR MEDIR"),
]
X3 = dict(n="X3", x=20, y=8, w=85, h=18, lab=["+24V", "0V", "+12V", "0VM", "+5V", "0VS", "MA", "MB"])
X4 = dict(n="X4", x=125, y=8, w=85, h=18, lab=["3V3", "GND", "SDA", "SCL", "IN1", "IN2", "ENA", "RES"])
PCA = MODS[3]
CAB = (PCA["x"], 32, PCA["w"], PCA["y"] - 32)

HOLES = []
for i, x in enumerate(LX):
    for j, y in enumerate(LY): HOLES.append((f"L{i + 1}-{j + 1}", x, y, DL, "Ángulo L (Ø5 medido)"))
for m, pre in zip(MODS, ["A", "H", "B", "P"]):
    for k, (hx, hy) in enumerate(m["holes"]):
        HOLES.append((f"{pre}{k + 1}", m["x"] + hx, m["y"] + hy, m["d"], f"{m['n']} — tornillo M3, separador {SO}"))

def interferencias():
    """Comprueba que agujeros de ángulos L no caigan dentro de ningún módulo (+3 mm de margen)."""
    out = []
    for n, x, y, d, _ in HOLES:
        if not n.startswith("L"): continue
        for m in MODS:
            if m["x"] - 3 - d / 2 < x < m["x"] + m["w"] + 3 + d / 2 and m["y"] - 3 - d / 2 < y < m["y"] + m["h"] + 3 + d / 2:
                out.append((n, m["n"]))
    return out

def base(ax, ox, oy, s, comp=True):
    P = lambda x, y: (ox + x * s, oy + y * s)
    ax.add_patch(Rectangle(P(0, 0), BW * s, BH * s, fc="white", ec="black", lw=1.3))
    for n, x, y, d, _ in HOLES: ax.add_patch(Circle(P(x, y), d / 2 * s, fc="white", ec="black", lw=0.8))
    if not comp: return P
    for m in MODS:
        ax.add_patch(Rectangle(P(m["x"], m["y"]), m["w"] * s, m["h"] * s, fc="none", ec="black", lw=0.7))
        ax.text(*P(m["x"] + m["w"] / 2, m["y"] + m["h"] / 2), m["n"] + ("\n(agujeros por medir)" if not m["holes"] else ""),
                fontsize=5.3, ha="center", va="center")
    for b in (X3, X4):
        ax.add_patch(Rectangle(P(b["x"], b["y"]), b["w"] * s, b["h"] * s, fc="none", ec="black", lw=0.7))
        p = b["w"] / 8
        for k, l in enumerate(b["lab"]):
            if k: ax.plot([ox + (b["x"] + p * k) * s] * 2, [oy + b["y"] * s, oy + (b["y"] + b["h"]) * s], c="black", lw=0.3)
            ax.text(*P(b["x"] + p * (k + .5), b["y"] + b["h"] * 0.68), str(k + 1), fontsize=4.2, ha="center", va="center")
            ax.text(*P(b["x"] + p * (k + .5), b["y"] + b["h"] * 0.3), l, fontsize=3.3, ha="center", va="center")
        ax.text(*P(b["x"] + b["w"] / 2, b["y"] + b["h"] + 3), b["n"], fontsize=5.5, ha="center", weight="bold")
    x, y, w, h = CAB
    ax.add_patch(Rectangle(P(x, y), w * s, h * s, fc="none", ec="black", lw=0.4, hatch="////"))
    ax.text(*P(x + w / 2, y + h / 2), "cables SG90 CH0–CH7", fontsize=4.5, ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.3))
    for i, x in enumerate(LX): ax.text(*P(x, LY[0] + 5), f"ÁNGULO L-{i + 1}", fontsize=5, ha="center", va="bottom", weight="bold")
    return P

def head(ax, t):
    ax.text(105, 276, AV, fontsize=10, ha="center", weight="bold")
    ax.text(105, 269, t, fontsize=8.3, ha="center", weight="bold")

def s1(ax):
    head(ax, "VISTA SUPERIOR ACOTADA — PRIMER PISO — escala 1:1.6 — cotas en mm")
    s = 0.625; ox, oy = 35, 108; P = base(ax, ox, oy, s)
    dim(ax, P(0, BH), P(BW, BH), "230", 10); dim(ax, P(BW, 0), P(BW, BH), "180", 21, vert=True)
    dim(ax, P(0, BH), P(LX[0], BH), f"{LX[0]:g}", 4, fs=4.2); dim(ax, P(LX[0], BH), P(LX[1], BH), "100", 4, fs=4.2)
    dim(ax, P(LX[1], LY[1]), P(LX[1], LY[0]), "18", -4, vert=True, fs=4.2)
    dim(ax, P(LX[1], LY[0]), P(LX[1], BH), "10", -4, vert=True, fs=4.2)
    for m in MODS: dim(ax, P(m["x"], m["y"] + m["h"]), P(m["x"] + m["w"], m["y"] + m["h"]), f"{m['w']:g}", 2.5, fs=4.2)
    X15, L298, X16, _ = MODS
    dim(ax, P(X15["x"], X15["y"]), P(X15["x"], X15["y"] + X15["h"]), "21", -3, vert=True, fs=4.2)
    dim(ax, P(0, 0), P(0, X3["y"]), "8", -5, vert=True, fs=4.2)
    dim(ax, P(0, X16["y"]), P(0, X16["y"] + X16["h"]), "47", -5, vert=True, fs=4.2)
    dim(ax, P(0, 0), P(0, X16["y"]), f"{X16['y']:g}", -11, vert=True, fs=4.2)
    dim(ax, P(0, 0), P(0, X15["y"]), f"{X15['y']:g}", -17, vert=True, fs=4.2)
    dim(ax, P(0, 0), P(0, LY[1]), f"{LY[1]:g}", -23, vert=True, fs=4.2)
    dim(ax, P(BW, L298["y"]), P(BW, L298["y"] + 43), "43", 4, vert=True, fs=4.2)
    dim(ax, P(BW, PCA["y"]), P(BW, PCA["y"] + PCA["h"]), f"{PCA['h']:g}", 4, vert=True, fs=4.2)
    dim(ax, P(BW, 0), P(BW, PCA["y"]), f"{PCA['y']:g}", 11, vert=True, fs=4.2)
    dim(ax, P(BW, 0), P(BW, L298["y"]), f"{L298['y']:g}", 16, vert=True, fs=4.2)
    dim(ax, P(X3["x"], 0), P(X3["x"] + 85, 0), "85 (zona X3)", -5, fs=4.2); dim(ax, P(X4["x"], 0), P(X4["x"] + 85, 0), "85 (zona X4)", -5, fs=4.2)
    tx = ["Borneras (propuesta eléctrica, pendiente de confirmar 24 V y control del L298N desde el ESP32):",
          "X3: 1 +24 V entrada · 2 0 V entrada · 3 +12 V motor · 4 0 V motor · 5 +5 V servos · 6 0 V servos · 7 Motor A · 8 Motor B",
          "X4: 1 3V3 · 2 GND lógica · 3 SDA · 4 SCL · 5 IN1 · 6 IN2 · 7 ENA/PWM · 8 reserva",
          "Los 8 SG90 funcionarán a la vez: este plano NO dimensiona la alimentación de los servos.",
          "Contornos de módulos, borneras y zona de cables = referencia (capa COMPONENTES), no se cortan."]
    for i, t in enumerate(tx): ax.text(16, 86 - i * 6, t, fontsize=5.6, weight="bold" if i == 0 else "normal")

def s2(ax):
    head(ax, "BASE SOLA CON PERFORACIONES — escala 1:1.67 — origen (0,0) en la esquina inferior izquierda")
    s = 0.6; ox, oy = 36, 150; P = base(ax, ox, oy, s, comp=False)
    for n, x, y, d, _ in HOLES: ax.text(*P(x + 3, y + 2.5), n, fontsize=4.2)
    dim(ax, P(0, BH), P(BW, BH), "230", 8); dim(ax, P(BW, 0), P(BW, BH), "180", 8, vert=True)
    rows = [("ID", "X", "Y", "Ø", "Elemento")] + [(n, f"{x:.2f}", f"{y:.2f}", f"{d:g}", e) for n, x, y, d, e in HOLES]
    rows += [("—", "—", "—", "—", "PCA9685: 4 agujeros Ø3 — posición POR MEDIR"),
             ("—", "—", "—", "—", "X3 / X4: fijación POR CONFIRMAR (modelo de bornera)")]
    cx = [16, 30, 48, 66, 78]; y0 = 141
    for i, r in enumerate(rows):
        for c, v in zip(cx, r): ax.text(c, y0 - i * 4.6, v, fontsize=5.0, weight="bold" if i == 0 else "normal")
    ax.plot([15, 195], [y0 - 1.8] * 2, c="black", lw=0.5)

def s3(ax):
    head(ax, "VISTA LATERAL (esquemática, frente) — escala 1:1 — alturas en mm")
    oy = 205; ax.add_patch(Rectangle((15, oy), 180, T, fc="white", ec="black", lw=0.9))
    ax.text(105, oy - 4, "MDF 3 mm", fontsize=5.5, ha="center")
    for m, x in zip(MODS, [18, 98, 58, 148]):
        w = 36
        for sx in (x + 3, x + w - 6): ax.add_patch(Rectangle((sx, oy + T), 3, SO, fc="white", ec="black", lw=0.6))
        ax.add_patch(Rectangle((x, oy + T + SO), w, 1.6, fc="white", ec="black", lw=0.6))
        z = m["z"] or 15
        ax.add_patch(Rectangle((x + 2, oy + T + SO + 1.6), w - 4, z - 1.6, fc="white", ec="black", lw=0.5, ls="-" if m["z"] else ":"))
        dim(ax, (x + w, oy + T + SO), (x + w, oy + T + SO + z), (f"{m['z']:g}" if m["z"] else "?") + ("*" if m["n"] == "PCA9685" else ""), 4, vert=True, fs=4.5)
        dim(ax, (x, oy + T), (x, oy + T + SO), f"{SO}", -3, vert=True, fs=4.5)
        ax.text(x + w / 2, oy - 10, m["n"], fontsize=5.5, ha="center", weight="bold")
        ax.text(x + w / 2, oy - 14, f"total {T + SO + m['z']:g}" if m["z"] else "alto POR MEDIR", fontsize=5, ha="center")
    dim(ax, (15, oy), (15, oy + T), "3", -4, vert=True, fs=4.5)
    tx = ["Montaje y fuentes:",
          f"• Separadores de nylon M3 macho/hembra de {SO} mm (estándar RS PRO / Essentra); MDF Ø3.4 (paso M3, ISO 273 medio).",
          "• Tornillo M3 por debajo del MDF hacia el separador; tuerca M3 sobre la placa."] + \
         [f"• {m['n']}: {m['fuente']}." for m in MODS] + \
         ["• Ángulo L: 2 agujeros Ø5 por ángulo, 18 entre centros (23 de borde a borde), 100 entre ángulos (medido).",
          "   Se supone el agujero superior a 10 del borde trasero; huella del ángulo POR CONFIRMAR.",
          "• *PCA9685: alto 3 = placa sin espadines; sumar espadines y conectores.",
          "• Dejar libres terminales, potenciómetros y disipadores; los cables de los servos salen hacia el frente."]
    for i, t in enumerate(tx): ax.text(16, 172 - i * 6.5, t, fontsize=5.6, weight="bold" if i == 0 else "normal")

with PdfPages(OUT + "tablero_piso1_planos.pdf") as pdf:
    hoja(pdf, "Primer piso:\nvista superior", "TPP-01", 1, 3, "1:1.6", 1, s1)
    hoja(pdf, "Primer piso:\nbase y perforaciones", "TPP-02", 2, 3, "1:1.67", 1, s2)
    hoja(pdf, "Primer piso:\nvista lateral", "TPP-03", 3, 3, "1:1", 1, s3)

# ---------------- DXF 1:1 en mm, capas separadas
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
for n in ["CORTE", "PERFORACIONES", "COMPONENTES", "COTAS", "TEXTOS"]: doc.layers.add(n, color=7)
Msp = doc.modelspace()
def rect(x, y, w, h, l): Msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True, dxfattribs={"layer": l})
def txt(t, x, y, h=2.5):
    Msp.add_text(t, height=h, dxfattribs={"layer": "TEXTOS"}).set_placement((x, y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
rect(0, 0, BW, BH, "CORTE")
for n, x, y, d, _ in HOLES:
    Msp.add_circle((x, y), d / 2, dxfattribs={"layer": "PERFORACIONES"})
    Msp.add_text(n, height=1.8, dxfattribs={"layer": "TEXTOS"}).set_placement((x + 3, y + 2))
for i, x in enumerate(LX): txt(f"ANGULO L-{i + 1}", x, LY[0] + 5, 2.2)
for m in MODS:
    rect(m["x"], m["y"], m["w"], m["h"], "COMPONENTES")
    txt(m["n"] + ("" if m["holes"] else " (agujeros por medir)"), m["x"] + m["w"] / 2, m["y"] + m["h"] / 2, 2.2)
for b in (X3, X4):
    rect(b["x"], b["y"], b["w"], b["h"], "COMPONENTES"); txt(b["n"], b["x"] + b["w"] / 2, b["y"] + b["h"] + 3, 3)
    for k, l in enumerate(b["lab"]): txt(f"{k + 1} {l}", b["x"] + b["w"] / 16 * (2 * k + 1), b["y"] + b["h"] / 2, 1.4)
rect(*CAB, "COMPONENTES"); txt("cables SG90 CH0-CH7", CAB[0] + CAB[2] / 2, CAB[1] + CAB[3] / 2, 2)
txt(AV, BW / 2, BH + 22, 5); txt("Primer piso - base MDF 3 mm - 230 x 180 - mm - escala 1:1", BW / 2, BH + 14, 3)
ds = dict(layer="COTAS")
Msp.add_linear_dim(base=(0, BH + 8), p1=(0, BH), p2=(BW, BH), dxfattribs=ds).render()
Msp.add_linear_dim(base=(BW + 8, 0), p1=(BW, 0), p2=(BW, BH), angle=90, dxfattribs=ds).render()
Msp.add_linear_dim(base=(0, BH + 4), p1=(0, BH), p2=(LX[0], BH), dxfattribs=ds).render()
Msp.add_linear_dim(base=(0, BH + 4), p1=(LX[0], BH), p2=(LX[1], BH), dxfattribs=ds).render()
Msp.add_linear_dim(base=(-8, 0), p1=(0, 0), p2=(0, LY[1]), angle=90, dxfattribs=ds).render()
Msp.add_linear_dim(base=(-14, 0), p1=(0, 0), p2=(0, LY[0]), angle=90, dxfattribs=ds).render()
doc.saveas(OUT + "tablero_piso1.dxf")
print("ok", len(HOLES), "agujeros; interferencias:", interferencias())
