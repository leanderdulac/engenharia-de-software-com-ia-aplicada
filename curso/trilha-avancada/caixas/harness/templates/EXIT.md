# EXIT

Saídas. Sem isto o agente repete o mesmo conserto até o orçamento acabar e ainda diz que terminou.

| Sinal | Ação |
| --- | --- |
| sensor verde nesta função | próximo id |
| o mesmo erro duas vezes (`muro_db`, ferramenta vazia, sensor vermelho) | parar, registrar em `dead ends` e `blocked`, escalar |
| teto de tentativas (aqui: 2 por função) | parar, registrar, escalar |
| id fora do contrato (`export_claims`) | não escrever; escalar |

«Pronto» só sai daqui, e só com o número que o sensor devolveu.
