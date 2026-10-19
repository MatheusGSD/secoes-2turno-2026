"""Dados da página (docs/dados.json): mapa, gráficos e tabela.

- fundo: todos os locais de votação do 2º turno, como pontos (lon, lat em milésimos de grau,
  ordenados e em diferenças, para o arquivo ficar pequeno). Desenham o Brasil sem depender de
  mapa de fundo externo.
- pares: as urnas que trocam de local, juntas por (local do 1º turno -> local do 2º turno). "aviso" marca
  os pares com o mesmo endereço nos dois turnos.
- ufs, efeito_2022, numeros: as tabelas de 03_impacto.py.
- distancia: faixas de distância entre o prédio do 1º e o do 2º turno e a mediana por estado.
- por_local, por_local_faixas: a regressão por local de votação e o percentual de locais na lista por faixa de
  voto em Lula, de 09_por_local.py (sem eles, os gráficos ficam vazios).

Uso: python -P scripts/04_exportar_web.py   (depois de 02 e 03, e de 09 para o gráfico por local)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
WEB = RAIZ / "docs"
WEB.mkdir(exist_ok=True)
GOVERNADOR_2T = ["AC", "AM", "DF", "ES", "RN", "TO"]  # 2º turno para governador em 2026 (o RJ decidiu no 1º)
MINUSCULAS = {"de", "da", "do", "das", "dos", "e"}


def nome_proprio(s):
    if not isinstance(s, str):
        return s
    return " ".join(p.lower() if i and p.lower() in MINUSCULAS else p.capitalize() for i, p in enumerate(s.split()))


def coord(x):
    return None if pd.isna(x) else round(float(x), 5)


def fundo():
    u = pd.read_csv(SAIDA / "urnas_2026.csv.gz", usecols=["SG_UF", "lat_2", "lon_2"]).dropna()
    # descarta coordenada fora do Brasil (cadastro com erro)
    u = u[u.lat_2.between(-34, 5.5) & u.lon_2.between(-74.5, -28.5)]
    pts = np.unique(np.round(u[["lon_2", "lat_2"]].to_numpy() * 1000).astype(int), axis=0)
    flat = pts.ravel()
    delta = np.concatenate([flat[:2], np.diff(flat.reshape(-1, 2), axis=0).ravel()])
    rotulos = u.groupby("SG_UF")[["lon_2", "lat_2"]].median().round(3).reset_index()
    return delta.tolist(), rotulos.values.tolist()


def pares():
    m = pd.read_csv(SAIDA / "urnas_mudadas_2026.csv")
    chave = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2", "tipo"]
    g = m.groupby(chave, dropna=False).agg(
        mun=("NM_MUNICIPIO", "first"), dist=("dist_km", "first"),
        de=("NM_LOCAL_VOTACAO", "first"), de_end=("DS_ENDERECO", "first"), de_bairro=("NM_BAIRRO", "first"),
        lat1=("lat", "first"), lon1=("lon", "first"),
        para=("NM_LOCAL_VOTACAO_2", "first"), para_end=("DS_ENDERECO_2", "first"), para_bairro=("NM_BAIRRO_2", "first"),
        lat2=("lat_2", "first"), lon2=("lon_2", "first"),
        secoes=("NR_SECAO", lambda s: sorted(int(x) for x in s)),
        aptos=("aptos", "sum"), comp=("comparecimento", "sum"), validos=("validos", "sum"),
        lula=("c13", "sum"), flavio=("c22", "sum"), outros=("outros", "sum"),
        urnas_lula=("vencedor", lambda s: int((s == "Lula").sum())),
        urnas_flavio=("vencedor", lambda s: int((s == "Flávio").sum())),
        mesmo_end=("mesmo_endereco", "any"),
    ).reset_index()
    tipo_curto = {"voltou ao local de cadastro": "volta", "saiu do local de cadastro": "sai",
                  "trocou de local provisório": "troca", "local de sempre em outro prédio": "predio"}
    out = []
    for r in g.itertuples():
        out.append({
            "uf": r.SG_UF, "cod": int(r.CD_MUNICIPIO), "mun": nome_proprio(r.mun), "zona": int(r.NR_ZONA), "secoes": r.secoes,
            "tipo": tipo_curto[r.tipo], "dist": None if pd.isna(r.dist) else round(float(r.dist), 2),
            "de": r.de, "de_end": r.de_end, "de_bairro": r.de_bairro, "a": [coord(r.lon1), coord(r.lat1)],
            "para": r.para, "para_end": r.para_end, "para_bairro": r.para_bairro, "b": [coord(r.lon2), coord(r.lat2)],
            "aptos": int(r.aptos), "comp": int(r.comp), "validos": int(r.validos), "lula": int(r.lula),
            "flavio": int(r.flavio), "outros": int(r.outros), "ul": r.urnas_lula, "uf_": r.urnas_flavio,
            "aviso": bool(r.mesmo_end),  # mesmo endereço nos dois turnos: pode ser o mesmo prédio
        })
    print("pares:", len(out), "| sem nenhuma coordenada:", sum(p["a"][0] is None and p["b"][0] is None for p in out),
          "| só uma:", sum((p["a"][0] is None) != (p["b"][0] is None) for p in out))
    return out


def mediana_ponderada(x, w):
    o = np.argsort(x)
    x, w = np.asarray(x)[o], np.asarray(w)[o]
    return float(x[np.searchsorted(np.cumsum(w) / w.sum(), 0.5)])


def distancia():
    """Distância entre o prédio do 1º e o do 2º turno: faixas e mediana por estado, ponderadas pelos eleitores.

    "trajetos" conta pares (local do 1º turno -> local do 2º) com distância: urnas do mesmo prédio têm a
    mesma distância, então é ele que diz quanto a mediana de um estado é confiável.
    """
    m = pd.read_csv(SAIDA / "urnas_mudadas_2026.csv")
    d = m.dropna(subset=["dist_km"])
    limites = [0, 0.3, 0.6, 1, 2, 5, 10, np.inf]
    rotulos = ["até 300 m", "300 a 600 m", "600 m a 1 km", "1 a 2 km", "2 a 5 km", "5 a 10 km", "mais de 10 km"]
    faixa = pd.cut(d.dist_km, limites, labels=rotulos, right=False)
    g = d.groupby(faixa, observed=False).aptos.agg(["size", "sum"])
    trajeto = ["CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2"]
    ufs = []
    for uf, t in m.groupby("SG_UF"):
        s = d[d.SG_UF == uf]
        ufs.append({"uf": uf, "urnas": len(t), "com": len(s), "trajetos": len(s.drop_duplicates(trajeto)),
                    "mediana": round(mediana_ponderada(s.dist_km, s.aptos), 3) if len(s) else None,
                    "menos_1km": round(100 * s[s.dist_km < 1].aptos.sum() / s.aptos.sum(), 1) if len(s) else None})
    sem = m.dist_km.isna()
    mediana = mediana_ponderada(d.dist_km, d.aptos)
    na_mediana = rotulos[np.searchsorted(limites, mediana, side="right") - 1]
    return {
        "mediana": round(mediana, 4),  # 4 casas: com 3, 414,6 m vira 0,415 e é arredondado de novo para 420 m
        "media": round(float((d.dist_km * d.aptos).sum() / d.aptos.sum()), 3),
        "menos_1km": round(100 * d[d.dist_km < 1].aptos.sum() / d.aptos.sum(), 1),
        "de_5km": round(100 * d[d.dist_km >= 5].aptos.sum() / d.aptos.sum(), 1),
        "urnas_com": len(d), "aptos_com": int(d.aptos.sum()), "urnas_sem": int(sem.sum()), "aptos_sem": int(m[sem].aptos.sum()),
        "faixas": [{"rot": r, "urnas": int(g.loc[r, "size"]), "aptos": int(g.loc[r, "sum"]), "med": r == na_mediana}
                   for r in rotulos],
        "ufs": ufs,
    }


def por_local():
    """Regressão por local de votação de 09_por_local.py, com o local de cadastro como unidade."""
    p = SAIDA / "por_local.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    d = d[d.unidade == "local de cadastro"]
    return [{"lista": r.lista, "ef": r.efeito_fixo, "locais": int(r.locais), "trocados": int(r.locais_trocados),
             "efeito": round(r.lula_10pp, 4), "ic": [round(r.lula_10pp - 1.96 * r.ep_lula_10pp, 4),
                                                     round(r.lula_10pp + 1.96 * r.ep_lula_10pp, 4)]}
            for r in d.itertuples()]


def por_local_faixas():
    """Percentual de locais na lista por faixa de voto em Lula, de 09_por_local.py."""
    p = SAIDA / "por_local_faixas.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    return [{"lista": r.lista, "painel": r.painel, "faixa": r.faixa, "locais": int(r.locais), "na_lista": int(r.na_lista),
             "pct": round(r.pct, 3), "ic": [round(r.ic_baixo, 3), round(r.ic_alto, 3)]} for r in d.itertuples()]


def main():
    delta, rotulos = fundo()
    uf = pd.read_csv(SAIDA / "impacto_uf_2026.csv")
    uf["gov_2t"] = uf.SG_UF.isin(GOVERNADOR_2T)
    numeros = json.loads((SAIDA / "numeros.json").read_text(encoding="utf-8"))
    dados = {
        "fundo": delta, "rotulos": rotulos, "pares": pares(),
        "ufs": uf[["SG_UF", "urnas", "aptos", "c13", "c22", "validos", "urnas_lula", "urnas_flavio", "c13_uf",
                   "c22_uf", "validos_uf", "gov_2t"]].to_dict("records"),
        "numeros": numeros, "distancia": distancia(), "por_local": por_local(),
        "por_local_faixas": por_local_faixas(),
    }
    txt = json.dumps(dados, ensure_ascii=False, separators=(",", ":"), default=lambda x: None)
    (WEB / "dados.json").write_text(txt, encoding="utf-8")
    print("dados.json:", round(len(txt.encode()) / 1e6, 2), "MB | pontos de fundo:", len(delta) // 2)


if __name__ == "__main__":
    main()
