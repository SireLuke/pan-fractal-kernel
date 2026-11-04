"""Bidirectional Cauchy-slice Janus benchmark on the fixed Gosset JOBF boundary.

This is a deterministic software initial-value benchmark, not a GR constraint solver.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence
import numpy as np
from hydra_semantic_reader import read_semantics
from jobf_v0_2 import JanusOctadialBreathingField, sphere_directions
from pan_v8_janus_phase import JanusPhaseCoupler
from pan_v8_phase_lock import PhaseLockState, wrap_phase

@dataclass(frozen=True)
class CauchyJanusInitialData:
    timestamp: float
    v8_state: Mapping[str,float] | Sequence[float]
    phases: tuple[float,...]
    angular_frequencies: tuple[float,...]
    v8_velocity: tuple[float,...]=(0.0,)*8
    phase_offsets: tuple[float,...]=(0.0,)*8
    geometric_reference_phase: float=0.0
    geometric_reference_frequency: float=0.0
    temperature: float=0.25
    filling_fraction: float=0.5
    capacity_per_state: float=1.0
    def __post_init__(self):
        if not isfinite(self.timestamp): raise ValueError("timestamp must be finite")
        for name in ("phases","angular_frequencies","v8_velocity","phase_offsets"):
            values=tuple(float(x) for x in getattr(self,name))
            if len(values)!=8 or not all(isfinite(x) for x in values): raise ValueError(f"{name} must contain 8 finite values")
            object.__setattr__(self,name,values)
        for name in ("geometric_reference_phase","geometric_reference_frequency","temperature","filling_fraction","capacity_per_state"):
            value=getattr(self,name)
            if not isfinite(value): raise ValueError(f"{name} must be finite")
        if self.temperature<0 or not 0<=self.filling_fraction<=1 or self.capacity_per_state<=0:
            raise ValueError("invalid temperature, filling fraction, or capacity")

def run_cauchy_janus_benchmark(initial:CauchyJanusInitialData,*,dt:float=0.01,
    steps:int=8,samples:int=256,seed:int=20261103)->dict:
    if not isfinite(dt) or dt<=0: raise ValueError("dt must be finite and positive")
    if isinstance(steps,bool) or not isinstance(steps,int) or steps<1: raise ValueError("steps must be positive integer")
    if isinstance(samples,bool) or not isinstance(samples,int) or samples<100: raise ValueError("samples must be integer >= 100")
    initial_frame=read_semantics(initial.v8_state); initial_values=np.asarray(initial_frame.state.as_tuple())
    velocity=np.asarray(initial.v8_velocity); directions=sphere_directions(samples,seed)
    target=initial.filling_fraction*8*initial.capacity_per_state
    model=JanusOctadialBreathingField(dt=dt); model.base=initial_values.copy()
    model.state_amp=np.zeros(8); model.h_base=initial_frame.uhfe_channels.copy(); model.d_base=initial_frame.udfe_channels.copy()
    branches={}; phase_errors={}; states={}
    for name,sign,pulse_start in (("forward",1.0,0),("backward",-1.0,1)):
        coupler=JanusPhaseCoupler(timestamp=initial.timestamp,phases=initial.phases,
            angular_frequencies=tuple(sign*x for x in initial.angular_frequencies),offsets=initial.phase_offsets,
            temperature=initial.temperature,fermi_filling_fraction=initial.filling_fraction,
            fermi_capacity_per_state=initial.capacity_per_state,initial_pulse_index=pulse_start)
        rows=[]; errs=[]; state_rows=[]
        for k in range(steps+1):
            elapsed=k*dt; signed=sign*elapsed; physical_time=initial.timestamp+signed
            scheduler_time=initial.timestamp+elapsed
            values=initial_values+signed*velocity
            mapping=dict(zip(("h","R","u","d","tau","chi","s","f"),map(float,values)))
            semantic=read_semantics(mapping)
            model.base=values.copy()
            ref=initial.geometric_reference_phase+sign*initial.geometric_reference_frequency*elapsed
            pulse=coupler.step(scheduler_time,mapping,geometric_reference_phase=ref)
            radii,base,exponent,diag=model.boundary(directions,signed,external_channel_drive=pulse.pulse_channels)
            errs.append(pulse.phase_errors); state_rows.append(semantic.state.as_tuple())
            rows.append({
                "step":k,"branch":name,"physical_time":physical_time,"scheduler_timestamp":scheduler_time,
                "v8_state":semantic.state.as_tuple(),"active_layer":pulse.active_layer,"polarity":pulse.polarity,
                "pulse_index":pulse.pulse_index,"phase_errors":pulse.phase_errors,
                "phase_error_rms":float(np.sqrt(np.mean(np.square(pulse.phase_errors)))),
                "effective_channel_drive":pulse.pulse_channels,
                "fermi_occupancy":pulse.fermi_occupancy,"fermi_holes":pulse.fermi_holes,
                "fermi_chemical_potential":pulse.fermi_chemical_potential,
                "fermi_particle_number":pulse.fermi_particle_number,"fermi_hole_number":pulse.fermi_hole_number,
                "fermi_filling_fraction":pulse.fermi_filling_fraction,
                "fermi_capacity":pulse.fermi_capacity,"fermi_occupancy_floor":pulse.fermi_occupancy_floor,
                "fermi_occupancy_ceiling":pulse.fermi_occupancy_ceiling,
                "fermi_energy_floor":pulse.fermi_energy_floor,"fermi_energy_ceiling":pulse.fermi_energy_ceiling,
                "fermi_mode":pulse.fermi_sea_mode,"mean_radius":float(np.mean(radii)),
                "minimum_radius":float(np.min(radii)),"maximum_radius":float(np.max(radii)),
                "boundary_positive":bool(np.all(np.isfinite(radii)) and np.all(radii>0)),
                "geometry":diag["geometry"],
            })
        branches[name]=tuple(rows); phase_errors[name]=errs; states[name]=state_rows
    initial_errors=PhaseLockState(initial.timestamp,initial.phases,initial.angular_frequencies,initial.phase_offsets).phase_errors(initial.geometric_reference_phase)
    phase_res=max(abs(wrap_phase(f+b-2*i)) for fs,bs in zip(phase_errors["forward"],phase_errors["backward"]) for f,b,i in zip(fs,bs,initial_errors))
    state_res=max(abs(f+b-2*i) for fs,bs in zip(states["forward"],states["backward"]) for f,b,i in zip(fs,bs,initial_values))
    all_rows=branches["forward"]+branches["backward"]; total_capacity=8*initial.capacity_per_state
    particle_res=max(abs(r["fermi_particle_number"]-target) for r in all_rows)
    ph_res=max(abs(r["fermi_particle_number"]+r["fermi_hole_number"]-total_capacity) for r in all_rows)
    bounds=all(all(r["fermi_occupancy_floor"]-1e-12<=x<=r["fermi_occupancy_ceiling"]+1e-12 for x in r["fermi_occupancy"]) and
        all(-1e-12<=x<=r["fermi_capacity"]+1e-12 for x in r["fermi_holes"]) for r in all_rows)
    return {"metadata":{"initial_timestamp":initial.timestamp,"dt":dt,"steps_per_branch":steps,"samples":samples,"seed":seed,
        "cauchy_initial_v8":initial_frame.state.as_tuple(),"v8_velocity":initial.v8_velocity,
        "geometry":"gosset_4_21_e8_root_polytope","fermi_model":"number_conserving_effective_eight_mode_sea",
        "filling_fraction_target":initial.filling_fraction,"capacity_per_mode":initial.capacity_per_state,
        "particle_number_target":target,"occupancy_floor":0.0,"occupancy_ceiling":initial.capacity_per_state,
        "interpretation":"Software initial-value benchmark; effective V8 modes are not asserted to be physical fermion species."},
        "branches":branches,"summary":{
            "gosset_boundary_only":all(r["geometry"]=="gosset_4_21_e8_root_polytope" for r in all_rows),
            "all_radial_boundaries_finite_positive":all(r["boundary_positive"] for r in all_rows),
            "fermi_occupancy_within_floor_ceiling":bounds,
            "maximum_particle_number_residual":particle_res,"maximum_particle_hole_capacity_residual":ph_res,
            "maximum_phase_time_reversal_residual":phase_res,"maximum_v8_time_reversal_residual":state_res,
            "forward_pulse_order":tuple(r["active_layer"] for r in branches["forward"]),
            "backward_pulse_order":tuple(r["active_layer"] for r in branches["backward"]),
            "evidence_label":"software_integration_and_numerical_invariants"}}
