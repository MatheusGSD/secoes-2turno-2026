"""Quais urnas mudam de prédio entre o 1º e o 2º turno, em 2026 e em 2022.

O painel do TSE ("Seções eleitorais alteradas no segundo turno", em Estatísticas > Eleitorado >
Capilaridade) lista 4.864 seções em 2026. Conferimos linha a linha: são as seções cujo local no 2º
turno é diferente do local de CADASTRO (NR_LOCAL_VOTACAO_ORIGINAL), não do local onde votaram no
1º turno. A maioria delas já tinha funcionado no local novo no 1º turno. Para o eleitor, o que importa é
outra comparação: prédio do 1º turno x prédio do 2º turno, que fazemos aqui com o cadastro de locais
do TSE (uma linha por seção e turno).

Unidade: a URNA, isto é, a seção principal (CD_TIPO_SECAO_AGREGADA 1). Seção agregada vota na urna
da principal; seção "distribuída de ofício" (tipo 3, só em 2022) não tem urna e fica de fora. Aptos:
QT_ELEITOR_ELEICAO_FEDERAL da principal em cada turno, que já soma as agregadas e os eleitores com
transferência temporária para aquela urna.

Quando a urna muda de prédio:
- o número do local mudou, a menos que nome E endereço continuem iguais (só renumeração); ou
- o número é o mesmo, mas nome E endereço mudaram (o cadastro trocou o prédio sem trocar o número),
  a menos que dois locais do mesmo município tenham trocado nome e endereço entre si (correção).
Troca só de nome ou só de endereço, com o mesmo número, é correção de cadastro e não conta.

Coordenadas: um ponto só vale se cair dentro do município (malha do IBGE, com folga de ~1 km).
Quando o prédio muda sem mudar o número, a coordenada não é atualizada no cadastro, e a distância
fica desconhecida.

Uso: python -P scripts/02_mudancas.py
Saídas: saida/urnas_2026.csv.gz e saida/urnas_2022.csv.gz (todas as urnas, com a classificação)
        saida/painel_tse_4864.csv (as seções do painel, com o que de fato mudou para o eleitor)
        saida/revisar_distancias.csv (mudanças de mais de 10 km, para conferência)
"""
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ibge  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
ARQ = {
    2026: (RAIZ / "dados/eleitorado_local_votacao_2026.zip", "eleitorado_local_votacao_2026_BRASIL.csv"),
    2022: (RAIZ / "dados/eleitorado_local_votacao_2022.zip", "eleitorado_local_votacao_2022.csv"),
}
COLS = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_TIPO_SECAO_AGREGADA",
        "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO", "NM_BAIRRO",
        "NR_LATITUDE", "NR_LONGITUDE", "QT_ELEITOR_SECAO", "QT_ELEITOR_ELEICAO_FEDERAL",
        "NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL"]
SECAO = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
FOLGA_GRAUS = 0.01  # ~1 km além do limite do município


def ler(ano):
    arquivo, membro = ARQ[ano]
    with zipfile.ZipFile(arquivo) as z, z.open(membro) as f:
        d = pd.read_csv(f, sep=";", encoding="latin1", usecols=COLS, dtype=str)
    d = d[d.SG_UF != "ZZ"].copy()
    for c in ["NR_TURNO", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO",
              "QT_ELEITOR_SECAO", "QT_ELEITOR_ELEICAO_FEDERAL", "NR_LOCAL_VOTACAO_ORIGINAL", "CD_TIPO_SECAO_AGREGADA"]:
        d[c] = pd.to_numeric(d[c])
    for c, n in [("NR_LATITUDE", "lat"), ("NR_LONGITUDE", "lon")]:
        d[n] = pd.to_numeric(d[c].str.replace(",", "."), errors="coerce")
    sem = (d.lat == -1) | (d.lon == -1) | (d.lat == 0) | (d.lon == 0) | d.lat.isna() | d.lon.isna()
    d.loc[sem, ["lat", "lon"]] = np.nan
    print(ano, "seções por tipo:", d[d.NR_TURNO == 1].CD_TIPO_SECAO_AGREGADA.value_counts().sort_index().to_dict())
    return d[d.CD_TIPO_SECAO_AGREGADA != 3]  # distribuída de ofício: sem urna


def km(la1, lo1, la2, lo2):
    p = np.pi / 180
    a = np.sin((la2 - la1) * p / 2) ** 2 + np.cos(la1 * p) * np.cos(la2 * p) * np.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def urnas(d):
    """Uma linha por urna, com o local do 1º e do 2º turno lado a lado."""
    agreg = (d[(d.CD_TIPO_SECAO_AGREGADA == 2) & (d.NR_TURNO == 1)]
             .groupby(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO_PRINCIPAL"]).size()
             .rename_axis(URNA).rename("agregadas"))
    princ = d[d.CD_TIPO_SECAO_AGREGADA == 1].set_index(["NR_TURNO"] + URNA)
    manter = ["NM_MUNICIPIO", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO", "NM_BAIRRO", "lat", "lon",
              "QT_ELEITOR_ELEICAO_FEDERAL", "NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL"]
    t1 = princ.loc[1, manter].rename(columns={"QT_ELEITOR_ELEICAO_FEDERAL": "aptos"})
    t2 = princ.loc[2, manter].rename(columns={"QT_ELEITOR_ELEICAO_FEDERAL": "aptos"}).add_suffix("_2")
    u = t1.join(t2, how="inner").join(agreg).fillna({"agregadas": 0})
    print("urnas:", len(u), "| aptos 1º turno:", int(u.aptos.sum()), "| sem par no outro turno:",
          princ.loc[1].shape[0] - len(u), princ.loc[2].shape[0] - len(u))

    num = u.NR_LOCAL_VOTACAO != u.NR_LOCAL_VOTACAO_2
    nome = u.NM_LOCAL_VOTACAO.map(ibge.norm) != u.NM_LOCAL_VOTACAO_2.map(ibge.norm)
    end = u.DS_ENDERECO.map(ibge.norm) != u.DS_ENDERECO_2.map(ibge.norm)
    renumerada = num & ~nome & ~end
    predio_novo = ~num & nome & end
    # dois locais do mesmo município que trocaram nome e endereço entre si: correção do cadastro
    r = u.reset_index()
    chave1 = r.CD_MUNICIPIO.astype(str) + "|" + r.NM_LOCAL_VOTACAO.map(ibge.norm) + "|" + r.DS_ENDERECO.map(ibge.norm)
    chave2 = r.CD_MUNICIPIO.astype(str) + "|" + r.NM_LOCAL_VOTACAO_2.map(ibge.norm) + "|" + r.DS_ENDERECO_2.map(ibge.norm)
    local1 = dict(zip(chave1, r.NR_LOCAL_VOTACAO))
    destino_de = dict(zip(r.CD_MUNICIPIO.astype(str) + "|" + r.NR_LOCAL_VOTACAO.astype(str), chave2))
    troca = []
    for c1, c2, m, n in zip(chave1, chave2, r.CD_MUNICIPIO, r.NR_LOCAL_VOTACAO):
        outro = local1.get(c2)
        troca.append(outro is not None and outro != n and destino_de.get(f"{m}|{outro}") == c1)
    troca = pd.Series(troca, index=u.index) & predio_novo
    u["criterio"] = np.select([num & ~renumerada, predio_novo & ~troca], ["numero", "predio_novo"], "")
    u["mudou"] = u.criterio != ""
    print("mudou de número:", int(num.sum()), "| só renumerada:", int(renumerada.sum()),
          "| mesmo número, prédio novo:", int(predio_novo.sum()), "| desses, troca entre locais:", int(troca.sum()),
          "| só nome ou só endereço:", int((~num & (nome ^ end)).sum()))

    orig = u.NR_LOCAL_VOTACAO_ORIGINAL
    u["tipo"] = np.select(
        [~u.mudou & (u.NR_LOCAL_VOTACAO_2 == orig), ~u.mudou,
         u.mudou & (u.criterio == "predio_novo") & (u.NR_LOCAL_VOTACAO == orig),
         u.mudou & (u.NR_LOCAL_VOTACAO == orig), u.mudou & (u.NR_LOCAL_VOTACAO_2 == orig)],
        ["igual", "igual, fora do cadastro nos dois turnos", "local de sempre em outro prédio",
         "saiu do local de cadastro", "voltou ao local de cadastro"],
        "trocou de local provisório")
    return u.reset_index()


def validar_coordenadas(u):
    """Anula, nas urnas que mudam, o ponto que cai fora do município (com folga)."""
    m = u[u.mudou]
    cods = dict(zip(zip(m.SG_UF, m.CD_MUNICIPIO), ibge.codigos(m.SG_UF, m.NM_MUNICIPIO)))
    sem_cod = [k for k, v in cods.items() if v is None]
    if sem_cod:
        print("AVISO: municípios sem código IBGE (coordenada não testada):", sem_cod)
    fora = 0
    for uf in sorted(m.SG_UF.unique()):
        geo = ibge.geometrias(uf)
        idx = m.index[m.SG_UF == uf]
        for i in idx:
            g = geo.get(cods.get((uf, u.at[i, "CD_MUNICIPIO"])))
            if g is None:
                continue
            g = shapely.buffer(g, FOLGA_GRAUS)
            for la, lo in [("lat", "lon"), ("lat_2", "lon_2")]:
                if pd.notna(u.at[i, la]) and not g.contains(shapely.Point(u.at[i, lo], u.at[i, la])):
                    u.loc[i, [la, lo]] = np.nan
                    fora += 1
    print("pontos fora do município, anulados:", fora)
    return u


def main():
    revisar = []
    for ano in [2026, 2022]:
        d = ler(ano)
        u = validar_coordenadas(urnas(d))
        u["dist_km"] = km(u.lat, u.lon, u.lat_2, u.lon_2).where(u.mudou, 0.0)
        u.loc[u.criterio == "predio_novo", "dist_km"] = np.nan  # coordenada não atualizada no cadastro
        print(ano, u.groupby("tipo").agg(urnas=("aptos", "size"), aptos=("aptos", "sum")).to_string())
        m = u[u.mudou]
        print(ano, "urnas que mudam:", len(m), "| aptos 1º turno:", int(m.aptos.sum()), "| 2º turno:", int(m.aptos_2.sum()),
              "| agregadas:", int(m.agregadas.sum()), "| municípios:", m.groupby(["SG_UF", "CD_MUNICIPIO"]).ngroups,
              "| UFs:", m.SG_UF.nunique())
        print(ano, "distância (km):", m.dist_km.describe(percentiles=[.25, .5, .75, .9]).round(3).to_dict(),
              "| sem distância:", int(m.dist_km.isna().sum()))
        longe = m[m.dist_km > 10][["SG_UF", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NM_LOCAL_VOTACAO",
                                   "NM_LOCAL_VOTACAO_2", "dist_km"]].assign(ano=ano)
        revisar.append(longe)
        u.to_csv(SAIDA / f"urnas_{ano}.csv.gz", index=False)
        if ano == 2026:
            # as 4.864 do painel: local do 2º turno diferente do de cadastro, por seção (não por urna)
            d["urna"] = d.NR_SECAO_PRINCIPAL.where(d.NR_SECAO_PRINCIPAL > 0, d.NR_SECAO)
            s = d.pivot_table(index=SECAO + ["NM_MUNICIPIO", "urna"], columns="NR_TURNO",
                              values="NR_LOCAL_VOTACAO", aggfunc="first")
            s = s.join(d[d.NR_TURNO == 2].set_index(SECAO)[["NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL"]],
                       on=SECAO)
            p = s[s[2] != s.NR_LOCAL_VOTACAO_ORIGINAL].reset_index()
            mudou = u.set_index(URNA).mudou
            p["mudou_do_1t_para_2t"] = [bool(mudou.get((a, b, c, e), False)) for a, b, c, e in
                                        zip(p.SG_UF, p.CD_MUNICIPIO, p.NR_ZONA, p.urna)]
            p.rename(columns={1: "local_1t", 2: "local_2t"}).to_csv(SAIDA / "painel_tse_4864.csv", index=False)
            print("painel:", len(p), "seções,", p.groupby(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "urna"]).ngroups,
                  "urnas | mudam do 1º para o 2º turno:", int(p.mudou_do_1t_para_2t.sum()))
    pd.concat(revisar).sort_values("dist_km", ascending=False).to_csv(SAIDA / "revisar_distancias.csv", index=False)


if __name__ == "__main__":
    main()
