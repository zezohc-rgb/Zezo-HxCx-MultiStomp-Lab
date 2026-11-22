# Refinamento do Zezo CE-2

Referência de software: commit `213148d0abbeda970926c5b69f53ed66ca080c49` e preflight #120.

- **Clock e modulação.** A referência já usava uma onda triangular e atraso inversamente proporcional ao clock, com interpolação linear. O novo polinômio inclui termos até a sétima ordem e mantém o centro nominal em 3,90 ms. Com DEPTH no máximo, o atraso nominal percorre de 3,20 a 4,99 ms antes do atraso de grupo dos filtros. RATE mantém a faixa de 0,30 a 3,50 Hz e concentra mais curso na região lenta. Ajustes de ambos os controles são suavizados com constante de tempo de aproximadamente 20 ms.
- **Filtragem.** O caminho BBD conserva três polos passa-baixas antes e depois da linha de atraso e um passa-altas de recuperação. A de-ênfase agora é calculada como a inversa discreta da pré-ênfase, com ganho unitário em DC para o par isolado. O par aproxima a função das redes do CE-2. A linha de atraso modulada e os filtros de banda continuam a colorir o retorno.
- **Mix e dinâmica.** O ganho final fixo da referência foi removido e o coeficiente wet passou de 0,390 para 0,42, com dry em 0,58. O wet é mono e recebe a média das entradas, enquanto o dry preserva cada canal. Uma saturação suave e simétrica na entrada da linha BBD mantém ganho unitário em pequeno sinal e comprime picos após a pré-ênfase. Frequências, taper, proporção e limiar digital são escolhas de modelagem. Ainda falta calibrá-los com capturas de um CE-2 físico.
- **LCD e formato.** A caixa, os dois knobs, o LED e a placa do pedal foram preservados. RATE e DEPTH agora usam glifos ampliados, com as áreas de valores reservadas. O alvo continua sendo a MS-70CDR original e o candidato conserva o ID 960, os slots e as faixas de parâmetros, o empacotador e o nome `ZZC2S2.ZDL`.

## Verificação

Execute `python3 -m unittest discover -s zezo-ce2/tests -v` e `python3 -m unittest discover -s tests -v` a partir da raiz. O teste de áudio compila o próprio C de estágio 2 no host com UBSan e cobre inicialização, bypass, os extremos de RATE e DEPTH, atraso por impulso, suavização, filtragem, resposta dinâmica e roteamento. O workflow **Zezo CE-2 source preflight** compila com o TI C6000, verifica a estrutura ZDL e publica o candidato experimental. A validação física e a comparação sonora com um CE-2 original continuam pendentes.

## Modelo baseado na placa ET-50B

A revisão de circuito usa a seção CE-2 das notas de serviço Roland de fevereiro de 1987. O percurso é jack → buffer Q1 → pré-ênfase IC1 → divisão dry/wet. No wet, seguem o acoplamento C5, o filtro Q2, o BBD MN3007, o acoplamento C10, o filtro Q3 e o acoplamento C14. Os dois ramos se encontram no somador IC1 com de-ênfase em realimentação. [Notas de serviço Roland, diagrama CE-2 e layout ET-50B](https://audioschematics.dk/wp-content/uploads/media/schematics/effects/boss-CE-2.pdf#page=1)

- **Pré-ênfase e de-ênfase.** C3/C15 de 6,8 nF e as resistências de 10 e 47 kΩ dão tempos de 68 e 387,6 µs. O DSP aplica a transformação bilinear do par de funções complementares. No ramo dry, o produto do par ideal é unitário, por isso o código pode somar o dry direto ao wet já de-enfatizado.
- **Acoplamentos wet.** C5/R8 dá 48,2 Hz e C10/R15 dá 14,6 Hz. C14 com R20 em paralelo com R22 dá cerca de 107 Hz, aproximando a saída de Q3 como fonte de baixa impedância. O DSP discretiza esses três polos em seus respectivos pontos do percurso.
- **Soma.** R21 e R22 têm 47 kΩ cada. O DSP usa pesos iguais e um fator global de 0,5 para margem digital na Zoom. O wet real tem ganho dependente da frequência por causa dos filtros e do BBD.
- **Clock.** O polo R35/C21 limita a modulação aplicada ao clock em cerca de 72 Hz. O DSP aplica esse polo à onda triangular antes de calcular o atraso. O comportamento de Q4/Q5 e do MN3101 ainda é aproximado pela curva de atraso existente. A faixa e a curva dos knobs e o limiar de saturação continuam sujeitos à calibração. Os passa-baixas Q2/Q3 também permanecem aproximados por três polos digitais existentes.
