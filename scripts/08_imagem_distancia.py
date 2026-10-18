"""Cartão para o X (1600 x 900): distância entre o prédio do 1º e o do 2º turno.

Usa os mesmos dados da página (docs/dados.json, bloco "distancia", e docs/contornos.json). À esquerda,
os estados pela mediana da distância; à direita, a distribuição por faixa e a ressalva de que é a
distância entre os prédios, não o deslocamento do eleitor.

Uso: python -P scripts/08_imagem_distancia.py   (depois de 04 e 06)
Saída: saida/imagem_distancia.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from matplotlib.transforms import blended_transform_factory

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
PAPEL, TINTA, TINTA2, TINTA3, VAZIO = "#f8f8f6", "#121417", "#4c5058", "#6a6e76", "#e6e7e4"
RAMPA = ["#ebd3a2", "#dbb56f", "#c4923f", "#94661c", "#5a3b0a"]  # as mesmas cores da página (--d1 a --d5)
CLASSES = [(0.3, "menos de 300 m"), (0.45, "300 a 450 m"), (0.6, "450 a 600 m"), (0.9, "600 a 900 m"), (np.inf, "900 m ou mais")]
POUCOS = 5  # trajetos com distância
FONTE, DADOS = "Segoe UI", "Consolas"


def merc(lon, lat):
    lat = np.radians(np.clip(lat, -80, 80))
    return np.asarray(lon), np.degrees(np.log(np.tan(np.pi / 4 + lat / 2)))


def forma(polis):
    """Polígonos [[anel lon, lat, ...]] como um Path do matplotlib (buracos pela regra par-ímpar)."""
    verts, codes = [], []
    for poli in polis:
        for anel in poli:
            x, y = merc(np.array(anel[0::2]), np.array(anel[1::2]))
            verts += list(zip(x, y)) + [(0, 0)]
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(x) - 1) + [MPath.CLOSEPOLY]
    return MPath(verts, codes)


def br(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")


def metros(km):
    return f"{round(km * 100) * 10} m" if km < 1 else f"{br(km)} km"


def main():
    d = json.loads((RAIZ / "docs/dados.json").read_text(encoding="utf-8"))["distancia"]
    contornos = json.loads((RAIZ / "docs/contornos.json").read_text(encoding="utf-8"))["uf"]
    por_uf = {u["uf"]: u for u in d["ufs"]}

    plt.rcParams["hatch.linewidth"] = 0.8
    fig = plt.figure(figsize=(8, 4.5), dpi=200, facecolor=PAPEL)
    ax = fig.add_axes([0.01, 0.17, 0.47, 0.78])
    ax.set_facecolor(PAPEL)
    for uf, polis in contornos.items():
        u = por_uf.get(uf)
        tem = u is not None and u["mediana"] is not None
        cor = RAMPA[next(i for i, (lim, _) in enumerate(CLASSES) if round(u["mediana"], 2) < lim)] if tem else VAZIO
        ax.add_patch(PathPatch(forma(polis), facecolor=cor, edgecolor=PAPEL, linewidth=0.5))
        if tem and u["trajetos"] < POUCOS:
            ax.add_patch(PathPatch(forma(polis), facecolor="none", edgecolor=PAPEL, linewidth=0, hatch="/////"))
    ax.set_xlim(-74.5, -34.2)
    ax.set_ylim(*merc(0, np.array([-34.2, 5.8]))[1])
    ax.set_aspect("equal")
    ax.axis("off")

    # legenda do mapa: cinco classes, hachura e sem dado, em duas linhas de quatro
    itens = [(dict(facecolor=c), rot) for c, (_, rot) in zip(RAMPA, CLASSES)]
    itens += [(dict(facecolor=RAMPA[2], edgecolor=PAPEL, hatch="/////", linewidth=0), "poucos trajetos"),
              (dict(facecolor=VAZIO), "sem dado")]
    for i, (estilo, rot) in enumerate(itens):
        x, y = 0.03 + (i % 4) * 0.115, 0.115 - (i // 4) * 0.04
        fig.patches.append(plt.Rectangle((x, y), 0.018, 0.022, transform=fig.transFigure, **estilo))
        fig.text(x + 0.024, y + 0.004, rot, family=FONTE, size=6.2, color=TINTA2)
    fig.text(0.03, 0.965, "MEDIANA POR ESTADO", family=DADOS, size=6.5, color=TINTA2, va="top")

    x0 = 0.52
    t = lambda y, s, **k: fig.text(x0, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)
    t(0.925, "2º TURNO · 25/10/2026 · CADASTRO DO TSE DE 17/10, 23H37", size=7, color=TINTA2, family=DADOS)
    t(0.80, "Quanto o local de votação\nmuda de lugar", size=17, weight="bold", va="bottom", linespacing=1.05)
    t(0.765, metros(d["mediana"]), size=30, weight="bold", va="top")
    t(0.765, f"\n\n\n\n\n", size=1)
    fig.text(x0 + 0.17, 0.745, "é a mediana: metade dos eleitores vota\nno 2º turno a até cerca dessa distância,\nem linha reta, do prédio do 1º turno",
             family=FONTE, size=7.6, color=TINTA2, va="top", linespacing=1.35)

    # barras por faixa
    total = sum(f["aptos"] for f in d["faixas"])
    vals = [100 * f["aptos"] / total for f in d["faixas"]]
    iMed = next(i for i, f in enumerate(d["faixas"]) if f["med"])
    bx = fig.add_axes([x0 + 0.115, 0.215, 0.29, 0.36])
    bx.set_facecolor(PAPEL)
    ys = np.arange(len(vals))[::-1]
    bx.barh(ys, vals, height=0.62, color=[TINTA if i == iMed else "#8a8f97" for i in range(len(vals))])
    for yv, v, f in zip(ys, vals, d["faixas"]):
        bx.text(v + 0.8, yv, f"{br(v)}%", va="center", family=DADOS, size=6.8, color=TINTA)
        bx.text(-0.03, yv, f["rot"], transform=blended_transform_factory(bx.transAxes, bx.transData), ha="right",
                va="center", family=FONTE, size=6.8, color=TINTA2)
    bx.set_xlim(0, max(vals) * 1.22)
    bx.set_ylim(-0.6, len(vals) - 0.4)
    bx.axis("off")
    t(0.6, "% DOS ELEITORES POR FAIXA DE DISTÂNCIA", size=6.5, color=TINTA2, family=DADOS)

    t(0.15, f"{br(d['menos_1km'], 0)}% a menos de 1 km · {br(d['de_5km'])}% a 5 km ou mais", size=8, weight="bold")
    t(0.105, "É a distância entre os prédios, não o deslocamento de cada eleitor:\no endereço do eleitor não é público.",
      size=6.8, color=TINTA2, va="top", linespacing=1.3)
    fig.text(0.955, 0.03, "matheusgsd.github.io/secoes-2turno-2026", family=DADOS, size=7.4, color=TINTA, ha="right")
    fig.text(0.03, 0.03, f"{d['urnas_com']:,} urnas com coordenada confiável nos dois prédios; {d['urnas_sem']} ficam sem distância.".replace(",", "."),
             family=FONTE, size=6, color=TINTA3)

    out = SAIDA / "imagem_distancia.png"
    fig.savefig(out, dpi=200, facecolor=PAPEL)
    print(out, fig.get_size_inches() * 200)


if __name__ == "__main__":
    main()
