# Corrida real — A13

`utc 2026-11-14T03:22:51Z`  `segundos_total=4.817`  `sklearn=1.9.1`

```
=== A13.1 shattering 2D (3 pontos vs XOR) ===
  3pts estilhaça=True 8/8  4pts estilhaça=False XOR sep=False
=== A13.2 margem e n_sv vs C ===
  C=0.01    n_sv=68  margem=6.6013 acc=0.675
  C=0.1     n_sv=60  margem=5.4240 acc=0.650
  C=1.0     n_sv=58  margem=4.9952 acc=0.675
  C=10.0    n_sv=58  margem=4.9933 acc=0.675
  C=100.0   n_sv=58  margem=4.9933 acc=0.675
=== A13.3 SVM linear/RBF vs logreg (frases) ===
  encoder_principal=smollm2-135m-meanpool
  tfidf svm_linear: treino=1.000 eval=1.000
  tfidf svm_rbf: treino=1.000 eval=1.000
  tfidf logreg: treino=1.000 eval=1.000
  embed svm_linear: treino=1.000 eval=1.000
  embed svm_rbf: treino=0.938 eval=1.000
  embed logreg: treino=1.000 eval=1.000
=== A13.4 rótulos aleatórios (Zhang) ===
  svm_rbf treino=1.000 eval=0.500  mlp treino=1.000 eval=0.667
=== A13.5 ponte A5 → pergunta 1971 ===
  A5 acc 1.00/0.50 vacuo_lora=True vacuo_vc3=True
```

pytest A13: 11 passed (`not modelo`).
