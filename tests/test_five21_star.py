import pytest
import five21_star as st


@pytest.fixture(scope="module")
def res():
    return st.audit()


def test_cell_counts_match_4_21_facet_counts(res):
    assert res["simplex_cells"] == 17280 and res["orthoplex_cells"] == 2160


def test_all_cells_are_equidistant_and_delaunay(res):
    assert res["simplex_delaunay_violations"] == (0, 0)
    assert res["orthoplex_delaunay_violations"] == (0, 0)


def test_origin_ridge_incidence_and_closure(res):
    assert res["facets_from_simplex"] == 8 * 17280 == 138_240
    assert res["facets_from_orthoplex"] == 128 * 2160 == 276_480
    assert res["distinct_origin_facets"] == 207_360
    assert res["facets_multiplicity_histogram"] == {"2": 207_360}


def test_ridge_cell_type_pairing(res):
    assert res["ridge_cell_type_pairs"] == {"orthoplex+simplex": 138_240, "orthoplex+orthoplex": 69_120}
    assert "simplex+simplex" not in res["ridge_cell_type_pairs"]


def test_translation_propagation_to_neighbouring_stars(res):
    assert res["neighbour_star_incidences_checked"] == 168_480
    assert res["neighbour_star_violations"] == 0


def test_every_ridge_of_every_origin_cell_lies_in_exactly_two_cells(res):
    assert res["ridges_in_origin_cells"] == 501_120
    assert res["ridges_not_in_exactly_two_cells"] == 0


def test_cells_tile_space_with_exact_unit_density():
    d = st.tiling_density()
    assert d["simplices_per_vertex"] == 1920 and d["orthoplices_per_vertex"] == 135
    assert d["volume_per_vertex"] == 1                    # E8 covolume: no gaps, no net overlap
