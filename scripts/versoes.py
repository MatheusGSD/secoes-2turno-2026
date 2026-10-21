"""Versões do cadastro de locais do TSE usadas na página, da mais antiga à atual.

Cada linha: data e hora de geração do cadastro (HH_GERACAO, de dentro do CSV, em Brasília), commit em que essa versão
era a atual (None na atual) e o arquivo de 07_versoes.py que a compara com a anterior (em saida/, no git daquele
commit; o da atual fica no disco). 00_atualizar.py acrescenta uma linha a cada cadastro novo; 07, 12, 14 e os cartões
leem daqui.
"""
VERSOES = [
    ("17/10, 6h28", "943ab33", None),
    ("17/10, 23h33", "fa873d1", "versoes_17_18out.csv"),
    ("18/10, 11h27", "2272612", "versoes_18out.csv"),
    ("18/10, 20h27", "5e55ef8", "versoes_18out_noite.csv"),
    ("19/10, 11h27", "e8cf919", "versoes_19out.csv"),
    ("19/10, 15h27", "da7f1cc", "versoes_19out_tarde.csv"),
    ("20/10, 6h27", "ea7023c", "versoes_20out_06h27.csv"),
    ("20/10, 11h27", "6c651e5", "versoes_20out_11h27.csv"),
    ("20/10, 12h32", "371bbe0", "versoes_20out_12h32.csv"),
    ("20/10, 15h27", "b9452ce", "versoes_20out_15h27.csv"),
    ("20/10, 20h27", "a395125", "versoes_20out_20h27.csv"),
    ("21/10, 6h27", "d1c3f30", "versoes_21out_06h27.csv"),
    ("21/10, 11h27", "90059c6", "versoes_21out_11h27.csv"),
    ("21/10, 14h19", "0f3a6a2", "versoes_21out_14h19.csv"),
    ("21/10, 15h27", None, "versoes_21out_15h27.csv"),
]
ATUAL = VERSOES[-1][0]
POR_EXTENSO = {5: "CINCO", 6: "SEIS", 7: "SETE", 8: "OITO", 9: "NOVE", 10: "DEZ", 11: "ONZE", 12: "DOZE",
               13: "TREZE", 14: "CATORZE", 15: "QUINZE", 16: "DEZESSEIS", 17: "DEZESSETE", 18: "DEZOITO",
               19: "DEZENOVE", 20: "VINTE"}


def cabecalho():
    """'CADASTRO DO TSE DE 19/10, 15H27', para o alto dos cartões."""
    return f"CADASTRO DO TSE DE {ATUAL.upper()}"


def sufixo(cadastro):
    """'19/10, 15h27' -> '19out_15h', para nomes de coluna."""
    data, hora = cadastro.split(", ")
    return f"{data.split('/')[0]}out_{hora.split('h')[0]}h"


def ref(commit, arquivo):
    """Onde ler um arquivo de saida/ de uma versão: no git, se a versão tem commit; senão, no disco."""
    return f"{commit}:saida/{arquivo}" if commit else arquivo
