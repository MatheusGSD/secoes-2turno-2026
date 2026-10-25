"""Os números do texto da página e do README, preenchidos a partir das saídas dos scripts.

O texto é escrito à mão, mas todo número que descreve a lista atual fica entre marcadores, e este script o reescreve
a cada versão do cadastro. Assim nenhum número do estado atual fica para trás quando a lista muda.
- <!--n:chave-->407<!--/n-->: um número ou trecho curto (na página e no README);
- <!--g:chave-->...<!--/g:chave-->: um bloco inteiro gerado (linhas de tabela, a barra das quatro situações);
- <meta name="versao-dados" content="...">: a versão nos endereços dos JSON, para o cache não misturar versões.
O que fica de fora dos marcadores é história (o que mudou em cada versão) ou interpretação, e continua à mão: o
CHECKLIST.md diz o que conferir e 19_conferir.py procura números da versão anterior que tenham ficado no texto.

Cada chave vem de uma conta abaixo; uma chave usada no texto e que não existe aqui faz o script parar. Os números
de cada versão anterior vêm do numeros.json daquela versão, no git (versoes.py).

Uso: python -P scripts/18_texto.py (depois de todos os outros; 00_atualizar.py roda na ordem)
Saídas: docs/index.html e README.md reescritos nos marcadores; saida/texto.json com todos os valores
"""
import io
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from versoes import VERSOES  # noqa: E402

PAGINA, README = RAIZ / "docs" / "index.html", RAIZ / "README.md"
URNA = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
URNAS_PAIS = 499248  # urnas do país com o exterior, como o TSE conta
CARDINAIS = ("zero um dois três quatro cinco seis sete oito nove dez onze doze treze catorze quinze dezesseis "
             "dezessete dezoito dezenove vinte").split()
ORDINAIS = ["", "primeira", "segunda", "terceira", "quarta", "quinta", "sexta", "sétima", "oitava", "nona", "décima"]
NOME_UF = {"AC": "no Acre", "AL": "em Alagoas", "AP": "no Amapá", "AM": "no Amazonas", "BA": "na Bahia",
           "CE": "no Ceará", "DF": "no Distrito Federal", "ES": "no Espírito Santo", "GO": "em Goiás",
           "MA": "no Maranhão", "MT": "em Mato Grosso", "MS": "em Mato Grosso do Sul", "MG": "em Minas Gerais",
           "PA": "no Pará", "PB": "na Paraíba", "PR": "no Paraná", "PE": "em Pernambuco", "PI": "no Piauí",
           "RJ": "no Rio de Janeiro", "RN": "no Rio Grande do Norte", "RS": "no Rio Grande do Sul", "RO": "em Rondônia",
           "RR": "em Roraima", "SC": "em Santa Catarina", "SP": "em São Paulo", "SE": "em Sergipe", "TO": "no Tocantins"}
NORTE = set("AC AM AP PA RO RR TO".split())
GOV_2T = ["AC", "AM", "DF", "ES", "RN", "TO"]  # estados com 2º turno para governador em 2026 (o RJ não terá)
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
# linhas fixas da tabela de fontes: as do TSE, com a data de cada uma (as versões desta página entram pela data)
FONTES_TSE = [
    ("16/10, 0h00", "TSE, número divulgado em 16/10", "Critério não informado", "4.352 seções", "0,87%"),
    ("17/10, 6h28", "Painel do TSE, atualização de 17/10, 6h28",
     "Local do 2º turno × local <strong>de cadastro</strong> da seção", "4.863", "0,97%"),
    ("18/10, 7h09", "Painel do TSE, atualização de 18/10, 7h09",
     "Local do 2º turno × local <strong>do 1º turno</strong>, pelo número ou pelo nome do local", "2.023", "0,41%"),
    ("19/10, 11h28", "Painel do TSE, atualização de 19/10, 11h27",
     "Seções que mudaram de endereço ou de local entre o 1º e o 2º turno", "554 seções", "0,11%"),
]


# --- formatação, em português ---------------------------------------------------------------------------------
def inteiro(x):
    return f"{round(x):,}".replace(",", ".")


def dec(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sinal(x, casas=1):
    """+0,5 / −0,9 / 0,0, com o sinal de menos tipográfico."""
    s = dec(abs(x), casas)
    if s.strip("0,") == "":
        return s
    return ("+" if x > 0 else "−") + s


def votos(x):
    """−11 / +4 / 0, em votos."""
    r = round(x)
    return "0" if r == 0 else ("+" if r > 0 else "−") + inteiro(abs(r))


def fino(x):
    """Com duas casas; com três ou quatro quando duas dariam zero (−0,003, e não 0,00, num limite de intervalo)."""
    for casas in (2, 3, 4):
        if round(abs(x), casas) > 0:
            return sinal(x, casas)
    return sinal(x, 2)


def ponto(x):
    """Diferença em pontos com uma casa; com duas quando uma casa daria zero."""
    return sinal(x, 2) if round(abs(x), 1) == 0 and round(abs(x), 2) > 0 else sinal(x, 1)


def pct(x, casas=None):
    """Percentual com uma casa (duas abaixo de 1%, se não, o número some)."""
    if casas is None:
        casas = 1 if x >= 1 else 2
    return dec(x, casas) + "%"


def mil(x):
    """126 mil / 2,0 milhões / 800."""
    if x >= 1e6:
        return dec(x / 1e6, 1) + (" milhão" if round(x / 1e6, 1) < 2 else " milhões")
    return f"{inteiro(x / 1000)} mil" if x >= 1000 else inteiro(x)


def arred(x, passo):
    return int(round(x / passo) * passo)


def cardinal(n):
    return CARDINAIS[n] if n < len(CARDINAIS) else inteiro(n)


def ordinal(n):
    """Feminino, por extenso: 'décima quarta'."""
    if n <= 10:
        return ORDINAIS[n]
    if n < 20:
        return "décima " + ORDINAIS[n - 10]
    dezena = "vigésima" if n < 30 else "trigésima"
    return dezena + ("" if n % 10 == 0 else " " + ORDINAIS[n % 10])


def lista(itens):
    itens = list(itens)
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]


def hora_por_extenso(rot):
    """'21/10, 14h19' -> '21/10 às 14h19'."""
    return rot.replace(", ", " às ")


def cadastros_por_dia(rotulos):
    """['18/10, 11h27', '18/10, 20h27', '19/10, 11h27'] -> '18/10, 11h27 e 20h27; e de 19/10, 11h27' (vem depois de 'de')."""
    dias = {}
    for r in rotulos:
        d, h = r.split(", ")
        dias.setdefault(d, []).append(h)
    partes = [f"{d}, {lista(hs)}" for d, hs in dias.items()]
    return partes[0] if len(partes) == 1 else "; de ".join(partes[:-1]) + "; e de " + partes[-1]


def chave(rot):
    """'18/10, 7h09' -> (10, 18, 7, 9), para ordenar."""
    d, h = rot.split(", ")
    hh, mm = h.split("h")
    return (int(d.split("/")[1]), int(d.split("/")[0]), int(hh), int(mm or 0))


# --- leitura ----------------------------------------------------------------------------------------------------
def git(ref):
    return subprocess.run(["git", "show", ref], cwd=RAIZ, capture_output=True, check=True).stdout


def ler_json(nome, commit=None):
    return json.loads(git(f"{commit}:saida/{nome}")) if commit else json.loads((SAIDA / nome).read_text(encoding="utf-8"))


def valores():
    n = ler_json("numeros.json")
    m, imp = n["mudadas"], n["impacto"]
    pri = imp[n["principal"]]
    ren, geo, ab = ler_json("renovadas.json"), ler_json("geografia.json"), ler_json("abstencao_1t.json")
    web = json.loads((RAIZ / "docs" / "dados.json").read_text(encoding="utf-8"))
    dist = web["distancia"]
    mud = pd.read_csv(SAIDA / "urnas_mudadas_2026.csv")
    tipos = {t["tipo"]: t["urnas"] for t in n["tipos"]}
    v = {}

    # versões
    rotulos = [r for r, _, _ in VERSOES]
    atual = rotulos[-1]
    nv = len(VERSOES)
    v["cadastro"] = atual
    v["cadastro_extenso"] = hora_por_extenso(atual)
    v["cadastro_dia"] = atual.split(", ")[0]
    v["atualizado"] = f"{date.today():%d/%m}"
    v["n_versoes"] = cardinal(nv)
    v["versao_atual_ordinal"] = ordinal(nv)
    v["primeira_data"], v["ultima_data"] = rotulos[0].split(", ")[0], v["cadastro_dia"]
    depois_painel = [r for r in rotulos if chave(r) > chave("18/10, 7h09")]
    v["n_cadastros_depois_do_painel"] = cardinal(len(depois_painel))
    v["cadastros_depois_do_painel"] = cadastros_por_dia(depois_painel)
    automaticas = rotulos[rotulos.index("20/10, 11h27"):]
    v["versoes_automaticas"] = cadastros_por_dia(automaticas)
    v["versoes_por_extenso"] = "; ".join(
        (f"a {ordinal(i + 1)} versão desta página usou o cadastro gerado em {hora_por_extenso(r)}" if i == 0
         else f"a {ordinal(i + 1)}, o gerado em {hora_por_extenso(r)}") for i, r in enumerate(rotulos[:-1]))
    v["versoes_por_extenso"] = v["versoes_por_extenso"][0].upper() + v["versoes_por_extenso"][1:]
    hist = []
    for rot, commit, _ in VERSOES:
        nn = ler_json("numeros.json", commit)
        hist.append({"rot": rot, "n": nn})
    v["serie_urnas"] = lista(inteiro(h["n"]["mudadas"]["urnas"]) for h in hist)
    v["serie_lula"] = "; ".join(f"{dec(h['n']['mudadas']['pct_lula'])}% nas {inteiro(h['n']['mudadas']['urnas'])}"
                                f"{' urnas' if i == 0 else ''} de {h['rot']}" for i, h in enumerate(hist[3:-1]))
    maior_ic = max(max(abs(x) for x in h["n"]["impacto"][h["n"]["principal"]]["margem_ic"]) for h in hist)
    v["teto_ic_versoes"] = inteiro(-(-maior_ic // 10) * 10)
    v["versao_anterior_urnas"] = inteiro(hist[-2]["n"]["mudadas"]["urnas"])
    v["versao_anterior"] = rotulos[-2]
    d, h = atual.split(", ")
    v["versao_meta"] = f"{d.split('/')[0]}out{h.replace('h', '')}"

    # topo
    v["urnas"] = inteiro(m["urnas"])
    v["pct_urnas_pais"] = pct(100 * m["urnas"] / URNAS_PAIS)
    v["aptos_mil"] = mil(m["aptos"])
    v["municipios"] = inteiro(m["municipios"])
    v["ufs"] = inteiro(m["ufs"])
    v["pct_validos_pais"] = pct(m["pct_validos_pais"])
    outras = [imp[b] for b in imp if b != n["principal"]]
    lo = min(min(x["margem_ic"][0] for x in outras), pri["margem_ic"][0])
    hi = max(max(x["margem_ic"][1] for x in outras), pri["margem_ic"][1])
    v["faixa_comparacoes"] = f"entre {inteiro(abs(lo))} votos a menos e {inteiro(hi)} a mais" if lo < 0 < hi else \
        f"entre {votos(lo)} e {votos(hi)} votos"
    v["outras_comparacoes"] = f"{votos(min(x['margem_ic'][0] for x in outras))} e {votos(max(x['margem_ic'][1] for x in outras))}"

    # efeito
    v["margem"] = votos(pri["margem"])
    v["margem_ic"] = f"{votos(pri['margem_ic'][0])} e {votos(pri['margem_ic'][1])}"
    v["margem_previsao"] = f"{votos(pri['margem_previsao'][0])} a {votos(pri['margem_previsao'][1])}"
    v["eleitores_a_mais"] = inteiro(arred(pri["eleitores_a_mais"], 10))
    lo_e, hi_e = pri["eleitores_ic"]
    v["eleitores_ic"] = (f"{inteiro(arred(-lo_e, 10))} a menos a {inteiro(arred(hi_e, 10))} a mais" if lo_e < 0
                         else f"{inteiro(arred(lo_e, 10))} a {inteiro(arred(hi_e, 10))} a mais")
    maior_e = max(max(abs(x) for x in imp[b]["eleitores_ic"]) for b in imp)
    v["eleitores_max"] = inteiro(arred(maior_e, 50))
    v["eleitores_max_pct"] = pct(100 * maior_e / n["nacional"]["margem_votos"])
    v["teto_votos"] = inteiro(m["teto_votos"])
    v["teto_pct"] = pct(m["teto_pct_margem"])
    v["outros_votos"] = mil(m["outros"]) if m["outros"] >= 1000 else inteiro(m["outros"])
    v["pessimista_votos"] = inteiro(arred(m["pessimista_votos"], 10))
    s22 = n["sensibilidade_2022"]
    limites = [(s22[b]["ic_alto"], "todas") for b in s22] + \
              [(s22[b][f"{g}_ic"][1], g) for b in s22 for g in ("volta", "sai")]
    v["maior_limite_2022"] = dec(max(limites)[0], 2)
    sp = s22[n["principal"]]
    v["efeito_2022"] = f"{dec(abs(sp['efeito_pp']), 2)} ponto {'a menos' if sp['efeito_pp'] < 0 else 'a mais'}"
    v["efeito_2022_ic"] = f"{dec(-sp['ic_baixo'], 2)} a menos a {dec(sp['ic_alto'], 2)} a mais" if sp["ic_baixo"] < 0 < sp["ic_alto"] else \
        f"{sinal(sp['ic_baixo'], 2)} a {sinal(sp['ic_alto'], 2)}"
    v["efeito_2022_volta"], v["efeito_2022_sai"] = dec(abs(sp["volta_pp"]), 2), dec(abs(sp["sai_pp"]), 2)
    z, lc = s22["zona"], s22["local_cadastro"]
    v["sens_zona"] = f"{dec(abs(z['efeito_pp']), 2)} ponto {'a menos' if z['efeito_pp'] < 0 else 'a mais'}"
    v["sens_local"] = f"{dec(abs(lc['efeito_pp']), 2)} {'a menos' if lc['efeito_pp'] < 0 else 'a mais'}"
    v["sens_zona_ic"] = f"{sinal(z['ic_baixo'], 2)} a {sinal(z['ic_alto'], 2)}"
    v["sens_local_ic"] = f"{sinal(lc['ic_baixo'], 2)} a {sinal(lc['ic_alto'], 2)}"
    s2t = ab["sensibilidade_2t"]
    v["sens_2t_urnas"] = inteiro(s2t["urnas"])
    v["sens_2t_margem"] = votos(s2t["margem"])
    v["sens_2t_ic"] = f"{votos(s2t['margem_ic_baixo'])} a {votos(s2t['margem_ic_alto'])}"
    v["sens_2t_votos"] = inteiro(abs(s2t["margem"]))
    v["sens_2t_ic_abs"] = f"de {inteiro(abs(s2t['margem_ic_baixo']))} a {inteiro(abs(s2t['margem_ic_alto']))}"
    v["pct_volta"] = pct(m["pct_volta"], 0)

    # quem vota
    v["pct_lula"], v["pct_flavio"] = pct(m["pct_lula"]), pct(m["pct_flavio"])
    v["urnas_lula"], v["urnas_flavio"] = inteiro(m["urnas_lula"]), inteiro(m["urnas_flavio"])
    v["urnas_empate"] = f"{m['urnas_empate']} empate" + ("s" if m["urnas_empate"] != 1 else "")
    lado = "Lula" if m["lula"] > m["flavio"] else "Flávio"
    v["urnas_vitorias_frase"] = (
        f"{lado} venceu em menos urnas, mas por margens maiores"
        if (m["urnas_lula"] < m["urnas_flavio"]) == (lado == "Lula") and m["urnas_lula"] != m["urnas_flavio"] else
        f"os dois venceram no mesmo número de urnas, e {lado} teve margens maiores"
        if m["urnas_lula"] == m["urnas_flavio"] else f"{lado} venceu em mais urnas e somou mais votos")
    v["abst"] = pct(m["abst"])
    vz = n["voto_vs_vizinhas"]
    ponto = lambda x: " pontos" if round(abs(x), 1) >= 2 else " ponto"
    v["vizinhas_dif"] = dec(abs(vz["dif_pp"])) + ponto(vz["dif_pp"]) + (" a mais" if vz["dif_pp"] >= 0 else " a menos")
    v["vizinhas_ic"] = (f"{dec(-vz['ic_baixo'])}{ponto(vz['ic_baixo'])} a menos a {dec(vz['ic_alto'])} a mais" if vz["ic_baixo"] < 0 < vz["ic_alto"]
                        else f"{sinal(vz['ic_baixo'])} a {sinal(vz['ic_alto'])}{ponto(vz['ic_alto'])}")
    v["vizinhas_pct_acima"] = pct(vz["pct_acima"], 0)
    g26 = geo["2026"]
    v["lula_esperado_municipio"] = pct(g26["lula_esperado_pelo_municipio"])
    v["lula_esperado_estado"] = pct(g26["lula_esperado_pelo_estado"])

    # distância
    v["dist_mediana"] = f"{arred(dist['mediana'] * 1000, 10)} m"
    v["dist_media"] = f"cerca de {arred(dist['media'] * 1000, 100)} m" if dist["media"] < 0.95 else f"cerca de {dec(dist['media'])} km"
    v["dist_menos_1km"] = pct(dist["menos_1km"], 0)
    v["dist_5km"] = pct(dist["de_5km"], 1)
    v["dist_urnas_com"], v["dist_aptos_com"] = inteiro(dist["urnas_com"]), mil(dist["aptos_com"])
    v["dist_urnas_sem"], v["dist_aptos_sem"] = inteiro(dist["urnas_sem"]), mil(dist["aptos_sem"])
    v["predio_novo"] = inteiro(m["predio_novo_mesmo_numero"])
    v["dist_sem_coord"] = inteiro(dist["urnas_sem"] - m["predio_novo_mesmo_numero"])
    norte = mud[mud.SG_UF.isin(NORTE)]
    v["norte_sem_dist"], v["norte_urnas"] = inteiro(norte.dist_km.isna().sum()), inteiro(len(norte))
    longe = mud.loc[mud.dist_km.idxmax()]
    km = longe.dist_km
    v["trajeto_mais_longo"] = (f"{dec(km) if km < 10 else inteiro(km)} km em {longe.NM_MUNICIPIO.title()} ({longe.SG_UF})")
    sem = [u["uf"] for u in dist["ufs"] if u["com"] == 0]
    v["ufs_sem_distancia"] = lista(NOME_UF[u] for u in sem) if sem else "em nenhum estado"
    so_lista = [p for p in web["pares"] if p["tipo"] != "confusao" and not any(c is not None for c in (p["a"] or [None]) + (p["b"] or [None]))]
    v["trajetos_so_na_lista"] = f"{len(so_lista)} trajeto" + ("s só aparecem" if len(so_lista) != 1 else " só aparece")

    # as quatro situações e o critério do painel de 17/10
    fc = n["fora_do_cadastro_2t"]
    sai = tipos.get("saiu do local de cadastro", 0) + tipos.get("trocou de local provisório", 0)
    volta, predio = tipos.get("voltou ao local de cadastro", 0), tipos.get("local de sempre em outro prédio", 0)
    v["ja_fora"], v["sai"], v["volta"], v["predio"] = (inteiro(fc["ja_fora_no_1t_urnas"]), inteiro(sai),
                                                         inteiro(volta), inteiro(predio))
    v["painel17_total"] = inteiro(fc["ja_fora_no_1t_urnas"] + sai)
    v["fora_2t_aptos"] = dec(fc["aptos"] / 1e6, 2) + " milhões"
    v["fora_2t_faltaram"] = f"{inteiro(arred(fc['faltaram_1t'], 10000) / 1000)} mil"
    v["ja_fora_abst"] = pct(fc["ja_fora_no_1t_abst"])
    v["abst_pais"] = pct(n["nacional"]["abst"])
    v["mesmo_endereco_urnas"] = inteiro(m["mesmo_endereco_urnas"])
    v["mesmo_endereco_aptos"] = inteiro(m["mesmo_endereco_aptos"])
    v["reescritas"] = "nenhuma urna" if m["reescritas_urnas"] == 0 else f"{m['reescritas_urnas']} urnas"
    v["nome_reescrito_urnas"] = inteiro(m["nome_reescrito_urnas"])
    v["nome_reescrito_aptos"] = inteiro(m["nome_reescrito_aptos"])
    v["nome_parecido_urnas"] = inteiro(m["nome_parecido_urnas"])
    n22 = int((pd.read_csv(SAIDA / "urnas_2022.csv.gz", usecols=["tipo"]).tipo
               == "mesmo prédio, nome e endereço reescritos no cadastro").sum())
    v["nome_reescrito_2022"] = "nenhuma urna" if n22 == 0 else "1 urna" if n22 == 1 else f"{inteiro(n22)} urnas"
    v["agregadas"] = inteiro(m["agregadas"])
    log02 = (SAIDA / "log_02.txt").read_text(encoding="utf-8")
    v["correcoes_cadastro"] = inteiro(int(re.search(r"só nome ou só endereço: (\d+)", log02).group(1)))

    # painel de 18/10
    pt = n["painel_tse"]
    so = pt["so_no_painel"]
    v["painel_nas_duas"] = inteiro(pt["nas_duas_listas"])
    v["painel_fora"] = inteiro(m["urnas"] - pt["nas_duas_listas"])
    v["painel_so"] = inteiro(sum(so.values()))
    v["painel_mesmo_local"] = inteiro(so.get("mesmo local nos dois turnos no cadastro atual", 0))
    v["painel_outras"] = inteiro(sum(so.values()) - so.get("mesmo local nos dois turnos no cadastro atual", 0))
    v["painel_so_nome"] = inteiro(so.get("só o nome do local mudou", 0))
    v["painel_so_grafia"] = inteiro(so.get("só a grafia do nome mudou", 0))
    v["painel_so_endereco"] = inteiro(so.get("só o endereço mudou", 0))
    p = pd.read_csv(SAIDA / "painel_tse.csv")
    p = p[p.fora_daqui == "mesmo local nos dois turnos no cadastro atual"]
    ja = pd.concat([pd.read_csv(io.BytesIO(git(f"{c}:saida/urnas_mudadas_2026.csv")), usecols=URNA)
                    for _, c, _ in VERSOES if c]).drop_duplicates()
    p = p.rename(columns={"NR_SECAO": "_s", "urna": "NR_SECAO"})
    v["painel_sairam"] = inteiro(len(p[URNA].drop_duplicates().merge(ja, on=URNA)))

    # como a lista encolheu
    v["renovadas"] = inteiro(ren["renovadas"])
    v["renovadas_ufs"], v["renovadas_municipios"], v["renovadas_zonas"] = (
        inteiro(ren["ufs_com_renovacao"]),
        inteiro(ren["municipios"]), inteiro(ren["zonas"]))
    ufs = pd.DataFrame(ren["ufs"])
    v["renovadas_pr_pct"] = pct(100 * ufs.set_index("uf").renovadas.get("PR", 0) / ren["renovadas"], 0)
    v["ainda_voltam_1o"] = inteiro(ren["ainda_voltam_1o_cadastro"])
    v["outro_provisorio"] = inteiro(ren["outro_provisorio"])
    com_outro = [u["uf"] for u in ren["ufs"] if u["outro_provisorio"]]
    v["outro_provisorio_frase"] = (
        "nenhuma foi para outro prédio provisório" if not ren["outro_provisorio"] else
        f"{inteiro(ren['outro_provisorio'])}" + (f", {'todas ' if ren['outro_provisorio'] > 1 else ''}{NOME_UF[com_outro[0]]},"
                                                     if len(com_outro) == 1 else "")
        + (" foi" if ren["outro_provisorio"] == 1 else " foram") + " para outro prédio provisório")
    v["voltavam_1o"] = inteiro(ren["renovadas"] + ren["ainda_voltam_1o_cadastro"] + ren["outro_provisorio"])
    v["ficam_no_local_de_sempre"] = inteiro(ren["ficam_no_local_de_sempre"])
    v["primeiro_turno_reescrito"] = inteiro(ren["primeiro_turno_reescrito"])
    v["fora_da_conta_renovadas"] = inteiro(ren["ficam_no_local_de_sempre"] + ren["primeiro_turno_reescrito"])
    v["fora_1t"] = inteiro(ren["fora_1t"])
    v["taxa_volta_1o"] = pct(ren["versoes"][0]["taxa_volta"], 0)
    v["taxa_volta"] = pct(ren["versoes"][-1]["taxa_volta"], 1)
    vr, va = ren["voto_renovadas"], ren["voto_ainda_voltam"]
    v["renovadas_lula"], v["renovadas_flavio"], v["renovadas_esperado"] = pct(vr["pct_lula"]), pct(vr["pct_flavio"]), pct(vr["lula_esperado_pelo_municipio"])
    v["ainda_voltam_lula"], v["ainda_voltam_flavio"], v["ainda_voltam_esperado"] = pct(va["pct_lula"]), pct(va["pct_flavio"]), pct(va["lula_esperado_pelo_municipio"])
    v["voltam_zona_renovacao"] = f"{ren['voltam_em_zona_com_renovacao']} das {inteiro(volta)}"
    todas = [u for u in ren["ufs"] if u["voltavam"] >= 10 and u["renovadas"] >= .97 * u["voltavam"]]
    todas.sort(key=lambda u: -u["voltavam"])
    v["ufs_todas_ou_quase"] = lista(f"{NOME_UF[u['uf']]} ({inteiro(u['renovadas'])} de {inteiro(u['voltavam'])})" for u in todas)
    v["ufs_todas_ou_quase"] = v["ufs_todas_ou_quase"][0].upper() + v["ufs_todas_ou_quase"][1:]
    poucas = [u for u in ren["ufs"] if u["voltavam"] >= 5 and u["renovadas"] <= u["voltavam"] / 4]
    v["ufs_quase_nenhuma"] = lista(f"{NOME_UF[u['uf']]} ({inteiro(u['renovadas'])} de {inteiro(u['voltavam'])})" for u in poucas)
    evo = json.loads((RAIZ / "docs" / "evolucao.json").read_text(encoding="utf-8"))
    v["evo_sem_coordenada"] = inteiro(sum(1 for u in evo["urnas"] if not u.get("xy")))

    # por local de votação (lista desta página)
    pl = {x["ef"]: x for x in web["por_local"] if x["lista"].startswith("urnas")}
    base = 100 * pl["nenhum"]["trocados"] / pl["nenhum"]["locais"]
    v["local_trocados"] = inteiro(pl["nenhum"]["trocados"])
    v["local_chance"] = pct(base, 2)
    v["local_por_mil"] = dec(10 * base, 1)
    for ef, k in [("nenhum", "pais"), ("estado", "estado"), ("município", "municipio")]:
        x = pl[ef]
        v[f"local_{k}"] = sinal(x["efeito"], 2)
        v[f"local_{k}_ic"] = f"{fino(x['ic'][0])} a {fino(x['ic'][1])}"
        v[f"local_{k}_limite"] = pct(base + x["ic"][1], 2)
    x = pl["nenhum"]
    v["local_pais_frase"] = ("o intervalo de 95% fica acima do zero" if x["ic"][0] > 0 else
                             "o intervalo de 95% inclui o zero" if x["ic"][1] > 0 else "o intervalo de 95% fica abaixo do zero")
    fx = [x for x in web["por_local_faixas"] if x["lista"].startswith("urnas")]
    for painel, k in [("país", "pais"), ("estado", "estado"), ("município", "municipio")]:
        ps = [x["pct"] for x in fx if x["painel"] == painel]
        v[f"faixas_{k}"] = f"de {pct(min(ps), 2)} a {pct(max(ps), 2)}"
    baixa = next(x for x in fx if x["painel"] == "país" and x["faixa"] == "menos de 30%")["pct"]
    outras_f = [x["pct"] for x in fx if x["painel"] == "país" and x["faixa"] != "menos de 30%"]
    v["faixas_pais_frase"] = (f"é de {pct(baixa, 2)} onde Lula teve menos de 30% e fica entre {pct(min(outras_f), 2)} "
                              f"e {pct(max(outras_f), 2)} nas outras faixas")

    # geografia
    reg = pd.read_csv(SAIDA / "geografia_regioes.csv").query("ano == 2026").set_index("regiao")
    for r in REGIOES:
        v[f"regiao_{r.lower().replace('-', '_')}"] = pct(reg.loc[r, "pct_aptos_mudam"], 0)
    v["pct_nordeste"] = v["regiao_nordeste"]

    def peso(r):  # a parte da região nas urnas que mudam, comparada com a parte dela no eleitorado
        a, e = reg.loc[r, "pct_aptos_mudam"], reg.loc[r, "pct_eleitorado"]
        return ("bem acima" if a > 2 * e else "bem abaixo" if a < e / 2 else "perto" if abs(a - e) < 5 else
                "acima" if a > e else "abaixo")
    v["nordeste_peso"] = f"{peso('Nordeste')} do peso da região"
    grupos = {}
    for r in ["Norte", "Sudeste", "Sul"]:
        grupos.setdefault(peso(r), []).append(r)
    # "o Norte fica bem acima do seu peso, e o Sudeste e o Sul, abaixo"
    partes = [f"{lista('o ' + r for r in rs)} {'ficam' if len(rs) > 1 else 'fica'} {p} do seu peso" if i == 0
              else f"{lista('o ' + r for r in rs)}, {p}" for i, (p, rs) in enumerate(grupos.items())]
    v["regioes_frase"] = ", ".join(partes[:-1]) + ", e " + partes[-1] if len(partes) > 1 else partes[0]
    ordem = list(geo["ufs_mais_mudam"]["2026"])  # os cinco estados com maior proporção de urnas mudando
    de = lambda u: NOME_UF[u].replace("no ", "do ", 1).replace("na ", "da ", 1).replace("em ", "de ", 1)  # noqa: E731
    if "AP" not in ordem:
        v["amapa_2026"] = f"fica fora dos {CARDINAIS[len(ordem)]} primeiros em 2026"
    else:
        i = ordem.index("AP")
        v["amapa_2026"] = (f"é o {['primeiro', 'segundo', 'terceiro', 'quarto', 'quinto'][i]} em 2026"
                           + (f", atrás {lista(de(u) for u in ordem[:i])}" if i else ""))
    v["correlacao"] = dec(geo["correlacao_ufs_2022_2026"], 2)

    # estado por estado
    uf = pd.DataFrame(web["ufs"]).set_index("SG_UF")
    com = [u for u in GOV_2T if u in uf.index]
    sem_gov = [u for u in GOV_2T if u not in uf.index]
    v["gov_com"] = lista(f"{NOME_UF[u].split(' ', 1)[1]} {inteiro(uf.loc[u, 'urnas'])}" for u in com)
    v["gov_sem"] = lista(NOME_UF[u] for u in sem_gov) if sem_gov else "em nenhum"
    v["urnas_sp_mg_rj_ba"] = lista(inteiro(uf.urnas.get(u, 0)) for u in ["SP", "MG", "RJ", "BA"])
    v["gov_aptos"] = mil(uf.loc[com, "aptos"].sum())

    # abstenção no 1º turno de 2026
    nv26, var, n22 = ab["nivel_2026"], ab["variacao_desde_2022"], ab["nivel_2022_mesmas_urnas"]
    v["abst1t_urnas"] = inteiro(ab["fora_no_1t_2026"])
    v["abst1t_nivel"], v["abst1t_nivel_ic"] = dec(nv26["dif_pp"], 2), f"{dec(nv26['ic'][0], 2)} a {dec(nv26['ic'][1], 2)}"
    v["abst1t_2022"], v["abst1t_2022_ic"] = sinal(n22["dif_pp"], 2), f"{sinal(n22['ic'][0], 2)} a {sinal(n22['ic'][1], 2)}"
    v["abst1t_var"], v["abst1t_var_ic"] = dec(var["dif_pp"], 2), f"{dec(var['ic'][0], 2)} a {dec(var['ic'][1], 2)}"
    v["abst1t_var_urnas"] = inteiro(var["urnas"])
    ef = ab["efeito_no_resultado_1t"]
    v["abst1t_eleitores"] = mil(arred(ef["estimativa"]["eleitores_a_menos"], 1000))
    v["abst1t_aptos"] = mil(ab["aptos_fora"])
    v["abst1t_lula"], v["abst1t_flavio"] = pct(ab["pct_lula_fora"]), pct(ab["pct_flavio_fora"])
    v["abst1t_votos"] = inteiro(arred(-ef["estimativa"]["votos_liquidos_lula"], 100))
    v["abst1t_votos_ic"] = f"{inteiro(arred(-ef['ic_baixo']['votos_liquidos_lula'], 100))} a {inteiro(arred(-ef['ic_alto']['votos_liquidos_lula'], 100))}"
    v["abst1t_votos_pct"] = pct(100 * -ef["estimativa"]["votos_liquidos_lula"] / n["nacional"]["margem_votos"], 2)
    v["abst1t_no_mesmo_predio"] = inteiro(fc["ja_fora_no_1t_urnas"])

    blocos = {"tab_efeito": tabela_efeito(hist), "tab_fontes": tabela_fontes(hist),
              "fluxo": fluxo(fc["ja_fora_no_1t_urnas"], sai, volta, predio, m["urnas"]),
              "linha_por_local": linha_por_local(pl, v)}
    return v, blocos


# --- blocos gerados ---------------------------------------------------------------------------------------------
def tabela_efeito(hist):
    linhas = []
    for i, h in enumerate(hist):
        n = h["n"]
        p, mu, vz = n["impacto"][n["principal"]], n["mudadas"], n["voto_vs_vizinhas"]
        teto_pct = pct(mu["teto_pct_margem"]) + (" da diferença" if i == 0 else "")
        classe = "nos" if i == len(hist) - 1 else "antiga"
        linhas.append(
            f'          <tr class="{classe}"><td class="txt">{h["rot"]}</td><td>{inteiro(mu["urnas"])}</td>'
            f'<td>{votos(p["margem"])} votos<br><small>{votos(p["margem_ic"][0])} a {votos(p["margem_ic"][1])}</small></td>'
            f'<td>{inteiro(mu["teto_votos"])} votos<br><small>{teto_pct}</small></td>'
            f'<td>{ponto(vz["dif_pp"])} ponto<br><small>{ponto(vz["ic_baixo"])} a {ponto(vz["ic_alto"])}</small></td></tr>')
    return "\n".join(linhas)


def tabela_fontes(hist):
    linhas = [(chave(r), f'        <tr><td class="txt">{a}</td><td class="txt">{b}</td><td>{c}</td><td>{d}</td></tr>')
              for r, a, b, c, d in FONTES_TSE]
    for i, h in enumerate(hist):
        u = h["n"]["mudadas"]["urnas"]
        atual = i == len(hist) - 1
        quem = "versão atual" if atual else f"{ordinal(i + 1)} versão"
        crit = ("Prédio do 2º turno × prédio registrado para o 1º turno" if not atual else
                "Prédio do 2º turno × prédio registrado para <strong>o 1º turno</strong>")
        linhas.append((chave(h["rot"]), f'        <tr class="{"nos" if atual else "antiga"}"><td class="txt">Este levantamento, '
                       f'{quem} (cadastro de {h["rot"]})</td><td class="txt">{crit}</td><td>{inteiro(u)}</td>'
                       f'<td>{pct(100 * u / URNAS_PAIS)}</td></tr>'))
    return "\n".join(x for _, x in sorted(linhas, key=lambda t: t[0]))


def fluxo(ja, sai, volta, predio, total):
    return (f'''    <div>
      <div class="rot"><b>Critério do painel de 17/10, com o cadastro atual</b><span class="num">{inteiro(ja + sai)} urnas</span></div>
      <div class="barra"><div class="seg-ja" style="flex: {ja}"></div><div class="seg-novo" style="flex: {sai}"></div></div>
    </div>
    <div>
      <div class="rot"><b>Mudam de prédio do 1º para o 2º turno</b><span class="num">{inteiro(total)} urnas</span></div>
      <div class="barra"><div class="seg-novo" style="flex: {sai}"></div><div class="seg-volta" style="flex: {volta}"></div><div class="seg-predio" style="flex: {predio}"></div></div>
    </div>
    <div class="leg-barra">
      <span><i class="seg-ja"></i>Já estavam nesse prédio no 1º turno ({inteiro(ja)})</span>
      <span><i class="seg-novo"></i>Saem do local de sempre ({inteiro(sai)})</span>
      <span><i class="seg-volta"></i>Voltam ao local de sempre ({inteiro(volta)})</span>
      <span><i class="seg-predio"></i>Local de sempre em outro prédio ({inteiro(predio)})</span>
    </div>''')


def linha_por_local(pl, v):
    x = pl["nenhum"]
    return (f'          <tr class="nos"><td class="txt">{v["urnas"]} urnas que mudam de prédio</td>'
            f'<td>{inteiro(x["trocados"])}<br><small>{v["local_chance"]}</small></td>'
            f'<td>{v["local_pais"]}<br><small>{v["local_pais_ic"]}</small></td>'
            f'<td>{v["local_estado"]}<br><small>{v["local_estado_ic"]}</small></td>'
            f'<td>{v["local_municipio"]}<br><small>{v["local_municipio_ic"]}</small></td></tr>')


# --- aplicação nos arquivos -------------------------------------------------------------------------------------
# marcador logo depois de crase é exemplo de código (no README), não marcador
N = re.compile(r"(?<!`)<!--n:([a-z0-9_]+)-->(.*?)<!--/n-->", re.S)
G = re.compile(r"(?<!`)<!--g:([a-z0-9_]+)-->.*?<!--/g:\1-->", re.S)
META = re.compile(r'(<meta name="versao-dados" content=")[^"]*(">)')
DESCRICAO = re.compile(r'(<meta (?:name|property)="(?:og:)?description" content="As )[\d.]+( urnas [^"]*Atualizado em )\d\d/\d\d(\.">)')


def preencher(texto, v, blocos, usadas):
    def n(mt):
        usadas.add(mt.group(1))
        if mt.group(1) not in v:
            sys.exit(f"chave sem valor: {mt.group(1)}")
        return f"<!--n:{mt.group(1)}-->{v[mt.group(1)]}<!--/n-->"

    def g(mt):
        k = mt.group(1)
        usadas.add(k)
        if k not in blocos:
            sys.exit(f"bloco sem valor: {k}")
        return f"<!--g:{k}-->\n{blocos[k]}\n<!--/g:{k}-->"
    texto = G.sub(g, N.sub(n, texto))
    # atributos não aceitam marcadores: a descrição da página tem o número e a data reescritos aqui
    texto = DESCRICAO.sub(lambda mt: f'{mt.group(1)}{v["urnas"]}{mt.group(2)}{v["atualizado"]}{mt.group(3)}', texto)
    return META.sub(lambda mt: mt.group(1) + v["versao_meta"] + mt.group(2), texto)


def main():
    v, blocos = valores()
    usadas = set()
    for arq in (PAGINA, README):
        antes = arq.read_text(encoding="utf-8")
        depois = preencher(antes, v, blocos, usadas)
        if depois != antes:
            arq.write_text(depois, encoding="utf-8", newline="\n")
        print(f"{arq.name}: {len(N.findall(depois))} números e {len(G.findall(depois))} blocos marcados"
              + ("" if depois != antes else " (sem mudança)"))
    (SAIDA / "texto.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    sobra = sorted(set(v) - usadas)
    if sobra:
        print("chaves sem uso no texto:", ", ".join(sobra))


if __name__ == "__main__":
    main()
