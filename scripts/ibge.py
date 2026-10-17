"""Malhas e códigos de município do IBGE, usados por 02_mudancas.py e 06_contornos.py.

Tudo vem da API de dados do IBGE (servicodados.ibge.gov.br) e fica guardado em dados/ibge/
depois do primeiro download. O TSE e o IBGE usam códigos de município diferentes; ligamos os dois
pelo nome e pela UF, sem acentos, apóstrofos ou hífens. Os nomes que não batem estão em GRAFIA_TSE.
"""
import gzip
import json
import time
import unicodedata
import urllib.request
from pathlib import Path

from shapely.geometry import shape

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "dados/ibge"
API = "https://servicodados.ibge.gov.br/api"
GEOJSON = "formato=application/vnd.geo%2Bjson&qualidade=intermediaria"
# (UF, nome normalizado no TSE) -> nome normalizado no IBGE, quando diferem
GRAFIA_TSE = {("GO", "BOMJESUS"): "BOMJESUSDEGOIAS", ("RR", "SAOLUIZ"): "SAOLUIZDOANAUA"}


def baixar(url, destino):
    PASTA.mkdir(parents=True, exist_ok=True)
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
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return "".join(c for c in s if c.isalnum())


def uf_de(x):
    """UF de um município da lista do IBGE (os criados há pouco vêm sem microrregião)."""
    if x.get("microrregiao"):
        return x["microrregiao"]["mesorregiao"]["UF"]
    return x["regiao-imediata"]["regiao-intermediaria"]["UF"]


def lista():
    return baixar(f"{API}/v1/localidades/municipios", PASTA / "municipios_lista.json")


def codigos(ufs, nomes):
    """Código IBGE de cada município do TSE (UF, nome), ou None quando o nome não bate."""
    ibge = {(uf_de(x)["sigla"], norm(x["nome"])): x["id"] for x in lista()}
    return [ibge.get((u, GRAFIA_TSE.get((u, norm(n)), norm(n)))) for u, n in zip(ufs, nomes)]


def malha_ufs():
    return baixar(f"{API}/v3/malhas/paises/BR?{GEOJSON}&intrarregiao=UF", PASTA / "uf_intermediaria.json")


def sigla_por_id():
    return {uf_de(x)["id"]: uf_de(x)["sigla"] for x in lista()}


def malha_municipios(uf):
    """{código IBGE: geometria} dos municípios de uma UF."""
    fc = baixar(f"{API}/v3/malhas/estados/{uf}?{GEOJSON}&intrarregiao=municipio", PASTA / f"municipios_{uf}.json")
    return {int(f["properties"]["codarea"]): f for f in fc["features"]}


def geometrias(uf):
    return {c: shape(f["geometry"]) for c, f in malha_municipios(uf).items()}
