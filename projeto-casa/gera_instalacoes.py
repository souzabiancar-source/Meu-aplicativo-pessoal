"""Planta de pontos elétricos e hidráulicos sobre a base em DXF (milímetros).

Uso: python3 gera_instalacoes.py base.dxf saida-eletrica.dxf saida-hidraulica.dxf
A base é a planta de layout gerada por gera_dxf.py.
"""
import sys
import ezdxf
from ezdxf.enums import TextEntityAlignment as A

BASE, OUT_E, OUT_H = sys.argv[1:4]
K = 1000 / 85
X0, Y0 = 92, 1040
P = lambda x, y: ((x - X0) * K, (Y0 - y) * K)

# ---------------- pontos elétricos (coordenadas da planta) ----------------
# luz: (x, y, circuito, tipo)  tipo: teto | pendente | arandela | spot | exaustor
LUZ = [
    (580, 110, "C1", "teto"), (767, 228, "C1", "teto"), (790, 380, "C1", "teto"), (780, 560, "C1", "teto"),
    (1100, 400, "C1", "teto"), (1180, 400, "C1", "teto"), (1080, 477, "C1", "pendente"), (1160, 477, "C1", "pendente"),
    (1312, 416, "C1", "pendente"), (1000, 600, "C1", "teto"), (1190, 640, "C1", "teto"),
    (200, 170, "C2", "teto"), (360, 200, "C2", "teto"), (578, 272, "C2", "teto"), (935, 200, "C2", "teto"),
    (390, 430, "C2", "teto"), (275, 322, "C2", "arandela"), (475, 322, "C2", "arandela"),
    (614, 348, "C2", "teto"), (592, 440, "C2", "teto"), (680, 410, "C2", "exaustor"),
    (900, 830, "C2", "teto"), (990, 930, "C2", "teto"), (752, 840, "C2", "teto"), (692, 800, "C2", "exaustor"),
    (1225, 900, "C2", "teto"), (1160, 1018, "C2", "arandela"), (1316, 1018, "C2", "arandela"),
]
# interruptores: (x, y, rótulo)
INT = [
    (678, 160, "S"), (465, 190, "S"), (525, 238, "S"), (858, 262, "S"), (536, 395, "S"), (678, 392, "S"),
    (632, 380, "S"), (700, 318, "S3"), (1378, 512, "S3"), (1030, 318, "S"), (1052, 868, "S"),
    (828, 866, "S"), (1340, 790, "S3"), (1168, 1018, "S3"),
]
# tomadas de uso geral: (x, y, altura B/M/A, circuito)
TUG = [
    (476, 140, "B", "C3"), (840, 290, "B", "C3"), (690, 450, "B", "C3"), (690, 640, "B", "C3"),
    (1378, 515, "B", "C3"), (1150, 770, "M", "C3"), (1230, 770, "M", "C3"), (1250, 310, "B", "C3"),
    (150, 80, "M", "C5"), (225, 80, "M", "C5"), (300, 80, "M", "C5"), (375, 80, "M", "C5"),
    (250, 300, "B", "C5"), (300, 260, "B", "C5"),
    (258, 326, "B", "C4"), (392, 318, "B", "C4"), (492, 326, "B", "C4"), (330, 560, "M", "C4"), (470, 560, "M", "C4"),
    (940, 786, "M", "C4"), (1146, 1020, "B", "C4"), (1328, 1020, "B", "C4"), (1066, 990, "B", "C4"), (1200, 792, "M", "C4"),
    (1035, 316, "M", "C6"), (1130, 316, "M", "C6"), (1200, 316, "M", "C6"), (995, 477, "M", "C6"), (1185, 477, "M", "C6"),
    (1015, 252, "M", "C7"), (480, 300, "B", "C7"),
    (570, 392, "M", "C8"), (690, 868, "M", "C8"),
]
# tomadas de uso específico: (x, y, rótulo, circuito)
TUE = [
    (1050, 318, "Forno 220V", "C9"), (1090, 500, "Cooktop indução 220V", "C10"), (1080, 318, "Micro-ondas", "C11"),
    (1215, 318, "Lava-louças", "C12"), (1015, 178, "Lava e seca", "C13"), (1090, 470, "Coifa (teto)", "C6"),
    (1068, 880, "Ar-cond. 220V", "C14"), (494, 500, "Ar-cond. 220V", "C15"), (466, 255, "Ar-cond. 220V", "C16"),
    (1300, 312, "Ar-cond. 220V", "C17"), (1012, 272, "Aquecedor (ignição)", "C7"),
]
REDE = [(180, 80, "RJ"), (340, 80, "RJ"), (400, 560, "RJ"), (1190, 770, "TV/RJ"), (1240, 792, "TV/RJ")]
OUTROS = [(476, 205, "QD", "Quadro de distribuição"), (694, 66, "CAMP", "Campainha"), (678, 176, "INT", "Interfone")]

CIRCUITOS = [
    ("C1", "Iluminação área social (hall, foyer, sala, cozinha, jantar, leitura)", "127 V"),
    ("C2", "Iluminação íntima (quartos, banhos, closet, escritório, despensa, lavanderia)", "127 V"),
    ("C3", "Tomadas sala, hall e leitura", "127 V"),
    ("C4", "Tomadas quartos e closet", "127 V"),
    ("C5", "Tomadas escritório", "127 V"),
    ("C6", "Tomadas cozinha e coifa (DR)", "127 V"),
    ("C7", "Tomadas lavanderia, despensa e aquecedor (DR)", "127 V"),
    ("C8", "Tomadas banheiros (DR)", "127 V"),
    ("C9", "Forno elétrico", "220 V"),
    ("C10", "Cooktop de indução", "220 V"),
    ("C11", "Micro-ondas", "127 V"),
    ("C12", "Lava-louças (DR)", "127 V"),
    ("C13", "Lava e seca (DR)", "127/220 V"),
    ("C14", "Ar-condicionado quarto do casal", "220 V"),
    ("C15", "Ar-condicionado quarto das crianças", "220 V"),
    ("C16", "Ar-condicionado escritório", "220 V"),
    ("C17", "Ar-condicionado sala", "220 V"),
]

# ---------------- pontos hidráulicos ----------------
# (x, y, tipo, rótulo)  tipo: AF água fria | AQ água quente | ES esgoto | R ralo | CS caixa sifonada | TQ tubo de queda | RG registro geral | GAS
HID = [
    (1015, 160, "RG", "Entrada de água / registro geral"),
    (1012, 172, "AF", "Máquina"), (1004, 192, "ES", ""), (1012, 222, "AF", "Tanque"), (1004, 236, "ES", ""), (930, 245, "CS", ""),
    (1012, 280, "AF", ""), (1000, 280, "AQ", "Aquecedor a gás"), (990, 296, "GAS", ""),
    (1150, 316, "AF", "Pia"), (1166, 316, "AQ", ""), (1158, 326, "ES", ""), (1132, 316, "AF", "Filtro"),
    (1212, 316, "AF", "Lava-louças"), (1212, 328, "ES", ""), (1035, 326, "AF", "Geladeira"),
    (560, 390, "AF", "Lavatório"), (576, 390, "AQ", ""), (568, 400, "ES", ""),
    (678, 430, "AF", "Vaso"), (668, 444, "ES", "100 mm"),
    (580, 560, "AF", "Chuveiro"), (600, 560, "AQ", ""), (592, 545, "R", "ralo linear"), (540, 500, "CS", ""), (678, 556, "TQ", "ponto de água existente"),
    (690, 905, "AF", "Lavatório (existente)"), (690, 920, "AQ", ""), (700, 912, "ES", ""),
    (814, 890, "AF", "Vaso (existente)"), (800, 900, "ES", ""),
    (742, 1020, "AF", "Chuveiro (existente)"), (762, 1020, "AQ", ""), (752, 1004, "R", ""), (760, 935, "CS", ""),
]
HID_NOTAS = [
    "AF = água fria  |  AQ = água quente  |  ES = esgoto  |  R = ralo  |  CS = caixa sifonada  |  TQ = tubo de queda  |  RG = registro geral",
    "Aquecedor a gás de passagem na lavanderia (janela para a escada garante a ventilação). Sem gás: chuveiros elétricos 220 V nos dois banhos.",
    "Água quente para os dois chuveiros, os dois lavatórios e a pia da cozinha. Trecho longo até os banhos: prever recirculação ou tubulação isolada.",
    "Banho do casal: pontos já existentes, conferir posição na obra. Banho das crianças: usar o ponto de água existente junto ao telhado.",
    "Drenos dos ar-condicionados: levar até ralo ou área externa (não desenhados).",
]


def prep(base_doc):
    for layer in base_doc.layers:
        if layer.dxf.name.startswith("ARQ-"):
            layer.color = 9
            layer.dxf.lineweight = 13
    for e in base_doc.modelspace().query("HATCH"):
        e.dxf.color = 254
    return base_doc


def text(msp, s, x, y, h, layer, align=A.MIDDLE_LEFT, color=None):
    attrs = {"layer": layer}
    if color is not None:
        attrs["color"] = color
    msp.add_text(s, height=h, dxfattribs=attrs).set_placement((x, y), align=align)


def legend_box(msp, x, y, title, rows, layer, w=9000):
    text(msp, title, x, y, 220, layer)
    yy = y - 380
    for r in rows:
        text(msp, r, x, yy, 120, layer)
        yy -= 220
    return yy


def eletrica():
    doc = prep(ezdxf.readfile(BASE))
    msp = doc.modelspace()
    for name, color in [("ELE-ILUMINACAO", 2), ("ELE-INTERRUPTOR", 3), ("ELE-TUG", 1), ("ELE-TUE", 6),
                        ("ELE-REDE", 4), ("ELE-QUADRO", 7), ("ELE-LEGENDA", 7)]:
        doc.layers.add(name, color=color)
    for x, y, c, t in LUZ:
        cx, cy = P(x, y)
        L = "ELE-ILUMINACAO"
        if t in ("teto", "pendente"):
            msp.add_circle((cx, cy), 150, dxfattribs={"layer": L})
            msp.add_line((cx - 106, cy - 106), (cx + 106, cy + 106), dxfattribs={"layer": L})
            msp.add_line((cx - 106, cy + 106), (cx + 106, cy - 106), dxfattribs={"layer": L})
            if t == "pendente":
                msp.add_circle((cx, cy), 60, dxfattribs={"layer": L})
        elif t == "arandela":
            msp.add_circle((cx, cy), 90, dxfattribs={"layer": L})
            text(msp, "A", cx, cy, 90, L, A.MIDDLE_CENTER)
        elif t == "exaustor":
            msp.add_circle((cx, cy), 110, dxfattribs={"layer": L})
            text(msp, "E", cx, cy, 100, L, A.MIDDLE_CENTER)
        text(msp, c, cx + 170, cy + 110, 70, L)
    for x, y, s in INT:
        cx, cy = P(x, y)
        msp.add_circle((cx, cy), 60, dxfattribs={"layer": "ELE-INTERRUPTOR"})
        text(msp, s, cx + 80, cy, 90, "ELE-INTERRUPTOR")
    for x, y, h, c in TUG:
        cx, cy = P(x, y)
        msp.add_lwpolyline([(cx - 90, cy - 70), (cx + 90, cy - 70), (cx, cy + 90)], close=True, dxfattribs={"layer": "ELE-TUG"})
        text(msp, f"{h}·{c}", cx + 110, cy, 70, "ELE-TUG")
    for x, y, s, c in TUE:
        cx, cy = P(x, y)
        msp.add_lwpolyline([(cx - 90, cy - 90), (cx + 90, cy - 90), (cx + 90, cy + 90), (cx - 90, cy + 90)], close=True, dxfattribs={"layer": "ELE-TUE"})
        msp.add_line((cx - 90, cy - 90), (cx + 90, cy + 90), dxfattribs={"layer": "ELE-TUE"})
        text(msp, f"{s} · {c}", cx + 120, cy - 140, 70, "ELE-TUE")
    for x, y, s in REDE:
        cx, cy = P(x, y)
        msp.add_lwpolyline([(cx - 80, cy - 80), (cx + 80, cy - 80), (cx + 80, cy + 80), (cx - 80, cy + 80)], close=True, dxfattribs={"layer": "ELE-REDE"})
        text(msp, s, cx + 100, cy - 120, 70, "ELE-REDE")
    for x, y, s, desc in OUTROS:
        cx, cy = P(x, y)
        if s == "QD":
            msp.add_lwpolyline([(cx, cy - 300), (cx + 160, cy - 300), (cx + 160, cy + 300), (cx, cy + 300)], close=True, dxfattribs={"layer": "ELE-QUADRO"})
            h = msp.add_hatch(color=7, dxfattribs={"layer": "ELE-QUADRO"})
            h.paths.add_polyline_path([(cx, cy - 300), (cx + 160, cy - 300), (cx + 160, cy + 300), (cx, cy + 300)], is_closed=True)
            text(msp, "QD", cx + 220, cy, 110, "ELE-QUADRO")
        else:
            msp.add_circle((cx, cy), 70, dxfattribs={"layer": "ELE-QUADRO"})
            text(msp, s, cx + 90, cy, 70, "ELE-QUADRO")
    lx, ly = P(1600, 60)
    y = legend_box(msp, lx, ly, "PLANTA DE PONTOS ELÉTRICOS - PRÉVIA S", [
        "Círculo com X = ponto de luz no teto (com círculo interno = pendente)",
        "A = arandela  |  E = exaustor  |  S = interruptor simples  |  S3 = interruptor paralelo (three-way)",
        "Triângulo = tomada de uso geral: B baixa 0,30 m · M média 1,10 m (bancadas 1,10 m) · A alta 2,20 m",
        "Quadrado com X = tomada de uso específico (TUE)  |  Quadrado = ponto de rede/TV  |  QD = quadro",
        "Fitas de LED em armários, nichos e sanca: alimentar a partir do circuito de iluminação do ambiente.",
    ], "ELE-LEGENDA")
    y = legend_box(msp, lx, y - 300, "DIVISÃO DE CIRCUITOS (sugestão)", [f"{c}  {d}  ({v})" for c, d, v in CIRCUITOS], "ELE-LEGENDA")
    legend_box(msp, lx, y - 300, "IMPORTANTE", [
        "Planta de pontos para orientar o projeto. Bitolas, disjuntores, DR/DPS e quadro devem ser",
        "dimensionados por engenheiro eletricista conforme a NBR 5410, com ART.",
    ], "ELE-LEGENDA")
    doc.saveas(OUT_E)


def hidraulica():
    doc = prep(ezdxf.readfile(BASE))
    msp = doc.modelspace()
    COL = {"AF": 5, "AQ": 1, "ES": 30, "R": 30, "CS": 30, "TQ": 30, "RG": 5, "GAS": 2}
    for name, color in [("HID-AGUA-FRIA", 5), ("HID-AGUA-QUENTE", 1), ("HID-ESGOTO", 30), ("HID-GAS", 2), ("HID-LEGENDA", 7)]:
        doc.layers.add(name, color=color)
    LAY = {"AF": "HID-AGUA-FRIA", "RG": "HID-AGUA-FRIA", "AQ": "HID-AGUA-QUENTE", "GAS": "HID-GAS"}
    for x, y, t, label in HID:
        cx, cy = P(x, y)
        L = LAY.get(t, "HID-ESGOTO")
        if t in ("R", "CS"):
            s = 90 if t == "R" else 140
            msp.add_lwpolyline([(cx - s, cy - s), (cx + s, cy - s), (cx + s, cy + s), (cx - s, cy + s)], close=True, dxfattribs={"layer": L})
            msp.add_line((cx - s, cy - s), (cx + s, cy + s), dxfattribs={"layer": L})
            msp.add_line((cx - s, cy + s), (cx + s, cy - s), dxfattribs={"layer": L})
        else:
            r = 140 if t in ("TQ", "RG") else 80
            msp.add_circle((cx, cy), r, dxfattribs={"layer": L})
            h = msp.add_hatch(color=COL[t], dxfattribs={"layer": L})
            h.paths.add_edge_path().add_arc((cx, cy), r * 0.6, 0, 360)
        tag = {"RG": "RG", "TQ": "TQ"}.get(t, t)
        text(msp, tag + (f" {label}" if label else ""), cx + 160, cy, 70, L)
    lx, ly = P(1600, 60)
    legend_box(msp, lx, ly, "PLANTA DE PONTOS HIDRÁULICOS - PRÉVIA S", HID_NOTAS + [
        "",
        "Planta de pontos para orientar o projeto. Diâmetros, caimentos, ventilação e reservatório devem",
        "ser dimensionados por engenheiro conforme NBR 5626 (água fria e quente) e NBR 8160 (esgoto), com ART.",
    ], "HID-LEGENDA")
    doc.saveas(OUT_H)


eletrica()
hidraulica()
print("ok")
