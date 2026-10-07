import pandas as pd

from app.drift.anomaly_detection import detect_anomalies
from app.drift.drift_score import get_combined_score
from app.drift.preprocessing import clean_weather_frame, prepare_variable_series
from app.drift.psi import calculate_psi
from app.drift.statistical_tests import ks_test


def run_drift_analysis(df: pd.DataFrame, variable: str, baseline_start, baseline_end, current_start, current_end):
    cleaned = clean_weather_frame(df)
    baseline_mask = (cleaned["observation_date"] >= baseline_start) & (cleaned["observation_date"] <= baseline_end)
    current_mask = (cleaned["observation_date"] >= current_start) & (cleaned["observation_date"] <= current_end)

    baseline_values = prepare_variable_series(cleaned[baseline_mask], variable)
    current_values = prepare_variable_series(cleaned[current_mask], variable)

    if baseline_values.empty or current_values.empty:
        return {
            "variable": variable,
            "baseline_mean": None,
            "current_mean": None,
            "ks_statistic": None,
            "ks_p_value": None,
            "psi_value": None,
            "anomaly_count": 0,
            "anomaly_percentage": 0.0,
            "drift_score": 0,
            "drift_status": "NORMAL",
            "message": "Insufficient data for drift analysis.",
        }

    ks = ks_test(baseline_values.to_numpy(), current_values.to_numpy())
    psi_value, psi_label = calculate_psi(baseline_values.to_numpy(), current_values.to_numpy())
    anomaly = detect_anomalies(current_values.to_numpy())
    score, status = get_combined_score(ks["drift_detected"], psi_label, anomaly["anomaly_count"])

    result = {
        "variable": variable,
        "baseline_mean": float(baseline_values.mean()),
        "current_mean": float(current_values.mean()),
        "baseline_std": float(baseline_values.std(ddof=1)) if len(baseline_values) > 1 else 0.0,
        "current_std": float(current_values.std(ddof=1)) if len(current_values) > 1 else 0.0,
        "ks_statistic": ks["ks_statistic"],
        "ks_p_value": ks["ks_p_value"],
        "psi_value": psi_value,
        "anomaly_count": anomaly["anomaly_count"],
        "anomaly_percentage": anomaly["anomaly_percentage"],
        "drift_score": score,
        "drift_status": status,
        "message": "Detected drift may indicate changes in observation behavior, data quality issues, unusual weather conditions, or other distributional changes and requires further investigation.",
    }
    return result
