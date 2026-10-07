import numpy as np
from sklearn.ensemble import IsolationForest


def detect_anomalies(values):
    values = np.asarray(values, dtype=float)
    if values.size < 5:
        return {"anomaly_count": 0, "anomaly_percentage": 0.0, "anomaly_dates": [], "anomaly_values": []}

    model = IsolationForest(contamination=0.1, random_state=42)
    predictions = model.fit_predict(values.reshape(-1, 1))
    is_anomaly = predictions == -1
    anomaly_indices = np.where(is_anomaly)[0]
    return {
        "anomaly_count": int(anomaly_indices.size),
        "anomaly_percentage": float((anomaly_indices.size / len(values)) * 100),
        "anomaly_dates": anomaly_indices.tolist(),
        "anomaly_values": values[anomaly_indices].tolist(),
    }
