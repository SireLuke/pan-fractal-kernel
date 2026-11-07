import numpy as np
import pytest
from hydra_semantic_reader import HEAD_SUPPORT, INVERSE_SUPPORT, read_semantics
from janus_hydra import V8State, formation_heads, inverse_heads

def state(values=(0.8, 0.7, 0.75, 0.25, 0.65, 0.6, 0.72, 0.55)):
    return V8State(*values)

def expected_defects(v):
    return {
        "bubble": (v.R + v.d - 1.0) / 3.0,
        "compoundeye": (2.0*v.d - 1.0) / 3.0,
        "honeycomb": (v.tau + v.s + 2.0*v.d - 2.0) / 6.0,
        "spiderweb": (v.f + v.h + v.R + 3.0*v.d - 3.0) / 12.0,
        "chiraldna": (v.chi + v.tau + v.R + 3.0*v.d - 3.0) / 12.0,
    }

def actual_defects(v):
    f, inv = formation_heads(v), inverse_heads(v)
    pairs = {
        "bubble": "antibubble_cavitation",
        "compoundeye": "discretesingulardots_inversecompoundeye",
        "honeycomb": "inversehoneycomb",
        "spiderweb": "inversespiderweb_radialvoid",
        "chiraldna": "chiralvoid",
    }
    return {key: f[key] + inv[inverse_key] - 1.0 for key, inverse_key in pairs.items()}

def test_all_five_dynamic_inverse_equations_and_pair_defects():
    v = state()
    for key, expected in expected_defects(v).items():
        assert actual_defects(v)[key] == pytest.approx(expected, abs=1e-12)

def test_all_inverse_heads_are_density_coupled_and_bounded():
    inv = inverse_heads(state())
    assert all(0.0 <= score <= 1.0 for score in inv.values())
    assert set(INVERSE_SUPPORT) == set(HEAD_SUPPORT)
    assert all("d" in support for support in INVERSE_SUPPORT.values())
    assert set().union(*map(set, INVERSE_SUPPORT.values())) == set(("h","R","u","d","tau","chi","s","f"))

def test_density_derivatives_match_canonical_pair_defect_slopes():
    values, step = [0.8,0.7,0.75,0.25,0.65,0.6,0.72,0.55], 1e-6
    slopes = {"bubble":1/3, "compoundeye":2/3, "honeycomb":1/3, "spiderweb":1/4, "chiraldna":1/4}
    for key, expected in slopes.items():
        plus, minus = values.copy(), values.copy()
        plus[3] += step
        minus[3] -= step
        derivative = (actual_defects(state(plus))[key] - actual_defects(state(minus))[key])/(2*step)
        assert derivative == pytest.approx(expected, abs=1e-9)

def test_reader_keeps_v8_order_and_versioned_inverse_rule():
    frame = read_semantics(state())
    assert frame.coordinate_order == ("h","R","u","d","tau","chi","s","f")
    assert frame.schema_version == "JANUS-HYDRA-DYNAMIC-INVERSE-v1"
    assert all(p["inverse_rule"] == frame.schema_version for p in frame.paired_heads.values())
    assert frame.uhfe_channels.shape == frame.udfe_channels.shape == (8,)
    assert np.all(np.isfinite(frame.uhfe_channels)) and np.all(np.isfinite(frame.udfe_channels))

def test_replay_and_separate_support_maps_are_stable():
    a, b = read_semantics(state()), read_semantics(state())
    assert a.state == b.state and a.uhfe_heads == b.uhfe_heads and a.udfe_heads == b.udfe_heads
    assert HEAD_SUPPORT["honeycomb"] == ("tau","s")
    assert HEAD_SUPPORT["spiderweb"] == ("f","h","R")
    assert HEAD_SUPPORT["chiraldna"] == ("chi","tau","R")
    assert INVERSE_SUPPORT["honeycomb"] == ("d","tau","s")
    assert INVERSE_SUPPORT["spiderweb"] == ("d","f","h","R")
    assert INVERSE_SUPPORT["chiraldna"] == ("d","chi","tau","R")

def test_randomized_scores_and_defects_respect_analytic_bounds():
    rng = np.random.default_rng(20261107)
    bounds = {"bubble":(-1/3,1/3), "compoundeye":(-1/3,1/3), "honeycomb":(-1/3,1/3),
              "spiderweb":(-1/4,1/4), "chiraldna":(-1/4,1/4)}
    for _ in range(500):
        v = state(tuple(rng.random(8)))
        f, inv = formation_heads(v), inverse_heads(v)
        assert all(0 <= x <= 1 for x in f.values()) and all(0 <= x <= 1 for x in inv.values())
        for key, defect in actual_defects(v).items():
            assert bounds[key][0]-1e-12 <= defect <= bounds[key][1]+1e-12
