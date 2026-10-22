"""Cartão para o X (1600 x 900): urnas que não contam porque o cadastro só reescreveu o registro do local.

São as urnas com o mesmo número de local nos dois turnos, o mesmo nome tirando a sigla e o endereço escrito de outro
jeito (tipo "mesmo prédio, nome e endereço reescritos no cadastro", de 02_mudancas.py; em 22/10, 17 urnas em
Tracuateua-PA). À esquerda, os registros do 1º e do 2º turno de cada local; à direita, os locais num mapa com fundo
do OpenStreetMap (tiles baixados uma vez para dados/osm/, com atribuição no cartão).

Uso: python -P scripts/20_imagem_reescritos.py   (depois de 03)
Saída: saida/imagem_reescritos.png
"""
import io
import math
import sys
import time
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import cabecalho  # noqa: E402
SAIDA = RAIZ / "saida"
CACHE = RAIZ / "dados" / "osm"
PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#80848c", "#dcdedf"
DESTAQUE = "#b4451f"
FONTE, DADOS = "Segoe UI", "Consolas"
NOME_REESCRITO = "mesmo prédio, nome e endereço reescritos no cadastro"
ZOOM = 12
TILE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"


def tile_xy(lat, lon, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def tile(z, x, y):
    arq = CACHE / f"{z}_{x}_{y}.png"
    if not arq.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(TILE.format(z=z, x=x, y=y),
                                     headers={"User-Agent": "secoes-2turno-2026 (cartao estatico, github.com/MatheusGSD)"})
        arq.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        time.sleep(0.3)
    return Image.open(io.BytesIO(arq.read_bytes())).convert("RGB")


def fundo(lat0, lat1, lon0, lon1, z):
    """Mosaico de tiles que cobre a caixa, em cinza claro, e a caixa em coordenadas de pixel do mosaico."""
    x0, y0 = tile_xy(lat1, lon0, z)
    x1, y1 = tile_xy(lat0, lon1, z)
    tx, ty = range(int(x0), int(x1) + 1), range(int(y0), int(y1) + 1)
    img = Image.new("RGB", (256 * len(tx), 256 * len(ty)))
    for i, x in enumerate(tx):
        for j, y in enumerate(ty):
            img.paste(tile(z, x, y), (256 * i, 256 * j))
    cinza = ImageOps.grayscale(img)
    # contraste forte (água e mata escuras, estradas e povoados claros), sem ficar preto
    cinza = ImageOps.autocontrast(cinza, cutoff=2).point(lambda v: 55 + v * 170 // 255)
    caixa = ((x0 - tx[0]) * 256, (y0 - ty[0]) * 256, (x1 - tx[0]) * 256, (y1 - ty[0]) * 256)
    return cinza.crop(tuple(round(c) for c in caixa)), tx[0], ty[0], caixa


def diferenca(antes, depois):
    """Marca em 'depois' as palavras que não estavam em 'antes' (sem acento), para destacar."""
    import unicodedata
    tirar = lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()  # noqa: E731
    velhas = set(tirar(antes).split())
    return [(p, tirar(p) not in velhas) for p in depois.split()]


def titulo(s):
    pequenas = {"DE", "DA", "DO", "DAS", "DOS", "E"}
    siglas = {"EMEF", "EMEIF", "EMQEIF", "EMEI"}
    return " ".join(p if p in siglas else p.lower() if i and p in pequenas else p.capitalize()
                    for i, p in enumerate(s.split()))


def main():
    r = pd.read_csv(SAIDA / "urnas_reescritas_2026.csv")
    r = r[r.tipo == NOME_REESCRITO]
    locais = (r.groupby(["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO_2", "DS_ENDERECO", "DS_ENDERECO_2"])
              .agg(lat=("lat", "first"), lon=("lon", "first"), urnas=("NR_SECAO", "size"), aptos=("aptos", "sum"),
                   mun=("NM_MUNICIPIO", "first"), uf=("SG_UF", "first"))
              .reset_index().sort_values("aptos", ascending=False))
    mun = f"{locais.mun.iloc[0].title()} ({locais.uf.iloc[0]})" if locais.mun.nunique() == 1 else "vários municípios"

    fig = plt.figure(figsize=(8, 4.5), dpi=200, facecolor=PAPEL)
    t = lambda x, y, s, **k: fig.text(x, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)  # noqa: E731
    t(0.045, 0.915, f"2º TURNO · 25/10/2026 · {cabecalho()} · CASOS QUE PODEM CONFUNDIR", size=7, color=TINTA2,
      family=DADOS)
    t(0.045, 0.80, "Mudou o nome, não o prédio", size=19, weight="bold")
    t(0.045, 0.735, f"Em {len(r)} urnas de {mun}, o cadastro do TSE trocou a sigla da escola\n"
                    "e a grafia do endereço do 2º turno, mas manteve o número do local.\n"
                    "É o mesmo prédio: essas urnas não entram na conta.",
      size=8.4, color=TINTA2, linespacing=1.4, va="top")

    # registros: os quatro locais com mais eleitores
    y = 0.555
    t(0.045, y, "1º TURNO", size=6.5, color=TINTA3, family=DADOS)
    t(0.30, y, "2º TURNO", size=6.5, color=TINTA3, family=DADOS)
    for row in locais.head(4).itertuples():
        y -= 0.098
        fig.add_artist(plt.Line2D([0.045, 0.545], [y + 0.064, y + 0.064], color=LINHA, lw=0.6))
        t(0.045, y + 0.025, titulo(row.NM_LOCAL_VOTACAO), size=7.6, weight="bold")
        t(0.045, y - 0.012, titulo(row.DS_ENDERECO), size=7, color=TINTA2)
        t(0.275, y + 0.008, "→", size=10, color=TINTA3)
        for linha, (antes, depois, peso, tam, cor0) in enumerate([
                (row.NM_LOCAL_VOTACAO, row.NM_LOCAL_VOTACAO_2, "bold", 7.6, TINTA),
                (row.DS_ENDERECO, row.DS_ENDERECO_2, "normal", 7, TINTA2)]):
            x = 0.30
            for palavra, nova in diferenca(antes, titulo(depois)):
                txt = t(x, y + 0.025 - linha * 0.037, palavra, size=tam, weight="bold" if nova else peso,
                        color=DESTAQUE if nova else cor0)
                bb = txt.get_window_extent(renderer=fig.canvas.get_renderer())
                x += bb.width / fig.bbox.width + 0.0032
        t(0.545, y - 0.012, f"{row.urnas} {'urna' if row.urnas == 1 else 'urnas'}", size=6.5, color=TINTA3,
          family=DADOS, ha="right")
    outros = len(locais) - 4
    if outros > 0:
        t(0.045, y - 0.068, f"E mais {outros} locais do mesmo jeito. Em vermelho, o que mudou no registro.",
          size=7, color=TINTA2)

    # mapa
    folga = 0.025
    lat0, lat1 = locais.lat.min() - folga, locais.lat.max() + folga
    lon0, lon1 = locais.lon.min() - folga, locais.lon.max() + folga
    # caixa com a proporção do painel (largura x altura em polegadas)
    larg, alt = 0.36 * 8, 0.70 * 4.5
    cx, cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    span_lon = max(lon1 - lon0, (lat1 - lat0) * larg / alt)
    span_lat = span_lon * alt / larg
    lon0, lon1, lat0, lat1 = cx - span_lon / 2, cx + span_lon / 2, cy - span_lat / 2, cy + span_lat / 2
    img, tx0, ty0, caixa = fundo(lat0, lat1, lon0, lon1, ZOOM)
    ax = fig.add_axes([0.6, 0.1, 0.36, 0.70])
    ax.imshow(img, extent=(0, img.width, img.height, 0), interpolation="lanczos", cmap="gray", vmin=0, vmax=255)
    for row in locais.itertuples():
        px, py = tile_xy(row.lat, row.lon, ZOOM)
        px, py = (px - tx0) * 256 - caixa[0], (py - ty0) * 256 - caixa[1]
        ax.scatter(px, py, s=30 + row.aptos / 6, facecolor=DESTAQUE, edgecolor="white", linewidth=1.6, zorder=3)
    ax.set_xlim(0, img.width)
    ax.set_ylim(img.height, 0)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(TINTA)
        s.set_linewidth(1)
    t(0.6, 0.83, f"OS {len(locais)} LOCAIS EM {locais.mun.iloc[0].upper()}", size=6.5, color=TINTA3, family=DADOS)
    t(0.96, 0.065, "Mapa: © colaboradores do OpenStreetMap", size=5.5, color=TINTA3, ha="right")
    t(0.6, 0.065, "Tamanho: eleitores", size=5.5, color=TINTA3)

    t(0.045, 0.045, "No mapa da página, filtro “Podem confundir”: matheusgsd.github.io/secoes-2turno-2026",
      size=6.8, weight="bold")
    fig.savefig(SAIDA / "imagem_reescritos.png", facecolor=PAPEL)
    print("saida/imagem_reescritos.png |", len(r), "urnas em", len(locais), "locais")


if __name__ == "__main__":
    main()
