def get_combined_score(ks_drift: bool, psi_label: str, anomaly_count: int):
    score = 0
    if ks_drift:
        score += 1
    if psi_label == "SIGNIFICANT_DRIFT":
        score += 1
    if anomaly_count > 0:
        score += 1

    if score == 0:
        status = "NORMAL"
    elif score == 1:
        status = "WARNING"
    elif score == 2:
        status = "MODERATE_DRIFT"
    else:
        status = "HIGH_DRIFT"

    return score, status
