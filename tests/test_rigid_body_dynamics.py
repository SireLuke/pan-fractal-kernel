import math
import pytest
from rigid_body_dynamics import TorqueFreeRigidBody

@pytest.fixture
def body():
    return TorqueFreeRigidBody((1.0, 2.0, 3.0))

def test_principal_axis_equilibria(body):
    for w in ((1.,0.,0.),(0.,1.,0.),(0.,0.,1.)):
        assert body.euler_rhs(w) == (0.,0.,0.)

def test_intermediate_axis_growth_exponent(body):
    assert body.intermediate_axis_growth_rate(1.) == pytest.approx(math.sqrt(1/3))

def test_energy_and_inertial_momentum_are_conserved_numerically(body):
    states = body.simulate((.02,1.,.01), duration=12., dt=.001)
    a = body.invariants(states[0].omega_body, states[0].attitude)
    b = body.invariants(states[-1].omega_body, states[-1].attitude)
    assert b.kinetic_energy == pytest.approx(a.kinetic_energy, rel=2e-8)
    assert b.angular_momentum_norm == pytest.approx(a.angular_momentum_norm, rel=2e-8)
    assert b.angular_momentum_inertial == pytest.approx(a.angular_momentum_inertial, abs=2e-7)

def test_intermediate_axis_perturbation_grows(body):
    states = body.simulate((1e-3,1.,0.), duration=8., dt=.001)
    transverse = [math.hypot(s.omega_body[0],s.omega_body[2]) for s in states]
    assert max(transverse) > 20*transverse[0]

def test_stable_axis_perturbations_remain_bounded(body):
    for w in ((1e-3,0.,1.),(0.,1e-3,1.)):
        states = body.simulate(w, duration=4., dt=.001)
        assert max(math.hypot(s.omega_body[0],s.omega_body[1]) for s in states) < .01

def test_quaternion_normalization(body):
    states = body.simulate((.02,1.,.01), duration=2., dt=.002)
    for s in states:
        assert sum(v*v for v in s.attitude) == pytest.approx(1., abs=1e-12)

def test_validation(body):
    with pytest.raises(ValueError):
        TorqueFreeRigidBody((1.,1.,3.))
    with pytest.raises(ValueError):
        body.simulate((0.,1.,0.), duration=-1, dt=.01)
