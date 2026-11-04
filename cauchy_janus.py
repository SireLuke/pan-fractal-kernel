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

V8_KEYS=("h","R","u","d","tau","chi","s","f")

def _state_tuple(state):
    """Serialize the semantic reader's V8State in canonical coordinate order."""
    return tuple(float(getattr(state,key)) for key in V8_KEYS)

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
    initial_frame=read_semantics(initial.v8_state); initial_values=np.asarray(_state_tuple(initial_frame.state))
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
            errs.append(pulse.phase_errors); state_rows.append(_state_tuple(semantic.state))
            rows.append({
                "step":k,"branch":name,"physical_time":physical_time,"scheduler_timestamp":scheduler_time,
                "v8_state":_state_tuple(semantic.state),"active_layer":pulse.active_layer,"polarity":pulse.polarity,
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
        "cauchy_initial_v8":_state_tuple(initial_frame.state),"v8_velocity":initial.v8_velocity,
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


def run_cauchy_janus_parameter_sweep(initial:CauchyJanusInitialData,*,
    fillings:Sequence[float]=(0.0,0.25,0.5,0.75,1.0),
    temperatures:Sequence[float]=(0.0,0.2,0.8),
    phase_shifts:Sequence[float]=(0.0,1.5707963267948966,3.141592653589793),
    pulse_intervals:Sequence[float]=(0.01,0.05),
    velocity_scales:Sequence[float]=(-1.0,0.0,1.0),
    steps:int=4,samples:int=100,seed:int=20261103)->dict:
    """One-factor-at-a-time sensitivity sweep around declared Cauchy initial data.

    This compact diagnostic isolates each control axis rather than claiming a
    full factorial/global sensitivity analysis. Every case runs both time
    directions and retains Gosset, Fermi, positivity, and reversal residuals.
    """
    axes={
        "filling_fraction":tuple(float(x) for x in fillings),
        "temperature":tuple(float(x) for x in temperatures),
        "phase_shift":tuple(float(x) for x in phase_shifts),
        "pulse_interval":tuple(float(x) for x in pulse_intervals),
        "velocity_scale":tuple(float(x) for x in velocity_scales),
    }
    for name,values in axes.items():
        if not values or not all(isfinite(x) for x in values):
            raise ValueError(f"{name} sweep must contain finite values")
    if any(x<0 or x>1 for x in axes["filling_fraction"]):
        raise ValueError("filling sweep values must lie in [0, 1]")
    if any(x<0 for x in axes["temperature"]):
        raise ValueError("temperature sweep values must be non-negative")
    if any(x<=0 for x in axes["pulse_interval"]):
        raise ValueError("pulse intervals must be positive")
    cases=[]
    def run_case(axis:str,value:float,case_id:str):
        kwargs={
            "timestamp":initial.timestamp,"v8_state":initial.v8_state,
            "v8_velocity":tuple(value*x for x in initial.v8_velocity) if axis=="velocity_scale" else initial.v8_velocity,
            "phases":initial.phases,"angular_frequencies":initial.angular_frequencies,
            "phase_offsets":initial.phase_offsets,
            "geometric_reference_phase":initial.geometric_reference_phase+value if axis=="phase_shift" else initial.geometric_reference_phase,
            "geometric_reference_frequency":initial.geometric_reference_frequency,
            "temperature":value if axis=="temperature" else initial.temperature,
            "filling_fraction":value if axis=="filling_fraction" else initial.filling_fraction,
            "capacity_per_state":initial.capacity_per_state,
        }
        dt=value if axis=="pulse_interval" else 0.01
        result=run_cauchy_janus_benchmark(CauchyJanusInitialData(**kwargs),
            dt=dt,steps=steps,samples=samples,seed=seed)
        summary=result["summary"]
        cases.append({"case_id":case_id,"axis":axis,"value":value,"dt":dt,
            "summary":summary})
    for axis,values in axes.items():
        for i,value in enumerate(values):
            run_case(axis,value,f"{axis}-{i}")
    return {
        "metadata":{"method":"one_factor_at_a_time","case_count":len(cases),
            "steps_per_branch":steps,"samples":samples,"seed":seed,
            "geometry":"gosset_4_21_e8_root_polytope",
            "scope":"sensitivity diagnostic, not exhaustive factorial analysis"},
        "cases":tuple(cases),
        "summary":{
            "all_gosset_boundary":all(c["summary"]["gosset_boundary_only"] for c in cases),
            "all_boundaries_positive":all(c["summary"]["all_radial_boundaries_finite_positive"] for c in cases),
            "all_fermi_bounds_valid":all(c["summary"]["fermi_occupancy_within_floor_ceiling"] for c in cases),
            "maximum_particle_number_residual":max(c["summary"]["maximum_particle_number_residual"] for c in cases),
            "maximum_particle_hole_capacity_residual":max(c["summary"]["maximum_particle_hole_capacity_residual"] for c in cases),
            "maximum_phase_reversal_residual":max(c["summary"]["maximum_phase_time_reversal_residual"] for c in cases),
            "maximum_v8_reversal_residual":max(c["summary"]["maximum_v8_time_reversal_residual"] for c in cases),
        },
    }
