"""STRATA v0.1 evidence record for the ABOM lemniscate geometry experiment.

This is a protocol adapter, not a replacement for the authoritative STRATA
protocol and runner maintained in PANoRAMic.os.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Status = Literal["pass", "fail", "inconclusive", "not_tested"]


@dataclass(frozen=True, slots=True)
class StrataDimension:
    dimension: str
    status: Status
    detail: str


@dataclass(frozen=True, slots=True)
class StrataEvidenceRecord:
    protocol: str
    claim_id: str
    hypothesis: str
    evidence_level: str
    seed: int
    dimensions: tuple[StrataDimension, ...]
    limitations: tuple[str, ...]

    def validate(self) -> "StrataEvidenceRecord":
        names = [item.dimension for item in self.dimensions]
        if len(names) != len(set(names)):
            raise ValueError("STRATA dimension names must be unique")
        if any(item.status not in {"pass", "fail", "inconclusive", "not_tested"}
               for item in self.dimensions):
            raise ValueError("invalid STRATA status")
        if self.evidence_level not in {
            "analogy", "reproducible-domain-pattern", "scale-persistent-pattern",
            "cross-domain-candidate", "predictive-candidate",
            "candidate-organizing-principle", "software-smoke-test",
        }:
            raise ValueError("unknown STRATA evidence level")
        return self

    def promotion_eligible(self) -> bool:
        """Conservative gate for scale-persistent/cross-domain promotion."""
        self.validate()
        required = {
            "three_meaningful_scales",
            "two_independent_domains",
            "two_representations",
            "observer_implementation_checks",
            "randomized_control",
            "structure_preserving_control",
            "held_out_predictive_evaluation",
        }
        indexed = {item.dimension: item.status for item in self.dimensions}
        return required.issubset(indexed) and all(
            indexed[name] == "pass" for name in required
        )

    def to_dict(self) -> dict:
        self.validate()
        return {
            "protocol": self.protocol,
            "claim_id": self.claim_id,
            "hypothesis": self.hypothesis,
            "evidence_level": self.evidence_level,
            "seed": self.seed,
            "dimensions": [asdict(item) for item in self.dimensions],
            "limitations": list(self.limitations),
            "promotion_eligible": self.promotion_eligible(),
        }


def lemniscate_strata_record(seed: int = 20261115) -> StrataEvidenceRecord:
    """Record what the geometry-only comparison actually tests."""
    return StrataEvidenceRecord(
        protocol="STRATA-0.1",
        claim_id="ABOM-V8-LEMNI-COMPARE-001",
        hypothesis=(
            "Gerono and Bernoulli sampled curves can be compared reproducibly "
            "under separately matched width, lobe-area and arc-length constraints."
        ),
        evidence_level="reproducible-domain-pattern",
        seed=seed,
        dimensions=(
            StrataDimension("three_meaningful_scales", "not_tested",
                            "401/801/1601 are numerical sampling resolutions, not three meaningful scales under STRATA."),
            StrataDimension("two_independent_domains", "not_tested",
                            "Only analytic planar curve families are compared."),
            StrataDimension("two_representations", "pass",
                            "Analytic parameterizations and sampled polylines."),
            StrataDimension("observer_implementation_checks", "not_tested",
                            "Independent implementation not yet supplied."),
            StrataDimension("randomized_control", "not_tested",
                            "No stochastic hypothesis in this deterministic geometry comparison."),
            StrataDimension("structure_preserving_control", "not_tested",
                            "To be preregistered before invariant claims."),
            StrataDimension("held_out_predictive_evaluation", "not_tested",
                            "No predictive cross-domain claim."),
        ),
        limitations=(
            "Numerical resolution is not a substitute for meaningful physical scales.",
            "Only planar analytic curve families are included.",
            "Polygonal areas and arc lengths are discretization-dependent estimates.",
            "Discrete curvature is a resolution-dependent proxy.",
            "No physical transport law, universal invariant or cross-domain equivalence is established.",
        ),
    )


_NOT_TESTED_REQUIRED = (
    ("two_independent_domains", "Only one arithmetic construction is involved."),
    ("observer_implementation_checks", "Independent implementation not yet supplied."),
    ("randomized_control", "No stochastic hypothesis; the claims are deterministic identities."),
    ("structure_preserving_control", "To be preregistered before invariant claims."),
    ("held_out_predictive_evaluation", "No predictive claim."),
)


def _arithmetic_dimensions(scales_detail: str, representations_detail: str,
                           formal_detail: str) -> tuple[StrataDimension, ...]:
    return (
        StrataDimension("three_meaningful_scales", "not_tested", scales_detail),
        StrataDimension("two_representations", "pass", representations_detail),
        *(StrataDimension(name, "not_tested", detail)
          for name, detail in _NOT_TESTED_REQUIRED),
        StrataDimension("formal_verification", "pass", formal_detail),
    )


def menger_flux_strata_record(seed: int = 20261115) -> StrataEvidenceRecord:
    """Exact Menger volume and two-state flux identities (arithmetic, not physics)."""
    return StrataEvidenceRecord(
        protocol="STRATA-0.1",
        claim_id="ABOM-V8-MENGER-FLUX-001",
        hypothesis=(
            "The level-n Menger volume fraction equals (20/27)^n and the two-state "
            "flux N(1-N) equals (1-delta^2)/4, with maximum 1/4 exactly at N = 1/2."
        ),
        evidence_level="software-smoke-test",
        seed=seed,
        dimensions=_arithmetic_dimensions(
            "Menger levels are combinatorial counts, not physical scales.",
            "Floating-point Python implementation and exact Lean statements over Int/Nat.",
            "formal/PAN/ABOM/Flux.lean and formal/PAN/ABOM/MengerVolume.lean.",
        ),
        limitations=(
            "Exact arithmetic identities only; no physical flow, energy or transport is claimed.",
            "The flux is the Bernoulli variance of a two-state occupancy.",
            "Lean statements use integer counts a and b with N = a/(a+b), not real-valued Fermi occupancy.",
        ),
    )


def menger_surface_strata_record(seed: int = 20261115) -> StrataEvidenceRecord:
    """Exact Menger surface-area counts (arithmetic, not physics)."""
    return StrataEvidenceRecord(
        protocol="STRATA-0.1",
        claim_id="ABOM-V8-MENGER-SURFACE-001",
        hypothesis=(
            "The level-n Menger sponge has 2*20^n + 4*8^n exposed cell faces, so its "
            "surface area is 2*(20/9)^n + 4*(8/9)^n: it increases with n and exceeds n, "
            "while the volume fraction (20/27)^n stays at most 1."
        ),
        evidence_level="software-smoke-test",
        seed=seed,
        dimensions=_arithmetic_dimensions(
            "Menger levels are combinatorial counts, not physical scales.",
            "Closed form and an independent face count from the cell coordinates (levels 0-3), plus exact Lean statements over Nat.",
            "formal/PAN/ABOM/MengerSurface.lean.",
        ),
        limitations=(
            "Exact counting identities only; no physical surface, material or transport is claimed.",
            "Lean proves arithmetic on the closed-form integers; the match to the geometric face count is checked by the Python recount for levels 0 to 3, not proved.",
            "The unbounded-area statement is about the sequence of finite levels.",
        ),
    )


def microtubule_lattice_strata_record(seed: int = 20261115) -> StrataEvidenceRecord:
    """Internal consistency of the 13_3 lattice arithmetic (not a structural claim)."""
    return StrataEvidenceRecord(
        protocol="STRATA-0.1",
        claim_id="ABOM-V8-MT13-3-LATTICE-001",
        hypothesis=(
            "The 13_3 lattice arithmetic is internally consistent: the seam vector "
            "(13, -3), helix families 3/5/8/13 with v3+v5=v8 and v5+v8=v13 modulo the "
            "seam, and an odd-start alpha-beta seam."
        ),
        evidence_level="software-smoke-test",
        seed=seed,
        dimensions=_arithmetic_dimensions(
            "Lattice indices are integers, not measured length scales.",
            "Python lattice class and exact Lean statements over Int.",
            "formal/PAN/ABOM/MicrotubuleLattice.lean.",
        ),
        limitations=(
            "Nominal nm values (4.0 nm monomer, 10.0 nm radius) are parameters, not measurements.",
            "The 5- and 8-start helices are long lattice paths, not nearest-neighbour bonds.",
            "The Fibonacci pattern is a property of the integers 3, 5, 8, 13.",
            "No tubulin structure file or coordinates are used.",
        ),
    )


def microtubule_interpretation_strata_record(seed: int = 20261115) -> StrataEvidenceRecord:
    """The physical interpretation is deliberately kept separate and untested."""
    names = (
        "three_meaningful_scales", "two_independent_domains", "two_representations",
        "observer_implementation_checks", "randomized_control",
        "structure_preserving_control", "held_out_predictive_evaluation",
        "formal_verification",
    )
    details = {
        "formal_verification": "No formal statement exists for the physical interpretation.",
    }
    return StrataEvidenceRecord(
        protocol="STRATA-0.1",
        claim_id="ABOM-V8-MT-COLLECTIVE-COUPLING-001",
        hypothesis=(
            "The 13_3 lattice geometry bears on collective tryptophan dipole coupling "
            "in microtubules."
        ),
        evidence_level="analogy",
        seed=seed,
        dimensions=tuple(
            StrataDimension(name, "not_tested", details.get(name, "No test performed."))
            for name in names
        ),
        limitations=(
            "Brainstorm-figure dipole couplings were ~400x too large and are not used.",
            "No transition dipole, orientation factor or structure coordinates are supplied.",
            "Fluorescence-yield data are unverified and confounded by tyrosine excitation.",
            "Nothing here is evidence for superradiance or any quantum effect.",
        ),
    )


def model_routing_strata_record(seed: int = 20261115) -> StrataEvidenceRecord:
    """Determinism and metric properties of capability placement/routing (software only)."""
    return StrataEvidenceRecord(
        protocol="STRATA-0.1",
        claim_id="ABOM-V8-MODEL-ROUTING-001",
        hypothesis=(
            "Capability placement and routing are deterministic and model-agnostic: the "
            "per-axis capability distance is a metric, seating a model in an occupied niche "
            "leaves the set of occupied niches unchanged, and the routing choice depends "
            "only on capability vectors, never on model or vendor names."
        ),
        evidence_level="software-smoke-test",
        seed=seed,
        dimensions=_arithmetic_dimensions(
            "Capability axes are normalised engineering descriptors, not physical or measured scales.",
            "Floating-point Python router and exact Lean statements over Nat (per-axis distance, seating).",
            "formal/PAN/ABOM/Routing.lean.",
        ),
        limitations=(
            "Software and arithmetic only; no claim that a capability coordinate describes a model's cognition.",
            "No benchmark-to-axis calibration is shipped or validated; callers declare one and its version.",
            "Lean covers the per-axis integer distance and seating, not the float router or benchmark placement.",
            "The capability profile is separate from the canonical V8 vector; no V8 mapping is claimed.",
            "NAHT channels (r, e, p) are carried as an unassigned parameter block; no routing-to-NAHT mapping is claimed.",
        ),
    )


def provenance_strata_record(seed: int = 20261115) -> StrataEvidenceRecord:
    """Evidence gating and ledger integrity for model placements (software only)."""
    return StrataEvidenceRecord(
        protocol="STRATA-0.1",
        claim_id="ABOM-V8-PROVENANCE-001",
        hypothesis=(
            "Placement provenance is a tamper-evident, ordered evidence ladder: altering a "
            "model id, coordinates or recorded evidence invalidates its digest, evidence gates "
            "are monotone in level, and every seat or vacate is appended to a hash-chained "
            "ledger in the same shape for every model."
        ),
        evidence_level="software-smoke-test",
        seed=seed,
        dimensions=_arithmetic_dimensions(
            "Evidence levels are ordered categories, not measured quantities or a trust score.",
            "SHA-256 digest and hash chain in Python and exact Lean statements over Nat orders and lists.",
            "formal/PAN/ABOM/Provenance.lean.",
        ),
        limitations=(
            "Software only; a valid digest shows the record is unaltered, not that the benchmarks were run honestly.",
            "Attester names are caller-asserted strings; there are no signatures or identity checks.",
            "The hash chain detects edits to a copied ledger but a holder of the whole ledger can recompute it; the head hash must be anchored externally.",
            "Lean covers evidence-gate monotonicity and ledger-append length only, not SHA-256 or chain integrity.",
            "Placement evidence levels are separate from STRATA claim evidence levels.",
        ),
    )


def abom_strata_records(seed: int = 20261115) -> tuple[StrataEvidenceRecord, ...]:
    """All ABOM-V8 STRATA records in a fixed order."""
    return (
        lemniscate_strata_record(seed),
        menger_flux_strata_record(seed),
        menger_surface_strata_record(seed),
        microtubule_lattice_strata_record(seed),
        microtubule_interpretation_strata_record(seed),
        model_routing_strata_record(seed),
        provenance_strata_record(seed),
    )
