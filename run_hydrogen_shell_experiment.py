"""Reproduces the numbers in HYDROGEN_SHELL_MODES.md. Deterministic (fixed seeds)."""
import json, math, sys
import numpy as np
import hydrogen_shell_modes as H

SEEDS_VIEW = (421, 7, 73)
SCALES = (2.0, 6.0, 12.0)
NULL_TRIALS = 40


def main(path=None):
    states = H.states_up_to(3)
    out = {"solid_gram_max_error": {}, "cross_lm_overlap": []}
    for n in (1, 2, 3):
        out["solid_gram_max_error"][f"shell{n}"] = max(H.solid_gram_error(H.shell_view(n, s)) for s in SEEDS_VIEW)
        p = H.shell_view(n, 421)
        rho = np.linalg.norm(p, axis=1)
        rng = np.random.default_rng(1000 + n)
        for scale in SCALES:
            e8 = H.max_cross_lm_overlap(p, states, length_scale=scale)
            nulls = []
            for _ in range(NULL_TRIALS):
                d = rng.normal(size=p.shape); d /= np.linalg.norm(d, axis=1)[:, None]
                nulls.append(H.max_cross_lm_overlap(d * rho[:, None], states, length_scale=scale))
            out["cross_lm_overlap"].append({
                "shell": n, "points": len(p), "length_scale_a0_per_unit": scale, "e8": e8,
                "null_median": float(np.median(nulls)), "null_min": float(min(nulls)),
                "fraction_null_le_e8": float(np.mean(np.array(nulls) <= e8))})
    text = json.dumps(out, indent=1)
    print(text)
    if path:
        open(path, "w").write(text)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
