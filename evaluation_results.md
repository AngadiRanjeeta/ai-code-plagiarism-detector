# Evaluation Results

Dataset: `data/pairs_100.csv`

## Summary (Best / Hybrid)

| Metric | Value |
|---|---:|
| Accuracy | **86%** |
| Precision | **83%** |
| Recall | **90%** |
| F1 Score | **0.865** |
| ROC-AUC | **0.946** |
| PR-AUC | **0.950** |
| Best Threshold (F1) | **0.290** |

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Semantic-only (SBERT cosine) | 0.86 | 0.83 | 0.90 | 0.865 | 0.946 |
| Structural-only (AST Jaccard) | 0.50 | 0.50 | 1.00 | 0.667 | 0.500 |
| Hybrid (0.7 semantic + 0.3 structural) | 0.86 | 0.83 | 0.90 | 0.865 | 0.946 |

> Confusion matrix format: `[[TN, FP], [FN, TP]]`
