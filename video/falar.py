#!/usr/bin/env python
"""Narração do roteiro com a voz Kokoro (offline, grátis, Apache 2.0) e tempos de cada palavra.

Uso:  python falar.py videos/malco            -> videos/malco/voz.wav + tempos.json
      python falar.py videos/malco --voz pm_alex --vel 1.05

Cada cena do roteiro.json tem "fala". Cada frase é gerada separada (tempo exato de início e fim);
dentro da frase, o tempo de cada palavra é proporcional ao tamanho dela (bom para legenda em blocos).
"pronuncia" na cena troca palavras só na voz: {"Malco": "Málco"} (a legenda continua com o texto original).
"""
import argparse, json, os, re
from pathlib import Path

import numpy as np
import soundfile as sf

BASE = Path(__file__).resolve().parent
SR = 24000
TTS_PADRAO = Path(os.environ.get("KOKORO_DIR", BASE / "assets" / "tts"))
TTS_RESERVA = Path(r"C:\Users\Win 11\Desktop\WORKSPACE\MINHAS_SKILS\mais_musica\assets\tts")


def pasta_tts():
    for p in (TTS_PADRAO, TTS_RESERVA):
        if (p / "kokoro-v1.0.onnx").exists():
            return p
    raise SystemExit("Modelo Kokoro não encontrado (kokoro-v1.0.onnx + voices-v1.0.bin). Defina KOKORO_DIR.")


def frases(texto):
    return [f.strip() for f in re.findall(r"[^.!?…]+[.!?…]*[\"”']?", texto) if re.search(r"\w", f)]


def aparar(y, lim=0.01):
    idx = np.where(np.abs(y) > lim)[0]
    if len(idx) == 0:
        return y
    a = max(0, idx[0] - int(0.02 * SR))
    b = min(len(y), idx[-1] + int(0.06 * SR))
    return y[a:b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--voz", default="pm_santa")
    ap.add_argument("--vel", type=float, default=1.0)
    ap.add_argument("--pausa-frase", type=float, default=0.22)
    ap.add_argument("--pausa-cena", type=float, default=0.45)
    a = ap.parse_args()

    from kokoro_onnx import Kokoro
    tts = pasta_tts()
    k = Kokoro(str(tts / "kokoro-v1.0.onnx"), str(tts / "voices-v1.0.bin"))

    pasta = Path(a.pasta)
    rot = json.loads((pasta / "roteiro.json").read_text(encoding="utf-8"))
    audio, t, cenas_t = [np.zeros(int(0.25 * SR), np.float32)], 0.25, []
    for i, cena in enumerate(rot["cenas"]):
        pron = cena.get("pronuncia", {})
        ini_cena, palavras = t, []
        for fr in frases(cena["fala"]):
            falada = fr
            for k_, v_ in pron.items():
                falada = re.sub(r"\b" + re.escape(k_) + r"\b", v_, falada)
            y, _ = k.create(falada, voice=a.voz, speed=a.vel * cena.get("vel", 1.0), lang="pt-br")
            y = aparar(np.asarray(y, np.float32))
            dur = len(y) / SR
            ws = fr.split()
            pesos = [len(re.sub(r"\W", "", w)) + 2 for w in ws]
            tot, acc = sum(pesos), 0
            for w, p in zip(ws, pesos):
                palavras.append({"w": w, "ini": round(t + dur * acc / tot, 3), "fim": round(t + dur * (acc + p) / tot, 3)})
                acc += p
            audio.append(y)
            t += dur
            audio.append(np.zeros(int(a.pausa_frase * SR), np.float32))
            t += a.pausa_frase
        extra = cena.get("pausa_depois", a.pausa_cena) - a.pausa_frase
        if extra > 0:
            audio.append(np.zeros(int(extra * SR), np.float32))
            t += extra
        cenas_t.append({"ini": round(ini_cena, 3), "fim": round(t, 3), "palavras": palavras})
        print(f"cena {i + 1}: {ini_cena:6.2f}s - {t:6.2f}s  {cena['fala'][:60]}")
    audio.append(np.zeros(int(0.6 * SR), np.float32))
    y = np.concatenate(audio)
    y = y / max(1e-6, np.abs(y).max()) * 0.9
    sf.write(pasta / "voz.wav", y, SR)
    (pasta / "tempos.json").write_text(json.dumps({"dur": round(len(y) / SR, 3), "cenas": cenas_t}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {pasta / 'voz.wav'}  ({len(y) / SR:.1f}s)")


if __name__ == "__main__":
    main()
