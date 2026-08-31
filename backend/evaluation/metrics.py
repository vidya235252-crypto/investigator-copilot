import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, average_precision_score

def binary_metrics(y_true, y_pred):
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "false_positive_rate": round(float(fpr), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }

def pr_auc(y_true, y_scores):
    return round(float(average_precision_score(y_true, y_scores)), 4)

def per_scenario_recall(y_true, y_pred, scenario_labels):
    scenarios = sorted(set(scenario_labels))
    results = {}
    for scenario in scenarios:
        mask = [s == scenario for s in scenario_labels]
        y_t = np.array(y_true)[mask]
        y_p = np.array(y_pred)[mask]
        if len(y_t) == 0:
            continue
        n = len(y_t)
        n_positive = int(y_t.sum())
        if n_positive == 0:
            results[scenario] = {"n": n, "n_positive": 0, "recall": None}
            continue
        recall = recall_score(y_t, y_p, zero_division=0)
        results[scenario] = {"n": n, "n_positive": n_positive, "recall": round(float(recall), 4)}
    return results