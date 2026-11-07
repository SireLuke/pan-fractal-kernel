import pytest

from transition_algebra import (
    History, Transition, V8State, becoming, compression, emergence,
    hydra, identity_distance, janus, memory, no_reset_holds, potential,
    structure, ubp_log,
)


def state(value=0.5):
    return V8State(value, value, value, value, value, value, value, value)


def event(event_id="e1", payload=None):
    return Transition(event_id, "test", payload or {"step": 1})


def test_potential_is_set_valued_and_emergence_selects_explicitly():
    source = state()
    candidates = potential(source, lambda x: (x, state(0.7)))
    assert len(candidates) == 2
    assert source == state()
    assert emergence(candidates, lambda items: 1) == state(0.7)
    with pytest.raises(ValueError):
        potential(source, lambda x: ())


def test_operator_contracts_for_structure_compression_janus_and_hydra():
    assert structure(2, lambda x: min(x, 1)) == 1
    assert compression({"x": 1}, lambda x: b"encoded") == b"encoded"
    with pytest.raises(TypeError):
        compression(1, lambda x: "not bytes")
    pair = janus(3, lambda x: x + 1, lambda x: -x)
    assert (pair.formation, pair.dissolution) == (4, -3)
    branches = hydra(2, {"double": lambda x: 2*x, "square": lambda x: x*x})
    assert branches == {"double": 4, "square": 4}
    with pytest.raises(ValueError):
        hydra(1, {})


def test_history_is_append_only_and_rejects_duplicate_ids():
    first = memory(History(), event("a"))
    second = memory(first, event("b", {"step": 2}))
    assert second.events[:1] == first.events
    assert second.revision == 2
    with pytest.raises(ValueError):
        memory(second, event("a"))


def test_ubp_log_is_deterministic_versioned_and_explicitly_lossy():
    h1 = History((event("a", {"x": 1, "y": 2}),))
    h2 = History((event("a", {"y": 2, "x": 1}),))
    assert ubp_log(h1) == ubp_log(h2)
    assert ubp_log(h1).schema == "pan-ubp-json-sha256-v1"
    # A digest is a fingerprint, not a reconstructable history.
    assert isinstance(ubp_log(h1).digest, str)
    assert len(ubp_log(h1).digest) == 64


def test_identity_and_conditional_no_reset_invariant():
    initial = becoming(state(), History())
    next_history = memory(initial.history, event("unique-1"))
    updated = becoming(state(), next_history)
    assert no_reset_holds(initial, updated)
    assert identity_distance(initial, updated) > 0
    assert not no_reset_holds(updated, updated)
    # Different paths with the same endpoint state remain distinguishable.
    other = becoming(state(), History((event("different-path"),)))
    assert identity_distance(updated, other) > 0


def test_metric_rejects_negative_weights():
    identity = becoming(state(), History())
    with pytest.raises(ValueError):
        identity_distance(identity, identity, state_weight=-1)
