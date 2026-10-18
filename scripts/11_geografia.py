"""Onde ficam as urnas que mudam de prédio do 1º para o 2º turno, em 2022 e em 2026, e quanto disso explica o voto.

Para cada ano: a parte dos eleitores das urnas que mudam em cada região, comparada com o peso da região no
eleitorado; a taxa de urnas que mudam por estado e a correlação entre os dois anos; e o voto em Lula no 1º
turno nessas urnas, comparado com o esperado se cada uma votasse como o próprio estado ou município (a média
do lugar, ponderada pelos votos válidos das urnas que mudam). Unidade: a urna; sem o exterior.

Uso: python -P scripts/11_geografia.py   (depois de 01 e 02)
Saídas: saida/geografia_regioes.csv, saida/geografia_ufs.csv e saida/geografia.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
REGIOES = {"Norte": "AC AM AP PA RO RR TO", "Nordeste": "AL BA CE MA PB PE PI RN SE", "Centro-Oeste": "DF GO MS MT",
           "Sudeste": "ES MG RJ SP", "Sul": "PR RS SC"}
REGIAO = {uf: r for r, ufs in REGIOES.items() for uf in ufs.split()}


def urnas(ano):
    u = pd.read_csv(SAIDA / f"urnas_{ano}.csv.gz", usecols=URNA + ["aptos", "mudou"])
    v = pd.read_csv(SAIDA / f"votos_{ano}_secao.csv.gz")
    v = v[v.NR_TURNO == 1][URNA + ["c13", "validos"]]
    d = u[u.SG_UF != "ZZ"].merge(v, on=URNA)
    d["regiao"] = d.SG_UF.map(REGIAO)
    return d


def main():
    regioes, ufs, resumo = [], [], {}
    for ano in [2022, 2026]:
        d = urnas(ano)
        m = d[d.mudou]
        r = pd.DataFrame({"aptos_mudam": m.groupby("regiao").aptos.sum(), "aptos": d.groupby("regiao").aptos.sum(),
                          "urnas_mudam": m.groupby("regiao").size(), "urnas": d.groupby("regiao").size()})
        r["pct_aptos_mudam"] = r.aptos_mudam / r.aptos_mudam.sum() * 100
        r["pct_eleitorado"] = r.aptos / r.aptos.sum() * 100
        regioes.append(r.reindex(list(REGIOES)).assign(ano=ano).reset_index())
        u = d.groupby("SG_UF").agg(urnas=("mudou", "size"), urnas_mudam=("mudou", "sum"), c13=("c13", "sum"),
                                   validos=("validos", "sum"))
        u["pct_urnas_mudam"] = u.urnas_mudam / u.urnas * 100
        u["pct_lula"] = u.c13 / u.validos * 100
        ufs.append(u.assign(ano=ano).reset_index())
        esperado = {}
        for g in ["regiao", "SG_UF", "CD_MUNICIPIO"]:
            lula = d.groupby(g).c13.sum() / d.groupby(g).validos.sum()
            esperado[g] = float((m.groupby(g).validos.sum() * lula).sum() / m.validos.sum() * 100)
        resumo[ano] = {"urnas_mudam": int(len(m)), "aptos_mudam": int(m.aptos.sum()),
                       "lula_nas_que_mudam": float(m.c13.sum() / m.validos.sum() * 100),
                       "lula_no_pais": float(d.c13.sum() / d.validos.sum() * 100),
                       "lula_esperado_pela_regiao": esperado["regiao"], "lula_esperado_pelo_estado": esperado["SG_UF"],
                       "lula_esperado_pelo_municipio": esperado["CD_MUNICIPIO"]}
        print(f"\n{ano}: {len(m)} urnas mudam, {m.aptos.sum():,} eleitores")
        print(r[["pct_aptos_mudam", "pct_eleitorado"]].reindex(list(REGIOES)).round(1).to_string())
        print({k: round(v, 1) if isinstance(v, float) else v for k, v in resumo[ano].items()})
    reg = pd.concat(regioes)
    uf = pd.concat(ufs)
    p = uf.pivot(index="SG_UF", columns="ano", values="pct_urnas_mudam")
    resumo["correlacao_ufs_2022_2026"] = float(p[2022].corr(p[2026], method="spearman"))
    resumo["ufs_mais_mudam"] = {str(a): p[a].sort_values(ascending=False).head(5).round(2).to_dict() for a in [2022, 2026]}
    print("\ncorrelação (Spearman) da taxa por estado, 2022 x 2026:", round(resumo["correlacao_ufs_2022_2026"], 2))
    print("estados com mais urnas mudando:", resumo["ufs_mais_mudam"])
    reg.to_csv(SAIDA / "geografia_regioes.csv", index=False)
    uf.to_csv(SAIDA / "geografia_ufs.csv", index=False)
    (SAIDA / "geografia.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
