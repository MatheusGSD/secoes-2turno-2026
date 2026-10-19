# Urnas que mudam de lugar no 2º turno de 2026

A Justiça Eleitoral trocou o endereço de algumas seções entre o 1º e o 2º turno de 2026. Este repositório mostra
quais urnas mudam de prédio, em quem os eleitores dessas urnas votaram no 1º turno e quanto isso pode pesar no resultado.

**Página com o mapa:** https://matheusgsd.github.io/secoes-2turno-2026/

## O que os números mostram

Cadastro de locais do TSE gerado em 19/10/2026 às 15h27 (Brasília), baixado em 19/10. O TSE ainda pode mudar locais
até o dia 25; se publicar outra versão, a página e este README serão refeitos, com a mudança registrada aqui.

**Atualização de 19/10, à noite.** A versão anterior (commit `e8cf919`) usava o cadastro gerado em 19/10 às 11h27 e
contava 596 urnas. No cadastro de 19/10, 15h27, 195 delas, com 59.017 eleitores, deixaram de mudar: iam voltar ao
local de sempre e agora ficam no prédio do 1º turno (AM 45, PR 42, MG 38, GO 27, SP 24, SE 14, PE 3, RS 1, TO 1).
Entraram 74 urnas que votavam no local de sempre nos dois turnos e agora saem dele no 2º: 46 em MG (entre elas, 9 em
Caratinga, 9 em Caldas, 7 em Nova Era e 5 em Bela Vista de Minas), 6 em São João da Boa Vista-SP, 5 em Breves-PA, 5
no AM, 4 em São Mateus do Maranhão-MA, 4 em Maringá-PR, 2 na BA, 1 em RO e 1 no RS. São 475 urnas. A lista está em
`saida/versoes_19out_tarde.csv`.

**As atualizações continuam.** Em nota de 19/10, reproduzida pela imprensa
([Brasil 247](https://www.brasil247.com/brasil/tse-registra-mudancas-em-1-106-locais-de-votacao-para-o-segundo-turno-das-eleicoes/)),
o TSE disse que os números ainda estão sendo atualizados à medida que as zonas eleitorais concluem os ajustes nos
sistemas, inclusive para manter no 2º turno locais alterados provisoriamente no 1º. É o que aparece em todas as
versões do cadastro (veja "Como a lista encolheu", abaixo). Alguns TREs publicaram listas próprias: o
[TRE-AL](https://www.tre-al.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-nao-houve-alteracao-de-locais-de-votacao-para-o-segundo-turno-em-alagoas)
diz que nenhum local muda (aqui, 1 urna em Pão de Açúcar, que vai para o anexo da mesma escola, no mesmo endereço); o
[TRE-PE](https://www.tre-pe.jus.br/comunicacao/noticias/2026/Outubro/2o-turno-apenas-6-secoes-eleitorais-terao-mudancas-em-pernambuco),
que só 6 seções mudam, em Floresta e Buíque (aqui, essas 6 e mais 2 urnas em Tacaimbó, que entraram com o cadastro de
19/10, 11h27; as 3 de Recife que voltavam ao local de sempre saíram da lista com o de 15h27). O
[TRE-RS](https://www.tre-rs.jus.br/comunicacao/noticias/2026/Outubro/tre-rs-informa-sobre-mudancas-pontuais-nos-locais-de-votacao-no-2o-turno)
e o TRE-RN ([Tribuna do Norte](https://tribunadonorte.com.br/tn-nas-eleicoes-2026/tre-altera-locais-de-votacao-em-seis-municipios-do-rn-para-o-segundo-turno/))
confirmam seções que voltam ao local de sempre. As 111 urnas que ainda voltam ao local de sempre são a parte da lista
com mais chance de mudar até o dia 25: eram 306 no cadastro de 11h27, e 195 delas passaram a ficar no prédio do 1º
turno no de 15h27. O painel de seções alteradas, na atualização de 19/10, 11h27 (não exportada), listava 554 seções;
com o cadastro daquela hora, tirando as 46 urnas cujo local de sempre mudava de prédio sem trocar de número, contávamos
550 urnas, com a mesma contagem por estado, menos em MG (98 no painel, 94 aqui). Não exportamos nem conferimos o
painel depois do cadastro de 15h27.

**O efeito estimado é próximo de zero em todas as versões.** Pelo que se mediu em 2022, trocar de prédio não fez a
abstenção subir, então a soma fica perto de zero qualquer que seja o número de urnas:

| Cadastro | Urnas | Variação na vantagem de Flávio (IC 95%) | Se ninguém votasse nessas urnas | Lula nas que mudam × vizinhas (IC 95%) |
| --- | ---: | ---: | ---: | ---: |
| 17/10, 6h28 | 2.059 | −47 (−114 a +23) | 36.096 votos (1,6% da diferença) | −0,4 ponto (−1,2 a +0,4) |
| 17/10, 23h33 | 1.792 | −37 (−91 a +18) | 29.159 (1,3%) | −0,6 (−1,4 a +0,2) |
| 18/10, 11h27 | 1.733 | −36 (−87 a +16) | 28.652 (1,3%) | −0,3 (−1,0 a +0,4) |
| 18/10, 20h27 | 1.025 | −31 (−77 a +14) | 26.108 (1,2%) | +0,05 (−0,9 a +1,0) |
| 19/10, 11h27 | 596 | +4 (−15 a +22) | 588 (0,03%) | +0,2 (−1,0 a +1,5) |
| **19/10, 15h27** | **475** | **−0,1 (−21 a +19)** | **3.932 (0,18%)** | **−0,7 (−2,0 a +0,7)** |

A diferença nacional no 1º turno foi de 2,24 milhões de votos. "Se ninguém votasse" é um limite, não uma previsão: é a
vantagem líquida de Lula nessas urnas no 1º turno. Ele cresceu de 588 para 3.932 votos no cadastro de 15h27: as 195
urnas que saíram da lista deram 2.376 votos a mais a Flávio no 1º turno, e as 74 que entraram, 968 a mais a Lula.
Continua sendo um limite: pelo que se mediu em 2022, a troca de prédio não tira eleitores, e a estimativa segue perto
de zero.

**Atualizações anteriores.** Em 19/10 à tarde (commit `4925b73`), o cadastro de 19/10, 11h27 tirou 449 urnas (iam
voltar ao local de sempre e passaram a ficar no prédio do 1º turno; BA 107, PB 80, PE 79, SE 54, AL 47) e pôs 20, 11
delas em Ubá-MG: de 1.025 para 596 (`saida/versoes_19out.csv`). Em 19/10 de manhã (commit `917ba7a`), o cadastro de
18/10, 20h27 tirou 741 urnas (PR 138, MA 124, PI 98, MG 93, AP 79, RR 60) e pôs 33, entre elas 8 em Confresa-MT, o
caso que o TSE citou como exemplo de escola atingida pela chuva: de 1.733 para 1.025
(`saida/versoes_18out_noite.csv`). Em 18/10 à tarde (commit `2272612`), o cadastro de 18/10, 11h27 tirou 72 e pôs 13
em Januária-MG: de 1.792 para 1.733 (`saida/versoes_18out.csv`). Em 18/10 de manhã (commit `fa873d1`), o cadastro de
17/10, 23h33 tirou 267 e não pôs nenhuma: de 2.059 para 1.792 (`saida/versoes_17_18out.csv`). A primeira versão
(commit `943ab33`) também dizia que nenhuma urna muda no exterior; 9 mudam, em Colônia e em Praga (fora da conta, como
todo o exterior).

- **475 urnas funcionam no 2º turno num prédio diferente do 1º**, com 144.030 eleitores aptos, em 110 municípios de 23
  estados: 0,10% das urnas do país, com 0,09% dos votos válidos no 1º turno.
- **Metade dos eleitores vota no 2º turno a cerca de 470 m do prédio do 1º**, em linha reta. Para 79%, a distância é menor
  que 1 km; para 2,5%, de 5 km ou mais. Vale para as 258 urnas com coordenada confiável nos dois prédios (217 ficam sem
  distância). É a distância entre os prédios, não o deslocamento de cada eleitor: o endereço do eleitor não é público.
- **O painel do TSE mudou de critério.** A lista "Seções alteradas" do painel de estatísticas tinha, em 17/10, 4.864
  seções (4.863 urnas): comparava o local do 2º turno com o local *de cadastro*. Em 18/10 (7h09), passou a comparar
  com o local do 1º turno e listava 2.033 seções (2.023 urnas, 9 no exterior). Essa exportação é anterior aos cadastros
  de 18/10, 11h27 e 20h27, e de 19/10, 11h27 e 15h27: 335 das 475 urnas daqui estão nela; as 140 que entraram com esses
  cadastros, não. Das 1.679 urnas a mais no Brasil, 1.475 têm, no cadastro atual, o mesmo local nos dois turnos (entre
  elas, as 1.457 que saíram da lista com esses quatro cadastros). As outras 204 têm o mesmo endereço de local nos dois
  turnos: 168 só mudam de nome, 32 só de grafia e 4 só de número. Em 33 das 168, o nome muda por completo e não dá para
  saber se é o mesmo prédio.
- **Como a lista encolheu.** A cada versão do cadastro que baixamos, a lista diminuiu (2.059, 1.792, 1.733, 1.025, 596,
  475), sempre do mesmo jeito: 1.724 urnas que iam voltar ao local de sempre passaram a ficar no prédio provisório do
  1º turno, e nenhuma fez o caminho contrário. Não foi um estado só (17 estados, 270 municípios e 286 zonas; o Paraná,
  o maior, tem 13%), mas a proporção varia muito: em PE (198 de 198), SP (163 de 163), BA (127 de 127), AL (101 de
  101), PB (96 de 96), SE (70 de 70), RR (60 de 60), AM (47 de 48) e MA (176 de 179), todas ou quase todas as que iam
  voltar passaram a ficar no prédio do 1º turno; no RN (0 de 9) e no RS (2 de 8), quase nenhuma. Só um prédio
  provisório ficou dividido: em Manaus, zona 62, 4 urnas que iam voltar ao local de sempre passaram a ficar na E. M.
  João Goulart, e 1 continua voltando. Das 6.592 urnas fora do local de sempre no 1º turno, 28% voltariam a ele pelo
  primeiro cadastro e 1,7% pelo atual; em 2022, pelo cadastro final, 15,1% (a comparação justa é entre cadastros
  finais). O voto em Lula nas 1.724 (51,3%) e nas 111 que continuam voltando (44,5%) fica perto do esperado pelos
  municípios (51,4% e 45,6%). O cadastro não diz o motivo nem quem decidiu (`12_renovadas.py`).
- **Por que não 4,3 mil.** O TSE divulgou em 16/10, e a imprensa reproduziu, que 4.352 seções mudaram de local, com
  dados até 16/10. As "499.248 seções instaladas" citadas são urnas, a mesma unidade usada aqui. O TSE não informou o
  critério. A distribuição por estado não fecha com os dados seguintes: o TSE cita 431 seções no Rio de Janeiro, onde o
  painel tinha 47 em 17/10, 19 em 18/10 e nenhuma em 19/10 (11h27), e 19 urnas mudam de prédio do 1º para o 2º turno.
- **Quando o cadastro não bate.** Quando o local muda de número e de nome, mas o cadastro reescreveu o endereço do
  local de sempre para o do prédio provisório, a urna quase certamente continua no mesmo prédio e fica de fora. Na
  primeira versão eram 32 urnas; as 12 de Timóteo-MG passaram a aparecer no mesmo prédio nos dois turnos no cadastro de
  17/10, 23h33, e as 20 de São Paulo, no de 18/10, 20h27, o que confirma o critério. No cadastro atual, nenhuma urna
  está nesse caso. Outras 28 têm o mesmo endereço nos dois turnos, em geral genérico ("S/N", povoado, aldeia), e
  continuam na conta com aviso no mapa.
- **No 1º turno, os eleitores dessas urnas votaram mais em Lula que o país** (48,5% para Lula e 44,9% para Flávio; no
  país, 45,2% contra 47,0%), perto do esperado pelos municípios onde estão (49,3%). O percentual muda de uma versão da
  lista para outra: 52,3% nas 1.025 urnas do cadastro de 18/10, 20h27, e 46,7% nas 596 do de 19/10, 11h27. Comparado
  com o das urnas do mesmo município e da mesma zona eleitoral que não mudam, não há diferença detectável (−0,7 ponto
  para Lula, intervalo de 95% de −2,0 a +0,7). Por local de votação (`09_por_local.py`), com as 475 urnas a associação
  entre voto em Lula e mudança aparece entre todos os locais do país, no limite da significância (+0,02 ponto por 10
  pontos de Lula, intervalo de +0,00 a +0,03), porque as mudanças estão mais em lugares onde Lula vence; comparando
  locais do mesmo estado ou do mesmo município, não aparece em nenhuma das medidas do script (votos em blocos de 10
  mil e percentual de Lula, com o local de cadastro ou o do 1º turno como unidade). Foi assim em quase todas as
  versões da lista; só com as 596 urnas do cadastro de 19/10, 11h27, não aparecia nem entre todos os locais (+0,01,
  intervalo de −0,01 a +0,02). Com a lista do painel de 17/10, que comparava com o local de cadastro, ela aparece
  dentro do estado em várias medidas, como na análise de
  [@DavidDinizK](https://x.com/DavidDinizK/status/2111616001443795222), mas não com o percentual de Lula e os votos
  válidos do local. A diferença vem da lista e da forma de medir, e a diferença entre as listas não é estatisticamente
  significativa. Em 2022, 47% dos eleitores das urnas que mudaram estavam no Nordeste; na lista atual de 2026, 25%
  (49% no cadastro de 18/10, 20h27). O voto em Lula nas urnas que mudam fica perto do esperado pelos lugares onde
  estão (48,5%, contra 46,3% pelo estado e 49,3% pelo município; `11_geografia.py`).
- **Em 2022, trocar de prédio não mostrou aumento de abstenção.** Nas 1.506 urnas que trocaram de prédio entre os
  turnos, a abstenção variou 0,08 ponto a menos que nas vizinhas do mesmo município e zona (intervalo de −0,23 a
  +0,08). Em outras comparações, vai de −0,19 a +0,14 ponto. É uma comparação entre urnas, não um experimento:
  essas urnas já tinham abstenção 0,8 ponto acima das vizinhas no 1º turno, e a conta supõe que, sem a mudança, a
  abstenção teria variado do mesmo jeito nos dois grupos.
- **O efeito estimado no resultado é próximo de zero.** Se 2026 repetir 2022, a vantagem de Flávio praticamente não
  mudaria (−0,1 voto; intervalo de −21 a +19; entre −24 e +28 nas outras comparações), diante de 2,24 milhões no 1º
  turno. A conta supõe que quem deixa de votar votaria como o resto da sua urna. Num cenário limite, se ninguém
  votasse nessas urnas, e com a abstenção igual dos dois lados, Lula perderia 3.932 votos líquidos (0,18% da
  diferença).

O voto para governador não foi calculado: o arquivo nacional de votação por seção do TSE traz só presidente. Os
estados com 2º turno para governador (AC, AM, ES, RN, TO e DF) têm 46 urnas mudando de prédio (AM 6, ES 14, RN 24 e
TO 2), com 14 mil eleitores; o AC e o DF não têm nenhuma.

Para quem faltou no 1º turno, a referência é o último local onde votou (em geral o de 2024), e essa comparação não foi
feita. O local de cadastro serve de aproximação: 6.784 urnas votam no 2º turno fora dele, com 2,04 milhões de eleitores,
dos quais 413 mil faltaram no 1º turno. Em 6.459 dessas urnas a mudança já valia no dia 4, e a abstenção nelas foi de
20,2%, perto dos 20,8% do país (`fora_do_cadastro_2t` em `saida/numeros.json`).

**A saída do local de sempre no 1º turno teve efeito pequeno na abstenção** (`13_abstencao_1t.py`). Nas 6.588 urnas
que votaram no 1º turno de 2026 fora do local de cadastro, a abstenção foi 0,66 ponto maior que nas vizinhas do mesmo
município e zona que votaram no local de cadastro (intervalo de 95% de 0,49 a 0,83). Em 2022, as mesmas urnas tinham a
abstenção das vizinhas (+0,03, de −0,18 a +0,23), e a variação de 2022 para 2026 foi 0,62 ponto maior (de 0,47 a
0,76; 5.180 urnas com a mesma seção e o mesmo local de cadastro nos dois anos). São cerca de 12 mil eleitores a menos,
em 1,98 milhão. Como essas urnas deram 50,1% a Lula e 43,0% a Flávio, equivale a cerca de 800 votos líquidos a menos
para Lula no 1º turno (de 600 a 1.000), 0,04% da diferença nacional. Esse efeito já está no resultado do dia 4.

## Como foi feito

A urna é a seção principal; os eleitores de seção agregada votam nela. Os aptos são o eleitorado federal de cada urna em cada turno.
Uma urna muda de prédio quando o número do local no 2º turno é diferente do 1º (salvo se o nome e o endereço
continuarem iguais), ou quando o número é o mesmo mas o nome e o endereço mudam juntos. Coordenada só vale se cair dentro do
município, pela malha do IBGE. Os detalhes estão no cabeçalho de cada script.

| Script | O que faz |
| --- | --- |
| `01_votos_1t.py` | Votos para presidente por seção: 1º turno de 2026 e os dois turnos de 2022 |
| `02_mudancas.py` | Urnas que mudam de prédio entre os turnos, em 2026 e 2022, e a conferência com o painel do TSE |
| `03_impacto.py` | Efeito da troca sobre a abstenção em 2022, sensibilidade e o peso das mudanças de 2026 na margem |
| `04_exportar_web.py` | Dados da página (`docs/dados.json`) |
| `05_imagem_x.py` | Cartão 1600 × 900 para redes sociais (`saida/imagem_x.png`) |
| `06_contornos.py` | Contornos de estados e municípios para o mapa (`docs/contornos.json`) |
| `07_versoes.py` | O que mudou entre a lista do cadastro de 19/10, 11h27 (commit `e8cf919`) e a atual (`saida/versoes_19out_tarde.csv`). As comparações anteriores ficam no git: entre os cadastros de 18/10, 20h27 e 19/10, 11h27 (`saida/versoes_19out.csv`, commit `4925b73`), entre os de 18/10, 11h27 e 20h27 (`saida/versoes_18out_noite.csv`, commit `917ba7a`), entre os de 17/10, 23h33 e 18/10, 11h27 (`saida/versoes_18out.csv`, commit `2272612`) e entre os de 17/10, 6h28 e 23h33 (`saida/versoes_17_18out.csv`, commit `fa873d1`) |
| `08_imagem_distancia.py` | Cartão 1600 × 900 com a distância entre o prédio do 1º e o do 2º turno (`saida/imagem_distancia.png`) |
| `09_por_local.py` | Locais de votação com urna na lista e voto no 1º turno, com as listas do painel de 17/10 e 18/10 e a daqui |
| `10_imagem_por_local.py` | Cartão 1600 × 900 com os locais na lista por faixa de voto em Lula (`saida/imagem_por_local.png`) |
| `11_geografia.py` | Onde ficam as urnas que mudam, em 2022 e 2026, e o voto esperado pela geografia |
| `12_renovadas.py` | Como a lista encolheu nas seis versões do cadastro: urnas que iam voltar ao local de sempre e passaram a ficar no prédio do 1º turno, por estado, e a taxa de volta comparada com 2022 (rode depois de 07 e antes de 04) |
| `13_abstencao_1t.py` | Abstenção no 1º turno nas urnas que já votaram fora do local de cadastro, comparada com as vizinhas, em 2026 e desde 2022 (`saida/abstencao_1t.json`) |
| `14_imagem_versoes.py` | Cartão 1600 × 900 com as urnas e o efeito estimado em cada versão do cadastro (`saida/imagem_versoes.png`) |
| `15_capa_linkedin.py` | Capa 1920 × 1080 para o artigo no LinkedIn (`saida/capa_linkedin.png`) |
| `ibge.py` | Malhas e códigos de município do IBGE, usados por 02 e 06 |

Para rodar do zero, baixe para `dados/` os arquivos do [portal de dados abertos do TSE](https://dadosabertos.tse.jus.br/)
(cerca de 630 MB, fora do git) e rode os scripts em ordem com `python -P scripts/0N_....py`:

- `votacao_secao_2026_BR.zip` e `votacao_secao_2022_BR.zip` (Resultados › Votação por seção eleitoral)
- `eleitorado_local_votacao_2026.zip` e `eleitorado_local_votacao_2022.zip` (Eleitorado › Eleitorado por local de
  votação). O de 2026 usado aqui foi gerado em 19/10/2026 às 15h27 (Brasília) e já traz o 2º turno. O portal guarda só
  a versão mais recente, então o resultado pode mudar se o TSE publicar outra. O CDN pode entregar uma cópia antiga em
  cache: baixe com um parâmetro qualquer no fim do endereço (por exemplo, `?x=1`) e confira `DT_GERACAO` e `HH_GERACAO`.
- `painel_secoes_alteradas_2026.csv`: a lista do painel de estatísticas (Eleitorado › Capilaridade › Seções alteradas,
  atualização de 18/10, 7h09), exportada pelo botão "Gerar arquivos". O arquivo vem como
  `secoes_eleitorais_alteradas_2t-pais_2026.csv`.
- Para `09_por_local.py`: o cadastro gerado em 17/10 às 6h28, em
  `dados/anteriores/eleitorado_local_votacao_2026_gerado_17out_0932utc.zip`. O portal não guarda mais essa versão.
- Também ficam em `dados/anteriores/` (fora do git), para conferência: os cadastros gerados em 17/10 às 23h33
  (`eleitorado_local_votacao_2026_gerado_18out_0233utc.zip`), em 18/10 às 11h27
  (`eleitorado_local_votacao_2026_gerado_18out_1427utc.zip`), em 18/10 às 20h27
  (`eleitorado_local_votacao_2026_gerado_18out_2327utc.zip`) e em 19/10 às 11h27
  (`eleitorado_local_votacao_2026_gerado_19out_1427utc.zip`), a exportação do painel de 18/10, 7h09
  (`painel_18out_0709.csv.zip`), e as listas de urnas das versões anteriores (`urnas_mudadas_2026_17out.csv`,
  `urnas_mudadas_2026_18out_manha.csv`, a do cadastro de 17/10, 23h33, `urnas_mudadas_2026_18out_tarde.csv`, a do
  de 18/10, 11h27, `urnas_mudadas_2026_18out_noite.csv`, a do de 18/10, 20h27, e
  `urnas_mudadas_2026_19out_manha.csv`, a do de 19/10, 11h27).

As malhas do IBGE são baixadas sozinhas para `dados/ibge/` na primeira execução. Precisa de Python com pandas, numpy,
shapely e matplotlib. As tabelas pequenas ficam em `saida/`; as tabelas completas por urna (`saida/urnas_*.csv.gz` e
`saida/votos_*_secao.csv.gz`) são geradas pelos scripts e não vão para o git.

Principais saídas:

- `saida/urnas_mudadas_2026.csv`: as 475 urnas, com prédio antigo e novo, critério, distância, aviso de mesmo
  endereço e voto no 1º turno
- `saida/mesmo_predio_2026.csv`: as urnas retiradas porque o cadastro reescreveu o endereço (nenhuma no cadastro atual)
- `saida/painel_tse.csv`: as 2.015 seções do painel de 18/10 no Brasil, com a classificação de cada uma aqui e, quando
  não contam, o motivo
- `saida/versoes_19out_tarde.csv`: as urnas da lista do cadastro de 19/10, 11h27 e da atual, com o que mudou no cadastro
- `saida/versoes_19out.csv`, `saida/versoes_18out_noite.csv`, `saida/versoes_18out.csv` e `saida/versoes_17_18out.csv`:
  as comparações anteriores (18/10, 20h27 × 19/10, 11h27; 18/10, 11h27 × 20h27; 17/10, 23h33 × 18/10, 11h27; 17/10,
  6h28 × 23h33)
- `saida/impacto_2022.csv` e `saida/impacto_uf_2026.csv`: efeito medido em 2022 e resumo por estado
- `saida/geografia.json`, `saida/geografia_regioes.csv` e `saida/geografia_ufs.csv`: as urnas que mudam por região e estado, em 2022 e 2026
- `saida/por_local_faixas.csv`: percentual de locais na lista por faixa de voto em Lula, no país e comparado com o estado e o município
- `saida/por_local.csv`: regressão por local de votação (chance de o local estar na lista e voto no 1º turno), com as três listas
- `saida/renovadas_uf.csv` e `saida/renovadas.json`: as urnas que saíram da lista a cada versão do cadastro, por estado, e a
  taxa de volta ao local de sempre em cada versão e em 2022
- `saida/revisar_distancias.csv`: mudanças de mais de 10 km, para conferência
- `saida/numeros.json`: todos os números da página

## Fontes

- TSE, [dados abertos](https://dadosabertos.tse.jus.br/): votação por seção e cadastro de locais de votação, 2022 e 2026.
- IBGE, [API de malhas](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3): contornos de estados e municípios.
- TSE, [painel de estatísticas do eleitorado](https://sig.tse.jus.br/ords/dwapr/r/seai/sig-eleicao-eleitorado/home),
  Capilaridade › Seções alteradas (atualizações de 17/10 e 18/10).
- Justiça Eleitoral, [Fato ou Boato](https://www.justicaeleitoral.jus.br/fato-ou-boato/checagens/2026/mudancas-de-locais-de-votacao-no-2o-turno-seguem-regras-e-atendem-a-necessidades-de-seguranca)
  e [notícia do TSE](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/entenda-por-que-a-justica-eleitoral-trocou-o-endereco-de-algumas-secoes-para-o-2o-turno).
- As 4.352 seções: [Agência Brasil](https://agenciabrasil.ebc.com.br/radioagencia-nacional/politica/audio/2026-10/tse-anuncia-alteracao-de-4352-locais-de-votacao-para-o-segundo-turno)
  (16/10) e [Correio](https://www.correio24horas.com.br/eleicoes/eleicoes-2026-bahia-tem-312-secoes-eleitorais-com-locais-de-votacao-alterados-para-o-2-turno-1026), entre outros.
- Governo do Rio decidido no 1º turno: [Correio da Manhã](https://www.correiodamanha.com.br/estado-do-rio/2026/10/327334-tre-rj-proclama-douglas-ruas-governador-eleito-no-primeiro-turno.html).

## Licença

Código sob a licença MIT (`LICENSE`). Dados derivados em `saida/` e `docs/` sob
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt-br): pode reusar, citando Matheus Dalmolin, o TSE e o IBGE.
