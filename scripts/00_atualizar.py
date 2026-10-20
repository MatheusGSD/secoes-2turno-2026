"""Confere se o TSE publicou um cadastro de locais novo e, se pedido, refaz tudo com ele.

O portal de dados abertos guarda só a última versão de eleitorado_local_votacao_2026.zip, e o TSE trocou o arquivo
várias vezes por dia antes do 2º turno. Uma versão pode sumir entre duas conferências (aconteceu em 20/10), então
--verificar baixa toda versão nova para dados/novos/, mesmo que ela não chegue a ser usada.

O CDN serve cópia velha a quem pede o endereço puro: a conferência vai sempre com um parâmetro que fura o cache.
A data de cada versão é a de geração (DT_GERACAO e HH_GERACAO, de dentro do CSV, em Brasília), não a do arquivo.

--aplicar põe no lugar a versão mais nova de dados/novos/, guarda a anterior em dados/anteriores/, acrescenta a
versão em versoes.py (com o commit atual como o da anterior) e roda os scripts na ordem. Não mexe no texto escrito à
mão em docs/index.html e no README, não faz commit e não publica: isso continua sendo feito depois, conferindo os
números de saida/numeros.json e o resumo de 07 (saida/log_07.txt).

Uso: python -P scripts/00_atualizar.py --verificar   (sai com código 10 se há versão nova esperando)
     python -P scripts/00_atualizar.py --aplicar
"""
import os
import subprocess
import sys
import time
import urllib.request
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
NOVOS, ANTERIORES = DADOS / "novos", DADOS / "anteriores"
ATUAL = DADOS / "eleitorado_local_votacao_2026.zip"
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip"
REGISTRO = RAIZ / "scripts" / "versoes.py"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
# ordem de 19/10: 09 antes de 04 (04 exporta por_local a partir dos CSVs de 09); 12 depois de 07
ORDEM = ["02", "03", "07", "12", "09", "11", "13", "04", "06", "05", "08", "10", "14", "15"]
COM_LOG = {"02", "03", "04", "07", "09", "11", "12", "13"}
NOVA = 10


def geracao(arquivo):
    """Data e hora de geração de dentro do cadastro, em Brasília."""
    with zipfile.ZipFile(arquivo) as z:
        membro = next(n for n in z.namelist() if n.endswith("_AC.csv"))
        with z.open(membro) as f:
            f.readline()
            dt, hh = f.readline().decode("latin-1").split(";")[:2]
    return datetime.strptime(dt.strip('"') + hh.strip('"'), "%d/%m/%Y%H:%M:%S")


def rotulo(g):
    return f"{g:%d/%m}, {g.hour}h{g:%M}"


def pendentes():
    """Versões em dados/novos/ mais novas que a atual, da mais velha à mais nova."""
    atual = geracao(ATUAL)
    vs = sorted((geracao(a), a) for a in NOVOS.glob("*.zip"))
    return atual, [(g, a) for g, a in vs if g > atual]


def verificar():
    NOVOS.mkdir(exist_ok=True)
    req = urllib.request.Request(f"{URL}?nc={int(time.time())}", method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        modificado = r.headers["Last-Modified"]
    carimbo = datetime.strptime(modificado, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y%m%d_%H%M%S")
    destino = NOVOS / f"cdn_{carimbo}utc.zip"
    if not destino.exists():
        parcial = destino.with_suffix(".parcial")
        urllib.request.urlretrieve(f"{URL}?nc={int(time.time())}", parcial)
        os.replace(parcial, destino)
        print(f"baixado: {destino.name} (gerado em {rotulo(geracao(destino))})")
    atual, novas = pendentes()
    print(f"{datetime.now():%d/%m %H:%M} | CDN: {modificado} | em uso: {rotulo(atual)} | novas:",
          ", ".join(rotulo(g) for g, _ in novas) or "nenhuma")
    return NOVA if novas else 0


def registrar(g):
    """Acrescenta a versão nova em versoes.py; a que era a atual ganha o commit de agora."""
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=RAIZ, capture_output=True, text=True,
                            check=True).stdout.strip()
    t = REGISTRO.read_text(encoding="utf-8")
    fim = t.index("\n]\n")
    linhas = t[:fim].split("\n")
    assert ", None, " in linhas[-1], linhas[-1]
    linhas[-1] = linhas[-1].replace(", None, ", f', "{commit}", ')
    linhas.append(f'    ("{rotulo(g)}", None, "versoes_{g.day:02d}{MESES[g.month - 1]}_{g.hour:02d}h{g:%M}.csv"),')
    REGISTRO.write_text("\n".join(linhas) + t[fim:], encoding="utf-8")


def aplicar():
    sujo = subprocess.run(["git", "status", "--porcelain", "--", "saida", "docs"], cwd=RAIZ, capture_output=True,
                          text=True, check=True).stdout
    if sujo:
        sys.exit("saida/ ou docs/ têm mudanças sem commit: o commit atual precisa ser o da versão em uso.\n" + sujo)
    atual, novas = pendentes()
    if not novas:
        sys.exit(f"nenhuma versão mais nova que a em uso ({rotulo(atual)}) em dados/novos/")
    g, nova = novas[-1]
    utc = atual + timedelta(hours=3)
    os.replace(ATUAL, ANTERIORES / f"eleitorado_local_votacao_2026_gerado_{utc:%d}{MESES[utc.month - 1]}_{utc:%H%M}utc.zip")
    for gi, a in novas[:-1]:  # versões intermediárias: guardadas, sem uso
        u = gi + timedelta(hours=3)
        os.replace(a, ANTERIORES / f"eleitorado_local_votacao_2026_gerado_{u:%d}{MESES[u.month - 1]}_{u:%H%M}utc.zip")
    os.replace(nova, ATUAL)
    registrar(g)
    print(f"cadastro de {rotulo(atual)} -> {rotulo(g)}" + (f" ({len(novas) - 1} intermediária(s) guardada(s))" if novas[:-1] else ""))

    amb = dict(os.environ, PYTHONIOENCODING="utf-8")
    for n in ORDEM:
        script = next((RAIZ / "scripts").glob(f"{n}_*.py"))
        print(f"rodando {script.name}", flush=True)
        r = subprocess.run([sys.executable, "-P", str(script)], cwd=RAIZ, env=amb, capture_output=True, text=True,
                           encoding="utf-8")
        if r.returncode:
            sys.exit(f"{script.name} falhou:\n{r.stdout[-2000:]}\n{r.stderr[-4000:]}")
        if n in COM_LOG:
            (RAIZ / "saida" / f"log_{n}.txt").write_text(r.stdout, encoding="utf-8")
    print((RAIZ / "saida" / "log_07.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    if "--aplicar" in sys.argv:
        aplicar()
    elif "--verificar" in sys.argv:
        sys.exit(verificar())
    else:
        sys.exit(__doc__)
