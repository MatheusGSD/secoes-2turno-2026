"""Dados da página (docs/dados.json): mapa, gráficos e tabela.

- fundo: todos os locais de votação do 2º turno, como pontos (lon, lat em milésimos de grau,
  ordenados e em diferenças, para o arquivo ficar pequeno). Desenham o Brasil sem depender de
  mapa de fundo externo.
- pares: as urnas que trocam de local, juntas por (local do 1º turno -> local do 2º turno).
- ufs, efeito_2022, numeros: as tabelas de 03_impacto.py.

Uso: python -P scripts/04_exportar_web.py   (depois de 02 e 03)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
WEB = RAIZ / "docs"
WEB.mkdir(exist_ok=True)
GOVERNADOR_2T = ["AC", "AM", "DF", "ES", "RJ", "RN", "TO"]  # 2º turno para governador em 2026
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
    chave = ["SG_UF", "CD_MUNICIPIO", "NR_LOCAL_VOTACAO", "NR_LOCAL_VOTACAO_2"]
    g = m.groupby(chave, dropna=False).agg(
        mun=("NM_MUNICIPIO", "first"), tipo=("tipo", "first"), dist=("dist_km", "first"),
        de=("NM_LOCAL_VOTACAO", "first"), de_end=("DS_ENDERECO", "first"), de_bairro=("NM_BAIRRO", "first"),
        lat1=("lat", "first"), lon1=("lon", "first"),
        para=("NM_LOCAL_VOTACAO_2", "first"), para_end=("DS_ENDERECO_2", "first"), para_bairro=("NM_BAIRRO_2", "first"),
        lat2=("lat_2", "first"), lon2=("lon_2", "first"),
        zona=("NR_ZONA", "first"), secoes=("NR_SECAO", lambda s: sorted(int(x) for x in s)),
        aptos=("aptos", "sum"), comp=("comparecimento", "sum"), validos=("validos", "sum"),
        lula=("c13", "sum"), flavio=("c22", "sum"), outros=("outros", "sum"),
        urnas_lula=("vencedor", lambda s: int((s == "Lula").sum())),
        urnas_flavio=("vencedor", lambda s: int((s == "Flávio").sum())),
    ).reset_index()
    tipo_curto = {"voltou ao local de cadastro": "volta", "saiu do local de cadastro": "sai",
                  "trocou de local provisório": "troca"}
    out = []
    for r in g.itertuples():
        out.append({
            "uf": r.SG_UF, "cod": int(r.CD_MUNICIPIO), "mun": nome_proprio(r.mun), "zona": int(r.zona), "secoes": r.secoes,
            "tipo": tipo_curto[r.tipo], "dist": None if pd.isna(r.dist) else round(float(r.dist), 2),
            "de": r.de, "de_end": r.de_end, "de_bairro": r.de_bairro, "a": [coord(r.lon1), coord(r.lat1)],
            "para": r.para, "para_end": r.para_end, "para_bairro": r.para_bairro, "b": [coord(r.lon2), coord(r.lat2)],
            "aptos": int(r.aptos), "comp": int(r.comp), "validos": int(r.validos), "lula": int(r.lula),
            "flavio": int(r.flavio), "outros": int(r.outros), "ul": r.urnas_lula, "uf_": r.urnas_flavio,
        })
    print("pares:", len(out), "| sem nenhuma coordenada:", sum(p["a"][0] is None and p["b"][0] is None for p in out),
          "| só uma:", sum((p["a"][0] is None) != (p["b"][0] is None) for p in out))
    return out


def main():
    delta, rotulos = fundo()
    uf = pd.read_csv(SAIDA / "impacto_uf_2026.csv")
    uf["gov_2t"] = uf.SG_UF.isin(GOVERNADOR_2T)
    numeros = json.loads((SAIDA / "numeros.json").read_text(encoding="utf-8"))
    dados = {
        "fundo": delta, "rotulos": rotulos, "pares": pares(),
        "ufs": uf[["SG_UF", "urnas", "aptos", "c13", "c22", "validos", "urnas_lula", "urnas_flavio", "c13_uf",
                   "c22_uf", "validos_uf", "gov_2t"]].to_dict("records"),
        "numeros": numeros,
    }
    txt = json.dumps(dados, ensure_ascii=False, separators=(",", ":"), default=lambda x: None)
    (WEB / "dados.json").write_text(txt, encoding="utf-8")
    print("dados.json:", round(len(txt.encode()) / 1e6, 2), "MB | pontos de fundo:", len(delta) // 2)


if __name__ == "__main__":
    main()
