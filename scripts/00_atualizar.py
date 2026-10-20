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

--automatico junta os dois, para o Agendador de Tarefas do Windows (tarefa "Cadastro TSE 2o turno", a cada 20 minutos
até 25/10): confere, aplica se saida/ e docs/ estão sem mudanças pendentes e avisa por notificação do Windows. Se há
mudanças pendentes (uma atualização ainda sem texto ou sem commit), só baixa e avisa. O registro fica em
dados/novos/automatico.log.

Uso: python -P scripts/00_atualizar.py --verificar   (sai com código 10 se há versão nova esperando)
     python -P scripts/00_atualizar.py --aplicar
     pythonw -P scripts/00_atualizar.py --automatico
"""
import contextlib
import os
import subprocess
import sys
import time
import traceback
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
ORDEM = ["02", "03", "07", "12", "16", "09", "11", "13", "04", "06", "05", "08", "10", "14", "15", "17"]
COM_LOG = {"02", "03", "04", "07", "09", "11", "12", "13", "16"}
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
    baixados = NOVOS / "baixados.txt"  # o zip sai de dados/novos/ quando é aplicado; o carimbo fica aqui
    vistos = set(baixados.read_text(encoding="utf-8").split()) if baixados.exists() else set()
    if carimbo not in vistos and not destino.exists():
        parcial = destino.with_suffix(".parcial")
        urllib.request.urlretrieve(f"{URL}?nc={int(time.time())}", parcial)
        os.replace(parcial, destino)
        with open(baixados, "a", encoding="utf-8") as f:
            f.write(carimbo + "\n")
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


def pendencias():
    return subprocess.run(["git", "status", "--porcelain", "--", "saida", "docs"], cwd=RAIZ, capture_output=True,
                          text=True, check=True).stdout


def aplicar():
    sujo = pendencias()
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


def avisar(titulo, texto):
    """Notificação do Windows, pelo PowerShell (o pythonw não tem console)."""
    q = lambda s: s.replace("'", "''")
    ps = ("[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;"
          "$x = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
          "[Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
          f"$x.GetElementsByTagName('text')[0].AppendChild($x.CreateTextNode('{q(titulo)}')) > $null;"
          f"$x.GetElementsByTagName('text')[1].AppendChild($x.CreateTextNode('{q(texto)}')) > $null;"
          "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("
          "'{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe')"
          ".Show([Windows.UI.Notifications.ToastNotification]::new($x))")
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def automatico():
    NOVOS.mkdir(exist_ok=True)
    avisado = NOVOS / "ultimo_aviso.txt"  # avisa uma vez por versão, não a cada 20 minutos
    with open(NOVOS / "automatico.log", "a", encoding="utf-8") as log, contextlib.redirect_stdout(log):
        try:
            try:
                if verificar() != NOVA:
                    return
            except OSError as e:  # rede ou CDN fora do ar: só registra, sem notificação a cada 20 minutos
                print(f"{datetime.now():%d/%m %H:%M} | conferência falhou: {e}")
                return
            g = pendentes()[1][-1][0]
            ramo = subprocess.run(["git", "branch", "--show-current"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
            if ramo != "main":  # um protótipo ou outro trabalho em andamento: não aplica fora do main
                if not avisado.exists() or avisado.read_text(encoding="utf-8") != rotulo(g):
                    avisar("Cadastro do TSE: versão nova", f"Gerada em {rotulo(g)} e guardada em dados/novos/. "
                           f"Não aplicada: o projeto está no branch {ramo}, não no main.")
                    avisado.write_text(rotulo(g), encoding="utf-8")
                print(f"versão nova não aplicada: branch {ramo}")
                return
            if pendencias():
                if not avisado.exists() or avisado.read_text(encoding="utf-8") != rotulo(g):
                    avisar("Cadastro do TSE: versão nova", f"Gerada em {rotulo(g)} e guardada em dados/novos/. "
                           "Não aplicada: saida/ ou docs/ têm mudanças sem commit.")
                    avisado.write_text(rotulo(g), encoding="utf-8")
                print("versão nova não aplicada: mudanças sem commit em saida/ ou docs/")
                return
            aplicar()
            avisar("Cadastro do TSE: versão nova aplicada", f"Gerada em {rotulo(g)}. Scripts rodados; falta o texto "
                   "da página e do README. Resumo em saida/log_07.txt.")
            avisado.write_text(rotulo(g), encoding="utf-8")
        except (Exception, SystemExit) as e:
            traceback.print_exc()
            avisar("Cadastro do TSE: a conferência falhou", f"{type(e).__name__}: {e}"[:200])


if __name__ == "__main__":
    if "--automatico" in sys.argv:
        automatico()
    elif "--aplicar" in sys.argv:
        aplicar()
    elif "--verificar" in sys.argv:
        sys.exit(verificar())
    else:
        sys.exit(__doc__)
