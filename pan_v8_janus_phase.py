"""Experimental integration of Janus Hydra semantics with eight phase channels.

This couples existing computational projections; it is not a physical field solver.
Timestamps and the geometric reference phase are supplied by the caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite
from typing import Mapping, Sequence

from hydra_semantic_reader import HydraSemanticFrame, read_semantics
from pan_v8_phase_lock import PhaseLockState, fermi_occupancy, wrap_phase

V8Source = object


@dataclass(frozen=True)
class JanusPulseFrame:
    """One auditable alternating pulse and its per-channel diagnostics."""
    timestamp: float
    pulse_index: int
    active_layer: str
    polarity: int
    phase_errors: tuple[float, ...]
    uhfe_channels: tuple[float, ...]
    udfe_channels: tuple[float, ...]
    pulse_channels: tuple[float, ...]
    fermi_occupancy: tuple[float, ...]
    fermi_holes: tuple[float, ...]


class JanusPhaseCoupler:
    """Alternate UHFE/UDFE projections under an explicit eight-channel phase lock.

    Pulse index 0 activates UHFE; index 1 activates UDFE, then the pattern repeats.
    Fermi occupancy is a declared numerical diagnostic over per-channel energy
    differences, not a claim that the semantic layers are physical fermion seas.
    """

    def __init__(
        self,
        *,
        timestamp: float,
        phases: Sequence[float],
        angular_frequencies: Sequence[float],
        offsets: Sequence[float] = (0.0,) * 8,
        temperature: float = 1.0,
        chemical_potential: float = 0.0,
    ) -> None:
        if not isfinite(temperature) or temperature < 0:
            raise ValueError("temperature must be finite and non-negative")
        if not isfinite(chemical_potential):
            raise ValueError("chemical_potential must be finite")
        self.temperature = float(temperature)
        self.chemical_potential = float(chemical_potential)
        self._phase_state = PhaseLockState(
            float(timestamp),
            tuple(float(x) for x in phases),
            tuple(float(x) for x in angular_frequencies),
            tuple(float(x) for x in offsets),
        )
        self._pulse_index = 0

    @property
    def pulse_index(self) -> int:
        return self._pulse_index

    def step(
        self,
        timestamp: float,
        v8_source: Mapping[str, float] | Sequence[float] | object,
        *,
        geometric_reference_phase: float = 0.0,
    ) -> JanusPulseFrame:
        """Advance one pulse; each call advances exactly one alternating layer."""
        if not isfinite(geometric_reference_phase):
            raise ValueError("geometric_reference_phase must be finite")
        next_phase = self._phase_state.advance(timestamp)
        semantic: HydraSemanticFrame = read_semantics(v8_source)  # type: ignore[arg-type]
        errors = next_phase.phase_errors(geometric_reference_phase)

        uhfe = tuple(float(x) for x in semantic.uhfe_channels)
        udfe = tuple(float(x) for x in semantic.udfe_channels)
        is_formation = self._pulse_index % 2 == 0
        layer = "UHFE" if is_formation else "UDFE"
        polarity = 1 if is_formation else -1
        active = uhfe if is_formation else udfe
        pulse = tuple(polarity * value * cos(error) for value, error in zip(active, errors))

        # Explicit diagnostic mapping: ΔE_i = UDFE_i - UHFE_i.
        # n_i uses the conventional Fermi-Dirac logistic; holes are its complement.
        occupancy = tuple(
            fermi_occupancy(ud - uh, self.chemical_potential, self.temperature)
            for uh, ud in zip(uhfe, udfe)
        )
        holes = tuple(1.0 - value for value in occupancy)

        # Commit temporal/pulse state only after validation and calculations succeed.
        self._phase_state = next_phase
        frame = JanusPulseFrame(
            timestamp=next_phase.timestamp,
            pulse_index=self._pulse_index,
            active_layer=layer,
            polarity=polarity,
            phase_errors=errors,
            uhfe_channels=uhfe,
            udfe_channels=udfe,
            pulse_channels=pulse,
            fermi_occupancy=occupancy,
            fermi_holes=holes,
        )
        self._pulse_index += 1
        return frame
