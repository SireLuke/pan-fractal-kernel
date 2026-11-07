import numpy as np
import pytest

from hydra_semantic_reader import INVERSE_NAMES, PAIR_KEYS
from janus_hydra import V8_KEYS, V8State, formation_heads, inverse_heads
from janus_metrics import head_matrices, head_metrics, pair_defect

RNG = np.random.default_rng(20261104)


def _rand_state():
    return V8State(**dict(zip(V8_KEYS, RNG.random(8))))


def test_matrix_form_reproduces_shipped_heads_exactly():
    wf, wi, bi = head_matrices()
    for _ in range(200):
        s = _rand_state()
        x = np.array([getattr(s, k) for k in V8_KEYS])
        f, i = formation_heads(s), inverse_heads(s)
        assert wf @ x == pytest.approx([f[k] for k in PAIR_KEYS], abs=1e-12)
        assert wi @ x + bi == pytest.approx([i[INVERSE_NAMES[k]] for k in PAIR_KEYS], abs=1e-12)


def test_pair_defect_closed_forms():
    for _ in range(200):
        s = _rand_state()
        d = pair_defect(s)
        assert d["bubble"] == pytest.approx((s.R + s.d - 1) / 3, abs=1e-12)
        assert d["compoundeye"] == pytest.approx((2 * s.d - 1) / 3, abs=1e-12)
        for k in ("honeycomb", "spiderweb", "chiraldna"):
            assert d[k] == pytest.approx(0.0, abs=1e-12)


def test_structural_metrics_are_pinned():
    m = head_metrics()
    assert m["rank_formation"] == 5 and m["nullity_formation"] == 3
    assert m["rank_stacked"] == 7
    assert m["lipschitz_linf"] == pytest.approx(1.0)
    assert m["tautological_pairs"] == ["honeycomb", "spiderweb", "chiraldna"]
    assert m["informative_pairs"] == ["bubble", "compoundeye"]
    assert m["participation_ratio"] == pytest.approx(3.358, abs=1e-3)


def test_uniform_covariance_matches_monte_carlo_within_sampling_error():
    wf, _, _ = head_matrices()
    x = np.random.default_rng(7).random((40000, 8))
    emp = np.cov((x @ wf.T).T)
    assert np.abs(emp - wf @ wf.T / 12.0).max() < 2e-3
