"""Tolva de MDF: láminas de medidas de cada pieza, tomadas de tolva.dxf (Andriy, 13/11/2026)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import plano
from plano import PdfPages, Circle, hoja, poly, dim, BLUE, RED
import ezdxf

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "tolva") + "/"
os.makedirs(OUT, exist_ok=True)

# ---------- lectura del DXF
ents = list(ezdxf.readfile(SRC).modelspace())
polys = [[(p[0], p[1]) for p in e.get_points()] for e in ents if e.dxftype() == "LWPOLYLINE"]
circ = [e for e in ents if e.dxftype() == "CIRCLE"][0]
bb = lambda P: (min(x for x, _ in P), min(y for _, y in P), max(x for x, _ in P), max(y for _, y in P))
inside = lambda P, B: all(B[0] - 1e-6 <= x <= B[2] + 1e-6 and B[1] - 1e-6 <= y <= B[3] + 1e-6 for x, y in P)

def pieza(contorno):
    B = bb(contorno)
    hu = [p for p in polys if p is not contorno and inside(p, B)]
    sh = lambda P: [(x - B[0], y - B[1]) for x, y in P]
    return sh(contorno), [sh(h) for h in hu], (B[2] - B[0], B[3] - B[1])

outer = sorted([p for p in polys if not any(q is not p and inside(p, bb(q)) for q in polys)], key=lambda P: bb(P)[0] + 1000 * (bb(P)[1] > 150))
EXT, LAT, INC = pieza(outer[0]), pieza(outer[2]), pieza(outer[4])          # una de cada par
ABA = pieza(outer[6])
cx, cy = circ.dxf.center.x - bb(outer[6])[0], circ.dxf.center.y - bb(outer[6])[1]; RH = circ.dxf.radius

def dim_al(ax, p1, p2, txt, off, fs=5):
    """Cota alineada a p1-p2, desplazada 'off' (mm de hoja) hacia la izquierda del sentido p1->p2."""
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
    a = (x1 + nx * off, y1 + ny * off); b = (x2 + nx * off, y2 + ny * off)
    k = 1.5 if off >= 0 else -1.5
    for (px, py), (qx, qy) in [((x1, y1), a), ((x2, y2), b)]:
        ax.plot([px, qx + nx * k], [py, qy + ny * k], c=BLUE, lw=0.35)
    ax.annotate("", a, b, arrowprops=dict(arrowstyle="<->", color=BLUE, lw=0.55, shrinkA=0, shrinkB=0))
    ang = math.degrees(math.atan2(uy, ux))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, txt, color=BLUE, fontsize=fs, rotation=ang, ha="center", va="center",
            rotation_mode="anchor", bbox=dict(fc="white", ec="none", pad=0.3))

f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")

def material(ax):
    ax.text(105, 262, "MATERIAL: MDF  —  ESPESOR 3 mm", fontsize=13, ha="center", weight="bold")

def h1(ax):
    ax.text(105, 276, "TOLVA — MEDIDAS DE CADA PIEZA (mm)", fontsize=10, ha="center", weight="bold")
    material(ax)
    C, H, (W, Hh) = EXT; s = 1.0; ox, oy = 35, 85
    T = lambda x, y: (ox + x * s, oy + y * s)
    poly(ax, C, ox, oy, s)
    for h in H: poly(ax, h, ox, oy, s, fc="white")
    xs = sorted({x for x, _ in C}); ys = sorted({y for _, y in C})
    x0, xb0, xb1, x1 = xs[0], xs[1], xs[-2], xs[-1]          # 0, 5, 135, 140
    bot = sorted(x for x, y in C if y == 0)                   # 45, 95
    yk = sorted({y for x, y in C if x == x0})                 # pestañas
    ys_side = sorted({y for x, y in C if x in (xb1, x1)})
    # horizontales
    dim(ax, T(x0, Hh), T(x1, Hh), f(x1 - x0), 12)
    dim(ax, T(xb0, Hh), T(xb1, Hh), f(xb1 - xb0), 6)
    dim(ax, T(x0, Hh), T(xb0, Hh), f(xb0 - x0), 6, fs=4.5)
    dim(ax, T(bot[0], 0), T(bot[1], 0), f(bot[1] - bot[0]), -6)
    dim(ax, T(xb0, 0), T(bot[0], 0), f(bot[0] - xb0), -6, fs=4.8)
    dim(ax, T(bot[1], 0), T(xb1, 0), f(xb1 - bot[1]), -6, fs=4.8)
    # verticales: cadena del lado derecho y total
    chain = [0] + ys_side
    for a, b in zip(chain, chain[1:]): dim(ax, T(x1, a), T(x1, b), f(b - a), 6, vert=True, fs=4.8)
    dim(ax, T(x1, 0), T(x1, Hh), f(Hh), 15, vert=True)
    # ranura horizontal inferior
    hz = [h for h in H if abs(bb(h)[3] - bb(h)[1]) < 4 and abs(bb(h)[2] - bb(h)[0]) > 10][0]; b = bb(hz)
    dim(ax, T(b[0], b[3]), T(b[2], b[3]), f(b[2] - b[0]), 4, fs=4.5)
    dim(ax, T(b[2], b[1]), T(b[2], b[3]), f(b[3] - b[1]), 4, vert=True, fs=4.2)
    dim(ax, T(b[0], 0), T(b[0], b[1]), f(b[1]), -3, vert=True, fs=4.2)
    dim(ax, T(bot[0], b[3]), T(b[0], b[3]), f(b[0] - bot[0]), 9, fs=4.2)
    # ranuras inclinadas del lado derecho: cadena a lo largo del borde inclinado
    p0, p1 = (bot[1], 0), (xb1, ys[1])                      # borde inclinado derecho
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); u = ((p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L)
    sl = [h for h in H if h is not hz and min(x for x, _ in h) > (xb0 + xb1) / 2]
    along = lambda P: sorted((x - p0[0]) * u[0] + (y - p0[1]) * u[1] for x, y in P)
    marks = [0] + sorted(v for h in sl for v in (along(h)[0], along(h)[-1])) + [L]
    for a, c in zip(marks, marks[1:]):
        dim_al(ax, T(p0[0] + u[0] * a, p0[1] + u[1] * a), T(p0[0] + u[0] * c, p0[1] + u[1] * c), f(c - a), -7, fs=4.6)
    dim_al(ax, T(*p0), T(*p1), f(L), -14, fs=5)
    h = sl[0]; n = (u[1], -u[0])
    dist = sorted((x - p0[0]) * n[0] + (y - p0[1]) * n[1] for x, y in h)
    al = along(h); mid = (al[0] + al[-1]) / 2
    e = (p0[0] + u[0] * mid, p0[1] + u[1] * mid)
    f1 = (e[0] + n[0] * dist[-1], e[1] + n[1] * dist[-1]); f2 = (e[0] + n[0] * dist[0], e[1] + n[1] * dist[0])
    g = (f2[0] + n[0] * dist[0] * 1.2, f2[1] + n[1] * dist[0] * 1.2)
    dim_al(ax, T(*f2), T(*f1), f(dist[-1] - dist[0]), 0, fs=4.2)
    dim_al(ax, T(*f1), T(*e), f(-dist[-1]), 0, fs=4.2)
    # ángulo de las caras inclinadas
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    ax.text(*T(bot[1] + 9, 3), f"{ang:.1f}°", fontsize=5, color=BLUE)
    ax.text(*T(W / 2, -16), "1   TAPA DE EXTREMO — 2 unidades — escala 1:1", fontsize=7.5, ha="center", weight="bold")

def h2(ax):
    ax.text(105, 276, "TOLVA — MEDIDAS DE CADA PIEZA (mm)", fontsize=10, ha="center", weight="bold")
    material(ax)
    s = 2 / 3
    # 2 pared lateral
    C, H, (W, Hh) = LAT; ox, oy = 105 - W * s / 2, 178
    T = lambda x, y: (ox + x * s, oy + y * s)
    poly(ax, C, ox, oy, s)
    for h in H: poly(ax, h, ox, oy, s, fc="white")
    dim(ax, T(0, Hh), T(W, Hh), f(W), 6)
    dim(ax, T(W, 0), T(W, Hh), f(Hh), 13, vert=True)
    left = sorted([bb(h) for h in H if bb(h)[0] < W / 2], key=lambda b: b[1])
    ys = [0] + [v for b in left for v in (b[1], b[3])] + [Hh]
    for a, c in zip(ys, ys[1:]): dim(ax, T(W, a), T(W, c), f(c - a), 5, vert=True, fs=4.6)
    b = left[0]
    dim(ax, T(0, b[1] - 4), T(b[0], b[1] - 4), f(b[0]), 0, fs=4.4)
    dim(ax, T(b[0], b[1]), T(b[2], b[1]), f(b[2] - b[0]), -3, fs=4.4)
    ax.text(*T(W / 2, -14), "2   PARED LATERAL — 2 unidades — escala 1:1.5", fontsize=7.5, ha="center", weight="bold")
    # 3 plancha inclinada
    C, H, (W, Hh) = INC; ox, oy = 105 - W * s / 2, 108
    T = lambda x, y: (ox + x * s, oy + y * s)
    poly(ax, C, ox, oy, s)
    xs = sorted({x for x, _ in C})
    dim(ax, T(xs[0], Hh), T(xs[-1], Hh), f(xs[-1] - xs[0]), 9)
    dim(ax, T(xs[1], Hh), T(xs[-2], Hh), f(xs[-2] - xs[1]), 4)
    dim(ax, T(xs[0], 0), T(xs[1], 0), f(xs[1] - xs[0]), -4, fs=4.4)
    ysd = sorted({y for x, y in C if x == xs[-1]})
    ys = [0] + ysd + [Hh]
    for a, c in zip(ys, ys[1:]): dim(ax, T(xs[-1], a), T(xs[-1], c), f(c - a), 5, vert=True, fs=4.6)
    dim(ax, T(xs[-1], 0), T(xs[-1], Hh), f(Hh), 13, vert=True)
    ax.text(*T(W / 2, -13), "3   PLANCHA INCLINADA — 2 unidades — escala 1:1.5", fontsize=7.5, ha="center", weight="bold")
    # 4 tapa de abajo
    C, H, (W, Hh) = ABA; ox, oy = 105 - W * s / 2, 63
    T = lambda x, y: (ox + x * s, oy + y * s)
    poly(ax, C, ox, oy, s)
    ax.add_patch(Circle(T(cx, cy), RH * s, fc="white", ec=RED, lw=1.0))
    dim(ax, T(0, Hh), T(W, Hh), f(W), 6)
    dim(ax, T(W, 0), T(W, Hh), f(Hh), 12, vert=True)
    dim(ax, T(0, cy), T(cx, cy), f(cx), 0, fs=4.6)
    dim(ax, T(cx - RH, 0), T(cx + RH, 0), f"Ø{f(2 * RH)}", -5)
    dim(ax, T(W, 0), T(W, cy), f(cy), 5, vert=True, fs=4.6)
    ax.text(*T(W / 2, -16), "4   TAPA DE ABAJO — 1 unidad — escala 1:1.5", fontsize=7.5, ha="center", weight="bold")

def h3(ax):
    ax.text(105, 276, "TOLVA DE MDF — NOTAS DE CORTE Y ARMADO", fontsize=10, ha="center", weight="bold")
    material(ax)
    cols = [16, 46, 60, 122]
    filas = [("Pieza", "Cant.", "Medidas [mm]", "Uniones"),
             ("1 TAPA", "2", "140 ancho (con lengüetas) x 150 alto;\ncuerpo 130; base 50; caras a 51.3°",
              "4 lengüetas de 5 x 22 a PARED;\n4 ranuras de 18.1 x 3.1 p/ INCL;\n1 ranura de 14.1 x 3.1 abajo"),
             ("2 PARED", "2", "130 x 100", "4 ranuras de 22.1 x 3.1\n(reciben las lengüetas de TAPA)"),
             ("3 INCL", "2", "118 (+2 x 3 lengüetas) = 124\nx 64.03", "4 lengüetas de 3 x 18, entran en las\nranuras inclinadas de TAPA"),
             ("4 TAPA-ABAJO", "1", "115 x 39, agujero Ø35 centrado", "Se pega bajo la boca de la tolva;\nel agujero va sobre la compuerta")]
    y = 245
    for i, fila in enumerate(filas):
        for c, t in zip(cols, fila): ax.text(c, y, t, fontsize=6.6, va="top", weight="bold" if i == 0 else "normal")
        y -= 6 if i == 0 else 13
        ax.plot([15, 195], [y + 2.5] * 2, c="#bbb", lw=0.4)
    notas = [
        "Espesor de diseño: T = 3 mm. Holgura de ranuras: 0.1 mm sobre el ancho y el largo de la lengüeta",
        "(ranuras de 3.1 para MDF de 3; 18.1 para lengüetas de 18; 22.1 para lengüetas de 22).",
        "Si el MDF real mide distinto, medir con calibrador y ajustar el espesor T en el diseño.",
        "DXF (tolva.dxf): contiene solo la capa CORTE; todas las líneas se cortan.",
        "",
        "Armado (orden recomendado):",
        "1) TAPA-1 sobre la mesa.",
        "2) Insertar las dos INCL de canto en sus ranuras inclinadas; sellar el contorno con silicona.",
        "3) Bajar TAPA-2 sobre los extremos libres de las INCL (las lengüetas de las INCL entran a la vez).",
        "4) Deslizar las dos PARED lateralmente sobre las lengüetas de las TAPAS. Pegar con cola blanca o",
        "    cianoacrilato en cada unión; sellar con cinta o silicona las juntas por donde pueda caer frejol.",
        "5) Pegar la TAPA-ABAJO bajo la boca, con el agujero Ø35 centrado sobre la salida.",
        "",
        "Nota: las TAPAS van retranqueadas 3 mm del borde de las PARED (para que las ranuras queden cerradas);",
        "por eso las INCL miden 124 en total y no 130.",
        "Nota: las lengüetas de TAPA sobresalen 5 y la PARED mide 3: quedan 2 mm fuera de la pared.",
        "Nota: la ranura inferior de 14.1 x 3.1 de las TAPAS no recibe ninguna pieza en este diseño",
        "(la TAPA-ABAJO no tiene lengüetas); puede quedar o eliminarse.",
    ]
    for i, t in enumerate(notas): ax.text(16, 178 - i * 6.3, t, fontsize=6.5, weight="bold" if t.startswith("Armado") else "normal")

with PdfPages(OUT + "tolva_planos.pdf") as pdf:
    hoja(pdf, "Tolva: tapa de extremo", "TOL-01", 1, 3, "1:1", 2, h1, material="MDF\ne = 3 mm")
    hoja(pdf, "Tolva: pared, plancha\ny tapa de abajo", "TOL-02", 2, 3, "1:1.5", 5, h2, material="MDF\ne = 3 mm")
    hoja(pdf, "Tolva de MDF: notas\nde corte y armado", "TOL-03", 3, 3, "—", 7, h3, material="MDF\ne = 3 mm")
print("ok", EXT[2], LAT[2], INC[2], ABA[2], (cx, cy, RH))
