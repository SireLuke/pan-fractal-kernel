"""Multi-seed Wilson-flow scan for finite-lattice topological-sector diagnostics.

This is deliberately an exploratory finite-spacing campaign. It records raw
clover Q(t), Wilson action, and a predeclared late-flow plateau diagnostic.
It does not round Q or claim continuum topological quantization.

Defaults: 8^4 lattice, third-order Runge-Kutta flow to t = 2.0 (smoothing radius
sqrt(8t) = 4 lattice spacings, half the extent), starting from Metropolis-thermalized
configurations (SU(2) beta=2.4, SU(3) beta=6.0). `--start hot` flows random links
instead, which probes the flow rather than an ensemble.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import numpy as np

from lattice_gauge.gradient_flow import wilson_flow
from lattice_gauge.lattice_gauge import Gauge


def thermalized_links(n: int, beta: float, seed: int, extent: int, therm: int,
                      n_configs: int, sep: int):
    """Metropolis-thermalize from a cold start, then yield n_configs link sets.

    A cold start is used deliberately: at 8^4 and SU(3) beta=6.0 the plaquette reaches
    its equilibrium value (about 0.594) within roughly 100-200 sweeps from cold, while a
    hot (random) start is still visibly below it after 400. Consecutive configurations
    are separated by `sep` sweeps. Each yielded item is (links, plaquette) with links
    copied so flowing them never touches the chain.
    """
    g = Gauge(n, (extent,) * 4, beta=beta, seed=seed, hot=False)

    def sweeps(count: int, offset: int = 0) -> None:
        for i in range(count):
            g.sweep()
            # Tune every sweep for the first 50 sweeps (large N starts with ~0 acceptance
            # at the default step size), then every 10 sweeps as before.
            if (i + offset) < 50 or (i + offset) % 10 == 9:
                g.tune()
            if (i + offset) % 20 == 19:
                g.reunitarize()

    sweeps(therm)
    for k in range(n_configs):
        sweeps(sep, offset=therm + k * sep)
        g.reunitarize()
        yield [u.copy() for u in g.U], g.plaquette()


def scan_one(n: int, beta: float, seed: int, extent: int = 8,
             steps: int = 100, step_size: float = 0.02,
             integrator: str = "rk3", links=None,
             start_plaquette: float | None = None) -> dict:
    g = Gauge(n, (extent,) * 4, beta=beta, seed=seed, hot=links is None)
    if links is not None:
        g.U = [u.copy() for u in links]
    history = wilson_flow(g, steps=steps, step_size=step_size, integrator=integrator)
    # Wilson-action energy density from the flowed action: E = 12 N (1 - P) per site
    # = 2 N S / (beta V). t^2 E is the standard flow observable (no literature
    # comparison is claimed here).
    volume = float(extent ** 4)
    for row in history:
        row["t2E"] = float(row["flow_time"] ** 2 * 2.0 * n * row["action"] / (beta * volume))
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
        "start": "hot" if links is None else "thermalized",
        "start_plaquette": start_plaquette,
        "t2E_final": history[-1]["t2E"],
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


HOT_BETAS = {2: 2.0, 3: 5.5}
THERMALIZED_BETAS = {2: 2.4, 3: 6.0}


def parse_beta_overrides(tokens) -> dict[int, float]:
    """Parse ["10=45", "2=2.5"] into {10: 45.0, 2: 2.5}."""
    out: dict[int, float] = {}
    for tok in tokens or ():
        n_text, sep, b_text = tok.partition("=")
        if not sep:
            raise ValueError(f"beta override {tok!r} must look like N=value")
        out[int(n_text)] = float(b_text)
    return out


def run_campaign(extent: int = 8, steps: int = 100, step_size: float = 0.02,
                 seeds: tuple[int, ...] = (101, 202, 303),
                 integrator: str = "rk3", start: str = "thermalized",
                 therm: int = 200, sep: int = 40, configs: int = 5,
                 groups: tuple[int, ...] = (2, 3), progress: bool = False,
                 betas: dict[int, float] | None = None) -> dict:
    """Flow campaign over SU(2) and SU(3).

    start="thermalized": one cold-start Metropolis chain per group (seeded by
    seeds[0]), `therm` sweeps, then `configs` configurations `sep` sweeps apart.
    start="hot": one flow per seed from random links (the original design).
    """
    if start not in ("thermalized", "hot"):
        raise ValueError("start must be 'thermalized' or 'hot'")
    runs = []
    if not groups or any((not isinstance(n, int)) or n < 2 for n in groups):
        raise ValueError("groups must be integers N >= 2")
    defaults = THERMALIZED_BETAS if start == "thermalized" else HOT_BETAS
    table = {**defaults, **(betas or {})}
    missing = [n for n in groups if n not in table]
    if missing:
        raise ValueError(f"no default beta for SU({missing[0]}); pass betas={{{missing[0]}: value}}")
    betas = tuple((n, table[n]) for n in groups)

    def note(row: dict) -> None:
        if progress:
            print(f"{row['group']} cfg {row.get('config_index', row['seed'])}: "
                  f"Q_final={row['Q_final_raw']:.3f} plateau={row['late_flow_plateau_candidate']}",
                  file=sys.stderr, flush=True)

    for n, beta in betas:
        if start == "hot":
            for seed in seeds:
                runs.append(scan_one(n, beta, seed, extent, steps, step_size, integrator))
                note(runs[-1])
        else:
            for k, (links, plaq) in enumerate(
                    thermalized_links(n, beta, seeds[0], extent, therm, configs, sep)):
                row = scan_one(n, beta, seeds[0], extent, steps, step_size, integrator,
                               links=links, start_plaquette=plaq)
                row["config_index"] = k
                runs.append(row)
                note(row)
    by_group = {}
    for r in runs:
        by_group.setdefault(r["group"], []).append(r)
    per_group = {
        grp: {
            "runs": len(rows),
            "plateau_candidates": sum(r["late_flow_plateau_candidate"] for r in rows),
            "mean_start_plaquette": (float(np.mean([r["start_plaquette"] for r in rows]))
                                     if start == "thermalized" else None),
            "Q_final_raw": [round(r["Q_final_raw"], 3) for r in rows],
        }
        for grp, rows in by_group.items()
    }
    return {
        "campaign": "PAN-WILSON-FLOW-SECTOR-SCAN-v2",
        "design": {
            "groups": [f"SU({n})" for n, _ in betas],
            "start": start,
            "betas": {f"SU({n})": b for n, b in betas},
            "seeds": list(seeds),
            "thermalization_sweeps": therm if start == "thermalized" else None,
            "separation_sweeps": sep if start == "thermalized" else None,
            "configs_per_group": configs if start == "thermalized" else None,
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
            "per_group": per_group,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extent", type=int, default=8)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--step-size", type=float, default=0.02)
    parser.add_argument("--integrator", choices=("euler", "rk3"), default="rk3")
    parser.add_argument("--start", choices=("thermalized", "hot"), default="thermalized")
    parser.add_argument("--therm", type=int, default=200, help="thermalization sweeps")
    parser.add_argument("--sep", type=int, default=40, help="sweeps between configurations")
    parser.add_argument("--configs", type=int, default=5, help="configurations per group")
    parser.add_argument("--groups", type=int, nargs="+", default=[2, 3],
                        help="gauge groups N to run (SU(N)); N other than 2, 3 needs --beta")
    parser.add_argument("--beta", nargs="*", default=[], metavar="N=VALUE",
                        help="per-group beta, e.g. --beta 3=5.85 10=45")
    parser.add_argument("--seeds", type=int, nargs="+", default=[101, 202, 303])
    parser.add_argument("--output", type=Path, default=Path("wilson_flow_sector_scan.json"))
    args = parser.parse_args()
    report = run_campaign(args.extent, args.steps, args.step_size, tuple(args.seeds),
                          args.integrator, args.start, args.therm, args.sep, args.configs,
                          tuple(args.groups), progress=True,
                          betas=parse_beta_overrides(args.beta))
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
