"""Votos para presidente por seção, Brasil inteiro: 1º turno de 2026 e os dois turnos de 2022.

Lê os CSVs de votação por seção do TSE em dados/ (ver README). O arquivo de votos não traz aptos nem
comparecimento: comparecimento é a soma dos votos para presidente (válidos + brancos + nulos) e os
aptos vêm do cadastro de locais, em 02_mudancas.py.

Uso: python -P scripts/01_votos_1t.py
Saídas: saida/votos_{ano}_secao.csv.gz (uma linha por seção e turno, uma coluna por candidato)
        saida/candidatos_{ano}.csv
"""
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
SAIDA.mkdir(exist_ok=True)
DADOS = RAIZ / "dados"
ANOS = {
    2026: (DADOS / "votacao_secao_2026_BR.zip", "votacao_secao_2026_BR.csv", {1}),
    2022: (DADOS / "votacao_secao_2022_BR.zip", "votacao_secao_2022_BR.csv", {1, 2}),
}
BRANCO, NULOS = 95, {96, 97, 98}  # nulos = nulo + anulados
SECAO = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]


def extrair(ano):
    arquivo, membro, turnos = ANOS[ano]
    cols = SECAO + ["CD_CARGO", "NR_VOTAVEL", "NM_VOTAVEL", "QT_VOTOS"]
    pedacos = []
    with zipfile.ZipFile(arquivo) as z, z.open(membro) as f:
        for ch in pd.read_csv(f, sep=";", encoding="latin1", usecols=cols, chunksize=2_000_000,
                              dtype={"SG_UF": str}):
            for c in ["NR_TURNO", "CD_CARGO", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_VOTAVEL", "QT_VOTOS"]:
                ch[c] = pd.to_numeric(ch[c])
            pedacos.append(ch[ch.NR_TURNO.isin(turnos) & (ch.CD_CARGO == 1) & (ch.SG_UF != "ZZ")])
    v = pd.concat(pedacos, ignore_index=True)
    print(ano, "linhas de voto:", len(v), "| seções x turno:", v.groupby(SECAO).ngroups)

    cand = (v[~v.NR_VOTAVEL.isin({BRANCO} | NULOS)].groupby(["NR_TURNO", "NR_VOTAVEL", "NM_VOTAVEL"])
              .QT_VOTOS.sum().reset_index().sort_values(["NR_TURNO", "QT_VOTOS"], ascending=[True, False]))
    cand["pct"] = 100 * cand.QT_VOTOS / cand.groupby("NR_TURNO").QT_VOTOS.transform("sum")
    cand.to_csv(SAIDA / f"candidatos_{ano}.csv", index=False)
    print(cand.to_string(index=False))

    v["col"] = v.NR_VOTAVEL.map(lambda n: "brancos" if n == BRANCO else "nulos" if n in NULOS else f"c{n}")
    sec = v.pivot_table(index=SECAO, columns="col", values="QT_VOTOS", aggfunc="sum", fill_value=0)
    cands = [c for c in sec.columns if c[1:].isdigit()]
    sec["validos"] = sec[cands].sum(axis=1)
    sec["comparecimento"] = sec.validos + sec.brancos + sec.nulos
    sec = sec.reset_index()
    sec.to_csv(SAIDA / f"votos_{ano}_secao.csv.gz", index=False)
    print(sec.groupby("NR_TURNO")[["comparecimento", "validos"]].sum())


def main():
    for ano in ANOS:
        extrair(ano)


if __name__ == "__main__":
    main()
