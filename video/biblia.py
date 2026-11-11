#!/usr/bin/env python
"""Busca versículos nas Bíblias em JSON da pasta BIBLIA (nvi.json, acf.json, aa.json).

Uso:
  python biblia.py "jo 18:10-11"            -> NVI (padrão)
  python biblia.py "lc 22:49-51" --versao acf
  python biblia.py "mt 26" --versao aa       -> capítulo inteiro
  python biblia.py --buscar "Malco"          -> procura a palavra na versão escolhida
  python biblia.py --livros                  -> lista as abreviações
Abreviações aceitas: as do JSON (gn, ex, 1sm, jo, atos...) e nomes como "joão", "lucas", "1 samuel".
"""
import argparse, json, re, sys, unicodedata
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
# os JSON da Bíblia ficam na pasta BIBLIA (fora do repositório) ou em video/biblia/
PASTA = next((p for p in (_AQUI / "biblia", _AQUI.parent, _AQUI.parent.parent) if (p / "nvi.json").exists()), _AQUI.parent.parent)
sys.stdout.reconfigure(encoding="utf-8")


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def carregar(versao):
    with open(PASTA / f"{versao}.json", encoding="utf-8-sig") as f:
        return json.load(f)


def achar_livro(biblia, nome):
    n = sem_acento(nome).replace(" ", "")
    apelidos = {"jo": "jo", "joao": "jo", "job": "jó", "atos": "atos", "at": "atos", "sl": "sl", "salmos": "sl",
                "salmo": "sl", "ap": "ap", "apocalipse": "ap"}
    if n in apelidos:
        n = sem_acento(apelidos[n])
    for livro in biblia:
        if sem_acento(livro["abbrev"]) == n:
            return livro
    for livro in biblia:
        if sem_acento(livro["name"]).replace(" ", "") == n:
            return livro
    for livro in biblia:
        if sem_acento(livro["name"]).replace(" ", "").startswith(n):
            return livro
    raise SystemExit(f"Livro não encontrado: {nome}")


def referencia(biblia, ref):
    m = re.match(r"^\s*(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?\s*$", ref)
    if not m:
        raise SystemExit("Formato: 'jo 18:10-11' ou 'jo 18'")
    livro = achar_livro(biblia, m.group(1))
    cap = int(m.group(2))
    vs = livro["chapters"][cap - 1]
    ini = int(m.group(3) or 1)
    fim = int(m.group(4) or (m.group(3) or len(vs)))
    return livro["name"], cap, [(i, vs[i - 1]) for i in range(ini, min(fim, len(vs)) + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref", nargs="?")
    ap.add_argument("--versao", default="nvi", choices=["nvi", "acf", "aa"])
    ap.add_argument("--buscar")
    ap.add_argument("--livros", action="store_true")
    a = ap.parse_args()
    b = carregar(a.versao)
    if a.livros:
        print(", ".join(f"{l['abbrev']}={l['name']}" for l in b))
    elif a.buscar:
        alvo = sem_acento(a.buscar)
        for l in b:
            for c, vs in enumerate(l["chapters"], 1):
                for v, t in enumerate(vs, 1):
                    if alvo in sem_acento(t):
                        print(f"{l['name']} {c}:{v}  {t}")
    elif a.ref:
        nome, cap, vs = referencia(b, a.ref)
        print(f"{nome} {cap} ({a.versao.upper()})")
        for v, t in vs:
            print(f"{v} {t}")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
