# Revisor de design

Contrato do modo C. Entrada: o trecho que seria gravado e o tipo da feature. Saída: `ok`, `recusar` ou `escalar`.

O revisor não recebe o resultado do teste. A função no lab é `revisor_design(tipo, trecho)`.

| O que vê no trecho | Resposta |
| --- | --- |
| lista copiada do registro, ou o corpo de `gravar` | `recusar` |
| parâmetro `legacy` | `recusar` |
| parâmetro `streaming` na feature de export | `escalar` |
| o resto | `ok` |

`escalar` não aceita o débito e não o rejeita como regra. O lab grava a versão limpa e conta um escalonamento. Aceitar `streaming` fica fora do script.
