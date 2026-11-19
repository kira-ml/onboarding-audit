"""Typed configuration for the onboarding-audit pilot."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Costs:
    fraud_loss_rate: float = 0.0019187869
    review_cost: float = 0.02
    false_reject_cost: float = 0.10
    residual_fraud_loss: float = 0.30
    amount_scaled: bool = True

    def with_false_reject(self, value: float) -> "Costs":
        return Costs(
            fraud_loss_rate=self.fraud_loss_rate,
            review_cost=self.review_cost,
            false_reject_cost=value,
            residual_fraud_loss=self.residual_fraud_loss,
            amount_scaled=self.amount_scaled,
        )


@dataclass(frozen=True)
class Observation:
    kappa_review: float = 0.90
    e_approve: float = 0.05
    audit_rate: float = 0.01
    review_delay_median: float = 3.0
    review_delay_sigma: float = 0.5
    approve_delay_median: float = 45.0
    approve_delay_sigma: float = 0.8
    cutoff_day: float = 90.0
    outcome_dependent: bool = False
    e_approve_fraud: float = 0.30

    def with_overrides(self, **kwargs: Any) -> "Observation":
        values = {
            "kappa_review": self.kappa_review,
            "e_approve": self.e_approve,
            "audit_rate": self.audit_rate,
            "review_delay_median": self.review_delay_median,
            "review_delay_sigma": self.review_delay_sigma,
            "approve_delay_median": self.approve_delay_median,
            "approve_delay_sigma": self.approve_delay_sigma,
            "cutoff_day": self.cutoff_day,
            "outcome_dependent": self.outcome_dependent,
            "e_approve_fraud": self.e_approve_fraud,
        }
        values.update(kwargs)
        return Observation(**values)


@dataclass(frozen=True)
class OutcomeModel:
    C: float = 0.5
    max_iter: int = 300
    n_splits: int = 5


@dataclass(frozen=True)
class PolicySpec:
    name: str
    score_col: str
    review_capacity: float
    decision_false_reject_cost: float | None = None


@dataclass(frozen=True)
class Scenario:
    id: str
    reps: int
    audit_rate: float
    approve_delay_median: float
    false_reject_cost: float
    outcome_dependent: bool = False
    candidate_capacity: float | None = None
    propensity_mode: str = "oracle"
    propensity_noise: float = 0.0


@dataclass(frozen=True)
class PilotConfig:
    seed: int
    data_path: Path
    label_col: str
    amount_col: str
    month_col: str
    outcome_features: tuple[str, ...]
    costs: Costs
    observation: Observation
    outcome_model: OutcomeModel
    policies: tuple[PolicySpec, ...]
    scenarios: tuple[Scenario, ...]
    data_root: Path = field(default_factory=lambda: Path("."))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_config(path: Path | str) -> PilotConfig:
    with open(path, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    _require(isinstance(raw, dict), "config root must be a mapping")

    data = raw["data"]
    cost_values = dict(raw["costs"])
    cost_values["amount_scaled"] = bool(cost_values.get("amount_scaled", True))
    for key in (
        "fraud_loss_rate",
        "review_cost",
        "false_reject_cost",
        "residual_fraud_loss",
    ):
        cost_values[key] = float(cost_values[key])
    costs = Costs(**cost_values)
    observation = Observation(
        **{
            k: float(v) if k not in ("outcome_dependent",) else bool(v)
            for k, v in raw.get("observation", {}).items()
        }
    )
    outcome = OutcomeModel(
        **{
            k: (float(v) if k == "C" else int(v))
            for k, v in raw.get("outcome_model", {}).items()
        }
    )
    policies = tuple(
        PolicySpec(
            name=str(p["name"]),
            score_col=str(p["score_col"]),
            review_capacity=float(p["review_capacity"]),
            decision_false_reject_cost=(
                float(p["decision_false_reject_cost"])
                if p.get("decision_false_reject_cost") is not None
                else None
            ),
        )
        for p in raw["policies"]
    )
    _require(len(policies) > 0, "at least one policy is required")
    _require(
        policies[0].name == "incumbent",
        "the first policy must be the logging policy, named 'incumbent'",
    )

    scenarios = tuple(
        Scenario(
            id=str(s["id"]),
            reps=int(s["reps"]),
            audit_rate=float(s["audit_rate"]),
            approve_delay_median=float(s["approve_delay_median"]),
            false_reject_cost=float(s["false_reject_cost"]),
            outcome_dependent=bool(s.get("outcome_dependent", False)),
            candidate_capacity=(
                float(s["candidate_capacity"])
                if s.get("candidate_capacity") is not None
                else None
            ),
            propensity_mode=str(s.get("propensity_mode", "oracle")),
            propensity_noise=float(s.get("propensity_noise", 0.0)),
        )
        for s in raw["scenarios"]
    )
    ids = [s.id for s in scenarios]
    _require(len(ids) == len(set(ids)), "scenario ids must be unique")

    for policy in policies:
        _require(
            0.0 < policy.review_capacity <= 1.0,
            f"review_capacity for {policy.name!r} must be in (0, 1]",
        )
    for scenario in scenarios:
        _require(scenario.reps > 0, f"scenario {scenario.id!r} needs reps > 0")
        _require(
            0.0 <= scenario.audit_rate <= 1.0,
            f"audit_rate for {scenario.id!r} must be in [0, 1]",
        )
        _require(
            scenario.approve_delay_median > 0.0,
            f"approve_delay_median for {scenario.id!r} must be positive",
        )
        _require(
            scenario.false_reject_cost >= 0.0,
            f"false_reject_cost for {scenario.id!r} must be >= 0",
        )
        _require(
            scenario.propensity_mode in {"oracle", "estimated", "noisy"},
            f"propensity_mode for {scenario.id!r} must be oracle/estimated/noisy",
        )
        _require(
            scenario.propensity_noise >= 0.0,
            f"propensity_noise for {scenario.id!r} must be >= 0",
        )

    return PilotConfig(
        seed=int(raw["seed"]),
        data_path=Path(data["path"]),
        label_col=str(data.get("label_col", "fraud_bool")),
        amount_col=str(data.get("amount_col", "amount_proxy")),
        month_col=str(data.get("month_col", "month")),
        outcome_features=tuple(data["outcome_features"]),
        costs=costs,
        observation=observation,
        outcome_model=outcome,
        policies=policies,
        scenarios=scenarios,
    )
