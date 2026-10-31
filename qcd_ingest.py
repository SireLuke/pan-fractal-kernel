"""CSV ingestion and explicit V8 hand-off for QCD coupling benchmarks.

Physical observables remain in physical units. No automatic normalization or
physical-to-V8 interpretation is performed.
"""
from __future__ import annotations
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Any
from qcd_reference import alpha_s_one_loop
from hydra_semantic_reader import read_semantics, V8_KEYS, HydraSemanticFrame

REQUIRED = {"mu_GeV", "alpha_s", "uncertainty", "source", "observable", "scheme", "nf"}


@dataclass(frozen=True)
class QCDMeasurement:
    mu_gev: float
    alpha_s: float
    uncertainty: float
    source: str
    observable: str
    scheme: str
    nf: int
    metadata: dict[str, str]


def _positive(value, field):
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{field} must be finite and positive")
    return number


def load_alpha_s_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = REQUIRED - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        rows = []
        for line, row in enumerate(reader, start=2):
            try:
                nf = int(row["nf"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"line {line}: nf must be an integer") from exc
            if nf < 1:
                raise ValueError(f"line {line}: nf must be positive")
            for key in ("source", "observable", "scheme"):
                if not row[key] or not row[key].strip():
                    raise ValueError(f"line {line}: {key} is required")
            rows.append(QCDMeasurement(
                _positive(row["mu_GeV"], f"line {line} mu_GeV"),
                _positive(row["alpha_s"], f"line {line} alpha_s"),
                _positive(row["uncertainty"], f"line {line} uncertainty"),
                row["source"].strip(), row["observable"].strip(),
                row["scheme"].strip(), nf,
                {k: v for k, v in row.items() if k not in REQUIRED and v not in (None, "")},
            ))
    if not rows:
        raise ValueError("QCD CSV contains no measurements")
    return rows


def compare_one_loop(measurements, *, lambda_qcd_gev, nc=3):
    if not measurements:
        raise ValueError("At least one measurement is required")
    output = []
    for item in measurements:
        prediction = alpha_s_one_loop(
            item.mu_gev, lambda_qcd_gev, nc=nc, nf=item.nf
        )
        residual = item.alpha_s - prediction
        output.append({
            "mu_GeV": item.mu_gev, "alpha_s_measured": item.alpha_s,
            "uncertainty": item.uncertainty, "alpha_s_one_loop": prediction,
            "residual": residual, "pull": residual / item.uncertainty,
            "source": item.source, "observable": item.observable,
            "scheme": item.scheme, "nf": item.nf, "metadata": dict(item.metadata),
        })
    return output


def calibrated_v8_frame(coordinate_values: Mapping[str, float], *,
                        source_id: str, calibration_id: str) -> tuple[HydraSemanticFrame, dict[str, str]]:
    """Only explicitly calibrated eight-coordinate mappings enter the V8 reader."""
    if set(coordinate_values) != set(V8_KEYS):
        raise ValueError(f"coordinate_values must contain exactly {V8_KEYS}")
    if not source_id.strip() or not calibration_id.strip():
        raise ValueError("source_id and calibration_id are required")
    frame = read_semantics(coordinate_values)
    return frame, {
        "source_id": source_id, "calibration_id": calibration_id,
        "mapping_status": "explicit_calibration_supplied_by_caller",
        "physical_claim": "none; V8 coordinates are engineering proxies",
    }
