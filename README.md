# Urnas que mudam de lugar no 2º turno de 2026

A Justiça Eleitoral trocou o endereço de algumas seções entre o 1º e o 2º turno de 2026. Este repositório mostra
quais urnas mudam de prédio, em quem os eleitores dessas urnas votaram no 1º turno e quanto isso pode pesar no resultado.

**Página com o mapa:** https://matheusgsd.github.io/secoes-2turno-2026/

## O que os números mostram

Cadastro de locais do TSE gerado em 17/10/2026 às 23h37 (Brasília), baixado em 18/10. O TSE ainda pode mudar locais
até o dia 25.

**Atualização de 18/10.** A primeira versão (commit `943ab33`) usava o cadastro gerado em 17/10 às 6h32 e contava
2.059 urnas. No cadastro novo, 267 delas, com 83.179 eleitores, deixaram de mudar: iam voltar ao local de sempre e agora
ficam no prédio do 1º turno. Nenhuma urna entrou. A lista está em `saida/versoes_17_18out.csv`. A primeira versão
também dizia que nenhuma urna muda no exterior; 9 mudam, em Colônia e em Praga (fora da conta, como todo o exterior).

- **1.792 urnas funcionam no 2º turno num prédio diferente do 1º**, com 528.489 eleitores aptos, em 297 municípios de 24
  estados: 0,36% das urnas do país, com 0,3% dos votos válidos no 1º turno. Metade muda até 415 m.
- **O painel do TSE mudou de critério.** A lista "Seções alteradas" do painel de estatísticas tinha, em 17/10, 4.864
  seções (4.863 urnas): comparava o local do 2º turno com o local *de cadastro*. Em 18/10 (7h09), passou a comparar
  com o local do 1º turno e lista 2.033 seções (2.023 urnas, 9 no exterior). As 1.792 urnas daqui estão todas nela. As 222
  urnas a mais no Brasil têm o mesmo endereço de local nos dois turnos: 162 só mudam de nome, 32 só de grafia,
  8 só de número; outras 20 têm o endereço reescrito no cadastro (abaixo). Em 33 das 162, o nome muda por completo e
  não dá para saber se é o mesmo prédio.
- **Por que não 4,3 mil.** O TSE divulgou em 16/10, e a imprensa reproduziu, que 4.352 seções mudaram de local, com
  dados até 16/10. As "499.248 seções instaladas" citadas são urnas, a mesma unidade usada aqui. O TSE não informou o
  critério. A distribuição por estado não fecha com os dados seguintes: o TSE cita 431 seções no Rio de Janeiro, onde o
  painel tinha 47 em 17/10 e tem 19 em 18/10, e 19 urnas mudam de prédio do 1º para o 2º turno.
- **Quando o cadastro não bate.** 20 urnas (São Paulo) ficaram de fora: o local muda de número e de nome, mas o
  cadastro reescreveu o endereço do local de sempre para o do prédio provisório, e a urna quase certamente continua no
  mesmo prédio. Na primeira versão eram 32; as 12 de Timóteo-MG agora aparecem no mesmo prédio nos dois turnos, o que
  confirma o critério. Outras 71 têm o mesmo endereço nos dois turnos, em geral genérico ("S/N", povoado, aldeia), e
  continuam na conta com aviso no mapa.
- **No 1º turno, os eleitores dessas urnas votaram mais em Lula** (50,3% contra 43,1% de Flávio; no país, 45,2% contra 47,0%).
  É geografia: 47% dos eleitores dessas urnas estão no Nordeste. Comparado com o das urnas do mesmo município e da mesma zona eleitoral
  que não mudam, não há diferença detectável (−0,6 ponto para Lula, intervalo de 95% de −1,4 a +0,2).
- **Em 2022, trocar de prédio não mostrou aumento de abstenção.** Nas 1.506 urnas que trocaram de prédio entre os
  turnos, a abstenção variou 0,08 ponto a menos que nas vizinhas do mesmo município e zona (intervalo de −0,23 a
  +0,08). Em outras comparações, vai de −0,19 a +0,14 ponto. É uma comparação entre urnas, não um experimento:
  essas urnas já tinham abstenção 0,8 ponto acima das vizinhas no 1º turno, e a conta supõe que, sem a mudança, a
  abstenção teria variado do mesmo jeito nos dois grupos.
- **O efeito estimado no resultado é próximo de zero.** Se 2026 repetir 2022, a vantagem de Flávio cairia 37 votos
  (intervalo de −91 a +18; entre −160 e +144 nas outras comparações), diante de 2,24 milhões no 1º turno. A conta supõe que quem deixa de votar votaria como o resto da sua urna. Num
  cenário limite, se ninguém votasse nessas urnas, e com a abstenção igual dos dois lados, Lula perderia 29.159 votos líquidos (1,3% da
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
| `07_versoes.py` | O que mudou entre a lista de 17/10 (commit `943ab33`) e a atual |
| `ibge.py` | Malhas e códigos de município do IBGE, usados por 02 e 06 |

Para rodar do zero, baixe para `dados/` os arquivos do [portal de dados abertos do TSE](https://dadosabertos.tse.jus.br/)
(cerca de 630 MB, fora do git) e rode os scripts em ordem com `python -P scripts/0N_....py`:

- `votacao_secao_2026_BR.zip` e `votacao_secao_2022_BR.zip` (Resultados › Votação por seção eleitoral)
- `eleitorado_local_votacao_2026.zip` e `eleitorado_local_votacao_2022.zip` (Eleitorado › Eleitorado por local de
  votação). O de 2026 usado aqui foi gerado em 17/10/2026 às 23h37 (Brasília) e já traz o 2º turno. O portal guarda só
  a versão mais recente, então o resultado pode mudar se o TSE publicar outra.
- `painel_secoes_alteradas_2026.csv`: a lista do painel de estatísticas (Eleitorado › Capilaridade › Seções alteradas,
  atualização de 18/10, 7h09), exportada pelo botão "Gerar arquivos". O arquivo vem como
  `secoes_eleitorais_alteradas_2t-pais_2026.csv`.

As malhas do IBGE são baixadas sozinhas para `dados/ibge/` na primeira execução. Precisa de Python com pandas, numpy,
shapely e matplotlib. As tabelas pequenas ficam em `saida/`; as tabelas completas por urna (`saida/urnas_*.csv.gz` e
`saida/votos_*_secao.csv.gz`) são geradas pelos scripts e não vão para o git.

Principais saídas:

- `saida/urnas_mudadas_2026.csv`: as 1.792 urnas, com prédio antigo e novo, critério, distância, aviso de mesmo
  endereço e voto no 1º turno
- `saida/mesmo_predio_2026.csv`: as 20 urnas retiradas porque o cadastro reescreveu o endereço
- `saida/painel_tse.csv`: as 2.015 seções do painel de 18/10 no Brasil, com a classificação de cada uma aqui e, quando
  não contam, o motivo
- `saida/versoes_17_18out.csv`: as urnas da lista de 17/10 e da atual, com o que mudou no cadastro
- `saida/impacto_2022.csv` e `saida/impacto_uf_2026.csv`: efeito medido em 2022 e resumo por estado
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
