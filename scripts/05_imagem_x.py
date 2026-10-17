"""Cartão para o X (1600 x 900): mapa das urnas que mudam de lugar e os números principais.

Usa os mesmos dados da página (docs/dados.json). Fundo: todos os locais de votação do 2º turno;
círculos: as urnas que mudam, na cor de quem venceu ali no 1º turno, do tamanho dos eleitores.

Uso: python -P scripts/05_imagem_x.py   (depois de 04)
Saída: saida/imagem_x.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#80848c", "#dcdedf"
LULA, FLAVIO, PONTO = "#d4574a", "#3f74c2", "#9a9fa6"
FONTE, DADOS = "Segoe UI", "Consolas"


def merc(lon, lat):
    lat = np.radians(np.clip(lat, -80, 80))
    return np.asarray(lon), np.degrees(np.log(np.tan(np.pi / 4 + lat / 2)))


def main():
    d = json.loads((RAIZ / "docs/dados.json").read_text(encoding="utf-8"))
    n, m = d["numeros"]["nacional"], d["numeros"]["mudadas"]
    f = np.cumsum(np.array(d["fundo"]).reshape(-1, 2), axis=0) / 1000
    bx, by = merc(f[:, 0], f[:, 1])
    pares = [p for p in d["pares"] if (p["b"][0] if p["b"][0] is not None else p["a"][0]) is not None]
    pos = np.array([p["b"] if p["b"][0] is not None else p["a"] for p in pares], dtype=float)
    px, py = merc(pos[:, 0], pos[:, 1])
    aptos = np.array([p["aptos"] for p in pares])
    cor = [LULA if p["lula"] > p["flavio"] else FLAVIO if p["flavio"] > p["lula"] else TINTA3 for p in pares]
    ordem = np.argsort(-aptos)  # grandes embaixo, pequenos por cima

    fig = plt.figure(figsize=(8, 4.5), dpi=200, facecolor=PAPEL)
    ax = fig.add_axes([0.0, 0.03, 0.52, 0.94])
    ax.set_facecolor(PAPEL)
    ax.scatter(bx, by, s=0.5, c=PONTO, alpha=0.6, linewidths=0, rasterized=True)
    ax.scatter(px[ordem], py[ordem], s=2 + aptos[ordem] / 55, c=np.array(cor)[ordem], alpha=0.9,
               edgecolors=PAPEL, linewidths=0.35)
    ax.set_xlim(-74.5, -34.2)
    ax.set_ylim(*merc(0, np.array([-34.2, 5.8]))[1])
    ax.set_aspect("equal")
    ax.axis("off")

    x0 = 0.535
    t = lambda y, s, **k: fig.text(x0, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)
    t(0.905, "2º TURNO · 25/10/2026 · DADOS DO TSE DE 17/10", size=7, color=TINTA2, family=DADOS)
    t(0.80, "Urnas que mudam de lugar", size=20, weight="bold")
    t(0.62, f"{m['urnas']:,}".replace(",", "."), size=34, weight="bold")
    fatia = f"{100 * m['validos'] / n['validos']:.1f}".replace(".", ",")
    t(0.555, f"urnas votam no 2º turno num prédio diferente do 1º,\ncom {fatia}% dos votos válidos do país",
      size=8.6, color=TINTA2, linespacing=1.35, va="top")

    itens = [
        ("Metade muda menos de 410 m", "do local onde a urna funcionou no 1º turno"),
        ("Votam igual às urnas vizinhas", "da mesma zona eleitoral, sem pender para um lado"),
        ("Efeito no resultado: menos de 300 votos", "numa diferença de 2,24 milhões no 1º turno"),
    ]
    y = 0.405
    fig.add_artist(plt.Line2D([x0, 0.955], [y + 0.035, y + 0.035], color=TINTA, linewidth=1.2))
    for a, b in itens:
        t(y, a, size=9.2, weight="bold", va="top")
        t(y - 0.05, b, size=7.6, color=TINTA2, va="top")
        y -= 0.102

    lx, ly = x0, 0.075
    for c, rot in [(LULA, "Lula venceu no 1º turno"), (FLAVIO, "Flávio venceu no 1º turno")]:
        fig.text(lx, ly, "●", family=FONTE, size=9, color=c, va="baseline")
        fig.text(lx + 0.02, ly, rot, family=FONTE, size=7, color=TINTA2, va="baseline")
        lx += 0.2
    fig.text(0.955, 0.03, "matheusgsd.github.io/secoes-2turno-2026", family=DADOS, size=7.4, color=TINTA, ha="right")
    fig.text(0.02, 0.03, "Cada ponto cinza é um local de votação. Círculo: tamanho = eleitores.", family=FONTE,
             size=6, color=TINTA3)

    out = SAIDA / "imagem_x.png"
    fig.savefig(out, dpi=200, facecolor=PAPEL)
    print(out, fig.get_size_inches() * 200)


if __name__ == "__main__":
    main()
