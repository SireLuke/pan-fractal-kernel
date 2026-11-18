import json
import random
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from abom_v8.routing import (
    AXES, BenchmarkMap, CapabilityVector, NahtChannelParameters, Niche, NicheMap,
    NoEligibleOccupant, OllamaTransport, Occupant, PlacementError, TaskProfile,
    TransportError, dispatch, fit_cost, l1_distance, place, route,
)


def vec(**overrides):
    base = {axis: 0.5 for axis in AXES}
    base.update(overrides)
    return CapabilityVector.from_mapping(base)


def rand_vec(rng):
    return CapabilityVector(tuple(rng.random() for _ in AXES))


# --- capability space -------------------------------------------------------

def test_vector_validation():
    with pytest.raises(ValueError):
        CapabilityVector((0.5,) * 7)
    with pytest.raises(ValueError):
        CapabilityVector((0.5,) * 7 + (1.5,))
    with pytest.raises(ValueError):
        CapabilityVector((0.5,) * 7 + (float("nan"),))
    with pytest.raises(ValueError):
        CapabilityVector((0.5,) * 7 + (True,))
    with pytest.raises(ValueError):
        CapabilityVector.from_mapping({**{a: 0.5 for a in AXES}, "vendor": 1.0})
    assert vec(tool_use=0.9)["tool_use"] == 0.9


def test_l1_is_a_metric_on_random_vectors():
    rng = random.Random(20261117)
    for _ in range(200):
        a, b, c = rand_vec(rng), rand_vec(rng), rand_vec(rng)
        assert l1_distance(a, a) == 0.0
        assert l1_distance(a, b) == pytest.approx(l1_distance(b, a))
        assert l1_distance(a, c) <= l1_distance(a, b) + l1_distance(b, c) + 1e-12


def test_fit_cost_penalises_shortfall_more_than_excess():
    need = vec(symbolic=0.6)
    short = vec(symbolic=0.4)
    over = vec(symbolic=0.8)
    assert fit_cost(need, short) > fit_cost(need, over) > fit_cost(need, need) == 0.0
    assert fit_cost(need, over, excess_penalty=1.0) == pytest.approx(l1_distance(need, over))
    with pytest.raises(ValueError):
        fit_cost(need, over, weights=[0.0] * 8)


# --- placement --------------------------------------------------------------

CALIBRATION = [  # illustrative test calibration, not a validated one
    BenchmarkMap(f"bench_{axis}", axis, 0.0, 100.0) for axis in AXES
]


def test_place_normalises_and_reports_evidence():
    results = {f"bench_{axis}": 50.0 for axis in AXES}
    results["bench_tool_use"] = 90.0
    placement = place(results, CALIBRATION, calibration_version="test-1")
    vector = placement.require_vector()
    assert vector["tool_use"] == pytest.approx(0.9)
    assert vector["symbolic"] == pytest.approx(0.5)
    assert placement.evidence["tool_use"] == ("bench_tool_use",)
    assert placement.calibration_version == "test-1"


def test_place_clips_and_inverts_and_averages():
    maps = [
        BenchmarkMap("fast", "tool_use", 0.0, 10.0),
        BenchmarkMap("latency_ms", "tool_use", 1000.0, 0.0),   # lower is better
    ]
    placement = place({"fast": 20.0, "latency_ms": 750.0}, maps)
    assert set(placement.clipped) == {"fast"}
    assert placement.missing_axes == tuple(a for a in AXES if a != "tool_use")


def test_missing_axis_is_never_filled_in():
    placement = place({"bench_tool_use": 80.0}, CALIBRATION)
    assert placement.vector is None
    assert "symbolic" in placement.missing_axes
    with pytest.raises(PlacementError):
        placement.require_vector()


def test_benchmark_map_validation():
    with pytest.raises(ValueError):
        BenchmarkMap("x", "not_an_axis", 0.0, 1.0)
    with pytest.raises(ValueError):
        BenchmarkMap("x", "tool_use", 1.0, 1.0)
    with pytest.raises(ValueError):
        place({"bench_tool_use": float("inf")}, CALIBRATION)


# --- niche map --------------------------------------------------------------

def make_map():
    return NicheMap([
        Niche("reasoning", vec(symbolic=0.9, recursive_depth=0.9)),
        Niche("coding", vec(tool_use=0.9, symbolic=0.7), minimums={"tool_use": 0.6}),
        Niche("knowledge", vec(memory_bandwidth=0.9, context_coherence=0.9)),
    ])


def occ(model_id, vector, **kwargs):
    return Occupant(model_id, kwargs.pop("transport_id", "fake"), vector, **kwargs)


def test_topology_is_fixed_under_swaps():
    nmap = make_map()
    ids_before = nmap.niche_ids
    first = occ("model-a", vec(symbolic=0.9, recursive_depth=0.9))
    nmap.seat("reasoning", first)
    displaced = nmap.seat("reasoning", occ("model-b", vec(symbolic=0.95, recursive_depth=0.95)))
    assert displaced == first
    nmap.vacate("reasoning")
    assert nmap.niche_ids == ids_before


def test_seat_enforces_minimums_and_unique_models():
    nmap = make_map()
    with pytest.raises(ValueError):
        nmap.seat("coding", occ("weak", vec(tool_use=0.2)))
    nmap.seat("reasoning", occ("m", vec(symbolic=0.9, recursive_depth=0.9)))
    with pytest.raises(ValueError):
        nmap.seat("knowledge", occ("m", vec(memory_bandwidth=0.9)))
    with pytest.raises(KeyError):
        nmap.seat("nowhere", occ("z", vec()))


def test_place_picks_nearest_niche_and_incumbent_needs_strictly_closer():
    nmap = make_map()
    anchor = nmap.niche("reasoning").anchor
    first = nmap.place(occ("a", anchor))
    assert (first.niche_id, first.seated) == ("reasoning", True)
    tie = nmap.place(occ("b", anchor))
    assert tie.seated is False and nmap.occupant("reasoning").model_id == "a"
    farther = nmap.place(occ("c", vec(symbolic=0.8, recursive_depth=0.8)))
    assert farther.seated is False
    refresh = nmap.place(occ("a", anchor, calibration_version="test-2"))
    assert refresh.seated and refresh.displaced is None
    assert nmap.occupant("reasoning").calibration_version == "test-2"


def test_place_reports_when_no_niche_accepts():
    nmap = NicheMap([Niche("only", vec(), minimums={"tool_use": 0.9})])
    decision = nmap.place(occ("weak", vec(tool_use=0.1)))
    assert decision.niche_id is None and decision.seated is False


def test_replacing_a_model_that_moved_niche_vacates_the_old_one():
    nmap = make_map()
    nmap.place(occ("a", nmap.niche("reasoning").anchor))
    moved = nmap.place(occ("a", nmap.niche("knowledge").anchor))
    assert moved.niche_id == "knowledge" and moved.seated
    assert nmap.occupant("reasoning") is None
    assert nmap.niche_of("a") == "knowledge"


def test_niche_map_rejects_bad_construction():
    with pytest.raises(ValueError):
        NicheMap([])
    with pytest.raises(ValueError):
        NicheMap([Niche("x", vec()), Niche("x", vec())])


# --- routing ----------------------------------------------------------------

def seated_map():
    nmap = make_map()
    nmap.seat("reasoning", occ("r1", vec(symbolic=0.9, recursive_depth=0.9), context_tokens=32_000))
    nmap.seat("coding", occ("c1", vec(tool_use=0.9, symbolic=0.7), context_tokens=128_000))
    nmap.seat("knowledge", occ("k1", vec(memory_bandwidth=0.9, context_coherence=0.9)))
    return nmap


def test_route_selects_by_capability():
    nmap = seated_map()
    decision = route(TaskProfile(vec(tool_use=0.9, symbolic=0.7)), nmap)
    assert (decision.niche_id, decision.occupant.model_id) == ("coding", "c1")
    assert [row[0] for row in decision.ranking][0] == "coding"
    decision = route(TaskProfile(vec(memory_bandwidth=0.9, context_coherence=0.9)), nmap)
    assert decision.niche_id == "knowledge"


def test_route_ignores_model_names_and_is_deterministic():
    task = TaskProfile(vec(symbolic=0.8))
    a = route(task, seated_map())
    renamed = seated_map()
    for niche_id, old in renamed.occupants():
        renamed.seat(niche_id, Occupant(f"renamed-{old.model_id}", "other", old.vector,
                                        context_tokens=old.context_tokens))
    b = route(task, renamed)
    assert a.niche_id == b.niche_id
    assert [r[2] for r in a.ranking] == [r[2] for r in b.ranking]
    assert route(task, seated_map()) == a


def test_route_ties_break_by_niche_id():
    nmap = NicheMap([Niche("zeta", vec()), Niche("alpha", vec())])
    nmap.seat("zeta", occ("m1", vec()))
    nmap.seat("alpha", occ("m2", vec()))
    assert route(TaskProfile(vec()), nmap).niche_id == "alpha"


def test_route_hard_requirements():
    nmap = seated_map()
    with pytest.raises(NoEligibleOccupant):
        route(TaskProfile(vec(), minimums={"coordination": 0.9}), nmap)
    only_big = route(TaskProfile(vec(), min_context_tokens=100_000), nmap)
    assert only_big.occupant.model_id == "c1"      # unknown context never qualifies
    with pytest.raises(ValueError):
        TaskProfile(vec(), min_context_tokens=0)
    with pytest.raises(ValueError):
        TaskProfile(vec(), minimums={"vendor": 0.5})


def test_swapping_an_occupant_reroutes_without_touching_topology():
    nmap = seated_map()
    task = TaskProfile(vec(tool_use=0.95, symbolic=0.7))
    before = route(task, nmap)
    nmap.seat("coding", occ("c2", vec(tool_use=0.95, symbolic=0.7), context_tokens=64_000))
    after = route(task, nmap)
    assert before.niche_id == after.niche_id == "coding"
    assert (before.occupant.model_id, after.occupant.model_id) == ("c1", "c2")
    assert after.cost < before.cost


# --- transports -------------------------------------------------------------

class FakeTransport:
    transport_id = "fake"

    def __init__(self):
        self.calls = []

    def generate(self, model_id, prompt, *, timeout=60.0):
        self.calls.append((model_id, prompt))
        return f"{model_id}:{prompt}"


def test_dispatch_uses_the_routed_models_transport():
    fake = FakeTransport()
    result = dispatch("hi", TaskProfile(vec(tool_use=0.9, symbolic=0.7)), seated_map(),
                      {"fake": fake})
    assert result.text == "c1:hi" and fake.calls == [("c1", "hi")]
    with pytest.raises(KeyError):
        dispatch("hi", TaskProfile(vec()), seated_map(), {})


class _OllamaStub(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/tags":
            self._send(200, {"models": [{"name": "qwen"}, {"name": "llama"}, {"bad": 1}]})
        else:
            self._send(404, {})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        if self.path == "/api/generate" and body.get("stream") is False:
            self._send(200, {"response": f"{body['model']}|{body['prompt']}"})
        elif self.path == "/api/generate":
            self._send(400, {})
        else:
            self._send(404, {})


@pytest.fixture()
def ollama_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _OllamaStub)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_ollama_transport_against_a_local_stub(ollama_url):
    transport = OllamaTransport(ollama_url)
    assert transport.generate("qwen", "hello") == "qwen|hello"
    assert transport.list_models() == ("qwen", "llama")
    nmap = seated_map()
    result = dispatch("ping", TaskProfile(vec(tool_use=0.9, symbolic=0.7)), nmap,
                      {"fake": transport})
    assert result.text == "c1|ping"


def test_ollama_transport_errors_and_url_validation(ollama_url):
    with pytest.raises(ValueError):
        OllamaTransport("ftp://example.com")
    with pytest.raises(ValueError):
        OllamaTransport("not a url")
    with pytest.raises(TransportError):
        OllamaTransport("http://127.0.0.1:9").generate("m", "p", timeout=2.0)
    bad = OllamaTransport(ollama_url + "/nope")
    with pytest.raises(TransportError):
        bad.generate("m", "p")


# --- NAHT parameters ---------------------------------------------------------

def test_naht_defaults_to_unassigned_and_requires_metadata_when_assigned():
    assert NahtChannelParameters().assigned is False
    assert Occupant("m", "t", vec()).naht.assigned is False
    with pytest.raises(ValueError):
        NahtChannelParameters(r=0.1)
    with pytest.raises(ValueError):
        NahtChannelParameters(r=float("nan"), units="u", normalization="n",
                              provenance="p", calibration_version="c")
    ok = NahtChannelParameters(r=0.1, e=0.2, p=0.3, units="dimensionless",
                               normalization="unit-sum", provenance="test",
                               calibration_version="t-1")
    assert ok.assigned
