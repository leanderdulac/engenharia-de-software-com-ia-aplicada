# Leituras opcionais da Trilha Avançada

Não valem nota. Não substituem CA*. **Nenhum PDF de livro está neste repositório.** O aluno baixa o que quiser, na licença de cada fonte.

## Lindholm, Wahlström, Lindsten & Schön (CUP)

- Andreas Lindholm, Niklas Wahlström, Fredrik Lindsten, Thomas B. Schön. *Machine Learning — A First Course for Engineers and Scientists*. Cambridge University Press, 1ª ed. impressa **2022**, ISBN **9781108843607**. Site oficial: <https://smlbook.org> (acesso 2026-11-18).
- Rascunho PDF: o site aponta um draft da 2ª ed. A numeração abaixo segue os **títulos** publicados na tabela de conteúdos do site em 2026-11-18 (2ª ed. em preparação). Um rascunho datado **4/mar/2026** pode diferir; a 2ª ed. impressa pode mudar de novo. Cite por **tema**, não por página.
- **Licença (crítico):** o material do livro/rascunho é para visualização e download de **uso pessoal**. **Não** redistribuir, **não** revender, **não** usar em obras derivadas. Esta trilha **não** copia texto, figura, exercício, notação nem estrutura de capítulo. Aula e lab do A14 são originais. Confira o aviso na cópia que *você* baixar.

Temas (títulos no site, não no nosso texto de aula):

| Onde na trilha | Tema no livro (site smlbook.org) |
| --- | --- |
| [A3](./modulo-a3/README.md) treino por dentro | “Learning parametric models” — loss, regularização, dados grandes |
| [A13](./modulo-a13/README.md) VC/SVM | “Nonlinear input transformations and kernels” — SVM; o A13 **não** substitui o capítulo |
| [A14](./modulo-a14/README.md) medição empírica | “Understanding, evaluating and improving the performance” — erro em dados novos, estimativa, hiato treino–teste, viés–variância |
| M08 (não editar) | “User aspects of machine learning” / confiança no modelo — paralelo conceitual ao eval gate; leia no tronco M08 |
| M09 (não editar) | mesmo bloco “user aspects” + harness: decisão de *não* treinar; leia no tronco M09 |

## ISLR / ISLP (PDF gratuito oficial)

James, Witten, Hastie, Tibshirani (e Taylor na ed. Python). *An Introduction to Statistical Learning*. Site: <https://www.statlearning.com/> (acesso 2026-11-18). Edição Python (ISLP, 2023): Springer <https://link.springer.com/book/10.1007/978-3-031-38747-0>. Recursos Python: <https://www.statlearning.com/resources-python>. Um PDF da 1ª ed. R (seventh printing) resolveu HTTP 200 em <https://www.statlearning.com/s/ISLRSeventhPrinting.pdf> (2026-11-18); prefira o botão atual do site. Capítulos úteis ao A14, por tema: resampling; linear model selection and regularization; classification.

## Papers abertos (já ligados aos módulos)

| Paper | Link verificado (2026-11-18) | Módulo |
| --- | --- | --- |
| Zhang et al., 2017, *Understanding deep learning requires rethinking generalization* | [arXiv 1611.03530](https://arxiv.org/abs/1611.03530) | A13, A14 |
| Belkin, Hsu, Ma & Mandal, 2019 | [arXiv 1812.11118](https://arxiv.org/abs/1812.11118) | A14 (double descent; **sem** reproduzir figura) |
| Nakkiran et al., 2019, *Deep Double Descent* | [arXiv 1912.02292](https://arxiv.org/abs/1912.02292) | A14 |
| Vapnik & Chervonenkis, 1971 | DOI [10.1137/1116025](https://doi.org/10.1137/1116025) | A13 |
| Cortes & Vapnik, 1995 | DOI [10.1007/BF00994018](https://doi.org/10.1007/BF00994018) | A13 |

## llm-course (Apache-2.0)

Leitura extra isolada: [`NOTICE.md`](./NOTICE.md). Não substitui A3/A13/A14.
