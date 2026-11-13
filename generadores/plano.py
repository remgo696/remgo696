"""Utilidades comunes para las láminas A4 (cajetín UPC) y cotas."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages  # noqa: F401  (se reexporta)
from matplotlib.patches import Polygon, Rectangle, Circle  # noqa: F401

RED = "#C8102E"; FILL = "#F3E2C7"; BLUE = "#1565C0"; GR = "#444"
PROYECTO = ("Máquina llenadora de frejol en grano en frascos de vidrio de\n"
            "peso determinado, con colocación de tapa y empaque sellador")


def hoja(pdf, titulo, cod, n, total, escala, cant, draw, autor="Montes Ricaldi,\nAndriy Percy",
         fecha="13/11/2026", material="MDF\ne = 3 mm"):
    fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 210); ax.set_ylim(0, 297); ax.axis("off")
    ax.add_patch(Rectangle((10, 10), 190, 277, fill=False, lw=1.6))
    rows = [10, 25, 37, 49]
    for y in rows[1:]: ax.plot([10, 200], [y, y], c="k", lw=0.9)
    ax.plot([84, 84], [rows[1], rows[3]], c="k", lw=0.9); ax.plot([160, 160], [rows[1], rows[2]], c="k", lw=0.9)
    cols = [10, 43, 77, 98, 113, 136, 149, 170, 190, 200]
    for c in cols[1:-1]: ax.plot([c, c], [rows[0], rows[1]], c="k", lw=0.9)
    lab = lambda x, y, t: ax.text(x + 1, y - 1.6, t, fontsize=4, color=GR, va="top")
    val = lambda x, y, t, fs=6.2: ax.text(x, y, t, fontsize=fs, ha="center", va="center")
    lab(10, rows[3], "TÍTULO"); val(47, rows[2] + 5.2, titulo, 9.5)
    lab(84, rows[3], "PROYECTO"); val(142, rows[2] + 5.2, PROYECTO, 5.8)
    lab(10, rows[2], "UNIVERSIDAD"); val(47, rows[1] + 5, "Universidad Peruana de Ciencias\nAplicadas (UPC)")
    lab(84, rows[2], "CURSO"); val(122, rows[1] + 5, "1AEL0258 Sensores y Acondicionadores ·\nNRC 8522 · 2026-20")
    lab(160, rows[2], "UNIDADES / TOLERANCIA"); val(180, rows[1] + 5, "Cotas en mm\nTol. general ±0.1 mm", 5.6)
    heads = ["AUTOR", "REVISÓ (DOCENTE)", "FECHA", "ESCALA", "MATERIAL", "CANT.", "CÓDIGO", "HOJA", "REV."]
    vals = [autor, "Gutiérrez Chávez,\nMoisés Ricardo", fecha, escala, material, str(cant), cod, f"{n} de {total}", "A"]
    for i, (hd, v) in enumerate(zip(heads, vals)):
        lab(cols[i], rows[1], hd); val((cols[i] + cols[i + 1]) / 2, rows[0] + 6, v, 5.6 if i < 2 else 6.5)
    draw(ax); pdf.savefig(fig); plt.close(fig)


def poly(ax, pts, ox, oy, s=1, fc=FILL, ec=RED, lw=1.0):
    ax.add_patch(Polygon([(ox + x * s, oy + y * s) for x, y in pts], closed=True, fc=fc, ec=ec, lw=lw))


def dim(ax, p1, p2, txt, off, vert=False, fs=5.5):
    (x1, y1), (x2, y2) = p1, p2
    k = 1.5 if off >= 0 else -1.5
    box = dict(fc="white", ec="none", pad=0.3)
    arr = dict(arrowstyle="<->", color=BLUE, lw=0.55, shrinkA=0, shrinkB=0)
    if vert:
        xd = x1 + off
        ax.plot([x1, xd + k], [y1, y1], c=BLUE, lw=0.35); ax.plot([x2, xd + k], [y2, y2], c=BLUE, lw=0.35)
        ax.annotate("", (xd, y1), (xd, y2), arrowprops=arr)
        ax.text(xd, (y1 + y2) / 2, txt, color=BLUE, fontsize=fs, rotation=90, ha="center", va="center", bbox=box)
    else:
        yd = y1 + off
        ax.plot([x1, x1], [y1, yd + k], c=BLUE, lw=0.35); ax.plot([x2, x2], [y2, yd + k], c=BLUE, lw=0.35)
        ax.annotate("", (x1, yd), (x2, yd), arrowprops=arr)
        ax.text((x1 + x2) / 2, yd, txt, color=BLUE, fontsize=fs, ha="center", va="center", bbox=box)
