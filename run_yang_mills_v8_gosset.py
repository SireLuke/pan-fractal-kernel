"""Reproducible SU(2) -> SU(3) -> V8 -> Gosset finite-lattice campaign.

Defaults are deliberately modest and exploratory. Statistical errors are
naive standard errors; no autocorrelation or continuum extrapolation is done.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from lattice_gauge.lattice_gauge import Gauge
from yang_mills_v8_gosset import (
    gosset_observable_field, gosset_star_report, measure,
    run_gauge_transform_control, v8_projection,
)


def run_group(n: int, beta: float, *, dims=(4, 4, 4, 4),
              therm: int = 12, measurements: int = 24, seed: int = 2026) -> dict:
    if therm < 0 or measurements < 2:
        raise ValueError("therm >= 0 and measurements >= 2 are required")
    g = Gauge(n, dims, beta, seed=seed, hot=True)
    acceptance = []
    for step in range(therm):
        acceptance.append(g.sweep(hits=2))
        if step % 10 == 9:
            g.tune()
    plaquettes = []
    for _ in range(measurements):
        acceptance.append(g.sweep(hits=2))
        plaquettes.append(g.plaquette())
    samples = np.asarray(plaquettes, dtype=float)
    # Explicitly naive estimate: autocorrelation is not estimated here.
    standard_error = float(samples.std(ddof=1) / np.sqrt(len(samples)))
    previous = measure(g, update_index=therm + measurements - 1)
    g.sweep(hits=2)
    current = measure(g, update_index=therm + measurements)
    projected = v8_projection(current, previous)
    gauge_control = run_gauge_transform_control(g)
    root_values = gosset_observable_field(current)
    gosset = gosset_star_report(root_values)
    rng = np.random.default_rng(seed + 17)
    shuffled = gosset_star_report(rng.permutation(root_values))
    return {
        "group": f"SU({n})",
        "N": n,
        "dimensions": list(dims),
        "beta": beta,
        "seed": seed,
        "thermalization_sweeps": therm,
        "measurement_sweeps": measurements,
        "plaquette_mean": float(samples.mean()),
        "plaquette_naive_standard_error": standard_error,
        "acceptance_mean": float(np.mean(acceptance)),
        "final_raw_observables": {
            "plaquette": current.plaquette,
            "action_density": current.action_density,
            "wilson_1x1": current.wilson_1x1,
            "wilson_1x2": current.wilson_1x2,
            "unitarity_residual": current.unitarity_residual,
            "determinant_residual": current.determinant_residual,
        },
        "gauge_invariance_control": gauge_control,
        "v8_projection": projected,
        "gosset_local_global": gosset,
        "gosset_shuffled_null": shuffled,
        "gosset_adjacent_star_delta_mean_minus_shuffle": (
            gosset["adjacent_star_delta_mean"] -
            shuffled["adjacent_star_delta_mean"]
        ),
        "statistical_limit": "Naive standard error only; autocorrelation not estimated.",
        "physical_limit": "Finite-lattice computational experiment; no continuum or mass-gap claim.",
    }


def run_campaign(*, therm: int = 12, measurements: int = 24,
                 dims=(4, 4, 4, 4), seed: int = 2026) -> dict:
    return {
        "campaign": "PAN-YM-V8-GOSSET-v0",
        "typed_spaces": {
            "gauge_base": "periodic hypercubic lattice",
            "gosset": "240 E8 roots / 56-neighbor local stars",
            "v8": ["h", "R", "u", "d", "tau", "chi", "s", "f"],
        },
        "runs": [
            run_group(2, 2.0, dims=dims, therm=therm,
                      measurements=measurements, seed=seed),
            run_group(3, 5.5, dims=dims, therm=therm,
                      measurements=measurements, seed=seed + 1),
        ],
        "conclusion_policy": "Compare controls and raw observables; do not infer physical E8 embedding.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--therm", type=int, default=12)
    parser.add_argument("--meas", type=int, default=24)
    parser.add_argument("--extent", type=int, default=4)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("yang_mills_v8_gosset_results.json"))
    args = parser.parse_args()
    report = run_campaign(
        therm=args.therm, measurements=args.meas,
        dims=(args.extent,) * 4, seed=args.seed,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "runs": [{
            "group": row["group"],
            "plaquette_mean": row["plaquette_mean"],
            "gauge_invariance_pass": row["gauge_invariance_control"]["pass"],
            "gosset_star_mean_global_residual": row["gosset_local_global"]["star_mean_global_residual"],
            "adjacent_star_delta_mean": row["gosset_local_global"]["adjacent_star_delta_mean"],
            "shuffled_adjacent_star_delta_mean": row["gosset_shuffled_null"]["adjacent_star_delta_mean"],
        } for row in report["runs"]],
    }, indent=2))


if __name__ == "__main__":
    main()
