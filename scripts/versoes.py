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
    ("21/10, 15h27", "d4e83d3", "versoes_21out_15h27.csv"),
    ("21/10, 20h28", "50fa582", "versoes_21out_20h28.csv"),
    ("22/10, 6h28", "17f4ce6", "versoes_22out_06h28.csv"),
    ("22/10, 11h27", "f287d0c", "versoes_22out_11h27.csv"),
    ("22/10, 15h27", "ace92f5", "versoes_22out_15h27.csv"),
    ("22/10, 20h28", "1412e2e", "versoes_22out_20h28.csv"),
    ("23/10, 6h27", "ee712d0", "versoes_23out_06h27.csv"),
    ("23/10, 10h00", "b651268", "versoes_23out_10h00.csv"),
    ("23/10, 10h47", "38c332d", "versoes_23out_10h47.csv"),
    ("23/10, 11h27", "ae60a3c", "versoes_23out_11h27.csv"),
    ("23/10, 15h28", "5df7b5f", "versoes_23out_15h28.csv"),
    ("23/10, 20h28", "6606e76", "versoes_23out_20h28.csv"),
    ("24/10, 6h27", "957dec4", "versoes_24out_06h27.csv"),
    ("24/10, 11h27", "7abb655", "versoes_24out_11h27.csv"),
    ("24/10, 15h28", "c40ade6", "versoes_24out_15h28.csv"),
    ("24/10, 20h27", None, "versoes_24out_20h27.csv"),
]
ATUAL = VERSOES[-1][0]
POR_EXTENSO = {5: "CINCO", 6: "SEIS", 7: "SETE", 8: "OITO", 9: "NOVE", 10: "DEZ", 11: "ONZE", 12: "DOZE",
               13: "TREZE", 14: "CATORZE", 15: "QUINZE", 16: "DEZESSEIS", 17: "DEZESSETE", 18: "DEZOITO",
               19: "DEZENOVE", 20: "VINTE", 21: "VINTE E UMA", 22: "VINTE E DUAS", 23: "VINTE E TRÊS",
               24: "VINTE E QUATRO", 25: "VINTE E CINCO", 26: "VINTE E SEIS", 27: "VINTE E SETE",
               28: "VINTE E OITO", 29: "VINTE E NOVE", 30: "TRINTA", 31: "TRINTA E UMA", 32: "TRINTA E DUAS",
               33: "TRINTA E TRÊS", 34: "TRINTA E QUATRO", 35: "TRINTA E CINCO"}


def cabecalho():
    """'CADASTRO DO TSE DE 19/10, 15H27', para o alto dos cartões."""
    return f"CADASTRO DO TSE DE {ATUAL.upper()}"


def sufixo(cadastro):
    """'19/10, 15h27' -> '19out_15h27', para nomes de coluna. Com os minutos desde 23/10, quando vieram dois cadastros
    na mesma hora (10h00 e 10h47); os CSVs de antes têm só a hora ('19out_15h')."""
    data, hora = cadastro.split(", ")
    return f"{data.split('/')[0]}out_{hora}"


def ref(commit, arquivo):
    """Onde ler um arquivo de saida/ de uma versão: no git, se a versão tem commit; senão, no disco."""
    return f"{commit}:saida/{arquivo}" if commit else arquivo
