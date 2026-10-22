from pathlib import Path
import joblib, numpy as np, pandas as pd
BASE = Path(__file__).resolve().parent
FEATURES = ["temp_C", "pH", "turbidity_NTU"]
clf = joblib.load(BASE / "model_klasifikasi_baseline.joblib")
km = joblib.load(BASE / "model_kmeans.joblib")
sc = joblib.load(BASE / "scaler_clustering.joblib")
iso = joblib.load(BASE / "model_isolation_forest.joblib")
sa = joblib.load(BASE / "scaler_isolation_forest.joblib")
def analyze_reading(reading):
    if not isinstance(reading, dict): raise TypeError("Input harus dictionary")
    missing = [c for c in FEATURES if c not in reading]
    if missing: raise ValueError(f"Fitur wajib tidak ada: {missing}")
    vals = {c: float(reading[c]) for c in FEATURES}
    if not all(np.isfinite(v) for v in vals.values()): raise ValueError("Nilai harus finite")
    one = pd.DataFrame([vals], columns=FEATURES); z = sa.transform(one)
    return {"class_label": str(clf.predict(one)[0]), "cluster_id": int(km.predict(sc.transform(one))[0]), "anomaly_detected": bool(iso.predict(z)[0] == -1), "anomaly_score": float(iso.decision_function(z)[0]), "interpretation": "Indikasi; bukan bukti pasti pencemaran"}
