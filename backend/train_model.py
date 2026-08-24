import pandas as pd
from detection import ml_risk_model

events = pd.read_csv("../data/raw/events.csv", parse_dates=["timestamp"])
labels = pd.read_csv("../data/raw/labels.csv")

model = ml_risk_model.train(events, labels)
ml_risk_model.save_model(model, "detection/risk_model.joblib")

X_val, y_val = ml_risk_model.build_dataset(events, labels, "val")
val_proba = model.predict_proba(X_val)[:, 1]

for threshold in [0.3, 0.4, 0.5, 0.6, 0.7]:
    preds = (val_proba >= threshold).astype(int)
    tp = ((preds == 1) & (y_val == 1)).sum()
    fp = ((preds == 1) & (y_val == 0)).sum()
    fn = ((preds == 0) & (y_val == 1)).sum()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    print(f"threshold={threshold} precision={precision:.3f} recall={recall:.3f}")

importances = sorted(zip(ml_risk_model.FEATURE_ORDER, model.feature_importances_), key=lambda x: -x[1])
print("\nfeature importances:")
for name, imp in importances:
    print(f"  {name}: {imp:.4f}")