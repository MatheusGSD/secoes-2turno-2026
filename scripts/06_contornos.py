"""Contornos de estados e municípios para o mapa da página (docs/contornos.json).

Malhas do IBGE em qualidade intermediária (ver ibge.py), simplificadas para a página. Só entram os
municípios que têm urna mudando de prédio.

Uso: python -P scripts/06_contornos.py   (depois de 03 e 04)
"""
import json
import sys
from pathlib import Path

import pandas as pd
from shapely.geometry import mapping, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ibge  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TOL_UF, TOL_MUN = 0.01, 0.0015  # simplificação, em graus (~1 km e ~150 m)


def aneis(geom, tol, casas):
    """Geometria simplificada como lista de polígonos; cada polígono, lista de anéis [lon, lat, lon, lat...]."""
    g = shape(geom).simplify(tol, preserve_topology=True)
    polis = mapping(g)["coordinates"] if g.geom_type == "MultiPolygon" else [mapping(g)["coordinates"]]
    return [[[round(v, casas) for xy in anel for v in xy] for anel in poli] for poli in polis]


def main():
    m = pd.read_csv(RAIZ / "saida/urnas_mudadas_2026.csv", usecols=["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"])
    m = m.drop_duplicates("CD_MUNICIPIO").copy()
    m["ibge"] = ibge.codigos(m.SG_UF, m.NM_MUNICIPIO)
    falta = m[m.ibge.isna()]
    print("municípios com urna mudando:", len(m), "| sem código IBGE:", len(falta))
    if len(falta):
        print(falta[["SG_UF", "NM_MUNICIPIO"]].to_string(index=False))

    sigla = ibge.sigla_por_id()
    out = {"uf": {sigla[int(f["properties"]["codarea"])]: aneis(f["geometry"], TOL_UF, 3)
                  for f in ibge.malha_ufs()["features"]}, "mun": {}}
    cod_tse = dict(zip(m.ibge.dropna().astype(int), m.CD_MUNICIPIO[m.ibge.notna()]))
    for uf in sorted(m.SG_UF.unique()):
        for c, f in ibge.malha_municipios(uf).items():
            if c in cod_tse:
                out["mun"][str(cod_tse[c])] = aneis(f["geometry"], TOL_MUN, 4)
    txt = json.dumps(out, separators=(",", ":"))
    (RAIZ / "docs/contornos.json").write_text(txt, encoding="utf-8")
    print("estados:", len(out["uf"]), "| municípios:", len(out["mun"]), "| contornos.json:", round(len(txt) / 1e3), "KB")


if __name__ == "__main__":
    main()
