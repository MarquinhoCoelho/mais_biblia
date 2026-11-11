#!/usr/bin/env python
"""Sobe um vídeo pronto para a API do app Mais Bíblia (aparece no app na hora, sem APK novo).

Uso:  python publicar.py videos/mt01a                 (usa saida/mt01a.mp4 e o roteiro.json)
      python publicar.py videos/mt01a --api http://localhost:3070
      python publicar.py --apagar mt01a
Config em video/.env (não vai para o git):  MAIS_BIBLIA_API=http://92.112.176.96:3070   MAIS_BIBLIA_TOKEN=...
O roteiro.json precisa de: livro (abreviação: mt, mc, lc, jo, gn...), capitulo, versiculos, parte, titulo, trecho.
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")


def env():
    e = {}
    for arq in (BASE / ".env",):
        if arq.exists():
            for l in arq.read_text(encoding="utf-8").splitlines():
                if "=" in l and not l.lstrip().startswith("#"):
                    k, v = l.split("=", 1)
                    e[k.strip()] = v.strip().strip("\"'")
    e.update({k: v for k, v in os.environ.items() if k.startswith("MAIS_BIBLIA_")})
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta", nargs="?")
    ap.add_argument("--api")
    ap.add_argument("--apagar")
    a = ap.parse_args()
    e = env()
    api = (a.api or e.get("MAIS_BIBLIA_API", "")).rstrip("/")
    tok = e.get("MAIS_BIBLIA_TOKEN", "")
    if not api or not tok:
        raise SystemExit("Defina MAIS_BIBLIA_API e MAIS_BIBLIA_TOKEN em video/.env")
    cab = {"Authorization": f"Bearer {tok}"}
    if a.apagar:
        r = requests.delete(f"{api}/api/videos/{a.apagar}", headers=cab, timeout=30)
        print(r.status_code, r.text)
        return

    pasta = Path(a.pasta).resolve()
    rot = json.loads((pasta / "roteiro.json").read_text(encoding="utf-8"))
    mp4 = BASE / "saida" / f"{pasta.name}.mp4"
    if not mp4.exists():
        raise SystemExit(f"Falta {mp4}: rode render.py antes.")
    tempos = json.loads((pasta / "tempos.json").read_text(encoding="utf-8"))
    meta = {
        "id": pasta.name, "livro": rot["livro"], "capitulo": rot["capitulo"], "versiculos": rot.get("versiculos", ""),
        "parte": rot.get("parte", 1), "titulo": rot["titulo"], "trecho": rot.get("trecho", ""),
        "descricao": rot.get("descricao", ""), "fontes": rot.get("fontes", []), "duracao": round(tempos["dur"], 1),
    }
    capa = Path(tempfile.gettempdir()) / f"{pasta.name}_capa.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", str(mp4), "-frames:v", "1",
                    "-vf", "scale=540:-2", "-q:v", "4", str(capa)], check=True)
    with open(mp4, "rb") as fv, open(capa, "rb") as fc:
        r = requests.post(f"{api}/api/videos", headers=cab, data={"meta": json.dumps(meta, ensure_ascii=False)},
                          files={"video": (mp4.name, fv, "video/mp4"), "capa": (capa.name, fc, "image/jpeg")}, timeout=600)
    capa.unlink(missing_ok=True)
    if r.status_code >= 300:
        raise SystemExit(f"Erro {r.status_code}: {r.text}")
    print("OK:", r.json()["url"])


if __name__ == "__main__":
    main()
