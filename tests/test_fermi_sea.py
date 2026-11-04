import pytest
from fermi_sea import number_conserving_fermi_sea

def test_finite_temperature_fixed_particle_number_and_hole_complement():
    x=number_conserving_fermi_sea((-0.8,-0.4,-0.1,0.0,0.2,0.5,0.7,1.0),temperature=0.15,filling_fraction=0.375)
    assert x.particle_number==pytest.approx(3.0,abs=1e-9)
    assert x.hole_number==pytest.approx(5.0,abs=1e-9)
    assert x.particle_number+x.hole_number==pytest.approx(8.0)
    assert x.occupancy_floor==0 and x.occupancy_ceiling==1
    assert all(0<=n<=1 for n in x.occupations)

def test_zero_temperature_fills_lowest_energy_and_splits_degenerate_shell():
    x=number_conserving_fermi_sea((-1,-1,0,0,1,2),temperature=0,filling_fraction=.5)
    assert x.occupations==pytest.approx((1,1,.5,.5,0,0))
    assert x.particle_number==pytest.approx(3)

def test_empty_and_full_sea_are_exact_floor_and_ceiling():
    empty=number_conserving_fermi_sea((0,1,2),temperature=.2,filling_fraction=0)
    full=number_conserving_fermi_sea((0,1,2),temperature=.2,filling_fraction=1)
    assert empty.occupations==(0,0,0) and empty.hole_number==3
    assert full.occupations==(1,1,1) and full.hole_number==0

def test_custom_capacity_and_invalid_values():
    x=number_conserving_fermi_sea((0,1,2,3),temperature=.3,filling_fraction=.5,capacity_per_state=2)
    assert x.particle_number==pytest.approx(4) and x.hole_number==pytest.approx(4)
    with pytest.raises(ValueError): number_conserving_fermi_sea((),temperature=1,filling_fraction=.5)
    with pytest.raises(ValueError): number_conserving_fermi_sea((0,),temperature=-1,filling_fraction=.5)
    with pytest.raises(ValueError): number_conserving_fermi_sea((0,),temperature=1,filling_fraction=1.1)
