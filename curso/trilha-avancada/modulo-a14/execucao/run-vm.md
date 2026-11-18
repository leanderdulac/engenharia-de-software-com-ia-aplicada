# Corrida real — A14

`utc 2026-11-18T14:26:05Z`  `segundos_total=0.124`  `sklearn=1.9.1`  `torch=ausente`

```
=== A14.1 IC Wilson/bootstrap nos números publicados A5/A7/A13 ===
  A5 eval: 1/2=0.500  Wilson[0.095,0.905] largura=0.811 vacuo_pratico=True
  A5 se n=6 (não medido): 3/6=0.500  Wilson[0.188,0.812] largura=0.625 vacuo_pratico=True
  A13 Zhang SVM RBF eval: 3/6=0.500  Wilson[0.188,0.812] largura=0.625 vacuo_pratico=True
  A7 acc_direto: 3/8=0.375  Wilson[0.137,0.694] largura=0.557 vacuo_pratico=True
=== A14.2 vazamento: escala antes do split ===
  antes=0.778 depois=0.704 delta=0.074 otimista=True
=== A14.3 vazamento: duplicatas de treino no teste ===
  limpo=0.600 sujo=0.791 delta=0.191
=== A14.4 k-fold ===
  accs=['0.812', '0.875', '0.688', '0.625', '0.938'] media=0.787 sd=0.130
=== A14.5 polinômio / k-NN / ridge ===
  poly grau→mse_eval [(1, 0.39), (2, 0.398), (4, 0.187), (8, 0.203), (12, 0.582), (16, 1.247)]
  knn k→acc_eval [(1, 0.738), (3, 0.714), (9, 0.667), (21, 0.595)]
=== A14.6 features aleatórias (pico de interpolação) ===
  pico_p=40 mse=4.984 desceu=True
```
