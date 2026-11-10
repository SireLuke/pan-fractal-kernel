import random
from fractions import Fraction
import pytest
import kac_moody_en as km
import five21_neighborhood as nb

EXPECTED_ROOT_GROWTH_E10 = [10, 29, 47, 65, 83, 101, 120, 140, 160, 180, 201, 223, 246]   # PANoRAMic.os E10_SIX_EXPERIMENTS.md


def test_cartan_determinant_is_9_minus_n_and_signature():
    for n, det in {3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0, 10: -1, 11: -2}.items():
        assert km.inertia_det(km.cartan_en(n))[3] == det
    assert km.inertia_det(km.cartan_en(8))[:3] == (8, 0, 0)
    assert km.inertia_det(km.cartan_en(9))[:3] == (8, 0, 1)
    assert km.inertia_det(km.cartan_en(10))[:3] == (9, 1, 0)
    assert km.inertia_det(km.cartan_en(11))[:3] == (10, 1, 0)


def test_matches_panoramic_gram_determinants():
    # PANoRAMic.os uses Gram = Cartan/2: det(E8)=1/256, det(E10)=-1/1024
    assert km.inertia_det(km.cartan_en(8))[3] / 2**8 == Fraction(1, 256)
    assert km.inertia_det(km.cartan_en(10))[3] / 2**10 == Fraction(-1, 1024)


def test_e9_null_root_marks_and_dual_coxeter_number():
    d = km.kernel_vector(km.cartan_en(9))
    assert d == [2, 3, 4, 6, 5, 4, 3, 2, 1]
    assert sum(d) == 30                                    # dual Coxeter number of E8


def test_e8_simple_roots_realise_the_cartan_matrix_and_theta():
    A = km.cartan_en(8)
    for i, a in enumerate(km.E8_SIMPLE2):
        for j, b in enumerate(km.E8_SIMPLE2):
            assert km.dot2(a, b) == A[i][j]
    marks = [2, 3, 4, 6, 5, 4, 3, 2]
    th = tuple(sum(m * a[k] for m, a in zip(marks, km.E8_SIMPLE2)) for k in range(8))
    assert th == km.THETA2 and tuple(km.THETA2) in nb.ROOTS2
    # affine node: a9 = -theta (+delta) has the right inner products with the finite simple roots
    a9 = tuple(-t for t in km.THETA2)
    assert [km.dot2(a9, a) for a in km.E8_SIMPLE2] == km.cartan_en(9)[8][:8]
    assert km.dot2(a9, a9) == 2


def test_kac_moody_reflection_equals_five21_affine_reflection():
    rng = random.Random(7)
    pts = list(nb.shell(1)) + [nb.shell(2)[i] for i in rng.sample(range(2160), 60)] + [(0,) * 8]
    idx = {r: i for i, r in enumerate(nb.ROOTS2)}
    for x in pts:
        for ri in rng.sample(range(240), 25):
            for k in (-2, -1, 0, 1, 2, 5):
                assert km.affine_reflection_via_roots(x, nb.ROOTS2[ri], k) == nb.affine_reflection(x, ri, k)


def test_affine_simple_reflection_s9_sends_origin_to_theta():
    (a9, n9) = km.e9_simple_roots_as_affine()[8]
    assert km.weight_reflection((0,) * 8, a9, n9) == km.THETA2
    for x in nb.shell(1)[:20]:                              # s_9 keeps the lattice and is an involution
        y = km.weight_reflection(x, a9, n9)
        assert nb.is_e8_doubled(y) and km.weight_reflection(y, a9, n9) == x


def test_e10_hyperbolic_ideal_vertex_and_inverse_diagonal():
    cls = km.delete_node_classes(10)
    assert sorted(cls.values()) == ["affine"] + ["finite"] * 9
    assert cls[10] == "affine"                              # deleting the long-arm end leaves affine E8 = E9
    assert km.is_hyperbolic(10)


def test_e11_is_not_hyperbolic_and_has_a_hyperideal_vertex():
    assert km.inertia_det(km.cartan_en(11))[:3] == (10, 1, 0)
    cls = km.delete_node_classes(11)
    assert cls[11] == "indefinite"                          # deleting the end leaves E10
    assert not km.is_hyperbolic(11)
    assert km.is_hyperbolic(10) and not km.is_hyperbolic(9)


def test_root_growth_replicates_panoramic_e10_counts():
    assert km.root_growth(10, 12) == EXPECTED_ROOT_GROWTH_E10


def test_e8_root_growth_saturates_at_240():
    c = km.root_growth(8, 40)
    assert c[-1] == 240 and c[-2] == 240


def test_e9_real_roots_never_saturate_and_grow_linearly():
    c = km.root_growth(9, 24)
    steps = [b - a for a, b in zip(c, c[1:])]
    assert all(x > 0 for x in steps)                        # affine: infinitely many real roots
    assert set(steps[1:]) <= {16, 17}                       # linear growth (about 16.6 per reflection depth), no saturation
    assert c[-1] > 240
