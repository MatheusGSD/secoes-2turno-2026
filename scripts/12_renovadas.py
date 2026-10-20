"""Como a lista encolheu entre as versões do cadastro de locais do TSE.

A cada versão do cadastro (todas em versoes.py), urnas saíram da lista, e
sempre do mesmo jeito: iam voltar ao local de sempre no 2º turno e passaram a ficar no prédio provisório do 1º
turno. Aqui juntamos as comparações de 07_versoes.py (as anteriores estão no git) para contar essas urnas por
estado, ver se algum prédio provisório ficou dividido (parte das urnas fica, parte volta) e acompanhar a taxa de
volta ao local de sempre, comparada com a de 2022.

Taxa de volta: urnas que voltam ao local de sempre no 2º turno / urnas que funcionaram fora dele no 1º turno. O
denominador vem do cadastro atual (o local do 1º turno é histórico e não muda entre as versões); o numerador de
cada versão, do numeros.json daquela versão no git. Em 2022 só existe o cadastro final.

As versões e os commits estão em versoes.py, que 00_atualizar.py atualiza a cada cadastro novo (o arquivo de
07_versoes.py da versão anterior fica no git). Precisa do histórico completo do git (não funciona em clone raso).

Uso: python -P scripts/12_renovadas.py (depois de 02_mudancas.py, 03_impacto.py e 07_versoes.py; antes de 04)
Saídas: saida/renovadas_uf.csv e saida/renovadas.json
"""
import io
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import VERSOES, ref  # noqa: E402

SAIDA = RAIZ / "saida"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
VOLTA, FICA, TROCA = "voltou ao local de cadastro", "igual, fora do cadastro nos dois turnos", "trocou de local provisório"


def git(ref):
    return subprocess.run(["git", "show", ref], cwd=RAIZ, capture_output=True, check=True).stdout


def main():
    u = pd.read_csv(SAIDA / "urnas_2026.csv.gz", low_memory=False)
    fora_1t = int(u.tipo.isin([VOLTA, FICA, TROCA]).sum())
    versoes, saidas = [], []
    for cadastro, commit, comp in VERSOES:
        n = json.loads(git(f"{commit}:saida/numeros.json")) if commit else json.loads((SAIDA / "numeros.json").read_text(encoding="utf-8"))
        voltam = next(t["urnas"] for t in n["tipos"] if t["tipo"] == VOLTA)
        v = {"cadastro": cadastro, "urnas": n["mudadas"]["urnas"], "voltam": voltam, "taxa_volta": round(100 * voltam / fora_1t, 1)}
        if comp:
            c = pd.read_csv(io.BytesIO(git(ref(commit, comp))) if commit else SAIDA / comp)
            s = c[c.situacao == "saiu da lista"]
            v.update(sairam=len(s), entraram=int((c.situacao == "entrou na lista").sum()))
            saidas.append(s[URNA].assign(cadastro=cadastro))
        versoes.append(v)

    ren = pd.concat(saidas).merge(u[URNA + ["tipo", "aptos", "NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_ORIGINAL"]], on=URNA)
    if not (ren.tipo == FICA).all():
        print("AVISO: urnas que saíram da lista e hoje não ficam no prédio do 1º turno:", ren.tipo.value_counts().to_dict())
    volta = u[u.tipo == VOLTA]
    # as que voltavam no primeiro cadastro e hoje vão para outro prédio provisório
    primeiro = pd.read_csv(io.BytesIO(git(f"{VERSOES[0][1]}:saida/urnas_mudadas_2026.csv")))
    outras = primeiro[primeiro.tipo == VOLTA][URNA].merge(u[URNA + ["tipo"]], on=URNA)
    outras = outras[outras.tipo == TROCA]
    # as que ainda voltam e já voltavam no primeiro cadastro (as outras entraram na lista depois)
    volta_1o = volta.merge(primeiro[primeiro.tipo == VOLTA][URNA], on=URNA)

    # prédio provisório dividido: parte das urnas ficou nele, parte ainda volta ao local de sempre
    predio = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO"]
    divididos = volta.merge(ren[predio].drop_duplicates(), on=predio)
    zona = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA"]
    mesma_zona = volta.merge(ren[zona].drop_duplicates(), on=zona)

    t = ren.pivot_table(index="SG_UF", columns="cadastro", values="aptos", aggfunc="size", fill_value=0)
    t = t.reindex(columns=[v["cadastro"] for v in versoes if "sairam" in v], fill_value=0)
    t["renovadas"] = t.sum(axis=1)
    t = t.join(volta_1o.groupby("SG_UF").size().rename("ainda_voltam"), how="outer")
    t = t.join(outras.groupby("SG_UF").size().rename("outro_provisorio"), how="outer").fillna(0).astype(int)
    t["voltavam_1o_cadastro"] = t.renovadas + t.ainda_voltam + t.outro_provisorio
    t = t.sort_values(["voltavam_1o_cadastro", "renovadas"], ascending=False)

    # voto no 1º turno: as que saíram da lista e as que ainda voltam
    # e o voto em Lula esperado pelo município, ponderado pelos votos válidos de cada urna (como em 11_geografia.py)
    v = pd.read_csv(SAIDA / "votos_2026_secao.csv.gz")
    v = v[v.NR_TURNO == 1]
    mun = v.groupby(["SG_UF", "CD_MUNICIPIO"])[["c13", "validos"]].sum()
    mun = (mun.c13 / mun.validos).rename("lula_mun")
    v = v.groupby(URNA)[["c13", "c22", "validos"]].sum()

    def voto(df):
        x = df[URNA].merge(v, left_on=URNA, right_index=True).join(mun, on=["SG_UF", "CD_MUNICIPIO"])
        return {"urnas": len(df), "pct_lula": round(100 * x.c13.sum() / x.validos.sum(), 1),
                "pct_flavio": round(100 * x.c22.sum() / x.validos.sum(), 1),
                "lula_esperado_pelo_municipio": round(100 * (x.lula_mun * x.validos).sum() / x.validos.sum(), 1)}
    t.to_csv(SAIDA / "renovadas_uf.csv")

    u22 = pd.read_csv(SAIDA / "urnas_2022.csv.gz", low_memory=False)
    fora_1t_22, voltam_22 = int(u22.tipo.isin([VOLTA, FICA, TROCA]).sum()), int((u22.tipo == VOLTA).sum())
    res = {
        "versoes": versoes, "renovadas": len(ren), "aptos_renovadas": int(ren.aptos.sum()),
        "entraram": sum(v.get("entraram", 0) for v in versoes),
        "ufs_com_renovacao": int((t.renovadas > 0).sum()), "municipios": int(ren.groupby(["SG_UF", "CD_MUNICIPIO"]).ngroups),
        "zonas": int(ren.groupby(zona).ngroups), "predios_divididos": int(len(divididos)),
        "voltam_em_zona_com_renovacao": int(len(mesma_zona)), "fora_1t": fora_1t,
        "taxa_volta_2022": round(100 * voltam_22 / fora_1t_22, 1), "voltam_2022": voltam_22, "fora_1t_2022": fora_1t_22,
        "outro_provisorio": len(outras), "ainda_voltam_1o_cadastro": len(volta_1o), "voto_renovadas": voto(ren), "voto_ainda_voltam": voto(volta),
        "ufs": [{"uf": uf, "renovadas": int(r.renovadas), "ainda_voltam": int(r.ainda_voltam),
                 "outro_provisorio": int(r.outro_provisorio), "voltavam": int(r.voltavam_1o_cadastro),
                 "por_versao": {c: int(r[c]) for c in t.columns[:len(saidas)]}}
                for uf, r in t.iterrows()],
    }
    (SAIDA / "renovadas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for v in versoes:
        print(v)
    print("renovadas:", res["renovadas"], "urnas,", res["aptos_renovadas"], "aptos | UFs:", res["ufs_com_renovacao"],
          "| municípios:", res["municipios"], "| zonas:", res["zonas"], "| prédios divididos:", res["predios_divididos"],
          "| ainda voltam em zona com renovação:", res["voltam_em_zona_com_renovacao"])
    print("foram para outro prédio provisório:", len(outras), "| voto no 1º turno:", res["voto_renovadas"], res["voto_ainda_voltam"])
    print("fora do local de sempre no 1º turno:", fora_1t, "| 2022:", voltam_22, "de", fora_1t_22, "voltaram,", res["taxa_volta_2022"], "%")
    print(t.to_string())


if __name__ == "__main__":
    main()
