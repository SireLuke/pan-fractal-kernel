"""Reproduces HYDROGEN_SHELL_SCALE_RULE.md. Deterministic (fixed seeds, 200 null trials)."""
import json, sys
import hydrogen_shell_scale as S


def main(path=None):
    out = {"preregistered_factor": S.PREREGISTERED_FACTOR, "halpha": S.halpha_check(),
           "planck_length_m": S.PLANCK_LENGTH_M,
           "results": [S.evaluate_rule(r, n) for r in S.RULES for n in (1, 2, 3)]}
    text = json.dumps(out, indent=1)
    print(text)
    if path:
        open(path, "w").write(text)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
