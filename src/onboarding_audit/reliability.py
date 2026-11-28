"""Decision reliability for a logged policy comparison.

The point estimate is not the product. A decision is reliable only when the
evidence supports the same decision under the uncertainty the log cannot
eliminate: sampling, nuisance-model error, cost assumptions, selective labels,
and data readiness. This module reports those dimensions separately and grades
the decision; it does not hide them in a single number.
"""

from __future__ import annotations

import numpy as np

from .config import Costs
from .estimators import compare_policies, expected_cost
from .policies import realized_cost


def _clean(value):
    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    return value


def _quantile(values: np.ndarray, q: float) -> float:
    return float(np.quantile(values, q)) if len(values) else float("nan")


def bootstrap_decision(
    cost_candidate: np.ndarray,
    actions_candidate: np.ndarray,
    cost_incumbent: np.ndarray,
    actions_incumbent: np.ndarray,
    amount: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
    phat: np.ndarray,
    costs: Costs,
    *,
    n_boot: int = 500,
    seed: int = 0,
) -> dict:
    """Paired row bootstrap of the DR policy-value difference.

    Nuisance models are fixed; the bootstrap measures evaluation-sample
    uncertainty, not propensity/outcome model uncertainty. It is a decision
    stability diagnostic, not a confidence guarantee.
    """
    observed = np.asarray(observed, dtype=bool)
    in_pop = np.asarray(in_pop, dtype=bool)
    if phat is None or not np.isfinite(np.asarray(phat, dtype=float)).all():
        return {"available": False, "reason": "outcome model unavailable"}
    n_pop = int(in_pop.sum())
    if n_pop < 2:
        return {"available": False, "reason": "fewer than two P0 rows"}

    mu_c = expected_cost(phat, actions_candidate, amount, costs)
    mu_i = expected_cost(phat, actions_incumbent, amount, costs)
    w = np.zeros(len(cost_candidate), dtype=float)
    np.divide(1.0, propensity, out=w, where=observed & (propensity > 0))
    term = (mu_c + w * (cost_candidate - mu_c)) - (mu_i + w * (cost_incumbent - mu_i))
    d = term[in_pop]
    if not np.isfinite(d).all():
        return {"available": False, "reason": "non-finite influence terms"}

    point = float(d.mean())
    rng = np.random.default_rng(seed)
    n = len(d)
    boot = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot[b] = float(d[idx].mean())

    p_better = float(np.mean(boot < 0.0))
    if p_better >= 0.95:
        decision = "prefer candidate"
    elif p_better <= 0.05:
        decision = "keep incumbent"
    else:
        decision = "inconclusive"
    same_direction = (
        p_better if point < 0 else (1.0 - p_better) if point > 0 else float("nan")
    )
    return {
        "available": True,
        "method": "paired row bootstrap of DR influence terms; nuisance fixed",
        "n_boot": int(n_boot),
        "n_pop": int(n_pop),
        "seed": int(seed),
        "point_difference": point,
        "p_candidate_better_boot": p_better,
        "decision_boot": decision,
        "same_direction_share": same_direction,
        "ci_low": _quantile(boot, 0.025),
        "ci_high": _quantile(boot, 0.975),
        "p05": _quantile(boot, 0.05),
        "p95": _quantile(boot, 0.95),
        "regret_candidate": float(np.mean(np.maximum(boot, 0.0))),
        "regret_incumbent": float(np.mean(np.maximum(-boot, 0.0))),
        "regret_p95_candidate": _quantile(np.maximum(boot, 0.0), 0.95),
        "regret_p95_incumbent": _quantile(np.maximum(-boot, 0.0), 0.95),
    }


def calibration_metrics(
    y: np.ndarray,
    phat: np.ndarray | None,
    observed: np.ndarray,
    *,
    n_bins: int = 10,
) -> dict:
    """Brier, log loss, and ECE for the cross-fitted outcome model."""
    if phat is None:
        return {"available": False, "reason": "outcome model unavailable"}
    y = np.asarray(y, dtype=float)
    phat = np.asarray(phat, dtype=float)
    mask = np.asarray(observed, dtype=bool) & np.isfinite(phat)
    if mask.sum() < 10:
        return {"available": False, "reason": "fewer than 10 observed predictions"}
    p = np.clip(phat[mask], 1e-6, 1.0 - 1e-6)
    yy = y[mask].astype(float)
    brier = float(np.mean((p - yy) ** 2))
    log_loss = float(-np.mean(yy * np.log(p) + (1.0 - yy) * np.log(1.0 - p)))

    edges = np.unique(np.quantile(p, np.linspace(0.0, 1.0, n_bins + 1)))
    if len(edges) < 3:
        bins = np.zeros(len(p), dtype=int)
        used = 1
    else:
        bins = np.clip(np.digitize(p, edges[1:-1]), 0, len(edges) - 2)
        used = int(len(edges) - 1)
    ece = 0.0
    for b in range(used):
        m = bins == b
        if m.any():
            ece += (m.sum() / len(p)) * abs(float(p[m].mean() - yy[m].mean()))
    return {
        "available": True,
        "n": len(p),
        "brier": brier,
        "log_loss": log_loss,
        "ece": float(ece),
        "n_bins": used,
    }


def propensity_calibration(
    propensity: np.ndarray,
    observed: np.ndarray,
    in_pop: np.ndarray,
    *,
    n_bins: int = 10,
) -> dict:
    """Observed/expected ratio and ECE for the observation propensity."""
    e = np.asarray(propensity, dtype=float)
    observed = np.asarray(observed, dtype=bool)
    in_pop = np.asarray(in_pop, dtype=bool)
    mask = in_pop & np.isfinite(e)
    if mask.sum() < 10:
        return {"available": False, "reason": "fewer than 10 P0 propensities"}
    p = np.clip(e[mask], 1e-9, 1.0)
    obs = observed[mask].astype(float)
    ratio = float(obs.sum() / p.sum()) if p.sum() > 0 else float("nan")

    edges = np.unique(np.quantile(p, np.linspace(0.0, 1.0, n_bins + 1)))
    if len(edges) < 3:
        bins = np.zeros(len(p), dtype=int)
        used = 1
    else:
        bins = np.clip(np.digitize(p, edges[1:-1]), 0, len(edges) - 2)
        used = int(len(edges) - 1)
    ece = 0.0
    for b in range(used):
        m = bins == b
        if m.any():
            ece += (m.sum() / len(p)) * abs(float(p[m].mean() - obs[m].mean()))
    return {
        "available": True,
        "n": len(p),
        "observed_expected_ratio": ratio,
        "ece": float(ece),
        "mean_predicted": float(p.mean()),
        "observed_rate": float(obs.mean()),
        "n_bins": used,
    }


def cost_stress(
    y: np.ndarray,
    actions: np.ndarray,
    candidate_actions: np.ndarray,
    amount: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
    phat: np.ndarray,
    costs: Costs,
    base_decision: str,
    *,
    false_reject_multipliers: tuple[float, ...] = (0.5, 1.0, 2.0),
    review_multipliers: tuple[float, ...] = (0.5, 1.0, 2.0),
) -> dict:
    """Re-run the paired comparison over a cost grid."""
    if phat is None or not np.isfinite(np.asarray(phat, dtype=float)).all():
        return {"available": False, "reason": "outcome model unavailable"}
    cells = []
    for fr in false_reject_multipliers:
        for rev in review_multipliers:
            stress = Costs(
                fraud_loss_rate=costs.fraud_loss_rate,
                review_cost=costs.review_cost * rev,
                false_reject_cost=costs.false_reject_cost * fr,
                residual_fraud_loss=costs.residual_fraud_loss,
                amount_scaled=costs.amount_scaled,
            )
            cost_c = realized_cost(candidate_actions, y, amount, stress)
            cost_i = realized_cost(actions, y, amount, stress)
            comp = compare_policies(
                cost_c,
                candidate_actions,
                cost_i,
                actions,
                amount,
                observed,
                propensity,
                in_pop,
                phat,
                stress,
            )
            cells.append(
                {
                    "false_reject_multiplier": float(fr),
                    "review_multiplier": float(rev),
                    "decision": comp.get("decision", "not identified"),
                    "difference": comp.get("difference", float("nan")),
                    "p_candidate_better": comp.get("p_candidate_better", float("nan")),
                }
            )
    same = sum(c["decision"] == base_decision for c in cells)
    share = float(same / len(cells)) if cells else float("nan")
    return {
        "available": True,
        "base_decision": base_decision,
        "n_cells": len(cells),
        "same_decision_share": share,
        "stable_at_80pct": bool(share >= 0.8),
        "cells": cells,
    }


def _dimension(status: str, evidence: str) -> dict:
    return {"status": status, "evidence": evidence}


def build_reliability_profile(
    *,
    identification,
    comparison: dict,
    bootstrap: dict,
    calibration: dict,
    prop_calibration: dict,
    stress: dict,
) -> dict:
    """Combine the dimensions into an explicit decision grade.

    Grade A: P0 decision stable under bootstrap, calibration, and cost stress;
    full-policy direction also survives. Grade B: P0 decision credible but one
    dimension is a caveat (usually the full-policy reject margin). Grade C:
    collect more evidence. Grade D: not identified.
    """
    dimensions: dict[str, dict] = {}
    reasons: list[str] = []

    if identification.passed:
        dimensions["identification"] = _dimension(
            "strong", "P0 identification gate passed"
        )
    else:
        dimensions["identification"] = _dimension(
            "fail", "; ".join(identification.reasons[:2]) or "gate failed"
        )

    if not bootstrap.get("available"):
        dimensions["statistical_stability"] = _dimension(
            "unavailable", str(bootstrap.get("reason", "bootstrap unavailable"))
        )
    else:
        p = float(bootstrap["p_candidate_better_boot"])
        same = bootstrap.get("same_direction_share")
        if (p >= 0.95 or p <= 0.05) and same is not None and same >= 0.9:
            status = "strong"
        elif p >= 0.8 or p <= 0.2:
            status = "moderate"
        else:
            status = "weak"
        dimensions["statistical_stability"] = _dimension(
            status,
            f"bootstrap P(candidate cheaper)={p:.3f}; same-direction share="
            f"{same if same is not None else float('nan'):.3f}",
        )

    full = (comparison.get("full_policy") or {}).get("decision", "not identified")
    n_rejected = int(identification.metrics.get("n_rejected", 0) or 0)
    full_text = str(full)
    point_decision = comparison.get("decision")
    full_direction = (
        "prefer candidate"
        if full_text.startswith("candidate cheaper")
        else "keep incumbent"
        if full_text.startswith("incumbent cheaper")
        else None
    )
    if full_direction and point_decision in {"prefer candidate", "keep incumbent"}:
        if full_direction != point_decision:
            structural = "unavailable"
            structural_evidence = "full-policy direction conflicts with the P0 decision"
        else:
            structural = "strong"
            structural_evidence = full_text
    elif full_text == "depends on the reject margin":
        structural = "caveat"
        structural_evidence = "full-policy direction depends on the reject margin"
    elif full_text == "P0 inconclusive" and n_rejected == 0:
        structural = "not_applicable"
        structural_evidence = "no logging-rejected rows; P0 is the full population"
    elif full_text == "P0 inconclusive":
        structural = "unavailable"
        structural_evidence = "P0 interval includes zero"
    else:
        structural = "unavailable"
        structural_evidence = full_text
    dimensions["structural_reject_margin"] = _dimension(structural, structural_evidence)

    model_statuses = []
    if calibration.get("available"):
        ece = float(calibration["ece"])
        model_statuses.append(
            "strong" if ece <= 0.05 else "moderate" if ece <= 0.10 else "weak"
        )
        model_evidence = f"outcome ECE={ece:.3f}, Brier={calibration['brier']:.3f}"
    else:
        model_statuses.append("unavailable")
        model_evidence = str(
            calibration.get("reason", "outcome calibration unavailable")
        )
    if prop_calibration.get("available"):
        ratio = float(prop_calibration["observed_expected_ratio"])
        if 0.75 <= ratio <= 1.25:
            prop_status = "strong"
        elif 0.5 <= ratio <= 1.5:
            prop_status = "moderate"
        else:
            prop_status = "weak"
        model_statuses.append(prop_status)
        model_evidence += f"; propensity O/E={ratio:.2f}"
    else:
        model_statuses.append("unavailable")
    if "weak" in model_statuses:
        model_status = "weak"
    elif "moderate" in model_statuses:
        model_status = "moderate"
    elif all(status == "unavailable" for status in model_statuses):
        model_status = "unavailable"
    elif "unavailable" in model_statuses:
        model_status = "moderate"
    else:
        model_status = "strong"
    dimensions["model_calibration"] = _dimension(model_status, model_evidence)

    if stress.get("available"):
        share = float(stress["same_decision_share"])
        status = "strong" if share >= 0.8 else "moderate" if share >= 0.6 else "weak"
        dimensions["cost_stress"] = _dimension(
            status,
            f"{round(share * stress['n_cells'])}/{stress['n_cells']} cost cells same decision",
        )
    else:
        dimensions["cost_stress"] = _dimension(
            "unavailable", str(stress.get("reason", "cost stress unavailable"))
        )

    metrics = identification.metrics
    observed_n = int(metrics.get("n_observed", 0))
    ess = float(metrics.get("ess", 0.0))
    warnings = len(identification.warnings)
    if observed_n >= 500 and ess >= 500 and warnings <= 1:
        op_status = "strong"
    elif observed_n >= 100 and ess >= 100 and warnings <= 3:
        op_status = "moderate"
    else:
        op_status = "weak"
    dimensions["operational_readiness"] = _dimension(
        op_status,
        f"labels={observed_n:,}; ESS={ess:.0f}; gate warnings={warnings}",
    )

    if not identification.passed:
        grade = "D — not identified"
        reasons.append("identification gate failed")
    elif comparison.get("decision") not in {"prefer candidate", "keep incumbent"}:
        grade = "C — collect more evidence"
        reasons.append("point decision is inconclusive")
    else:
        blocked = [
            k
            for k, d in dimensions.items()
            if d["status"] in {"weak", "unavailable", "fail"}
        ]
        if blocked:
            grade = "C — collect more evidence"
            reasons.extend(f"{k}: {dimensions[k]['status']}" for k in blocked)
        elif dimensions["structural_reject_margin"]["status"] == "caveat" or any(
            d["status"] == "moderate" for d in dimensions.values()
        ):
            grade = "B — decision-grade with caveats"
            if dimensions["structural_reject_margin"]["status"] == "caveat":
                reasons.append("full-policy direction depends on the reject margin")
            reasons.extend(
                f"{k}: moderate"
                for k, d in dimensions.items()
                if d["status"] == "moderate"
            )
        else:
            grade = "A — decision-grade (conditional on assumptions)"
            reasons.append("all reliability dimensions strong")

    return {
        "grade": grade,
        "dimensions": dimensions,
        "reasons": reasons,
        "note": (
            "A decision aid, not a certification. The observation model, cost "
            "matrix, and audit design remain assumptions."
        ),
    }


def build_reliability(
    *,
    y: np.ndarray,
    cost: np.ndarray,
    actions: np.ndarray,
    candidate_actions: np.ndarray,
    amount: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
    phat: np.ndarray | None,
    costs: Costs,
    comparison: dict,
    identification,
    seed: int = 0,
    n_boot: int = 500,
) -> dict:
    """Build the full decision-reliability payload for the report."""
    if not identification.passed or not np.isfinite(
        comparison.get("difference", np.nan)
    ):
        profile = build_reliability_profile(
            identification=identification,
            comparison=comparison,
            bootstrap={"available": False, "reason": "decision not identified"},
            calibration={"available": False, "reason": "decision not identified"},
            prop_calibration={"available": False, "reason": "decision not identified"},
            stress={"available": False, "reason": "decision not identified"},
        )
        return {
            "bootstrap": {"available": False, "reason": "decision not identified"},
            "calibration": {"available": False, "reason": "decision not identified"},
            "propensity_calibration": {
                "available": False,
                "reason": "decision not identified",
            },
            "cost_stress": {"available": False, "reason": "decision not identified"},
            "profile": profile,
        }

    bootstrap = bootstrap_decision(
        cost,
        candidate_actions,
        realized_cost(actions, y, amount, costs),
        actions,
        amount,
        observed,
        propensity,
        in_pop,
        phat,
        costs,
        n_boot=n_boot,
        seed=seed,
    )
    calibration = calibration_metrics(y, phat, observed)
    prop_cal = propensity_calibration(propensity, observed, in_pop)
    stress = cost_stress(
        y,
        actions,
        candidate_actions,
        amount,
        observed,
        propensity,
        in_pop,
        phat,
        costs,
        comparison.get("decision", "not identified"),
    )
    profile = build_reliability_profile(
        identification=identification,
        comparison=comparison,
        bootstrap=bootstrap,
        calibration=calibration,
        prop_calibration=prop_cal,
        stress=stress,
    )
    return _clean(
        {
            "bootstrap": bootstrap,
            "calibration": calibration,
            "propensity_calibration": prop_cal,
            "cost_stress": stress,
            "profile": profile,
        }
    )
