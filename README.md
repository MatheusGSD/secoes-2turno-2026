# Urnas que mudam de lugar no 2º turno de 2026

A Justiça Eleitoral trocou o endereço de algumas seções entre o 1º e o 2º turno de 2026. Este repositório mostra
quais urnas mudam de prédio, em quem esses eleitores votaram no 1º turno e quanto isso pode pesar no resultado.

**Página com o mapa:** https://matheusgsd.github.io/secoes-2turno-2026/

## O que os números mostram

Dados do TSE de 17/10/2026, às 6h28. O TSE ainda pode mudar locais até o dia 25.

- **2.091 urnas votam no 2º turno num prédio diferente do 1º**, com 620.947 eleitores aptos, em 342 municípios de 24
  estados: 0,42% das urnas e 0,4% dos votos válidos do país. Metade muda até 415 m.
- **O painel do TSE não mostra isso.** A lista "Seções alteradas" do painel de estatísticas tem 4.864 seções (4.863
  urnas), mas compara o local do 2º turno com o local *de cadastro*. 4.695 delas já votaram nesse mesmo prédio no 1º
  turno. E ficam de fora 1.877 urnas que voltam ao local de sempre, depois de terem sido deslocadas no 1º turno, e 46
  cujo local de sempre passou a outro prédio sem trocar de número no cadastro. Só 168 urnas estão nas duas contas.
- **Por que não 4,3 mil.** O TSE divulgou em 16/10, e a imprensa reproduziu, que 4.352 seções mudaram de local, com
  dados até 16/10. As "499.248 seções instaladas" citadas são urnas, a mesma unidade usada aqui. O TSE não informou o
  critério. A distribuição por estado não fecha com os dados de 17/10: são 431 seções no Rio de Janeiro, onde o painel
  tem 47 e só 19 urnas mudam de prédio do 1º para o 2º turno.
- **No 1º turno, essas urnas votaram mais em Lula** (50,6% contra 42,8% de Flávio; no país, 45,2% contra 47,0%).
  É geografia: 48% dos eleitores estão no Nordeste. Comparadas com as urnas que não mudam do mesmo município e da mesma
  zona eleitoral, votaram em média como elas (−0,4 ponto para Lula, intervalo de 95% de −1,1 a +0,4).
- **Em 2022, trocar de prédio não mostrou aumento de abstenção.** Nas 1.506 urnas que trocaram de prédio entre os
  turnos, a abstenção variou 0,08 ponto a menos que nas vizinhas do mesmo município e zona (intervalo de −0,23 a
  +0,08). Em outras comparações, vai de −0,19 a +0,14 ponto. É uma comparação observacional: essas urnas já tinham
  abstenção 0,8 ponto acima das vizinhas no 1º turno.
- **O efeito estimado no resultado é próximo de zero.** Se 2026 repetir 2022, a vantagem de Flávio muda em −48 votos
  (intervalo de −116 a +23; entre −203 e +182 nas outras comparações), diante de 2,24 milhões no 1º turno. Mesmo que
  ninguém votasse nessas urnas, e com a abstenção igual dos dois lados, Lula perderia 36.485 votos líquidos (1,6% da
  diferença).

O voto para governador não foi calculado: o arquivo nacional de votação por seção do TSE traz só presidente. Os
estados com 2º turno para governador (AC, AM, ES, RN, TO e DF) têm 136 urnas mudando de prédio, com 39 mil eleitores.

## Como foi feito

A urna é a seção principal; seção agregada vota nela. Os aptos são o eleitorado federal de cada urna em cada turno.
Uma urna muda de prédio quando o número do local no 2º turno é diferente do 1º (salvo se nome e endereço continuam
iguais), ou quando o número é o mesmo mas nome e endereço mudaram juntos. Coordenada só vale se cair dentro do
município, pela malha do IBGE. Os detalhes estão no cabeçalho de cada script.

| Script | O que faz |
| --- | --- |
| `01_votos_1t.py` | Votos para presidente por seção: 1º turno de 2026 e os dois turnos de 2022 |
| `02_mudancas.py` | Urnas que mudam de prédio entre os turnos, em 2026 e 2022, e a conferência com o painel do TSE |
| `03_impacto.py` | Efeito da troca sobre a abstenção em 2022, sensibilidade e o peso das mudanças de 2026 na margem |
| `04_exportar_web.py` | Dados da página (`docs/dados.json`) |
| `05_imagem_x.py` | Cartão 1600 × 900 para redes sociais (`saida/imagem_x.png`) |
| `06_contornos.py` | Contornos de estados e municípios para o mapa (`docs/contornos.json`) |
| `ibge.py` | Malhas e códigos de município do IBGE, usados por 02 e 06 |

Para rodar do zero, baixe para `dados/` os arquivos do [portal de dados abertos do TSE](https://dadosabertos.tse.jus.br/)
(cerca de 630 MB, fora do git) e rode os scripts em ordem com `python -P scripts/0N_....py`:

- `votacao_secao_2026_BR.zip` e `votacao_secao_2022_BR.zip` (Resultados › Votação por seção eleitoral)
- `eleitorado_local_votacao_2026.zip` e `eleitorado_local_votacao_2022.zip` (Eleitorado › Eleitorado por local de
  votação). O de 2026 usado aqui foi gerado em 17/10/2026 e já traz o 2º turno.

As malhas do IBGE são baixadas sozinhas para `dados/ibge/` na primeira execução. Precisa de Python com pandas, numpy,
shapely e matplotlib. As tabelas pequenas ficam em `saida/`; as tabelas completas por urna (`saida/urnas_*.csv.gz` e
`saida/votos_*_secao.csv.gz`) são geradas pelos scripts e não vão para o git.

Principais saídas:

- `saida/urnas_mudadas_2026.csv`: as 2.091 urnas, com prédio antigo e novo, critério, distância e voto no 1º turno
- `saida/painel_tse_4864.csv`: as seções do painel do TSE, marcando quais mudam de fato do 1º para o 2º turno
- `saida/impacto_2022.csv` e `saida/impacto_uf_2026.csv`: efeito medido em 2022 e resumo por estado
- `saida/revisar_distancias.csv`: mudanças de mais de 10 km, para conferência
- `saida/numeros.json`: todos os números da página

## Fontes

- TSE, [dados abertos](https://dadosabertos.tse.jus.br/): votação por seção e cadastro de locais de votação, 2022 e 2026.
- IBGE, [API de malhas](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3): contornos de estados e municípios.
- TSE, [painel de estatísticas do eleitorado](https://sig.tse.jus.br/ords/dwapr/r/seai/sig-eleicao-eleitorado/home),
  Capilaridade › Seções alteradas.
- Justiça Eleitoral, [Fato ou Boato](https://www.justicaeleitoral.jus.br/fato-ou-boato/checagens/2026/mudancas-de-locais-de-votacao-no-2o-turno-seguem-regras-e-atendem-a-necessidades-de-seguranca)
  e [notícia do TSE](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/entenda-por-que-a-justica-eleitoral-trocou-o-endereco-de-algumas-secoes-para-o-2o-turno).
- As 4.352 seções: [Agência Brasil](https://agenciabrasil.ebc.com.br/radioagencia-nacional/politica/audio/2026-10/tse-anuncia-alteracao-de-4352-locais-de-votacao-para-o-segundo-turno)
  (16/10) e [Correio](https://www.correio24horas.com.br/eleicoes/eleicoes-2026-bahia-tem-312-secoes-eleitorais-com-locais-de-votacao-alterados-para-o-2-turno-1026), entre outros.
- Governo do Rio decidido no 1º turno: [Correio da Manhã](https://www.correiodamanha.com.br/estado-do-rio/2026/10/327334-tre-rj-proclama-douglas-ruas-governador-eleito-no-primeiro-turno.html).

## Licença

Código sob a licença MIT (`LICENSE`). Dados derivados em `saida/` e `docs/` sob
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt-br): pode reusar, citando Matheus Dalmolin, o TSE e o IBGE.
