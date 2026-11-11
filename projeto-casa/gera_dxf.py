"""Gera a planta de layout da versão final (L) em DXF (AutoCAD R2013, milímetros)."""
import json, math, sys
import ezdxf
from ezdxf.enums import TextEntityAlignment

SRC = sys.argv[1]
OUT = sys.argv[2]
d = json.load(open(SRC))

K = 1000 / 85          # px da planta → mm
X0, Y0 = 92, 1040      # origem: canto esquerdo da divisa, linha do vizinho de baixo
P = lambda x, y: ((x - X0) * K, (Y0 - y) * K)
T = 150                # espessura de parede (mm)

doc = ezdxf.new("R2013", setup=True)
doc.header["$INSUNITS"] = 4      # milímetros
doc.header["$MEASUREMENT"] = 1
msp = doc.modelspace()

LAYERS = {
    "ARQ-PAREDE": 7, "ARQ-PAREDE-HACHURA": 8, "ARQ-JANELA": 4, "ARQ-PORTA": 3,
    "ARQ-PORTICO": 30, "ARQ-MOBILIARIO": 9, "ARQ-MOBILIARIO-TEXTO": 9,
    "ARQ-AMBIENTE": 7, "ARQ-AREA": 141, "ARQ-DIVISA": 6, "ARQ-EXTERNO": 8,
    "ARQ-ESCADA": 8, "ARQ-COTA": 1, "ARQ-CARIMBO": 7,
}
for name, color in LAYERS.items():
    doc.layers.add(name, color=color)
doc.layers.get("ARQ-PAREDE").dxf.lineweight = 50
doc.layers.get("ARQ-DIVISA").dxf.linetype = "DASHED"
doc.layers.get("ARQ-PORTICO").dxf.linetype = "DASHED"
doc.layers.get("ARQ-AREA").off()  # polígonos de área ficam desligados por padrão

style = doc.styles.get("Standard")
style.dxf.font = "arial.ttf"


def wall_poly(x1, y1, x2, y2, t=T):
    (ax, ay), (bx, by) = P(x1, y1), P(x2, y2)
    L = math.hypot(bx - ax, by - ay) or 1
    ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = -uy * t / 2, ux * t / 2
    ax, ay, bx, by = ax - ux * t / 2, ay - uy * t / 2, bx + ux * t / 2, by + uy * t / 2
    return [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)], (ux, uy, nx, ny)


# paredes e janelas
for x1, y1, x2, y2, kind in d["walls"]:
    pts, (ux, uy, nx, ny) = wall_poly(x1, y1, x2, y2)
    if kind == "w":
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "ARQ-PAREDE"})
        h = msp.add_hatch(color=8, dxfattribs={"layer": "ARQ-PAREDE-HACHURA"})
        h.paths.add_polyline_path(pts, is_closed=True)
    else:
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "ARQ-JANELA"})
        (ax, ay), (bx, by) = P(x1, y1), P(x2, y2)
        msp.add_line((ax, ay), (bx, by), dxfattribs={"layer": "ARQ-JANELA"})
        if kind == "h":
            mx, my = (ax + bx) / 2, (ay + by) / 2
            msp.add_text("JANELA ALTA h=1600", height=80, dxfattribs={"layer": "ARQ-JANELA"}).set_placement(
                (mx + nx * 3, my + ny * 3), align=TextEntityAlignment.MIDDLE_CENTER)

# portas: [x1,y1,x2,y2, sentido de abertura em px (dx,dy), tipo]
DOORS = [
    (685, 78, 685, 144, (-1, 0), "entrada"),     # entrada, de frente para a escada
    (850, 175, 850, 250, None, "correr"),        # lavanderia
    (470, 110, 470, 180, (-1, 0), "giro"),       # hall → escritório
    (520, 230, 580, 230, (0, 1), "giro"),        # hall → despensa
    (685, 320, 685, 380, (-1, 0), "giro"),       # foyer → vestíbulo
    (543, 320, 543, 380, (-1, 0), "giro"),       # vestíbulo → quarto das crianças
    (560, 385, 625, 385, (0, 1), "giro"),        # vestíbulo → banho das crianças
    (500, 400, 500, 465, (1, 0), "giro"),        # quarto das crianças → banho
    (1058, 780, 1110, 780, (0, 1), "giro"),      # sala → quarto do casal
    (960, 800, 960, 870, (-1, 0), "giro"),       # quarto do casal → closet
    (735, 775, 800, 775, (0, 1), "giro"),        # closet → banho do casal (porta existente)
]
for x1, y1, x2, y2, sw, kind in DOORS:
    (ax, ay), (bx, by) = P(x1, y1), P(x2, y2)
    w = math.hypot(bx - ax, by - ay)
    if kind == "correr":
        ux, uy = (bx - ax) / w, (by - ay) / w
        for off, s0 in ((-30, 0.0), (30, 0.4)):
            nx, ny = -uy * off, ux * off
            msp.add_line((ax + ux * w * s0 + nx, ay + uy * w * s0 + ny), (ax + ux * w * (s0 + 0.6) + nx, ay + uy * w * (s0 + 0.6) + ny),
                         dxfattribs={"layer": "ARQ-PORTA"})
        continue
    dx, dy = sw[0], -sw[1]           # eixo y invertido no DXF
    tip = (ax + dx * w, ay + dy * w)
    msp.add_line((ax, ay), tip, dxfattribs={"layer": "ARQ-PORTA"})
    a_leaf = math.degrees(math.atan2(tip[1] - ay, tip[0] - ax))
    a_jamb = math.degrees(math.atan2(by - ay, bx - ax))
    start, end = sorted([a_leaf, a_jamb])
    if end - start > 180:
        start, end = end, start + 360
    msp.add_arc((ax, ay), w, start, end, dxfattribs={"layer": "ARQ-PORTA"})
    if kind == "entrada":
        msp.add_text("PORTA DE ENTRADA ~900x2400", height=90, dxfattribs={"layer": "ARQ-PORTA"}).set_placement(
            (ax + 1300, (ay + by) / 2), align=TextEntityAlignment.MIDDLE_CENTER)

# pórtico de madeira (projeção, acima)
pa, pb = d["portal"]
(ax, ay), (bx, by) = P(pa, 305), P(pb, 305)
msp.add_lwpolyline([(ax, ay - 125), (bx, by - 125), (bx, by + 125), (ax, ay + 125)], close=True, dxfattribs={"layer": "ARQ-PORTICO"})
for x in (ax, bx - 200):
    msp.add_lwpolyline([(x, ay - 100), (x + 200, ay - 100), (x + 200, ay + 100), (x, ay + 100)], close=True, dxfattribs={"layer": "ARQ-PORTICO"})
msp.add_text("PÓRTICO DE MADEIRA (PROJEÇÃO)", height=80, dxfattribs={"layer": "ARQ-PORTICO"}).set_placement(
    ((ax + bx) / 2, ay - 260), align=TextEntityAlignment.MIDDLE_CENTER)

# ambientes: nome, área e polígono
NAMES = {"telhado": "TELHADO (NÍVEL DO PISO)", "ext": "ÁREA EXTERNA (A CONFIRMAR)",
         "escada": "ESCADA - DESCE P/ QUINTAL", "sala": "ESTAR / JANTAR / COZINHA"}
for key, r in d["rooms"].items():
    if r.get("hide"):
        continue
    pts = [tuple(map(float, p.split(","))) for p in r["p"].split()]
    out = r.get("out")
    layer = "ARQ-EXTERNO" if out else "ARQ-AREA"
    msp.add_lwpolyline([P(*p) for p in pts], close=True, dxfattribs={"layer": layer})
    if r.get("hatch"):
        h = msp.add_hatch(color=8, dxfattribs={"layer": "ARQ-EXTERNO"})
        h.set_pattern_fill("ANSI31", scale=40)
        h.paths.add_polyline_path([P(*p) for p in pts], is_closed=True)
    name = NAMES.get(key, r["n"]).upper()
    lx, ly = P(*r["l"])
    msp.add_text(name, height=120, dxfattribs={"layer": "ARQ-AMBIENTE"}).set_placement((lx, ly), align=TextEntityAlignment.MIDDLE_CENTER)
    if r.get("a"):
        a = r["a"].replace("≈", "~").replace("²", "2")
        msp.add_text(a, height=90, dxfattribs={"layer": "ARQ-AMBIENTE"}).set_placement((lx, ly - 180), align=TextEntityAlignment.MIDDLE_CENTER)

# mobiliário
for f in d["fur"]:
    x, y, w, h = f[:4]
    label = f[4] if len(f) > 4 else ""
    (ax, ay), (bx, by) = P(x, y), P(x + w, y + h)
    msp.add_lwpolyline([(ax, ay), (bx, ay), (bx, by), (ax, by)], close=True, dxfattribs={"layer": "ARQ-MOBILIARIO"})
    if label and w > 40:
        msp.add_text(label.upper(), height=60, dxfattribs={"layer": "ARQ-MOBILIARIO-TEXTO"}).set_placement(
            ((ax + bx) / 2, (ay + by) / 2), align=TextEntityAlignment.MIDDLE_CENTER)

# divisas
msp.add_lwpolyline([P(70, 60), P(690, 60)], dxfattribs={"layer": "ARQ-DIVISA"})
msp.add_lwpolyline([P(70, 60), P(465, 1040), P(1555, 1040)], dxfattribs={"layer": "ARQ-DIVISA"})
for txt, (x, y), rot in [("VIZINHO - SEM JANELAS", (380, 45), 0), ("VIZINHO - SEM JANELAS", (1000, 1065), 0),
                         ("DIVISA - MURO ANTIGA FÁBRICA", (150, 380), -68.05)]:
    t = msp.add_text(txt, height=120, dxfattribs={"layer": "ARQ-DIVISA", "rotation": rot})
    t.set_placement(P(x, y), align=TextEntityAlignment.MIDDLE_CENTER)

# escada
for i in range(9):
    x = 690 + i * 70
    msp.add_line(P(min(x, 1255), 62), P(min(x, 1255), 140), dxfattribs={"layer": "ARQ-ESCADA"})
msp.add_line(P(720, 101), P(1230, 101), dxfattribs={"layer": "ARQ-ESCADA"})
msp.add_lwpolyline([P(1205, 92), P(1230, 101), P(1205, 110)], dxfattribs={"layer": "ARQ-ESCADA"})

# cotas gerais
dim_attr = {"layer": "ARQ-COTA"}
doc.dimstyles.new("COTA-50", dxfattribs={"dimtxt": 120, "dimasz": 80, "dimexe": 60, "dimexo": 60, "dimgap": 40, "dimdec": 0, "dimtsz": 0})
def dim(p1, p2, base, angle=0):
    msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle="COTA-50", dxfattribs=dim_attr).render()
dim(P(685, 1025), P(1385, 1025), (0, P(0, 1025)[1] - 900))
dim(P(92, 72), P(685, 72), (0, P(0, 72)[1] + 700))
dim(P(1385, 305), P(1385, 1025), (P(1385, 0)[0] + 2400, 0), angle=90)
dim(P(1050, 780), P(1385, 780), (0, P(0, 780)[1] + 350))
dim(P(186, 312), P(685, 312), (0, P(0, 312)[1] + 350))

# carimbo
bx0, by0 = P(1450, 1180)
lines = ["NOSSA CASA - PLANTA DE LAYOUT", "VERSÃO FINAL (P) - HALL EM L E BANHEIRO EXISTENTE", "ESCALA SUGERIDA 1:50  |  UNIDADE: MILÍMETROS",
         "Medidas aproximadas, tiradas do croqui enviado.", "Conferir em obra e com o arquiteto antes de executar."]
for i, txt in enumerate(lines):
    msp.add_text(txt, height=160 if i == 0 else 110, dxfattribs={"layer": "ARQ-CARIMBO"}).set_placement((bx0 - 9000, by0 - i * 230))

doc.saveas(OUT)
print("ok", OUT)
