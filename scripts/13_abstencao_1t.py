"""A mudança do local de cadastro para o prédio provisório, já no 1º turno de 2026, fez o eleitor faltar?

Em 6.588 urnas, o 1º turno de 2026 já foi num prédio diferente do local de cadastro (o local de sempre, em geral o
mesmo de 2022 e 2024). Comparamos a abstenção delas no 1º turno com a das urnas do mesmo município e da mesma zona
eleitoral que votaram no local de cadastro, de duas formas:
- nível: abstenção no 1º turno de 2026 menos a das vizinhas;
- variação desde 2022: (abstenção no 1º turno de 2026 menos a do 1º turno de 2022, na mesma urna) menos a mesma
  variação nas vizinhas. Só entram urnas com a mesma chave (estado, município, zona e seção) nos dois anos, o mesmo
  local de cadastro e que, no 1º turno de 2022, votaram no local de cadastro. Assim, a comparação desconta o que já
  era diferente nessas urnas antes da mudança.
Média ponderada pelos aptos; intervalo de 95% por 2.000 sorteios dos grupos de comparação (município e zona). É uma
comparação entre urnas, não um experimento. Para a ordem de grandeza no resultado, aplicamos a variação desde 2022 (e
os limites do intervalo) a todas as urnas fora do local de cadastro, com quem deixou de votar dividido como os votos
da própria urna.

Uso: python -P scripts/13_abstencao_1t.py (depois de 02_mudancas.py e 01_votos_1t.py)
Saída: saida/abstencao_1t.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
BASE = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA"]
SORTEIOS = 2000
rng = np.random.default_rng(2026)


def abstencao_1t(ano):
    u = pd.read_csv(SAIDA / f"urnas_{ano}.csv.gz", usecols=URNA + ["aptos", "NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_ORIGINAL"])
    v = pd.read_csv(SAIDA / f"votos_{ano}_secao.csv.gz", usecols=URNA + ["NR_TURNO", "comparecimento", "c13", "c22", "validos"])
    v = v[v.NR_TURNO == 1].groupby(URNA)[["comparecimento", "c13", "c22", "validos"]].sum()
    u = u.join(v, on=URNA, how="inner")
    u = u[u.aptos > 0]
    u["abst"] = 100 * (1 - u.comparecimento / u.aptos)
    u["fora"] = u.NR_LOCAL_VOTACAO != u.NR_LOCAL_VOTACAO_ORIGINAL
    return u


def comparar(u, col):
    """Diferença ponderada entre as urnas fora do local de cadastro e as vizinhas que ficaram nele, com intervalo."""
    viz = (u[~u.fora].assign(p=lambda d: d[col] * d.aptos).groupby(BASE)[["p", "aptos"]].sum()
           .pipe(lambda x: (x.p / x.aptos).rename("base")))
    m = u[u.fora].join(viz, on=BASE).dropna(subset=["base"]).assign(ef=lambda d: d[col] - d.base)
    cl = m.groupby(BASE).ngroup().to_numpy()
    n = cl.max() + 1
    num, den = np.bincount(cl, m.ef * m.aptos, n), np.bincount(cl, m.aptos, n)
    w = rng.multinomial(n, np.full(n, 1 / n), size=SORTEIOS)
    bs = (w @ num) / (w @ den)
    return {"dif_pp": float(np.average(m.ef, weights=m.aptos)), "ic": [float(x) for x in np.percentile(bs, [2.5, 97.5])],
            "urnas": len(m), "aptos": int(m.aptos.sum()),
            "abst_fora": float(100 * (1 - m.comparecimento.sum() / m.aptos.sum()))}


def main():
    a26, a22 = abstencao_1t(2026), abstencao_1t(2022)
    nivel = comparar(a26, "abst")

    d = a26.merge(a22[URNA + ["abst", "fora", "NR_LOCAL_VOTACAO_ORIGINAL"]], on=URNA, suffixes=("", "_22"))
    d = d[(d.NR_LOCAL_VOTACAO_ORIGINAL == d.NR_LOCAL_VOTACAO_ORIGINAL_22) & ~d.fora_22].assign(var=lambda x: x.abst - x.abst_22)
    d = d[d["var"].between(-60, 60)]
    variacao = comparar(d, "var")
    nivel_22 = comparar(d.assign(abst=d.abst_22), "abst")  # as mesmas urnas, em 2022, antes da mudança

    f = a26[a26.fora]
    efeito = {}
    for nome, pp in [("estimativa", variacao["dif_pp"]), ("ic_baixo", variacao["ic"][0]), ("ic_alto", variacao["ic"][1])]:
        faltaram = pp / 100 * f.aptos
        efeito[nome] = {"eleitores_a_menos": float(faltaram.sum()),
                        "votos_liquidos_lula": float(-(faltaram * (f.c13 - f.c22) / f.comparecimento).sum())}
    res = {"fora_no_1t_2026": int(a26.fora.sum()), "aptos_fora": int(f.aptos.sum()),
           "pct_lula_fora": float(100 * f.c13.sum() / f.validos.sum()), "pct_flavio_fora": float(100 * f.c22.sum() / f.validos.sum()),
           "efeito_no_resultado_1t": efeito,
           "abst_pais_1t_2026": float(100 * (1 - a26.comparecimento.sum() / a26.aptos.sum())),
           "nivel_2026": nivel, "variacao_desde_2022": variacao, "nivel_2022_mesmas_urnas": nivel_22}
    (SAIDA / "abstencao_1t.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
