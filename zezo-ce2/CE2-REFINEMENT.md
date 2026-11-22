# Refinamento do Zezo CE-2

Referência de software: commit `213148d0abbeda970926c5b69f53ed66ca080c49` e preflight #120.

- **Clock e modulação.** A referência já usava uma onda triangular e atraso inversamente proporcional ao clock, com interpolação linear. O novo polinômio inclui termos até a sétima ordem e mantém o centro nominal em 3,90 ms. Com DEPTH no máximo, o atraso nominal percorre de 3,20 a 4,99 ms antes do atraso de grupo dos filtros. RATE mantém a faixa de 0,30 a 3,50 Hz e concentra mais curso na região lenta. Ajustes de ambos os controles são suavizados com constante de tempo de aproximadamente 20 ms.
- **Filtragem.** O caminho BBD conserva três polos passa-baixas antes e depois da linha de atraso e um passa-altas de recuperação. A de-ênfase agora é calculada como a inversa discreta da pré-ênfase, com ganho unitário em DC para o par isolado. O par aproxima a função das redes do CE-2. A linha de atraso modulada e os filtros de banda continuam a colorir o retorno.
- **Mix e dinâmica.** O ganho final fixo da referência foi removido e o coeficiente wet passou de 0,390 para 0,42, com dry em 0,58. O wet é mono e recebe a média das entradas, enquanto o dry preserva cada canal. Uma saturação suave e simétrica na entrada da linha BBD mantém ganho unitário em pequeno sinal e comprime picos após a pré-ênfase. Frequências, taper, proporção e limiar digital são escolhas de modelagem. Ainda falta calibrá-los com capturas de um CE-2 físico.
- **LCD e formato.** A caixa, os dois knobs, o LED e a placa do pedal foram preservados. RATE e DEPTH agora usam glifos ampliados, com as áreas de valores reservadas. O alvo continua sendo a MS-70CDR original e o candidato conserva o ID 960, os slots e as faixas de parâmetros, o empacotador e o nome `ZZC2S2.ZDL`.

## Verificação

Execute `python3 -m unittest discover -s zezo-ce2/tests -v` e `python3 -m unittest discover -s tests -v` a partir da raiz. O teste de áudio compila o próprio C de estágio 2 no host com UBSan e cobre inicialização, bypass, os extremos de RATE e DEPTH, atraso por impulso, suavização, filtragem, resposta dinâmica e roteamento. O workflow **Zezo CE-2 source preflight** compila com o TI C6000, verifica a estrutura ZDL e publica o candidato experimental. A validação física e a comparação sonora com um CE-2 original continuam pendentes.
