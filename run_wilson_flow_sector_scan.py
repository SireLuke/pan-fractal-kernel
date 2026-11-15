"""Multi-seed Wilson-flow scan for finite-lattice topological-sector diagnostics.

This is deliberately an exploratory finite-spacing campaign. It records raw
clover Q(t), Wilson action, and a predeclared late-flow plateau diagnostic.
It does not round Q or claim continuum topological quantization.

Defaults: 8^4 lattice, third-order Runge-Kutta flow to t = 2.0 (smoothing radius
sqrt(8t) = 4 lattice spacings, half the extent). Starts are hot (random) links,
not thermalized configurations, so the scan probes the flow, not an ensemble.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from lattice_gauge.gradient_flow import wilson_flow
from lattice_gauge.lattice_gauge import Gauge


def scan_one(n: int, beta: float, seed: int, extent: int = 8,
             steps: int = 100, step_size: float = 0.02,
             integrator: str = "rk3") -> dict:
    g = Gauge(n, (extent,) * 4, beta=beta, seed=seed, hot=True)
    history = wilson_flow(g, steps=steps, step_size=step_size, integrator=integrator)
    actions = np.asarray([x["action"] for x in history], dtype=float)
    charges = np.asarray([x["topological_charge"] for x in history], dtype=float)
    tail = charges[-min(8, len(charges)):]
    q_end = float(charges[-1])
    nearest_integer_distance = float(abs(q_end - np.rint(q_end)))
    tail_span = float(np.ptp(tail))
    # Operational diagnostic only; these thresholds are not a theorem.
    plateau_candidate = bool(tail_span < 0.02 and nearest_integer_distance < 0.10)
    increments = np.diff(actions)
    return {
        "group": f"SU({n})",
        "N": n,
        "beta": beta,
        "seed": seed,
        "extent": extent,
        "flow_steps": steps,
        "step_size": step_size,
        "integrator": integrator,
        "flow_time_final": steps * step_size,
        # Gradient-flow smoothing radius sqrt(8t), in lattice spacings; it should
        # stay below about half the extent to avoid finite-volume artefacts.
        "smoothing_radius": float(np.sqrt(8.0 * steps * step_size)),
        "smoothing_radius_over_half_extent": float(np.sqrt(8.0 * steps * step_size) / (extent / 2.0)),
        "initial_action": float(actions[0]),
        "final_action": float(actions[-1]),
        "max_action_increment": float(increments.max(initial=0.0)),
        "action_monotone_within_tolerance": bool(np.all(increments <= 1e-9)),
        "Q_initial": float(charges[0]),
        "Q_final_raw": q_end,
        "distance_to_nearest_integer": nearest_integer_distance,
        "late_flow_Q_span": tail_span,
        "late_flow_plateau_candidate": plateau_candidate,
        "trajectory": history,
        "interpretation": "Finite-lattice raw clover diagnostic only; no continuum or integer-sector claim.",
    }


def run_campaign(extent: int = 8, steps: int = 100, step_size: float = 0.02,
                 seeds: tuple[int, ...] = (101, 202, 303),
                 integrator: str = "rk3") -> dict:
    runs = []
    for n, beta in ((2, 2.0), (3, 5.5)):
        for seed in seeds:
            runs.append(scan_one(n, beta, seed, extent, steps, step_size, integrator))
    return {
        "campaign": "PAN-WILSON-FLOW-SECTOR-SCAN-v1",
        "design": {
            "groups": ["SU(2)", "SU(3)"],
            "seeds": list(seeds),
            "lattice": [extent] * 4,
            "flow_steps": steps,
            "step_size": step_size,
            "integrator": integrator,
            "flow_time_final": steps * step_size,
            "plateau_rule": "last up to 8 Q samples span < 0.02 and endpoint distance to nearest integer < 0.10",
            "warning": "Exploratory coarse finite-lattice thresholds, not continuum criteria.",
        },
        "runs": runs,
        "summary": {
            "all_actions_monotone": all(r["action_monotone_within_tolerance"] for r in runs),
            "plateau_candidates": sum(r["late_flow_plateau_candidate"] for r in runs),
            "run_count": len(runs),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extent", type=int, default=8)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--step-size", type=float, default=0.02)
    parser.add_argument("--integrator", choices=("euler", "rk3"), default="rk3")
    parser.add_argument("--seeds", type=int, nargs="+", default=[101, 202, 303])
    parser.add_argument("--output", type=Path, default=Path("wilson_flow_sector_scan.json"))
    args = parser.parse_args()
    report = run_campaign(args.extent, args.steps, args.step_size, tuple(args.seeds), args.integrator)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
