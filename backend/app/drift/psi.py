import numpy as np


def calculate_psi(baseline, current, bins=10):
    baseline = np.asarray(baseline, dtype=float)
    current = np.asarray(current, dtype=float)
    if baseline.size == 0 or current.size == 0:
        return 0.0, "NORMAL"

    baseline = np.nan_to_num(baseline, nan=np.nanmean(baseline))
    current = np.nan_to_num(current, nan=np.nanmean(current))
    min_val = min(np.min(baseline), np.min(current))
    max_val = max(np.max(baseline), np.max(current))
    if np.isclose(min_val, max_val):
        return 0.0, "NORMAL"

    edges = np.linspace(min_val, max_val, bins + 1)
    baseline_hist, _ = np.histogram(baseline, bins=edges)
    current_hist, _ = np.histogram(current, bins=edges)
    baseline_pct = np.clip(baseline_hist / max(np.sum(baseline_hist), 1), 1e-6, None)
    current_pct = np.clip(current_hist / max(np.sum(current_hist), 1), 1e-6, None)
    psi_value = np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct))

    if psi_value < 0.10:
        label = "NORMAL"
    elif psi_value <= 0.25:
        label = "WARNING"
    else:
        label = "SIGNIFICANT_DRIFT"

    return float(psi_value), label
