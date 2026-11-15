"""Feynman sensitivity analysis for the owner-defined exponential ruler.

Canonical geometry: y_n(x)=n*b**x and adjacent gap Delta y=b**x.
Auxiliary lambda scales x: B_n=n*b**(lambda*x). The integral is an
analysis functional, not a physical partition function.
"""
from dataclasses import dataclass
from math import exp,isfinite,log

@dataclass(frozen=True)
class FeynmanBarbershopResult:
    mode_count:int; scale_parameter:float; base:float; beta:float
    x_min:float; x_max:float; intervals:int
    mode_integrals:tuple[float,...]; mode_first_derivatives:tuple[float,...]; mode_second_derivatives:tuple[float,...]
    @property
    def integral(self): return sum(self.mode_integrals)
    @property
    def first_derivative(self): return sum(self.mode_first_derivatives)
    @property
    def second_derivative(self): return sum(self.mode_second_derivatives)

def barbershop_amplitude(mode:int,x:float,scale_parameter:float=1.,base:float=2.)->float:
    if isinstance(mode,bool) or not isinstance(mode,int) or mode<1: raise ValueError("mode must be a positive integer")
    if not all(isfinite(v) for v in (x,scale_parameter,base)): raise ValueError("inputs must be finite")
    if base<=0 or base==1: raise ValueError("base must be positive and different from 1")
    e=scale_parameter*x*log(base)
    if e>709: raise OverflowError("amplitude exceeds finite float range")
    if e < -745: return 0.
    return mode*exp(e)

def adjacent_line_gap(x:float,base:float=2.)->float:
    if not isfinite(x) or not isfinite(base) or base<=0 or base==1: raise ValueError("invalid x or base")
    e=x*log(base)
    if e>709: raise OverflowError("gap exceeds finite float range")
    if e < -745: return 0.
    return exp(e)

def horizontal_coordinate_for_gap(length:float,base:float=2.)->float:
    if not isfinite(length) or length<=0: raise ValueError("length must be finite and positive")
    if not isfinite(base) or base<=0 or base==1: raise ValueError("base must be positive and different from 1")
    return log(length)/log(base)

def _simpson(v:list[float],h:float)->float:
    n=len(v)-1
    if n<2 or n%2: raise ValueError("Simpson integration needs even interval count >= 2")
    return h/3*(v[0]+v[-1]+4*sum(v[1:-1:2])+2*sum(v[2:-1:2]))

def evaluate_feynman_barbershop(*,mode_count:int=8,scale_parameter:float=1.,base:float=2.,beta:float=1.,x_min:float=0.,x_max:float=1.,intervals:int=512)->FeynmanBarbershopResult:
    if isinstance(mode_count,bool) or not isinstance(mode_count,int) or mode_count<1: raise ValueError("mode_count must be a positive integer")
    if isinstance(intervals,bool) or not isinstance(intervals,int) or intervals<2 or intervals%2: raise ValueError("intervals must be even and >= 2")
    if not all(isfinite(v) for v in (scale_parameter,base,beta,x_min,x_max)): raise ValueError("parameters must be finite")
    if base<=0 or base==1 or beta<=0 or x_max<=x_min: raise ValueError("invalid base, beta or interval")
    h=(x_max-x_min)/intervals; lb=log(base); zs=[]; ds=[]; dds=[]
    for n in range(1,mode_count+1):
        z=[]; d=[]; dd=[]
        for i in range(intervals+1):
            x=x_min+i*h; B=barbershop_amplitude(n,x,scale_parameter,base); w=exp(-beta*B)
            z.append(w); d.append(-beta*lb*x*B*w); dd.append(-beta*lb*lb*x*x*B*(1-beta*B)*w)
        zs.append(_simpson(z,h)); ds.append(_simpson(d,h)); dds.append(_simpson(dd,h))
    return FeynmanBarbershopResult(mode_count,scale_parameter,base,beta,x_min,x_max,intervals,tuple(zs),tuple(ds),tuple(dds))
