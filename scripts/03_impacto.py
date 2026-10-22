"""Impacto das mudanças de local no 2º turno de 2026, a partir do voto no 1º turno.

1. Quanto a troca de prédio mexe na abstenção? Medimos em 2022, quando 1.506 urnas trocaram de
   prédio entre os turnos. Para cada urna, a variação da abstenção do 1º para o 2º turno (em pontos)
   menos a variação média das urnas que NÃO mudaram na mesma comparação (o efeito do turno em si,
   igual para todos ali). Comparação principal: urnas do mesmo município e da mesma zona eleitoral.
   Sensibilidade: só a mesma zona (que pode juntar vários municípios) e o mesmo local de cadastro (com a zona: o
   número do local se repete entre zonas do mesmo município, em prédios diferentes).
   Média ponderada pelos aptos; intervalo de 95% por 2.000 sorteios dos grupos de comparação.
   É uma comparação observacional: urnas que mudam já tinham abstenção maior no 1º turno (parte
   delas tinha sido deslocada), e parte da variação pode ser volta ao normal.
2. Quem votou nessas urnas em 2026? Votos do 1º turno nas urnas que trocam de prédio, vencedor de
   cada uma e peso na margem nacional e de cada estado. Para ver se as mudanças pegam urnas de um
   lado, comparamos o % de Lula de cada uma com o das urnas que não mudam da mesma comparação.
3. Quanto isso pode mexer na margem? Eleitores a mais ou a menos = aptos x efeito de 2022 do mesmo
   tipo de mudança (volta ao local de sempre, ou sai dele); quem deixa de votar se divide como os
   votos daquela urna no 1º turno. O intervalo sorteia os grupos de 2022 uma vez para os dois tipos
   ao mesmo tempo (bootstrap conjunto): é o intervalo do efeito médio, que supõe o mesmo efeito em todas as urnas
   do tipo. A faixa de previsão sorteia, para cada urna de 2026, o efeito de uma urna de 2022 do mesmo tipo, e assim
   inclui a variação de uma urna para outra. É uma conta de ordem de grandeza, não uma previsão.

Uso: python -P scripts/03_impacto.py
Saídas: saida/impacto_2022.csv, saida/urnas_mudadas_2026.csv, saida/urnas_reescritas_2026.csv, saida/impacto_uf_2026.csv, saida/numeros.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
BASES = {
    "zona_municipio": ["SG_UF", "CD_MUNICIPIO", "NR_ZONA"],
    "zona": ["SG_UF", "NR_ZONA"],
    "local_cadastro": ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO_ORIGINAL"],
}
PRINCIPAL = "zona_municipio"
REESCRITO = "mesmo prédio, endereço reescrito no cadastro"  # de 02_mudancas.py: não conta como mudança
NOME_REESCRITO = "mesmo prédio, nome e endereço reescritos no cadastro"  # idem
GRUPO = {"voltou ao local de cadastro": "volta", "saiu do local de cadastro": "sai",
         "local de sempre em outro prédio": "sai", "trocou de local provisório": "sai"}
FAIXAS = [0, 0.3, 0.6, 1.2, np.inf]
ROTULOS = ["até 300 m", "300 a 600 m", "600 m a 1,2 km", "mais de 1,2 km"]
SORTEIOS = 2000
NORDESTE = {"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"}
rng = np.random.default_rng(2026)


def faixa(dist):
    f = pd.cut(dist, FAIXAS, labels=ROTULOS, right=False).astype(object)
    return f.where(dist.notna(), "sem distância")


def urnas_com_voto(ano):
    u = pd.read_csv(SAIDA / f"urnas_{ano}.csv.gz")
    v = pd.read_csv(SAIDA / f"votos_{ano}_secao.csv.gz")
    v = v.pivot_table(index=URNA, columns="NR_TURNO",
                      values=[c for c in v.columns if c not in URNA + ["NR_TURNO"]], aggfunc="sum")
    v.columns = [f"{a}_t{b}" for a, b in v.columns]
    u = u.merge(v, left_on=URNA, right_index=True, how="inner")
    u["grupo"] = u.tipo.map(GRUPO)
    u["faixa"] = faixa(u.dist_km)
    return u


def com_base(u, base, coluna, peso):
    """Junta a cada urna a média ponderada de `coluna` nas urnas que não mudaram do mesmo grupo."""
    g = (u[~u.mudou].assign(p=lambda d: d[coluna] * d[peso]).groupby(base)[["p", peso]].sum()
           .pipe(lambda x: (x.p / x[peso]).rename("base")))
    return u.join(g, on=base)


def media(d, col, peso):
    return np.average(d[col], weights=d[peso]) if len(d) else np.nan


def bootstrap(m, base, col, peso, grupos):
    """Médias por grupo (e o total) em cada sorteio dos grupos de comparação, com os mesmos sorteios para todos."""
    m = m.assign(cl=m.groupby(base).ngroup())
    n = m.cl.max() + 1
    num = {g: np.bincount(m.cl[m.grupo == g], (m[col] * m[peso])[m.grupo == g], n) for g in grupos}
    den = {g: np.bincount(m.cl[m.grupo == g], m[peso][m.grupo == g], n) for g in grupos}
    tot_n, tot_d = np.bincount(m.cl, m[col] * m[peso], n), np.bincount(m.cl, m[peso], n)
    w = rng.multinomial(n, np.full(n, 1 / n), size=SORTEIOS)
    saida = {g: (w @ num[g]) / (w @ den[g]) for g in grupos}
    saida["todas"] = (w @ tot_n) / (w @ tot_d)
    return saida


def efeito_2022():
    u = urnas_com_voto(2022)
    u = u[(u.aptos > 0) & (u.aptos_2 > 0)].copy()
    u["abst1"] = 100 * (1 - u.comparecimento_t1 / u.aptos)
    u["abst2"] = 100 * (1 - u.comparecimento_t2 / u.aptos_2)
    u["delta"] = u.abst2 - u.abst1
    u = u[u.delta.between(-60, 60)]
    print("2022: urnas que mudaram, com votos nos dois turnos:", int(u.mudou.sum()))
    res, sens, draws, efs = [], {}, {}, {}
    for nome, base in BASES.items():
        b = com_base(u, base, "delta", "aptos")
        m = b[b.mudou & b.base.notna()].assign(ef=lambda d: d.delta - d.base)
        bs = bootstrap(m, base, "ef", "aptos", ["volta", "sai"])
        draws[nome] = bs
        nivel = com_base(u, base, "abst1", "aptos")
        nivel = nivel[nivel.mudou & nivel.base.notna()]
        sens[nome] = {"efeito_pp": media(m, "ef", "aptos"), "ic_baixo": np.percentile(bs["todas"], 2.5),
                      "ic_alto": np.percentile(bs["todas"], 97.5), "urnas": len(m),
                      "abst1_acima_pp": media(nivel.assign(d=nivel.abst1 - nivel.base), "d", "aptos"),
                      **{f"{g}_pp": media(m[m.grupo == g], "ef", "aptos") for g in ["volta", "sai"]},
                      **{f"{g}_ic": list(np.percentile(bs[g], [2.5, 97.5])) for g in ["volta", "sai"]}}
        if nome != PRINCIPAL:
            continue
        efs = {g: m[m.grupo == g].ef.to_numpy() for g in ["volta", "sai"]}
        linhas = [("todas", m)] + [(g, m[m.grupo == g]) for g in ["sai", "volta"]] + \
                 [(f, m[m.faixa == f]) for f in ROTULOS + ["sem distância"]]
        for rot, d in linhas:
            if rot in ("todas", "sai", "volta"):
                lo, hi = np.percentile(bs[rot], [2.5, 97.5])
            else:
                bsf = bootstrap(d.assign(grupo="x"), base, "ef", "aptos", [])["todas"]
                lo, hi = np.nanpercentile(bsf, [2.5, 97.5])
            res.append((rot, media(d, "ef", "aptos"), lo, hi, len(d), int(d.aptos.sum())))
    res = pd.DataFrame(res, columns=["grupo", "efeito_pp", "ic_baixo", "ic_alto", "urnas", "aptos"])
    res.to_csv(SAIDA / "impacto_2022.csv", index=False)
    print(res.round(2).to_string(index=False))
    print(json.dumps({k: {a: (round(b, 2) if isinstance(b, float) else b) for a, b in v.items()}
                      for k, v in sens.items()}, indent=1, default=str))
    return res, sens, draws, efs


def votos_2026():
    u = urnas_com_voto(2026)
    for c in [c for c in u.columns if c.endswith("_t1")]:
        u[c[:-3]] = u[c]
    u["outros"] = u.validos - u.c13 - u.c22
    u["abst"] = 100 * (1 - u.comparecimento / u.aptos)
    u["pct_lula"] = 100 * u.c13 / u.validos
    u["pct_flavio"] = 100 * u.c22 / u.validos
    u["vencedor"] = np.where(u.c13 > u.c22, "Lula", np.where(u.c22 > u.c13, "Flávio", "empate"))
    # votos de margem (Flávio - Lula) que mudam por +1 ponto de abstenção em cada urna
    u["margem_por_pp"] = u.aptos_2 / 100 * (u.c13 - u.c22) / u.comparecimento
    return u


def previsao(m, efs):
    """Faixa de 95% da margem quando cada urna de 2026 recebe o efeito de uma urna de 2022 do mesmo tipo, sorteada."""
    r = np.random.default_rng(25)  # gerador próprio: não mexe nos sorteios das outras contas
    tot = np.zeros(SORTEIOS)
    for g, ef in efs.items():
        a = m[m.grupo == g].margem_por_pp.to_numpy()
        if len(a):
            tot += r.choice(ef, size=(SORTEIOS, len(a))) @ a
    return list(np.percentile(tot, [2.5, 97.5]))


def aplicar(m, draws, sens):
    """Efeito na margem (Flávio - Lula, em votos) e eleitores a mais, por base de comparação."""
    a = m.groupby("grupo").margem_por_pp.sum()
    e = (m.aptos_2 / 100).groupby(m.grupo).sum()
    out = {}
    for nome, bs in draws.items():
        marg = sum(bs[g] * a.get(g, 0) for g in ["volta", "sai"])
        elei = -sum(bs[g] * e.get(g, 0) for g in ["volta", "sai"])
        cen = sum(sens[nome][f"{g}_pp"] * a.get(g, 0) for g in ["volta", "sai"])
        cen_e = -sum(sens[nome][f"{g}_pp"] * e.get(g, 0) for g in ["volta", "sai"])
        out[nome] = {"margem": cen, "margem_ic": list(np.percentile(marg, [2.5, 97.5])),
                     "eleitores_a_mais": cen_e, "eleitores_ic": list(np.percentile(elei, [2.5, 97.5]))}
    print("efeito na margem (Flávio - Lula):", json.dumps(out, default=lambda x: round(float(x), 1)))
    return out


def voto_vs_vizinhas(u):
    b = com_base(u.assign(pl=u.pct_lula), BASES[PRINCIPAL], "pl", "validos")
    m = b[b.mudou & b.base.notna()].assign(dif=lambda d: d.pl - d.base)
    bs = bootstrap(m.assign(grupo="x"), BASES[PRINCIPAL], "dif", "validos", [])["todas"]
    nivel = com_base(u, BASES[PRINCIPAL], "abst", "aptos")
    nivel = nivel[nivel.mudou & nivel.base.notna()]
    r = {"dif_pp": media(m, "dif", "validos"), "ic_baixo": np.percentile(bs, 2.5), "ic_alto": np.percentile(bs, 97.5),
         "pct_acima": 100 * (m.dif > 0).mean(), "urnas": len(m),
         "abst_acima_pp": media(nivel.assign(d=nivel.abst - nivel.base), "d", "aptos")}
    print("voto de Lula nas urnas que mudam, menos o das vizinhas:", {k: round(float(v), 2) for k, v in r.items()})
    return r


def main():
    res, sens, draws, efs = efeito_2022()
    u = votos_2026()
    m = u[u.mudou].copy()
    impacto = aplicar(m, draws, sens)
    impacto[PRINCIPAL]["margem_previsao"] = previsao(m, efs)
    print("faixa de previsão da margem:", np.round(impacto[PRINCIPAL]["margem_previsao"], 1))
    ef = sens[PRINCIPAL]
    m["ef"] = m.grupo.map({g: ef[f"{g}_pp"] for g in ["volta", "sai"]})
    m["efeito_margem"] = m.ef * m.margem_por_pp
    cols = (URNA + ["NM_MUNICIPIO", "tipo", "grupo", "criterio", "dist_km", "faixa", "NR_LOCAL_VOTACAO",
                    "NM_LOCAL_VOTACAO", "DS_ENDERECO", "NM_BAIRRO", "lat", "lon", "NR_LOCAL_VOTACAO_2",
                    "NM_LOCAL_VOTACAO_2", "DS_ENDERECO_2", "NM_BAIRRO_2", "lat_2", "lon_2", "NR_LOCAL_VOTACAO_ORIGINAL",
                    "NM_LOCAL_VOTACAO_ORIGINAL", "agregadas", "aptos", "aptos_2", "comparecimento", "abst", "validos",
                    "c13", "c22", "outros", "brancos", "nulos", "pct_lula", "pct_flavio", "vencedor", "ef",
                    "efeito_margem", "mesmo_endereco", "nome_parecido"])
    m[cols].to_csv(SAIDA / "urnas_mudadas_2026.csv", index=False)
    # as que não contam porque o cadastro reescreveu o registro: o mapa as mostra à parte
    u[u.tipo.isin([REESCRITO, NOME_REESCRITO])][[c for c in cols if c in u.columns]].to_csv(
        SAIDA / "urnas_reescritas_2026.csv", index=False)

    nac = u[["c13", "c22", "validos", "comparecimento", "aptos"]].sum()
    mm = m[["c13", "c22", "outros", "validos", "comparecimento", "aptos", "aptos_2"]].sum()
    por_uf = u.groupby("SG_UF")[["c13", "c22", "validos"]].sum()
    muf = m.groupby("SG_UF").agg(urnas=("aptos", "size"), aptos=("aptos", "sum"), c13=("c13", "sum"),
                                 c22=("c22", "sum"), validos=("validos", "sum"),
                                 urnas_lula=("vencedor", lambda s: int((s == "Lula").sum())),
                                 urnas_flavio=("vencedor", lambda s: int((s == "Flávio").sum())),
                                 efeito=("efeito_margem", "sum"))
    muf = muf.join(por_uf.add_suffix("_uf")).sort_values("aptos", ascending=False)
    muf.to_csv(SAIDA / "impacto_uf_2026.csv")
    print(muf[["urnas", "aptos", "urnas_lula", "urnas_flavio", "efeito"]].round(1).to_string())

    teto = mm.c13 - mm.c22
    pessimista = mm.aptos_2 * 0.05 * teto / mm.comparecimento
    tipos = m.groupby("tipo").agg(urnas=("aptos", "size"), aptos=("aptos", "sum"), c13=("c13", "sum"),
                                  c22=("c22", "sum"), validos=("validos", "sum"))
    p = pd.read_csv(SAIDA / "painel_tse.csv").drop_duplicates(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "urna"])
    # urnas que votam no 2º turno fora do local de cadastro (critério do painel de 17/10): referência de quem faltou no 1º
    fc = u[u.tipo.isin(["igual, fora do cadastro nos dois turnos", "saiu do local de cadastro",
                        "trocou de local provisório"])]
    ja_fora = fc.tipo == "igual, fora do cadastro nos dois turnos"
    n = {
        "nacional": {"lula": int(nac.c13), "flavio": int(nac.c22), "validos": int(nac.validos),
                     "comparecimento": int(nac.comparecimento), "aptos": int(nac.aptos),
                     "pct_lula": 100 * nac.c13 / nac.validos, "pct_flavio": 100 * nac.c22 / nac.validos,
                     "margem_votos": int(nac.c22 - nac.c13), "abst": 100 * (1 - nac.comparecimento / nac.aptos),
                     "urnas": len(u)},
        "mudadas": {"urnas": len(m), "aptos": int(mm.aptos), "aptos_2": int(mm.aptos_2),
                    "comparecimento": int(mm.comparecimento), "validos": int(mm.validos), "lula": int(mm.c13),
                    "flavio": int(mm.c22), "outros": int(mm.outros),
                    "pct_lula": 100 * mm.c13 / mm.validos, "pct_flavio": 100 * mm.c22 / mm.validos,
                    "abst": 100 * (1 - mm.comparecimento / mm.aptos), "margem_votos": int(mm.c22 - mm.c13),
                    "pct_validos_pais": 100 * mm.validos / nac.validos,
                    "pct_urnas_pais": 100 * len(m) / len(u),
                    "urnas_lula": int((m.vencedor == "Lula").sum()), "urnas_flavio": int((m.vencedor == "Flávio").sum()),
                    "urnas_empate": int((m.vencedor == "empate").sum()),
                    "municipios": int(m.groupby(["SG_UF", "CD_MUNICIPIO"]).ngroups), "ufs": int(m.SG_UF.nunique()),
                    "agregadas": int(m.agregadas.sum()),
                    "dist_mediana_km": float(m.dist_km.median()), "dist_p90_km": float(m.dist_km.quantile(0.9)),
                    "com_distancia": int(m.dist_km.notna().sum()), "sem_distancia": int(m.dist_km.isna().sum()),
                    "predio_novo_mesmo_numero": int((m.criterio == "predio_novo").sum()),
                    "mesmo_endereco_urnas": int(m.mesmo_endereco.sum()),
                    "mesmo_endereco_aptos": int(m[m.mesmo_endereco].aptos.sum()),
                    "reescritas_urnas": int((u.tipo == REESCRITO).sum()),
                    "reescritas_aptos": int(u[u.tipo == REESCRITO].aptos.sum()),
                    "nome_reescrito_urnas": int((u.tipo == NOME_REESCRITO).sum()),
                    "nome_reescrito_aptos": int(u[u.tipo == NOME_REESCRITO].aptos.sum()),
                    "nome_parecido_urnas": int(m.nome_parecido.sum()),
                    "pct_aptos_nordeste": 100 * m[m.SG_UF.isin(NORDESTE)].aptos.sum() / mm.aptos,
                    "pct_volta": 100 * (m.grupo == "volta").mean(),
                    "teto_votos": int(teto), "teto_pct_margem": 100 * teto / (nac.c22 - nac.c13),
                    "pessimista_votos": float(pessimista), "pessimista_pct_margem": 100 * pessimista / (nac.c22 - nac.c13)},
        "impacto": impacto, "principal": PRINCIPAL,
        "tipos": tipos.assign(pct_lula=100 * tipos.c13 / tipos.validos).reset_index().to_dict("records"),
        "efeito_2022": res.to_dict("records"), "sensibilidade_2022": sens,
        "voto_vs_vizinhas": voto_vs_vizinhas(u),
        "painel_tse": {"urnas": len(p), "nas_duas_listas": int(p.muda_de_predio_aqui.sum()),
                       "so_no_painel": p[~p.muda_de_predio_aqui].fora_daqui.value_counts().to_dict()},
        "fora_do_cadastro_2t": {"urnas": len(fc), "aptos": int(fc.aptos.sum()),
                                "faltaram_1t": int((fc.aptos - fc.comparecimento).sum()),
                                "abst": 100 * (1 - fc.comparecimento.sum() / fc.aptos.sum()),
                                "ja_fora_no_1t_urnas": int(ja_fora.sum()),
                                "ja_fora_no_1t_abst": 100 * (1 - fc[ja_fora].comparecimento.sum() / fc[ja_fora].aptos.sum())},
    }
    print(json.dumps({k: n[k] for k in ["nacional", "mudadas", "painel_tse"]}, indent=1, ensure_ascii=False, default=float))
    print(tipos.assign(pct_lula=100 * tipos.c13 / tipos.validos).round(1).to_string())
    (SAIDA / "numeros.json").write_text(json.dumps(n, indent=1, ensure_ascii=False, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
