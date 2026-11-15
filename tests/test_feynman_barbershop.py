import math
import pytest
from feynman_barbershop import adjacent_line_gap,barbershop_amplitude,evaluate_feynman_barbershop,horizontal_coordinate_for_gap

def test_adjacent_gap_independent_of_n():
 for x in (-1,0,.5,2):
  for n in (1,2,7,100): assert barbershop_amplitude(n+1,x)-barbershop_amplitude(n,x)==pytest.approx(2**x,rel=1e-12)
  assert adjacent_line_gap(x)==pytest.approx(2**x)

def test_origin_and_x_two():
 assert adjacent_line_gap(0)==pytest.approx(1); assert adjacent_line_gap(2)==pytest.approx(4)

def test_log_cursor():
 for L in (.01,.5,1,2.54,25.4,100): assert adjacent_line_gap(horizontal_coordinate_for_gap(L),2)==pytest.approx(L,rel=1e-12)

def test_general_base():
 for b in (1.2,2,10,math.e):
  for x in (-.5,0,1.3): assert adjacent_line_gap(x,b)==pytest.approx(b**x)

def test_first_derivative_finite_difference():
 a=dict(mode_count=5,base=2,beta=.7,x_min=0,x_max=1.3,intervals=800); l=.8; h=1e-5
 c=evaluate_feynman_barbershop(scale_parameter=l,**a); p=evaluate_feynman_barbershop(scale_parameter=l+h,**a); m=evaluate_feynman_barbershop(scale_parameter=l-h,**a)
 assert c.first_derivative==pytest.approx((p.integral-m.integral)/(2*h),rel=2e-7,abs=2e-9)

def test_second_derivative_finite_difference():
 a=dict(mode_count=4,base=2,beta=.9,x_min=0,x_max=1,intervals=800); l=.65; h=2e-5
 c=evaluate_feynman_barbershop(scale_parameter=l,**a); p=evaluate_feynman_barbershop(scale_parameter=l+h,**a); m=evaluate_feynman_barbershop(scale_parameter=l-h,**a)
 assert c.second_derivative==pytest.approx((p.first_derivative-m.first_derivative)/(2*h),rel=3e-7,abs=3e-9)

def test_eight_modes():
 r=evaluate_feynman_barbershop(mode_count=8,intervals=256)
 assert len(r.mode_integrals)==8
 assert all(math.isfinite(v) for v in (r.integral,r.first_derivative,r.second_derivative))

def test_reciprocal_base():
 for n in (1,4,9):
  for x in (-.5,0,1): assert barbershop_amplitude(n,x,base=2)*barbershop_amplitude(n,x,base=.5)==pytest.approx(n*n)

@pytest.mark.parametrize("kw",[{"mode_count":0},{"mode_count":1.5},{"beta":0},{"x_min":2,"x_max":1},{"intervals":3},{"base":1},{"base":-2},{"scale_parameter":float("nan")}])
def test_bad_inputs(kw):
 with pytest.raises(ValueError): evaluate_feynman_barbershop(**kw)
