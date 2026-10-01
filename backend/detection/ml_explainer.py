"""
Per-prediction explanation for the RandomForest risk model.

For a single account, decompose the model's score into
    baseline + sum(per-feature contributions) = ml_risk_score
so it can be shown the same way as the rule engine's evidence:
signal, value, and how many points it moved the score (signed).

Method: decision-path attribution (Saabas / "treeinterpreter"). For each tree we
walk the path the account takes and credit the change in P(ATO) at every split to
the feature that was split on; then average over trees. It is exactly additive
and needs no extra dependency. `shap.TreeExplainer` is the more rigorous
alternative (see explain_shap) and can be swapped in without changing the output shape.
"""
import numpy as np
from detection.ml_risk_model import FEATURE_ORDER, SENTINEL, build_feature_vector

MIN_POINTS = 0.5  # hide contributions that round to noise


def _p_positive(tree, node):
    counts = tree.value[node][0]
    return counts[1] / counts.sum()


def _tree_contributions(tree, x):
    """Return (root_probability, per-feature contribution array) for one tree."""
    contrib = np.zeros(len(FEATURE_ORDER))
    node = 0
    while tree.children_left[node] != -1:
        feat = tree.feature[node]
        # sklearn evaluates splits in float32; match it or borderline values flip
        nxt = (tree.children_left[node]
               if np.float32(x[feat]) <= np.float32(tree.threshold[node])
               else tree.children_right[node])
        contrib[feat] += _p_positive(tree, nxt) - _p_positive(tree, node)
        node = nxt
    return _p_positive(tree, 0), contrib


def explain(model, signals: dict, top_k: int = 6) -> dict:
    x = build_feature_vector(signals)
    total = np.zeros(len(FEATURE_ORDER))
    base = 0.0
    for est in model.estimators_:
        root_p, c = _tree_contributions(est.tree_, x)
        base += root_p
        total += c
    n = len(model.estimators_)
    base, total = base / n, total / n

    items = []
    for i, name in enumerate(FEATURE_ORDER):
        points = round(float(total[i]) * 100, 1)
        if abs(points) < MIN_POINTS:
            continue
        observed = x[i] != SENTINEL
        items.append({
            "signal": name,
            "weight": points,                       # signed, in score points
            "value": x[i] if observed else None,    # None = event never occurred
        })
    items.sort(key=lambda it: abs(it["weight"]), reverse=True)

    shown = items[:top_k]
    other = round(float(total.sum()) * 100 - sum(it["weight"] for it in shown), 1)
    return {
        "base_score": round(float(base) * 100, 1),
        "score": round(float(base + total.sum()) * 100, 2),
        "drivers": shown,
        "other": other,   # net of everything not shown, so the rows still sum to the score
    }


def explain_shap(model, signals: dict, top_k: int = 6) -> dict:
    """Same output shape via SHAP (pip install shap). Slower, but consistent attributions."""
    import shap
    x = np.array([build_feature_vector(signals)])
    ex = shap.TreeExplainer(model)
    sv = ex.shap_values(x)
    sv = sv[0, :, 1] if getattr(sv, "ndim", 0) == 3 else sv[1][0]
    base = float(np.atleast_1d(ex.expected_value)[-1])
    items = [{"signal": n, "weight": round(float(v) * 100, 1),
              "value": None if x[0][i] == SENTINEL else x[0][i]}
             for i, (n, v) in enumerate(zip(FEATURE_ORDER, sv)) if abs(v) * 100 >= MIN_POINTS]
    items.sort(key=lambda it: abs(it["weight"]), reverse=True)
    shown = items[:top_k]
    return {"base_score": round(base * 100, 1), "score": round((base + sv.sum()) * 100, 2),
            "drivers": shown, "other": round(float(sv.sum()) * 100 - sum(i["weight"] for i in shown), 1)}
