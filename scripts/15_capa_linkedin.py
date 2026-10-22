"""Capa do artigo no LinkedIn (1920 x 1080): o mapa das urnas que mudam de lugar, em fundo escuro, com o número atual.

À direita, o mapa da página (docs/dados.json): cada ponto claro é um local de votação do 2º turno, e os círculos são
as urnas que mudam, na cor de quem venceu ali no 1º turno, do tamanho dos eleitores (como em 05_imagem_x.py). À
esquerda, em letra grande, o número atual e o caminho desde as 4.352 seções divulgadas pelo TSE; um degradê deixa o
texto legível onde ele encosta no mapa. A data do cadastro atual vem de versoes.py.
Versão escolhida no protótipo rascunhos/prototipo_capa.py (variante A).

No feed, o LinkedIn corta a capa para 1,91:1 (cerca de 37 px em cima e embaixo). Mapa e texto ficam dentro de
MARGEM, com folga. Para conferir, rode com --corte: a saída ganha linhas tracejadas onde o feed corta.

Uso: python -P scripts/15_capa_linkedin.py [--corte]   (depois de 04)
Saída: saida/capa_linkedin.png (com --corte, saida/capa_linkedin_corte.png, só para conferência)
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import ATUAL as CADASTRO  # noqa: E402

SAIDA = RAIZ / "saida"
FUNDO, TINTA, TINTA2, PONTO = "#0e1014", "#f5f6f8", "#b4b9c1", "#d7dbe1"
LULA, FLAVIO = "#ee6f61", "#5f97ea"
FONTE, DADOS = "Segoe UI", "Consolas"
MARGEM = 0.075  # fração da altura livre em cima e embaixo (o corte do feed é ~0,035)


def merc(lon, lat):
    lat = np.radians(np.clip(lat, -80, 80))
    return np.asarray(lon), np.degrees(np.log(np.tan(np.pi / 4 + lat / 2)))


def fmt(v):
    return f"{v:,.0f}".replace(",", ".")


def main():
    d = json.loads((RAIZ / "docs/dados.json").read_text(encoding="utf-8"))
    m = d["numeros"]["mudadas"]
    f = np.cumsum(np.array(d["fundo"]).reshape(-1, 2), axis=0) / 1000
    bx, by = merc(f[:, 0], f[:, 1])
    pares = [p for p in d["pares"] if p["tipo"] != "confusao" and (p["b"][0] if p["b"][0] is not None else p["a"][0]) is not None]
    pos = np.array([p["b"] if p["b"][0] is not None else p["a"] for p in pares], dtype=float)
    px, py = merc(pos[:, 0], pos[:, 1])
    aptos = np.array([p["aptos"] for p in pares])
    cor = np.array([LULA if p["lula"] > p["flavio"] else FLAVIO for p in pares])
    ordem = np.argsort(-aptos)  # grandes embaixo, pequenos por cima

    fig = plt.figure(figsize=(9.6, 5.4), dpi=200, facecolor=FUNDO)
    # mapa à direita, inteiro dentro da margem (aspecto igual: a largura se ajusta à altura)
    ax = fig.add_axes([0.47, MARGEM, 0.5, 1 - 2 * MARGEM])
    ax.set_facecolor(FUNDO)
    ax.scatter(bx, by, s=0.35, c=PONTO, alpha=0.3, linewidths=0, rasterized=True)
    s = 5 + aptos[ordem] / 26
    ax.scatter(px[ordem], py[ordem], s=s * 4.5, c=cor[ordem], alpha=0.16, linewidths=0)  # halo
    ax.scatter(px[ordem], py[ordem], s=s, c=cor[ordem], alpha=0.95, edgecolors=FUNDO, linewidths=0.4)
    ax.set_xlim(-74.5, -34.2)
    ax.set_ylim(*merc(0, np.array([-34.2, 5.8]))[1])
    ax.set_aspect("equal", anchor="E")
    ax.axis("off")
    # degradê para o texto ler bem onde encosta no mapa
    g = fig.add_axes([0, 0, 0.66, 1], zorder=1)
    cm = LinearSegmentedColormap.from_list("g", [(14 / 255, 16 / 255, 20 / 255, 1), (14 / 255, 16 / 255, 20 / 255, 0)])
    g.imshow(np.linspace(0, 1, 256)[None, :] ** 1.6, aspect="auto", cmap=cm, extent=(0, 1, 0, 1))
    g.axis("off")

    t = lambda x, y, s, **k: fig.text(x, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), zorder=2, **k)
    t(0.05, 0.835, "2º TURNO · 25/10 · DADOS ABERTOS DO TSE", size=12, color=TINTA2, family=DADOS)
    t(0.05, 0.785, "Urnas que mudam\nde lugar no 2º turno", size=34, weight="bold", va="top", linespacing=1.0)
    t(0.045, 0.31, fmt(m["urnas"]), size=118, weight="bold")
    t(0.05, 0.275, f"urnas, pelo cadastro de {CADASTRO}.\nO TSE falou em 4.352 seções.", size=15, color=TINTA2,
      va="top", linespacing=1.3)
    y = 0.13
    for x, c, rot in [(0.05, LULA, "Lula venceu ali no 1º turno"), (0.30, FLAVIO, "Flávio venceu")]:
        t(x, y, "●", size=14, color=c, va="baseline")
        t(x + 0.022, y, rot, size=12, color=TINTA2, va="baseline")
    t(0.05, MARGEM + 0.008, "matheusgsd.github.io/secoes-2turno-2026", size=12, color=TINTA2, family=DADOS)

    out = SAIDA / "capa_linkedin.png"
    fig.savefig(out, dpi=200, facecolor=FUNDO)
    print(out)
    if "--corte" in sys.argv:
        corte = (1 - 1920 / 1.91 / 1080) / 2
        for yy in (corte, 1 - corte):
            fig.add_artist(plt.Line2D([0, 1], [yy, yy], color="#ffd54a", lw=1.2, ls="--", zorder=5))
        fig.savefig(SAIDA / "capa_linkedin_corte.png", dpi=200, facecolor=FUNDO)
        print(SAIDA / "capa_linkedin_corte.png")


if __name__ == "__main__":
    main()
