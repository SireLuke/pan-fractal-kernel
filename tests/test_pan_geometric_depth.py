import pytest
from five21_neighborhood import ROOTS2
from pan_geometric_depth import explore, run_to_dict

def test_depth_zero_is_origin_only():
    result = explore(0)
    assert result.shell_counts() == (1,)
    assert result.visited_vertices == 1
    assert result.reached_depth == 0
    assert not result.truncated

def test_first_two_graph_shells_are_exact_and_deterministic():
    first = explore(2, max_vertices=10000)
    second = explore(2, max_vertices=10000)
    assert first.shell_counts() == (1, 240, 9120)
    assert first.visited_vertices == 9361
    assert first.shells == second.shells
    assert first.shells[1].euclidean_norm_squared_counts == ((2, 240),)
    assert len(first.shells[2].sha256) == 64

def test_graph_depth_and_euclidean_norm_are_distinct():
    result = explore(2, max_vertices=10000)
    norms = dict(result.shells[2].euclidean_norm_squared_counts)
    assert len(norms) > 1
    assert sum(norms.values()) == 9120

def test_origin_translation_equivariance():
    shift = ROOTS2[11]
    translated = explore(2, origin=shift, max_vertices=10000)
    base = explore(2, max_vertices=10000)
    assert translated.shell_counts() == base.shell_counts()
    assert translated.visited_vertices == base.visited_vertices

def test_parent_paths_reconstruct_exact_lattice_walk():
    result = explore(2, max_vertices=10000, track_paths=True)
    target = next(iter(result.parent_edges))
    path = result.path_to(target)
    assert len(path) == 1
    reached = tuple(sum(ROOTS2[i][axis] for i in path) for axis in range(8))
    assert reached == target
    target2 = next(point for point in result.parent_edges if len(result.path_to(point)) == 2)
    path2 = result.path_to(target2)
    reached2 = tuple(sum(ROOTS2[i][axis] for i in path2) for axis in range(8))
    assert reached2 == target2

def test_vertex_limit_discards_partial_shell():
    result = explore(2, max_vertices=100)
    assert result.shell_counts() == (1,)
    assert result.visited_vertices == 1
    assert result.truncated and result.stop_reason == "max_vertices"

def test_json_report_keeps_depth_metrics_separate():
    payload = run_to_dict(explore(1))
    assert payload["schema"] == "pan-geometric-depth-v1"
    assert "shortest-path" in payload["depth_metric"]
    assert "squared Euclidean norm" in payload["euclidean_norm_metric"]
    assert payload["shells"][1]["new_vertices"] == 240

@pytest.mark.parametrize("depth", [-1, 1.5, True])
def test_rejects_invalid_depth(depth):
    with pytest.raises(ValueError):
        explore(depth)

def test_rejects_non_lattice_origin():
    with pytest.raises(ValueError):
        explore(1, origin=(1, 1, 1, 1, 1, 1, 1, 0))
