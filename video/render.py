#!/usr/bin/env python
"""Monta o Short vertical (1080x1920, 30 fps): papel de caderno + rabiscos que "tremem" + legenda palavra por palavra + voz.

Uso:
  python render.py videos/malco                       -> saida/malco.mp4
  python render.py videos/malco --em "1,8,20,35"      -> só PNGs de conferência em saida/amostras/
  python render.py videos/malco --musica assets/musica/faixa.mp3   (música baixa que abaixa quando a voz fala)
Antes: python falar.py videos/malco  (gera voz.wav + tempos.json)
"""
import argparse, hashlib, json, math, re, subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import desenhos

BASE = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
FONTE = BASE / "assets" / "fonts" / "Kalam-Bold.ttf"
TREMOR = 3            # variações do traço (efeito rabisco vivo)
TROCA_TREMOR = 4      # troca a variação a cada N frames
CENTRO_ZOOM = (540, 1100)


# ------------------------------------------------------------------ papel
def papel():
    img = Image.new("RGB", (W, H), "#fbf7ec")
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    arr = np.asarray(img).astype(np.int16)
    arr += rng.integers(-6, 6, (H, W, 1), dtype=np.int16)  # textura leve
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for y in range(150, H, 64):
        d.line([(0, y), (W, y)], fill="#c9d9ee", width=3)
    d.line([(118, 0), (118, H)], fill="#ec9c9c", width=4)
    for y in (420, 960, 1500):
        d.ellipse([34, y - 24, 82, y + 24], fill="#e9e3d3", outline="#d6cfbd", width=3)
    return img


# ------------------------------------------------------------------ desenho -> PNG (Chromium)
def html_cena(svg_interno, seed):
    fonte = FONTE.as_uri()
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Kalam; src: url('{fonte}'); font-weight: bold; }}
html,body {{ margin:0; background:transparent; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><filter id="tr" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="{seed}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="7" xChannelSelector="R" yChannelSelector="G"/></filter></defs>
<g filter="url(#tr)">{svg_interno}</g></svg></body></html>"""


def renderizar_desenhos(rot, cache):
    cache.mkdir(parents=True, exist_ok=True)
    pendentes = []
    caminhos = []
    for i, cena in enumerate(rot["cenas"]):
        svg = desenhos.montar(cena.get("desenho", []))
        h = hashlib.md5((svg + str(TREMOR)).encode()).hexdigest()[:10]
        lst = []
        for k in range(TREMOR):
            p = cache / f"c{i:02d}_{h}_{k}.png"
            lst.append(p)
            if not p.exists():
                pendentes.append((p, html_cena(svg, 3 + k * 11)))
        caminhos.append(lst)
    if pendentes:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            nav = pw.chromium.launch()
            pg = nav.new_page(viewport={"width": W, "height": H})
            tmp = cache / "_cena.html"
            for p, html in pendentes:
                tmp.write_text(html, encoding="utf-8")
                pg.goto(tmp.as_uri())
                pg.wait_for_timeout(60)
                pg.screenshot(path=str(p), omit_background=True)
            nav.close()
            tmp.unlink(missing_ok=True)
        print(f"desenhos renderizados: {len(pendentes)}")
    out = []
    for lst in caminhos:
        vs = []
        for p in lst:
            im = Image.open(p).convert("RGBA")
            bb = im.getbbox() or (0, 0, 1, 1)
            vs.append((im.crop(bb), bb))
        out.append(vs)
    return out


# ------------------------------------------------------------------ legenda
def blocos(palavras, max_pal=4, max_chars=24):
    """Agrupa palavras em blocos curtos para a legenda, quebrando na pontuação."""
    out, cur = [], []
    for w in palavras:
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        if len(cur) >= max_pal or len(txt) >= max_chars or re.search(r"[.!?:;,…]$", w["w"]):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


class Legenda:
    def __init__(self, tam=88):
        self.f = ImageFont.truetype(str(FONTE), tam)
        self.tam = tam
        self.cache = {}

    def imagem(self, bloco, ativo):
        chave = (tuple(w["w"] for w in bloco), ativo)
        if chave in self.cache:
            return self.cache[chave]
        palavras = [w["w"] for w in bloco]
        # quebra em até 2 linhas
        linhas, cur = [], []
        for i, p in enumerate(palavras):
            teste = " ".join(palavras[j] for j in cur + [i])
            if cur and self.f.getlength(teste) > W - 200:
                linhas.append(cur)
                cur = []
            cur.append(i)
        linhas.append(cur)
        im = Image.new("RGBA", (W, int(self.tam * 1.25 * len(linhas) + 40)), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        esp = self.f.getlength(" ")
        for li, idxs in enumerate(linhas):
            larg = sum(self.f.getlength(palavras[i]) for i in idxs) + esp * (len(idxs) - 1)
            x = (W - larg) / 2
            y = 10 + li * self.tam * 1.2
            for i in idxs:
                cor = "#c0392b" if i == ativo else "#1d1d1d"
                d.text((x, y), palavras[i], font=self.f, fill=cor, stroke_width=9, stroke_fill="#fbf7ec")
                x += self.f.getlength(palavras[i]) + esp
        self.cache[chave] = im
        return im


def selo(texto, cor="#c0392b", tam=46):
    f = ImageFont.truetype(str(FONTE), tam)
    w = int(f.getlength(texto)) + 50
    im = Image.new("RGBA", (w + 20, tam + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, w + 6, tam + 36], radius=16, fill="#fbf7ec", outline=cor, width=5)
    d.text((31, 10), texto, font=f, fill=cor)
    return im


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# ------------------------------------------------------------------ montagem
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--em", help="segundos separados por vírgula: só gera PNGs de conferência")
    ap.add_argument("--musica")
    ap.add_argument("--vol-musica", type=float, default=0.18)
    ap.add_argument("--saida")
    a = ap.parse_args()

    pasta = Path(a.pasta).resolve()
    rot = json.loads((pasta / "roteiro.json").read_text(encoding="utf-8"))
    tempos = json.loads((pasta / "tempos.json").read_text(encoding="utf-8"))
    cenas_t = tempos["cenas"]
    if len(cenas_t) != len(rot["cenas"]):
        raise SystemExit("roteiro.json mudou depois da voz: rode falar.py de novo.")
    dur = tempos["dur"]
    imgs = renderizar_desenhos(rot, pasta / "_cache")
    fundo = papel()
    if rot.get("trecho"):  # trecho fixo no topo do vídeo (ex.: "Mateus 1:18-21")
        cab = selo(rot["trecho"], "#1d1d1d", 50)
        fundo.paste(cab, ((W - cab.width) // 2, 150), cab)
    leg = Legenda()
    selos = {}
    for i, c in enumerate(rot["cenas"]):
        s = []
        if c.get("tipo") == "historico":
            s.append(("hist", selo("DADO HISTÓRICO", "#8a5a12")))
        elif c.get("tipo") == "teologico":
            s.append(("hist", selo("TEOLOGIA", "#6b3fa0")))
        elif c.get("tipo") == "biblia":
            s.append(("hist", selo("O TEXTO BÍBLICO", "#2f5d9b")))
        if c.get("ref"):
            s.append(("ref", selo(c["ref"], "#2f5d9b", 42)))
        selos[i] = s
    leg_blocos = [blocos(c["palavras"]) for c in cenas_t]

    def cena_em(t):
        idx = 0
        for i, c in enumerate(cenas_t):
            if t >= c["ini"]:
                idx = i
        return idx

    def frame(n):
        t = n / FPS
        i = cena_em(t)
        c = cenas_t[i]
        fim_c = cenas_t[i + 1]["ini"] if i + 1 < len(cenas_t) else dur
        loc = t - c["ini"]
        frac = loc / max(0.1, fim_c - c["ini"])
        img = fundo.copy()
        k = (n // TROCA_TREMOR) % TREMOR

        def colar(i_, alpha, escala):
            pedaco, bb = imgs[i_][k]
            if escala != 1.0:
                pw_, ph_ = pedaco.size
                pedaco = pedaco.resize((max(1, int(pw_ * escala)), max(1, int(ph_ * escala))), Image.BILINEAR)
                x0 = int(CENTRO_ZOOM[0] + (bb[0] - CENTRO_ZOOM[0]) * escala)
                y0 = int(CENTRO_ZOOM[1] + (bb[1] - CENTRO_ZOOM[1]) * escala)
            else:
                x0, y0 = bb[0], bb[1]
            if alpha < 1:
                r, g, b_, al = pedaco.split()
                al = al.point(lambda v: int(v * alpha))
                pedaco = Image.merge("RGBA", (r, g, b_, al))
            img.paste(pedaco, (x0, y0), pedaco)

        entra = ease(loc / 0.35)
        if i > 0 and entra < 1:
            colar(i - 1, 1 - entra, 1.0 + 0.04)
        escala = (1.03 - 0.03 * entra) + 0.04 * frac * (rot["cenas"][i].get("zoom", 1))
        colar(i, entra, escala)

        for tipo, s in selos[i]:
            if tipo == "hist":
                img.paste(s.rotate(-3, expand=True, resample=Image.BICUBIC), (150, 590), s.rotate(-3, expand=True, resample=Image.BICUBIC))
            else:
                img.paste(s, (W - s.width - 60, 1580), s)

        # legenda: bloco atual da cena
        bl = leg_blocos[i]
        atual, ativo = None, None
        for b in bl:
            if t >= b[0]["ini"] - 0.05:
                atual = b
        if atual is not None and t <= atual[-1]["fim"] + 0.6:
            for j, w in enumerate(atual):
                if w["ini"] - 0.03 <= t:
                    ativo = j
            li = leg.imagem(atual, ativo)
            img.paste(li, (0, 330 - li.height // 2 + 40), li)
        return img

    saida_dir = BASE / "saida"
    if a.em:
        (saida_dir / "amostras").mkdir(parents=True, exist_ok=True)
        for s in a.em.split(","):
            p = saida_dir / "amostras" / f"{pasta.name}_{float(s):05.1f}.png"
            frame(int(float(s) * FPS)).save(p)
            print(p)
        return

    saida = Path(a.saida) if a.saida else saida_dir / f"{pasta.name}.mp4"
    saida.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", str(pasta / "voz.wav")]
    if a.musica:
        cmd += ["-stream_loop", "-1", "-i", a.musica, "-filter_complex",
                f"[2:a]volume={a.vol_musica}[m];[1:a]asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];"
                f"[v][md]amix=inputs=2:duration=first:normalize=0[a]", "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "27", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-shortest", str(saida)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(math.ceil(dur * FPS))
    for n in range(total):
        proc.stdin.write(frame(n).tobytes())
        if n % 300 == 0:
            print(f"  {n}/{total} frames")
    proc.stdin.close()
    proc.wait()
    print(f"OK: {saida}  ({dur:.1f}s)")


if __name__ == "__main__":
    main()
