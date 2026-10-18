# Urnas que mudam de lugar no 2º turno de 2026

A Justiça Eleitoral trocou o endereço de algumas seções entre o 1º e o 2º turno de 2026. Este repositório mostra
quais urnas mudam de prédio, em quem os eleitores dessas urnas votaram no 1º turno e quanto isso pode pesar no resultado.

**Página com o mapa:** https://matheusgsd.github.io/secoes-2turno-2026/

## O que os números mostram

Cadastro de locais do TSE gerado em 18/10/2026 às 11h27 (Brasília), baixado em 18/10. O TSE ainda pode mudar locais
até o dia 25; se publicar outra versão, a página e este README serão refeitos, com a mudança registrada aqui.

**Atualização de 18/10, à tarde.** A versão anterior (commit `01b4452`) usava o cadastro gerado em 17/10 às 23h37 e
contava 1.792 urnas. No cadastro de 18/10, 11h27, 72 delas, com 22.247 eleitores, deixaram de mudar: iam voltar ao
local de sempre e agora ficam no prédio do 1º turno (40 em Bacabal-MA; 20 em Alagoas: 7 em Matriz de Camaragibe, 6 em
Coité do Nóia, 5 em Igaci e 2 em Porto de Pedras; 9 em Pernambuco: 6 em Jaboatão dos Guararapes, 2 no Recife e 1 em
Solidão; 3 em Botucatu-SP). Entraram 13 urnas, todas em Januária-MG (zona 148), que votavam no local de sempre nos dois
turnos e agora saem dele no 2º. São 1.733 urnas. A lista está em `saida/versoes_18out.csv`. A exportação do painel do
TSE usada na conferência (18/10, 7h09) é anterior a esse cadastro: 1.720 das 1.733 urnas estão nela (as 13 de
Januária, não), e 72 urnas do painel são as que saíram da lista, com o mesmo local nos dois turnos no cadastro atual.

**Atualização de 18/10, de manhã.** A primeira versão (commit `943ab33`) usava o cadastro gerado em 17/10 às 6h32 e
contava 2.059 urnas. No cadastro de 17/10, 23h37, 267 delas, com 83.179 eleitores, deixaram de mudar: iam voltar ao
local de sempre e passaram a ficar no prédio do 1º turno. Nenhuma urna entrou. A lista está em
`saida/versoes_17_18out.csv`. A primeira versão também dizia que nenhuma urna muda no exterior; 9 mudam, em Colônia e
em Praga (fora da conta, como todo o exterior).

- **1.733 urnas funcionam no 2º turno num prédio diferente do 1º**, com 509.645 eleitores aptos, em 290 municípios de 24
  estados: 0,35% das urnas do país, com 0,3% dos votos válidos no 1º turno.
- **Metade dos eleitores vota no 2º turno a cerca de 420 m do prédio do 1º**, em linha reta. Para 88%, a distância é menor
  que 1 km; para 1,8%, de 5 km ou mais. Vale para as 1.354 urnas com coordenada confiável nos dois prédios (379 ficam sem
  distância). É a distância entre os prédios, não o deslocamento de cada eleitor: o endereço do eleitor não é público.
- **O painel do TSE mudou de critério.** A lista "Seções alteradas" do painel de estatísticas tinha, em 17/10, 4.864
  seções (4.863 urnas): comparava o local do 2º turno com o local *de cadastro*. Em 18/10 (7h09), passou a comparar
  com o local do 1º turno e lista 2.033 seções (2.023 urnas, 9 no exterior). A exportação é anterior ao cadastro de
  18/10, 11h27: 1.720 das 1.733 urnas daqui estão nela; as 13 de Januária-MG, que entraram com o cadastro novo, não. Das
  294 urnas a mais no Brasil, 72 têm, no cadastro atual, o mesmo local nos dois turnos (são as que saíram da lista). As
  outras 222 têm o mesmo endereço de local nos dois turnos: 162 só mudam de nome, 32 só de grafia,
  8 só de número; outras 20 têm o endereço reescrito no cadastro (abaixo). Em 33 das 162, o nome muda por completo e
  não dá para saber se é o mesmo prédio.
- **Por que não 4,3 mil.** O TSE divulgou em 16/10, e a imprensa reproduziu, que 4.352 seções mudaram de local, com
  dados até 16/10. As "499.248 seções instaladas" citadas são urnas, a mesma unidade usada aqui. O TSE não informou o
  critério. A distribuição por estado não fecha com os dados seguintes: o TSE cita 431 seções no Rio de Janeiro, onde o
  painel tinha 47 em 17/10 e tem 19 em 18/10, e 19 urnas mudam de prédio do 1º para o 2º turno.
- **Quando o cadastro não bate.** 20 urnas (São Paulo) ficaram de fora: o local muda de número e de nome, mas o
  cadastro reescreveu o endereço do local de sempre para o do prédio provisório, e a urna quase certamente continua no
  mesmo prédio. Na primeira versão eram 32; as 12 de Timóteo-MG agora aparecem no mesmo prédio nos dois turnos, o que
  confirma o critério. Outras 69 têm o mesmo endereço nos dois turnos, em geral genérico ("S/N", povoado, aldeia), e
  continuam na conta com aviso no mapa.
- **No 1º turno, os eleitores dessas urnas votaram mais em Lula** (50,4% contra 43,0% de Flávio; no país, 45,2% contra 47,0%).
  É geografia: 45% dos eleitores dessas urnas estão no Nordeste. Comparado com o das urnas do mesmo município e da mesma zona eleitoral
  que não mudam, não há diferença detectável (−0,3 ponto para Lula, intervalo de 95% de −1,0 a +0,4). Por local
  de votação (`09_por_local.py`), locais mais lulistas têm mais chance de ter urna mudando entre todos os locais do país,
  nas três listas (painel de 17/10, painel de 18/10 e as 1.733 urnas). Comparando locais do mesmo estado ou do mesmo
  município, a associação não aparece com as duas listas que medem a mudança do 1º para o 2º turno, em nenhuma das
  formas de medir testadas; algumas dão negativa. Com a lista do painel de 17/10, que comparava com o local de cadastro,
  ela aparece dentro do estado em várias medidas, como na análise de
  [@DavidDinizK](https://x.com/DavidDinizK/status/2111616001443795222), mas não com o percentual de Lula e os votos
  válidos do local. A diferença vem da lista e da forma de medir, e a diferença entre as listas não é estatisticamente
  significativa. As mudanças se concentram no Nordeste, como em 2022 (lá estão 47% dos eleitores das urnas que mudam
  em 2022 e 45% em 2026), e o voto em Lula nessas urnas fica perto do esperado pelos estados onde estão (50,4% contra
  49,5%; `11_geografia.py`).
- **Em 2022, trocar de prédio não mostrou aumento de abstenção.** Nas 1.506 urnas que trocaram de prédio entre os
  turnos, a abstenção variou 0,08 ponto a menos que nas vizinhas do mesmo município e zona (intervalo de −0,23 a
  +0,08). Em outras comparações, vai de −0,19 a +0,14 ponto. É uma comparação entre urnas, não um experimento:
  essas urnas já tinham abstenção 0,8 ponto acima das vizinhas no 1º turno, e a conta supõe que, sem a mudança, a
  abstenção teria variado do mesmo jeito nos dois grupos.
- **O efeito estimado no resultado é próximo de zero.** Se 2026 repetir 2022, a vantagem de Flávio cairia 36 votos
  (intervalo de −87 a +16; entre −152 e +138 nas outras comparações), diante de 2,24 milhões no 1º turno. A conta supõe que quem deixa de votar votaria como o resto da sua urna. Num
  cenário limite, se ninguém votasse nessas urnas, e com a abstenção igual dos dois lados, Lula perderia 28.652 votos líquidos (1,3% da
  diferença).

O voto para governador não foi calculado: o arquivo nacional de votação por seção do TSE traz só presidente. Os
estados com 2º turno para governador (AC, AM, ES, RN, TO e DF) têm 136 urnas mudando de prédio, com 39 mil eleitores.

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
| `07_versoes.py` | O que mudou entre a lista do cadastro de 17/10, 23h37 (commit `01b4452`) e a atual (`saida/versoes_18out.csv`). A comparação anterior, entre as listas dos cadastros de 17/10, 6h32 (commit `943ab33`) e 23h37, está em `saida/versoes_17_18out.csv`, gerada no commit `fa873d1` |
| `08_imagem_distancia.py` | Cartão 1600 × 900 com a distância entre o prédio do 1º e o do 2º turno (`saida/imagem_distancia.png`) |
| `09_por_local.py` | Locais de votação com urna na lista e voto no 1º turno, com as listas do painel de 17/10 e 18/10 e a daqui |
| `10_imagem_por_local.py` | Cartão 1600 × 900 com os locais na lista por faixa de voto em Lula (`saida/imagem_por_local.png`) |
| `11_geografia.py` | Onde ficam as urnas que mudam, em 2022 e 2026, e o voto esperado pela geografia |
| `ibge.py` | Malhas e códigos de município do IBGE, usados por 02 e 06 |

Para rodar do zero, baixe para `dados/` os arquivos do [portal de dados abertos do TSE](https://dadosabertos.tse.jus.br/)
(cerca de 630 MB, fora do git) e rode os scripts em ordem com `python -P scripts/0N_....py`:

- `votacao_secao_2026_BR.zip` e `votacao_secao_2022_BR.zip` (Resultados › Votação por seção eleitoral)
- `eleitorado_local_votacao_2026.zip` e `eleitorado_local_votacao_2022.zip` (Eleitorado › Eleitorado por local de
  votação). O de 2026 usado aqui foi gerado em 18/10/2026 às 11h27 (Brasília) e já traz o 2º turno. O portal guarda só
  a versão mais recente, então o resultado pode mudar se o TSE publicar outra.
- `painel_secoes_alteradas_2026.csv`: a lista do painel de estatísticas (Eleitorado › Capilaridade › Seções alteradas,
  atualização de 18/10, 7h09), exportada pelo botão "Gerar arquivos". O arquivo vem como
  `secoes_eleitorais_alteradas_2t-pais_2026.csv`.
- Para `09_por_local.py`: o cadastro gerado em 17/10 às 6h28, em
  `dados/anteriores/eleitorado_local_votacao_2026_gerado_17out_0932utc.zip`. O portal não guarda mais essa versão.
- Também ficam em `dados/anteriores/` (fora do git), para conferência: o cadastro gerado em 17/10 às 23h37, usado na
  versão anterior (`eleitorado_local_votacao_2026_gerado_18out_0233utc.zip`), a exportação do painel de 18/10, 7h09
  (`painel_18out_0709.csv.zip`), e as listas de urnas das versões anteriores (`urnas_mudadas_2026_17out.csv` e
  `urnas_mudadas_2026_18out_manha.csv`, a do cadastro de 17/10, 23h37).

As malhas do IBGE são baixadas sozinhas para `dados/ibge/` na primeira execução. Precisa de Python com pandas, numpy,
shapely e matplotlib. As tabelas pequenas ficam em `saida/`; as tabelas completas por urna (`saida/urnas_*.csv.gz` e
`saida/votos_*_secao.csv.gz`) são geradas pelos scripts e não vão para o git.

Principais saídas:

- `saida/urnas_mudadas_2026.csv`: as 1.733 urnas, com prédio antigo e novo, critério, distância, aviso de mesmo
  endereço e voto no 1º turno
- `saida/mesmo_predio_2026.csv`: as 20 urnas retiradas porque o cadastro reescreveu o endereço
- `saida/painel_tse.csv`: as 2.015 seções do painel de 18/10 no Brasil, com a classificação de cada uma aqui e, quando
  não contam, o motivo
- `saida/versoes_18out.csv`: as urnas da lista do cadastro de 17/10, 23h37 e da atual, com o que mudou no cadastro
- `saida/versoes_17_18out.csv`: a comparação anterior, entre as listas dos cadastros de 17/10, 6h32 e 23h37
- `saida/impacto_2022.csv` e `saida/impacto_uf_2026.csv`: efeito medido em 2022 e resumo por estado
- `saida/geografia.json`, `saida/geografia_regioes.csv` e `saida/geografia_ufs.csv`: as urnas que mudam por região e estado, em 2022 e 2026
- `saida/por_local_faixas.csv`: percentual de locais na lista por faixa de voto em Lula, no país e comparado com o estado e o município
- `saida/por_local.csv`: regressão por local de votação (chance de o local estar na lista e voto no 1º turno), com as três listas
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
