import pytest
from cauchy_janus import CauchyJanusInitialData, run_cauchy_janus_benchmark

def initial():
    return CauchyJanusInitialData(timestamp=100.0,
        v8_state={"h":.60,"R":.58,"u":.55,"d":.42,"tau":.62,"chi":.51,"s":.64,"f":.57},
        v8_velocity=(.01,-.006,.004,.003,-.005,.002,.006,-.004),
        phases=(.1,-.2,.3,-.4,.5,-.6,.7,-.8),
        angular_frequencies=(.7,-.4,.3,.8,-.5,.6,.2,-.9),
        phase_offsets=(0,.1,-.1,.2,-.2,.3,-.3,0),
        geometric_reference_phase=.17,geometric_reference_frequency=.11,
        temperature=.2,filling_fraction=.5)

def test_bidirectional_cauchy_janus_and_fermi_conservation():
    x=run_cauchy_janus_benchmark(initial(),dt=.02,steps=4,samples=100,seed=73)
    s=x["summary"]
    assert s["gosset_boundary_only"] and s["all_radial_boundaries_finite_positive"]
    assert s["fermi_occupancy_within_floor_ceiling"]
    assert s["maximum_particle_number_residual"]<1e-9
    assert s["maximum_particle_hole_capacity_residual"]<1e-9
    assert s["maximum_phase_time_reversal_residual"]<1e-9
    assert s["maximum_v8_time_reversal_residual"]<1e-12
    assert s["forward_pulse_order"]==("UHFE","UDFE","UHFE","UDFE","UHFE")
    assert s["backward_pulse_order"]==("UDFE","UHFE","UDFE","UHFE","UDFE")

def test_cauchy_initial_data_and_trajectory_validation():
    x=initial()
    bad=CauchyJanusInitialData(timestamp=x.timestamp,v8_state=x.v8_state,
        phases=x.phases,angular_frequencies=x.angular_frequencies,
        v8_velocity=(1,)*8)
    with pytest.raises(ValueError): run_cauchy_janus_benchmark(bad,dt=1,steps=2,samples=100)
