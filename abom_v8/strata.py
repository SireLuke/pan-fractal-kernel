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
