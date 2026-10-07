import numpy as np

from app.drift.drift_score import get_combined_score
from app.drift.psi import calculate_psi
from app.drift.statistical_tests import ks_test


def test_ks_calculation():
    baseline = np.array([10, 12, 11, 13, 12])
    current = np.array([20, 18, 22, 21, 19])
    result = ks_test(baseline, current)
    assert 'ks_statistic' in result
    assert 'ks_p_value' in result


def test_psi_calculation():
    baseline = np.array([10, 12, 11, 13, 12])
    current = np.array([20, 18, 22, 21, 19])
    value, label = calculate_psi(baseline, current)
    assert isinstance(value, float)
    assert label in {'NORMAL', 'WARNING', 'SIGNIFICANT_DRIFT'}


def test_combined_score():
    score, label = get_combined_score(True, 'SIGNIFICANT_DRIFT', 2)
    assert score >= 2
    assert label in {'MODERATE_DRIFT', 'HIGH_DRIFT'}
