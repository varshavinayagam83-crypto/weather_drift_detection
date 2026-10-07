from scipy.stats import ks_2samp


def ks_test(baseline, current, alpha=0.05):
    statistic, p_value = ks_2samp(baseline, current)
    drift_detected = p_value < alpha
    return {
        "ks_statistic": float(statistic),
        "ks_p_value": float(p_value),
        "drift_detected": drift_detected,
    }
