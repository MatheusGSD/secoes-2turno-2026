"""Quais urnas mudam de prédio entre o 1º e o 2º turno, em 2026 e em 2022.

Para o eleitor, o que importa é prédio do 1º turno x prédio do 2º turno, que comparamos aqui com o
cadastro de locais do TSE (uma linha por seção e turno).

O painel do TSE ("Seções eleitorais alteradas no segundo turno", em Estatísticas > Eleitorado >
Capilaridade) mudou de critério. Na atualização de 17/10 (6h28), listava 4.864 seções: as que tinham
local no 2º turno diferente do local de CADASTRO (NR_LOCAL_VOTACAO_ORIGINAL). Na de 18/10 (7h09),
lista 2.033: as que têm local no 2º turno diferente do local do 1º turno, pelo número ou pelo nome.
A lista de 18/10, exportada pelo botão "Gerar arquivos" do painel, está em dados/ e é conferida aqui
seção a seção.

Unidade: a URNA, isto é, a seção principal (CD_TIPO_SECAO_AGREGADA 1). Seção agregada vota na urna
da principal; seção "distribuída de ofício" (tipo 3, só em 2022) não tem urna e fica de fora. Aptos:
QT_ELEITOR_ELEICAO_FEDERAL da principal em cada turno, que já soma as agregadas e os eleitores com
transferência temporária para aquela urna.

Quando a urna muda de prédio:
- o número do local mudou, a menos que nome E endereço continuem iguais (só renumeração); ou
- o número é o mesmo, mas nome E endereço mudaram (o cadastro trocou o prédio sem trocar o número),
  a menos que dois locais do mesmo município tenham trocado nome e endereço entre si (correção).
Troca só de nome ou só de endereço, com o mesmo número, é correção de cadastro e não conta.

Mesmo endereço nos dois turnos: às vezes o número e o nome do local mudam, mas o endereço é idêntico.
- Em 2026, se o local do 2º turno tinha outro endereço em 2022, o cadastro reescreveu o endereço dele
  para o do local do 1º turno (caso de Timóteo-MG: a E.M. Limoeiro "passou" para a Rua Tuia, 101, onde
  fica a E.E. Haydée, para onde as seções tinham ido no 1º turno). A urna quase certamente fica no
  mesmo prédio, e não conta como mudança. Em 2022 não dá para fazer esse teste (faltaria o cadastro de
  2020).
- Nos demais casos (em geral endereço genérico, como "S/N", povoado ou aldeia, com dois prédios
  diferentes), a urna conta, mas fica marcada (mesmo_endereco) para o mapa avisar.

Coordenadas: um ponto só vale se cair dentro do município (malha do IBGE, com folga de ~1 km).
Quando o prédio muda sem mudar o número, a coordenada não é atualizada no cadastro, e a distância
fica desconhecida.

Uso: python -P scripts/02_mudancas.py
Saídas: saida/urnas_2026.csv.gz e saida/urnas_2022.csv.gz (todas as urnas, com a classificação)
        saida/mesmo_predio_2026.csv (urnas retiradas: endereço reescrito no cadastro)
        saida/painel_tse.csv (as seções do painel de 18/10, com a classificação de cada uma aqui)
        saida/revisar_distancias.csv (mudanças de mais de 10 km, para conferência)
"""
import io
import sys
import zipfile
from datetime import datetime, timedelta
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
PAINEL = RAIZ / "dados/painel_secoes_alteradas_2026.csv"  # exportado do painel, atualização de 18/10, 7h09
REESCRITO = "mesmo prédio, endereço reescrito no cadastro"
COLS = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_TIPO_SECAO_AGREGADA",
        "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO", "NM_BAIRRO",
        "NR_LATITUDE", "NR_LONGITUDE", "QT_ELEITOR_SECAO", "QT_ELEITOR_ELEICAO_FEDERAL",
        "NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL"]
SECAO = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
FOLGA_GRAUS = 0.01  # ~1 km além do limite do município
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


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
    return uma_por_secao(d[d.CD_TIPO_SECAO_AGREGADA != 3], ano)  # distribuída de ofício: sem urna


def anterior_2026():
    """O zip da versão anterior do cadastro, em dados/anteriores/ (nome em UTC, como o 00_atualizar.py guarda)."""
    from versoes import VERSOES
    if len(VERSOES) < 2:
        return None
    dia, hora = VERSOES[-2][0].split(", ")
    h, m = (int(x) for x in hora.split("h"))
    g = datetime(2026, int(dia.split("/")[1]), int(dia.split("/")[0]), h, m) + timedelta(hours=3)
    p = RAIZ / f"dados/anteriores/eleitorado_local_votacao_2026_gerado_{g.day:02d}{MESES[g.month - 1]}_{g:%H%M}utc.zip"
    return p if p.exists() else None


def escolha_anterior(ano):
    """O local que ficou para cada seção repetida na versão anterior, do saida/duplicadas_<ano>.csv do commit dela."""
    import subprocess
    from versoes import VERSOES
    if len(VERSOES) < 2 or not VERSOES[-2][1]:
        return None
    out = subprocess.run(["git", "show", f"{VERSOES[-2][1]}:saida/duplicadas_{ano}.csv"], cwd=RAIZ,
                         capture_output=True)
    if out.returncode:
        return None
    a = pd.read_csv(io.BytesIO(out.stdout))
    a = a[a.fica]
    return a.set_index(["NR_TURNO"] + SECAO).NR_LOCAL_VOTACAO


def uma_por_secao(d, ano):
    """Uma linha por seção e turno.

    O cadastro de 20/10, 15h27 trouxe 15 seções duas vezes no 2º turno, cada vez num local (o TSE parecia estar no
    meio de uma mudança). Para não deixar um registro pela metade mexer na lista, fica o local que a seção tinha no
    mesmo turno na versão anterior do cadastro; se não houver, o local do 1º turno; se não, a primeira linha.
    Se a seção já vinha repetida na versão anterior (as mesmas 15 voltaram em 20/10, 20h27), vale o local que ficou
    naquela versão, lido do duplicadas_<ano>.csv do commit dela: sem isso a escolha virava o local do 1º turno e
    11 urnas "saíam" e "entravam" da lista sem que o TSE tivesse mudado nada.
    As repetidas vão para saida/duplicadas_<ano>.csv.
    """
    chave = ["NR_TURNO"] + SECAO
    rep = d.duplicated(chave, keep=False)
    if not rep.any():
        # o de uma versão anterior não vale para esta (no cadastro de 21/10, 6h27, as 15 repetidas sumiram)
        (SAIDA / f"duplicadas_{ano}.csv").unlink(missing_ok=True)
        return d
    r = d[rep].copy()
    ant = anterior_2026() if ano == 2026 else None
    if ant is not None:
        with zipfile.ZipFile(ant) as z, z.open(ARQ[ano][1]) as f:
            a = pd.read_csv(f, sep=";", encoding="latin1", dtype=str, usecols=chave + ["NR_LOCAL_VOTACAO"])
        for c in ["NR_TURNO", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO"]:
            a[c] = pd.to_numeric(a[c])
        a = a.drop_duplicates(chave, keep=False)
        r = r.merge(a.rename(columns={"NR_LOCAL_VOTACAO": "local_anterior"}), on=chave, how="left")
        ja = escolha_anterior(ano)
        if ja is not None:
            r["local_anterior"] = r.local_anterior.fillna(pd.Series(r.set_index(chave).index.map(ja), index=r.index))
    else:
        r["local_anterior"] = np.nan
    t1 = d[(d.NR_TURNO == 1) & ~rep].set_index(SECAO).NR_LOCAL_VOTACAO
    r["local_1t"] = r.set_index(SECAO).index.map(t1)
    r["prioridade"] = np.select([r.NR_LOCAL_VOTACAO == r.local_anterior, r.NR_LOCAL_VOTACAO == r.local_1t],
                                [0, 1], 2)
    r["fica"] = False
    r.loc[r.sort_values("prioridade", kind="stable").drop_duplicates(chave).index, "fica"] = True
    (r.sort_values(chave + ["fica"], ascending=[True] * len(chave) + [False])
     [chave + ["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "local_anterior", "local_1t", "fica"]]
     .to_csv(SAIDA / f"duplicadas_{ano}.csv", index=False))
    fica = r[r.fica]
    print(f"AVISO: {ano}: {fica.shape[0]} seções com mais de uma linha no mesmo turno",
          fica.groupby(["NR_TURNO", "SG_UF"]).size().to_dict(),
          "| ficou o local da versão anterior:", int((fica.prioridade == 0).sum()),
          "| o do 1º turno:", int((fica.prioridade == 1).sum()), "| a primeira linha:", int((fica.prioridade == 2).sum()),
          "| cadastro anterior:", ant.name if ant is not None else "não achado")
    return pd.concat([d[~rep], fica[d.columns]], ignore_index=True)


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


def mesmo_endereco(u, anterior):
    """Marca as mudanças com endereço idêntico nos dois turnos e retira as de endereço reescrito.

    anterior: endereço de cada local (SG_UF, CD_MUNICIPIO, NR_ZONA, NR_LOCAL_VOTACAO) na eleição anterior,
    ou None. Endereço só conta como reescrito se um não contém o outro ("PORTO DO MATO" e "POV. PORTO DO
    MATO" são o mesmo).
    """
    igual = u.mudou & (u.DS_ENDERECO.map(ibge.norm) == u.DS_ENDERECO_2.map(ibge.norm))
    reescrito = pd.Series(False, index=u.index)
    if anterior is not None:
        chaves = zip(u.SG_UF, u.CD_MUNICIPIO, u.NR_ZONA, u.NR_LOCAL_VOTACAO_2)
        antes = [ibge.norm(anterior[k]) if isinstance(anterior.get(k), str) else None for k in chaves]
        reescrito = igual & pd.Series([a is not None and a not in b and b not in a
                                       for a, b in zip(antes, u.DS_ENDERECO_2.map(ibge.norm))], index=u.index)
    u.loc[reescrito, ["mudou", "criterio", "tipo"]] = [False, "", REESCRITO]
    u["mesmo_endereco"] = igual & ~reescrito
    print("mesmo endereço nos dois turnos:", int(igual.sum()), "| retiradas (endereço reescrito):", int(reescrito.sum()),
          int(u[reescrito].aptos.sum()), "aptos | marcadas:", int(u.mesmo_endereco.sum()))
    return u


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
    anterior = None
    for ano in [2022, 2026]:
        d = ler(ano)
        u = validar_coordenadas(mesmo_endereco(urnas(d), anterior))
        if ano == 2022:
            locais = d.drop_duplicates(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO"])
            anterior = dict(zip(zip(locais.SG_UF, locais.CD_MUNICIPIO, locais.NR_ZONA, locais.NR_LOCAL_VOTACAO),
                                locais.DS_ENDERECO))
        else:
            u[u.tipo == REESCRITO][URNA + ["NM_MUNICIPIO", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO",
                                   "NR_LOCAL_VOTACAO_2", "NM_LOCAL_VOTACAO_2", "DS_ENDERECO_2", "aptos"]].to_csv(
                SAIDA / "mesmo_predio_2026.csv", index=False)
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
            conferir_painel(d, u)
    pd.concat(revisar).sort_values("dist_km", ascending=False).to_csv(SAIDA / "revisar_distancias.csv", index=False)


def conferir_painel(d, u):
    """Liga cada seção do painel do TSE ao cadastro e diz como ela foi classificada aqui.

    O painel não traz o código do município nem o número dos locais; a ligação é por UF, nome do
    município (normalizado), zona e seção. O exterior fica de fora, como no resto do levantamento.
    """
    p = pd.read_csv(PAINEL, sep=";", encoding="latin1", dtype=str)
    ext = p[p.sg_uf == "ZZ"]
    p = p[p.sg_uf != "ZZ"].copy()
    p["NR_ZONA"], p["NR_SECAO"] = pd.to_numeric(p.nr_zona), pd.to_numeric(p.nr_secao)
    p["mun"] = p.nm_municipio.map(ibge.norm)
    s = d.pivot_table(index=SECAO + ["NM_MUNICIPIO", "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO_ORIGINAL"],
                      columns="NR_TURNO", values="NR_LOCAL_VOTACAO", aggfunc="first")
    s = s.rename(columns={1: "local_1t", 2: "local_2t"}).reset_index()
    s["mun"] = s.NM_MUNICIPIO.map(ibge.norm)
    s["urna"] = s.NR_SECAO_PRINCIPAL.where(s.NR_SECAO_PRINCIPAL > 0, s.NR_SECAO)
    p = p.merge(s, left_on=["sg_uf", "mun", "NR_ZONA", "NR_SECAO"], right_on=["SG_UF", "mun", "NR_ZONA", "NR_SECAO"],
                how="left")
    if p.CD_MUNICIPIO.isna().any():
        print("AVISO: seções do painel sem par no cadastro:", int(p.CD_MUNICIPIO.isna().sum()))
    c = u.set_index(URNA)
    c = c.assign(nome=c.NM_LOCAL_VOTACAO.map(ibge.norm) != c.NM_LOCAL_VOTACAO_2.map(ibge.norm),
                 end=c.DS_ENDERECO.map(ibge.norm) != c.DS_ENDERECO_2.map(ibge.norm),
                 igual=(c.NR_LOCAL_VOTACAO == c.NR_LOCAL_VOTACAO_2) & (c.NM_LOCAL_VOTACAO == c.NM_LOCAL_VOTACAO_2)
                 & (c.DS_ENDERECO == c.DS_ENDERECO_2))[["mudou", "tipo", "nome", "end", "igual"]]
    p = p.join(c, on=["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "urna"])
    p["mesmo_numero_de_local"] = p.local_1t == p.local_2t
    # por que a urna do painel não conta aqui
    p["fora_daqui"] = np.select(
        [p.mudou, p.tipo == REESCRITO, p.nome & ~p.end, ~p.nome & p.end, ~p.mesmo_numero_de_local & ~p.nome & ~p.end,
         p.igual, p.mesmo_numero_de_local & ~p.nome & ~p.end],
        ["", "endereço reescrito no cadastro", "só o nome do local mudou", "só o endereço mudou", "local só renumerado",
         "mesmo local nos dois turnos no cadastro atual", "só a grafia do nome mudou"], "outro")
    cols = ["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "urna", "nm_local_votacao_inicial",
            "nm_local_votacao_final", "local_1t", "local_2t", "NR_LOCAL_VOTACAO_ORIGINAL", "mesmo_numero_de_local",
            "mudou", "tipo", "fora_daqui"]
    p[cols].rename(columns={"mudou": "muda_de_predio_aqui", "tipo": "tipo_aqui"}).to_csv(SAIDA / "painel_tse.csv", index=False)
    urnas = p.drop_duplicates(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "urna"])
    nossas = int(u.mudou.sum())
    print("painel:", len(p) + len(ext), "seções (", len(ext), "no exterior ) |", len(urnas), "urnas no Brasil",
          "| mesmo número de local nos dois turnos:", int(p.mesmo_numero_de_local.sum()), "seções")
    print("painel x aqui: nas duas listas:", int(urnas.mudou.sum()), "de", nossas, "| só no painel:",
          urnas[~urnas.mudou].fora_daqui.value_counts().to_dict())


if __name__ == "__main__":
    main()
