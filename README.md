# Urnas que mudam de lugar no 2º turno de 2026

A Justiça Eleitoral trocou o endereço de algumas seções entre o 1º e o 2º turno de 2026. Este repositório mostra
quais urnas mudam de prédio, em quem esses eleitores votaram no 1º turno e quanto isso pode pesar no resultado.

**Página com o mapa:** https://matheusgsd.github.io/secoes-2turno-2026/

## O que os números mostram

- **2.053 urnas votam em outro prédio no 2º turno**, com 609.969 eleitores aptos, em 336 municípios de 23 estados.
  Metade muda menos de 410 metros.
- **O painel do TSE não mostra isso.** A lista "Seções alteradas" do painel de estatísticas tem 4.864 seções (4.863
  urnas), mas compara o local do 2º turno com o local *de cadastro*. 4.691 delas já votaram nesse mesmo prédio no 1º
  turno. E 1.881 urnas que voltam ao local de sempre, depois de terem sido deslocadas no 1º turno, ficam de fora da
  lista. Só 172 urnas estão nas duas contas.
- **Por que não 4,3 mil.** As reportagens de 17/10 (Agência Brasil e outras) falam em 4.352 seções, com dados até
  16/10. As "499.248 seções instaladas" citadas nelas são urnas, a mesma unidade usada aqui. O critério delas não foi
  divulgado; o total sugere o do painel (comparação com o local de cadastro), mas a distribuição por estado não fecha
  com os dados de 17/10 (431 no Rio de Janeiro, onde nenhuma urna muda do 1º para o 2º turno e o painel tem 47).
- **No 1º turno, essas urnas votaram mais em Lula** (50,7% contra 42,7% de Flávio; no país, 45,2% contra 47,0%).
  É geografia: 48% dos eleitores estão no Nordeste. Comparadas com as urnas que não mudam da mesma zona eleitoral, votaram
  igual (−0,24 ponto para Lula, intervalo de 95% de −1,0 a +0,6).
- **Mudar de lugar não fez o eleitor faltar em 2022.** As 1.382 urnas que trocaram de prédio entre os turnos de 2022
  tiveram abstenção 0,22 ponto menor que as vizinhas da mesma zona (intervalo de 95% de −0,40 a −0,04).
- **O efeito estimado no resultado é próximo de zero.** Se 2026 repetir 2022, a vantagem de Flávio muda entre −250 e
  +80 votos, diante de 2,24 milhões no 1º turno. Mesmo com abstenção total nessas urnas, Lula perderia no máximo
  36.895 votos líquidos (1,6% da diferença).

O voto para governador não foi calculado: o arquivo nacional de votação por seção do TSE traz só presidente.

## Como foi feito

Uma urna "muda" quando o número do local de votação no 2º turno é diferente do 1º, no cadastro de locais do TSE
(uma linha por seção e turno). Seção agregada conta junto com a urna da principal. Troca só de nome, com o mesmo
local e a mesma coordenada, não conta. Os detalhes estão no cabeçalho de cada script.

| Script | O que faz |
| --- | --- |
| `01_votos_1t.py` | Votos para presidente por seção: 1º turno de 2026 e os dois turnos de 2022 |
| `02_mudancas.py` | Urnas que mudam de local entre os turnos, em 2026 e 2022, e a conferência com o painel do TSE |
| `03_impacto.py` | Efeito da troca sobre a abstenção em 2022 e o peso das mudanças de 2026 na margem |
| `04_exportar_web.py` | Dados da página (`docs/dados.json`) |
| `05_imagem_x.py` | Cartão 1600 × 900 para redes sociais (`saida/imagem_x.png`) |
| `06_contornos.py` | Contornos de estados e municípios do IBGE para o mapa (`docs/contornos.json`) |

Para rodar do zero, baixe para `dados/` os arquivos do [portal de dados abertos do TSE](https://dadosabertos.tse.jus.br/)
(cerca de 630 MB, fora do git) e rode os scripts em ordem com `python -P scripts/0N_....py`:

- `votacao_secao_2026_BR.zip` e `votacao_secao_2022_BR.zip` (Resultados › Votação por seção eleitoral)
- `eleitorado_local_votacao_2026.zip` e `eleitorado_local_votacao_2022.zip` (Eleitorado › Eleitorado por local de
  votação). O de 2026 usado aqui foi gerado em 17/10/2026 e já traz o 2º turno.

Precisa de Python com pandas e numpy. As tabelas pequenas ficam em `saida/`; as tabelas completas por urna
(`saida/urnas_*.csv.gz` e `saida/votos_*_secao.csv.gz`) são geradas pelos scripts e não vão para o git.

Principais saídas:

- `saida/urnas_mudadas_2026.csv`: as 2.053 urnas, com local antigo e novo, distância e voto no 1º turno
- `saida/painel_tse_4864.csv`: as seções do painel do TSE, marcando quais mudam de fato do 1º para o 2º turno
- `saida/impacto_2022.csv` e `saida/impacto_uf_2026.csv`: efeito medido em 2022 e resumo por estado

## Fontes

- TSE, [dados abertos](https://dadosabertos.tse.jus.br/): votação por seção e cadastro de locais de votação, 2022 e 2026.
- IBGE, [API de malhas](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3): contornos de estados e municípios
  (baixados por `06_contornos.py` para `dados/ibge/`).
- TSE, [painel de estatísticas do eleitorado](https://sig.tse.jus.br/ords/dwapr/r/seai/sig-eleicao-eleitorado/home),
  Capilaridade › Seções alteradas.
- Justiça Eleitoral, [Fato ou Boato](https://www.justicaeleitoral.jus.br/fato-ou-boato/checagens/2026/mudancas-de-locais-de-votacao-no-2o-turno-seguem-regras-e-atendem-a-necessidades-de-seguranca)
  e [notícia do TSE](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/entenda-por-que-a-justica-eleitoral-trocou-o-endereco-de-algumas-secoes-para-o-2o-turno),
  de 16/10/2026.

## Licença

Código sob a licença MIT (`LICENSE`). Dados derivados em `saida/` e `docs/` sob
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt-br): pode reusar, citando Matheus Dalmolin e o TSE.
