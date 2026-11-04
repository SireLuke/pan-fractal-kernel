"""Finite number-conserving Fermi sea for effective PAN channels."""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, isfinite
from typing import Sequence

@dataclass(frozen=True)
class FermiSeaFrame:
    energies: tuple[float, ...]
    occupations: tuple[float, ...]
    holes: tuple[float, ...]
    chemical_potential: float | None
    temperature: float
    filling_target: float
    filling_fraction: float
    particle_number: float
    hole_number: float
    capacity_per_state: float
    occupancy_floor: float
    occupancy_ceiling: float
    energy_floor: float
    energy_ceiling: float

def _occupation(energy: float, mu: float, temperature: float, capacity: float) -> float:
    z=(energy-mu)/temperature
    if z >= 0.0:
        e=exp(-z)
        return capacity*e/(1.0+e)
    e=exp(z)
    return capacity/(1.0+e)

def number_conserving_fermi_sea(
    energies: Sequence[float], *, temperature: float, filling_fraction: float,
    capacity_per_state: float=1.0, tolerance: float=1e-12,
) -> FermiSeaFrame:
    """Solve finite-mode Fermi filling at fixed nu; holes complete each mode's capacity.

    At T=0 the lowest-energy modes fill first; a degenerate Fermi shell shares
    fractional occupancy uniformly. Effective modes are numerical channels,
    not an assertion that V8 coordinates are physical fermion species.
    """
    e=tuple(float(x) for x in energies)
    if not e or not all(isfinite(x) for x in e): raise ValueError("energies must be non-empty and finite")
    if not isfinite(temperature) or temperature<0: raise ValueError("temperature must be finite and non-negative")
    if not isfinite(filling_fraction) or not 0<=filling_fraction<=1: raise ValueError("filling_fraction must lie in [0, 1]")
    if not isfinite(capacity_per_state) or capacity_per_state<=0: raise ValueError("capacity_per_state must be finite and positive")
    if not isfinite(tolerance) or tolerance<=0: raise ValueError("tolerance must be finite and positive")
    cap=float(capacity_per_state); n=len(e); total=cap*n; target=filling_fraction*total
    occ=[0.0]*n; mu=None
    if filling_fraction==1.0:
        occ=[cap]*n
    elif filling_fraction==0.0:
        pass
    elif temperature==0.0:
        ordered=sorted((energy,i) for i,energy in enumerate(e))
        groups=[]
        for energy,i in ordered:
            if not groups or groups[-1][0]!=energy: groups.append([energy,[]])
            groups[-1][1].append(i)
        remaining=target
        for gi,(energy,indices) in enumerate(groups):
            group_cap=cap*len(indices)
            if remaining>=group_cap-tolerance:
                for i in indices: occ[i]=cap
                remaining=max(0.0,remaining-group_cap)
                if remaining<=tolerance:
                    mu=(energy+groups[gi+1][0])*0.5 if gi+1<len(groups) else energy
                    break
            else:
                share=max(0.0,remaining/len(indices))
                for i in indices: occ[i]=share
                mu=energy; remaining=0.0; break
        if abs(sum(occ)-target)>max(1e-10,tolerance*total*8):
            raise ArithmeticError("zero-temperature shell filling failed particle conservation")
    else:
        lo=min(e)-(max(e)-min(e)+64*temperature+1.0)
        hi=max(e)+(max(e)-min(e)+64*temperature+1.0)
        for _ in range(256):
            mid=(lo+hi)*0.5
            count=sum(_occupation(x,mid,temperature,cap) for x in e)
            if count<target: lo=mid
            else: hi=mid
            if hi-lo<=tolerance*max(1.0,abs(mid)): break
        mu=(lo+hi)*0.5
        occ=[_occupation(x,mu,temperature,cap) for x in e]
    holes=[cap-x for x in occ]
    particles=sum(occ); vacancies=sum(holes)
    tol=max(1e-10,tolerance*total*8)
    if abs(particles-target)>tol: raise ArithmeticError("Fermi solver failed particle-number conservation")
    if abs(particles+vacancies-total)>tol: raise ArithmeticError("particle-hole capacity identity failed")
    if any(x < -tolerance or x > cap+tolerance for x in occ): raise ArithmeticError("occupancy escaped floor/ceiling")
    return FermiSeaFrame(e,tuple(occ),tuple(holes),mu,float(temperature),target,
        particles/total,particles,vacancies,cap,0.0,cap,min(e),max(e))
