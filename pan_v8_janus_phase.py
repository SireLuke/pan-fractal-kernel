"""Experimental Janus Hydra coupling with optional number-conserving Fermi filling."""
from __future__ import annotations
from dataclasses import dataclass
from math import cos, isfinite
from typing import Mapping, Sequence
from hydra_semantic_reader import HydraSemanticFrame, read_semantics
from pan_v8_phase_lock import PhaseLockState, fermi_occupancy
try:
    from .fermi_sea import number_conserving_fermi_sea
except ImportError:
    from fermi_sea import number_conserving_fermi_sea

@dataclass(frozen=True)
class JanusPulseFrame:
    timestamp: float
    pulse_index: int
    active_layer: str
    polarity: int
    phase_errors: tuple[float,...]
    uhfe_channels: tuple[float,...]
    udfe_channels: tuple[float,...]
    pulse_channels: tuple[float,...]
    fermi_occupancy: tuple[float,...]
    fermi_holes: tuple[float,...]
    fermi_chemical_potential: float | None
    fermi_particle_number: float
    fermi_hole_number: float
    fermi_filling_fraction: float
    fermi_capacity: float
    fermi_occupancy_floor: float
    fermi_occupancy_ceiling: float
    fermi_energy_floor: float
    fermi_energy_ceiling: float
    fermi_sea_mode: str

class JanusPhaseCoupler:
    """Alternating UHFE/UDFE phase pulses with explicit effective Fermi diagnostics."""
    def __init__(self, *, timestamp: float, phases: Sequence[float],
        angular_frequencies: Sequence[float], offsets: Sequence[float]=(0.0,)*8,
        temperature: float=1.0, chemical_potential: float=0.0,
        fermi_filling_fraction: float | None=None, fermi_capacity_per_state: float=1.0,
        initial_pulse_index: int=0) -> None:
        if not isfinite(temperature) or temperature<0: raise ValueError("temperature must be finite and non-negative")
        if not isfinite(chemical_potential): raise ValueError("chemical_potential must be finite")
        if fermi_filling_fraction is not None and (not isfinite(fermi_filling_fraction) or not 0<=fermi_filling_fraction<=1):
            raise ValueError("fermi_filling_fraction must lie in [0, 1]")
        if not isfinite(fermi_capacity_per_state) or fermi_capacity_per_state<=0:
            raise ValueError("fermi_capacity_per_state must be finite and positive")
        if isinstance(initial_pulse_index,bool) or not isinstance(initial_pulse_index,int) or initial_pulse_index<0:
            raise ValueError("initial_pulse_index must be a non-negative integer")
        self.temperature=float(temperature); self.chemical_potential=float(chemical_potential)
        self.fermi_filling_fraction=fermi_filling_fraction
        self.fermi_capacity_per_state=float(fermi_capacity_per_state)
        self._phase_state=PhaseLockState(float(timestamp),tuple(float(x) for x in phases),
            tuple(float(x) for x in angular_frequencies),tuple(float(x) for x in offsets))
        self._pulse_index=initial_pulse_index
    @property
    def pulse_index(self): return self._pulse_index
    def step(self,timestamp:float,v8_source:Mapping[str,float]|Sequence[float]|object,
        *,geometric_reference_phase:float=0.0)->JanusPulseFrame:
        if not isfinite(geometric_reference_phase): raise ValueError("geometric_reference_phase must be finite")
        next_phase=self._phase_state.advance(timestamp)
        semantic:HydraSemanticFrame=read_semantics(v8_source) # type: ignore[arg-type]
        errors=next_phase.phase_errors(geometric_reference_phase)
        uh=tuple(float(x) for x in semantic.uhfe_channels); ud=tuple(float(x) for x in semantic.udfe_channels)
        formation=self._pulse_index%2==0; layer="UHFE" if formation else "UDFE"; polarity=1 if formation else -1
        active=uh if formation else ud
        pulse=tuple(polarity*x*cos(err) for x,err in zip(active,errors))
        energies=tuple(d-h for h,d in zip(uh,ud))
        if self.fermi_filling_fraction is not None:
            sea=number_conserving_fermi_sea(energies,temperature=self.temperature,
                filling_fraction=self.fermi_filling_fraction,capacity_per_state=self.fermi_capacity_per_state)
            occupancy,holes=sea.occupations,sea.holes; mu=sea.chemical_potential
            particles, vacancies, filling=sea.particle_number,sea.hole_number,sea.filling_fraction
            cap,floor,ceiling=sea.capacity_per_state,sea.occupancy_floor,sea.occupancy_ceiling
            e_floor,e_ceiling=sea.energy_floor,sea.energy_ceiling; mode="number_conserving"
        else:
            cap=self.fermi_capacity_per_state
            occupancy=tuple(fermi_occupancy(e,self.chemical_potential,self.temperature) for e in energies)
            holes=tuple(cap-x for x in occupancy); particles=sum(occupancy); vacancies=sum(holes)
            filling=particles/(len(occupancy)*cap); mu=self.chemical_potential
            floor,ceiling=0.0,cap; e_floor,e_ceiling=min(energies),max(energies)
            mode="fixed_chemical_potential"
        self._phase_state=next_phase
        frame=JanusPulseFrame(next_phase.timestamp,self._pulse_index,layer,polarity,errors,uh,ud,pulse,
            tuple(occupancy),tuple(holes),mu,particles,vacancies,filling,cap,floor,ceiling,
            e_floor,e_ceiling,mode)
        self._pulse_index+=1
        return frame
