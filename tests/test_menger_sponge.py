import numpy as np
import pytest

from menger_sponge import (MAX_CELLS, adjacency, audit_menger, box_counting_dimension,
                           cells_per_level, menger_cells, return_probabilities,
                           sierpinski_gasket_graph, similarity_dimension, spectral_dimension)


@pytest.mark.parametrize("d,expected", [(1, 3), (2, 8), (3, 20), (4, 48), (8, 1280), (10, 6144)])
def test_cells_per_level(d, expected):
    assert cells_per_level(d) == expected


def test_level_one_menger_sponge_matches_hand_count():
    a = audit_menger(3, 1)
    assert a["cells"] == 20 and a["expected_cells"] == 20
    # 8 corner cubes touch 3 edge cubes; 12 edge cubes touch 2 corner cubes: (8*3 + 12*2) / 2
    assert a["edges"] == 24
    assert a["degree_histogram"] == {"2": 12, "3": 8}
    assert a["connected_components"] == 1


def test_level_one_carpet_is_an_eight_cycle():
    a = audit_menger(2, 1)
    assert (a["cells"], a["edges"], a["degree_histogram"]) == (8, 8, {"2": 8})


@pytest.mark.parametrize("d,level", [(2, 3), (3, 2), (3, 3), (4, 2)])
def test_exact_counts_connectivity_and_box_dimension(d, level):
    a = audit_menger(d, level)
    assert a["cells"] == a["expected_cells"] == cells_per_level(d) ** level
    assert a["connected_components"] == 1
    assert a["box_counts"] == [cells_per_level(d) ** (level - j) for j in range(level + 1)]
    assert a["box_counting_dimension"] == pytest.approx(similarity_dimension(d), abs=1e-9)


def test_cells_are_unique_in_range_and_adjacency_is_simple():
    cells = menger_cells(3, 3)
    assert len(np.unique(cells, axis=0)) == len(cells)
    assert cells.min() == 0 and cells.max() == 3**3 - 1
    adj = adjacency(cells, 3**3)
    assert (adj != adj.T).nnz == 0
    assert adj.diagonal().sum() == 0
    assert set(np.unique(adj.data)) == {1.0}


def test_ten_dimensional_level_one_count():
    cells = menger_cells(10, 1)
    assert cells.shape == (6144, 10)
    assert similarity_dimension(10) == pytest.approx(7.9402, abs=1e-4)


def test_input_validation():
    for bad in (0, -1, 2.5):
        with pytest.raises(ValueError):
            menger_cells(bad, 1)
    with pytest.raises(ValueError):
        menger_cells(3, -1)
    with pytest.raises(ValueError):
        menger_cells(10, 5)  # 6144^5 cells
    assert MAX_CELLS > 0
    with pytest.raises(ValueError):
        box_counting_dimension(menger_cells(3, 0), 0)


@pytest.mark.parametrize("stage", [0, 1, 2, 3, 6])
def test_gasket_reference_counts(stage):
    g = sierpinski_gasket_graph(stage)
    assert g.shape[0] == (3 ** (stage + 1) + 3) // 2
    assert g.nnz // 2 == 3 ** (stage + 1)


def test_return_probability_starts_at_one_and_is_nonincreasing_on_average():
    p = return_probabilities(adjacency(menger_cells(2, 2), 9), starts=[0, 5, 17], steps=20)
    assert p[0] == 1.0 and p[1] == pytest.approx(0.5)
    assert np.all(np.diff(p[1:]) <= 1e-12)


def test_spectral_estimator_recovers_gasket_value():
    exact = 2 * np.log(3) / np.log(5)  # 1.3652
    for steps in (400, 1500):
        est = spectral_dimension(sierpinski_gasket_graph(8), steps=steps)["d_s"]
        assert est == pytest.approx(exact, abs=0.1)


def test_carpet_spectral_dimension_is_stable_and_below_similarity_dimension():
    adj = adjacency(menger_cells(2, 5), 3**5)
    est = [spectral_dimension(adj, steps=s, n_starts=8)["d_s"] for s in (1000, 2500)]
    assert all(1.6 < e < similarity_dimension(2) for e in est)
    assert abs(est[0] - est[1]) < 0.1
