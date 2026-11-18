import dataclasses

import pytest

from abom_v8.routing import (
    AXES, GENESIS_HASH, CapabilityVector, EvidenceLevel, LedgerError, Niche, NicheMap,
    Occupant, PlacementLedger, Provenance, TaskProfile, route,
)


def vec(**overrides):
    base = {axis: 0.5 for axis in AXES}
    base.update(overrides)
    return CapabilityVector.from_mapping(base)


def prov(model_id, vector, level=EvidenceLevel.BENCHMARKED, **kwargs):
    kwargs.setdefault("sources", ("bench-suite-a",))
    kwargs.setdefault("calibration_version", "test-1")
    if level >= EvidenceLevel.REPRODUCED:
        kwargs.setdefault("attested_by", ("lab-1", "lab-2")[: 1 if level == 2 else 2])
    return Provenance.create(model_id, vector, level, **kwargs)


def occ(model_id, vector, level=None, **kwargs):
    provenance = None if level is None else prov(model_id, vector, level)
    return Occupant(model_id, "fake", vector, provenance=provenance, **kwargs)


# --- provenance -------------------------------------------------------------

def test_digest_is_deterministic_and_verifies():
    v = vec(tool_use=0.8)
    a, b = prov("m", v), prov("m", v)
    assert a.digest == b.digest and a.verify("m", v)


def test_digest_detects_tampering():
    v = vec(tool_use=0.8)
    p = prov("m", v)
    assert not p.verify("other-model", v)
    assert not p.verify("m", vec(tool_use=0.81))
    forged = dataclasses.replace(p, level=EvidenceLevel.REPRODUCED, attested_by=("x",))
    assert not forged.verify("m", v)


def test_level_requirements_are_enforced():
    v = vec()
    with pytest.raises(ValueError):
        Provenance.create("m", v, EvidenceLevel.BENCHMARKED, "c-1")                # no sources
    with pytest.raises(ValueError):
        Provenance.create("m", v, EvidenceLevel.REPRODUCED, "c-1", sources=("s",))  # no attester
    with pytest.raises(ValueError):
        Provenance.create("m", v, EvidenceLevel.INDEPENDENTLY_REPRODUCED, "c-1",
                          sources=("s",), attested_by=("a",))
    with pytest.raises(ValueError):
        Provenance.create("m", v, EvidenceLevel.INDEPENDENTLY_REPRODUCED, "c-1",
                          sources=("s",), attested_by=("a", "a"))
    with pytest.raises(ValueError):
        Provenance.create("m", v, EvidenceLevel.DECLARED, " ")
    with pytest.raises(ValueError):
        dataclasses.replace(prov("m", v), digest="xyz")
    assert Provenance.create("m", v, EvidenceLevel.DECLARED, "c-1").level == 0


def test_provenance_ok_follows_the_occupant_it_was_made_for():
    v = vec()
    assert occ("m", v, EvidenceLevel.BENCHMARKED).provenance_ok
    assert not occ("m", v).provenance_ok
    stolen = Occupant("impostor", "fake", v, provenance=prov("m", v))
    assert not stolen.provenance_ok


# --- gating -----------------------------------------------------------------

def gated_map(**kwargs):
    return NicheMap([
        Niche("strict", vec(), min_evidence=EvidenceLevel.REPRODUCED),
        Niche("open", vec(symbolic=0.9)),
    ], **kwargs)


def test_niche_requires_verified_evidence_of_enough_rank():
    nmap = gated_map()
    v = vec()
    with pytest.raises(ValueError):
        nmap.seat("strict", occ("m", v))                                        # none
    with pytest.raises(ValueError):
        nmap.seat("strict", occ("m", v, EvidenceLevel.BENCHMARKED))             # too low
    with pytest.raises(ValueError):
        nmap.seat("strict", Occupant("m", "fake", v, provenance=prov("z", v, EvidenceLevel.REPRODUCED)))
    assert nmap.seat("strict", occ("m", v, EvidenceLevel.REPRODUCED)) is None
    assert nmap.seat("strict", occ("n", v, EvidenceLevel.INDEPENDENTLY_REPRODUCED)).model_id == "m"


def test_raising_evidence_never_loses_eligibility():
    nmap = gated_map()
    v = vec()
    levels = list(EvidenceLevel)
    for required in levels:
        niche = Niche("n", v, min_evidence=required)
        admitted = [niche.admits(occ("m", v, level)) for level in levels]
        assert admitted == sorted(admitted)          # False..False, True..True


def test_place_skips_niches_the_occupant_cannot_enter():
    nmap = gated_map()
    decision = nmap.place(occ("m", vec(), EvidenceLevel.BENCHMARKED))
    assert decision.niche_id == "open" and decision.seated


def test_route_can_demand_evidence():
    v = vec(symbolic=0.9)
    nmap = NicheMap([Niche("a", v), Niche("b", v)])
    nmap.seat("a", occ("low", v, EvidenceLevel.BENCHMARKED))
    nmap.seat("b", occ("high", v, EvidenceLevel.INDEPENDENTLY_REPRODUCED))
    task = TaskProfile(v, min_evidence=EvidenceLevel.INDEPENDENTLY_REPRODUCED)
    assert route(task, nmap).occupant.model_id == "high"
    assert route(TaskProfile(v), nmap).niche_id == "a"      # no demand: tie -> niche id
    nmap.vacate("b")
    with pytest.raises(LookupError):
        route(task, nmap)


# --- ledger -----------------------------------------------------------------

def test_ledger_chain_and_tamper_detection():
    ledger = PlacementLedger()
    assert ledger.head == GENESIS_HASH and ledger.verify()
    ledger.append("seat", "n1", "m1", "a" * 64)
    ledger.append("vacate", "n1", "m1")
    ledger.append("seat", "n2", "m2")
    assert len(ledger) == 3 and ledger.verify()
    entries = list(ledger.entries)
    assert entries[1].prev_hash == entries[0].entry_hash
    edited = entries.copy()
    edited[1] = dataclasses.replace(entries[1], model_id="someone-else")
    assert not PlacementLedger.check(tuple(edited))
    dropped = entries[:1] + entries[2:]
    assert not PlacementLedger.check(tuple(dropped))
    reordered = [entries[1], entries[0], entries[2]]
    assert not PlacementLedger.check(tuple(reordered))
    with pytest.raises(LedgerError):
        ledger.append("promote", "n1", "m1")


def test_ledger_jsonl_roundtrip_and_rejects_tampering():
    ledger = PlacementLedger()
    ledger.append("seat", "n1", "m1", "b" * 64)
    ledger.append("vacate", "n1", "m1", "b" * 64)
    text = ledger.to_jsonl()
    restored = PlacementLedger.from_jsonl(text)
    assert restored.entries == ledger.entries and restored.head == ledger.head
    with pytest.raises(LedgerError):
        PlacementLedger.from_jsonl(text.replace('"m1"', '"m9"', 1))
    with pytest.raises(LedgerError):
        PlacementLedger.from_jsonl("not json\n")
    assert PlacementLedger.from_jsonl("").entries == ()


def test_niche_map_writes_every_seat_and_vacate_to_the_ledger():
    ledger = PlacementLedger()
    nmap = gated_map(ledger=ledger)
    v = vec()
    first = occ("m1", v, EvidenceLevel.REPRODUCED)
    nmap.seat("strict", first)
    nmap.seat("strict", occ("m2", v, EvidenceLevel.REPRODUCED))      # swap = one seat entry
    nmap.vacate("strict")
    nmap.vacate("strict")                                            # empty: nothing recorded
    assert [(e.action, e.model_id) for e in ledger.entries] == [
        ("seat", "m1"), ("seat", "m2"), ("vacate", "m2"),
    ]
    assert ledger.entries[0].provenance_digest == first.provenance.digest
    assert ledger.verify()


def test_failed_seat_and_rejected_place_leave_no_ledger_entry():
    ledger = PlacementLedger()
    nmap = gated_map(ledger=ledger)
    with pytest.raises(ValueError):
        nmap.seat("strict", occ("m", vec()))
    assert len(ledger) == 0
    nmap2 = NicheMap([Niche("only", vec(), min_evidence=EvidenceLevel.REPRODUCED)], ledger=ledger)
    assert nmap2.place(occ("m", vec())).seated is False
    assert len(ledger) == 0


def test_ledger_entries_have_the_same_shape_for_every_model():
    ledger = PlacementLedger()
    nmap = NicheMap([Niche("a", vec()), Niche("b", vec())], ledger=ledger)
    nmap.seat("a", occ("any-vendor/anything", vec()))
    nmap.seat("b", occ("claude-sonnet", vec()))
    first, second = ledger.entries
    assert dataclasses.fields(first) == dataclasses.fields(second)
    assert (first.action, first.provenance_digest) == (second.action, second.provenance_digest)
