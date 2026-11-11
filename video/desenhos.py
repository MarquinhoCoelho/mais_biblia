"""Biblioteca de rabiscos (SVG) para as cenas. Quadro de 1080x1920.

Zonas do quadro:  legenda no topo (y 170-560) | cena (y 600-1650; chão em y~1480) | rodapé livre (y>1700, UI do YouTube).
Cada função devolve um pedaço de SVG. No roteiro.json, cada item de "desenho" é {"f": "<nome>", ...argumentos}.
Para algo que não existe aqui, use {"f": "svg", "codigo": "<path .../>"} (traço preto 6px, cantos redondos).

Cores sugeridas (marcador): AZUL #5b8fd6, VERMELHO #d9534f, VERDE #6bb36b, AMARELO #f4c542,
MARROM #9b6b43, ROXO #8e6bbf, CINZA #9aa0a6, BRANCO #fdfaf2, PELE #fbe3c4, LARANJA #f0954a.
"""
import math
from html import escape

T = 'stroke="#222" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'
PELE = "#fbe3c4"


def _p(d, fill="none", w=6, cor="#222"):
    return f'<path d="{d}" fill="{fill}" stroke="{cor}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def _c(x, y, r, fill="none", w=6, cor="#222"):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{cor}" stroke-width="{w}"/>'


def _txt(x, y, s, tam=48, cor="#222", anchor="middle", peso="bold"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Kalam" font-weight="{peso}" font-size="{tam}" fill="{cor}" '
            f'text-anchor="{anchor}">{escape(str(s))}</text>')


# ------------------------------------------------------------------ pessoa
def pessoa(x=540, y=1480, h=500, roupa="#5b8fd6", faixa=None, cabelo=None, barba=None, olhos="normal",
           boca="normal", bracos="baixo", virado=1, acessorios=(), rotulo=None, pele=PELE, cabelo_longo=False):
    """Boneco de rabisco. y = altura dos pés. h = altura total.
    olhos: normal | bravo | triste | fechado | arregalado      boca: normal | feliz | triste | aberta | dor | reta
    bracos: baixo | cima | frente | ouvido | atacar | abertos | cruzados | rezando | apontar
    virado: 1 olha p/ direita, -1 p/ esquerda (afeta braço da frente e acessórios na mão)
    acessorios: coroa, capacete, espada, lanca, tocha, cajado, turbante, mitra, veu, sangue_orelha, sem_orelha,
                curativo, brilho, corrente, escudo, saco_moedas, pergaminho
    cabelo/barba: cor (ex. "#5a3b22") ou None. rotulo: texto com seta acima da cabeça."""
    s = h / 430
    v = virado
    hx, hy, hr = x, y - 365 * s, 50 * s          # cabeça
    sy = y - 305 * s                               # ombros
    out = []
    ac = set(acessorios)

    # braço de trás e itens atrás do corpo
    def braco(lado, modo):
        ox = x + lado * 34 * s
        if modo == "baixo":
            pts = [(ox, sy + 10 * s), (x + lado * 62 * s, sy + 90 * s), (x + lado * 66 * s, sy + 170 * s)]
        elif modo == "cima":
            pts = [(ox, sy + 10 * s), (x + lado * 85 * s, sy - 60 * s), (x + lado * 100 * s, sy - 140 * s)]
        elif modo == "frente":
            pts = [(ox, sy + 10 * s), (x + lado * 100 * s, sy + 40 * s), (x + lado * 170 * s, sy + 30 * s)]
        elif modo == "apontar":
            pts = [(ox, sy + 10 * s), (x + lado * 110 * s, sy - 10 * s), (x + lado * 190 * s, sy - 50 * s)]
        elif modo == "atacar":
            pts = [(ox, sy + 10 * s), (x + lado * 95 * s, sy - 50 * s), (x + lado * 150 * s, sy - 110 * s)]
        elif modo == "abertos":
            pts = [(ox, sy + 10 * s), (x + lado * 110 * s, sy + 20 * s), (x + lado * 170 * s, sy - 30 * s)]
        elif modo == "ouvido":
            pts = [(ox, sy + 10 * s), (x + lado * 90 * s, sy - 10 * s), (hx + lado * hr * 1.05, hy + 6 * s)]
        elif modo == "cruzados":
            pts = [(ox, sy + 10 * s), (x + lado * 40 * s, sy + 80 * s), (x - lado * 40 * s, sy + 95 * s)]
        elif modo == "rezando":
            pts = [(ox, sy + 10 * s), (x + lado * 45 * s, sy + 90 * s), (x + v * 8 * s, sy + 40 * s)]
        else:
            pts = [(ox, sy + 10 * s), (x + lado * 62 * s, sy + 90 * s), (x + lado * 66 * s, sy + 170 * s)]
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} Q{pts[1][0]:.1f},{pts[1][1]:.1f} {pts[2][0]:.1f},{pts[2][1]:.1f}"
        return _p(d, w=7) + _c(pts[2][0], pts[2][1], 13 * s, fill=pele, w=5), pts[2]

    modos = bracos if isinstance(bracos, (list, tuple)) else (
        (bracos, bracos) if bracos in ("cima", "abertos", "cruzados", "rezando", "baixo") else ("baixo", bracos))
    tras_modo, frente_modo = modos[0], modos[1]
    if "asas" in ac:
        for lado in (-1, 1):
            out.append(_p(f"M{x + lado * 20 * s:.1f},{sy + 20 * s:.1f} Q{x + lado * 200 * s:.1f},{sy - 160 * s:.1f} {x + lado * 230 * s:.1f},{sy - 40 * s:.1f} "
                          f"Q{x + lado * 190 * s:.1f},{sy + 20 * s:.1f} {x + lado * 210 * s:.1f},{sy + 80 * s:.1f} Q{x + lado * 130 * s:.1f},{sy + 90 * s:.1f} {x + lado * 40 * s:.1f},{sy + 110 * s:.1f} Z",
                          fill="#ffffff", w=5))
    b_tras, mao_tras = braco(-v, tras_modo)
    out.append(b_tras)

    # pernas
    out.append(_p(f"M{x - 28 * s:.1f},{y - 95 * s:.1f} L{x - 34 * s:.1f},{y:.1f} l{-18 * s:.1f},0", w=7))
    out.append(_p(f"M{x + 28 * s:.1f},{y - 95 * s:.1f} L{x + 34 * s:.1f},{y:.1f} l{18 * s:.1f},0", w=7))
    # túnica
    d = (f"M{x - 40 * s:.1f},{sy:.1f} Q{x:.1f},{sy - 14 * s:.1f} {x + 40 * s:.1f},{sy:.1f} "
         f"L{x + 82 * s:.1f},{y - 90 * s:.1f} Q{x:.1f},{y - 76 * s:.1f} {x - 82 * s:.1f},{y - 90 * s:.1f} Z")
    out.append(_p(d, fill=roupa))
    if "gravida" in ac:
        out.append(f'<ellipse cx="{x + v * 40 * s:.1f}" cy="{y - 175 * s:.1f}" rx="{40 * s:.1f}" ry="{52 * s:.1f}" fill="{roupa}" {T}/>')
    if faixa:
        out.append(_p(f"M{x - 52 * s:.1f},{y - 205 * s:.1f} Q{x:.1f},{y - 190 * s:.1f} {x + 54 * s:.1f},{y - 208 * s:.1f}",
                      cor=faixa, w=16 * s))
    if "corrente" in ac:
        out.append(_p(f"M{x - 60 * s:.1f},{y - 160 * s:.1f} Q{x:.1f},{y - 140 * s:.1f} {x + 62 * s:.1f},{y - 162 * s:.1f}",
                      cor="#777", w=8 * s) )
    if "saco_moedas" in ac:
        out.append(_c(x + v * 60 * s, y - 180 * s, 26 * s, fill="#c9a66b"))
        out.append(_txt(x + v * 60 * s, y - 170 * s, "$", 30 * s))

    # cabelo longo atrás
    if cabelo and cabelo_longo:
        out.append(_p(f"M{hx - hr:.1f},{hy:.1f} Q{hx - hr * 1.25:.1f},{hy + hr * 1.3:.1f} {hx - hr * 0.6:.1f},{hy + hr * 1.5:.1f} "
                      f"L{hx + hr * 0.6:.1f},{hy + hr * 1.5:.1f} Q{hx + hr * 1.25:.1f},{hy + hr * 1.3:.1f} {hx + hr:.1f},{hy:.1f} Z",
                      fill=cabelo))
    # cabeça
    if "veu" in ac or "turbante" in ac:
        cor_pano = "#e9dcc3" if "veu" in ac else "#d9c48f"
        out.append(_p(f"M{hx - hr * 1.15:.1f},{hy + hr * 1.6:.1f} Q{hx - hr * 1.35:.1f},{hy - hr * 1.3:.1f} {hx:.1f},{hy - hr * 1.3:.1f} "
                      f"Q{hx + hr * 1.35:.1f},{hy - hr * 1.3:.1f} {hx + hr * 1.15:.1f},{hy + hr * 1.6:.1f} Z", fill=cor_pano))
    out.append(_c(hx, hy, hr, fill=pele))
    if "sem_orelha" not in ac:
        out.append(_c(hx - v * hr * 0.98, hy + 4 * s, 11 * s, fill=pele, w=5))
    if cabelo and not ("veu" in ac or "turbante" in ac):
        out.append(_p(f"M{hx - hr * 0.95:.1f},{hy - hr * 0.2:.1f} Q{hx - hr * 0.6:.1f},{hy - hr * 1.35:.1f} {hx + hr * 0.2:.1f},{hy - hr * 1.02:.1f} "
                      f"Q{hx + hr * 0.95:.1f},{hy - hr * 0.95:.1f} {hx + hr * 0.95:.1f},{hy - hr * 0.2:.1f} "
                      f"Q{hx + hr * 0.4:.1f},{hy - hr * 0.6:.1f} {hx - hr * 0.95:.1f},{hy - hr * 0.2:.1f} Z", fill=cabelo, w=5))
    if barba:
        out.append(_p(f"M{hx - hr * 0.92:.1f},{hy + hr * 0.15:.1f} Q{hx - hr * 0.8:.1f},{hy + hr * 1.55:.1f} {hx:.1f},{hy + hr * 1.6:.1f} "
                      f"Q{hx + hr * 0.8:.1f},{hy + hr * 1.55:.1f} {hx + hr * 0.92:.1f},{hy + hr * 0.15:.1f} "
                      f"Q{hx:.1f},{hy + hr * 0.75:.1f} {hx - hr * 0.92:.1f},{hy + hr * 0.15:.1f} Z", fill=barba, w=5))
    # rosto (deslocado para o lado que olha)
    fx = hx + v * hr * 0.22
    ex, ey, eo = fx - hr * 0.33, hy - hr * 0.08, hr * 0.66
    if olhos == "fechado":
        out.append(_p(f"M{ex - 9 * s:.1f},{ey:.1f} q{9 * s:.1f},{7 * s:.1f} {18 * s:.1f},0", w=5))
        out.append(_p(f"M{ex + eo - 9 * s:.1f},{ey:.1f} q{9 * s:.1f},{7 * s:.1f} {18 * s:.1f},0", w=5))
    elif olhos == "arregalado":
        out.append(_c(ex, ey, 11 * s, fill="#fff", w=4) + _c(ex, ey, 4 * s, fill="#222", w=2))
        out.append(_c(ex + eo, ey, 11 * s, fill="#fff", w=4) + _c(ex + eo, ey, 4 * s, fill="#222", w=2))
    else:
        out.append(_c(ex, ey, 5.5 * s, fill="#222", w=2) + _c(ex + eo, ey, 5.5 * s, fill="#222", w=2))
    if olhos == "bravo":
        out.append(_p(f"M{ex - 14 * s:.1f},{ey - 22 * s:.1f} L{ex + 10 * s:.1f},{ey - 12 * s:.1f}", w=5))
        out.append(_p(f"M{ex + eo + 14 * s:.1f},{ey - 22 * s:.1f} L{ex + eo - 10 * s:.1f},{ey - 12 * s:.1f}", w=5))
    if olhos == "triste":
        out.append(_p(f"M{ex - 12 * s:.1f},{ey - 14 * s:.1f} L{ex + 10 * s:.1f},{ey - 22 * s:.1f}", w=5))
        out.append(_p(f"M{ex + eo + 12 * s:.1f},{ey - 14 * s:.1f} L{ex + eo - 10 * s:.1f},{ey - 22 * s:.1f}", w=5))
    mx, my = fx, hy + hr * 0.42
    if barba:
        my = hy + hr * 0.5
    bocas = {
        "feliz": f"M{mx - 18 * s:.1f},{my - 4 * s:.1f} Q{mx:.1f},{my + 16 * s:.1f} {mx + 18 * s:.1f},{my - 4 * s:.1f}",
        "triste": f"M{mx - 16 * s:.1f},{my + 8 * s:.1f} Q{mx:.1f},{my - 8 * s:.1f} {mx + 16 * s:.1f},{my + 8 * s:.1f}",
        "reta": f"M{mx - 14 * s:.1f},{my:.1f} L{mx + 14 * s:.1f},{my:.1f}",
        "dor": f"M{mx - 18 * s:.1f},{my:.1f} l{9 * s:.1f},{-7 * s:.1f} l{9 * s:.1f},{7 * s:.1f} l{9 * s:.1f},{-7 * s:.1f} l{9 * s:.1f},{7 * s:.1f}",
        "normal": f"M{mx - 12 * s:.1f},{my:.1f} Q{mx:.1f},{my + 7 * s:.1f} {mx + 12 * s:.1f},{my:.1f}",
    }
    if boca == "aberta":
        out.append(f'<ellipse cx="{mx:.1f}" cy="{my + 3 * s:.1f}" rx="{10 * s:.1f}" ry="{13 * s:.1f}" fill="#7a2222" {T} stroke-width="4"/>')
    else:
        out.append(_p(bocas.get(boca, bocas["normal"]), w=5))

    # chapéus
    if "coroa" in ac:
        cy = hy - hr * 0.8
        out.append(_p(f"M{hx - hr * 0.8:.1f},{cy:.1f} L{hx - hr * 0.9:.1f},{cy - hr * 0.9:.1f} L{hx - hr * 0.4:.1f},{cy - hr * 0.45:.1f} "
                      f"L{hx:.1f},{cy - hr:.1f} L{hx + hr * 0.4:.1f},{cy - hr * 0.45:.1f} L{hx + hr * 0.9:.1f},{cy - hr * 0.9:.1f} "
                      f"L{hx + hr * 0.8:.1f},{cy:.1f} Z", fill="#f4c542", w=5))
    if "mitra" in ac:   # turbante alto do sumo sacerdote
        cy = hy - hr * 0.7
        out.append(_p(f"M{hx - hr * 0.85:.1f},{cy + 8 * s:.1f} L{hx - hr * 0.7:.1f},{cy - hr * 0.9:.1f} Q{hx:.1f},{cy - hr * 1.2:.1f} "
                      f"{hx + hr * 0.7:.1f},{cy - hr * 0.9:.1f} L{hx + hr * 0.85:.1f},{cy + 8 * s:.1f} Z", fill="#fdfaf2", w=5))
        out.append(f'<rect x="{hx - hr * 0.5:.1f}" y="{cy - hr * 0.35:.1f}" width="{hr:.1f}" height="{hr * 0.28:.1f}" fill="#f4c542" {T} stroke-width="4"/>')
    if "capacete" in ac:
        out.append(_p(f"M{hx - hr * 1.05:.1f},{hy - hr * 0.05:.1f} Q{hx - hr * 1.05:.1f},{hy - hr * 1.2:.1f} {hx:.1f},{hy - hr * 1.15:.1f} "
                      f"Q{hx + hr * 1.05:.1f},{hy - hr * 1.2:.1f} {hx + hr * 1.05:.1f},{hy - hr * 0.05:.1f} Z", fill="#b0b6bd", w=5))
        out.append(_p(f"M{hx - hr * 0.7:.1f},{hy - hr * 1.15:.1f} Q{hx:.1f},{hy - hr * 2.0:.1f} {hx + hr * 0.7:.1f},{hy - hr * 1.15:.1f} Z",
                      fill="#d9534f", w=5))
    if "brilho" in ac:
        for i in range(10):
            ang = math.pi * (1.05 + i * 0.1)
            r1, r2 = hr * 1.6, hr * 2.05
            out.append(_p(f"M{hx + math.cos(ang) * r1:.1f},{hy + math.sin(ang) * r1:.1f} "
                          f"L{hx + math.cos(ang) * r2:.1f},{hy + math.sin(ang) * r2:.1f}", cor="#f4c542", w=6))
    if "sangue_orelha" in ac:
        ox = hx - v * hr * 1.0
        for k, (dx, dy) in enumerate([(0, 30), (-10, 55), (8, 70)]):
            out.append(f'<path d="M{ox + dx * s:.1f},{hy + dy * s:.1f} q{-7 * s:.1f},{14 * s:.1f} 0,{18 * s:.1f} q{7 * s:.1f},{-4 * s:.1f} 0,{-18 * s:.1f} Z" fill="#d9534f" stroke="#a33" stroke-width="3"/>')
    if "curativo" in ac:
        ox = hx - v * hr * 1.0
        out.append(f'<rect x="{ox - 16 * s:.1f}" y="{hy - 16 * s:.1f}" width="{32 * s:.1f}" height="{36 * s:.1f}" rx="6" fill="#f5e6d0" {T} stroke-width="4" transform="rotate(20 {ox:.1f} {hy:.1f})"/>')

    # braço da frente + item na mão
    b_fr, mao = braco(v, frente_modo)
    mx_, my_ = mao
    if "espada" in ac:
        ang = -60 if frente_modo in ("atacar", "cima") else -10
        out.append(f'<g transform="translate({mx_:.1f},{my_:.1f}) rotate({ang if v == 1 else 180 - ang}) scale({s:.3f})">'
                   f'<rect x="-6" y="-8" width="40" height="16" rx="4" fill="#9b6b43" {T} stroke-width="5"/>'
                   f'<rect x="30" y="-22" width="10" height="44" fill="#9b6b43" {T} stroke-width="5"/>'
                   f'<path d="M40,-9 L190,-6 L215,0 L190,6 L40,9 Z" fill="#d6dbe0" {T} stroke-width="5"/></g>')
    if "lanca" in ac:
        out.append(_p(f"M{mx_:.1f},{my_ + 120 * s:.1f} L{mx_:.1f},{my_ - 260 * s:.1f}", cor="#9b6b43", w=9 * s))
        out.append(_p(f"M{mx_ - 14 * s:.1f},{my_ - 250 * s:.1f} L{mx_:.1f},{my_ - 310 * s:.1f} L{mx_ + 14 * s:.1f},{my_ - 250 * s:.1f} Z", fill="#d6dbe0", w=5))
    if "cajado" in ac:
        out.append(_p(f"M{mx_:.1f},{y:.1f} L{mx_:.1f},{my_ - 160 * s:.1f} q0,{-50 * s:.1f} {v * 40 * s:.1f},{-45 * s:.1f}", cor="#9b6b43", w=10 * s))
    if "tocha" in ac:
        out.append(_p(f"M{mx_:.1f},{my_ + 30 * s:.1f} L{mx_ + v * 10 * s:.1f},{my_ - 90 * s:.1f}", cor="#9b6b43", w=12 * s))
        out.append(fogo(mx_ + v * 10 * s, my_ - 85 * s, 0.7 * s))
    if "escudo" in ac:
        out.append(f'<rect x="{mx_ - 45 * s:.1f}" y="{my_ - 80 * s:.1f}" width="{90 * s:.1f}" height="{150 * s:.1f}" rx="{12 * s:.1f}" fill="#d9534f" {T}/>')
    if "pergaminho" in ac:
        out.append(f'<rect x="{mx_ - 20 * s:.1f}" y="{my_ - 50 * s:.1f}" width="{40 * s:.1f}" height="{90 * s:.1f}" rx="6" fill="#f3e2b8" {T} stroke-width="5"/>')
    out.append(b_fr)
    if rotulo:
        out.append(seta_rotulo(hx, hy - hr * (2.3 if ("coroa" in ac or "capacete" in ac or "mitra" in ac) else 1.6), rotulo))
    return "<g>" + "".join(out) + "</g>"


def seta_rotulo(x, y, texto, tam=46, cor="#c0392b"):
    """Etiqueta escrita à mão com seta para baixo (x,y = ponta da seta)."""
    return (_p(f"M{x:.1f},{y - 70:.1f} Q{x + 12:.1f},{y - 35:.1f} {x:.1f},{y:.1f}", cor=cor, w=5) +
            _p(f"M{x - 14:.1f},{y - 18:.1f} L{x:.1f},{y:.1f} L{x + 16:.1f},{y - 16:.1f}", cor=cor, w=5) +
            _txt(x, y - 84, texto, tam, cor))


def deitado(x=540, y=1480, roupa="#5b8fd6", cabelo=None, barba=None, s=1.0, cama=True, olhos="fechado"):
    """Pessoa dormindo deitada (cabeça à esquerda) numa esteira."""
    out = ""
    if cama:
        out += f'<rect x="{x - 260 * s:.1f}" y="{y - 40 * s:.1f}" width="{520 * s:.1f}" height="{40 * s:.1f}" rx="10" fill="#c9a66b" {T}/>'
    hx, hy, hr = x - 200 * s, y - 95 * s, 50 * s
    out += _p(f"M{x - 160 * s:.1f},{y - 130 * s:.1f} Q{x + 40 * s:.1f},{y - 175 * s:.1f} {x + 230 * s:.1f},{y - 110 * s:.1f} L{x + 230 * s:.1f},{y - 42 * s:.1f} L{x - 160 * s:.1f},{y - 42 * s:.1f} Z", fill=roupa)
    out += f'<ellipse cx="{hx - 20 * s:.1f}" cy="{y - 62 * s:.1f}" rx="{70 * s:.1f}" ry="{24 * s:.1f}" fill="#fdfaf2" {T} stroke-width="5"/>'
    out += _c(hx, hy, hr, fill=PELE)
    if cabelo:
        out += _p(f"M{hx - hr:.1f},{hy:.1f} Q{hx - hr:.1f},{hy - hr * 1.1:.1f} {hx + hr * 0.3:.1f},{hy - hr:.1f} Q{hx - hr * 0.3:.1f},{hy - hr * 0.4:.1f} {hx - hr:.1f},{hy:.1f} Z", fill=cabelo, w=5)
    if barba:
        out += _p(f"M{hx + hr * 0.1:.1f},{hy + hr * 0.9:.1f} Q{hx + hr * 1.3:.1f},{hy + hr * 0.9:.1f} {hx + hr * 0.95:.1f},{hy - hr * 0.1:.1f} Q{hx + hr * 0.5:.1f},{hy + hr * 0.4:.1f} {hx + hr * 0.1:.1f},{hy + hr * 0.9:.1f} Z", fill=barba, w=5)
    if olhos == "fechado":
        out += _p(f"M{hx + 4 * s:.1f},{hy - 14 * s:.1f} q9,7 18,0 M{hx + 4 * s:.1f},{hy + 14 * s:.1f} q9,7 18,0", w=5)
    else:
        out += _c(hx + 12 * s, hy - 12 * s, 5.5 * s, fill="#222", w=2) + _c(hx + 12 * s, hy + 14 * s, 5.5 * s, fill="#222", w=2)
    return out


def zzz(x=700, y=1200, tam=70, cor="#5b8fd6"):
    return _txt(x, y, "z", tam * 0.6, cor) + _txt(x + 45, y - 55, "z", tam * 0.8, cor) + _txt(x + 100, y - 120, "Z", tam, cor)


def bebe(x=540, y=1480, s=1.0, manjedoura=True):
    """Bebê enrolado em panos (com manjedoura)."""
    out = ""
    if manjedoura:
        out += _p(f"M{x - 150 * s},{y - 160 * s} L{x - 110 * s},{y - 40 * s} L{x + 110 * s},{y - 40 * s} L{x + 150 * s},{y - 160 * s} Z", fill="#c9a66b")
        out += _p(f"M{x - 110 * s},{y - 40 * s} L{x - 140 * s},{y} M{x + 110 * s},{y - 40 * s} L{x + 140 * s},{y}", cor="#7a4f2e", w=10)
        out += _p(f"M{x - 140 * s},{y - 160 * s} q40,-25 70,0 q40,-25 70,0 q40,-25 70,0 q40,-25 70,0", cor="#e0a800", w=6)
    by = y - 190 * s
    out += f'<ellipse cx="{x + 20 * s:.1f}" cy="{by:.1f}" rx="{90 * s:.1f}" ry="{40 * s:.1f}" fill="#fdfaf2" {T}/>'
    out += _c(x - 70 * s, by - 5 * s, 38 * s, fill=PELE)
    out += _p(f"M{x - 82 * s:.1f},{by - 10 * s:.1f} q6,5 12,0 M{x - 62 * s:.1f},{by - 10 * s:.1f} q6,5 12,0", w=4)
    return out


def pedras(x=540, y=1480, n=5):
    out = ""
    for i in range(n):
        px = x - (n - 1) * 45 + i * 90
        r = 32 + (i * 7) % 15
        out += f'<ellipse cx="{px}" cy="{y - r * 0.6:.1f}" rx="{r}" ry="{r * 0.65:.1f}" fill="#b5b0a6" {T} stroke-width="5"/>'
    return out


# ------------------------------------------------------------------ cenário
def chao(y=1480, cor="#6bb36b", grama=True):
    d = f"M-20,{y} " + " ".join(f"Q{x + 60},{y + (-14 if (x // 120) % 2 else 10)} {x + 120},{y}" for x in range(-20, 1100, 120))
    out = _p(d, w=6)
    if grama:
        for gx in range(70, 1080, 170):
            gy = y + 60 + (gx % 3) * 25
            out += _p(f"M{gx - 14},{gy} l6,-24 M{gx},{gy} l0,-32 M{gx + 14},{gy} l-6,-24", cor=cor, w=5)
    return out


def sol(x=860, y=720, r=70):
    raios = "".join(_p(f"M{x + math.cos(a) * (r + 18):.1f},{y + math.sin(a) * (r + 18):.1f} "
                       f"L{x + math.cos(a) * (r + 48):.1f},{y + math.sin(a) * (r + 48):.1f}", cor="#e0a800", w=6)
                    for a in [i * math.pi / 6 for i in range(12)])
    return raios + _c(x, y, r, fill="#f4c542")


def lua(x=860, y=720, r=65):
    return (f'<path d="M{x + r * 0.3},{y - r} A{r},{r} 0 1,0 {x + r * 0.3},{y + r} A{r * 0.75},{r * 0.75} 0 1,1 {x + r * 0.3},{y - r} Z" '
            f'fill="#f7e9a8" {T}/>')


def estrelas(n=6, y0=640, y1=900):
    out = ""
    for i in range(n):
        x = 90 + (i * 197) % 900
        y = y0 + (i * 131) % max(1, (y1 - y0))
        out += _p(f"M{x - 14},{y} L{x + 14},{y} M{x},{y - 14} L{x},{y + 14}", cor="#e0a800", w=5)
    return out


def noite(y0=0, y1=1920):
    """Noite: aguada azul clara no quadro todo (ponha primeiro)."""
    return f'<rect x="-200" y="{y0}" width="1480" height="{y1 - y0}" fill="#8fa6d4" opacity="0.30"/>'


def nuvem(x=250, y=760, s=1.0):
    return _p(f"M{x - 90 * s},{y} q-10,-55 50,-55 q20,-45 75,-25 q45,-35 85,10 q55,0 45,55 Z", fill="#fdfaf2")


def arvore(x=150, y=1480, s=1.0, tipo="oliveira"):
    tronco = _p(f"M{x - 18 * s},{y} Q{x - 8 * s},{y - 120 * s} {x - 30 * s},{y - 230 * s} M{x + 18 * s},{y} "
                f"Q{x + 12 * s},{y - 120 * s} {x + 28 * s},{y - 230 * s}", cor="#7a4f2e", w=8)
    cor = "#8fae6b" if tipo == "oliveira" else "#6bb36b"
    copa = (_c(x - 70 * s, y - 270 * s, 70 * s, fill=cor) + _c(x + 60 * s, y - 280 * s, 75 * s, fill=cor) +
            _c(x, y - 340 * s, 85 * s, fill=cor))
    if tipo == "oliveira":
        copa += "".join(_c(x + dx * s, y + dy * s, 7 * s, fill="#4a5d32", w=3) for dx, dy in [(-60, -260), (30, -330), (70, -270), (-10, -290)])
    return tronco + copa


def templo(x=540, y=1480, s=1.0):
    w, h = 520 * s, 330 * s
    out = f'<rect x="{x - w / 2:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#efe1c0" {T}/>'
    out += _p(f"M{x - w / 2 - 30 * s:.1f},{y - h:.1f} L{x:.1f},{y - h - 120 * s:.1f} L{x + w / 2 + 30 * s:.1f},{y - h:.1f} Z", fill="#e8d3a3")
    for i in range(5):
        cx = x - w / 2 + (i + 0.5) * w / 5
        out += _p(f"M{cx - 18 * s:.1f},{y - h + 20 * s:.1f} L{cx - 18 * s:.1f},{y:.1f} M{cx + 18 * s:.1f},{y - h + 20 * s:.1f} L{cx + 18 * s:.1f},{y:.1f}", w=5)
    return out


def casa(x=540, y=1480, s=1.0, cor="#e8d3a3"):
    w, h = 300 * s, 220 * s
    return (f'<rect x="{x - w / 2:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{cor}" {T}/>' +
            f'<rect x="{x - 35 * s:.1f}" y="{y - 120 * s:.1f}" width="{70 * s:.1f}" height="{120 * s:.1f}" rx="{30 * s:.1f}" fill="#9b6b43" {T}/>' +
            _p(f"M{x - w / 2 - 15 * s:.1f},{y - h:.1f} L{x + w / 2 + 15 * s:.1f},{y - h:.1f}", w=8))


def fogo(x=540, y=1440, s=1.0):
    return (_p(f"M{x - 40 * s:.1f},{y:.1f} Q{x - 60 * s:.1f},{y - 70 * s:.1f} {x - 10 * s:.1f},{y - 120 * s:.1f} Q{x:.1f},{y - 70 * s:.1f} "
               f"{x + 20 * s:.1f},{y - 90 * s:.1f} Q{x + 60 * s:.1f},{y - 40 * s:.1f} {x + 40 * s:.1f},{y:.1f} Z", fill="#f0954a", w=5) +
            _p(f"M{x - 18 * s:.1f},{y:.1f} Q{x - 22 * s:.1f},{y - 40 * s:.1f} {x:.1f},{y - 60 * s:.1f} Q{x + 22 * s:.1f},{y - 30 * s:.1f} {x + 18 * s:.1f},{y:.1f} Z", fill="#f4c542", w=4))


def fogueira(x=540, y=1480, s=1.0):
    return (_p(f"M{x - 80 * s},{y} L{x + 80 * s},{y - 30 * s} M{x - 80 * s},{y - 30 * s} L{x + 80 * s},{y}", cor="#7a4f2e", w=14) +
            fogo(x, y - 20 * s, 1.2 * s))


def galo(x=800, y=1480, s=1.0):
    return (_p(f"M{x - 60 * s},{y - 90 * s} Q{x - 70 * s},{y - 20 * s} {x},{y - 20 * s} Q{x + 60 * s},{y - 20 * s} {x + 50 * s},{y - 100 * s} "
               f"Q{x + 30 * s},{y - 170 * s} {x + 10 * s},{y - 100 * s} Q{x - 20 * s},{y - 70 * s} {x - 60 * s},{y - 90 * s} Z", fill="#fdfaf2") +
            _c(x + 35 * s, y - 145 * s, 30 * s, fill="#fdfaf2") + _p(f"M{x + 25 * s},{y - 175 * s} q8,-25 22,-5 q10,-22 18,4", fill="#d9534f", w=4) +
            _p(f"M{x + 62 * s},{y - 148 * s} l22,6 l-22,8 Z", fill="#f4c542", w=4) + _c(x + 42 * s, y - 150 * s, 4 * s, fill="#222", w=2) +
            _p(f"M{x - 60 * s},{y - 90 * s} q-50,-40 -30,-90 M{x - 62 * s},{y - 80 * s} q-60,-10 -60,-60", cor="#d9534f", w=7) +
            _p(f"M{x - 10 * s},{y - 22 * s} L{x - 14 * s},{y} M{x + 15 * s},{y - 22 * s} L{x + 18 * s},{y}", cor="#e0a800", w=5))


def tabuas(x=540, y=1100, s=1.0):
    """Tábuas da Lei."""
    out = ""
    for dx in (-95, 95):
        cx = x + dx * s
        out += _p(f"M{cx - 85 * s},{y + 160 * s} L{cx - 85 * s},{y - 90 * s} Q{cx},{y - 190 * s} {cx + 85 * s},{y - 90 * s} L{cx + 85 * s},{y + 160 * s} Z", fill="#c9c5bb")
        for i in range(4):
            out += _p(f"M{cx - 50 * s},{y - 40 * s + i * 50 * s} L{cx + 50 * s},{y - 40 * s + i * 50 * s}", w=4)
    return out


def cruz(x=540, y=1480, s=1.0):
    return (f'<rect x="{x - 22 * s}" y="{y - 520 * s}" width="{44 * s}" height="{520 * s}" fill="#9b6b43" {T}/>' +
            f'<rect x="{x - 150 * s}" y="{y - 420 * s}" width="{300 * s}" height="{42 * s}" fill="#9b6b43" {T}/>')


def orelha(x=540, y=1000, s=1.0, cortada=False):
    """Orelha grande (ícone)."""
    out = _p(f"M{x - 40 * s},{y + 110 * s} Q{x - 110 * s},{y + 40 * s} {x - 90 * s},{y - 50 * s} Q{x - 60 * s},{y - 150 * s} {x + 20 * s},{y - 140 * s} "
             f"Q{x + 110 * s},{y - 120 * s} {x + 90 * s},{y - 20 * s} Q{x + 70 * s},{y + 50 * s} {x + 20 * s},{y + 70 * s} Q{x - 10 * s},{y + 130 * s} {x - 40 * s},{y + 110 * s} Z",
             fill=PELE, w=7)
    out += _p(f"M{x - 40 * s},{y + 40 * s} Q{x - 60 * s},{y - 70 * s} {x + 10 * s},{y - 80 * s} Q{x + 60 * s},{y - 70 * s} {x + 40 * s},{y - 10 * s} Q{x + 10 * s},{y + 10 * s} {x + 5 * s},{y + 40 * s}", w=5)
    if cortada:
        out += _p(f"M{x - 140 * s},{y + 150 * s} L{x + 150 * s},{y - 150 * s}", cor="#d9534f", w=10)
    return out


def espada(x=540, y=1000, s=1.0, ang=-30):
    return (f'<g transform="translate({x},{y}) rotate({ang}) scale({s})">'
            f'<rect x="-6" y="-10" width="50" height="20" rx="5" fill="#9b6b43" {T}/>'
            f'<rect x="40" y="-28" width="12" height="56" fill="#9b6b43" {T}/>'
            f'<path d="M52,-11 L260,-8 L292,0 L260,8 L52,11 Z" fill="#d6dbe0" {T}/></g>')


def coracao(x=540, y=1000, s=1.0, cor="#d9534f"):
    return _p(f"M{x},{y + 70 * s} C{x - 120 * s},{y - 10 * s} {x - 70 * s},{y - 110 * s} {x},{y - 50 * s} "
              f"C{x + 70 * s},{y - 110 * s} {x + 120 * s},{y - 10 * s} {x},{y + 70 * s} Z", fill=cor)


def seta(x1, y1, x2, y2, cor="#c0392b"):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - 30 * math.cos(a - 0.5), y2 - 30 * math.sin(a - 0.5))
    p2 = (x2 - 30 * math.cos(a + 0.5), y2 - 30 * math.sin(a + 0.5))
    mx, my = (x1 + x2) / 2 + (y2 - y1) * 0.12, (y1 + y2) / 2 - (x2 - x1) * 0.12
    return (_p(f"M{x1},{y1} Q{mx:.1f},{my:.1f} {x2},{y2}", cor=cor, w=6) +
            _p(f"M{p1[0]:.1f},{p1[1]:.1f} L{x2},{y2} L{p2[0]:.1f},{p2[1]:.1f}", cor=cor, w=6))


def texto(x=540, y=1000, t="", tam=60, cor="#222", anchor="middle"):
    linhas = str(t).split("\n")
    return "".join(_txt(x, y + i * tam * 1.15, l, tam, cor, anchor) for i, l in enumerate(linhas))


def balao(x=540, y=800, t="", tam=46, w=None, cauda=(0, 0), pensamento=False):
    """Balão de fala centrado em (x,y). cauda = ponto (absoluto) para onde aponta. Use \\n para quebrar linha."""
    linhas = str(t).split("\n")
    w = w or max(len(l) for l in linhas) * tam * 0.55 + 70
    h = len(linhas) * tam * 1.15 + 50
    out = ""
    if cauda != (0, 0):
        cx, cy = cauda
        if pensamento:
            for k in (0.3, 0.6):
                out += _c(x + (cx - x) * k, y + h / 2 + (cy - y - h / 2) * k, 16 - 8 * k, fill="#fff")
        else:
            out += _p(f"M{x - 25:.1f},{y + h / 2 - 4:.1f} L{cx},{cy} L{x + 25:.1f},{y + h / 2 - 4:.1f} Z", fill="#fff")
    out += f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{min(h, w) / 2.2:.1f}" fill="#fff" {T}/>'
    out += "".join(_txt(x, y - h / 2 + 25 + tam * 0.9 + i * tam * 1.15, l, tam) for i, l in enumerate(linhas))
    return out


def pergaminho(x=540, y=1050, w=820, h=560, titulo="", linhas=(), tam=50, cor_titulo="#c0392b"):
    """Cartão de pergaminho para dados históricos/explicações. linhas = lista de textos curtos."""
    x0, y0 = x - w / 2, y - h / 2
    out = (f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="18" fill="#f6e7c1" {T}/>' +
           _p(f"M{x0 - 20:.1f},{y0 + 10:.1f} q-10,{h / 2 - 10:.1f} 0,{h - 20:.1f}", w=6) +
           _p(f"M{x0 + w + 20:.1f},{y0 + 10:.1f} q10,{h / 2 - 10:.1f} 0,{h - 20:.1f}", w=6))
    yy = y0 + 85
    if titulo:
        out += _txt(x, yy, titulo, tam * 1.1, cor_titulo)
        yy += tam * 1.5
    for l in linhas:
        out += _txt(x, yy, l, tam)
        yy += tam * 1.3
    return out


def interrogacao(x=540, y=900, tam=160, cor="#c0392b"):
    return _txt(x, y, "?", tam, cor)


def xis(x=540, y=1000, r=120, cor="#d9534f"):
    return _p(f"M{x - r},{y - r} L{x + r},{y + r} M{x + r},{y - r} L{x - r},{y + r}", cor=cor, w=14)


def certo(x=540, y=1000, r=120, cor="#3c9a4a"):
    return _p(f"M{x - r},{y} L{x - r * 0.3},{y + r * 0.7} L{x + r},{y - r * 0.8}", cor=cor, w=16)


def svg(codigo=""):
    return codigo


FUNCS = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_") and k not in ("escape",)}


def montar(itens):
    out = []
    for it in itens:
        it = dict(it)
        f = it.pop("f")
        if f not in FUNCS:
            raise SystemExit(f"Desenho desconhecido: {f}. Existem: {', '.join(sorted(FUNCS))}")
        if "cauda" in it:
            it["cauda"] = tuple(it["cauda"])
        out.append(FUNCS[f](**it))
    return "\n".join(out)
