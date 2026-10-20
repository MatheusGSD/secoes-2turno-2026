"""A situação de cada urna em cada versão do cadastro, para os gráficos animados da evolução da lista.

Para cada urna que esteve na lista em alguma versão (versoes.py), a situação em cada uma: "volta" (volta ao local de
sempre), "sai" (sai do local de sempre ou troca de prédio provisório), "predio" (o local de sempre muda de prédio) ou
null (fora da lista). As listas das versões anteriores vêm do git; a da atual, de saida/. A coordenada é a do prédio
do 1º turno (ou a do 2º, se a do 1º falta). Também guarda, por versão, o número de urnas e o efeito estimado.

Uso: python -P scripts/16_evolucao.py   (depois de 02 e 03; precisa do histórico completo do git)
Saída: docs/evolucao.json
"""
import io
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import VERSOES  # noqa: E402

URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
SITUACAO = {"voltou ao local de cadastro": "volta", "saiu do local de cadastro": "sai", "trocou de local provisório": "sai",
            "local de sempre em outro prédio": "predio"}
PERDIDA_DEPOIS_DE = "19/10, 15h27"  # versão publicada na noite de 19/10 e substituída antes de ser baixada


def ler(commit, arquivo):
    if commit is None:
        return (RAIZ / "saida" / arquivo).read_bytes()
    return subprocess.run(["git", "show", f"{commit}:saida/{arquivo}"], cwd=RAIZ, capture_output=True, check=True).stdout


def main():
    listas, versoes = [], []
    for rot, commit, _ in VERSOES:
        m = pd.read_csv(io.BytesIO(ler(commit, "urnas_mudadas_2026.csv")))
        m["sit"] = m.tipo.map(SITUACAO)
        if m.sit.isna().any():
            sys.exit(f"tipo sem situação em {rot}: {m[m.sit.isna()].tipo.unique()}")
        listas.append(m)
        n = json.loads(ler(commit, "numeros.json"))
        imp = n["impacto"][n["principal"]]
        versoes.append({"rot": rot, "urnas": n["mudadas"]["urnas"], "margem": round(imp["margem"], 3),
                        "ic": [round(v, 3) for v in imp["margem_ic"]]})

    # a última aparição de cada urna traz os dados mais recentes (local do 1º turno e votos não mudam entre versões)
    base = pd.concat(listas).drop_duplicates(URNA, keep="last")[
        URNA + ["NM_MUNICIPIO", "NR_LOCAL_VOTACAO", "lat", "lon", "lat_2", "lon_2", "aptos"]]
    for i, m in enumerate(listas):
        base = base.merge(m[URNA + ["sit"]].rename(columns={"sit": f"v{i}"}), on=URNA, how="left")
    base["x"], base["y"] = base.lon.fillna(base.lon_2), base.lat.fillna(base.lat_2)
    cols = [f"v{i}" for i in range(len(listas))]
    urnas = [{"uf": r.SG_UF, "mun": r.NM_MUNICIPIO, "local": int(r.NR_LOCAL_VOTACAO), "aptos": int(r.aptos),
              "xy": None if pd.isna(r.x) else [round(r.x, 4), round(r.y, 4)],
              "s": [None if pd.isna(getattr(r, c)) else getattr(r, c) for c in cols]} for r in base.itertuples()]
    conta = [sum(u["s"][i] is not None for u in urnas) for i in range(len(versoes))]
    if conta != [v["urnas"] for v in versoes]:
        sys.exit(f"contagem por versão não fecha: {conta} x {[v['urnas'] for v in versoes]}")
    res = {"versoes": versoes, "perdida_depois_de": PERDIDA_DEPOIS_DE, "urnas": urnas}
    (RAIZ / "docs" / "evolucao.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(urnas), "urnas em alguma versão | por versão:", conta, "| sem coordenada:", sum(u["xy"] is None for u in urnas))


if __name__ == "__main__":
    main()
