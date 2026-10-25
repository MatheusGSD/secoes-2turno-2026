"""Confere o texto da página e do README depois de cada versão do cadastro, antes do commit.

18_texto.py preenche os números marcados. Este script procura o que ele não alcança:
1. marcadores desatualizados: o valor escrito difere do que 18_texto.py calcularia agora (alguém esqueceu de rodá-lo,
   ou rodou antes de um script que mudou as saídas);
2. números da versão anterior que ficaram no texto fora dos marcadores: os valores de saida/texto.json no commit da
   versão anterior (versoes.py) que mudaram e ainda aparecem no texto corrido, e o rótulo do cadastro anterior
   ("21/10, 11h27"). Ficam de fora o histórico (o <details id="det-atualizacao">, as linhas de tabela class="antiga")
   e os trechos marcados como história com <!--h-->...<!--/h-->. Um achado aqui ou é um número esquecido, ou é
   história: nesse caso, marque o trecho com <!--h--> para que não volte a aparecer;
3. regras de interpretação: frases que dependem de um número passar de um limite (um intervalo incluir o zero, a
   ordem dos estados, o sinal de um efeito). Se uma regra falha, a frase indicada precisa ser reescrita à mão;
4. o checklist do que continua manual (CHECKLIST.md), para não esquecer.

Uso: python -P scripts/19_conferir.py (depois de 18_texto.py). Sai com código 1 se algum dos três primeiros itens
encontrou problema.
"""
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import VERSOES  # noqa: E402

texto = importlib.import_module("18_texto")
ARQUIVOS = [texto.PAGINA, texto.README]


def git(ref):
    r = subprocess.run(["git", "show", ref], cwd=RAIZ, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def corrido(t, arquivo):
    """O texto fora dos marcadores, do histórico, dos scripts e dos estilos, com o número da linha de cada trecho."""
    apagar = [r"<!--n:[a-z0-9_]+-->.*?<!--/n-->", r"<!--g:([a-z0-9_]+)-->.*?<!--/g:\1-->", r"<!--h-->.*?<!--/h-->",
              r"<script.*?</script>", r"<style.*?</style>", r'<details id="det-atualizacao">.*?</details>',
              r'<tr class="antiga">.*?</tr>', r"<head>.*?</head>"]
    if arquivo == texto.README:  # no README, o histórico são os parágrafos "Atualização de ..." e a tabela de versões
        apagar += [r"\*\*Atualização de .*?(?=\n\n)", r"\n\|.*?\|(?=\n)"]
    for a in apagar:
        t = re.sub(a, lambda m: re.sub(r"[^\n]", " ", m.group(0)), t, flags=re.S)  # mantém as linhas
    return t


def procurar(t, valor):
    """Ocorrências de um valor como número inteiro (não dentro de outro número)."""
    v = re.escape(valor)
    return [t.count("\n", 0, m.start()) + 1 for m in re.finditer(rf"(?<![\d.,]){v}(?![\d]|,\d|\.\d)", t)]


def marcadores(v, blocos):
    erros = []
    for arq in ARQUIVOS:
        t = arq.read_text(encoding="utf-8")
        for k, valor in texto.N.findall(t):
            if k in v and v[k] != valor:
                erros.append(f"{arq.name}: <!--n:{k}--> diz '{valor}', o certo agora é '{v[k]}' (rode 18_texto.py)")
        for m in texto.G.finditer(t):
            k = m.group(1)
            if k in blocos and m.group(0) != f"<!--g:{k}-->\n{blocos[k]}\n<!--/g:{k}-->":
                erros.append(f"{arq.name}: bloco {k} desatualizado (rode 18_texto.py)")
    return erros


def sobras(v):
    """Valores da versão anterior que mudaram e ainda aparecem fora dos marcadores."""
    rot_ant, commit_ant, _ = VERSOES[-2]
    antes = git(f"{commit_ant}:saida/texto.json") if commit_ant else None
    if antes:
        antes = json.loads(antes)
    else:  # versão anterior a este script: os números principais, do numeros.json daquele commit
        n = json.loads(git(f"{commit_ant}:saida/numeros.json"))
        m = n["mudadas"]
        antes = {"urnas": texto.inteiro(m["urnas"]), "aptos_mil": texto.mil(m["aptos"]),
                 "teto_votos": texto.inteiro(m["teto_votos"]), "municipios": texto.inteiro(m["municipios"])}
        print(f"(sem saida/texto.json no commit {commit_ant}: conferindo só {', '.join(antes)})")
    # valores curtos ("126", "0,02") aparecem por acaso em número de seção e em intervalos antigos: só o total de urnas
    # entra mesmo curto. Datas e rótulos de versão ("21/10", "21/10, 15h27") no texto citam versões passadas; o rótulo
    # da anterior é conferido abaixo
    suspeitos = {k: a for k, a in antes.items() if k in v and a != v[k] and re.search(r"\d", a)
                 and (len(a) >= 5 or k == "urnas") and not re.fullmatch(r"\d\d/\d\d(, \d{1,2}h\d\d)?", a)}
    achados = []
    for arq in ARQUIVOS:
        t = corrido(arq.read_text(encoding="utf-8"), arq)
        linhas = arq.read_text(encoding="utf-8").split("\n")
        for k, a in sorted(suspeitos.items()):
            for ln in procurar(t, a):
                achados.append(f"{arq.name}:{ln}: '{a}' era {k} na versão de {rot_ant} (agora '{v[k]}'): "
                               f"…{trecho(linhas[ln - 1], a)}…")
        for ln in procurar(t, rot_ant):
            achados.append(f"{arq.name}:{ln}: cita o cadastro anterior, {rot_ant}: …{trecho(linhas[ln - 1], rot_ant)}…")
    return achados


def trecho(linha, valor, folga=70):
    i = linha.find(valor)
    return re.sub(r"<[^>]+>", "", linha[max(0, i - folga): i + len(valor) + folga]).strip()


NOME_REESCRITO = "mesmo prédio, nome e endereço reescritos no cadastro"  # de 02_mudancas.py


def municipios(arquivo, coluna, valor):
    u = __import__("pandas").read_csv(arquivo)
    return set(u[u[coluna] == valor].NM_MUNICIPIO)


def regras():
    """Cada regra: (vale?, frase que depende dela)."""
    n = json.loads((SAIDA / "numeros.json").read_text(encoding="utf-8"))
    ren = json.loads((SAIDA / "renovadas.json").read_text(encoding="utf-8"))
    geo = json.loads((SAIDA / "geografia.json").read_text(encoding="utf-8"))
    ab = json.loads((SAIDA / "abstencao_1t.json").read_text(encoding="utf-8"))
    web = json.loads((RAIZ / "docs" / "dados.json").read_text(encoding="utf-8"))
    m, nac, vz, s22 = n["mudadas"], n["nacional"], n["voto_vs_vizinhas"], n["sensibilidade_2022"]
    pri = n["impacto"][n["principal"]]
    pl = {x["ef"]: x for x in web["por_local"] if x["lista"].startswith("urnas")}
    fx = [x for x in web["por_local_faixas"] if x["lista"].startswith("urnas") and x["painel"] == "país"]
    log02 = (SAIDA / "log_02.txt").read_text(encoding="utf-8")
    ufs = {u["uf"]: u for u in ren["ufs"]}
    inclui = lambda lo, hi: lo <= 0 <= hi  # noqa: E731
    return [
        (m["pct_lula"] > nac["pct_lula"], "Quem vota: 'votaram mais em Lula que o resto do país'"),
        (m["abst"] > nac["abst"], "Quem vota: 'A abstenção foi um pouco maior que a do país'"),
        (inclui(vz["ic_baixo"], vz["ic_alto"]), "Quem vota: 'A diferença fica dentro da margem de erro' (urna a urna)"),
        (all(inclui(*pl[e]["ic"]) for e in ("estado", "município")),
         "Por local: 'dentro do estado e do município, não aparece' / 'não é estatisticamente significativa'"),
        (pl["nenhum"]["ic"][1] < 0.05, "Cartão 10 (10_imagem_por_local.py): subtítulo 'No país, pouco'"),
        (inclui(*pl["nenhum"]["ic"]), "Por local: 'a última delas a de 25/10, 6h28; com a lista atual, ..., por pouco' (página)"
         " e 'voltou a ter intervalo que inclui o zero' (README, 25/10, 11h29)"),
        (m["pct_lula"] - geo["2026"]["lula_esperado_pelo_municipio"] < 1.5,
         "Geografia: 'em 2026, perto do esperado pelo município'"),
        (inclui(s22[n["principal"]]["ic_baixo"], s22[n["principal"]]["ic_alto"]),
         "Impacto: 'uma diferença que não se distingue de zero' (2022)"),
        (s22["zona"]["ic_alto"] < 0 and inclui(s22["local_cadastro"]["ic_baixo"], s22["local_cadastro"]["ic_alto"]),
         "Impacto: 'só a mesma zona ... o único intervalo que não inclui o zero, no sentido de menos abstenção'"),
        (all(s22[b]["ic_baixo"] <= 0 for b in s22), "Impacto: 'nenhum mostra abstenção maior'"),
        (s22[n["principal"]]["volta_pp"] < 0 and s22[n["principal"]]["sai_pp"] < 0,
         "Impacto: 'abstenção ... ponto menor nas urnas que voltam ... e ... menor nas que saem'"),
        (max(abs(x) for x in pri["margem_previsao"]) < 0.0001 * nac["margem_votos"],
         "Impacto: faixa de previsão 'ainda menos de 0,01% da diferença nacional'"),
        (ab["nivel_2026"]["ic"][0] > 0 and ab["variacao_desde_2022"]["ic"][0] > 0
         and inclui(*ab["nivel_2022_mesmas_urnas"]["ic"]), "Abstenção no 1º turno: 'compatível com um efeito pequeno'"),
        (ab["sensibilidade_2t"]["margem"] > 0, "Impacto: 'a vantagem de Flávio cresceria' (com o efeito de 2026)"),
        (m["pessimista_votos"] > 0, "Impacto: 5 pontos, 'a vantagem de Flávio cresceria'"),
        (m["teto_votos"] > 0, "Impacto e quadro: cenário extremo 'Lula perderia ... vantagem dele ali' / 'de Lula, em todas as versões'"),
        (municipios(SAIDA / "urnas_reescritas_2026.csv", "tipo", NOME_REESCRITO) == {"TRACUATEUA", "BRAGANÇA"},
         "Quando o cadastro não bate: nome e endereço reescritos 'todas na zona 13 do Pará' (Tracuateua e Bragança)"),
        (municipios(SAIDA / "urnas_mudadas_2026.csv", "nome_parecido", True) == {"JACARACI", "BRAGANÇA"},
         "Quando o cadastro não bate: nome parecido '4 em Jacaraci (BA) ... e 3 em Bragança (PA)'"),
        (m["reescritas_urnas"] == 0, "Quando o cadastro não bate e Como foi feito: 'No cadastro atual, nenhuma urna está nesse caso'"),
        ("só renumerada: 0 " in log02, "Como foi feito: '(só renumerada; nenhuma urna no cadastro atual)'"),
        (max(ufs, key=lambda u: ufs[u]["renovadas"]) == "PR", "Como a lista encolheu: 'o Paraná, o que tem mais'"),
        (ren["predios_divididos"] == 0, "Como a lista encolheu: 'Nenhum prédio provisório ficou dividido'"),
        (min(fx, key=lambda r: r["pct"])["faixa"] == "menos de 30%",
         "Por local e cartão 10: 'os locais onde Lula teve menos de 30% têm a menor fração na lista'"),
        (n["fora_do_cadastro_2t"]["ja_fora_no_1t_abst"] < nac["abst"] + 1,
         "Como foi feito: abstenção nas que já estavam fora 'perto dos ... do país'"),
    ]


def main():
    v, blocos = texto.valores()
    problemas = 0
    print("1. marcadores")
    for e in marcadores(v, blocos) or ["   ok"]:
        print("  ", e)
    problemas += len(marcadores(v, blocos))
    print("\n2. números da versão anterior fora dos marcadores")
    achados = sobras(v)
    for a in achados or ["   nenhum"]:
        print("  ", a)
    problemas += len(achados)
    print("\n3. regras de interpretação")
    falhas = [frase for ok, frase in regras() if not ok]
    for f in falhas or ["   todas valem"]:
        print("   FALHOU:" if f != "   todas valem" else "", f)
    problemas += len(falhas)
    print("\n4. continua manual (CHECKLIST.md):")
    itens = re.findall(r"^- \[ \] (.*?)(?=\n- \[ \]|\n\n|\Z)", (RAIZ / "CHECKLIST.md").read_text(encoding="utf-8"), re.S | re.M)
    for item in itens:
        print("   -", re.sub(r"\s+", " ", item))
    print(f"\npendências: {problemas}")
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
