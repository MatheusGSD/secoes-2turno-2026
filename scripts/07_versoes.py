"""O que mudou entre a versão anterior e a atual da lista de urnas que mudam de prédio.

Versões, todas no histórico do git:
- 943ab33: cadastro de locais gerado em 17/10, 6h28 de Brasília (2.059 urnas);
- 01b4452: cadastro gerado em 17/10, 23h33 (1.792 urnas). A comparação com a anterior está em
  saida/versoes_17_18out.csv, gerada no commit fa873d1;
- 2272612: cadastro gerado em 18/10, 11h27 (1.733 urnas). A comparação com a anterior está em
  saida/versoes_18out.csv, gerada nesse commit;
- 5e55ef8: cadastro gerado em 18/10, 20h27 (1.025 urnas). A comparação com a anterior está em
  saida/versoes_18out_noite.csv, gerada no commit 917ba7a;
- e8cf919: cadastro gerado em 19/10, 11h27 (596 urnas). A comparação com a anterior está em
  saida/versoes_19out.csv, gerada no commit 4925b73;
- da7f1cc: cadastro gerado em 19/10, 15h27 (475 urnas). A comparação com a anterior está em
  saida/versoes_19out_tarde.csv, gerada no commit 6804293;
- atual: o cadastro em dados/eleitorado_local_votacao_2026.zip.
A versão anterior, a atual e o nome da saída vêm de versoes.py.
Para cada urna que está em uma das duas listas, compara o local do 1º e do 2º turno nas duas versões, pelo número,
pelo nome e pelo endereço. Os locais da versão anterior vêm do zip dela em dados/anteriores/ (as urnas que entraram
não estão na lista anterior); sem o zip, só os da lista anterior, no git.

Uso: python -P scripts/07_versoes.py (depois de 02_mudancas.py)
Saída: saida/<último arquivo de versoes.VERSOES>
"""
import importlib
import io
import subprocess
import zipfile
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ibge  # noqa: E402
from versoes import VERSOES, sufixo  # noqa: E402

(_, COMMIT_ANTES, _), (_, _, SAIDA_CSV) = VERSOES[-2], VERSOES[-1]
ANTES, AGORA = sufixo(VERSOES[-2][0]), sufixo(VERSOES[-1][0])  # sufixos: data e hora do cadastro
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
LOCAIS = ["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2", "NM_LOCAL_VOTACAO_2"]
ENDERECOS = ["DS_ENDERECO", "DS_ENDERECO_2"]


def git(arquivo):
    return io.BytesIO(subprocess.run(["git", "show", f"{COMMIT_ANTES}:saida/{arquivo}"], cwd=RAIZ,
                                     capture_output=True, check=True).stdout)


def locais_anteriores():
    """Local do 1º e do 2º turno de cada urna no zip da versão anterior (seção principal; repetida: a primeira)."""
    zp = importlib.import_module("02_mudancas").anterior_2026()
    if zp is None:
        print("AVISO: sem o zip da versão anterior em dados/anteriores/; as urnas que entraram ficam sem comparação")
        return None
    with zipfile.ZipFile(zp) as z, z.open(next(n for n in z.namelist() if n.endswith("_BRASIL.csv"))) as f:
        d = pd.read_csv(f, sep=";", encoding="latin1", dtype=str,
                        usecols=["NR_TURNO", "CD_TIPO_SECAO_AGREGADA", "NM_MUNICIPIO"] + URNA + LOCAIS[:2] + ENDERECOS[:1])
    d = d[(d.SG_UF != "ZZ") & (d.CD_TIPO_SECAO_AGREGADA == "1")]
    for c in ["NR_TURNO"] + URNA[1:] + ["NR_LOCAL_VOTACAO"]:
        d[c] = pd.to_numeric(d[c])
    d = d.drop_duplicates(["NR_TURNO"] + URNA).set_index(URNA)
    t1, t2 = d[d.NR_TURNO == 1], d[d.NR_TURNO == 2]
    return (t1[["NM_MUNICIPIO", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO"]]
            .join(t2[["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO"]].add_suffix("_2"), how="inner"))


def mudou(v, cols):
    """O local mudou entre as versões em alguma das colunas (número, nome ou endereço, sem diferença de grafia)."""
    return pd.concat([v[f"{c}_{ANTES}"].map(ibge.norm) != v[f"{c}_{AGORA}"].map(ibge.norm) for c in cols], axis=1).any(axis=1)


def main():
    lista_antes = pd.read_csv(git("urnas_mudadas_2026.csv")).set_index(URNA)
    cols = ["NM_MUNICIPIO", "tipo", "mudou", "aptos"] + LOCAIS + ENDERECOS
    agora = pd.read_csv(SAIDA / "urnas_2026.csv.gz", usecols=URNA + cols).set_index(URNA)
    antes = lista_antes.reindex(columns=cols)
    if (cad := locais_anteriores()) is not None:  # as que não estavam na lista, com os locais do cadastro anterior
        antes = pd.concat([antes, cad.loc[cad.index.difference(antes.index)]])
    chaves = lista_antes.index.union(agora.index[agora.mudou])
    v = (antes.reindex(chaves)[["NM_MUNICIPIO", "tipo", "aptos"] + LOCAIS + ENDERECOS].add_suffix(f"_{ANTES}")
         .join(agora.reindex(chaves)[["tipo", "mudou"] + LOCAIS + ENDERECOS].add_suffix(f"_{AGORA}")))
    v["situacao"] = "nas duas versões"
    v.loc[~v[f"mudou_{AGORA}"].fillna(False).astype(bool), "situacao"] = "saiu da lista"
    v.loc[~v.index.isin(lista_antes.index), "situacao"] = "entrou na lista"
    mudou_1t = mudou(v, ["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO"])
    mudou_2t = mudou(v, ["NR_LOCAL_VOTACAO_2", "NM_LOCAL_VOTACAO_2", "DS_ENDERECO_2"])
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
