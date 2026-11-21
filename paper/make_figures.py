"""Generate the paper figures from the committed JSON artifacts.

Usage:
    python paper/make_figures.py

Writes PDF figures to paper/figures/.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "figure.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    }
)

NAIVE = "#B22222"
DR = "#1F4E79"
GREY = "#666666"


def _sweep():
    payload = json.loads(
        (ROOT / "reports" / "obs_sweep" / "pilot.json").read_text(encoding="utf-8")
    )
    cells = sorted({r["scenario"] for r in payload["summary"]})
    naive, dr, cov, pbest = [], [], [], []
    for cell in cells:
        n = [
            r
            for r in payload["summary"]
            if r["scenario"] == cell and r["estimator"] == "naive"
        ]
        d = [
            r
            for r in payload["summary"]
            if r["scenario"] == cell and r["estimator"] == "dr"
        ]
        naive.append(max(abs(r["rel_bias"]) for r in n))
        dr.append(max(abs(r["rel_bias"]) for r in d))
        cov.append(np.mean([r["coverage"] for r in d]))
        rank = [
            r
            for r in payload.get("ranking", [])
            if r["scenario"] == cell and r["estimator"] == "dr"
        ]
        pbest.append(rank[0]["p_select_true_best"] if rank else np.nan)
    return cells, np.array(naive), np.array(dr), np.array(cov), np.array(pbest)


def fig_sweep():
    cells, naive, dr, _, _ = _sweep()
    x = np.arange(len(cells))
    fig, ax = plt.subplots(figsize=(3.4, 2.05))
    ax.plot(x, naive * 100, "o-", color=NAIVE, ms=3.2, lw=1.1, label="Naive")
    ax.plot(x, dr * 100, "s-", color=DR, ms=3.0, lw=1.1, label="DR")
    ax.axhline(5.0, color=GREY, ls="--", lw=0.8)
    ax.text(
        len(cells) - 0.4, 5.8, "5%", color=GREY, ha="right", va="bottom", fontsize=6.5
    )
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", "\n") for c in cells], rotation=90, fontsize=6)
    ax.set_ylabel("Max |relative bias| (%)")
    ax.legend(frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(OUT / "sweep_bias.pdf")
    plt.close(fig)


def fig_double_robustness():
    payload = json.loads(
        (ROOT / "reports" / "double_robustness.json").read_text(encoding="utf-8")
    )
    arms = [
        ("correct_e_wrong_outcome", "Wrong outcome"),
        ("wrong_e_correct_outcome", "Wrong propensity"),
        ("wrong_e_wrong_outcome", "Both wrong"),
    ]
    estimators = [
        ("plug_in", "Plug-in", "#999999"),
        ("ipw", "IPW", NAIVE),
        ("dr", "DR", DR),
    ]
    width = 0.26
    x = np.arange(len(arms))
    fig, ax = plt.subplots(figsize=(3.4, 2.05))
    for i, (key, label, color) in enumerate(estimators):
        values = [payload["arms"][a][key]["rel_bias"] * 100 for a, _ in arms]
        ax.bar(x + (i - 1) * width, values, width, color=color, label=label)
    ax.axhline(0.0, color="black", lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, label in arms])
    ax.set_ylabel("Relative bias (%)")
    ax.legend(frameon=False, ncol=3, loc="lower left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(OUT / "double_robustness.pdf")
    plt.close(fig)


def fig_case_study():
    truth = json.loads(
        (ROOT / "examples" / "case_truth.json").read_text(encoding="utf-8")
    )
    labels = ["Incumbent", "Candidate"]
    naive = [truth["naive_incumbent"], truth["naive_candidate"]]
    true = [truth["true_incumbent"], truth["true_candidate"]]
    x = np.arange(2)
    width = 0.34
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    ax.bar(x - width / 2, naive, width, color="#999999", label="Naive (labeled rows)")
    ax.bar(x + width / 2, true, width, color=DR, label="True (P0)")
    for i, (a, b) in enumerate(zip(naive, true)):
        ax.text(i - width / 2, a + 0.01, f"{a:.3f}", ha="center", fontsize=6.5)
        ax.text(i + width / 2, b + 0.01, f"{b:.3f}", ha="center", fontsize=6.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Cost per application")
    ax.set_ylim(0, max(max(naive), max(true)) * 1.18)
    ax.legend(frameon=False, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(OUT / "case_study.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_sweep()
    fig_double_robustness()
    fig_case_study()
    print(f"wrote figures to {OUT}")
