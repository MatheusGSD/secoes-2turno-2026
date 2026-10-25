"""Cartão para o X (1600 x 900): o que mudou na última versão do cadastro, prédio por prédio.

Lê as urnas que saíram e entraram em saida/versoes_<atual>.csv (07_versoes.py) e os votos delas no 1º turno na lista
da versão anterior (saida/urnas_mudadas_2026.csv no commit dela, versoes.py). Feito para o cadastro de 25/10, 6h28, em
que só saíram urnas; as que entram aparecem na mesma tabela, com o prédio do 2º turno.

Uso: python -P scripts/23_imagem_hoje.py   (depois de 07)
Saída: saida/imagem_hoje.png
"""
import io
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import VERSOES  # noqa: E402

SAIDA = RAIZ / "saida"
PAPEL, TINTA, TINTA2, TINTA3, LINHA = "#f8f8f6", "#121417", "#4c5058", "#80848c", "#dcdedf"
LULA, FLAVIO = "#c8423b", "#2f5fa7"
FONTE, DADOS = "Segoe UI", "Consolas"


def fmt(v):
    return f"{v:,.0f}".replace(",", ".").replace("-", "−")


def titulo(s):
    minusculas = {"DE", "DO", "DA", "DOS", "DAS", "À", "E"}
    siglas = {"APAE", "CMEI", "EMEF", "UBS"}
    ps = [p if p in siglas else p.lower() if i and p in minusculas else p.capitalize() for i, p in enumerate(s.split())]
    return " ".join(ps).replace("(vila", "(Vila").replace("(anexo", "(anexo")


def quebra(s):
    """Nome longo em duas linhas, no parêntese."""
    return s.replace(" (", "\n(", 1) if len(s) > 40 else s


def main():
    rot, _, arq = VERSOES[-1]
    rot_ant, commit_ant, _ = VERSOES[-2]
    v = pd.read_csv(SAIDA / arq)
    sairam = v[v.situacao == "saiu da lista"]
    cols = [c for c in v.columns if c.startswith("NM_LOCAL_VOTACAO_") and not c.startswith("NM_LOCAL_VOTACAO_2_")]
    col_1t, col_2t = cols[0], [c for c in v.columns if c.startswith("NM_LOCAL_VOTACAO_2_")][0]
    ant = pd.read_csv(io.BytesIO(subprocess.run(["git", "show", f"{commit_ant}:saida/urnas_mudadas_2026.csv"], cwd=RAIZ,
                                                capture_output=True, check=True).stdout))
    chave = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    s = sairam.merge(ant[chave + ["c13", "c22", "aptos"]], on=chave, how="left")
    grupos = (s.groupby(["NM_MUNICIPIO_" + col_1t.removeprefix("NM_LOCAL_VOTACAO_"), "SG_UF", col_1t, col_2t])
              .agg(urnas=("NR_SECAO", "size"), aptos=("aptos", "sum"), lula=("c13", "sum"), flavio=("c22", "sum"))
              .reset_index().sort_values("urnas", ascending=False))
    mun = grupos.iloc[0, 0]
    uf = grupos.iloc[0, 1]
    n_ant = len(ant)
    n_atual = n_ant - len(sairam) + int((v.situacao == "entrou na lista").sum())
    print(grupos.to_string(), n_ant, n_atual)

    fig = plt.figure(figsize=(8, 4.5), dpi=200, facecolor=PAPEL)
    t = lambda x, y, s, **k: fig.text(x, y, s, family=k.pop("family", FONTE), color=k.pop("color", TINTA), **k)  # noqa: E731
    t(0.045, 0.915, f"2º TURNO · 25/10/2026 · O QUE MUDOU NO CADASTRO DO TSE DE {rot.upper()}", size=7, color=TINTA2, family=DADOS)
    t(0.045, 0.80, f"Hoje cedo, a troca de prédio foi cancelada em {titulo(mun)} ({uf})", size=16, weight="bold")
    t(0.045, 0.735, f"As {len(sairam)} urnas tinham entrado na lista no cadastro de 24/10, 15h28. No de hoje, o local do 2º turno voltou a ser\n"
                    f"o mesmo do 1º: quem vota nelas vai ao mesmo prédio do dia 4. A lista foi de {fmt(n_ant)} para {fmt(n_atual)} urnas.",
      size=8.2, color=TINTA2, linespacing=1.4, va="top")

    # tabela: prédio do 1º turno → prédio cancelado
    y0 = 0.56
    t(0.045, y0 + 0.045, "URNAS", size=6.5, color=TINTA2, family=DADOS)
    t(0.12, y0 + 0.045, "VOTAM NO MESMO PRÉDIO DO DIA 4", size=6.5, color=TINTA2, family=DADOS)
    t(0.58, y0 + 0.045, "IAM PARA (CANCELADO)", size=6.5, color=TINTA2, family=DADOS)
    t(0.80, y0 + 0.045, "1º TURNO: LULA × FLÁVIO", size=6.5, color=TINTA2, family=DADOS)
    for i, g in enumerate(grupos.itertuples(index=False)):
        y = y0 - 0.14 * i
        fig.add_artist(plt.Line2D([0.045, 0.955], [y + 0.03, y + 0.03], color=LINHA, lw=0.6, transform=fig.transFigure))
        t(0.045, y - 0.03, str(g.urnas), size=22, weight="bold", family=DADOS)
        nome = quebra(titulo(getattr(g, col_1t)))
        t(0.12, y + 0.012, nome, size=8.6, weight="bold", va="top", linespacing=1.3)
        t(0.12, y - 0.025 - 0.035 * nome.count("\n"), f"{fmt(g.aptos)} eleitores aptos", size=7, color=TINTA2, va="top")
        destino = titulo(getattr(g, col_2t))
        txt = t(0.58, y - 0.02, destino, size=8.6, color=TINTA3, va="center")
        fig.canvas.draw()
        bb = txt.get_window_extent().transformed(fig.transFigure.inverted())
        meio = (bb.y0 + bb.y1) / 2
        fig.add_artist(plt.Line2D([bb.x0, bb.x1], [meio, meio], color=TINTA3, lw=1.1, transform=fig.transFigure))
        t(0.80, y - 0.02, fmt(g.lula), size=10, color=LULA, weight="bold", va="center", family=DADOS)
        t(0.855, y - 0.02, "×", size=9, color=TINTA2, va="center")
        t(0.875, y - 0.02, fmt(g.flavio), size=10, color=FLAVIO, weight="bold", va="center", family=DADOS)
    yb = y0 - 0.14 * len(grupos) + 0.03
    fig.add_artist(plt.Line2D([0.045, 0.955], [yb, yb], color=LINHA, lw=0.6, transform=fig.transFigure))

    tot_l, tot_f = int(s.c13.sum()), int(s.c22.sum())
    t(0.045, 0.215, f"No 1º turno, essas urnas deram a Flávio {fmt(tot_f - tot_l)} votos de vantagem. O efeito estimado da troca de prédio no país",
      size=8.2, color=TINTA2)
    t(0.045, 0.17, "segue perto de zero: −2 votos (de −14 a +9), numa diferença de 2,24 milhões no 1º turno.", size=8.2, color=TINTA2)
    t(0.045, 0.03, "Na dúvida, confira o seu local no e-Título.", size=7.4, color=TINTA2)
    fig.text(0.955, 0.03, "matheusgsd.github.io/secoes-2turno-2026", family=DADOS, size=7.4, color=TINTA, ha="right")
    out = SAIDA / "imagem_hoje.png"
    fig.savefig(out, dpi=200, facecolor=PAPEL)
    print(out)


if __name__ == "__main__":
    main()
