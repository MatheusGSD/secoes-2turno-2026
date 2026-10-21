# Checklist de cada versão nova do cadastro

O TSE republica o cadastro de locais várias vezes por dia até o 2º turno. A cada versão, a página e o README são
refeitos. Parte disso é automática; o resto é este checklist. A ideia é que nenhum número do estado atual fique
para trás: a revisão de 21/10 achou uma média de distância de três versões antes, um total de categoria que tinha
mudado e uma referência a "a versão anterior" que já não era a anterior.

## O que é automático

`scripts/00_atualizar.py` (pela tarefa agendada, a cada 20 minutos, ou com `--aplicar`) baixa a versão nova, roda
todos os scripts e, por último:

- `18_texto.py` reescreve todo número do texto que descreve a lista atual. Esses números ficam entre marcadores:
  `<!--n:urnas-->364<!--/n-->` na página e no README, e blocos inteiros entre `<!--g:chave-->` e `<!--/g:chave-->`
  (as tabelas de versões e de fontes, a barra das quatro situações, a linha da regressão por local). As
  descrições da página (`<meta>`) e a versão nos endereços dos JSON também. Todos os valores ficam em
  `saida/texto.json`.
- `19_conferir.py` confere o texto e grava `saida/log_19.txt`:
  1. marcadores com valor diferente do que 18 calcularia agora;
  2. números da versão anterior (o `texto.json` do commit dela) e o rótulo do cadastro anterior que ainda aparecem no
     texto corrido, fora dos marcadores e fora do histórico;
  3. regras de interpretação: frases que dependem de um número passar de um limite (um intervalo incluir o zero, a
     ordem dos estados, o sinal de um efeito);
  4. este checklist.

Para rodar só os dois depois de mexer no texto: `python -P scripts/18_texto.py` e `python -P scripts/19_conferir.py`.

## O que continua à mão

- [ ] Ler `saida/log_07.txt` (o que saiu e o que entrou, por estado e município) e `saida/log_02.txt` (avisos de
      seções repetidas).
- [ ] Página, quadro do alto: reescrever o resumo visível (três ou quatro frases: o que saiu e o que entrou, o efeito
      segue perto de zero?). O título já é preenchido.
- [ ] Página, "O que mudou, versão por versão": parágrafo novo no topo, em negrito "De dd/mm, hhhmm: de N para M
      urnas.", com o que saiu e o que entrou e o link para o `saida/versoes_*.csv`. O parágrafo do cenário extremo
      ("caiu/subiu de X para Y") também.
- [ ] Resolver cada achado do item 2 de `log_19.txt`: ou é um número esquecido (pôr num marcador, criando a chave em
      18 se for preciso), ou é história (marcar o trecho com `<!--h-->...<!--/h-->`).
- [ ] Resolver cada regra que falhou no item 3: reescrever a frase indicada.
- [ ] Frases que contam versões ou citam a última pelo nome ("nos cadastros de 21/10", "nos de 11h27 e 14h19") e
      ainda não têm marcador: conferir se continuam verdadeiras.
- [ ] Cartão 10 (`10_imagem_por_local.py`): o subtítulo é escrito à mão; a regra do item 3 diz se ainda vale.
- [ ] README: parágrafo "**Atualização de dd/mm, cadastro de hhhmm.**" no topo de "O que os números mostram"; linha
      nova em negrito na tabela de versões (e tirar o negrito da anterior); `07_versoes.py` na tabela de scripts e a
      lista de arquivos de saída, com o CSV novo e o commit da versão anterior.
- [ ] Rodar de novo `18_texto.py` e `19_conferir.py` até `pendências: 0`.
- [ ] Abrir a página localmente (`python -m http.server --directory docs`) e olhar o alto, o mapa e a seção "Como a
      lista encolheu".
- [ ] Commit no `main` ("Atualização de dd/mm, hhhmm: N urnas saíram e M entraram, T urnas"), push, e conferir a
      página publicada (o GitHub Pages leva um ou dois minutos).
- [ ] Post no X, se for o caso: engatilhado no navegador para o autor publicar.

## Mexer nos marcadores

- **Número novo do estado atual no texto:** crie a chave em `valores()` do `scripts/18_texto.py`, já formatada (use
  `inteiro`, `dec`, `pct`, `mil`, `votos`, `sinal` ou `fino`), e escreva `<!--n:chave--><!--/n-->` no texto; o 18
  preenche. Na página, um marcador não pode ficar dentro de um atributo HTML (`aria-label`, `content`): ali, troque o
  número por uma conta no JS ou trate no 18, como as descrições `<meta>`.
- **Frase que depende de um limite** (um intervalo incluir o zero, um estado ser o primeiro, um efeito ser negativo):
  se ela pode ser gerada, gere a frase inteira numa chave (como `local_pais_frase`); se não, acrescente uma regra em
  `regras()` do `scripts/19_conferir.py`, com a condição e a frase que depende dela.
- **História fora do quadro de versões:** marque com `<!--h-->...<!--/h-->`. O 19 deixa de olhar o trecho.
- **Bloco gerado** (tabela inteira): função própria no 18, registrada em `blocos`, e `<!--g:chave-->` / `<!--/g:chave-->`
  no lugar do conteúdo.
- **Conferir:** `python -P scripts/18_texto.py` e depois `python -P scripts/19_conferir.py`, até `pendências: 0`.
