"""O que mudou entre a versão anterior e a atual da lista de urnas que mudam de prédio.

Versões, todas no histórico do git:
- 943ab33: cadastro de locais gerado em 17/10, 6h32 de Brasília (2.059 urnas);
- 01b4452: cadastro gerado em 17/10, 23h37 (1.792 urnas). A comparação com a anterior está em
  saida/versoes_17_18out.csv, gerada no commit fa873d1;
- 2272612: cadastro gerado em 18/10, 11h27 (1.733 urnas). A comparação com a anterior está em
  saida/versoes_18out.csv, gerada nesse commit;
- atual: cadastro gerado em 18/10, 20h27 (dados/eleitorado_local_votacao_2026.zip).
Para cada urna que está em uma das duas listas, compara o local do 1º e do 2º turno nas duas versões.

Uso: python -P scripts/07_versoes.py (depois de 02_mudancas.py)
Saída: saida/versoes_18out_noite.csv
"""
import io
import subprocess
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
COMMIT_ANTES, ANTES, AGORA = "2272612", "18out_11h", "18out_20h"  # sufixos: data e hora do cadastro
SAIDA_CSV = "versoes_18out_noite.csv"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
LOCAIS = ["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2", "NM_LOCAL_VOTACAO_2"]


def main():
    csv = subprocess.run(["git", "show", f"{COMMIT_ANTES}:saida/urnas_mudadas_2026.csv"], cwd=RAIZ,
                         capture_output=True, check=True).stdout
    antes = pd.read_csv(io.BytesIO(csv)).set_index(URNA)
    agora = pd.read_csv(SAIDA / "urnas_2026.csv.gz").set_index(URNA)
    chaves = antes.index.union(agora.index[agora.mudou])
    v = (antes.reindex(chaves)[["NM_MUNICIPIO", "tipo", "aptos"] + LOCAIS].add_suffix(f"_{ANTES}")
         .join(agora.reindex(chaves)[["tipo", "mudou"] + LOCAIS].add_suffix(f"_{AGORA}")))
    v["situacao"] = "nas duas versões"
    v.loc[~v[f"mudou_{AGORA}"].astype(bool), "situacao"] = "saiu da lista"
    v.loc[v[f"tipo_{ANTES}"].isna(), "situacao"] = "entrou na lista"
    mudou_1t = v[f"NR_LOCAL_VOTACAO_{ANTES}"] != v[f"NR_LOCAL_VOTACAO_{AGORA}"]
    mudou_2t = v[f"NR_LOCAL_VOTACAO_2_{ANTES}"] != v[f"NR_LOCAL_VOTACAO_2_{AGORA}"]
    v["o_que_mudou_no_cadastro"] = ""
    v.loc[mudou_2t & ~mudou_1t, "o_que_mudou_no_cadastro"] = "local do 2º turno"
    v.loc[mudou_1t & ~mudou_2t, "o_que_mudou_no_cadastro"] = "local do 1º turno"
    v.loc[mudou_1t & mudou_2t, "o_que_mudou_no_cadastro"] = "os dois"
    v.loc[v.situacao == "saiu da lista", "fica_no_predio_do_1t"] = (
        v[f"NR_LOCAL_VOTACAO_2_{AGORA}"] == v[f"NR_LOCAL_VOTACAO_{ANTES}"])
    v.reset_index().to_csv(SAIDA / SAIDA_CSV, index=False)
    print(v.groupby(["situacao", "o_que_mudou_no_cadastro"]).size().to_string())
    s = v[v.situacao == "saiu da lista"]
    print("saíram:", len(s), "urnas,", int(s[f"aptos_{ANTES}"].sum()), "aptos | tipo antes:", s[f"tipo_{ANTES}"].value_counts().to_dict(),
          "| tipo agora:", s[f"tipo_{AGORA}"].value_counts().to_dict(),
          "| ficam no prédio do 1º turno:", int(s.fica_no_predio_do_1t.sum()))
    e = v[v.situacao == "entrou na lista"].reset_index()
    print("entraram:", len(e), "urnas | por município:", e.groupby(["SG_UF", f"NM_MUNICIPIO_{ANTES}"]).size().to_dict()
          if e[f"NM_MUNICIPIO_{ANTES}"].notna().any() else e.groupby("SG_UF").size().to_dict())
    print("por UF:", s.SG_UF.value_counts().to_dict() if "SG_UF" in s else s.reset_index().SG_UF.value_counts().to_dict())


if __name__ == "__main__":
    main()
