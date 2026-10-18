"""O que mudou entre a versão de 17/10 e a atual da lista de urnas que mudam de prédio.

A versão de 17/10 usava o cadastro de locais gerado em 17/10 (6h32 de Brasília) e está no histórico do
git, no commit 943ab33. A atual usa o cadastro gerado em 17/10 às 23h37 de Brasília, baixado em 18/10.
Para cada urna que está em uma das duas listas, compara o local do 1º e do 2º turno nas duas versões.

Uso: python -P scripts/07_versoes.py (depois de 02_mudancas.py)
Saída: saida/versoes_17_18out.csv
"""
import io
import subprocess
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
COMMIT_17OUT = "943ab33"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
LOCAIS = ["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2", "NM_LOCAL_VOTACAO_2"]


def main():
    csv = subprocess.run(["git", "show", f"{COMMIT_17OUT}:saida/urnas_mudadas_2026.csv"], cwd=RAIZ,
                         capture_output=True, check=True).stdout
    antes = pd.read_csv(io.BytesIO(csv)).set_index(URNA)
    agora = pd.read_csv(SAIDA / "urnas_2026.csv.gz").set_index(URNA)
    chaves = antes.index.union(agora.index[agora.mudou])
    v = (antes.reindex(chaves)[["NM_MUNICIPIO", "tipo", "aptos"] + LOCAIS].add_suffix("_17out")
         .join(agora.reindex(chaves)[["tipo", "mudou"] + LOCAIS].add_suffix("_18out")))
    v["situacao"] = "nas duas versões"
    v.loc[~v.mudou_18out.astype(bool), "situacao"] = "saiu da lista"
    v.loc[v.tipo_17out.isna(), "situacao"] = "entrou na lista"
    mudou_1t = v.NR_LOCAL_VOTACAO_17out != v.NR_LOCAL_VOTACAO_18out
    mudou_2t = v.NR_LOCAL_VOTACAO_2_17out != v.NR_LOCAL_VOTACAO_2_18out
    v["o_que_mudou_no_cadastro"] = ""
    v.loc[mudou_2t & ~mudou_1t, "o_que_mudou_no_cadastro"] = "local do 2º turno"
    v.loc[mudou_1t & ~mudou_2t, "o_que_mudou_no_cadastro"] = "local do 1º turno"
    v.loc[mudou_1t & mudou_2t, "o_que_mudou_no_cadastro"] = "os dois"
    v.loc[v.situacao == "saiu da lista", "fica_no_predio_do_1t"] = (
        v.NR_LOCAL_VOTACAO_2_18out == v.NR_LOCAL_VOTACAO_17out)
    v.reset_index().to_csv(SAIDA / "versoes_17_18out.csv", index=False)
    print(v.groupby(["situacao", "o_que_mudou_no_cadastro"]).size().to_string())
    s = v[v.situacao == "saiu da lista"]
    print("saíram:", len(s), "urnas,", int(s.aptos_17out.sum()), "aptos | tipo em 17/10:", s.tipo_17out.value_counts().to_dict(),
          "| tipo agora:", s.tipo_18out.value_counts().to_dict(),
          "| ficam no prédio do 1º turno:", int(s.fica_no_predio_do_1t.sum()))
    print("por UF:", s.SG_UF.value_counts().to_dict() if "SG_UF" in s else s.reset_index().SG_UF.value_counts().to_dict())


if __name__ == "__main__":
    main()
