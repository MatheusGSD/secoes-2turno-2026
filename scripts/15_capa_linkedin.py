"""Capa do artigo no LinkedIn (1920 x 1080): de 4.352 seções a 596 urnas, com o aviso de que os números ainda mudam.

Os três números são os do título do artigo: as seções que o TSE divulgou em 16/10, as urnas que mudam de prédio no
primeiro cadastro baixado (17/10, 6h28) e no atual. O atual vem de saida/numeros.json; a data do cadastro atual é
escrita à mão em CADASTRO, como em 14_imagem_versoes.py. O LinkedIn corta a capa no feed (cerca de 1,91:1), então o
texto fica longe das bordas de cima e de baixo.

Uso: python -P scripts/15_capa_linkedin.py   (depois de 03)
Saída: saida/capa_linkedin.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#8a8e96", "#dcdedf"
AVISO = "#c4923f"
FONTE, DADOS = "Segoe UI", "Consolas"
CADASTRO = "19/10, 15h27"


def fmt(v):
    return f"{v:,.0f}".replace(",", ".")


def main():
    n = json.loads((SAIDA / "numeros.json").read_text(encoding="utf-8"))
    passos = [(4352, "seções com local alterado,", "segundo o TSE em 16/10"),
              (2059, "urnas mudam de prédio no", "primeiro cadastro, de 17/10"),
              (n["mudadas"]["urnas"], "urnas mudam de prédio no", f"cadastro de {CADASTRO}")]

    fig = plt.figure(figsize=(9.6, 5.4), dpi=200, facecolor=PAPEL)
    t = lambda x, y, s, **k: fig.text(x, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)
    t(0.06, 0.84, "2º TURNO · 25/10/2026 · DADOS ABERTOS DO TSE", size=8, color=TINTA2, family=DADOS)
    t(0.06, 0.725, "Urnas que mudam de lugar no 2º turno", size=24, weight="bold")

    xs = [0.06, 0.37, 0.68]
    for i, (x, (v, l1, l2)) in enumerate(zip(xs, passos)):
        atual = i == len(passos) - 1
        t(x, 0.475, fmt(v), size=50 if atual else 40, weight="bold", color=TINTA if atual else TINTA3)
        t(x, 0.42, l1 + "\n" + l2, size=9.5, color=TINTA if atual else TINTA2, linespacing=1.35, va="top")
        if not atual:
            t(xs[i + 1] - 0.045, 0.51, "→", size=26, color=TINTA3, ha="center")

    fig.patches.append(plt.Rectangle((0.06, 0.2), 0.006, 0.075, transform=fig.transFigure, color=AVISO))
    t(0.078, 0.26, "Números sujeitos a atualização.", size=10, weight="bold", va="top")
    t(0.078, 0.217, "O TSE pode mudar locais até 25/10; a cada versão nova do cadastro, o artigo e o mapa são refeitos.",
      size=9, color=TINTA2, va="top")
    t(0.94, 0.075, "matheusgsd.github.io/secoes-2turno-2026", family=DADOS, size=8.5, ha="right")

    out = SAIDA / "capa_linkedin.png"
    fig.savefig(out, dpi=200, facecolor=PAPEL)
    print(out)


if __name__ == "__main__":
    main()
