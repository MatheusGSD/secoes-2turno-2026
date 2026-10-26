"""Confere se o TSE publicou um cadastro de locais novo e, se pedido, refaz tudo com ele.

O portal de dados abertos guarda só a última versão de eleitorado_local_votacao_2026.zip, e o TSE trocou o arquivo
várias vezes por dia antes do 2º turno. Uma versão pode sumir entre duas conferências (aconteceu em 20/10), então
--verificar baixa toda versão nova para dados/novos/, mesmo que ela não chegue a ser usada.

O CDN serve cópia velha a quem pede o endereço puro: a conferência vai sempre com um parâmetro que fura o cache.
A data de cada versão é a de geração (DT_GERACAO e HH_GERACAO, de dentro do CSV, em Brasília), não a do arquivo.

--aplicar põe no lugar a versão mais nova de dados/novos/, guarda a anterior em dados/anteriores/, acrescenta a
versão em versoes.py (com o commit atual como o da anterior) e roda os scripts na ordem. O último, 18_texto.py,
preenche os números marcados no texto da página e do README; depois, 19_conferir.py procura o que ficou para trás
(saida/log_19.txt), sem desfazer nada se encontrar. O resto do texto, o commit e a publicação continuam à mão, pelo
CHECKLIST.md.

Robustez (depois de 20/10, 15h27, quando o cadastro trouxe 15 seções repetidas e 07_versoes.py quebrou no meio):
- antes de aplicar, a versão nova é conferida (colunas, os dois turnos, número de linhas); se não passa, nada muda;
- se um script falha, tudo é desfeito: zip em uso, versoes.py, saida/ e docs/ voltam ao que eram, e a versão nova
  volta para dados/novos/. No --automatico ela fica marcada em dados/novos/falhou.txt e não é tentada de novo a cada
  20 minutos; depois de corrigir o script, aplica-se com --aplicar.

--automatico junta os dois, para o Agendador de Tarefas do Windows (tarefa "Cadastro TSE 2o turno", a cada 20 minutos
até 25/10): confere, aplica se saida/ e docs/ estão sem mudanças pendentes e avisa por notificação do Windows. Se há
mudanças pendentes (uma atualização ainda sem texto ou sem commit), só baixa e avisa. O registro fica em
dados/novos/automatico.log.

Uso: python -P scripts/00_atualizar.py --verificar   (sai com código 10 se há versão nova esperando)
     python -P scripts/00_atualizar.py --aplicar
     python -P scripts/00_atualizar.py --rodar     (só os scripts, sem trocar o cadastro: depois de corrigir um deles)
     pythonw -P scripts/00_atualizar.py --automatico
"""
import contextlib
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
NOVOS, ANTERIORES = DADOS / "novos", DADOS / "anteriores"
FALHOU = NOVOS / "falhou.txt"  # versão que falhou no --automatico: não é tentada de novo sozinha
ATUAL = DADOS / "eleitorado_local_votacao_2026.zip"
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip"
REGISTRO = RAIZ / "scripts" / "versoes.py"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
# ordem de 19/10: 09 antes de 04 (04 exporta por_local a partir dos CSVs de 09); 12 depois de 07. Desde 26/10, 24 (o
# resultado do 2º turno) depois de 13 e antes de 04 e 18, que leem a saída dele
ORDEM = ["02", "03", "07", "12", "16", "09", "11", "13", "24", "04", "06", "05", "08", "10", "14", "15", "17", "18"]
COM_LOG = {"02", "03", "04", "07", "09", "11", "12", "13", "16", "18", "24"}
NOVA = 10
# no Agendador, o script roda com pythonw, sem console: cada processo filho que precisa de console (git, python) abriria
# uma janela. Os filhos rodam com python.exe num console oculto (CREATE_NO_WINDOW), que os netos (o git chamado pelos
# scripts) herdam, e nada aparece na tela.
SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)
PYTHON = sys.executable
if Path(PYTHON).name.lower() == "pythonw.exe":
    PYTHON = str(Path(PYTHON).with_name("python.exe"))


def executar(*args, **kw):
    """subprocess.run sem janela."""
    return subprocess.run(*args, creationflags=SEM_JANELA, **kw)


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
    commit = executar(["git", "rev-parse", "--short=7", "HEAD"], cwd=RAIZ, capture_output=True, text=True,
                            check=True).stdout.strip()
    t = REGISTRO.read_text(encoding="utf-8")
    fim = t.index("\n]\n")
    linhas = t[:fim].split("\n")
    assert ", None, " in linhas[-1], linhas[-1]
    linhas[-1] = linhas[-1].replace(", None, ", f', "{commit}", ')
    linhas.append(f'    ("{rotulo(g)}", None, "versoes_{g.day:02d}{MESES[g.month - 1]}_{g.hour:02d}h{g:%M}.csv"),')
    REGISTRO.write_text("\n".join(linhas) + t[fim:], encoding="utf-8")


def pendencias():
    return executar(["git", "status", "--porcelain", "--", "saida", "docs"], cwd=RAIZ, capture_output=True,
                          text=True, check=True).stdout


def conferir(arquivo):
    """Antes de aplicar: o cadastro novo tem as colunas de sempre, os dois turnos e quase o mesmo número de linhas."""
    def ler(a):
        with zipfile.ZipFile(a) as z, z.open("eleitorado_local_votacao_2026_BRASIL.csv") as f:
            cab = f.readline().decode("latin-1").strip().replace('"', "").split(";")
            turnos, n = set(), 0
            for linha in f:
                turnos.add(linha.split(b";", 6)[5].strip(b'"'))
                n += 1
        return cab, turnos, n
    cab, turnos, n = ler(arquivo)
    cab0, _, n0 = ler(ATUAL)
    problemas = []
    if missing := [c for c in cab0 if c not in cab]:
        problemas.append(f"colunas que sumiram: {missing}")
    if turnos != {b"1", b"2"}:
        problemas.append(f"turnos: {sorted(t.decode() for t in turnos)}")
    if abs(n - n0) > .02 * n0:
        problemas.append(f"{n} linhas, contra {n0} na versão em uso")
    return problemas


def rodar():
    """Roda os scripts na ordem; para no primeiro que falhar."""
    amb = dict(os.environ, PYTHONIOENCODING="utf-8")
    for n in ORDEM:
        script = next((RAIZ / "scripts").glob(f"{n}_*.py"))
        print(f"rodando {script.name}", flush=True)
        r = executar([PYTHON, "-P", str(script)], cwd=RAIZ, env=amb, capture_output=True, text=True,
                           encoding="utf-8")
        if r.returncode:
            sys.exit(f"{script.name} falhou:\n{r.stdout[-2000:]}\n{r.stderr[-4000:]}")
        if n in COM_LOG:
            (RAIZ / "saida" / f"log_{n}.txt").write_text(r.stdout, encoding="utf-8")
    print((RAIZ / "saida" / "log_07.txt").read_text(encoding="utf-8"))
    # a conferência do texto não desfaz nada: o que ela acha é trabalho para o texto escrito à mão
    r = executar([PYTHON, "-P", str(RAIZ / "scripts" / "19_conferir.py")], cwd=RAIZ, env=amb,
                       capture_output=True, text=True, encoding="utf-8")
    (RAIZ / "saida" / "log_19.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
    print(r.stdout + r.stderr)


def aplicar():
    """Põe no lugar a versão mais nova e roda os scripts. Se um script falha, desfaz tudo: o zip em uso, versoes.py,
    saida/ e docs/ voltam a ser os da versão anterior, e a nova volta para dados/novos/."""
    sujo = pendencias()
    if sujo:
        sys.exit("saida/ ou docs/ têm mudanças sem commit: o commit atual precisa ser o da versão em uso.\n" + sujo)
    atual, novas = pendentes()
    if not novas:
        sys.exit(f"nenhuma versão mais nova que a em uso ({rotulo(atual)}) em dados/novos/")
    g, nova = novas[-1]
    if problemas := conferir(nova):
        sys.exit(f"o cadastro de {rotulo(g)} não passou na conferência, e nada foi aplicado: " + "; ".join(problemas))
    movidos, registro = [], REGISTRO.read_text(encoding="utf-8")
    copia = NOVOS / "antes_de_aplicar"  # tabelas completas (fora do git) da versão em uso, para desfazer
    copia.mkdir(exist_ok=True)
    for p in (RAIZ / "saida").glob("*.csv.gz"):
        shutil.copy2(p, copia / p.name)

    def mover(a, b):
        os.replace(a, b)
        movidos.append((a, b))
    try:
        utc = atual + timedelta(hours=3)
        mover(ATUAL, ANTERIORES / f"eleitorado_local_votacao_2026_gerado_{utc:%d}{MESES[utc.month - 1]}_{utc:%H%M}utc.zip")
        for gi, a in novas[:-1]:  # versões intermediárias: guardadas, sem uso
            u = gi + timedelta(hours=3)
            mover(a, ANTERIORES / f"eleitorado_local_votacao_2026_gerado_{u:%d}{MESES[u.month - 1]}_{u:%H%M}utc.zip")
        mover(nova, ATUAL)
        registrar(g)
        print(f"cadastro de {rotulo(atual)} -> {rotulo(g)}" + (f" ({len(novas) - 1} intermediária(s) guardada(s))" if novas[:-1] else ""))
        rodar()
    except BaseException:
        for a, b in reversed(movidos):
            os.replace(b, a)
        REGISTRO.write_text(registro, encoding="utf-8")
        for p in copia.glob("*.csv.gz"):
            shutil.copy2(p, RAIZ / "saida" / p.name)
        executar(["git", "checkout", "--", "saida", "docs"], cwd=RAIZ, check=True)
        executar(["git", "clean", "-fdq", "--", "saida", "docs"], cwd=RAIZ, check=True)  # o que os scripts criaram
        print(f"desfeito: de volta ao cadastro de {rotulo(atual)}; o de {rotulo(g)} continua em dados/novos/")
        raise
    shutil.rmtree(copia)
    FALHOU.unlink(missing_ok=True)


def avisar(titulo, texto):
    """Notificação do Windows, pelo PowerShell (o pythonw não tem console). É do tipo lembrete: fica na tela até ser
    fechada, em vez de sumir em poucos segundos (o aviso de 20/10, 11h42, passou despercebido)."""
    xml = (f"<toast scenario='reminder'><visual><binding template='ToastGeneric'><text>{escape(titulo)}</text>"
           f"<text>{escape(texto)}</text></binding></visual>"
           "<actions><action activationType='system' arguments='dismiss' content=''/></actions></toast>")
    ps = ("[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;"
          "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null;"
          "$x = [Windows.Data.Xml.Dom.XmlDocument]::new(); $x.LoadXml('" + xml.replace("'", "''") + "');"
          "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("
          "'{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe')"
          ".Show([Windows.UI.Notifications.ToastNotification]::new($x))")
    executar(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True)


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
            ramo = executar(["git", "branch", "--show-current"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
            if ramo != "main":  # um protótipo ou outro trabalho em andamento: não aplica fora do main
                if not avisado.exists() or avisado.read_text(encoding="utf-8") != rotulo(g):
                    avisar("Cadastro do TSE: versão nova", f"Gerada em {rotulo(g)} e guardada em dados/novos/. "
                           f"Não aplicada: o projeto está no branch {ramo}, não no main.")
                    avisado.write_text(rotulo(g), encoding="utf-8")
                print(f"versão nova não aplicada: branch {ramo}")
                return
            if FALHOU.exists() and FALHOU.read_text(encoding="utf-8") == rotulo(g):
                print(f"versão de {rotulo(g)} já falhou uma vez: só com --aplicar, à mão")
                return
            if pendencias():
                if not avisado.exists() or avisado.read_text(encoding="utf-8") != rotulo(g):
                    avisar("Cadastro do TSE: versão nova", f"Gerada em {rotulo(g)} e guardada em dados/novos/. "
                           "Não aplicada: saida/ ou docs/ têm mudanças sem commit.")
                    avisado.write_text(rotulo(g), encoding="utf-8")
                print("versão nova não aplicada: mudanças sem commit em saida/ ou docs/")
                return
            try:
                aplicar()
            except (Exception, SystemExit):
                FALHOU.write_text(rotulo(g), encoding="utf-8")
                raise
            avisos = [l for l in (RAIZ / "saida" / "log_02.txt").read_text(encoding="utf-8").splitlines() if "AVISO" in l]
            pend = re.search(r"pendências: (\d+)", (RAIZ / "saida" / "log_19.txt").read_text(encoding="utf-8"))
            avisar("Cadastro do TSE: versão nova aplicada", f"Gerada em {rotulo(g)}. Scripts rodados e números do texto "
                   f"preenchidos; falta o texto à mão (CHECKLIST.md). Conferência: {pend.group(1) if pend else '?'} "
                   "pendência(s) em saida/log_19.txt." + (f" Atenção: {len(avisos)} aviso(s) em saida/log_02.txt."
                                                          if avisos else ""))
            avisado.write_text(rotulo(g), encoding="utf-8")
        except (Exception, SystemExit) as e:
            traceback.print_exc()
            avisar("Cadastro do TSE: a atualização falhou", (f"{e}".strip().splitlines() or [type(e).__name__])[0][:150]
                   + " Nada foi mudado; detalhes em dados/novos/automatico.log.")


if __name__ == "__main__":
    if "--automatico" in sys.argv:
        automatico()
    elif "--aplicar" in sys.argv:
        aplicar()
    elif "--rodar" in sys.argv:
        rodar()
    elif "--verificar" in sys.argv:
        sys.exit(verificar())
    else:
        sys.exit(__doc__)
