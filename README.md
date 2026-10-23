# Urnas que mudam de lugar no 2º turno de 2026

A Justiça Eleitoral trocou o endereço de algumas seções entre o 1º e o 2º turno de 2026. Este repositório mostra
quais urnas mudam de prédio, em quem os eleitores dessas urnas votaram no 1º turno e quanto isso pode pesar no resultado.

**Página com o mapa:** https://matheusgsd.github.io/secoes-2turno-2026/

## O que os números mostram

Cadastro de locais do TSE gerado em <!--n:cadastro_extenso-->23/10 às 11h27<!--/n--> (Brasília), baixado no mesmo dia. O TSE ainda pode mudar locais
até o dia 25; se publicar outra versão, a página e este README serão refeitos, com a mudança registrada aqui.

**Atualização de 22/10, cadastros de 11h27 e 15h27.** O TSE publicou mais duas versões do cadastro. A de 11h27 foi
aplicada pela tarefa agendada às 11h42; a de 15h27, baixada às 15h42, esperou a anterior, que ganhou um commit só com as
saídas (`f287d0c`), e foi aplicada depois dele. A de 11h27 tirou 29 urnas do Pará (Vigia 12, São Geraldo do
Araguaia 9, Colares 4, Piçarra 4), todas com o registro do 1º turno mudado para o prédio do 2º (as 12 de Vigia e 1 de
Piçarra tinham entrado às 20h28 de 21/10), e pôs 3 em São Raimundo Nonato-PI, em que o local do 2º turno mudou. De 339
para 313 (`saida/versoes_22out_11h27.csv`). A de 15h27 tirou 8 urnas de Várzea Grande-MT, também pelo registro do 1º
turno, e pôs 14: 11 em que o local do 2º turno passou a ser outro, com número novo (Almeirim-PA 7, Entre Rios de
Minas-MG 2, João Pinheiro-MG 1 e Aracati-CE 1; em Aracati, o cadastro já dava ao local do 2º turno o nome da igreja,
com o número e o endereço do 1º, e era correção de cadastro; agora a igreja tem número próprio, no mesmo endereço, e a
urna conta, com aviso no mapa) e 3 em Januária-MG, que tinham saído às 20h28 de 21/10, quando o registro do 1º turno
passou a ser a escola municipal da comunidade: agora ele voltou a ser o local de sempre, e no 2º turno elas continuam
na escola, que ganhou outro número. De 313 para 319 (`saida/versoes_22out_15h27.csv`). Nenhuma das duas tinha seção repetida. A
estimativa segue em −3 votos (−25 a +15 no cadastro de 15h27), e o cenário extremo foi de 6.015 para 5.380 votos e
depois para 6.194 (0,28% da diferença nacional). A versão anterior, com 313 urnas, é a do commit `f287d0c`.

**Atualização de 22/10, cadastros de 21/10, 20h28, e 22/10, 6h28.** O TSE publicou mais duas versões do cadastro.
A de 21/10, 20h28, foi baixada pela conferência automática às 20h45, mas a aplicação parou no meio quando o
computador suspendeu, às 21h09 (veja "Como acompanhamos as atualizações do TSE"); os scripts foram rodados de novo com
`--rodar`, e a versão ganhou um commit só com as saídas (`50fa582`). Ela tirou 68 urnas: 51 em que o registro do 1º
turno passou a ser o prédio do 2º (Araguari 16, Januária 13, Caratinga 9 e Ubaporanga 4, em MG; 4 no PR; 3 no RS; 2
em Itamarati-AM), 15 em que mudaram os dois registros e o do 1º turno ficou igual ao do 2º (Nova Iguaçu-RJ 14, São
Tiago-MG 1) e as 2 de Serra do Ramalho-BA que tinham entrado às 15h27. Pôs 41: 29 em que o local do 2º turno mudou
(Vigia-PA 12, Barras-PI 9, Manaus 5, Moju-PA 2, Piçarra-PA 1) e 12 em Laranjeiras do Sul-PR, que tinham saído às 6h27
e voltam à lista porque o registro do 1º turno passou a ser o Pavilhão da Igreja Matriz Santana. Tinha 3 seções do PR
repetidas no 1º turno; ficou o local da versão anterior. De 367 para 340 (`saida/versoes_21out_20h28.csv`). A de 22/10,
6h28, foi baixada às 6h42 e esperou o commit da anterior; foi aplicada às 8h04. Tirou 5 urnas (3 em Santo Inácio-PR,
pelo registro do 1º turno, e as 2 de Moju) e pôs 4 em Jacaraci-BA, com o mesmo número de local e um nome que contém o
outro, noutra rua (contam, com aviso no mapa). Em 17 urnas de Tracuateua-PA, o cadastro reescreveu o nome e o
endereço do local do 2º turno sem trocar o número: "EMEF" virou "EMEIF", e o endereço é o mesmo povoado escrito de
outro jeito. Na primeira passada elas contaram como prédio novo (356 urnas, cenário extremo de 8.153 votos, 2.138 deles
de Tracuateua); o `02_mudancas.py` passou a tratá-las como o mesmo prédio (`NOME_REESCRITO`: mesmo número, mesmo
nome tirando a sigla e um endereço contido no outro), e o mapa ganhou o filtro "Podem confundir", com elas e as que
contam com ressalva. Em 2022, o critério tira 1 urna (Itaúna-MG), e a estimativa do efeito não muda. De 340 para 339
(`saida/versoes_22out_06h28.csv`). A versão anterior, com 340 urnas, é a do commit `50fa582`.

**Atualização de 21/10, cadastro de 15h27.** O TSE publicou outra versão do cadastro, gerada em 21/10 às 15h27, e a
conferência automática a baixou e aplicou às 15h42, já com os números do texto preenchidos pelo `18_texto.py`. Ela
tirou 4 urnas pelo mesmo motivo das versões de 11h27 e 14h19 (o registro do 1º turno passou a ser o prédio do 2º): 2
em Santa Juliana-MG e 2 em Tacaimbó-PE; com a saída das de Tacaimbó, Pernambuco fica com as mesmas 6 seções da lista
do TRE-PE. Pôs 7: 5 em Ibitinga-SP (zona 49), que vão da EM Prof. Benedito Teixeira de Macedo para a Fundação
Educacional Municipal da Estância Turística de Ibitinga no 2º turno, e 2 em Serra do Ramalho-BA (zona 71), em que o
registro do 1º turno mudou no sentido inverso: o 1º turno passou a ser um "Local temporário da escola. AG 03", e o
2º continua na Escola Municipal Frei Francisco da Soledade, o local de sempre, para onde elas voltam. É a primeira
vez que a mudança no registro do 1º turno põe urnas na lista. De 364 para 367 (`saida/versoes_21out_15h27.csv`). A
versão anterior, com 364 urnas, é a do commit `0f3a6a2`.

**Atualização de 21/10, cadastro de 14h19.** O TSE publicou outra versão do cadastro, gerada em 21/10 às 14h19, e a
conferência automática a baixou e aplicou às 14h42. Ela tirou 51 urnas. Em 50, aconteceu o mesmo que em 66 no cadastro
de 11h27 (abaixo): o local do 2º turno não mudou, e o cadastro passou a dizer que elas já funcionaram nesse prédio no
dia 4 (MG 23: 8 em Córrego Novo, 5 em Caratinga, 4 em Águas Vermelhas, 3 em Itamarandiba e 3 em Três Corações; SP 13:
12 em Presidente Prudente e 1 na capital; 6 em Pelotas-RS; 4 em Maringá-PR; MA 2, em Presidente Vargas e Vargem
Grande; 1 em Pão de Açúcar-AL; 1 em Ipueiras-CE). Em Presidente Prudente, o registro novo bate com o que o TRE-SP
informou: depois de um vendaval, as seções da zona 402 funcionaram no dia 4 na Faculdade de Ciências e Tecnologia da
Unesp, e não na E.E. Florivaldo Leal, como dizia o cadastro; nas outras, não dá para saber qual registro está certo.
A 51ª, em Caiana-MG, ia voltar ao local de sempre e passou a ficar no prédio do 1º turno. O registro do 1º turno
também mudou em 4 urnas da zona 25 de MG que tinham saído da lista no cadastro de 6h27. Entraram 8: 7 em
Paracatu-MG, que pelo cadastro anterior ficavam na E. E. Olindina Loureiro nos dois turnos e agora vão para a E. M.
Joaquim Adjuto Botelho no 2º, e 1 em Pilão Arcado-BA. De 407 para 364 (`saida/versoes_21out_14h19.csv`). A versão
anterior, com 407 urnas, é a do commit `90059c6`. Duas correções nos scripts vieram junto. O `07_versoes.py` marcava
as urnas que entraram como se o local tivesse mudado nos dois turnos, porque só tinha os locais da lista anterior;
agora lê os locais da versão anterior do zip dela e compara número, nome e endereço, e as 8 que entraram aparecem com
o local do 2º turno mudado. O `12_renovadas.py` passou a classificar cada saída pelo cadastro atual: as 6 urnas que
saíram no cadastro de 6h27 e depois tiveram o 1º turno reescrito (4 na zona 25 de MG e 2 em Miguel Calmon-BA) contam
agora em `primeiro_turno_reescrito`, e não em `ficam_no_local_de_sempre`. Com o cadastro de 14h19, `saida/renovadas.json`
fica com 1.814 renovadas (a de Caiana a mais), 19 em `ficam_no_local_de_sempre` e 122 em `primeiro_turno_reescrito`.

**Atualização de 21/10, cadastro de 11h27.** O TSE publicou outra versão do cadastro, gerada em 21/10 às 11h27, e a
conferência automática a baixou e aplicou às 11h45. Ela tirou 66 urnas de um jeito novo: o local do 2º turno não
mudou, e sim o registro do 1º. Até a versão de 6h27, o cadastro dizia que elas funcionaram no dia 4 no local de sempre
e iam para outro prédio no dia 25; agora diz que já funcionaram nesse outro prédio no dia 4, e por isso não mudam mais
(PI 26, 11 delas em São João do Piauí; MG 20, em Caldas, Montes Claros e Bela Vista de Minas; MA 15, em Santa Inês e
Bacuri; 3 em Quixadá-CE; 2 em Itaguatins-TO). Não dá para saber qual registro do 1º turno está certo: o arquivo de
votação por seção traz o local de cadastro, não o prédio onde a urna funcionou. Seguimos o cadastro mais recente; se o
antigo estiver certo, essas 66 urnas, com 17 mil eleitores, continuam mudando. O registro do 1º turno também mudou em 2
urnas de Miguel Calmon-BA, que já tinham saído da lista no cadastro de 6h27. Entraram 11 em Manaus (zona 58), que
votavam na mesma escola nos dois turnos e vão para a E. E. Raio de Sol no 2º. De 462 para 407
(`saida/versoes_21out_11h27.csv`). A versão anterior, com 462 urnas, é a do commit `d1c3f30`. O `12_renovadas.py`
supunha que o local do 1º turno não mudava entre versões; agora conta à parte as urnas em que ele mudou
(`primeiro_turno_reescrito` em `saida/renovadas.json`), e as 1.813 que iam voltar e passaram a ficar continuam as mesmas.

**Atualização de 21/10, cadastro de 6h27.** O TSE publicou outra versão do cadastro, gerada em 21/10 às 6h27, e a
conferência automática a baixou e aplicou às 8h16. Ela tirou 32 urnas, todas passando a ficar no prédio do 1º turno, e
pela primeira vez a maioria não ia voltar ao local de sempre: 25 votaram no local de sempre no 1º turno, iam sair dele
no 2º e agora ficam nele (12 em Laranjeiras do Sul-PR; 7 em Candeias-BA e 2 em Miguel Calmon-BA; 4 na zona 25 de MG,
em Senhora dos Remédios, Desterro do Melo e Ressaquinha). As outras 7 são as de Almirante Tamandaré-PR, das seções
repetidas. Entraram 6: 4 em Cuiabá-MT, também das repetidas, e 2 em Manhuaçu-MG, onde o local de sempre muda de prédio
sem trocar de número. De 488 para 462 (`saida/versoes_21out_06h27.csv`). A versão anterior, com 488 urnas, é a do
commit `a395125`. O script ficou parado na madrugada (de 23h41 a 8h16); se o TSE publicou outra versão nesse
intervalo, ela não foi baixada.

**Atualização de 20/10, cadastro de 20h27.** O TSE publicou outra versão do cadastro, gerada em 20/10 às 20h27, e a
conferência automática a baixou e aplicou às 20h42. Ela tirou 1 urna de Unaí-MG, que ia voltar ao local de sempre e
passou a ficar no prédio do 1º turno, como todas as saídas anteriores, e pôs 19 que passam a sair do local de sempre
no 2º turno (13 na zona 72 de MG, 8 em Córrego Novo e 5 em Caratinga; 4 em São Paulo, zona 320; 2 em Santa Maria-RS):
de 470 para 488 (`saida/versoes_20out_20h27.csv`). As 15 seções repetidas do cadastro de 15h27 continuam repetidas,
com os mesmos dois locais, e ficam no mesmo local de antes (veja abaixo). A versão anterior, com 470 urnas, é a do
commit `b9452ce`.

**Atualização de 20/10, cadastro de 15h27.** O TSE publicou outra versão do cadastro, gerada em 20/10 às 15h27. Ela tirou
15 urnas que iam voltar ao local de sempre e passaram a ficar no prédio do 1º turno (11 em Iapu-MG, 4 em Cianorte-PR)
e pôs 9 que passam a sair do local de sempre no 2º turno (PR 4, em Inácio Martins e Irati; 2 em Santana do
Cariri-CE; 2 em Santarém-PA; 1 em Inhapim-MG): de 476 para 470 (`saida/versoes_20out_15h27.csv`). Em 7 urnas de
Ibitirama-ES, que continuam na lista, só mudou o número do local do 2º turno. A versão anterior, com 476 urnas, é a do
commit `371bbe0`.

No cadastro de 15h27, 15 seções aparecem duas vezes no 2º turno, cada vez num local (7 em Almirante Tamandaré-PR, 4 em
Aimorés-MG, 4 em Cuiabá-MT): parece um arquivo gerado no meio de uma mudança. `02_mudancas.py` fica, nesses casos, com
o local que a seção tinha no mesmo turno na versão anterior do cadastro (`saida/duplicadas_2026.csv`, no commit
`a395125`); pelo outro local, entrariam as 4 de Cuiabá e sairiam as 7 de Almirante Tamandaré, e a lista teria 467
urnas (485 com o cadastro de 20h27, em que as mesmas 15 seguem repetidas e fica a mesma escolha). As linhas repetidas
quebraram a atualização automática (veja [Como acompanhamos](#como-acompanhamos-as-atualizações-do-tse)). No cadastro
de 21/10, 6h27, as repetições sumiram, e o TSE ficou com o outro local nas 11 urnas que mudavam a conta: a nossa
escolha estava errada em Almirante Tamandaré (as 7 ficam no prédio do 1º turno) e em Cuiabá (as 4 trocam de prédio
provisório). As 4 de Aimorés ficam no mesmo local nos dois turnos.

**Atualização de 20/10, 11h27 e 12h32.** O TSE publicou mais duas versões do cadastro em 20/10, geradas às 11h27 e às 12h32,
e as duas foram baixadas pela conferência automática (veja abaixo). A de 11h27 (commit `6c651e5`, só com as saídas dos
scripts) tirou 5 urnas do AP (4 em Pracuúba, 1 em Amapá), que iam voltar ao local de sempre e passaram a ficar no
prédio do 1º turno, e pôs 6 que passam a sair do local de sempre no 2º turno (4 em Rio Piracicaba-MG, 2 em
Bacuri-MA): de 469 para 470 (`saida/versoes_20out_11h27.csv`). A de 12h32 tirou 1 urna de Ipiranga de Goiás-GO, pelo
mesmo motivo, e pôs 7 em MG que também passam a sair do local de sempre (4 em Águas Vermelhas, 3 em Três Corações):
476 urnas (`saida/versoes_20out_12h32.csv`).

**Atualização de 20/10, de manhã.** A versão anterior (commit `da7f1cc`) usava o cadastro gerado em 19/10 às 15h27 e contava
475 urnas. No cadastro de 20/10, 6h27, 60 delas, com 17.840 eleitores, deixaram de mudar: iam voltar ao local de
sempre e agora ficam no prédio do 1º turno (AP 28, em Santana e Ferreira Gomes; PR 25, em Francisco Alves, Campo
Largo, Rio Bonito do Iguaçu e Capanema; MG 6; AM 1, a urna de Manaus que deixava dividido um prédio provisório).
Entraram 54: 49 que votavam no local de sempre nos dois turnos e agora saem dele no 2º (18 em MG, 16 delas em
Araguari; 17 no PI, em São João do Piauí e João Costa; 8 em Várzea Grande-MT; 2 em Itamarati-AM; 2 em Mantenópolis-ES;
1 em Presidente Médici-RO; 1 em São Paulo), 2 em Extremoz-RN, onde o local de sempre muda de prédio sem trocar de
número, e 3 que fazem pela primeira vez o caminho inverso das saídas: ficavam no prédio provisório do 1º turno e agora
voltam ao local de sempre (2 em Vigia-PA, 1 em Ipueiras-CE). Eram 469 urnas (commit `ea7023c`). A lista está em
`saida/versoes_20out_06h27.csv`. Uma versão intermediária, publicada na noite de 19/10 (no CDN, `Last-Modified` de
20/10, 00h05 UTC), foi substituída antes que a baixássemos.

**As atualizações continuam.** Em nota de 19/10, reproduzida pela imprensa
([Brasil 247](https://www.brasil247.com/brasil/tse-registra-mudancas-em-1-106-locais-de-votacao-para-o-segundo-turno-das-eleicoes/)),
o TSE disse que os números ainda estão sendo atualizados à medida que as zonas eleitorais concluem os ajustes nos
sistemas, inclusive para manter no 2º turno locais alterados provisoriamente no 1º. É o que aparece em quase todas
as saídas até 20/10 (veja "Como a lista encolheu", abaixo); as exceções vieram a partir de 21/10: as 25 do cadastro de
6h27, que iam sair do local de sempre, e, desde então, <!--n:primeiro_turno_reescrito-->243<!--/n--> em que mudou o registro do 1º turno. Alguns TREs publicaram listas próprias: o
[TRE-AL](https://www.tre-al.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-nao-houve-alteracao-de-locais-de-votacao-para-o-segundo-turno-em-alagoas)
diz que nenhum local muda (aqui, havia 1 urna em Pão de Açúcar, que ia para o anexo da mesma escola, no mesmo
endereço; ela saiu da lista no cadastro de <!--h-->21/10, 14h19<!--/h-->, e Alagoas ficou sem nenhuma); o
[TRE-PE](https://www.tre-pe.jus.br/comunicacao/noticias/2026/Outubro/2o-turno-apenas-6-secoes-eleitorais-terao-mudancas-em-pernambuco),
que só 6 seções mudam, em Floresta e Buíque (aqui, as mesmas 6; havia também 2 urnas em Tacaimbó, que entraram com o cadastro de 19/10, 11h27, e saíram com o de
21/10, 15h27, quando o registro do 1º turno delas mudou; as 3 de Recife que voltavam ao local de sempre saíram da lista com o de 15h27). O
[TRE-RS](https://www.tre-rs.jus.br/comunicacao/noticias/2026/Outubro/tre-rs-informa-sobre-mudancas-pontuais-nos-locais-de-votacao-no-2o-turno)
e o TRE-RN ([Tribuna do Norte](https://tribunadonorte.com.br/tn-nas-eleicoes-2026/tre-altera-locais-de-votacao-em-seis-municipios-do-rn-para-o-segundo-turno/))
confirmam seções que voltam ao local de sempre. Até 20/10, as urnas que voltavam ao local de sempre foram a parte da
lista que mais mudou: eram 306 no cadastro de 19/10, 11h27, 111 no de 15h27, 54 no de 20/10, 6h27, 49 no de 11h27, 48 no de 12h32, 33 no de 15h27, 32 nos de 20h27 e de 21/10, 6h27 e 11h27, 30 no de 14h19 e 32 no de 15h27, com as 2 de Serra do Ramalho; nos cadastros de 21/10, quase todas as saídas vieram das outras partes da lista. No de 20h28, subiram para 42, com as 12 de Laranjeiras do Sul-PR e sem as 2 de Serra do Ramalho; no cadastro atual, são <!--n:volta-->51<!--/n-->.
O painel de seções alteradas, na atualização de 19/10, 11h27 (não exportada), listava 554 seções;
com o cadastro daquela hora, tirando as 46 urnas cujo local de sempre mudava de prédio sem trocar de número, contávamos
550 urnas, com a mesma contagem por estado, menos em MG (98 no painel, 94 aqui). Não exportamos nem conferimos o
painel depois disso.

**O efeito estimado é próximo de zero em todas as versões.** Pelo que se mediu em 2022, não há sinal de que a troca
de prédio entre os turnos aumente a abstenção, e por isso a soma fica perto de zero qualquer que seja o número de urnas:

| Cadastro | Urnas | Variação na vantagem de Flávio (IC 95%) | Se ninguém votasse nessas urnas | Lula nas que mudam × vizinhas (IC 95%) |
| --- | ---: | ---: | ---: | ---: |
| 17/10, 6h28 | 2.059 | −47 (−114 a +23) | 36.096 votos (1,6% da diferença) | −0,4 ponto (−1,2 a +0,4) |
| 17/10, 23h33 | 1.792 | −37 (−91 a +18) | 29.159 (1,3%) | −0,6 (−1,4 a +0,2) |
| 18/10, 11h27 | 1.733 | −36 (−87 a +16) | 28.652 (1,3%) | −0,3 (−1,0 a +0,4) |
| 18/10, 20h27 | 1.025 | −31 (−77 a +14) | 26.108 (1,2%) | +0,05 (−0,9 a +1,0) |
| 19/10, 11h27 | 596 | +4 (−15 a +22) | 588 (0,03%) | +0,2 (−1,0 a +1,5) |
| 19/10, 15h27 | 475 | −0,1 (−21 a +19) | 3.932 (0,18%) | −0,7 (−2,0 a +0,7) |
| 20/10, 6h27 | 469 | −4 (−26 a +17) | 6.978 (0,31%) | −0,1 (−1,5 a +1,4) |
| 20/10, 11h27 | 470 | −4 (−28 a +19) | 7.307 (0,33%) | 0,0 (−1,5 a +1,5) |
| 20/10, 12h32 | 476 | −4 (−30 a +20) | 7.784 (0,35%) | +0,1 (−1,3 a +1,7) |
| 20/10, 15h27 | 470 | −5 (−31 a +18) | 8.438 (0,38%) | +0,2 (−1,3 a +1,7) |
| 20/10, 20h27 | 488 | −5 (−33 a +19) | 8.771 (0,39%) | +0,2 (−1,2 a +1,7) |
| 21/10, 6h27 | 462 | −5 (−32 a +18) | 8.396 (0,38%) | +0,6 (−0,8 a +2,0) |
| 21/10, 11h27 | 407 | −3 (−11 a +4) | 3.838 (0,17%) | +0,5 (−0,9 a +2,0) |
| 21/10, 14h19 | 364 | −3 (−11 a +4) | 3.609 (0,16%) | +0,3 (−1,2 a +1,8) |
| 21/10, 15h27 | 367 | −3 (−9 a +2) | 3.256 (0,15%) | +0,2 (−1,2 a +1,8) |
| 21/10, 20h28 | 340 | −3 (−21 a +12) | 5.616 (0,25%) | −0,2 (−2,0 a +1,7) |
| 22/10, 6h28 | 339 | −3 (−24 a +15) | 6.015 (0,27%) | −0,3 (−2,1 a +1,5) |
| 22/10, 11h27 | 313 | −3 (−21 a +12) | 5.380 (0,24%) | −0,6 (−2,4 a +1,3) |
| **22/10, 15h27** | **319** | **−3 (−25 a +15)** | **6.194 (0,28%)** | **−0,7 (−2,5 a +1,0)** |

O intervalo da terceira coluna é o do efeito médio, que supõe o mesmo efeito em todas as urnas do mesmo tipo (veja
abaixo a faixa de previsão). A diferença nacional no 1º turno foi de 2,24 milhões de votos. "Se ninguém votasse" é um
cenário extremo, não uma previsão nem um limite superior: é a vantagem líquida de Lula nessas urnas no 1º turno, e
deixa de lado os votos em outros candidatos, que no 2º turno vão para um dos dois, e uma abstenção que atinja mais um
lado que o outro. <!--h-->Ele caiu de 3.609 para 3.256 votos com o cadastro de 21/10, 15h27, e de 3.838 para 3.609 com o de 21/10, 14h19. Com o de 11h27, tinha caído de
8.396 para 3.838:<!--/h--> as 66 urnas que saíram deram 3.870 votos a mais a Lula no 1º turno, e as 11 que entraram, 688 a mais a Flávio; o
intervalo da estimativa encolheu pelo mesmo motivo. Com o de 6h27, tinha caído de 8.771 para 8.396 (as 32 urnas que
saíram deram 39 votos a mais a Lula, e as 6 que entraram, 336 a mais a Flávio). Antes,
tinha crescido a cada cadastro: de 8.438 para 8.771 com o de 20/10, 20h27 (a urna que saiu deu 12 votos a mais a
Flávio, e as 19 que entraram, 321 a mais a Lula); com o de 15h27, tinha crescido de 7.784 para 8.438 (as 15 urnas que saíram deram 703 votos a mais a Flávio, e as 9 que
entraram, 49 a mais a Flávio).
Pelo mesmo motivo, já tinha subido de 6.978 para 7.307 com o cadastro de 20/10, 11h27, e de 7.307 para 7.784 com o de
12h32 (somando os dois, as 13 urnas que entraram deram 755 votos a mais a Lula, e as 6 que saíram, 51 a mais a
Flávio), de 3.932 para 6.978 no cadastro de 20/10, 6h27 (as 60 urnas que saíram deram 2.102 votos a mais a Flávio, e
as 54 que entraram, 944 a mais a Lula), e de 588 para 3.932 no de 19/10, 15h27. Continua sendo um cenário extremo:
pelo que se mediu em 2022, não há sinal de que a troca de prédio entre os turnos aumente a abstenção, e a estimativa
segue perto de zero.

**Atualizações anteriores.** Em 19/10 à noite (commit `6804293`), o cadastro de 19/10, 15h27 tirou 195 urnas (AM 45,
PR 42, MG 38, GO 27, SP 24, SE 14) e pôs 74, 46 delas em MG: de 596 para 475 (`saida/versoes_19out_tarde.csv`). Em
19/10 à tarde (commit `4925b73`), o cadastro de 19/10, 11h27 tirou 449 urnas (iam
voltar ao local de sempre e passaram a ficar no prédio do 1º turno; BA 107, PB 80, PE 79, SE 54, AL 47) e pôs 20, 11
delas em Ubá-MG: de 1.025 para 596 (`saida/versoes_19out.csv`). Em 19/10 de manhã (commit `917ba7a`), o cadastro de
18/10, 20h27 tirou 741 urnas (PR 138, MA 124, PI 98, MG 93, AP 79, RR 60) e pôs 33, entre elas 8 em Confresa-MT, o
caso que o TSE citou como exemplo de escola atingida pela chuva: de 1.733 para 1.025
(`saida/versoes_18out_noite.csv`). Em 18/10 à tarde (commit `2272612`), o cadastro de 18/10, 11h27 tirou 72 e pôs 13
em Januária-MG: de 1.792 para 1.733 (`saida/versoes_18out.csv`). Em 18/10 de manhã (commit `fa873d1`), o cadastro de
17/10, 23h33 tirou 267 e não pôs nenhuma: de 2.059 para 1.792 (`saida/versoes_17_18out.csv`). A primeira versão
(commit `943ab33`) também dizia que nenhuma urna muda no exterior; 9 mudam, em Colônia e em Praga (fora da conta, como
todo o exterior).

- **<!--n:urnas-->358<!--/n--> urnas funcionam no 2º turno num prédio diferente do 1º**, com <!--n:aptos_mil-->113 mil<!--/n--> eleitores aptos, em
  <!--n:municipios-->89<!--/n--> municípios de <!--n:ufs-->21<!--/n--> estados: <!--n:pct_urnas_pais-->0,07%<!--/n--> das 499.248 urnas do país, com <!--n:pct_validos_pais-->0,07%<!--/n--> dos votos válidos no 1º
  turno.
- **Metade dos eleitores vota no 2º turno a no máximo <!--n:dist_mediana-->250 m<!--/n--> do prédio do 1º**, em linha reta. Para
  <!--n:dist_menos_1km-->85%<!--/n-->, a distância é menor que 1 km; para <!--n:dist_5km-->0,3%<!--/n-->, de 5 km ou mais. Vale para as <!--n:dist_urnas_com-->201<!--/n--> urnas com
  coordenada confiável nos dois prédios (<!--n:dist_urnas_sem-->157<!--/n--> ficam sem distância). É a distância entre os prédios, não o
  deslocamento de cada eleitor: o endereço do eleitor não é público.
- **O painel do TSE mudou de critério.** A lista "Seções alteradas" do painel de estatísticas tinha, em 17/10, 4.864
  seções (4.863 urnas): comparava o local do 2º turno com o local *de cadastro*. Em 18/10 (7h09), passou a comparar
  com o local do 1º turno e listava 2.033 seções (2.023 urnas, 9 no exterior). Essa exportação é anterior aos
  <!--n:n_cadastros_depois_do_painel-->22<!--/n--> cadastros que baixamos depois (de <!--n:cadastros_depois_do_painel-->18/10, 11h27 e 20h27; de 19/10, 11h27 e 15h27; de 20/10, 6h27, 11h27, 12h32, 15h27 e 20h27; de 21/10, 6h27, 11h27, 14h19, 15h27 e 20h28; de 22/10, 6h28, 11h27, 15h27 e 20h28; e de 23/10, 6h27, 10h00, 10h47 e 11h27<!--/n-->):
  <!--n:painel_nas_duas-->173<!--/n--> das <!--n:urnas-->358<!--/n--> urnas daqui estão nela; as outras <!--n:painel_fora-->185<!--/n--> entraram com esses cadastros. Das <!--n:painel_so-->1.841<!--/n--> urnas
  a mais no Brasil, <!--n:painel_mesmo_local-->1.635<!--/n--> têm, no cadastro atual, o mesmo local nos dois turnos (entre elas, <!--n:painel_sairam-->1.613<!--/n--> que
  saíram da lista com esses cadastros). As outras <!--n:painel_outras-->206<!--/n--> têm o mesmo número de local nos dois turnos: <!--n:painel_so_nome-->167<!--/n--> só
  mudam de nome, <!--n:painel_so_grafia-->32<!--/n--> só de grafia do nome e <!--n:painel_so_endereco-->7<!--/n-->, em Candeias-BA, só de grafia do endereço. Em 32 das <!--n:painel_so_nome-->167<!--/n-->, o
  nome muda por completo e não dá para saber se é o mesmo prédio. Havia um 33º caso, em Presidente Médici-RO, que no cadastro de
  20/10, 6h27, passou a mudar também o número do local e entrou na lista.
- **Como a lista encolheu.** Nas <!--n:n_versoes-->24<!--/n--> versões do cadastro que baixamos, a lista teve <!--n:serie_urnas-->2.059, 1.792, 1.733, 1.025, 596, 475, 469, 470, 476, 470, 488, 462, 407, 364, 367, 340, 339, 313, 319, 334, 337, 338, 358 e 358<!--/n-->
  urnas: encolheu muito até o cadastro de 19/10, 15h27, e desde então muda menos a cada versão. Quase todas as saídas
  foram do mesmo jeito: <!--n:renovadas-->1.814<!--/n--> urnas que iam voltar ao local de sempre passaram a ficar no prédio provisório do 1º
  turno. Nos cadastros de 21/10 apareceram dois outros tipos de saída. No de 6h27, urnas que votaram no local de
  sempre no 1º turno e iam sair dele no 2º passaram a ficar nele (pelo cadastro atual, <!--n:ficam_no_local_de_sempre-->7<!--/n-->). A partir do
  de 11h27, o cadastro mudou o local do 1º turno para o do 2º (pelo cadastro atual, <!--n:primeiro_turno_reescrito-->243<!--/n-->, incluindo algumas que
  tinham saído antes por outro motivo). Essas <!--n:fora_da_conta_renovadas-->250<!--/n--> ficam fora da conta abaixo, que acompanha as urnas que iam
  voltar. Só no cadastro de 20/10, 6h27, 3 urnas fizeram o caminho contrário (Vigia-PA e Ipueiras-CE; a de Ipueiras saiu da lista no cadastro de <!--h-->21/10, 14h19<!--/h-->,
  quando o registro do 1º turno dela mudou). Não foi um
  estado só (<!--n:renovadas_ufs-->17<!--/n--> estados, <!--n:renovadas_municipios-->287<!--/n--> municípios e <!--n:renovadas_zonas-->303<!--/n--> zonas; o Paraná, o maior, tem <!--n:renovadas_pr_pct-->14%<!--/n-->), mas a
  proporção varia muito. <!--n:ufs_todas_ou_quase-->No Paraná (253 de 255), em Pernambuco (198 de 198), no Maranhão (176 de 179), em São Paulo (163 de 163), em Minas Gerais (158 de 158), na Bahia (127 de 127), no Amapá (112 de 112), em Alagoas (101 de 101), na Paraíba (96 de 96), em Goiás (73 de 73), em Sergipe (70 de 70), em Roraima (60 de 60), no Amazonas (48 de 48), no Tocantins (37 de 37) e no Acre (13 de 13)<!--/n-->, todas ou quase todas as que iam
  voltar passaram a ficar no prédio do 1º turno; <!--n:ufs_quase_nenhuma-->no Rio Grande do Norte (0 de 9) e no Rio Grande do Sul (2 de 8)<!--/n-->, quase nenhuma. Nenhum prédio
  provisório ficou dividido: o único caso, em Manaus, zona 62, se desfez no cadastro de 20/10, 6h27. Das <!--n:fora_1t-->6.987<!--/n--> urnas
  registradas fora do local de sempre no 1º turno, <!--n:taxa_volta_1o-->26%<!--/n--> voltariam a ele pelo primeiro cadastro e <!--n:taxa_volta-->0,7%<!--/n--> pelo atual; em
  2022, pelo cadastro final, 15,1% (a comparação justa é entre cadastros finais). O voto em Lula nas <!--n:renovadas-->1.814<!--/n-->
  (<!--n:renovadas_lula-->50,7%<!--/n-->) e nas <!--n:volta-->51<!--/n--> que voltam no cadastro atual (<!--n:ainda_voltam_lula-->50,6%<!--/n-->) fica perto do esperado pelos municípios
  (<!--n:renovadas_esperado-->50,9%<!--/n--> e <!--n:ainda_voltam_esperado-->51,6%<!--/n-->). O cadastro não diz o motivo nem quem decidiu (`12_renovadas.py`).
- **Por que não 4,3 mil.** O TSE divulgou em 16/10, e a imprensa reproduziu, que 4.352 seções mudaram de local, com
  dados até 16/10. As "499.248 seções instaladas" citadas são urnas, a mesma unidade usada aqui. O TSE não informou o
  critério. A distribuição por estado não fecha com os dados seguintes: o TSE cita 982 seções em SP, 514 em MG, 431 no
  RJ e 312 na BA, e as urnas que mudam de prédio do 1º para o 2º turno, aqui, são <!--n:urnas_sp_mg_rj_ba-->27, 50, 5 e 10<!--/n-->. No Rio, o
  painel tinha 47 seções em 17/10, 19 em 18/10 e nenhuma em 19/10 (11h27).
- **Quando o cadastro não bate.** Quando o local muda de número e de nome, mas o cadastro reescreveu o endereço do
  local de sempre para o do prédio provisório, a urna quase certamente continua no mesmo prédio e fica de fora. Na
  primeira versão eram 32 urnas; as 12 de Timóteo-MG passaram a aparecer no mesmo prédio nos dois turnos no cadastro de
  17/10, 23h33, e as 20 de São Paulo, no de 18/10, 20h27, o que confirma o critério (no cadastro atual:
  <!--n:reescritas-->nenhuma urna<!--/n-->). Outras <!--n:mesmo_endereco_urnas-->17<!--/n--> têm o mesmo endereço nos dois turnos, em geral genérico ("S/N", povoado,
  aldeia), e continuam na conta com aviso no mapa. Quando o número do local é o mesmo nos dois turnos e o cadastro
  reescreve o nome e o endereço, mas o nome é o mesmo tirando a sigla e o endereço é o mesmo lugar escrito de outro
  jeito, a urna também fica de fora: são <!--n:nome_reescrito_urnas-->64<!--/n--> no cadastro atual, <!--h-->todas em Tracuateua-PA, onde "EMEF"
  virou "EMEIF" e "Vila da Flexeira" virou "Flexeira"<!--/h--> (em 2022, o critério tira <!--n:nome_reescrito_2022-->1 urna<!--/n-->). O mapa as mostra
  no filtro "Podem confundir", com as que contam com ressalva: as de mesmo endereço e as <!--n:nome_parecido_urnas-->7<!--/n--> de mesmo número
  com um nome contido no outro (<!--h-->Jacaraci-BA<!--/h-->), que continuam na conta.
- **No 1º turno, os eleitores dessas urnas votaram mais em Lula que o país** (<!--n:pct_lula-->49,1%<!--/n--> para Lula e <!--n:pct_flavio-->44,4%<!--/n--> para
  Flávio; no país, 45,2% contra 47,0%), perto do esperado pelos municípios onde estão (<!--n:lula_esperado_municipio-->49,9%<!--/n-->). O percentual
  muda de uma versão da lista para outra: <!--n:serie_lula-->52,3% nas 1.025 urnas de 18/10, 20h27; 46,7% nas 596 de 19/10, 11h27; 48,5% nas 475 de 19/10, 15h27; 50,0% nas 469 de 20/10, 6h27; 50,2% nas 470 de 20/10, 11h27; 50,4% nas 476 de 20/10, 12h32; 50,7% nas 470 de 20/10, 15h27; 50,7% nas 488 de 20/10, 20h27; 50,8% nas 462 de 21/10, 6h27; 48,7% nas 407 de 21/10, 11h27; 48,8% nas 364 de 21/10, 14h19; 48,6% nas 367 de 21/10, 15h27; 50,2% nas 340 de 21/10, 20h28; 50,5% nas 339 de 22/10, 6h28; 50,3% nas 313 de 22/10, 11h27; 50,8% nas 319 de 22/10, 15h27; 50,9% nas 334 de 22/10, 20h28; 50,9% nas 337 de 23/10, 6h27; 50,8% nas 338 de 23/10, 10h00; 49,1% nas 358 de 23/10, 10h47<!--/n-->. Comparado com o das urnas do mesmo
  município e da mesma zona eleitoral que não mudam, não há diferença detectável (<!--n:vizinhas_dif-->0,6 ponto a menos<!--/n--> para Lula,
  intervalo de 95% de <!--n:vizinhas_ic-->2,3 ponto a menos a 1,2 a mais<!--/n-->). Por local de votação (`09_por_local.py`), com as <!--n:urnas-->358<!--/n--> urnas, a
  associação entre voto em Lula e mudança entre todos os locais do país é pequena (<!--n:local_pais-->+0,01<!--/n--> ponto por 10 pontos de
  Lula), e <!--n:local_pais_frase-->o intervalo de 95% fica acima do zero<!--/n--> (<!--n:local_pais_ic-->+0,003 a +0,02<!--/n-->), <!--h-->como com as 340, 339 e 313 dos cadastros de 21/10, 20h28, e de 22/10, 6h28 e 11h27 (de +0,0002 a +0,03, de +0,0004 a +0,03 e de +0,002 a +0,02);
  com as 407, 364 e 367 dos de 21/10, 11h27, 14h19 e 15h27, incluía o zero (de −0,003 a +0,03 nos dois últimos);
  com as 469, 470, 476, 470, 488 e 462 das versões de 20/10 e de 21/10, 6h27, aparecia (+0,02, de +0,01 a +0,04),
  porque as mudanças estavam mais em lugares onde Lula vence; com as 475 do cadastro de 19/10, 15h27, ficava no limite
  da significância (+0,02, de +0,00 a +0,03); com as 596 do de 19/10, 11h27, não aparecia (+0,01, de −0,01 a
  +0,02)<!--/h-->. Comparando locais do mesmo estado (<!--n:local_estado_ic-->−0,01 a +0,03<!--/n-->) ou do mesmo município (<!--n:local_municipio_ic-->−0,03 a +0,02<!--/n-->), não aparece
  em nenhuma das medidas do script (votos em blocos de 10 mil e percentual de Lula, com o local de cadastro ou o do
  1º turno como unidade). Com a lista do painel de 17/10, que comparava com o local de cadastro, ela aparece dentro do
  estado em várias medidas, como na análise de [@DavidDinizK](https://x.com/DavidDinizK/status/2111616001443795222),
  mas não com o percentual de Lula e os votos válidos do local. O resultado depende da lista e da forma de medir. Não
  testamos se a diferença entre as listas é estatisticamente significativa: elas se sobrepõem, e comparar os
  intervalos a olho não basta. Em 2022, 47% dos eleitores das urnas que mudaram estavam no Nordeste; na lista atual de
  2026, <!--n:pct_nordeste-->30%<!--/n--> (49% no cadastro de 18/10, 20h27). O voto em Lula nas urnas que mudam fica perto do esperado pelo
  município onde estão (<!--n:pct_lula-->49,1%<!--/n-->, contra <!--n:lula_esperado_estado-->48,4%<!--/n--> pelo estado e <!--n:lula_esperado_municipio-->49,9%<!--/n--> pelo município; `11_geografia.py`).
- **Em 2022, não houve sinal de que a troca de prédio entre os turnos aumentasse a abstenção.** Nas 1.506 urnas que
  trocaram de prédio entre os turnos, a abstenção variou <!--n:efeito_2022-->0,08 ponto a menos<!--/n--> que nas vizinhas do mesmo município e
  zona (intervalo de 95% de <!--n:efeito_2022_ic-->0,24 a menos a 0,08 a mais<!--/n-->). Em outras comparações, vai de <!--n:sens_zona-->0,19 ponto a menos<!--/n--> (só a
  mesma zona; de <!--n:sens_zona_ic-->−0,37 a −0,03<!--/n-->) a <!--n:sens_local-->0,24 a mais<!--/n--> (mesmo local de cadastro, na mesma zona; de <!--n:sens_local_ic-->−0,05 a +0,53<!--/n-->). O
  resultado depende do grupo de comparação, mas nenhum mostra abstenção maior. É uma comparação entre urnas, não um
  experimento: essas urnas já tinham abstenção 0,8 ponto acima das vizinhas no 1º turno, e a conta supõe que, sem a
  mudança, a abstenção teria variado do mesmo jeito nos dois grupos.
- **O efeito estimado no resultado é próximo de zero.** Se 2026 repetir 2022, a vantagem de Flávio praticamente não
  mudaria (<!--n:margem-->−2<!--/n--> votos), diante de 2,24 milhões no 1º turno. O intervalo de 95% do efeito médio fica entre <!--n:margem_ic-->−15 e +9<!--/n-->
  votos e supõe que a troca de prédio tem o mesmo efeito em todas as urnas do mesmo tipo; se cada urna puder ter um
  efeito diferente, como as de 2022 tiveram, a faixa de previsão vai de <!--n:margem_previsao-->−102 a +103<!--/n--> votos. Nas outras comparações,
  o intervalo fica entre <!--n:outras_comparacoes-->−17 e +24<!--/n--> votos. A conta supõe que quem deixa de votar votaria como o resto da sua
  urna. Se, em vez do efeito de 2022, valesse o medido no 1º turno de 2026 nas urnas que saíram do local de sempre
  (<!--n:abst1t_var-->0,64<!--/n--> ponto a mais de abstenção, veja abaixo), aplicado às <!--n:sens_2t_urnas-->277<!--/n--> urnas que saem do local de sempre só no 2º
  turno, a vantagem de Flávio mudaria em cerca de <!--n:sens_2t_margem-->+12<!--/n--> votos (<!--n:sens_2t_ic-->+9 a +15<!--/n-->; `13_abstencao_1t.py`). Num cenário
  extremo, se ninguém votasse nessas urnas e os votos do 1º turno se mantivessem, Lula perderia <!--n:teto_votos-->4.018<!--/n--> votos líquidos
  (<!--n:teto_pct-->0,18%<!--/n--> da diferença). Não é um limite superior: a conta deixa de lado os cerca de <!--n:outros_votos-->5 mil<!--/n--> votos em outros
  candidatos nessas urnas, que no 2º turno vão para um dos dois, e uma abstenção que atinja mais um lado que o outro.

O voto para governador não foi calculado: o arquivo nacional de votação por seção do TSE traz só presidente. Nos
estados com 2º turno para governador (AC, AM, ES, RN, TO e DF), as urnas que mudam de prédio são: <!--n:gov_com-->Amazonas 21, Espírito Santo 16 e Rio Grande do Norte 26<!--/n-->,
com <!--n:gov_aptos-->21 mil<!--/n--> eleitores; não há nenhuma <!--n:gov_sem-->no Acre, no Distrito Federal e no Tocantins<!--/n-->.

Para quem faltou no 1º turno, a referência é o último local onde votou (em geral o de 2024), e essa comparação não foi
feita. O local de cadastro serve de aproximação: <!--n:painel17_total-->7.213<!--/n--> urnas votam no 2º turno fora dele, com <!--n:fora_2t_aptos-->2,17 milhões<!--/n--> de
eleitores, dos quais <!--n:fora_2t_faltaram-->440 mil<!--/n--> faltaram no 1º turno. Em <!--n:ja_fora-->6.920<!--/n--> dessas urnas a mudança já valia no dia 4, e a
abstenção nelas foi de <!--n:ja_fora_abst-->20,2%<!--/n-->, perto dos <!--n:abst_pais-->20,8%<!--/n--> do país (`fora_do_cadastro_2t` em `saida/numeros.json`).

**A saída do local de sempre no 1º turno teve efeito pequeno na abstenção** (`13_abstencao_1t.py`). Nas <!--n:abst1t_urnas-->6.990<!--/n--> urnas
que, pelo cadastro, votaram no 1º turno de 2026 fora do local de cadastro, a abstenção foi <!--n:abst1t_nivel-->0,64<!--/n--> ponto maior que nas
vizinhas do mesmo município e zona que votaram no local de cadastro (intervalo de 95% de <!--n:abst1t_nivel_ic-->0,47 a 0,81<!--/n-->). Em 2022, as
mesmas urnas tinham a abstenção das vizinhas (<!--n:abst1t_2022-->−0,01<!--/n-->, de <!--n:abst1t_2022_ic-->−0,22 a +0,19<!--/n-->), e a variação de 2022 para 2026 foi
<!--n:abst1t_var-->0,64<!--/n--> ponto maior (de <!--n:abst1t_var_ic-->0,49 a 0,79<!--/n-->; <!--n:abst1t_var_urnas-->5.520<!--/n--> urnas com a mesma seção e o mesmo local de cadastro nos dois
anos). São cerca de <!--n:abst1t_eleitores-->13 mil<!--/n--> eleitores a menos, em <!--n:abst1t_aptos-->2,1 milhões<!--/n-->. Como essas urnas deram <!--n:abst1t_lula-->50,3%<!--/n--> a Lula e <!--n:abst1t_flavio-->42,9%<!--/n--> a
Flávio, equivale a cerca de <!--n:abst1t_votos-->900<!--/n--> votos líquidos a menos para Lula no 1º turno (de <!--n:abst1t_votos_ic-->700 a 1.100<!--/n-->), <!--n:abst1t_votos_pct-->0,04%<!--/n--> da
diferença nacional. Esse efeito já está no resultado do dia 4.

## Como acompanhamos as atualizações do TSE

O TSE troca o cadastro de locais (`eleitorado_local_votacao_2026.zip`) no portal de dados abertos sem aviso, às vezes
mais de uma vez por dia, e o portal guarda só a última versão. Entre <!--n:primeira_data-->17/10<!--/n--> e <!--n:ultima_data-->23/10<!--/n--> baixamos <!--n:n_versoes-->24<!--/n--> versões; outra,
publicada na noite de 19/10, foi substituída antes que a baixássemos, e não dá mais para recuperá-la. O CDN do portal
também pode entregar uma cópia antiga em cache a quem pede o endereço puro.

Por isso, desde 20/10, `scripts/00_atualizar.py` roda a cada 20 minutos, até o dia 25, pelo Agendador de Tarefas do
Windows, num computador nosso (não no GitHub):

1. pergunta ao CDN a data do arquivo (`Last-Modified`), com um parâmetro que fura o cache;
2. se a data é nova, baixa o arquivo e guarda em `dados/novos/`, para nenhuma versão se perder;
3. lê de dentro do CSV a data e a hora de geração (`DT_GERACAO` e `HH_GERACAO`), que é a que citamos;
4. se a versão é mais nova que a em uso, guarda a anterior em `dados/anteriores/`, registra a nova em
   `scripts/versoes.py` e roda os scripts na ordem, refazendo os números, os dados da página e os cartões;
5. por último, `18_texto.py` reescreve os números da lista atual no texto da página e deste README, e
   `19_conferir.py` procura o que ficou para trás (veja abaixo);
6. avisa por notificação do Windows, do tipo lembrete, que fica na tela até ser fechada, com o número de pendências
   que a conferência achou.

Tudo roda sem abrir janela: o Agendador chama o `pythonw`, e os scripts e o `git` rodam num console oculto (até 21/10, 15h27,
cada `git` chamado pelos scripts abria um terminal na tela a cada rodada).

As versões de <!--n:versoes_automaticas-->20/10, 11h27, 12h32, 15h27 e 20h27; de 21/10, 6h27, 11h27, 14h19, 15h27 e 20h28; de 22/10, 6h28, 11h27, 15h27 e 20h28; e de 23/10, 6h27, 10h00, 10h47 e 11h27<!--/n--> chegaram assim.

Se uma versão nova chega quando a anterior ainda não tem texto nem commit (`saida/` ou `docs/` com mudanças
pendentes), o script só baixa e avisa: o commit em uso precisa ser o da versão anterior, porque é dele que as
comparações leem a lista. Foi o que aconteceu em 20/10: a versão de 11h27 foi aplicada às 11h42, a de 12h32 chegou às
12h42 e esperou; a de 11h27 ganhou um commit só com as saídas dos scripts (`6c651e5`), e o texto veio junto com a de
12h32. O registro de cada conferência fica em `dados/novos/automatico.log`.

A versão de 15h27 chegou às 15h42 e foi aplicada, mas o `07_versoes.py` quebrou com as 15 seções repetidas, e o
repositório ficou pela metade: zip trocado, `versoes.py` com a linha nova, `saida/` com as saídas de `02` e `03`.
Desde então:

- antes de aplicar, o script confere o cadastro novo: as colunas de sempre, os dois turnos e o número de linhas, que
  não pode variar mais de 2%; se não passa, nada muda;
- se um script falha, desfaz tudo: o zip em uso, `versoes.py`, `saida/` e `docs/` voltam ao que eram, e a versão
  nova volta para `dados/novos/`, marcada em `dados/novos/falhou.txt` para não ser tentada de novo a cada 20 minutos;
  a notificação diz qual script falhou;
- depois de corrigir o script, `--aplicar` aplica a versão, e `--rodar` refaz só os scripts, sem trocar o cadastro;
- `02_mudancas.py` aceita uma seção repetida no mesmo turno (fica o local da versão anterior; veja acima), e a
  notificação de sucesso avisa quando `saida/log_02.txt` tem avisos.

A versão de 20h27 chegou às 20h42 e foi aplicada sem erro, mas a primeira passada saiu com 481 urnas: as 15 seções
continuavam repetidas, também na versão anterior, e o `02_mudancas.py` não achava nela um local único, caía no do
1º turno e tirava da lista as 7 de Almirante Tamandaré sem que o TSE tivesse mudado nada. Agora, quando a seção já
vinha repetida, vale o local que ficou na versão anterior, lido do `saida/duplicadas_2026.csv` do commit dela. O
aviso de `log_02` mostrava "ficou o local da versão anterior: 0"; conferimos antes de publicar.

A versão de 21/10, 6h27, chegou às 8h16, depois de o computador passar a madrugada parado (a última conferência
tinha sido às 23h41). Ela já não tinha seções repetidas; o `02_mudancas.py` agora apaga o `duplicadas_2026.csv`
quando não há nenhuma, para o da versão anterior não ficar valendo. E, pela primeira vez, saíram da lista urnas
que não iam voltar ao local de sempre: o `12_renovadas.py` passou a contá-las à parte
(`ficam_no_local_de_sempre` em `saida/renovadas.json`), fora das que iam voltar.

<!--h-->A versão de 21/10, 11h27,<!--/h--> chegou às 11h45 e foi aplicada sem erro, mas trouxe outra novidade: em 66 urnas, mudou o
local do 1º turno, e o `12_renovadas.py`, que classificava cada saída pelo tipo da urna no cadastro atual, contou
essas urnas entre as que iam voltar ao local de sempre e passaram a ficar no prédio provisório. Agora ele compara
o local do 1º turno de hoje com o da versão anterior à saída e conta à parte as que mudaram
(`primeiro_turno_reescrito`).

<!--h-->A versão de 21/10, 14h19,<!--/h--> foi a primeira atualizada com os números do texto preenchidos por script (abaixo). Na
mesma rodada, o `07_versoes.py` passou a ler os locais da versão anterior no zip dela, em `dados/anteriores/`: antes,
as urnas que entravam na lista não tinham local anterior para comparar e saíam todas como "os dois" turnos mudados.
E o `12_renovadas.py` passou a contar como renovadas só as urnas que voltavam ao local de sempre no primeiro
cadastro, com aviso se sair alguma que não voltava.

<!--h-->A versão de 21/10, 20h28,<!--/h--> chegou às 20h45, mas o computador suspendeu às 21h09, no meio do `09_por_local.py`. A
tarefa agendada tem limite de 45 minutos, e o Agendador encerrou o processo sem que ele pudesse desfazer nada: ficaram
o zip novo, a linha nova em `versoes.py` e as saídas até o `16_evolucao.py`, e as conferências seguintes não tentaram
de novo, porque a versão já constava como em uso. Ela foi terminada com `--rodar`.

### O texto a cada versão

Uma revisão de 21/10 achou, na página, números que tinham ficado de versões anteriores: a média da distância, de
uma versão de dois dias antes; o total de uma categoria que outro cadastro tinha mudado; "a versão anterior" apontando para uma
versão que já não era a anterior; e frases cuja conclusão dependia de um intervalo que passou a incluir o zero. Por
isso o texto passou a ter três partes:

- **Números da lista atual, preenchidos por script.** Todo número que descreve a lista atual, na página e neste
  README, fica entre marcadores de comentário HTML, invisíveis na página e no GitHub: `<!--n:urnas-->364<!--/n-->`.
  O `18_texto.py` calcula cada valor a partir das saídas dos outros scripts (`numeros.json`, `renovadas.json`,
  `abstencao_1t.json`, `geografia.json`, `docs/dados.json` e os `numeros.json` de cada versão no git), já no formato
  do texto (1.234, 0,17%, "12 mil", "−5 e +2", listas de estados com a preposição certa), e reescreve o que está
  entre os marcadores. Blocos inteiros vêm prontos entre `<!--g:chave-->` e `<!--/g:chave-->`: a tabela de versões do
  alto da página, a tabela de fontes, a barra das quatro situações e a linha da regressão por local. A descrição da
  página (`<meta>`) e a versão nos endereços dos JSON (`<meta name="versao-dados">`, para o cache do navegador não
  misturar texto novo com dados velhos) também. Todos os valores ficam em `saida/texto.json`. Uma chave usada no
  texto que o script não conhece faz ele parar, e ele lista as chaves que calculou e não foram usadas.
- **História, escrita à mão e marcada.** O que mudou em cada versão (o quadro "O que mudou, versão por versão" e os
  parágrafos "Atualização de..." deste README) continua escrito à mão e não muda depois. Um trecho de história fora
  desses lugares é marcado com `<!--h-->...<!--/h-->`.
- **Conferência.** O `19_conferir.py` grava `saida/log_19.txt` com quatro listas: marcadores com valor diferente do
  que o `18_texto.py` calcularia agora; valores da versão anterior (o `texto.json` do commit dela) e o rótulo do
  cadastro anterior que ainda aparecem no texto, fora dos marcadores e da história; regras de interpretação que
  deixaram de valer (frases que dependem de um intervalo incluir o zero, da ordem dos estados, do sinal de um efeito
  ou de uma contagem ser zero); e o que continua manual. Termina com `pendências: N`. No `00_atualizar.py`, ele roda
  sem desfazer nada: o que ele acha é trabalho para o texto, não erro dos dados.

O que continua à mão está em [`CHECKLIST.md`](CHECKLIST.md): o resumo do alto da página, o parágrafo da versão nova,
o parágrafo e a linha da tabela deste README, o subtítulo do cartão 10, os achados da conferência, o commit, a
publicação e o post. A comparação entre cada versão e a anterior fica em `saida/versoes_*.csv`, e a lista de urnas
de cada versão, no histórico do git (os commits estão em `scripts/versoes.py`).

Para fazer à mão: `python -P scripts/00_atualizar.py --verificar` (baixa a versão nova, se houver),
`python -P scripts/00_atualizar.py --aplicar` (põe no lugar e roda os scripts, o 18 e o 19) e, depois de mexer no
texto, `python -P scripts/18_texto.py` e `python -P scripts/19_conferir.py`, até `pendências: 0`.

## Como foi feito

A urna é a seção principal; os eleitores de seção agregada votam nela. Os aptos são o eleitorado federal de cada urna em cada turno.
Uma urna muda de prédio quando o número do local no 2º turno é diferente do 1º (salvo se o nome e o endereço
continuarem iguais), ou quando o número é o mesmo mas o nome e o endereço mudam juntos. O local do 1º turno é o que o
cadastro registra: o arquivo de votação por seção não diz onde a urna funcionou, e o TSE reescreveu esse registro em
<!--n:primeiro_turno_reescrito-->243<!--/n--> urnas desde o cadastro de 21/10, 6h27. Coordenada só vale se cair dentro do
município, pela malha do IBGE. Os detalhes estão no cabeçalho de cada script.

| Script | O que faz |
| --- | --- |
| `01_votos_1t.py` | Votos para presidente por seção: 1º turno de 2026 e os dois turnos de 2022 |
| `02_mudancas.py` | Urnas que mudam de prédio entre os turnos, em 2026 e 2022, e a conferência com o painel do TSE |
| `03_impacto.py` | Efeito da troca sobre a abstenção em 2022, sensibilidade e o peso das mudanças de 2026 na margem |
| `04_exportar_web.py` | Dados da página (`docs/dados.json`) |
| `05_imagem_x.py` | Cartão 1600 × 900 para redes sociais (`saida/imagem_x.png`) |
| `06_contornos.py` | Contornos de estados e municípios para o mapa (`docs/contornos.json`) |
| `00_atualizar.py` | Confere se o TSE publicou um cadastro novo e guarda toda versão nova em `dados/novos/` (`--verificar`); põe a mais nova no lugar, registra a versão em `versoes.py` e roda os scripts na ordem (`--aplicar`); `--automatico` faz os dois e avisa por notificação do Windows, chamado a cada 20 minutos pelo Agendador de Tarefas até 25/10. Os números da lista atual no texto da página e do README são preenchidos por `18_texto.py`; o resto do texto continua escrito à mão |
| `versoes.py` | As versões do cadastro usadas na página, com o commit de cada uma; 07, 12, 14, 18 e os cartões leem daqui |
| `07_versoes.py` | O que mudou entre a lista do cadastro anterior e a atual (a última linha de `versoes.py`; hoje, `saida/versoes_22out_15h27.csv`, entre os cadastros de 22/10, 11h27, commit `f287d0c`, e 22/10, 15h27), pelo número, pelo nome e pelo endereço do local, com os locais da versão anterior lidos do zip dela. As comparações anteriores ficam no git: entre os cadastros de 22/10, 6h28 e 11h27 (`saida/versoes_22out_11h27.csv`, commit `f287d0c`), entre os cadastros de 21/10, 20h28, e 22/10, 6h28 (`saida/versoes_22out_06h28.csv`, commit `17f4ce6`), entre os cadastros de 21/10, 15h27 e 20h28 (`saida/versoes_21out_20h28.csv`, commit `50fa582`), entre os cadastros de 21/10, 14h19 e 15h27 (`saida/versoes_21out_15h27.csv`, commit `d4e83d3`), entre os cadastros de 21/10, 11h27 e 14h19 (`saida/versoes_21out_14h19.csv`, commit `0f3a6a2`), entre os cadastros de 21/10, 6h27 e 11h27 (`saida/versoes_21out_11h27.csv`, commit `90059c6`), entre os cadastros de 20/10, 20h27 e 21/10, 6h27 (`saida/versoes_21out_06h27.csv`, commit `d1c3f30`), entre os cadastros de 20/10, 15h27 e 20h27 (`saida/versoes_20out_20h27.csv`, commit `a395125`), entre os cadastros de 20/10, 12h32 e 15h27 (`saida/versoes_20out_15h27.csv`, commit `b9452ce`), entre os cadastros de 20/10, 11h27 e 12h32 (`saida/versoes_20out_12h32.csv`, commit `371bbe0`), entre os cadastros de 20/10, 6h27 e 11h27 (`saida/versoes_20out_11h27.csv`, commit `6c651e5`), entre os de 19/10, 15h27 e 20/10, 6h27 (`saida/versoes_20out_06h27.csv`, commit `f292653`), entre os cadastros de 19/10, 11h27 e 15h27 (`saida/versoes_19out_tarde.csv`, commit `6804293`), entre os cadastros de 18/10, 20h27 e 19/10, 11h27 (`saida/versoes_19out.csv`, commit `4925b73`), entre os de 18/10, 11h27 e 20h27 (`saida/versoes_18out_noite.csv`, commit `917ba7a`), entre os de 17/10, 23h33 e 18/10, 11h27 (`saida/versoes_18out.csv`, commit `2272612`) e entre os de 17/10, 6h28 e 23h33 (`saida/versoes_17_18out.csv`, commit `fa873d1`) |
| `08_imagem_distancia.py` | Cartão 1600 × 900 com a distância entre o prédio do 1º e o do 2º turno (`saida/imagem_distancia.png`) |
| `09_por_local.py` | Locais de votação com urna na lista e voto no 1º turno, com as listas do painel de 17/10 e 18/10 e a daqui |
| `10_imagem_por_local.py` | Cartão 1600 × 900 com os locais na lista por faixa de voto em Lula (`saida/imagem_por_local.png`) |
| `11_geografia.py` | Onde ficam as urnas que mudam, em 2022 e 2026, e o voto esperado pela geografia |
| `12_renovadas.py` | Como a lista encolheu nas versões do cadastro: urnas que iam voltar ao local de sempre e passaram a ficar no prédio do 1º turno, por estado (e, à parte, as que iam sair do local de sempre e passaram a ficar nele e as que tiveram o local do 1º turno reescrito), e a taxa de volta comparada com 2022 (rode depois de 07 e antes de 04) |
| `13_abstencao_1t.py` | Abstenção no 1º turno nas urnas que já votaram fora do local de cadastro, comparada com as vizinhas, em 2026 e desde 2022 (`saida/abstencao_1t.json`) |
| `14_imagem_versoes.py` | Cartão 1600 × 900 com as urnas e o efeito estimado em cada versão do cadastro (`saida/imagem_versoes.png`) |
| `15_capa_linkedin.py` | Capa 1920 × 1080 para o artigo no LinkedIn (`saida/capa_linkedin.png`) |
| `16_evolucao.py` | A situação de cada urna em cada versão do cadastro (`docs/evolucao.json`), para o mapa e os quadrados animados da seção "Como a lista encolheu" (rode depois de 03) |
| `17_gif_evolucao.py` | Cartão animado 1200 × 675 com o mapa da evolução da lista, versão por versão (`saida/evolucao.gif`) |
| `18_texto.py` | Os números da lista atual no texto da página e deste README, entre marcadores, reescritos a partir das saídas dos outros scripts (rode depois deles); todos os valores ficam em `saida/texto.json` |
| `19_conferir.py` | Confere o texto depois do 18: marcadores desatualizados, números e rótulo da versão anterior que ficaram no texto, regras de interpretação que deixaram de valer e o que falta do `CHECKLIST.md` (`saida/log_19.txt`) |
| `20_imagem_reescritos.py` | Cartão 1600 × 900 com as urnas que não contam porque o cadastro só reescreveu o nome e o endereço do local (mesmo número), com os registros dos dois turnos e um mapa com fundo do OpenStreetMap (`saida/imagem_reescritos.png`); avulso, fora do `00_atualizar.py` |
| `ibge.py` | Malhas e códigos de município do IBGE, usados por 02 e 06 |

Para rodar do zero, baixe para `dados/` os arquivos do [portal de dados abertos do TSE](https://dadosabertos.tse.jus.br/)
(cerca de 630 MB, fora do git) e rode os scripts em ordem com `python -P scripts/0N_....py`:

- `votacao_secao_2026_BR.zip` e `votacao_secao_2022_BR.zip` (Resultados › Votação por seção eleitoral)
- `eleitorado_local_votacao_2026.zip` e `eleitorado_local_votacao_2022.zip` (Eleitorado › Eleitorado por local de
  votação). O de 2026 usado aqui foi gerado em <!--n:cadastro_extenso-->23/10 às 11h27<!--/n--> (Brasília) e já traz o 2º turno. O portal guarda só
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
  (`eleitorado_local_votacao_2026_gerado_18out_2327utc.zip`), em 19/10 às 11h27
  (`eleitorado_local_votacao_2026_gerado_19out_1427utc.zip`), em 19/10 às 15h27
  (`eleitorado_local_votacao_2026_gerado_19out_1827utc.zip`), em 20/10 às 6h27
  (`eleitorado_local_votacao_2026_gerado_20out_0927utc.zip`), em 20/10 às 11h27
  (`eleitorado_local_votacao_2026_gerado_20out_1427utc.zip`), às 12h32
  (`eleitorado_local_votacao_2026_gerado_20out_1532utc.zip`), às 15h27
  (`eleitorado_local_votacao_2026_gerado_20out_1827utc.zip`) e às 20h27
  (`eleitorado_local_votacao_2026_gerado_20out_2327utc.zip`), em 21/10 às 6h27
  (`eleitorado_local_votacao_2026_gerado_21out_0927utc.zip`) e às 11h27
  (`eleitorado_local_votacao_2026_gerado_21out_1427utc.zip`), a exportação do painel de 18/10, 7h09
  (`painel_18out_0709.csv.zip`), e as listas de urnas das versões anteriores (`urnas_mudadas_2026_17out.csv`,
  `urnas_mudadas_2026_18out_manha.csv`, a do cadastro de 17/10, 23h33, `urnas_mudadas_2026_18out_tarde.csv`, a do
  de 18/10, 11h27, `urnas_mudadas_2026_18out_noite.csv`, a do de 18/10, 20h27, e
  `urnas_mudadas_2026_19out_manha.csv`, a do de 19/10, 11h27).

As malhas do IBGE são baixadas sozinhas para `dados/ibge/` na primeira execução. Precisa de Python com pandas, numpy,
shapely e matplotlib. As tabelas pequenas ficam em `saida/`; as tabelas completas por urna (`saida/urnas_*.csv.gz` e
`saida/votos_*_secao.csv.gz`) são geradas pelos scripts e não vão para o git.

Principais saídas:

- `saida/urnas_mudadas_2026.csv`: as <!--n:urnas-->358<!--/n--> urnas, com prédio antigo e novo, critério, distância, aviso de mesmo
  endereço e voto no 1º turno
- `saida/mesmo_predio_2026.csv`: as urnas retiradas porque o cadastro reescreveu o endereço (no cadastro atual: <!--n:reescritas-->nenhuma urna<!--/n-->)
  ou o nome e o endereço com o mesmo número de local (<!--n:nome_reescrito_urnas-->64<!--/n-->), com o tipo de cada uma
- `saida/urnas_reescritas_2026.csv`: essas mesmas urnas, com o voto no 1º turno, para o filtro "Podem confundir" do mapa
- `saida/painel_tse.csv`: as 2.015 seções do painel de 18/10 no Brasil, com a classificação de cada uma aqui e, quando
  não contam, o motivo
- `saida/versoes_22out_15h27.csv`: as urnas da lista do cadastro de <!--h-->22/10, 11h27<!--/h--> e da atual, com o que mudou no cadastro
- `saida/duplicadas_2026.csv`: as seções que aparecem mais de uma vez no mesmo turno do cadastro atual, com o local
  que ficou e o da versão anterior (só existe quando há alguma; a dos cadastros de 20/10, 15h27 e 20h27 está no
  commit `a395125`, <!--h-->e a do de 21/10, 20h28, no `50fa582`<!--/h-->)
- `saida/versoes_22out_11h27.csv`, `saida/versoes_22out_06h28.csv`, `saida/versoes_21out_20h28.csv`, `saida/versoes_21out_15h27.csv`, `saida/versoes_21out_14h19.csv`, `saida/versoes_21out_11h27.csv`, `saida/versoes_21out_06h27.csv`, `saida/versoes_20out_20h27.csv`, `saida/versoes_20out_15h27.csv`, `saida/versoes_20out_12h32.csv`, `saida/versoes_20out_11h27.csv`, `saida/versoes_20out_06h27.csv`, `saida/versoes_19out_tarde.csv`, `saida/versoes_19out.csv`, `saida/versoes_18out_noite.csv`, `saida/versoes_18out.csv`
  e `saida/versoes_17_18out.csv`: as comparações anteriores (<!--h-->22/10, 6h28 × 11h27; 21/10, 20h28 × 22/10, 6h28; 21/10, 15h27 × 20h28; 21/10, 14h19 × 15h27; 21/10, 11h27 × 14h19<!--/h-->; 21/10, 6h27 × 11h27; 20/10, 20h27 × 21/10, 6h27; 20/10, 15h27 × 20h27; 20/10, 12h32 × 15h27; 20/10, 11h27 × 12h32; 20/10, 6h27 × 11h27; 19/10, 15h27 × 20/10, 6h27; 19/10, 11h27 × 15h27; 18/10, 20h27 × 19/10, 11h27; 18/10,
  11h27 × 20h27; 17/10, 23h33 × 18/10, 11h27; 17/10, 6h28 × 23h33)
- `saida/impacto_2022.csv` e `saida/impacto_uf_2026.csv`: efeito medido em 2022 e resumo por estado
- `saida/geografia.json`, `saida/geografia_regioes.csv` e `saida/geografia_ufs.csv`: as urnas que mudam por região e estado, em 2022 e 2026
- `saida/por_local_faixas.csv`: percentual de locais na lista por faixa de voto em Lula, no país e comparado com o estado e o município
- `saida/por_local.csv`: regressão por local de votação (chance de o local estar na lista e voto no 1º turno), com as três listas
- `saida/renovadas_uf.csv` e `saida/renovadas.json`: as urnas que saíram da lista a cada versão do cadastro, por estado, e a
  taxa de volta ao local de sempre em cada versão e em 2022
- `saida/revisar_distancias.csv`: mudanças de mais de 10 km, para conferência
- `docs/evolucao.json`: cada urna que esteve na lista em alguma versão do cadastro, com a situação dela em cada versão
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
