"""GIF (1200 x 675) de um município, versão por versão do cadastro, para o X: o lugar que mais mudou numa atualização.

O mesmo desenho do mapa de "Como a lista encolheu" (um círculo por prédio do 1º turno, do tamanho do número de urnas
dele na lista, anel nas que entram), mais perto, com fundo do OpenStreetMap (tiles de 20_imagem_reescritos.py, em
dados/osm/). Quando o prédio do 2º turno tem coordenada no cadastro, uma seta liga os dois; os destinos sem coordenada
ficam só na lista à direita. A lista de cada versão vem de saida/urnas_mudadas_2026.csv no commit dela (versoes.py).

Uso: python -P scripts/21_gif_municipio.py PA TUCUMÃ 5   (estado, município, quantas versões, das mais recentes)
Saída: saida/gif_<município>.gif
"""
import importlib
import io
import math
import subprocess
import sys
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import VERSOES, ref  # noqa: E402

osm = importlib.import_module("20_imagem_reescritos")
PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#80848c", "#dcdedf"
VOLTA, PREDIO = "#c4923f", "#80848c"
COR = {"saiu do local de cadastro": TINTA, "voltou ao local de cadastro": VOLTA,
       "local de sempre em outro prédio": PREDIO, "trocou de local provisório": TINTA2}
FONTE, DADOS = "Segoe UI", "Consolas"
PASSOS, MS_PASSO, MS_PARADO, MS_PRIMEIRO, MS_ULTIMO = 9, 35, 1300, 2200, 5000
SIGLAS = {"EM", "EE", "EMEF", "EMEI", "EMEIF", "UBS", "CE", "EEEF"}


def nome(s):
    pequenas = {"DE", "DA", "DO", "DAS", "DOS", "E"}
    ps = s.replace(".", " ").split()
    return " ".join(p if p in SIGLAS else p.lower() if i and p in pequenas else p.capitalize() for i, p in enumerate(ps))


def lista_da_versao(commit):
    alvo = ref(commit, "urnas_mudadas_2026.csv")
    dado = (subprocess.run(["git", "show", alvo], cwd=RAIZ, capture_output=True, check=True).stdout if commit
            else (RAIZ / "saida" / alvo).read_bytes())
    return pd.read_csv(io.BytesIO(dado))


def fmt(v):
    return f"{v:,.0f}".replace(",", ".").replace("-", "−")


def main():
    uf, mun, n = sys.argv[1], sys.argv[2].upper(), int(sys.argv[3]) if len(sys.argv) > 3 else 5
    vers = VERSOES[-n:]
    listas = []
    for rot, commit, _ in vers:
        m = lista_da_versao(commit)
        listas.append((rot, len(m), m[(m.SG_UF == uf) & (m.NM_MUNICIPIO == mun)].copy()))
    ultima = listas[-1][2]
    if ultima.empty:
        sys.exit(f"nenhuma urna de {mun} ({uf}) na lista atual")
    nm_mun = nome(mun)

    # prédios do 1º turno e trajetos (1º -> 2º turno) de todas as versões mostradas
    todas = pd.concat([l for _, _, l in listas])
    predios = todas.groupby("NR_LOCAL_VOTACAO").agg(nm=("NM_LOCAL_VOTACAO", "first"), lat=("lat", "first"), lon=("lon", "first"))
    trajetos = (todas.groupby(["NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2"])
                .agg(nm2=("NM_LOCAL_VOTACAO_2", "first"), lat2=("lat_2", "first"), lon2=("lon_2", "first")).reset_index())

    def contagem(l, chave):
        return l.groupby(chave).size().to_dict() if len(l) else {}

    estado = []
    for k, (rot, total, l) in enumerate(listas):
        antes = set(map(tuple, listas[k - 1][2][["NR_ZONA", "NR_SECAO"]].values)) if k else None
        agora = set(map(tuple, l[["NR_ZONA", "NR_SECAO"]].values))
        entrou = {tuple(r) for r in l[["NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO"]].values if k and tuple(r[:2]) not in antes}
        estado.append({"rot": rot, "total": total, "mun": len(l), "predio": contagem(l, "NR_LOCAL_VOTACAO"),
                       "trajeto": contagem(l, ["NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2"]),
                       "anel": {loc for _, _, loc in entrou},
                       "cor": l.groupby("NR_LOCAL_VOTACAO").tipo.agg(lambda s: s.mode()[0]).to_dict() if len(l) else {},
                       "sai": len(antes - agora) if k else 0, "ent": len(entrou)})

    # caixa quadrada (em metros) em volta dos pontos com coordenada, com folga
    pts = list(zip(predios.lat, predios.lon)) + [(a, b) for a, b in zip(trajetos.lat2, trajetos.lon2) if pd.notna(a)]
    la, lo = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
    clat, clon = (la.min() + la.max()) / 2, (lo.min() + lo.max()) / 2
    kx = 111320 * math.cos(math.radians(clat))
    meio = max((la.max() - la.min()) * 111320, (lo.max() - lo.min()) * kx) / 2 * 1.5 + 500
    lat0, lat1 = clat - meio / 111320, clat + meio / 111320
    lon0, lon1 = clon - meio / kx, clon + meio / kx
    z = int(np.clip(round(math.log2(360 / (lon1 - lon0) * 3.5)), 10, 17))
    img, tx0, ty0, caixa = osm.fundo(lat0, lat1, lon0, lon1, z)
    fundo = np.asarray(img)

    def px(lat, lon):
        x, y = osm.tile_xy(lat, lon, z)
        return (x - tx0) * 256 - caixa[0], (y - ty0) * 256 - caixa[1]

    area = lambda u: 26 * u + 20  # noqa: E731
    quadros, tempos = [], []

    def quadro(i, j, t):
        e = t * t * (3 - 2 * t)
        a, b = estado[i], estado[j]
        v = b if t >= .5 else a
        fig = plt.figure(figsize=(8, 4.5), dpi=150, facecolor=PAPEL)
        ax = fig.add_axes([0.02, 0.1, 0.48, 0.85]); ax.set_facecolor(PAPEL)
        ax.imshow(fundo, cmap="gray", vmin=0, vmax=255, alpha=.5, interpolation="lanczos")
        ax.set_xlim(0, fundo.shape[1]); ax.set_ylim(fundo.shape[0], 0); ax.axis("off")
        # setas para os prédios do 2º turno com coordenada
        for r in trajetos.itertuples():
            if pd.isna(r.lat2):
                continue
            q = a["trajeto"].get((r.NR_LOCAL_VOTACAO, r.NR_LOCAL_VOTACAO_2), 0) * (1 - e) + \
                b["trajeto"].get((r.NR_LOCAL_VOTACAO, r.NR_LOCAL_VOTACAO_2), 0) * e
            if q <= 0:
                continue
            p1, p2 = px(*predios.loc[r.NR_LOCAL_VOTACAO, ["lat", "lon"]]), px(r.lat2, r.lon2)
            ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="-|>", color=TINTA, lw=1.1, alpha=min(1, q),
                                                              shrinkA=7, shrinkB=3, mutation_scale=9))
            ax.plot(*p2, "s", ms=5, color=PAPEL, mec=TINTA, mew=1, alpha=min(1, q))
            ax.text(p2[0] + 9, p2[1] + 4, nome(r.nm2), size=6.4, color=TINTA, family=FONTE, va="top", alpha=min(1, q))
        for loc, p in predios.iterrows():
            x, y = px(p.lat, p.lon)
            u = a["predio"].get(loc, 0) * (1 - e) + b["predio"].get(loc, 0) * e
            anel = (loc in a["anel"]) * (1 - e) + (loc in b["anel"]) * e
            cor = COR.get(v["cor"].get(loc) or a["cor"].get(loc) or b["cor"].get(loc), TINTA)
            if anel > 0:
                ax.scatter([x], [y], s=area(u) * 1.9 + 60, facecolors="none", edgecolors=TINTA, linewidths=1.1, alpha=anel)
            if u > 0:
                ax.scatter([x], [y], s=area(u), c=cor, edgecolors=PAPEL, linewidths=.6)
            raio = math.sqrt(area(max(u, a["predio"].get(loc, 0), b["predio"].get(loc, 0)))) / 2  # em pontos
            ax.annotate(nome(p.nm), (x, y), xytext=(raio + 4, 0), textcoords="offset points", va="center", size=6.8,
                        weight="bold", color=TINTA, family=FONTE, alpha=.35 + .65 * (u > 0))

        x0 = .55
        T = lambda y, s, **k: fig.text(x0, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)  # noqa: E731
        dias = sorted({r[0].split(",")[0] for r in vers})
        T(.935, f"2º TURNO · 25/10/2026 · CADASTROS DO TSE DE {' E '.join(dias)}", size=6.6, color=TINTA2, family=DADOS)
        T(.8, f"{nm_mun} ({uf})", size=19, weight="bold", va="bottom")
        T(.735, f"CADASTRO DE {v['rot'].upper()}", size=7.4, color=TINTA2, family=DADOS)
        T(.585, fmt(a["mun"] + (b["mun"] - a["mun"]) * e), size=36, weight="bold")
        T(.565, f"urnas de {nm_mun} mudam de prédio no 2º turno\nno país, {fmt(v['total'])}", size=8.2, color=TINTA2,
          va="top", linespacing=1.4)
        # trajetos da última versão, aparecendo quando entram
        T(.43, "DO 1º TURNO  →  PARA O 2º TURNO", size=6.2, color=TINTA2, family=DADOS)
        y = .385
        for r in trajetos.itertuples():
            q = a["trajeto"].get((r.NR_LOCAL_VOTACAO, r.NR_LOCAL_VOTACAO_2), 0) * (1 - e) + \
                b["trajeto"].get((r.NR_LOCAL_VOTACAO, r.NR_LOCAL_VOTACAO_2), 0) * e
            u = v["trajeto"].get((r.NR_LOCAL_VOTACAO, r.NR_LOCAL_VOTACAO_2), 0)
            T(y, f"{nome(predios.loc[r.NR_LOCAL_VOTACAO, 'nm'])}  →  {nome(r.nm2)}", size=7.2, alpha=.25 + .75 * min(1, q))
            fig.text(.955, y, f"{u} urna{'s' if u != 1 else ''}" if u else "", ha="right", size=7.2, family=DADOS,
                     color=TINTA2)
            y -= .045
        sem = trajetos.lat2.isna().sum()
        lat_fl = ultima.c22.sum() - ultima.c13.sum()
        T(y - .02, (f"No 1º turno, essas urnas deram a {'Flávio' if lat_fl > 0 else 'Lula'} {fmt(abs(lat_fl))} votos de vantagem."
                    + ("\nOs prédios do 2º turno sem seta não têm coordenada no cadastro." if sem else "")),
          size=6.6, color=TINTA2, va="top", linespacing=1.4)
        # linha do tempo das versões mostradas
        tl = fig.add_axes([x0, .075, .4, .06]); tl.set_xlim(-.5, len(vers) - .5); tl.set_ylim(-1, 1); tl.axis("off")
        tl.plot([0, len(vers) - 1], [0, 0], color=LINHA, lw=1.2, zorder=1)
        pos = i + (j - i) * e
        for q in range(len(vers)):
            tl.plot([q], [0], "o", ms=5.5, color=TINTA if q <= round(pos) else LINHA, mec=PAPEL, mew=.8, zorder=2)
            tl.text(q, .6, vers[q][0].split(", ")[1], ha="center", family=DADOS, size=5.6, color=TINTA3)
        tl.plot([pos], [0], "o", ms=9, mfc="none", mec=TINTA, mew=1.2, zorder=3)
        fig.text(.02, .04, "Mapa: © colaboradores do OpenStreetMap. Círculo: prédio do 1º turno, do tamanho do número de urnas.",
                 size=5.8, color=TINTA3, family=FONTE)
        fig.text(.955, .04, "matheusgsd.github.io/secoes-2turno-2026", family=DADOS, size=6.4, color=TINTA, ha="right")
        buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=PAPEL); plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

    k = len(estado)
    for i in range(k):
        quadros.append(quadro(i, i, 0)); tempos.append(MS_PRIMEIRO if i == 0 else MS_ULTIMO if i == k - 1 else MS_PARADO)
        if i < k - 1:
            for p in range(1, PASSOS + 1):
                quadros.append(quadro(i, i + 1, p / (PASSOS + 1))); tempos.append(MS_PASSO)
    amostra = quadros[::max(1, len(quadros) // 6)] + [quadros[-1]]
    mosaico = Image.new("RGB", (amostra[0].width * len(amostra), amostra[0].height))
    for q, im in enumerate(amostra):
        mosaico.paste(im, (q * im.width, 0))
    paleta = mosaico.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    gif = [q.quantize(palette=paleta, dither=Image.Dither.NONE) for q in quadros]
    slug = unicodedata.normalize("NFKD", mun).encode("ascii", "ignore").decode().lower().replace(" ", "_")
    saida = RAIZ / "saida" / f"gif_{slug}.gif"
    gif[0].save(saida, save_all=True, append_images=gif[1:], duration=tempos, loop=0, optimize=True, disposal=1)
    quadros[-1].save(RAIZ / "saida" / f"gif_{slug}_ultimo.png")
    print(saida.name, len(gif), "quadros,", round(sum(tempos) / 1000, 1), "s,", round(saida.stat().st_size / 1e6, 2), "MB | zoom", z)


if __name__ == "__main__":
    main()
