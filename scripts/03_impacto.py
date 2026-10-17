"""Impacto das mudanças de local no 2º turno de 2026, a partir do voto no 1º turno.

1. Quanto a troca de local mexe na abstenção? Medimos em 2022, que teve 1.384 urnas trocando de
   local entre os turnos. Para cada urna, a variação da abstenção do 1º para o 2º turno (em pontos)
   menos a variação média das urnas que NÃO mudaram na mesma zona eleitoral (o efeito do turno em
   si, igual para todos ali). Média ponderada pelos aptos; intervalo de 95% por 2.000 sorteios das
   zonas com reposição.
2. Quem votou nessas urnas em 2026? Votos do 1º turno nas 2.053 urnas que trocam de local,
   vencedor de cada uma e peso na margem nacional e de cada estado. Para ver se as mudanças
   escolhem urnas de um lado, comparamos o % de Lula de cada uma com o das urnas que não mudam na
   mesma zona (mesmo sorteio de zonas para o intervalo).
3. Quanto isso pode mexer na margem? Eleitores a menos = aptos x efeito medido em 2022; supomos que
   quem deixa de votar se divide como os votos válidos daquela urna no 1º turno. É uma conta de
   ordem de grandeza, não uma previsão.

Uso: python -P scripts/03_impacto.py
Saídas: saida/impacto_2022.csv, saida/urnas_mudadas_2026.csv, saida/impacto_uf_2026.csv, saida/numeros.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
ZONA = ["SG_UF", "NR_ZONA"]
FAIXAS = [0, 0.3, 0.6, 1.2, np.inf]
ROTULOS = ["até 300 m", "300 a 600 m", "600 m a 1,2 km", "mais de 1,2 km"]
SORTEIOS = 2000
rng = np.random.default_rng(2026)


def faixa(dist):
    f = pd.cut(dist, FAIXAS, labels=ROTULOS, right=False).astype(object)
    return f.where(dist.notna(), "sem coordenada")


def efeito_2022():
    u = pd.read_csv(SAIDA / "urnas_2022.csv.gz")
    v = pd.read_csv(SAIDA / "votos_2022_secao.csv.gz", usecols=["NR_TURNO"] + URNA + ["comparecimento"])
    v = v.pivot_table(index=URNA, columns="NR_TURNO", values="comparecimento").add_prefix("comp")
    u = u.merge(v, left_on=URNA, right_index=True, how="inner")
    u = u[(u.aptos > 0) & (u.aptos_2 > 0)]
    u["delta"] = 100 * ((1 - u.comp2 / u.aptos_2) - (1 - u.comp1 / u.aptos))  # pontos de abstenção
    u = u[u.delta.between(-60, 60)]  # descarta urna com aptos inconsistentes
    base = (u[~u.mudou].assign(p=lambda d: d.delta * d.aptos).groupby(ZONA)[["p", "aptos"]].sum()
              .pipe(lambda g: (g.p / g.aptos).rename("base")))
    u = u.join(base, on=ZONA)
    u["efeito"] = u.delta - u.base
    u["faixa"] = faixa(u.dist_km)
    m = u[u.mudou & u.base.notna()].copy()
    print("2022: urnas que mudaram com comparação na zona:", len(m), "de", int(u.mudou.sum()))

    zonas = m.groupby(ZONA)
    blocos = {k: g for k, g in zonas}
    chaves = list(blocos)

    def media(g):
        return np.average(g.efeito, weights=g.aptos)

    def ic(filtro):
        sub = {k: g[filtro(g)] for k, g in blocos.items()}
        sub = {k: g for k, g in sub.items() if len(g)}
        ks = list(sub)
        if not ks:
            return np.nan, np.nan, np.nan, 0, 0
        est = media(pd.concat(sub.values()))
        bs = []
        for _ in range(SORTEIOS):
            amostra = rng.choice(len(ks), len(ks), replace=True)
            bs.append(media(pd.concat([sub[ks[i]] for i in amostra])))
        n = sum(len(g) for g in sub.values())
        return est, *np.percentile(bs, [2.5, 97.5]), n, int(sum(g.aptos.sum() for g in sub.values()))

    linhas = [("todas", *ic(lambda g: g.index == g.index))]
    for t in ["saiu do local de cadastro", "voltou ao local de cadastro", "trocou de local provisório"]:
        linhas.append((t, *ic(lambda g, t=t: g.tipo == t)))
    for f in ROTULOS + ["sem coordenada"]:
        linhas.append((f, *ic(lambda g, f=f: g.faixa == f)))
    res = pd.DataFrame(linhas, columns=["grupo", "efeito_pp", "ic_baixo", "ic_alto", "urnas", "aptos"])
    res.to_csv(SAIDA / "impacto_2022.csv", index=False)
    print(res.round(2).to_string(index=False))
    # placebo: as urnas que não mudaram, sorteadas, têm efeito zero por construção; conferimos a variação geral
    print("variação média da abstenção 1º->2º turno em 2022 (urnas sem mudança):",
          round(np.average(u[~u.mudou].delta, weights=u[~u.mudou].aptos), 2), "pontos")
    _ = chaves
    return res


def votos_2026(res):
    u = pd.read_csv(SAIDA / "urnas_2026.csv.gz")
    v = pd.read_csv(SAIDA / "votos_2026_secao.csv.gz")
    v = v[v.NR_TURNO == 1].drop(columns="NR_TURNO")
    u = u.merge(v, on=URNA, how="left", validate="one_to_one")
    print("2026: urnas sem voto no 1º turno:", int(u.comparecimento.isna().sum()))
    u = u[u.comparecimento.notna()].copy()
    u["outros"] = u.validos - u.c13 - u.c22
    u["abst"] = 100 * (1 - u.comparecimento / u.aptos)
    u["pct_lula"] = 100 * u.c13 / u.validos
    u["pct_flavio"] = 100 * u.c22 / u.validos
    u["vencedor"] = np.where(u.c13 > u.c22, "Lula", np.where(u.c22 > u.c13, "Flávio", "empate"))
    u["faixa"] = faixa(u.dist_km)

    ef = res.set_index("grupo")
    m = u[u.mudou].copy()
    # efeito por faixa de distância (é o que mais separa em 2022); IC da própria faixa
    m["ef"] = m.faixa.map(ef.efeito_pp)
    m["ef_lo"] = m.faixa.map(ef.ic_baixo)
    m["ef_hi"] = m.faixa.map(ef.ic_alto)
    for s in ["", "_lo", "_hi"]:
        perdidos = m.aptos * m[f"ef{s}"] / 100
        # eleitores a menos (efeito positivo) tiram votos de cada lado na proporção dos válidos da urna
        m[f"perde_lula{s}"] = perdidos * m.c13 / m.comparecimento
        m[f"perde_flavio{s}"] = perdidos * m.c22 / m.comparecimento
        m[f"efeito_margem{s}"] = m[f"perde_lula{s}"] - m[f"perde_flavio{s}"]  # >0 = ajuda Flávio
    cols = (URNA + ["NM_MUNICIPIO", "tipo", "dist_km", "faixa", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO",
                    "NM_BAIRRO", "lat", "lon", "NR_LOCAL_VOTACAO_2", "NM_LOCAL_VOTACAO_2", "DS_ENDERECO_2", "NM_BAIRRO_2",
                    "lat_2", "lon_2", "NR_LOCAL_VOTACAO_ORIGINAL", "NM_LOCAL_VOTACAO_ORIGINAL", "aptos",
                    "comparecimento", "abst", "validos", "c13", "c22", "outros", "brancos", "nulos", "pct_lula",
                    "pct_flavio", "vencedor", "ef", "perde_lula", "perde_flavio", "efeito_margem",
                    "efeito_margem_lo", "efeito_margem_hi"])
    m[cols].to_csv(SAIDA / "urnas_mudadas_2026.csv", index=False)
    return u, m


def voto_vs_zona(u):
    """As urnas que mudam votam diferente das que não mudam na mesma zona? (% de Lula nos válidos)"""
    base = (u[~u.mudou].assign(p=lambda d: d.c13, v=lambda d: d.validos).groupby(ZONA)[["p", "v"]].sum()
              .pipe(lambda g: (100 * g.p / g.v).rename("base")))
    m = u[u.mudou].join(base, on=ZONA).dropna(subset=["base"])
    m["dif"] = m.pct_lula - m.base
    blocos = [g for _, g in m.groupby(ZONA)]
    est = np.average(m.dif, weights=m.validos)
    bs = []
    for _ in range(SORTEIOS):
        g = pd.concat([blocos[i] for i in rng.choice(len(blocos), len(blocos), replace=True)])
        bs.append(np.average(g.dif, weights=g.validos))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    r = {"dif_pp": est, "ic_baixo": lo, "ic_alto": hi, "pct_acima": 100 * (m.dif > 0).mean(), "urnas": len(m)}
    print("voto de Lula nas urnas que mudam, menos o das vizinhas da zona:", {k: round(v, 2) for k, v in r.items()})
    return r


def resumo(u, m, res):
    nac = u[["c13", "c22", "validos", "comparecimento", "aptos"]].sum()
    mm = m[["c13", "c22", "outros", "validos", "comparecimento", "aptos", "brancos", "nulos"]].sum()
    resto = u[~u.mudou][["c13", "c22", "validos", "comparecimento", "aptos"]].sum()
    por_uf = u.groupby("SG_UF")[["c13", "c22", "validos"]].sum()
    muf = m.groupby("SG_UF").agg(urnas=("aptos", "size"), aptos=("aptos", "sum"), c13=("c13", "sum"),
                                 c22=("c22", "sum"), validos=("validos", "sum"),
                                 urnas_lula=("vencedor", lambda s: int((s == "Lula").sum())),
                                 urnas_flavio=("vencedor", lambda s: int((s == "Flávio").sum())),
                                 efeito=("efeito_margem", "sum"), efeito_lo=("efeito_margem_lo", "sum"),
                                 efeito_hi=("efeito_margem_hi", "sum"))
    muf = muf.join(por_uf.add_suffix("_uf"))
    muf["margem_uf_votos"] = muf.c22_uf - muf.c13_uf  # >0 = Flávio à frente
    muf["margem_urnas_votos"] = muf.c22 - muf.c13
    muf["pct_lula_urnas"] = 100 * muf.c13 / muf.validos
    muf["pct_lula_uf"] = 100 * muf.c13_uf / muf.validos_uf
    muf["efeito_sobre_margem_uf_pct"] = 100 * muf.efeito.abs() / muf.margem_uf_votos.abs()
    muf = muf.sort_values("aptos", ascending=False)
    muf.to_csv(SAIDA / "impacto_uf_2026.csv")
    print(muf[["urnas", "aptos", "pct_lula_urnas", "pct_lula_uf", "urnas_lula", "urnas_flavio",
               "margem_urnas_votos", "efeito", "margem_uf_votos"]].round(1).to_string())

    tipos = m.groupby("tipo").agg(urnas=("aptos", "size"), aptos=("aptos", "sum"), c13=("c13", "sum"),
                                  c22=("c22", "sum"), validos=("validos", "sum"))
    faixas = m.groupby("faixa").agg(urnas=("aptos", "size"), aptos=("aptos", "sum"))
    n = {
        "nacional": {"lula": int(nac.c13), "flavio": int(nac.c22), "validos": int(nac.validos),
                     "pct_lula": 100 * nac.c13 / nac.validos, "pct_flavio": 100 * nac.c22 / nac.validos,
                     "margem_votos": int(nac.c22 - nac.c13),
                     "abst": 100 * (1 - nac.comparecimento / nac.aptos)},
        "mudadas": {"urnas": len(m), "aptos": int(mm.aptos), "comparecimento": int(mm.comparecimento),
                    "validos": int(mm.validos), "lula": int(mm.c13), "flavio": int(mm.c22), "outros": int(mm.outros),
                    "pct_lula": 100 * mm.c13 / mm.validos, "pct_flavio": 100 * mm.c22 / mm.validos,
                    "abst": 100 * (1 - mm.comparecimento / mm.aptos),
                    "margem_votos": int(mm.c22 - mm.c13),
                    "urnas_lula": int((m.vencedor == "Lula").sum()), "urnas_flavio": int((m.vencedor == "Flávio").sum()),
                    "urnas_empate": int((m.vencedor == "empate").sum()),
                    "municipios": int(m.groupby(["SG_UF", "CD_MUNICIPIO"]).ngroups), "ufs": int(m.SG_UF.nunique()),
                    "dist_mediana_km": float(m.dist_km.median()), "sem_coord": int(m.dist_km.isna().sum()),
                    "efeito_margem": float(m.efeito_margem.sum()), "efeito_margem_lo": float(m.efeito_margem_lo.sum()),
                    "efeito_margem_hi": float(m.efeito_margem_hi.sum()),
                    "eleitores_a_menos": float((m.aptos * m.ef / 100).sum())},
        "resto": {"pct_lula": 100 * resto.c13 / resto.validos, "abst": 100 * (1 - resto.comparecimento / resto.aptos)},
        "tipos": tipos.assign(pct_lula=100 * tipos.c13 / tipos.validos).reset_index().to_dict("records"),
        "faixas": faixas.reset_index().to_dict("records"),
        "efeito_2022": res.to_dict("records"),
        "voto_vs_zona": voto_vs_zona(u),
        "painel_tse": {"secoes": 4864, "mudaram_1t_2t": int(pd.read_csv(SAIDA / "painel_tse_4864.csv").mudou_do_1t_para_2t.sum())},
    }
    print(json.dumps({k: n[k] for k in ["nacional", "mudadas", "resto"]}, indent=1, ensure_ascii=False, default=float))
    print(tipos.assign(pct_lula=100 * tipos.c13 / tipos.validos).round(1).to_string())
    (SAIDA / "numeros.json").write_text(json.dumps(n, indent=1, ensure_ascii=False, default=float), encoding="utf-8")


def main():
    res = efeito_2022()
    u, m = votos_2026(res)
    resumo(u, m, res)


if __name__ == "__main__":
    main()
