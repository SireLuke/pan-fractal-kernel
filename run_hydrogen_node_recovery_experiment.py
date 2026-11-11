"""Reproduces HYDROGEN_NODE_RECOVERY.md. Deterministic. Primary: seed 421, k=10, 100 null trials."""
import json, sys
import hydrogen_node_recovery as N

def main(path=None):
    out = {"primary": [], "sensitivity_k": [], "low_n_stress": []}
    for rule in ("lattice_unit", "mean_radius"):
        for n in (2, 3):
            out["primary"].append(N.evaluate(n, rule, k=N.PRIMARY_K, null_trials=100))
            for k in (6, 16):
                r = N.evaluate(n, rule, k=k, null_trials=30)
                out["sensitivity_k"].append({kk: r[kk] for kk in ("shell", "rule", "k", "null_rate_mean", "null_rate_p95", "passes")}
                                            | {"e8_rate": r["e8"]["recovery_rate"], "scored": r["e8"]["scored"]})
    for rule in ("lattice_unit", "mean_radius"):
        for n in (2, 3):
            for n_sub in (120, 240, 480):
                out["low_n_stress"].append(N.evaluate_subsampled(n, rule, n_sub, trials=20))
    text = json.dumps(out, indent=1)
    if path: open(path, "w").write(text)
    return out

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
