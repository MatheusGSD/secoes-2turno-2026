"""Quais urnas mudaram de local entre o 1º e o 2º turno, em 2026 e em 2022.

O painel do TSE ("Seções eleitorais alteradas no segundo turno", em Estatísticas > Eleitorado >
Capilaridade) lista 4.864 seções em 2026. Conferimos linha a linha: são as seções cujo local no 2º
turno é diferente do local de CADASTRO (NR_LOCAL_VOTACAO_ORIGINAL), não do local onde votaram no
1º turno. A maioria delas já tinha votado no local novo no 1º turno. Para o eleitor, o que importa é
outra comparação: local do 1º turno x local do 2º turno, que fazemos aqui com o cadastro de locais
do TSE (uma linha por seção e turno).

A unidade é a URNA: seção agregada vota na urna da principal, então os aptos dela vão para a
principal, e a urna "mudou" quando o local da principal mudou. Troca só de nome (mesmo número de
local, mesma coordenada) não conta como mudança: são correções de grafia.

Uso: python -P scripts/02_mudancas.py
Saídas: saida/urnas_2026.csv.gz e saida/urnas_2022.csv.gz (todas as urnas, com a classificação)
        saida/painel_tse_4864.csv (as seções do painel, com o que de fato mudou para o eleitor)
"""
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
ARQ = {
    2026: (RAIZ / "dados/eleitorado_local_votacao_2026.zip", "eleitorado_local_votacao_2026_BRASIL.csv"),
    2022: (RAIZ / "dados/eleitorado_local_votacao_2022.zip", "eleitorado_local_votacao_2022.csv"),
}
COLS = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_TIPO_SECAO_AGREGADA",
        "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO", "NM_BAIRRO",
        "NR_LATITUDE", "NR_LONGITUDE", "QT_ELEITOR_SECAO", "NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL"]
SECAO = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]


def ler(ano):
    arquivo, membro = ARQ[ano]
    with zipfile.ZipFile(arquivo) as z, z.open(membro) as f:
        d = pd.read_csv(f, sep=";", encoding="latin1", usecols=COLS, dtype=str)
    d = d[d.SG_UF != "ZZ"].copy()
    for c in ["NR_TURNO", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO",
              "QT_ELEITOR_SECAO", "NR_LOCAL_VOTACAO_ORIGINAL"]:
        d[c] = pd.to_numeric(d[c])
    for c, n in [("NR_LATITUDE", "lat"), ("NR_LONGITUDE", "lon")]:
        d[n] = pd.to_numeric(d[c].str.replace(",", "."), errors="coerce")
    sem = (d.lat == -1) | (d.lon == -1) | (d.lat == 0) | d.lat.isna()
    d.loc[sem, ["lat", "lon"]] = np.nan
    d["urna"] = d.NR_SECAO_PRINCIPAL.where(d.NR_SECAO_PRINCIPAL > 0, d.NR_SECAO)
    return d


def km(la1, lo1, la2, lo2):
    p = np.pi / 180
    a = np.sin((la2 - la1) * p / 2) ** 2 + np.cos(la1 * p) * np.cos(la2 * p) * np.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def urnas(d):
    """Uma linha por urna, com o local do 1º e do 2º turno lado a lado."""
    aptos = d.groupby(["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "urna"]).QT_ELEITOR_SECAO.sum()
    princ = d[d.NR_SECAO == d.urna].set_index(["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "urna"])
    princ = princ.join(aptos.rename("aptos"))
    manter = ["NM_MUNICIPIO", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO", "NM_BAIRRO", "lat", "lon",
              "aptos", "NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL"]
    t1 = princ.loc[1, manter]
    t2 = princ.loc[2, manter].add_suffix("_2")
    u = t1.join(t2, how="inner")
    u["mudou"] = u.NR_LOCAL_VOTACAO != u.NR_LOCAL_VOTACAO_2
    u["dist_km"] = km(u.lat, u.lon, u.lat_2, u.lon_2).where(u.mudou, 0.0)
    # dentro do mesmo município, mais de 50 km é coordenada errada no cadastro (ex.: Verdelândia-MG, 220 km)
    u.loc[u.dist_km > 50, "dist_km"] = np.nan
    orig = u.NR_LOCAL_VOTACAO_ORIGINAL
    u["tipo"] = np.select(
        [~u.mudou & (u.NR_LOCAL_VOTACAO == orig), ~u.mudou,
         u.mudou & (u.NR_LOCAL_VOTACAO == orig), u.mudou & (u.NR_LOCAL_VOTACAO_2 == orig)],
        ["igual", "igual, fora do cadastro nos dois turnos", "saiu do local de cadastro", "voltou ao local de cadastro"],
        "trocou de local provisório")
    u = u.reset_index().rename(columns={"urna": "NR_SECAO"})
    print("urnas:", len(u), "| aptos:", int(u.aptos.sum()), "| sem par no outro turno:",
          princ.loc[1].shape[0] - len(u), princ.loc[2].shape[0] - len(u))
    return u


def main():
    for ano in [2026, 2022]:
        d = ler(ano)
        u = urnas(d)
        print(ano, u.groupby("tipo").agg(urnas=("aptos", "size"), aptos=("aptos", "sum")).to_string())
        m = u[u.mudou]
        print(ano, "distância (km) das que mudaram:", m.dist_km.describe(percentiles=[.25, .5, .75, .9]).round(2).to_dict(),
              "| sem coordenada:", int(m.dist_km.isna().sum()))
        u.to_csv(SAIDA / f"urnas_{ano}.csv.gz", index=False)
        if ano == 2026:
            # as 4.864 do painel: local do 2º turno diferente do de cadastro, por seção (não por urna)
            s = d.pivot_table(index=SECAO + ["NM_MUNICIPIO", "urna"], columns="NR_TURNO",
                              values="NR_LOCAL_VOTACAO", aggfunc="first")
            s = s.join(d[d.NR_TURNO == 2].set_index(SECAO)[["NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL"]],
                       on=SECAO)
            p = s[s[2] != s.NR_LOCAL_VOTACAO_ORIGINAL].reset_index()
            p["mudou_do_1t_para_2t"] = p[1] != p[2]
            p.rename(columns={1: "local_1t", 2: "local_2t"}).to_csv(SAIDA / "painel_tse_4864.csv", index=False)
            print("painel:", len(p), "seções | mudaram do 1º para o 2º turno:", int(p.mudou_do_1t_para_2t.sum()))


if __name__ == "__main__":
    main()
