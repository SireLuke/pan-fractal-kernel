import copy, json
import numpy as np
import pytest

from gosset_421 import E8_ROOTS
from gosset_projection import project_gosset_chain
from view_ladder import (LadderError, build_ladder, gosset_coordinate_ladder, gosset_seeded_ladder,
                         seeded_3d_rows, validate_schema, extend_orthonormal)
from gosset_projection import ProjectionFrame
import five21_neighborhood as f21


def test_coordinate_ladder_matches_existing_chain_exactly():
    lad, chain = gosset_coordinate_ladder(), project_gosset_chain()
    assert lad.dimensions == (8, 4, 3, 2)
    for d in (4, 3, 2):
        assert np.array_equal(lad.stage(d).result.projected_points, chain[d].projected_points)


def test_seeded_3d_stage_is_the_existing_3d_simulation_view():
    gs = pytest.importorskip("gosset_3d_simulation")      # needs scipy + matplotlib
    lad = gosset_seeded_ladder(73)
    assert np.allclose(lad.stage(3).frame.matrix, gs.seeded_view(73).matrix, atol=1e-12)
    assert np.allclose(seeded_3d_rows(73), gs.seeded_view(73).matrix, atol=1e-12)


def test_seeded_ladder_is_nested_orthonormal_and_deterministic():
    a, b = gosset_seeded_ladder(421), gosset_seeded_ladder(421)
    assert all(s.nested_in_previous for s in a.stages)
    for s in a.stages:
        m = s.frame.matrix
        assert np.allclose(m @ m.T, np.eye(len(m)), atol=1e-12)
    assert a.to_schema() == b.to_schema()
    assert a.to_schema() != gosset_seeded_ladder(7).to_schema()


def test_8d_stage_is_lossless_rotation_and_error_is_monotone():
    for lad in (gosset_coordinate_ladder(), gosset_seeded_ladder()):
        errs = [s.result.maximum_reconstruction_error for s in lad.stages]
        assert lad.stage(8).result.is_lossless
        assert errs == sorted(errs) and errs[-1] > 0


def test_roots_are_isotropic_so_every_k_frame_retains_k_over_8():
    # E8 roots form a spherical 7-design: sum x x^T = 60 I, for ANY orthonormal frame.
    for lad in (gosset_coordinate_ladder(), gosset_seeded_ladder(5)):
        for s in lad.to_schema()["stages"]:
            assert s["energy_retained_fraction"] == pytest.approx(s["dimension"] / 8, abs=1e-12)


def test_schema_validates_roundtrips_json_and_detects_tampering():
    doc = json.loads(json.dumps(gosset_seeded_ladder().to_schema()))
    validate_schema(doc)
    bad = copy.deepcopy(doc); bad["stages"][1]["energy_retained_fraction"] = 0.9
    with pytest.raises(LadderError): validate_schema(bad)
    bad = copy.deepcopy(doc); bad["schema"] = "other"
    with pytest.raises(LadderError): validate_schema(bad)


def test_builder_rejects_bad_input():
    pts = np.eye(3)
    f2 = ProjectionFrame(np.eye(3)[:2], "a"); f3 = ProjectionFrame(np.eye(3), "b")
    with pytest.raises(LadderError): build_ladder("x", "g", pts, [0, 1, 2], "i", [f2, f3])   # increasing dims
    with pytest.raises(LadderError): build_ladder("x", "g", pts, [0, 1], "i", [f3])            # id count
    with pytest.raises(LadderError): build_ladder("x", "g", np.array([[np.nan, 0, 0]]), [0], "i", [f3])


def test_nonnested_frames_are_flagged_not_hidden():
    pts = np.random.default_rng(0).normal(size=(5, 3))
    f_a = ProjectionFrame(np.eye(3)[:2], "xy"); f_b = ProjectionFrame(np.eye(3)[1:], "yz")
    lad = build_ladder("x", "g", pts, list(range(5)), "i", [ProjectionFrame(np.eye(3), "id"), f_a])
    assert lad.stage(2).nested_in_previous
    lad2 = build_ladder("x", "g", pts, list(range(5)), "i", [f_a, ProjectionFrame(np.eye(3)[:1] , "x")])
    assert lad2.stage(1).nested_in_previous
    lad3 = build_ladder("x", "g", pts, list(range(5)), "i",
                        [ProjectionFrame(np.array([[1, 0, 0], [0, 1, 0.0]]), "a"),
                         ProjectionFrame(np.array([[0, 0, 1.0]]), "c")])
    assert not lad3.stage(1).nested_in_previous


# ------------------------------------------------------------------ 5_21 / affine E8 ("E9")

def test_shell_counts_match_e8_theta_series():
    for n, count in f21.THETA_COUNTS.items():
        s = f21.shell(n)
        assert len(s) == count == len(set(s))
        assert all(f21.is_e8_doubled(v) and f21.norm2(v) == 2 * n for v in s)


def test_lattice_membership_and_neighbors_are_exact():
    assert not f21.is_e8_doubled((1, 1, 1, 1, 1, 1, 1, 0))
    assert not f21.is_e8_doubled((2, 0, 0, 0, 0, 0, 0, 0))     # (1,0,..): odd sum
    assert f21.is_e8_doubled((2, 2, 0, 0, 0, 0, 0, 0))
    nb = f21.neighbors((0,) * 8)
    assert len(set(nb)) == 240 and set(nb) == set(f21.ROOTS2)
    c = f21.ROOTS2[17]
    shared = set(f21.neighbors((0,) * 8)) & set(f21.neighbors(c))
    assert len(shared) == 56                                    # documented 5_21 invariant


def test_affine_reflections_are_involutions_that_preserve_the_lattice():
    rng = np.random.default_rng(3)
    pts = [f21.shell(2)[i] for i in rng.integers(0, 2160, 20)]
    for p in pts:
        for ri in (0, 100, 239):
            for k in (-2, 0, 1, 3):
                q = f21.affine_reflection(p, ri, k)
                assert f21.is_e8_doubled(q)
                assert f21.affine_reflection(q, ri, k) == p


def test_affine_reflection_moves_origin_to_a_root_and_preserves_distances():
    for ri in (0, 5, 200):
        assert f21.affine_reflection((0,) * 8, ri, 1) == f21.ROOTS2[ri]   # origin -> alpha
    a, b = f21.shell(1)[3], f21.shell(2)[11]
    d = lambda u, v: f21.norm2(tuple(x - y for x, y in zip(u, v)))
    ra, rb = f21.affine_reflection(a, 9, 2), f21.affine_reflection(b, 9, 2)
    assert d(ra, rb) == d(a, b)


def test_k0_reflection_fixes_the_origin_shell_structure():
    for ri in (0, 77):
        s1 = set(f21.shell(1))
        assert {f21.affine_reflection(v, ri, 0) for v in s1} == s1       # finite Weyl group


def test_five21_patch_ladders_have_sound_schemas():
    for kind in ("coordinate", "seeded"):
        lad = f21.five21_ladder(1, kind)
        doc = lad.to_schema(); validate_schema(doc)
        assert doc["source"]["point_count"] == 241
        assert lad.stage(8).result.is_lossless
        assert [s["dimension"] for s in doc["stages"]] == [8, 4, 3, 2]
    assert f21.five21_ladder(2).to_schema()["source"]["point_count"] == 241 + 2160
    with pytest.raises(ValueError): f21.five21_ladder(1, "nope")
    with pytest.raises(ValueError): f21.patch(4)


def test_five21_origin_shell_inherits_gosset_view():
    lad = f21.five21_ladder(1, "seeded")
    gl = gosset_seeded_ladder(421)
    assert np.allclose(lad.stage(3).result.projected_points[1:], gl.stage(3).result.projected_points[
        [list(E8_ROOTS).index(tuple(v / 2.0 for v in r)) for r in f21.shell(1)]], atol=1e-12)
    assert np.allclose(lad.stage(3).result.projected_points[0], 0.0)
