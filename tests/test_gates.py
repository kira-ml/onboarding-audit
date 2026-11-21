import numpy as np

from onboarding_audit.gates import check_identification


def _valid_inputs(n=1000, n_reject=50):
    actions = np.array(
        ["approve"] * (n - n_reject - 150) + ["review"] * 150 + ["reject"] * n_reject
    )
    candidate = actions.copy()
    observed = np.zeros(n, dtype=bool)
    observed[:200] = True  # 200 approve labels
    observed[-150 - n_reject : -n_reject] = True  # 150 review labels
    e = np.full(n, 0.2)
    e[actions == "review"] = 0.9
    e[actions == "reject"] = 0.0
    cost = np.zeros(n)
    return actions, candidate, observed, e, cost


def _check(**overrides):
    actions, candidate, observed, e, cost = _valid_inputs()
    values = dict(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=True,
        propensity_source="provided",
        has_audit=True,
    )
    values.update(overrides)
    return check_identification(**values)


def test_valid_log_passes():
    report = _check()
    assert report.passed
    assert not report.reasons
    assert report.metrics["n_observed"] == 350


def test_positivity_failure_refuses():
    actions, candidate, observed, e, cost = _valid_inputs()
    e = e.copy()
    e[actions == "approve"] = 0.0
    report = check_identification(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=False,
        propensity_source="provided",
        has_audit=True,
    )
    assert not report.passed
    assert any("positivity" in reason for reason in report.reasons)


def test_negative_cost_refuses():
    actions, candidate, observed, e, cost = _valid_inputs()
    cost = cost.copy()
    cost[0] = -1.0
    report = check_identification(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=True,
        propensity_source="provided",
        has_audit=True,
    )
    assert not report.passed
    assert any("negative" in reason for reason in report.reasons)


def test_small_sample_refuses():
    actions, candidate, observed, e, cost = _valid_inputs()
    observed = observed.copy()
    observed[:] = False
    observed[:50] = True
    report = check_identification(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=True,
        propensity_source="provided",
        has_audit=True,
    )
    assert not report.passed
    assert any("sample too small" in reason for reason in report.reasons)


def test_low_ess_refuses():
    report = _check(min_ess=1e9)
    assert not report.passed
    assert any("effective sample size" in reason for reason in report.reasons)


def test_candidate_outside_p0_warns():
    actions, candidate, observed, e, cost = _valid_inputs(n=1000, n_reject=200)
    candidate = candidate.copy()
    rejected = actions == "reject"
    candidate[rejected] = "approve"
    report = check_identification(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=True,
        propensity_source="provided",
        has_audit=True,
    )
    assert report.passed
    assert any("outside P0" in warning for warning in report.warnings)


def test_estimated_without_audit_warns():
    report = _check(propensity_source="estimated", has_audit=False)
    assert report.passed
    assert any("without an audit" in warning for warning in report.warnings)


def test_declared_outcome_dependent_refuses():
    report = _check(observation_assumption="outcome")
    assert not report.passed
    assert any("outcome-dependent" in reason for reason in report.reasons)


def test_undeclared_observation_mechanism_warns():
    report = _check()
    assert report.passed
    assert report.observation_assumption == "unknown"
    assert any("not declared" in warning for warning in report.warnings)


def test_declared_action_dependent_passes_without_the_warning():
    report = _check(observation_assumption="action")
    assert report.passed
    assert not any("not declared" in warning for warning in report.warnings)

def test_propensity_above_one_refuses():
    actions, candidate, observed, e, cost = _valid_inputs()
    e = e.copy()
    e[actions == "approve"] = 1.5
    report = check_identification(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=True,
        propensity_source="provided",
        has_audit=True,
    )
    assert not report.passed
    assert any("exceeds 1" in reason for reason in report.reasons)


def test_non_finite_cost_refuses():
    actions, candidate, observed, e, cost = _valid_inputs()
    cost = cost.copy()
    cost[0] = np.nan
    report = check_identification(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=True,
        propensity_source="provided",
        has_audit=True,
    )
    assert not report.passed
    assert any("not finite" in reason for reason in report.reasons)


def test_unknown_action_refuses():
    actions, candidate, observed, e, cost = _valid_inputs()
    actions = actions.copy()
    actions[0] = "Rejected"
    report = check_identification(
        actions=actions,
        candidate_actions=candidate,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=True,
        propensity_source="provided",
        has_audit=True,
    )
    assert not report.passed
    assert any("unknown action" in reason for reason in report.reasons)


def test_impossible_calibration_refuses():
    report = _check(calibration_ratio=2.0)
    assert not report.passed
    assert any("calibration failure" in reason for reason in report.reasons)


def test_low_calibration_warns_and_flags():
    report = _check(calibration_ratio=0.2)
    assert report.passed
    assert report.metrics["calibration_flagged"] == 1.0
    assert any("calibration" in warning for warning in report.warnings)
