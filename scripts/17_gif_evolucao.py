"""Cartão animado (GIF, 1200 x 675) da evolução da lista, versão por versão do cadastro, para o X.

O mesmo desenho do mapa da seção "Como a lista encolheu" da página: um círculo por prédio do 1º turno, do tamanho do
número de urnas dele na lista, na cor da situação; tracejado, as que saíram da lista e ficam no prédio do 1º turno;
anel escuro, as que entraram naquela versão. À direita, o número de urnas e o efeito estimado de cada versão. Fundo:
os locais de votação do 2º turno (docs/dados.json), como em 05_imagem_x.py.

Uso: python -P scripts/17_gif_evolucao.py   (depois de 04 e 16)
Saída: saida/evolucao.gif
"""
import io
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import POR_EXTENSO  # noqa: E402

PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#80848c", "#dcdedf"
VOLTA, PREDIO, PONTO, SAIU = "#c4923f", "#80848c", "#b4b8be", "#d6b97c"
COR = {"sai": TINTA, "predio": PREDIO, "volta": VOLTA}
FONTE, DADOS = "Segoe UI", "Consolas"
PASSOS = 9                # quadros de transição entre duas versões
# metade do tempo de antes (70 e 1700) desde 22/10, quando a lista passou de 17 versões e o GIF, de 40 segundos
MS_PASSO, MS_PARADO = 35, 850
MS_PRIMEIRO, MS_ULTIMO = 2200, 4200


def merc(lon, lat):
    lat = np.radians(np.clip(lat, -80, 80))
    return np.asarray(lon), np.degrees(np.log(np.tan(np.pi / 4 + lat / 2)))


def fmt(v):
    return f"{v:,.0f}".replace(",", ".").replace("-", "−")


def sinal(v):
    return ("+" if round(v) > 0 else "") + fmt(v)


def main():
    ev = json.loads((RAIZ / "docs/evolucao.json").read_text(encoding="utf-8"))
    d = json.loads((RAIZ / "docs/dados.json").read_text(encoding="utf-8"))
    V, U = ev["versoes"], ev["urnas"]
    nv = len(V)
    f = np.cumsum(np.array(d["fundo"]).reshape(-1, 2), axis=0) / 1000
    bx, by = merc(f[:, 0], f[:, 1])

    # um círculo por prédio do 1º turno; por versão: urnas na lista, cor dominante, se há saídas, se há entradas
    locais = {}
    for u in U:
        if u["xy"]:
            locais.setdefault((u["uf"], u["mun"], u["local"]), []).append(u)
    L = list(locais.values())
    lx, ly = merc(np.array([us[0]["xy"][0] for us in L]), np.array([us[0]["xy"][1] for us in L]))
    total = np.array([len(us) for us in L])
    na = np.array([[sum(u["s"][i] is not None for u in us) for us in L] for i in range(nv)])
    saiu = np.array([[any(u["s"][i] is None and any(u["s"][:i]) for u in us) for us in L] for i in range(nv)])
    entrou = np.array([[i > 0 and any(u["s"][i] and not u["s"][i - 1] for u in us) for us in L] for i in range(nv)])

    def cor(i, k):
        c = [u["s"][i] for u in L[k] if u["s"][i]]
        return COR[max(set(c), key=c.count)] if c else PAPEL

    area = lambda n: 2.2 * n  # pontos² por urna: a área do círculo é proporcional às urnas
    estado = []
    for i in range(nv):
        estado.append({"cheio": area(na[i]), "tracejado": np.where((na[i] == 0) & saiu[i], area(total) * .4, 0.0),
                       "anel": np.where(entrou[i], area(na[i]) * 1.9 + 30, 0.0),
                       "cor": [cor(i, k) for k in range(len(L))]})

    ordem = np.argsort(-total)
    quadros, tempos = [], []

    def quadro(i, j, t):
        """Versão i indo para a j, t de 0 a 1 (t=0: parado na i)."""
        e = t * t * (3 - 2 * t)
        a, b = estado[i], estado[j]
        mix = lambda k: a[k] + (b[k] - a[k]) * e
        # a cor muda no meio da transição; quem entra já nasce com a cor nova e quem sai some com a antiga
        cores = [(cb if t >= .5 else ca) if PAPEL not in (ca, cb) else (cb if ca == PAPEL else ca) for ca, cb in zip(a["cor"], b["cor"])]
        v = V[j] if t >= .5 else V[i]
        num = V[i]["urnas"] + (V[j]["urnas"] - V[i]["urnas"]) * e

        fig = plt.figure(figsize=(8, 4.5), dpi=150, facecolor=PAPEL)
        ax = fig.add_axes([0.0, 0.03, 0.52, 0.94]); ax.set_facecolor(PAPEL)
        ax.scatter(bx, by, s=.35, c=PONTO, alpha=.55, linewidths=0, rasterized=True)
        tr = mix("tracejado")
        ax.scatter(lx[ordem], ly[ordem], s=tr[ordem], facecolors="none", edgecolors=SAIU, linewidths=.55, linestyles=(0, (2, 1.6)), alpha=.85)
        an = mix("anel")
        ax.scatter(lx[ordem], ly[ordem], s=an[ordem], facecolors="none", edgecolors=TINTA, linewidths=1.0)
        ch = mix("cheio")
        ax.scatter(lx[ordem], ly[ordem], s=ch[ordem], c=np.array(cores)[ordem], edgecolors=PAPEL, linewidths=.4)
        ax.set_aspect("equal"); ax.set_xlim(bx.min() - .4, bx.max() + .4); ax.set_ylim(by.min() - .4, by.max() + .4)
        ax.axis("off")

        x0 = .55
        T = lambda y, s, **k: fig.text(x0, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)
        T(.935, f"2º TURNO · 25/10/2026 · {POR_EXTENSO.get(nv, nv)} VERSÕES DO CADASTRO DO TSE", size=6.6, color=TINTA2, family=DADOS)
        T(.78, "A lista encolheu.\nA conclusão, não.", size=17, weight="bold", va="bottom", linespacing=1.05)
        T(.715, f"CADASTRO DE {v['rot'].upper()}", size=7.4, color=TINTA2, family=DADOS)
        T(.555, fmt(num), size=40, weight="bold")
        k = V.index(v)
        if k:
            sai = sum(1 for u in U if u["s"][k - 1] and not u["s"][k]); ent = sum(1 for u in U if u["s"][k] and not u["s"][k - 1])
            T(.49, f"urnas mudam de prédio no 2º turno\n{fmt(sai)} {'saiu' if sai == 1 else 'saíram'} e {fmt(ent)} {'entrou' if ent == 1 else 'entraram'} na lista", size=8.4, color=TINTA2, va="top", linespacing=1.4)
        else:
            T(.49, "urnas mudam de prédio no 2º turno\nprimeira versão baixada", size=8.4, color=TINTA2, va="top", linespacing=1.4)
        # efeito estimado: a mesma escala em todas as versões
        bx2 = fig.add_axes([x0, .245, .3, .07]); bx2.set_xlim(-120, 120); bx2.set_ylim(-1, 1); bx2.axis("off")
        bx2.axvline(0, color=TINTA3, lw=.8)
        ic = [V[i]["ic"][q] + (V[j]["ic"][q] - V[i]["ic"][q]) * e for q in (0, 1)]
        mg = V[i]["margem"] + (V[j]["margem"] - V[i]["margem"]) * e
        bx2.plot(ic, [0, 0], color=TINTA, lw=2.4, solid_capstyle="butt"); bx2.plot([mg], [0], "o", ms=5, color=TINTA, mec=PAPEL, mew=.8)
        for tk in (-100, 100):
            bx2.text(tk, -.95, sinal(tk), ha="center", va="bottom", family=DADOS, size=6, color=TINTA3)
        T(.335, "EFEITO ESTIMADO NA VANTAGEM DE FLÁVIO", size=6.2, color=TINTA2, family=DADOS)
        T(.2, f"{sinal(v['ic'][0])} a {sinal(v['ic'][1])} votos, numa diferença de 2,24 milhões", size=7.6, color=TINTA2)
        # linha do tempo das versões, com a perdida
        tl = fig.add_axes([x0, .095, .4, .05]); tl.set_xlim(-.5, nv - .5); tl.set_ylim(-1, 1); tl.axis("off")
        tl.plot([0, nv - 1], [0, 0], color=LINHA, lw=1.2, zorder=1)
        pos_atual = i + (j - i) * e
        for q in range(nv):
            tl.plot([q], [0], "o", ms=5.5, color=TINTA if q <= round(pos_atual) else LINHA, mec=PAPEL, mew=.8, zorder=2)
        perd = next((q for q, vv in enumerate(V) if vv["rot"] == ev["perdida_depois_de"]), None)
        if perd is not None and perd < nv - 1:
            tl.plot([perd + .5], [0], "o", ms=4.5, mfc=PAPEL, mec=TINTA3, mew=.8, zorder=2)
            tl.text(perd + .5, -.95, "perdida", ha="center", va="bottom", family=DADOS, size=5.4, color=TINTA3)
        tl.text(0, .55, V[0]["rot"].split(",")[0], ha="center", family=DADOS, size=5.6, color=TINTA3)
        tl.text(nv - 1, .55, V[-1]["rot"].split(",")[0], ha="center", family=DADOS, size=5.6, color=TINTA3)
        tl.plot([pos_atual], [0], "o", ms=9, mfc="none", mec=TINTA, mew=1.2, zorder=3)
        # legenda e assinatura
        lg = [(TINTA, "●", "sai do local de sempre"), (VOLTA, "●", "volta ao local de sempre"),
              (PREDIO, "●", "local de sempre em outro prédio"), (SAIU, "◌", "saiu da lista (fica no prédio do 1º turno)")]
        for xq, (c, m, s) in zip((.03, .165, .315, .495), lg):
            fig.text(xq, .04, m, color=c, size=8, family=FONTE)
            fig.text(xq + .016, .04, s, color=TINTA2, size=6, family=FONTE)
        fig.text(.955, .04, "secoes.dalmolin.dev", family=DADOS, size=6.4, color=TINTA, ha="right")
        buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=PAPEL); plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

    for i in range(nv):
        quadros.append(quadro(i, i, 0)); tempos.append(MS_PRIMEIRO if i == 0 else MS_ULTIMO if i == nv - 1 else MS_PARADO)
        if i < nv - 1:
            for p in range(1, PASSOS + 1):
                quadros.append(quadro(i, i + 1, p / (PASSOS + 1))); tempos.append(MS_PASSO)
    # paleta única para todos os quadros (sem tremido entre eles)
    amostra = [quadros[k] for k in range(0, len(quadros), max(1, len(quadros) // 6))] + [quadros[-1]]
    mosaico = Image.new("RGB", (amostra[0].width * len(amostra), amostra[0].height))
    for k, q in enumerate(amostra):
        mosaico.paste(q, (k * q.width, 0))
    paleta = mosaico.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    gif = [q.quantize(palette=paleta, dither=Image.Dither.NONE) for q in quadros]
    saida = RAIZ / "saida" / "evolucao.gif"
    gif[0].save(saida, save_all=True, append_images=gif[1:], duration=tempos, loop=0, optimize=True, disposal=1)
    print(len(gif), "quadros,", round(sum(tempos) / 1000, 1), "s,", round(saida.stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
