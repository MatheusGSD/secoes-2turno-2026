"""Cartão para o X (1600 x 900): locais de votação com urna que muda de prédio, por faixa de voto em Lula.

Usa os mesmos dados da página (docs/dados.json, bloco "por_local_faixas", de 09_por_local.py), só com as urnas
que mudam de prédio (a chave da lista, "urnas que mudam de prédio", vem de 09_por_local.py): no país, e
comparando cada local com o resultado de Lula no próprio estado e no próprio município.

Uso: python -P scripts/10_imagem_por_local.py   (depois de 09 e 04)
Saída: saida/imagem_por_local.png
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import cabecalho  # noqa: E402
SAIDA = RAIZ / "saida"
PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#80848c", "#dcdedf"
FONTE, DADOS = "Segoe UI", "Consolas"
LISTA = "urnas que mudam de prédio"
PAINEIS = [("país", "No país", "Lula no local, em %", ["30%", "45%", "60%", "75%"]),
           ("estado", "Comparando com o estado", "pontos de Lula acima ou abaixo do estado", ["−10", "−5", "0", "+5", "+10"]),
           ("município", "Comparando com o município", "pontos de Lula acima ou abaixo do município", ["−10", "−5", "0", "+5", "+10"])]


def pct(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


def main():
    d = json.loads((RAIZ / "docs/dados.json").read_text(encoding="utf-8"))
    fx = [r for r in d["por_local_faixas"] if r["lista"] == LISTA]
    pais = [r for r in fx if r["painel"] == "país"]
    media = 100 * sum(r["na_lista"] for r in pais) / sum(r["locais"] for r in pais)

    fig = plt.figure(figsize=(8, 4.5), dpi=200, facecolor=PAPEL)
    t = lambda x, y, s, **k: fig.text(x, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)
    t(0.045, 0.915, f"2º TURNO · 25/10/2026 · {cabecalho()} · LOCAIS DE VOTAÇÃO E VOTO NO 1º TURNO", size=7,
      color=TINTA2, family=DADOS)
    t(0.045, 0.80, "Onde Lula foi melhor, mais urnas mudam de prédio?", size=17, weight="bold")
    t(0.045, 0.735, "No país, pouco: só os locais onde Lula teve menos de 30% ficam abaixo da média. Comparando cada local com o\n"
                    "próprio estado ou município, a linha varia pouco, dentro da margem de erro: as mudanças não se concentram nos locais mais lulistas.",
      size=8.2, color=TINTA2, linespacing=1.4, va="top")

    largura, x = 0.27, 0.075
    for chave, titulo, eixo, limites in PAINEIS:
        rs = [r for r in fx if r["painel"] == chave]
        ax = fig.add_axes([x, 0.215, largura, 0.37])
        ax.set_facecolor(PAPEL)
        xs = list(range(len(rs)))
        ys = [r["pct"] for r in rs]
        ax.axhline(media, color=TINTA3, linewidth=0.7, linestyle=(0, (3, 3)))
        ax.vlines(xs, [r["ic"][0] for r in rs], [r["ic"][1] for r in rs], color=TINTA, linewidth=1.3)
        ax.plot(xs, ys, color=TINTA, linewidth=1.6)
        ax.scatter(xs, ys, s=22, color=TINTA, edgecolors=PAPEL, linewidths=1.2, zorder=3)
        ax.set_ylim(0, 1.0)
        ax.set_xlim(-0.5, len(rs) - 0.5)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels([pct(v) + "%" for v in [0, 0.25, 0.5, 0.75, 1.0]] if chave == "país" else [])
        ax.set_xticks([i + 0.5 for i in range(len(limites))])
        ax.set_xticklabels(limites)
        ax.tick_params(colors=TINTA2, labelsize=7.6, length=2.5, width=0.6)
        if chave != "país":
            ax.tick_params(axis="y", length=0)
        for lb in ax.get_xticklabels() + ax.get_yticklabels():
            lb.set_family(DADOS)
        ax.grid(axis="y", color=LINHA, linewidth=0.6)
        ax.set_axisbelow(True)
        for lado in ["top", "right", "left"]:
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color(TINTA2)
        ax.set_title(titulo, loc="left", fontsize=9.4, fontweight="bold", color=TINTA, family=FONTE, pad=6)
        ax.set_xlabel(eixo, fontsize=7.4, color=TINTA2, family=FONTE, labelpad=3)
        if chave == "país":
            ax.set_ylabel("% dos locais de votação", fontsize=7.4, color=TINTA2, family=FONTE, labelpad=4)
            ax.text(-0.45, media + 0.03, "média", fontsize=7, color=TINTA3, family=FONTE)
        x += largura + 0.035

    t(0.045, 0.045, "Locais de votação com alguma urna que muda de prédio do 1º para o 2º turno, por faixa de voto em Lula\n"
                    "no 1º turno, com intervalo de 95%. Dados: TSE.", size=6.8, color=TINTA3, linespacing=1.35)
    t(0.955, 0.05, "matheusgsd.github.io/secoes-2turno-2026", size=7.4, family=DADOS, ha="right")

    out = SAIDA / "imagem_por_local.png"
    fig.savefig(out, dpi=200, facecolor=PAPEL)
    print(out, fig.get_size_inches() * 200)


if __name__ == "__main__":
    main()
