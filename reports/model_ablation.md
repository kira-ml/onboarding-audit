# Model / Score Ablation

**Status:** Post-hoc, 2026-11-27. Not a production estimate.

## Existing scores (month 6)

| Score | AUC | Average precision | KS | Fraud rate | n |
|---|---:|---:|---:|---:|---:|
| `incumbent_p_fraud` | 0.8733 | 0.1442 | 0.5981 | 1.3405% | 108,168 |
| `candidate_p_fraud_lgbm` | 0.8829 | 0.1545 | 0.6114 | 1.3405% | 108,168 |
| `random_forest_diagnostic` | 0.8508 | 0.1263 | 0.5478 | 1.3405% | 108,168 |

## Retrained ablation (train month 5, test month 6)

| Model | Features | AUC | Average precision | KS |
|---|---:|---:|---:|---:|
| `logistic_all_features` | 31 | 0.8754 | 0.1496 | 0.5983 |
| `hist_gradient_boosting_all_features` | 31 | 0.8773 | 0.1537 | 0.6010 |
| `logistic_reduced_no_velocity` | 26 | 0.8711 | 0.1441 | 0.5869 |

**Read:** if the LightGBM candidate has a higher AUC/AP than the logistic
incumbent on the same test window, the “better model” premise is
supported as a ranking claim. The retrained ablation is a same-window
temporal check, not the original benchmark score; a same-feature
gradient-boosting model should beat logistic if model class is the
driver. This does not isolate observation selection from model capacity.
