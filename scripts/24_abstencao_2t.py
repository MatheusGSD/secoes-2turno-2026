"""Depois do 2º turno de 2026: as urnas que mudaram de prédio tiveram mais abstenção?

O resultado por seção do TSE (detalhe da votação por seção, com aptos e comparecimento de cada turno, e votação por
seção, com os votos do 2º turno) permite medir o que 03_impacto.py só podia estimar com 2022.
1. Conferência: o local de votação de cada seção em cada turno no resultado, comparado com o do cadastro final.
2. Efeito: o mesmo desenho de 2022. Para cada urna da lista, a variação da abstenção do 1º para o 2º turno (em pontos)
   menos a variação média das urnas do mesmo município e da mesma zona que não mudaram. Ficam fora da comparação as
   urnas que estiveram na lista em alguma versão do cadastro e as que o cadastro reescreveu: se a lista confundiu o
   eleitor, elas não são vizinhas limpas. Média ponderada pelos aptos do 1º turno; intervalo de 95% por 2.000 sorteios
   dos grupos de comparação (município e zona). Por tipo de mudança, distância, endereço genérico, bairro, data em que
   a urna entrou na lista e região. Com poucos grupos de comparação (coluna "grupos"), o intervalo não é confiável.
3. Testes de controle: o mesmo cálculo em urnas que não mudaram de prédio e deveriam dar perto de zero (as reescritas
   no cadastro, as que estiveram na lista e saíram, as que votaram fora do local de sempre nos dois turnos).
4. Distância: inclinação por km e as faixas de 2022 e 2026 juntas. As urnas sem coordenada confiável nos dois prédios
   ficam sem distância (02_mudancas.py). Tentamos completar pelo endereço no OpenStreetMap, mas o ponto da rua erra
   justamente as distâncias longas (2,6 km entre dois blocos do mesmo campus da UFU), e a tentativa ficou de fora.
5. No resultado: quem deixou de votar a mais (ou a menos) divide-se como os votos da própria urna no 2º turno.
   Comparamos com o que 03_impacto.py e 13_abstencao_1t.py estimaram antes da eleição.
É uma comparação entre urnas, não um experimento.

Uso: python -P scripts/24_abstencao_2t.py   (depois de 02, 03 e 13; lê dados/detalhe_votacao_secao_2026.zip e
     dados/votacao_secao_2026_BR.zip, os dois com o 2º turno, e o histórico da lista no git, por versoes.py)
Saídas: saida/abstencao_2t.json, saida/abstencao_2t.csv (efeito por grupo), saida/abstencao_2t_urnas.csv (as urnas da
        lista, com a abstenção nos dois turnos e o efeito), saida/abstencao_2t_municipios.csv,
        saida/turnos_2026_secao.csv.gz (o que foi lido dos arquivos do TSE, para não reler)
"""
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA, DADOS = RAIZ / "saida", RAIZ / "dados"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import VERSOES  # noqa: E402

DETALHE = (DADOS / "detalhe_votacao_secao_2026.zip", "detalhe_votacao_secao_2026_BR.csv")
VOTACAO = (DADOS / "votacao_secao_2026_BR.zip", "votacao_secao_2026_BR.csv")
CACHE = SAIDA / "turnos_2026_secao.csv.gz"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
BASES = {"zona_municipio": ["SG_UF", "CD_MUNICIPIO", "NR_ZONA"], "zona": ["SG_UF", "NR_ZONA"],
         "local_cadastro": ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO_ORIGINAL"]}
B = BASES["zona_municipio"]
GRUPO = {"voltou ao local de cadastro": "volta", "saiu do local de cadastro": "sai",
         "local de sempre em outro prédio": "sai", "trocou de local provisório": "sai"}
REESCRITAS = ["mesmo prédio, endereço reescrito no cadastro", "mesmo prédio, nome e endereço reescritos no cadastro"]
FAIXAS = [0, 0.3, 0.6, 1.2, np.inf]
ROTULOS = ["até 300 m", "300 a 600 m", "600 m a 1,2 km", "mais de 1,2 km"]
REGIAO = {**dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
          **dict.fromkeys(["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "Norte"),
          **dict.fromkeys(["DF", "GO", "MS", "MT"], "Centro-Oeste"),
          **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"), **dict.fromkeys(["PR", "RS", "SC"], "Sul")}
ENTRADA = {"17/10": "17/10", "18/10": "18 e 19/10", "19/10": "18 e 19/10", "20/10": "20 e 21/10",
           "21/10": "20 e 21/10", "22/10": "22 e 23/10", "23/10": "22 e 23/10", "24/10": "24 e 25/10",
           "25/10": "24 e 25/10"}
SORTEIOS = 2000
rng = np.random.default_rng(2026)


# --- leitura dos arquivos do TSE -------------------------------------------------------------------------------
def ler_tse():
    """Uma linha por urna (seção principal) do Brasil, sem o exterior: aptos, comparecimento e local em cada turno, e
    os votos do 2º turno. Fica em saida/turnos_2026_secao.csv.gz enquanto os zips não mudam."""
    zips = [DETALHE[0], VOTACAO[0]]
    if CACHE.exists() and CACHE.stat().st_mtime > max(z.stat().st_mtime for z in zips):
        return pd.read_csv(CACHE)
    cols = ["NR_TURNO", *URNA, "CD_CARGO", "QT_APTOS", "QT_COMPARECIMENTO", "NR_LOCAL_VOTACAO",
            "ST_SECAO_INSTALADA", "DS_ORIGEM_VOTO"]
    pedacos = []
    with zipfile.ZipFile(DETALHE[0]) as z, z.open(DETALHE[1]) as f:
        for ch in pd.read_csv(f, sep=";", encoding="latin1", usecols=cols, chunksize=2_000_000, dtype={"SG_UF": str}):
            pedacos.append(ch[(ch.CD_CARGO == 1) & (ch.SG_UF != "ZZ")])
    d = pd.concat(pedacos).drop(columns="CD_CARGO")
    d = d.rename(columns={"QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "NR_LOCAL_VOTACAO": "local",
                          "ST_SECAO_INSTALADA": "instalada", "DS_ORIGEM_VOTO": "origem"})
    d = d.pivot(index=URNA, columns="NR_TURNO")
    d.columns = [f"{a}_t{b}" for a, b in d.columns]
    d = d.drop(columns=["instalada_t1", "origem_t1"])
    pedacos = []
    with zipfile.ZipFile(VOTACAO[0]) as z, z.open(VOTACAO[1]) as f:
        for ch in pd.read_csv(f, sep=";", encoding="latin1", usecols=["NR_TURNO", *URNA, "CD_CARGO", "NR_VOTAVEL", "QT_VOTOS"],
                              chunksize=2_000_000, dtype={"SG_UF": str}):
            pedacos.append(ch[(ch.CD_CARGO == 1) & (ch.NR_TURNO == 2) & (ch.SG_UF != "ZZ")])
    v = pd.concat(pedacos)
    v["col"] = v.NR_VOTAVEL.map({13: "c13_t2", 22: "c22_t2", 95: "brancos_t2"}).fillna("nulos_t2")
    v = v.pivot_table(index=URNA, columns="col", values="QT_VOTOS", aggfunc="sum", fill_value=0)
    d = d.join(v, how="left").fillna({c: 0 for c in v.columns}).reset_index()
    d["validos_t2"] = d.c13_t2 + d.c22_t2
    votos = d.validos_t2 + d.brancos_t2 + d.nulos_t2
    if (votos != d.comparecimento_t2).any():
        sys.exit(f"comparecimento do detalhe diferente da soma dos votos em {(votos != d.comparecimento_t2).sum()} urnas")
    d.to_csv(CACHE, index=False)
    return d


def historico():
    """Em que versões do cadastro cada urna esteve na lista (do git, pela lista de cada versão em versoes.py)."""
    vs = []
    for i, (_, commit, _) in enumerate(VERSOES):
        b = ((SAIDA / "urnas_mudadas_2026.csv").read_bytes() if commit is None else
             subprocess.run(["git", "show", f"{commit}:saida/urnas_mudadas_2026.csv"], cwd=RAIZ, capture_output=True,
                            check=True).stdout)
        vs.append(pd.read_csv(io.BytesIO(b), usecols=URNA).assign(v=i))
    p = pd.concat(vs).assign(x=True).pivot_table(index=URNA, columns="v", values="x", aggfunc="any", fill_value=False)
    return p.reindex(columns=range(len(VERSOES)), fill_value=False)


def urnas():
    u = pd.read_csv(SAIDA / "urnas_2026.csv.gz").merge(ler_tse(), on=URNA, how="inner", validate="1:1")
    u = u[(u.aptos_t1 > 0) & (u.aptos_t2 > 0)].copy()
    u["abst1"] = 100 * (1 - u.comparecimento_t1 / u.aptos_t1)
    u["abst2"] = 100 * (1 - u.comparecimento_t2 / u.aptos_t2)
    u["delta"] = u.abst2 - u.abst1
    u["grupo"] = u.tipo.map(GRUPO)
    u["faixa"] = faixa(u.dist_km)
    u["regiao"] = u.SG_UF.map(REGIAO)
    p = historico()
    final = p[p[len(VERSOES) - 1]]
    # a data de entrada é a do começo da sequência final de versões na lista (algumas saíram e voltaram)
    ini = final.apply(lambda r: len(r) - np.argmin(r.to_numpy()[::-1]) if not r.all() else 0, axis=1)
    u = u.join(ini.rename("v_entrada"), on=URNA)
    u["entrada"] = u.v_entrada.map(lambda i: np.nan if pd.isna(i) else ENTRADA[VERSOES[int(i)][0].split(",")[0]])
    u["ja_esteve"] = u.set_index(URNA).index.isin(p.index) & ~u.mudou
    return u


def faixa(dist):
    f = pd.cut(dist, FAIXAS, labels=ROTULOS, right=False).astype(object)
    return f.where(dist.notna(), "sem distância")


# --- comparação com as vizinhas ---------------------------------------------------------------------------------
def com_base(u, controle, base=B, cols=("delta", "abst1", "abst2"), peso="aptos_t1"):
    """Junta a cada urna a média ponderada de cada coluna nas urnas de controle do mesmo grupo."""
    out = u.copy()
    for c in cols:
        g = u[controle].assign(p=lambda d: d[c] * d[peso]).groupby(base)[["p", peso]].sum()
        out[f"base_{c}"] = u[base].join((g.p / g[peso]).rename("b"), on=base)["b"]
    return out.assign(ef=out.delta - out.base_delta)


def sorteio(m, base=B, col="ef", peso="aptos_t1"):
    """Média ponderada em cada sorteio dos grupos de comparação."""
    cl = m.groupby(base).ngroup().to_numpy()
    n = cl.max() + 1
    num, den = np.bincount(cl, m[col] * m[peso], n), np.bincount(cl, m[peso], n)
    w = rng.multinomial(n, np.full(n, 1 / n), size=SORTEIOS)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (w @ num) / (w @ den)


def linha(rot, m, base=B, peso="aptos_t1"):
    if m.empty:
        return None
    lo, hi = np.nanpercentile(sorteio(m, base, peso=peso), [2.5, 97.5])
    w = m[peso]
    return {"grupo": rot, "efeito_pp": np.average(m.ef, weights=w), "ic_baixo": lo, "ic_alto": hi, "urnas": len(m),
            "aptos": int(w.sum()), "grupos": m.groupby(base).ngroups, "pct_subiu_mais": 100 * (m.ef > 0).mean(),
            "abst1": 100 * (1 - m.comparecimento_t1.sum() / m.aptos_t1.sum()) if "comparecimento_t1" in m else np.nan,
            "abst2": 100 * (1 - m.comparecimento_t2.sum() / m.aptos_t2.sum()) if "comparecimento_t2" in m else np.nan,
            "abst1_acima": np.average(m.abst1 - m.base_abst1, weights=w) if "base_abst1" in m else np.nan,
            "abst2_acima": np.average(m.abst2 - m.base_abst2, weights=w) if "base_abst2" in m else np.nan}


def inclinacao(d, base, peso="aptos_t1", extra=None):
    """Pontos de efeito por km (mínimos quadrados ponderados), com intervalo por sorteio dos grupos."""
    d = d.reset_index(drop=True)

    def ajuste(dd):
        X = np.c_[np.ones(len(dd)), dd.dist_km] if extra is None else np.c_[pd.get_dummies(dd[extra]).to_numpy(float), dd.dist_km]
        w = np.sqrt(dd[peso].to_numpy(float))
        return np.linalg.lstsq(X * w[:, None], dd.ef.to_numpy() * w, rcond=None)[0][-1]

    cl = d.groupby(base).ngroup().to_numpy()
    n = cl.max() + 1
    idx = [np.flatnonzero(cl == k) for k in range(n)]
    bs = [ajuste(d.iloc[np.concatenate([idx[k] for k in rng.integers(0, n, n)])]) for _ in range(SORTEIOS)]
    return {"pp_por_km": float(ajuste(d)), "ic": [float(x) for x in np.percentile(bs, [2.5, 97.5])], "urnas": len(d),
            "mediana_km": float(d.dist_km.median()), "max_km": float(d.dist_km.max())}


def efeitos_2022():
    """Efeito urna a urna em 2022, como em 03_impacto.py (vizinhas: todas as que não mudaram)."""
    u = pd.read_csv(SAIDA / "urnas_2022.csv.gz")
    v = pd.read_csv(SAIDA / "votos_2022_secao.csv.gz", usecols=URNA + ["NR_TURNO", "comparecimento"])
    v = v.pivot_table(index=URNA, columns="NR_TURNO", values="comparecimento", aggfunc="sum")
    u = u.join(v.rename(columns={1: "comparecimento_t1", 2: "comparecimento_t2"}), on=URNA, how="inner")
    u = u[(u.aptos > 0) & (u.aptos_2 > 0)].rename(columns={"aptos": "aptos_t1", "aptos_2": "aptos_t2"})
    u = u.assign(abst1=100 * (1 - u.comparecimento_t1 / u.aptos_t1), abst2=100 * (1 - u.comparecimento_t2 / u.aptos_t2))
    u = u.assign(delta=u.abst2 - u.abst1)
    u = u[u.delta.between(-60, 60)]
    m = com_base(u, ~u.mudou)
    return m[m.mudou & m.base_delta.notna()].assign(faixa=lambda d: faixa(d.dist_km), ano=2022)


# --- contas ---------------------------------------------------------------------------------------------------
def main():
    u = urnas()
    print("urnas:", len(u), "| na lista:", int(u.mudou.sum()), "| estiveram na lista e saíram:", int(u.ja_esteve.sum()),
          "| variação de mais de 60 pontos (fora):", int((~u.delta.between(-60, 60)).sum()))

    # 1. o local de cada urna no resultado, comparado com o cadastro final
    conf = {"urnas": len(u),
            "local_diferente_t1": int((u.local_t1 != u.NR_LOCAL_VOTACAO).sum()),
            "local_diferente_t2": int((u.local_t2 != u.NR_LOCAL_VOTACAO_2).sum()),
            "mudou_numero": int((u.local_t1 != u.local_t2).sum()),
            "mudou_numero_fora_da_lista": int(((u.local_t1 != u.local_t2) & ~u.mudou).sum()),
            "lista_mesmo_numero": int(((u.local_t1 == u.local_t2) & u.mudou).sum()),
            "lista_instaladas": int((u.mudou & (u.instalada_t2 == "Sim")).sum()),
            "lista_urna_eletronica": int((u.mudou & (u.origem_t2 == "Urna Eletrônica")).sum())}
    print("conferência:", conf)
    nac = {"lula": int(u.c13_t2.sum()), "flavio": int(u.c22_t2.sum()), "validos": int(u.validos_t2.sum()),
           "aptos_t1": int(u.aptos_t1.sum()), "aptos_t2": int(u.aptos_t2.sum()),
           "abst_t1": 100 * (1 - u.comparecimento_t1.sum() / u.aptos_t1.sum()),
           "abst_t2": 100 * (1 - u.comparecimento_t2.sum() / u.aptos_t2.sum())}
    nac.update(pct_lula=100 * nac["lula"] / nac["validos"], pct_flavio=100 * nac["flavio"] / nac["validos"],
               margem_lula=nac["lula"] - nac["flavio"])
    print("2º turno no Brasil:", nac)

    # 2. efeito, com as vizinhas que nunca estiveram na lista
    u = u[u.delta.between(-60, 60)].copy()
    ctrl = ~u.mudou & ~u.ja_esteve & ~u.tipo.isin(REESCRITAS)
    b = com_base(u, ctrl)
    m = b[b.mudou & b.base_delta.notna()].sort_values(URNA).copy()
    m["generico"] = m.mesmo_endereco
    print("urnas da lista com vizinhas:", len(m), "| com distância:", int(m.dist_km.notna().sum()))

    q = pd.qcut(m.abst1 - m.base_abst1, 3, labels=["abaixo", "perto", "acima"])
    grupos = [("todas", m), ("saíram do local de sempre ou trocaram de provisório", m[m.grupo == "sai"]),
              ("voltaram ao local de sempre", m[m.grupo == "volta"])]
    grupos += [(t, m[m.tipo == t]) for t in m.tipo.value_counts().index]
    grupos += [(f, m[m.faixa == f]) for f in ROTULOS + ["sem distância"]]
    grupos += [("endereço genérico", m[m.generico]), ("nome parecido", m[m.nome_parecido]),
               ("mesmo bairro", m[m.NM_BAIRRO == m.NM_BAIRRO_2]), ("outro bairro", m[m.NM_BAIRRO != m.NM_BAIRRO_2])]
    grupos += [(f"entraram na lista em {e}", m[m.entrada == e]) for e in dict.fromkeys(ENTRADA.values())]
    grupos += [(r, m[m.regiao == r]) for r in ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]]
    grupos += [(f"abstenção no 1º turno {k} das vizinhas", m[q == k]) for k in q.cat.categories]

    # 3. testes de controle: cada grupo comparado com as vizinhas sem ele
    reesc = u.tipo.isin(REESCRITAS)
    for rot, sel in [("controle: reescritas no cadastro", reesc),
                     ("controle: estiveram na lista e saíram", u.ja_esteve & ~reesc),
                     ("controle: fora do local de sempre nos dois turnos",
                      ctrl & (u.tipo == "igual, fora do cadastro nos dois turnos"))]:
        p = com_base(u, ctrl & ~sel)
        grupos.append((rot, p[sel & p.base_delta.notna()]))
    res = pd.DataFrame([r for r in (linha(rot, d) for rot, d in grupos) if r])
    res.to_csv(SAIDA / "abstencao_2t.csv", index=False)
    pd.set_option("display.width", 250)
    print(res.drop(columns=["aptos", "abst1", "abst2"]).round(2).to_string(index=False))

    outras = {}
    for nome, base in BASES.items():
        bb = com_base(u, ctrl, base)
        mb = bb[bb.mudou & bb.base_delta.notna()]
        outras[nome] = linha(nome, mb, base)
    bb = com_base(u, ~u.mudou)
    outras["todas_as_vizinhas"] = linha("todas_as_vizinhas", bb[bb.mudou & bb.base_delta.notna()])
    print("outras comparações:", {k: (round(v["efeito_pp"], 2), [round(x, 2) for x in (v["ic_baixo"], v["ic_alto"])],
                                      v["urnas"]) for k, v in outras.items()})

    # 4. distância: inclinação, e 2022 e 2026 juntos
    d26 = m[m.dist_km.notna()].assign(ano=2026)
    m22 = efeitos_2022()
    d22 = m22[m22.dist_km.notna()]
    print("2022, conferência com 03_impacto.py: efeito de todas as urnas", round(np.average(m22.ef, weights=m22.aptos_t1), 3))
    juntas = pd.concat([d26, d22], ignore_index=True)[["ano", *B, "ef", "dist_km", "aptos_t1", "faixa"]]
    dist = {"inclinacao_2026": inclinacao(d26, B),
            "inclinacao_juntas_ate_5km": inclinacao(juntas[juntas.dist_km <= 5], ["ano", *B], extra="ano"),
            "faixas_2022": [linha(f, d22[d22.faixa == f]) for f in ROTULOS],
            "faixas_juntas": [linha(f, juntas[juntas.faixa == f], ["ano", *B]) for f in ROTULOS],
            "mais_longe_2026": m[m.dist_km >= 1.2].sort_values("dist_km", ascending=False)[
                ["SG_UF", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "tipo", "dist_km", "ef"]].to_dict("records")}
    print("distância:", json.dumps({k: v for k, v in dist.items() if k.startswith("inclinacao")}, default=float))
    print(pd.DataFrame(dist["faixas_juntas"])[["grupo", "efeito_pp", "ic_baixo", "ic_alto", "urnas"]].round(2).to_string(index=False))

    # por município, para os casos com muitas urnas
    mun = (m.assign(p=m.ef * m.aptos_t1).groupby(["SG_UF", "NM_MUNICIPIO"])
           .agg(urnas=("ef", "size"), aptos=("aptos_t1", "sum"), p=("p", "sum"), subiram_mais=("ef", lambda s: int((s > 0).sum())),
                dist_mediana_km=("dist_km", "median"), generico=("generico", "sum"))
           .assign(efeito_pp=lambda d: d.p / d.aptos).drop(columns="p").sort_values("urnas", ascending=False))
    mun.to_csv(SAIDA / "abstencao_2t_municipios.csv")

    # 5. no resultado: votos de margem (Flávio - Lula) por ponto de abstenção, como os votos da urna no 2º turno
    m["margem_por_pp"] = m.aptos_t2 / 100 * (m.c13_t2 - m.c22_t2) / m.comparecimento_t2
    todas = res.iloc[0]
    n = json.loads((SAIDA / "numeros.json").read_text(encoding="utf-8"))
    a1 = json.loads((SAIDA / "abstencao_1t.json").read_text(encoding="utf-8"))
    sai = res.set_index("grupo").loc["saiu do local de cadastro"]
    resultado = {
        "margem_media": float(todas.efeito_pp * m.margem_por_pp.sum()),
        "margem_ic": sorted([float(todas.ic_baixo * m.margem_por_pp.sum()), float(todas.ic_alto * m.margem_por_pp.sum())]),
        "margem_urna_a_urna": float((m.ef * m.margem_por_pp).sum()),
        "eleitores_a_mais": float(-(m.ef * m.aptos_t2 / 100).sum()),
        "estimado_antes": {k: n["impacto"][n["principal"]][k] for k in ["margem", "margem_ic", "margem_previsao", "eleitores_a_mais"]},
        "efeito_2022": {k: n["sensibilidade_2022"][n["principal"]][k] for k in ["efeito_pp", "ic_baixo", "ic_alto"]},
        "efeito_1t_2026": {"dif_pp": a1["variacao_desde_2022"]["dif_pp"], "ic": a1["variacao_desde_2022"]["ic"]},
        "sens_2t_antes": a1["sensibilidade_2t"]["margem"],
        "sai_cadastro_pp": float(sai.efeito_pp), "sai_cadastro_ic": [float(sai.ic_baixo), float(sai.ic_alto)],
    }
    print("no resultado:", json.dumps(resultado, default=float))

    lista = {"urnas": len(m), "aptos": int(m.aptos_t1.sum()), "lula_t2": int(m.c13_t2.sum()), "flavio_t2": int(m.c22_t2.sum()),
             "pct_lula_t2": float(100 * m.c13_t2.sum() / m.validos_t2.sum()),
             "pct_lula_t1": n["mudadas"]["pct_lula"], "com_distancia": int(m.dist_km.notna().sum())}
    out = {"conferencia": conf, "nacional_2t": nac, "lista": lista, "grupos": res.to_dict("records"),
           "outras_comparacoes": outras, "distancia": dist, "resultado": resultado}
    (SAIDA / "abstencao_2t.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    cols = (URNA + ["NM_MUNICIPIO", "tipo", "NM_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO_2", "dist_km",
                    "generico", "entrada", "aptos_t1", "aptos_t2", "comparecimento_t1", "comparecimento_t2", "abst1",
                    "abst2", "base_abst1", "base_abst2", "base_delta", "ef", "c13_t2", "c22_t2"])
    m[cols].to_csv(SAIDA / "abstencao_2t_urnas.csv", index=False, float_format="%.4f")


if __name__ == "__main__":
    main()
