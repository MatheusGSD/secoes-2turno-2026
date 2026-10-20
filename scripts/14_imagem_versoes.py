"""Cartão para o X (1600 x 900): a lista em cada versão do cadastro do TSE e o efeito estimado em cada uma.

À esquerda, as urnas que mudam de prédio do 1º para o 2º turno em cada versão do cadastro, separando as que voltam ao
local de sempre; à direita, a variação estimada na vantagem de Flávio (comparação principal de 03_impacto.py, com
intervalo de 95%). Os números de cada versão vêm do numeros.json daquela versão no git (VERSOES, como em
12_renovadas.py); a versão atual, de saida/numeros.json.

Uso: python -P scripts/14_imagem_versoes.py   (depois de 03)
Saída: saida/imagem_versoes.png
"""
import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.transforms import blended_transform_factory

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import POR_EXTENSO, VERSOES  # noqa: E402

SAIDA = RAIZ / "saida"
PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#6a6e76", "#dcdedf"
VOLTA, SAI = "#c4923f", "#121417"
FONTE, DADOS = "Segoe UI", "Consolas"
VOLTA_TIPO = "voltou ao local de cadastro"


def numeros(commit):
    if commit is None:
        return json.loads((SAIDA / "numeros.json").read_text(encoding="utf-8"))
    out = subprocess.run(["git", "show", f"{commit}:saida/numeros.json"], cwd=RAIZ, capture_output=True, check=True).stdout
    return json.loads(out)


def fmt(v):
    return f"{v:,.0f}".replace(",", ".").replace("-", "−")


def sinal(v):
    return ("+" if round(v) > 0 else "") + fmt(v)


def main():
    linhas = []
    for rot, commit, _ in VERSOES:
        n = numeros(commit)
        voltam = next(t["urnas"] for t in n["tipos"] if t["tipo"] == VOLTA_TIPO)
        imp = n["impacto"][n["principal"]]
        linhas.append({"rot": rot, "urnas": n["mudadas"]["urnas"], "voltam": voltam, "margem": imp["margem"],
                       "ic": imp["margem_ic"], "diferenca": n["nacional"]["margem_votos"]})
    for l in linhas:
        print(l)

    fig = plt.figure(figsize=(8, 4.5), dpi=200, facecolor=PAPEL)
    t = lambda x, y, s, **k: fig.text(x, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)
    de, a = (v[0].split(",")[0] for v in (VERSOES[0], VERSOES[-1]))
    t(0.045, 0.915, f"2º TURNO · 25/10/2026 · {POR_EXTENSO[len(VERSOES)]} VERSÕES DO CADASTRO DO TSE, DE {de} A {a}", size=7,
      color=TINTA2, family=DADOS)
    t(0.045, 0.80, "A lista encolheu. A conclusão, não.", size=20, weight="bold")
    t(0.045, 0.735, "Urnas que mudam de prédio do 1º para o 2º turno em cada versão do cadastro e o efeito estimado no resultado,\n"
                    "com base no que aconteceu em 2022, quando 1.506 urnas trocaram de prédio entre os turnos.",
      size=8.2, color=TINTA2, linespacing=1.4, va="top")

    ys = np.arange(len(linhas))[::-1]
    # esquerda: urnas por versão
    ax = fig.add_axes([0.16, 0.16, 0.36, 0.42])
    ax.set_facecolor(PAPEL)
    vmax = max(l["urnas"] for l in linhas)
    for y, l in zip(ys, linhas):
        atual = l is linhas[-1]
        outras = l["urnas"] - l["voltam"]
        ax.barh(y, outras, height=0.6, color=SAI)
        ax.barh(y, l["voltam"], left=outras, height=0.6, color=VOLTA)
        ax.text(l["urnas"] + vmax * 0.02, y, fmt(l["urnas"]), va="center", family=DADOS, size=8,
                weight="bold" if atual else "normal", color=TINTA)
        ax.text(-0.03, y, l["rot"], transform=blended_transform_factory(ax.transAxes, ax.transData), ha="right",
                va="center", family=DADOS, size=7, weight="bold" if atual else "normal", color=TINTA if atual else TINTA2)
    ax.set_xlim(0, vmax * 1.18)
    ax.set_ylim(-0.6, len(linhas) - 0.4)
    ax.axis("off")
    t(0.045, 0.635, "URNAS QUE MUDAM DE PRÉDIO", size=6.5, color=TINTA2, family=DADOS)
    fig.patches.append(plt.Rectangle((0.045, 0.098), 0.012, 0.022, transform=fig.transFigure, color=SAI))
    t(0.062, 0.1, "saem do local de sempre ou trocam de prédio", size=6.6, color=TINTA2)
    fig.patches.append(plt.Rectangle((0.335, 0.098), 0.012, 0.022, transform=fig.transFigure, color=VOLTA))
    t(0.352, 0.1, "voltam ao local de sempre", size=6.6, color=TINTA2)

    # direita: efeito estimado com intervalo
    bx = fig.add_axes([0.6, 0.16, 0.25, 0.42])
    bx.set_facecolor(PAPEL)
    lim = 150
    bx.axvline(0, color=TINTA3, lw=0.8, zorder=1)
    for y, l in zip(ys, linhas):
        atual = l is linhas[-1]
        bx.plot(l["ic"], [y, y], color=TINTA, lw=2.2 if atual else 1.4, solid_capstyle="butt", zorder=2)
        bx.plot([l["margem"]], [y], "o", ms=5.5 if atual else 4.5, color=TINTA, mec=PAPEL, mew=0.8, zorder=3)
        bx.text(lim * 1.08, y, f"{sinal(l['ic'][0])} a {sinal(l['ic'][1])}", va="center", family=DADOS, size=7.4,
                weight="bold" if atual else "normal", color=TINTA)
    bx.set_xlim(-lim, lim)
    bx.set_ylim(-0.6, len(linhas) - 0.4)
    bx.set_yticks([])
    bx.set_xticks([-100, 0, 100], ["−100", "0", "+100"])
    bx.tick_params(axis="x", labelsize=6.5, colors=TINTA2, length=0)
    for lado in ["top", "right", "left"]:
        bx.spines[lado].set_visible(False)
    bx.spines["bottom"].set_color(LINHA)
    for tick in bx.get_xticklabels():
        tick.set_fontfamily(DADOS)
    t(0.6, 0.635, "VARIAÇÃO ESTIMADA NA VANTAGEM DE FLÁVIO", size=6.5, color=TINTA2, family=DADOS)
    dif = linhas[-1]["diferenca"] / 1e6
    t(0.6, 0.1, "Intervalo de 95%, em votos. A diferença no 1º turno foi de " + f"{dif:.2f}".replace(".", ",") + " milhões.",
      size=6.6, color=TINTA2)

    fig.text(0.955, 0.03, "matheusgsd.github.io/secoes-2turno-2026", family=DADOS, size=7.4, color=TINTA, ha="right")
    out = SAIDA / "imagem_versoes.png"
    fig.savefig(out, dpi=200, facecolor=PAPEL)
    print(out)


if __name__ == "__main__":
    main()
