from pathlib import Path
import re

import pytest

from abom_v8.adapters.builtins import StrataEvidencePlugin
from abom_v8.strata import (
    abom_strata_records, menger_flux_strata_record, menger_surface_strata_record,
    microtubule_interpretation_strata_record, microtubule_lattice_strata_record,
)

FORMAL = Path(__file__).resolve().parents[1] / "formal"

# Theorems that the Python tests and STRATA records rely on, per Lean file.
EXPECTED_THEOREMS = {
    "PAN/ABOM/Flux.lean": [
        "flux_identity", "flux_le_quarter", "flux_equilibrium", "flux_eq_max_iff",
        "flux_symmetric", "asymmetry_sq_le",
    ],
    "PAN/ABOM/MengerVolume.lean": [
        "cellsPerLevel_three", "menger_three_removed",
        "menger_dimension_between_two_and_three", "volNum_succ", "volDen_succ",
        "vol_le_one", "vol_level_two",
    ],
    "PAN/ABOM/MengerSurface.lean": [
        "surf_level_zero", "surf_level_one", "surf_level_two", "surf_level_three",
        "surfDen_succ", "surfNum_succ", "surf_strictly_increasing",
        "surf_exceeds_level", "volume_bounded_surface_unbounded",
    ],
    "PAN/ABOM/MicrotubuleLattice.lean": [
        "helixIndex_seam", "helixIndex_seam_invariant", "helixIndex_add",
        "v3_add_v5_eq_v8_mod_seam", "v5_add_v8_eq_v13", "fibonacci_start_numbers",
        "seam_flips_type", "even_start_keeps_type", "axial_wraps",
        "axial_rise_per_turn", "axial_offset_between_neighbours",
    ],
}


def _statuses(record):
    return {d["dimension"]: d["status"] for d in record.to_dict()["dimensions"]}


def test_no_record_is_promotion_eligible():
    for record in abom_strata_records():
        assert record.to_dict()["promotion_eligible"] is False


def test_record_ids_are_unique_and_ordered():
    ids = [r.claim_id for r in abom_strata_records()]
    assert len(ids) == len(set(ids)) == 5
    assert ids[1:] == [
        "ABOM-V8-MENGER-FLUX-001", "ABOM-V8-MENGER-SURFACE-001", "ABOM-V8-MT13-3-LATTICE-001",
        "ABOM-V8-MT-COLLECTIVE-COUPLING-001",
    ]


@pytest.mark.parametrize("factory", [menger_flux_strata_record, menger_surface_strata_record, microtubule_lattice_strata_record])
def test_arithmetic_records_pass_formal_and_leave_science_untested(factory):
    statuses = _statuses(factory())
    assert statuses["formal_verification"] == "pass"
    assert statuses["two_representations"] == "pass"
    for name in ("three_meaningful_scales", "two_independent_domains",
                 "randomized_control", "held_out_predictive_evaluation"):
        assert statuses[name] == "not_tested"
    assert factory().evidence_level == "software-smoke-test"


def test_physical_interpretation_is_separate_and_fully_untested():
    record = microtubule_interpretation_strata_record()
    assert record.evidence_level == "analogy"
    assert set(_statuses(record).values()) == {"not_tested"}
    text = " ".join(record.limitations)
    assert "400x" in text and "superradiance" in text


def test_plugin_exposes_the_new_records():
    assert StrataEvidencePlugin.create_menger_flux_record().claim_id == "ABOM-V8-MENGER-FLUX-001"
    assert len(StrataEvidencePlugin.all_records()) == 5


@pytest.mark.parametrize("relpath", sorted(EXPECTED_THEOREMS))
def test_lean_files_declare_the_referenced_theorems(relpath):
    source = (FORMAL / relpath).read_text()
    declared = set(re.findall(r"^(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)", source, re.M))
    missing = [name for name in EXPECTED_THEOREMS[relpath] if name not in declared]
    assert not missing, f"missing theorems in {relpath}: {missing}"


def test_lean_sources_have_no_escape_hatches():
    for path in (FORMAL / "PAN").rglob("*.lean"):
        code = re.sub(r"/-.*?-/", "", path.read_text(), flags=re.S)
        code = re.sub(r"--.*", "", code)
        for banned in ("sorry", "axiom ", "native_decide", "admit"):
            assert banned not in code, f"{banned!r} found in {path.name}"


def test_lean_library_has_a_root_module_that_imports_everything():
    root = (FORMAL / "PAN.lean").read_text()
    assert "import PAN.ABOM" in root and "import PAN.V8.Coordinates" in root
    abom = (FORMAL / "PAN" / "ABOM.lean").read_text()
    for module in ("Occupancy", "Flux", "MengerVolume", "MicrotubuleLattice"):
        assert f"import PAN.ABOM.{module}" in abom
