"""Locais de votação com seção trocada e voto no 1º turno: refaz a regressão publicada por David Diniz no X.

A análise original (17/10) usa a lista do painel do TSE de 17/10, que comparava o local do 2º turno com o
local de cadastro, e estima, por local de votação, a probabilidade de o local ter alguma seção trocada em
função dos votos de Lula e de Flávio no 1º turno, em blocos de 10 mil, sem efeito fixo e com efeito fixo de
estado, mesorregião e município. Aqui a mesma conta é feita com três listas:

- painel de 17/10: seções com local do 2º turno diferente do local de cadastro, no cadastro gerado em 17/10
  às 6h28, o mesmo que o painel usava (4.864 seções);
- painel de 18/10: as urnas da lista exportada em 18/10, 7h09 (2º turno diferente do 1º);
- as urnas que mudam de prédio (a lista de 02_mudancas.py).

A unidade é o local de cadastro, o mesmo do arquivo de votação por seção, e, como sensibilidade, o local do
1º turno. Além dos votos em blocos de 10 mil, a regressão é feita com o percentual de Lula nos votos válidos,
controlando o total de votos válidos do local, para separar o voto do tamanho do local. Mínimos quadrados,
erro-padrão agrupado por município.

A unidade vem do cadastro de 17/10, 6h28; as listas de 18/10 e das urnas que mudam de prédio vêm do cadastro atual e entram
pela urna. Os votos ficam no local da urna principal. Uma seção agregada em outro local de cadastro (cerca de mil)
marca o próprio local, sem votos: o efeito na conta é desprezível.

Uso: python -P scripts/09_por_local.py (depois de 01_votos_1t.py e 02_mudancas.py)
Precisa de dados/anteriores/eleitorado_local_votacao_2026_gerado_17out_0932utc.zip (cadastro de 17/10, 6h28)
Saída: saida/por_local.csv
"""
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
CADASTRO_17OUT = RAIZ / "dados/anteriores/eleitorado_local_votacao_2026_gerado_17out_0932utc.zip"
SECAO = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "urna"]
LISTAS = {"painel_17out": "painel de 17/10 (2º turno x cadastro)", "painel_18out": "painel de 18/10 (2º x 1º turno)",
          "mudam_de_predio": "urnas que mudam de prédio"}
UNIDADES = {"NR_LOCAL_VOTACAO_ORIGINAL": "local de cadastro", "NR_LOCAL_VOTACAO": "local do 1º turno"}


def cadastro_17out():
    cols = SECAO + ["NR_TURNO", "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_ORIGINAL",
                    "QT_ELEITOR_ELEICAO_FEDERAL"]
    with zipfile.ZipFile(CADASTRO_17OUT) as z:
        c = pd.concat(pd.read_csv(z.open("eleitorado_local_votacao_2026_BRASIL.csv"), sep=";", encoding="latin1",
                                  dtype=str, usecols=cols, chunksize=1_000_000))
    c = c[c.SG_UF != "ZZ"]
    for x in cols:
        if x not in ("SG_UF", "NR_TURNO"):
            c[x] = pd.to_numeric(c[x])
    s = c[c.NR_TURNO == "1"].merge(c[c.NR_TURNO == "2"][SECAO + ["NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_ORIGINAL"]],
                                   on=SECAO, suffixes=("", "_2"))
    s["urna"] = np.where(s.NR_SECAO_PRINCIPAL > 0, s.NR_SECAO_PRINCIPAL, s.NR_SECAO)
    s["painel_17out"] = s.NR_LOCAL_VOTACAO_2 != s.NR_LOCAL_VOTACAO_ORIGINAL_2
    return s


def ols(d, y, xs, ef):
    """Mínimos quadrados com efeito fixo opcional e erro-padrão agrupado por município."""
    d = d[list(dict.fromkeys([y] + xs + ([ef] if ef else []) + ["CD_MUNICIPIO"]))].dropna()
    Y, X = d[y].values.astype(float), d[xs].values.astype(float)
    if ef:
        Y = Y - d.groupby(ef)[y].transform("mean").values
        X = X - d.groupby(ef)[xs].transform("mean").values
    else:
        X = np.column_stack([np.ones(len(X)), X])
    b = np.linalg.lstsq(X, Y, rcond=None)[0]
    XtXi = np.linalg.inv(X.T @ X)
    S = pd.DataFrame(X * (Y - X @ b)[:, None]).groupby(d.CD_MUNICIPIO.values).sum().values
    n, p = X.shape
    g = d.CD_MUNICIPIO.nunique()
    ep = np.sqrt(np.diag(XtXi @ (S.T @ S) @ XtXi * g / (g - 1) * (n - 1) / (n - p)))
    o = 0 if ef else 1
    return {x: (b[i + o], ep[i + o]) for i, x in enumerate(xs)}


FAIXAS_PAIS = ([0, 30, 45, 60, 75, 101], ["menos de 30%", "30 a 45%", "45 a 60%", "60 a 75%", "75% ou mais"])
FAIXAS_DIF = ([-101, -10, -5, 0, 5, 10, 101], ["−10 ou menos", "−10 a −5", "−5 a 0", "0 a +5", "+5 a +10", "+10 ou mais"])


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - m, c + m


def faixas(loc):
    """Percentual de locais na lista por faixa de voto em Lula: no país, e em relação à média do estado e do
    município (pontos acima ou abaixo do percentual de Lula no lugar). No município, só entram os que têm mais de
    um local, porque num município de local único não há com o que comparar."""
    loc = loc[loc.validos > 0].copy()
    for g in ["SG_UF", "CD_MUNICIPIO"]:
        m = loc.groupby(g)[["c13", "validos"]].transform("sum")
        loc["dif_" + g] = loc.pct_lula - m.c13 / m.validos * 100
    varios = loc.groupby("CD_MUNICIPIO").CD_MUNICIPIO.transform("size") > 1
    linhas = []
    for painel, d, col, (cortes, rotulos) in [("país", loc, "pct_lula", FAIXAS_PAIS),
                                              ("estado", loc, "dif_SG_UF", FAIXAS_DIF),
                                              ("município", loc[varios], "dif_CD_MUNICIPIO", FAIXAS_DIF)]:
        fx = pd.cut(d[col], cortes, labels=rotulos, right=False)
        for lista in LISTAS:
            g = d.groupby(fx, observed=False)[lista].agg(["size", "sum"])
            for ordem, (rot, r) in enumerate(g.iterrows()):
                baixo, alto = wilson(r["sum"], r["size"])
                linhas.append({"lista": LISTAS[lista], "painel": painel, "ordem": ordem, "faixa": rot,
                               "locais": int(r["size"]), "na_lista": int(r["sum"]), "pct": r["sum"] / r["size"] * 100,
                               "ic_baixo": baixo * 100, "ic_alto": alto * 100})
    return pd.DataFrame(linhas)


def main():
    s = cadastro_17out()
    p18 = pd.read_csv(SAIDA / "painel_tse.csv")[URNA].drop_duplicates().assign(painel_18out=True)
    nos = (pd.read_csv(SAIDA / "urnas_mudadas_2026.csv").rename(columns={"NR_SECAO": "urna"})[URNA]
           .assign(mudam_de_predio=True))
    s = s.merge(p18, on=URNA, how="left").merge(nos, on=URNA, how="left")
    s[["painel_18out", "mudam_de_predio"]] = s[["painel_18out", "mudam_de_predio"]].fillna(False).astype(bool)

    v = pd.read_csv(SAIDA / "votos_2026_secao.csv.gz")
    v = v[(v.NR_TURNO == 1) & (v.SG_UF != "ZZ")].rename(columns={"NR_SECAO": "urna"})
    v = v.merge(s[s.NR_SECAO == s.urna][URNA + list(UNIDADES)], on=URNA)

    linhas = []
    for unidade, nome_unidade in UNIDADES.items():
        kl = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", unidade]
        loc = v.groupby(kl)[["c13", "c22", "validos"]].sum().join(
            s.groupby(kl).agg(aptos=("QT_ELEITOR_ELEICAO_FEDERAL", "sum"), **{l: (l, "any") for l in LISTAS}))
        loc = loc.reset_index()
        loc["lula_10mil"], loc["flavio_10mil"] = loc.c13 / 1e4, loc.c22 / 1e4
        loc["pct_lula"] = loc.c13 / loc.validos.replace(0, np.nan) * 100
        loc["validos_mil"] = loc.validos / 1e3
        print(f"\n{nome_unidade}: {len(loc)} locais, mediana de {loc.validos.median():.0f} votos válidos")
        for lista, nome_lista in LISTAS.items():
            loc["y"] = loc[lista].astype(float)
            print(f"  {nome_lista}: {int(loc[lista].sum())} locais trocados ({loc.y.mean() * 100:.2f}%), "
                  f"{loc.loc[loc[lista], 'aptos'].sum():,.0f} eleitores nesses locais")
            for ef, nome_ef in [(None, "nenhum"), ("SG_UF", "estado"), ("CD_MUNICIPIO", "município")]:
                r = ols(loc, "y", ["lula_10mil", "flavio_10mil"], ef)
                q = ols(loc, "y", ["pct_lula", "validos_mil"], ef)
                linhas.append({"unidade": nome_unidade, "lista": nome_lista, "efeito_fixo": nome_ef,
                               "locais": len(loc), "locais_trocados": int(loc[lista].sum()),
                               "eleitores_nos_locais": int(loc.loc[loc[lista], "aptos"].sum()),
                               "lula_10mil": r["lula_10mil"][0], "ep_lula_10mil": r["lula_10mil"][1],
                               "flavio_10mil": r["flavio_10mil"][0], "ep_flavio_10mil": r["flavio_10mil"][1],
                               # efeito de 10 pontos a mais de Lula, em pontos percentuais de chance de troca
                               "lula_10pp": q["pct_lula"][0] * 1000, "ep_lula_10pp": q["pct_lula"][1] * 1000})
                l = linhas[-1]
                print(f"    EF {nome_ef:9s} Lula {l['lula_10mil']:+.4f} ({l['ep_lula_10mil']:.4f})  "
                      f"Flávio {l['flavio_10mil']:+.4f} ({l['ep_flavio_10mil']:.4f})  |  "
                      f"+10 p.p. de Lula: {l['lula_10pp']:+.3f} p.p. ({l['ep_lula_10pp']:.3f})")
        if unidade == "NR_LOCAL_VOTACAO_ORIGINAL":
            fx = faixas(loc)
            fx.to_csv(SAIDA / "por_local_faixas.csv", index=False)
            print("\n  % de locais na lista, por faixa de voto em Lula (urnas que mudam de prédio):")
            for painel, g in fx[fx.lista == LISTAS["mudam_de_predio"]].groupby("painel", sort=False):
                print(f"    {painel:9s} " + "  ".join(f"{r.faixa}: {r.pct:.2f}% ({r.locais})" for r in g.itertuples()))
    pd.DataFrame(linhas).to_csv(SAIDA / "por_local.csv", index=False)

    a = s[s.painel_17out]
    print(f"\npainel de 17/10: {len(a)} seções, {int((a.NR_LOCAL_VOTACAO == a.NR_LOCAL_VOTACAO_2).sum())} "
          f"no mesmo local nos dois turnos")


if __name__ == "__main__":
    main()
