"""Exhaustive 240-seed orbit audit and reproducible graph-mode benchmark."""
from __future__ import annotations
import json
import statistics
import time
import tracemalloc
from e8_bounded_symmetry import MAX_TRANSITIONS, ROOT_COUNT, GossetGraph, propagate_root_orbit


def timed_peak(callable_):
    tracemalloc.start()
    start = time.perf_counter()
    result = callable_()
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, {"seconds": elapsed, "peak_traced_bytes": peak}


def exhaustive_seed_audit():
    reference = set(propagate_root_orbit().roots)
    depths = []
    total_transitions = 0
    for index, seed in enumerate(sorted(reference), start=1):
        orbit = propagate_root_orbit(seed)
        if set(orbit.roots) != reference:
            raise AssertionError(f"seed {index} did not generate the full E8 root orbit")
        if orbit.transitions != MAX_TRANSITIONS:
            raise AssertionError(f"seed {index} used unexpected transition count")
        depths.append(orbit.max_depth_reached)
        total_transitions += orbit.transitions
    return {
        "seeds_checked": len(depths),
        "unique_roots_per_seed": ROOT_COUNT,
        "total_reflection_applications": total_transitions,
        "expected_reflection_applications": ROOT_COUNT * MAX_TRANSITIONS,
        "max_bfs_depth": max(depths),
        "min_bfs_depth": min(depths),
        "mean_bfs_depth": statistics.mean(depths),
        "all_seeds_generate_identical_root_set": True,
    }


def benchmark_graph_modes():
    roots = propagate_root_orbit().roots

    def run_mode(mode):
        # Include graph construction and the full 240-neighborhood query pass
        # in both elapsed time and peak traced allocations.
        cache_limit = ROOT_COUNT if mode == "cached" else 64
        graph = GossetGraph(mode, max_cache_entries=cache_limit)
        neighborhoods = tuple(graph.neighbors(root) for root in roots)
        return neighborhoods, graph.cache_info()

    (expected, explicit_storage), explicit_metrics = timed_peak(
        lambda: run_mode("explicit")
    )
    (cached_result, cached_storage), cached_metrics = timed_peak(
        lambda: run_mode("cached")
    )
    (implicit_result, implicit_storage), implicit_metrics = timed_peak(
        lambda: run_mode("implicit")
    )
    if not (expected == cached_result == implicit_result):
        raise AssertionError("explicit, cached, and implicit neighborhoods differ")
    return {
        "queries": ROOT_COUNT,
        "neighbors_per_vertex": 56,
        "all_modes_identical": True,
        "explicit": {**explicit_metrics, "storage": explicit_storage},
        "cached": {**cached_metrics, "storage": cached_storage},
        "implicit": {**implicit_metrics, "storage": implicit_storage},
        "measurement_scope": (
            "Includes graph construction and all neighborhood queries; Python "
            "tracemalloc peak is not total process RSS."
        ),
        "interpretation": (
            "Machine-specific observations only; no timing threshold or portable "
            "performance guarantee is asserted."
        ),
    }


def main():
    print(json.dumps({
        "status": "PASS",
        "exhaustive_seed_audit": exhaustive_seed_audit(),
        "graph_mode_benchmark": benchmark_graph_modes(),
        "weyl_group_enumerated": False,
        "physical_validation_claimed": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
