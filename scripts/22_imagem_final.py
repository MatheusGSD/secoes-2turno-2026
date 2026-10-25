"""Cartão para o X (1600 x 900) do fechamento: a lista e o efeito estimado ao longo do tempo, versão por versão.

Em cima, as urnas que mudam de prédio do 1º para o 2º turno em cada versão do cadastro do TSE, no horário em que ela
foi gerada; embaixo, a variação estimada na vantagem de Flávio (comparação principal de 03_impacto.py) com o intervalo
de 95%. Os números de cada versão vêm do numeros.json daquela versão no git, como em 14_imagem_versoes.py.

Uso: python -P scripts/22_imagem_final.py   (depois de 03)
Saída: saida/imagem_final.png
"""
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import POR_EXTENSO, VERSOES  # noqa: E402

im14 = __import__("14_imagem_versoes")
numeros, fmt, sinal = im14.numeros, im14.fmt, im14.sinal
PAPEL, TINTA, TINTA2, TINTA3, LINHA = im14.PAPEL, im14.TINTA, im14.TINTA2, im14.TINTA3, im14.LINHA
FONTE, DADOS, SAIDA = im14.FONTE, im14.DADOS, im14.SAIDA
BANDA = "#c4923f"


def quando(rot):
    dia, hora = rot.split(", ")
    h, m = hora.split("h")
    d, mes = dia.split("/")
    return datetime(2026, int(mes), int(d), int(h), int(m))


def main():
    linhas = []
    for rot, commit, _ in VERSOES:
        n = numeros(commit)
        imp = n["impacto"][n["principal"]]
        linhas.append({"rot": rot, "t": quando(rot), "urnas": n["mudadas"]["urnas"], "margem": imp["margem"],
                       "ic": imp["margem_ic"], "diferenca": n["nacional"]["margem_votos"]})
    ts = [l["t"] for l in linhas]
    fim = datetime(2026, 10, 25, 8, 0)

    fig = plt.figure(figsize=(8, 4.5), dpi=200, facecolor=PAPEL)
    t = lambda x, y, s, **k: fig.text(x, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)  # noqa: E731
    de, a = (v[0].split(",")[0] for v in (VERSOES[0], VERSOES[-1]))
    t(0.045, 0.915, f"2º TURNO · 25/10/2026 · {POR_EXTENSO[len(VERSOES)]} VERSÕES DO CADASTRO DO TSE, DE {de} A {a}", size=7,
      color=TINTA2, family=DADOS)
    t(0.045, 0.80, f"{len(VERSOES)} versões da lista. O efeito ficou perto de zero em todas.", size=18, weight="bold")
    t(0.045, 0.735, "Urnas que mudam de prédio do 1º para o 2º turno a cada versão do cadastro, no horário em que foi gerada,\n"
                    "e a variação estimada na vantagem de Flávio, com base no que aconteceu em 2022.",
      size=8.2, color=TINTA2, linespacing=1.4, va="top")

    # em cima: urnas por versão
    ax = fig.add_axes([0.075, 0.385, 0.83, 0.225])
    ax.set_facecolor(PAPEL)
    us = [l["urnas"] for l in linhas]
    ax.step(ts + [fim], us + [us[-1]], where="post", color=TINTA, lw=1.6, zorder=2)
    ax.plot(ts, us, "o", ms=2.6, color=TINTA, zorder=3)
    menor = min(linhas, key=lambda l: l["urnas"])
    marcas = [(linhas[0], "1º cadastro", (4, 5), "left"), (linhas[3], None, (6, 4), "left"),
              (linhas[4], None, (6, 4), "left"), (menor, "menor lista", (0, -14), "center"),
              (linhas[-1], "dia da eleição", (-6, 6), "right")]
    for l, nota, (dx, dy), ha in marcas:
        txt = fmt(l["urnas"]) + (f"  {nota}" if nota and ha != "right" else "")
        if ha == "right":
            txt = f"{nota}  " + fmt(l["urnas"])
        ax.annotate(txt, (l["t"], l["urnas"]), xytext=(dx, dy), textcoords="offset points", ha=ha, va="bottom",
                    family=DADOS, size=7, color=TINTA, weight="bold" if l is linhas[-1] else "normal")
    ax.set_ylim(-300, 2400)
    ax.set_yticks([0, 1000, 2000], ["0", "1.000", "2.000"])
    t(0.045, 0.645, "URNAS QUE MUDAM DE PRÉDIO", size=6.5, color=TINTA2, family=DADOS)

    # embaixo: efeito estimado
    bx = fig.add_axes([0.075, 0.13, 0.83, 0.17], sharex=ax)
    bx.set_facecolor(PAPEL)
    lo = [l["ic"][0] for l in linhas]
    hi = [l["ic"][1] for l in linhas]
    bx.fill_between(ts + [fim], lo + [lo[-1]], hi + [hi[-1]], step="post", color=BANDA, alpha=0.35, lw=0, zorder=1)
    bx.axhline(0, color=TINTA3, lw=0.8, zorder=2)
    ms = [l["margem"] for l in linhas]
    bx.step(ts + [fim], ms + [ms[-1]], where="post", color=TINTA, lw=1.4, zorder=3)
    u = linhas[-1]
    bx.annotate(f"{sinal(u['margem'])} votos ({sinal(u['ic'][0])} a {sinal(u['ic'][1])})", (u["t"], u["ic"][1]),
                xytext=(-4, 4), textcoords="offset points", ha="right", va="bottom", family=DADOS, size=7,
                weight="bold", color=TINTA)
    bx.set_ylim(-130, 130)
    bx.set_yticks([-100, 0, 100], ["−100", "0", "+100"])
    dif = u["diferenca"] / 1e6
    t(0.045, 0.325, "VARIAÇÃO ESTIMADA NA VANTAGEM DE FLÁVIO, EM VOTOS (FAIXA: INTERVALO DE 95%). DIFERENÇA NO 1º TURNO: "
      + f"{dif:.2f}".replace(".", ",") + " MILHÕES", size=6.5, color=TINTA2, family=DADOS)

    for eixo in (ax, bx):
        for lado in ["top", "right", "left"]:
            eixo.spines[lado].set_visible(False)
        eixo.spines["bottom"].set_color(LINHA)
        eixo.tick_params(labelsize=6.5, colors=TINTA2, length=0)
        eixo.grid(axis="y", color=LINHA, lw=0.5, zorder=0)
        for tick in eixo.get_yticklabels() + eixo.get_xticklabels():
            tick.set_fontfamily(DADOS)
    ax.tick_params(labelbottom=False)
    bx.set_xlim(datetime(2026, 10, 17), fim)
    bx.xaxis.set_major_locator(mdates.DayLocator())
    bx.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))

    fig.text(0.955, 0.03, "matheusgsd.github.io/secoes-2turno-2026", family=DADOS, size=7.4, color=TINTA, ha="right")
    out = SAIDA / "imagem_final.png"
    fig.savefig(out, dpi=200, facecolor=PAPEL)
    print(out)


if __name__ == "__main__":
    main()
