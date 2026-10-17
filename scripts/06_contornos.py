"""Contornos de estados e municípios para o mapa da página (docs/contornos.json).

Malhas do IBGE pela API de dados (servicodados.ibge.gov.br), baixadas uma vez para dados/ibge/:
estados do Brasil e, para cada estado com urna que muda, os municípios, ambos em qualidade
intermediária. Só entram na página os municípios que têm urna mudando.

O TSE e o IBGE usam códigos de município diferentes; ligamos os dois pelo nome e pela UF, sem
acentos, apóstrofos ou hífens. Os poucos nomes que não batem estão em GRAFIA_TSE.

Uso: python -P scripts/06_contornos.py   (depois de 03 e 04)
"""
import gzip
import json
import time
import unicodedata
import urllib.request
from pathlib import Path

import pandas as pd
from shapely.geometry import shape, mapping

RAIZ = Path(__file__).resolve().parent.parent
IBGE = RAIZ / "dados/ibge"
IBGE.mkdir(parents=True, exist_ok=True)
API = "https://servicodados.ibge.gov.br/api"
GEOJSON = "formato=application/vnd.geo%2Bjson&qualidade=intermediaria"
TOL_UF, TOL_MUN = 0.01, 0.0015  # simplificação, em graus (~1 km e ~150 m)
# (UF, nome normalizado no TSE) -> nome normalizado no IBGE, quando diferem
GRAFIA_TSE = {("GO", "BOMJESUS"): "BOMJESUSDEGOIAS", ("RR", "SAOLUIZ"): "SAOLUIZDOANAUA"}


def baixar(url, destino):
    if not destino.exists():
        for tentativa in range(4):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    corpo = r.read()
                break
            except OSError:
                if tentativa == 3:
                    raise
                time.sleep(5 * (tentativa + 1))
        if corpo[:2] == b"\x1f\x8b":  # a API às vezes responde em gzip
            corpo = gzip.decompress(corpo)
        destino.write_bytes(corpo)
        time.sleep(0.5)
    return json.loads(destino.read_text(encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return "".join(c for c in s if c.isalnum())


def uf_de(x):
    """UF de um município da lista do IBGE (os criados há pouco vêm sem microrregião)."""
    if x.get("microrregiao"):
        return x["microrregiao"]["mesorregiao"]["UF"]
    return x["regiao-imediata"]["regiao-intermediaria"]["UF"]


def aneis(geom, tol, casas):
    """Geometria simplificada como lista de polígonos; cada polígono, lista de anéis [lon, lat, lon, lat...]."""
    g = shape(geom).simplify(tol, preserve_topology=True)
    polis = mapping(g)["coordinates"] if g.geom_type == "MultiPolygon" else [mapping(g)["coordinates"]]
    return [[[round(v, casas) for xy in anel for v in xy] for anel in poli] for poli in polis]


def main():
    m = pd.read_csv(RAIZ / "saida/urnas_mudadas_2026.csv", usecols=["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"])
    m = m.drop_duplicates("CD_MUNICIPIO")
    lista = baixar(f"{API}/v1/localidades/municipios", IBGE / "municipios_lista.json")
    ibge = {(uf_de(x)["sigla"], norm(x["nome"])): x["id"] for x in lista}
    m["chave"] = [GRAFIA_TSE.get((u, norm(n)), norm(n)) for u, n in zip(m.SG_UF, m.NM_MUNICIPIO)]
    m["ibge"] = [ibge.get((u, k)) for u, k in zip(m.SG_UF, m.chave)]
    falta = m[m.ibge.isna()]
    print("municípios com urna mudando:", len(m), "| sem código IBGE:", len(falta))
    if len(falta):
        print(falta[["SG_UF", "NM_MUNICIPIO"]].to_string(index=False))

    ufs = baixar(f"{API}/v3/malhas/paises/BR?{GEOJSON}&intrarregiao=UF", IBGE / "uf_intermediaria.json")
    sigla = {uf_de(x)["id"]: uf_de(x)["sigla"] for x in lista}
    out = {"uf": {sigla[int(f["properties"]["codarea"])]: aneis(f["geometry"], TOL_UF, 3) for f in ufs["features"]},
           "mun": {}}
    cod_tse = dict(zip(m.ibge.dropna().astype(int), m.CD_MUNICIPIO[m.ibge.notna()]))
    for uf in sorted(m.SG_UF.unique()):
        mun = baixar(f"{API}/v3/malhas/estados/{uf}?{GEOJSON}&intrarregiao=municipio", IBGE / f"municipios_{uf}.json")
        for f in mun["features"]:
            c = int(f["properties"]["codarea"])
            if c in cod_tse:
                out["mun"][str(cod_tse[c])] = aneis(f["geometry"], TOL_MUN, 4)
    txt = json.dumps(out, separators=(",", ":"))
    (RAIZ / "docs/contornos.json").write_text(txt, encoding="utf-8")
    print("estados:", len(out["uf"]), "| municípios:", len(out["mun"]), "| contornos.json:",
          round(len(txt) / 1e3), "KB")


if __name__ == "__main__":
    main()
