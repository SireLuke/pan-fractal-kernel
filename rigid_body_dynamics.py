"""Torque-free asymmetric rigid-body dynamics and attitude integration.

Project attribution: Lucas Thouvenell (@SireLuke).
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Iterable

Vector3 = tuple[float, float, float]
Quaternion = tuple[float, float, float, float]


def _finite3(values: Iterable[float], name: str) -> Vector3:
    out = tuple(float(v) for v in values)
    if len(out) != 3 or not all(math.isfinite(v) for v in out):
        raise ValueError(f"{name} must contain exactly three finite values")
    return out  # type: ignore[return-value]


def _qmul(a: Quaternion, b: Quaternion) -> Quaternion:
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw*bw-ax*bx-ay*by-az*bz, aw*bx+ax*bw+ay*bz-az*by,
            aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw)


def _qnormalize(q: Quaternion) -> Quaternion:
    norm = math.sqrt(sum(v*v for v in q))
    if not math.isfinite(norm) or norm == 0:
        raise ArithmeticError("invalid attitude quaternion")
    return tuple(v/norm for v in q)  # type: ignore[return-value]


def _rotate(q: Quaternion, v: Vector3) -> Vector3:
    p = _qmul(_qmul(q, (0.0, *v)), (q[0], -q[1], -q[2], -q[3]))
    return (p[1], p[2], p[3])


@dataclass(frozen=True)
class RigidBodyState:
    time: float
    omega_body: Vector3
    attitude: Quaternion


@dataclass(frozen=True)
class InvariantReport:
    kinetic_energy: float
    angular_momentum_body: Vector3
    angular_momentum_inertial: Vector3
    angular_momentum_norm: float


@dataclass(frozen=True)
class TorqueFreeRigidBody:
    """Principal-axis rigid body with 0 < I1 < I2 < I3."""
    moments: Vector3

    def __post_init__(self):
        moments = _finite3(self.moments, "moments")
        if not (0 < moments[0] < moments[1] < moments[2]):
            raise ValueError("principal moments must satisfy 0 < I1 < I2 < I3")

    def euler_rhs(self, omega: Vector3) -> Vector3:
        w1, w2, w3 = _finite3(omega, "omega")
        i1, i2, i3 = self.moments
        return (((i2-i3)/i1)*w2*w3, ((i3-i1)/i2)*w3*w1,
                ((i1-i2)/i3)*w1*w2)

    def energy(self, omega: Vector3) -> float:
        return 0.5 * sum(i*w*w for i, w in zip(self.moments, _finite3(omega, "omega")))

    def momentum_body(self, omega: Vector3) -> Vector3:
        return tuple(i*w for i, w in zip(self.moments, _finite3(omega, "omega")))  # type: ignore[return-value]

    def invariants(self, omega: Vector3, attitude: Quaternion = (1.,0.,0.,0.)) -> InvariantReport:
        q = _qnormalize(tuple(float(v) for v in attitude))  # type: ignore[arg-type]
        body_l = self.momentum_body(omega)
        world_l = _rotate(q, body_l)
        return InvariantReport(self.energy(omega), body_l, world_l,
                               math.sqrt(sum(v*v for v in body_l)))

    def intermediate_axis_growth_rate(self, spin_rate: float) -> float:
        spin_rate = float(spin_rate)
        if not math.isfinite(spin_rate):
            raise ValueError("spin_rate must be finite")
        i1, i2, i3 = self.moments
        return abs(spin_rate)*math.sqrt((i2-i1)*(i3-i2)/(i1*i3))

    def simulate(self, omega0: Vector3, *, duration: float, dt: float,
                 attitude0: Quaternion = (1.,0.,0.,0.)) -> tuple[RigidBodyState, ...]:
        """RK4 integration of Euler equations and qdot = q*(0,omega)/2."""
        omega0 = _finite3(omega0, "omega0")
        duration, dt = float(duration), float(dt)
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("duration must be finite and positive")
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive")
        q0 = _qnormalize(tuple(float(v) for v in attitude0))  # type: ignore[arg-type]
        y = (*omega0, *q0)
        t = 0.0
        result = [RigidBodyState(t, omega0, q0)]

        def rhs(s):
            w = s[:3]
            q = s[3:]
            dw = self.euler_rhs(w)
            dq = tuple(0.5*v for v in _qmul(q, (0., *w)))
            return (*dw, *dq)

        steps = math.ceil(duration/dt)
        for _ in range(steps):
            h = min(dt, duration-t)
            k1 = rhs(y)
            k2 = rhs(tuple(a+h*b/2 for a,b in zip(y,k1)))
            k3 = rhs(tuple(a+h*b/2 for a,b in zip(y,k2)))
            k4 = rhs(tuple(a+h*b for a,b in zip(y,k3)))
            y = tuple(a+h*(b+2*c+2*d+e)/6
                      for a,b,c,d,e in zip(y,k1,k2,k3,k4))
            omega = (y[0],y[1],y[2])
            q = _qnormalize((y[3],y[4],y[5],y[6]))
            y = (*omega,*q)
            t += h
            result.append(RigidBodyState(t,omega,q))
        return tuple(result)
