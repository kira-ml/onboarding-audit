import numpy as np
import pandas as pd

from onboarding_audit.metrics import pairwise_inversions


def test_pairwise_inversions_known_example():
    est = np.array([1.0, 2.0, 3.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 0
    est = np.array([3.0, 2.0, 1.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 3
    est = np.array([1.0, 3.0, 2.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 1


def test_pairwise_inversions_ties_are_not_inversions():
    est = np.array([1.0, 1.0, 2.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 0
