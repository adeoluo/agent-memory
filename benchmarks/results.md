Seeds [7, 8, 9], 12 users x 20 sessions, questions per seed [162, 152, 152]

Tuned weights (selected on seeds [101, 102]): lexical=0.15, semantic=0.0, recency=0.0, importance=0.15

Memory conditions (mean ± standard deviation across seeds):
| Condition | accuracy | accuracy_current | accuracy_previous | accuracy_paraphrased | recall@1 | recall@5 |
|---|---|---|---|---|---|---|
| no memory | 0.172 ± 0.012 | 0.184 ± 0.006 | 0.150 ± 0.038 | 0.179 ± 0.055 | n/a | n/a |
| full-context truncation (400 words) | 0.114 ± 0.010 | 0.181 ± 0.016 | 0.005 ± 0.009 | 0.130 ± 0.019 | n/a | n/a |
| full-context truncation (1600 words) | 0.573 ± 0.013 | 0.670 ± 0.016 | 0.416 ± 0.045 | 0.616 ± 0.069 | n/a | n/a |
| lexical only (BM25) | 0.974 ± 0.030 | 0.969 ± 0.038 | 0.983 ± 0.018 | 0.916 ± 0.093 | 0.589 ± 0.055 | 0.974 ± 0.030 |
| full hybrid | 0.957 ± 0.014 | 0.976 ± 0.016 | 0.929 ± 0.035 | 0.855 ± 0.052 | 0.584 ± 0.042 | 0.957 ± 0.014 |
| full hybrid, episodes only (no fact extraction) | 0.597 ± 0.030 | 0.656 ± 0.038 | 0.502 ± 0.028 | 0.392 ± 0.023 | 0.294 ± 0.009 | 0.659 ± 0.022 |
| hybrid, weights tuned on development seeds | 0.981 ± 0.018 | 0.979 ± 0.018 | 0.983 ± 0.018 | 0.936 ± 0.052 | 0.526 ± 0.034 | 0.981 ± 0.018 |

Scoring-term ablation on the full store:
| Condition | accuracy | accuracy_current | accuracy_previous | accuracy_paraphrased | recall@1 | recall@5 |
|---|---|---|---|---|---|---|
| full hybrid | 0.957 ± 0.014 | 0.976 ± 0.016 | 0.929 ± 0.035 | 0.855 ± 0.052 | 0.584 ± 0.042 | 0.957 ± 0.014 |
| without lexical | 0.860 ± 0.023 | 0.910 ± 0.049 | 0.781 ± 0.019 | 0.660 ± 0.069 | 0.374 ± 0.047 | 0.873 ± 0.033 |
| without semantic | 0.972 ± 0.019 | 0.979 ± 0.010 | 0.963 ± 0.038 | 0.904 ± 0.071 | 0.567 ± 0.035 | 0.972 ± 0.019 |
| without recency | 0.961 ± 0.007 | 0.976 ± 0.016 | 0.938 ± 0.009 | 0.870 ± 0.019 | 0.664 ± 0.047 | 0.964 ± 0.010 |
| without importance | 0.957 ± 0.021 | 0.979 ± 0.018 | 0.923 ± 0.027 | 0.853 ± 0.084 | 0.578 ± 0.041 | 0.960 ± 0.021 |
| semantic only (embedding) | 0.876 ± 0.011 | 0.913 ± 0.043 | 0.816 ± 0.051 | 0.690 ± 0.054 | 0.589 ± 0.023 | 0.897 ± 0.017 |

Scoring-term ablation on an episodes-only store:
| Condition | accuracy | accuracy_current | accuracy_previous | accuracy_paraphrased | recall@1 | recall@5 |
|---|---|---|---|---|---|---|
| full hybrid | 0.597 ± 0.030 | 0.656 ± 0.038 | 0.502 ± 0.028 | 0.392 ± 0.023 | 0.294 ± 0.009 | 0.659 ± 0.022 |
| without lexical | 0.344 ± 0.045 | 0.455 ± 0.026 | 0.165 ± 0.075 | 0.268 ± 0.032 | 0.160 ± 0.027 | 0.413 ± 0.029 |
| without semantic | 0.573 ± 0.012 | 0.632 ± 0.032 | 0.476 ± 0.057 | 0.385 ± 0.035 | 0.239 ± 0.028 | 0.631 ± 0.012 |
| without recency | 0.635 ± 0.011 | 0.670 ± 0.042 | 0.578 ± 0.055 | 0.420 ± 0.008 | 0.327 ± 0.030 | 0.713 ± 0.027 |
| without importance | 0.576 ± 0.022 | 0.642 ± 0.039 | 0.467 ± 0.029 | 0.355 ± 0.013 | 0.290 ± 0.016 | 0.640 ± 0.015 |

Scaling (3 users, consolidation every 10 sessions when enabled):
| Sessions | Consolidation | Turns | Memories stored | Database KB | Ingest ms/turn | Recall p50 ms | Recall p95 ms | Accuracy |
|---|---|---|---|---|---|---|---|---|
| 10 | no | 392 | 432 | 728 | 0.08 | 0.59 | 0.83 | 0.971 |
| 10 | yes | 392 | 453 | 776 | 0.08 | 0.60 | 0.80 | 0.971 |
| 25 | no | 866 | 909 | 1460 | 0.08 | 0.90 | 1.35 | 0.944 |
| 25 | yes | 866 | 898 | 1496 | 0.08 | 0.99 | 1.37 | 0.944 |
| 50 | no | 1714 | 1760 | 2772 | 0.08 | 1.10 | 1.84 | 0.950 |
| 50 | yes | 1714 | 1094 | 1852 | 0.08 | 1.15 | 1.71 | 0.950 |
| 100 | no | 3272 | 3313 | 5168 | 0.08 | 1.46 | 3.37 | 0.944 |
| 100 | yes | 3272 | 1157 | 2036 | 0.15 | 1.52 | 3.09 | 0.917 |
| 200 | no | 6556 | 6601 | 10212 | 0.38 | 2.85 | 11.50 | 0.949 |
| 200 | yes | 6556 | 1428 | 2644 | 0.10 | 1.78 | 3.14 | 0.949 |
