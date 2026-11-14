"""Bounded, exact E8 Weyl-orbit propagation and Gosset graph views.

Coordinates are doubled: X = 2*x. Every E8 root therefore has integer
coordinates and squared norm 8. For a simple root A, the exact reflection is

    X' = X - (dot(X, A) // 4) * A.

The module stores eight simple-root generators, not the full Weyl group and
not a recursively duplicated tree. Expanded roots/edges are produced only
under explicit traversal budgets.
"""
from __future__ import annotations

from collections import OrderedDict, deque
from dataclasses import dataclass
from itertools import combinations
from typing import Literal, Sequence

DIMENSION = 8
ROOT_COUNT = 240
EDGE_COUNT = 6720
ROOT_NORM_SQUARED_SCALED = 8
SIMPLE_GENERATOR_COUNT = 8
MAX_TRANSITIONS = ROOT_COUNT * SIMPLE_GENERATOR_COUNT
MAX_DEPTH = 64
GraphMode = Literal["explicit", "implicit", "cached"]
ScaledRoot = tuple[int, ...]

# A Bourbaki-shaped E8 simple-root system in doubled coordinates.
# Its Gram matrix has diagonal 8 and off-diagonal entries 0 or -4.
E8_SIMPLE_ROOTS_SCALED: tuple[ScaledRoot, ...] = (
    (-1, 1, 1, 1, -1, 1, 1, 1),
    (0, 2, 0, -2, 0, 0, 0, 0),
    (2, 0, -2, 0, 0, 0, 0, 0),
    (-2, -2, 0, 0, 0, 0, 0, 0),
    (2, 0, 2, 0, 0, 0, 0, 0),
    (-1, 1, -1, 1, -1, -1, -1, -1),
    (0, 0, 0, 0, 2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)
DEFAULT_SEED: ScaledRoot = E8_SIMPLE_ROOTS_SCALED[0]


class TraversalBudgetExceeded(RuntimeError):
    """Raised rather than allowing a traversal to exceed its declared budget."""


@dataclass(frozen=True)
class TraversalBudget:
    max_nodes: int = ROOT_COUNT
    max_depth: int = MAX_DEPTH
    max_transitions: int = MAX_TRANSITIONS

    def __post_init__(self) -> None:
        if not 1 <= self.max_nodes <= ROOT_COUNT:
            raise ValueError(f"max_nodes must be in [1, {ROOT_COUNT}]")
        if not 0 <= self.max_depth <= MAX_DEPTH:
            raise ValueError(f"max_depth must be in [0, {MAX_DEPTH}]")
        if not 1 <= self.max_transitions <= MAX_TRANSITIONS:
            raise ValueError(f"max_transitions must be in [1, {MAX_TRANSITIONS}]")


@dataclass(frozen=True)
class RootOrbit:
    seed: ScaledRoot
    roots: tuple[ScaledRoot, ...]
    max_depth_reached: int
    transitions: int


def _as_scaled_vector(values: Sequence[int], *, name: str = "root") -> ScaledRoot:
    if len(values) != DIMENSION:
        raise ValueError(f"{name} must contain exactly {DIMENSION} coordinates")
    result = tuple(values)
    if any(type(value) is not int for value in result):
        raise TypeError(f"{name} coordinates must be exact Python integers")
    return result


def _dot(a: Sequence[int], b: Sequence[int]) -> int:
    return sum(x * y for x, y in zip(a, b))


def is_scaled_e8_root(values: Sequence[int]) -> bool:
    """Recognize the 240 roots using exact doubled-coordinate predicates."""
    try:
        vector = _as_scaled_vector(values)
    except (TypeError, ValueError):
        return False

    # 112 integer-coordinate roots: exactly two coordinates are +/-2.
    if all(value in (-2, 0, 2) for value in vector):
        return sum(value != 0 for value in vector) == 2

    # 128 half-integer roots: all coordinates are +/-1, even minus parity.
    return all(abs(value) == 1 for value in vector) and (
        sum(value < 0 for value in vector) % 2 == 0
    )


def simple_root_gram_matrix() -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(_dot(left, right) for right in E8_SIMPLE_ROOTS_SCALED)
        for left in E8_SIMPLE_ROOTS_SCALED
    )


def validate_simple_root_system() -> bool:
    """Check generator count, root membership, norms, and E8 Cartan entries."""
    if len(E8_SIMPLE_ROOTS_SCALED) != SIMPLE_GENERATOR_COUNT:
        return False
    if len(set(E8_SIMPLE_ROOTS_SCALED)) != SIMPLE_GENERATOR_COUNT:
        return False
    if not all(is_scaled_e8_root(root) for root in E8_SIMPLE_ROOTS_SCALED):
        return False
    gram = simple_root_gram_matrix()
    entries_valid = all(
        gram[i][j] == (
            ROOT_NORM_SQUARED_SCALED if i == j else
            (-4 if gram[i][j] == -4 else 0)
        )
        for i in range(SIMPLE_GENERATOR_COUNT)
        for j in range(SIMPLE_GENERATOR_COUNT)
    )
    edge_count = sum(
        gram[i][j] == -4
        for i in range(SIMPLE_GENERATOR_COUNT)
        for j in range(i + 1, SIMPLE_GENERATOR_COUNT)
    )
    return entries_valid and edge_count == 7


def reflect_scaled_root(root: Sequence[int], simple_root: Sequence[int]) -> ScaledRoot:
    """Apply one exact simple Weyl reflection to a doubled-coordinate root."""
    vector = _as_scaled_vector(root)
    normal = _as_scaled_vector(simple_root, name="simple_root")
    if not is_scaled_e8_root(vector):
        raise ValueError("root must be one of the 240 scaled E8 roots")
    if normal not in E8_SIMPLE_ROOTS_SCALED:
        raise ValueError("reflection normal must be one of the eight simple roots")
    if _dot(normal, normal) != ROOT_NORM_SQUARED_SCALED:
        raise ValueError("simple-root squared norm must be 8 in doubled coordinates")

    numerator = _dot(vector, normal)
    if numerator % 4:
        raise ArithmeticError("scaled reflection coefficient is not integral")
    coefficient = numerator // 4
    reflected = tuple(
        value - coefficient * component
        for value, component in zip(vector, normal)
    )
    if not is_scaled_e8_root(reflected):
        raise ArithmeticError("simple reflection left the E8 root set")
    return reflected


def propagate_root_orbit(
    seed: Sequence[int] | None = None,
    *,
    budget: TraversalBudget | None = None,
) -> RootOrbit:
    """Breadth-first simple-reflection orbit with hard node/depth/step limits."""
    start = DEFAULT_SEED if seed is None else _as_scaled_vector(seed)
    if not is_scaled_e8_root(start):
        raise ValueError("seed must be one of the 240 scaled E8 roots")
    limits = budget or TraversalBudget()

    seen: set[ScaledRoot] = {start}
    depths: dict[ScaledRoot, int] = {start: 0}
    pending = deque([start])
    transitions = 0

    while pending:
        current = pending.popleft()
        depth = depths[current]
        for generator in E8_SIMPLE_ROOTS_SCALED:
            if transitions >= limits.max_transitions:
                raise TraversalBudgetExceeded(
                    f"transition budget {limits.max_transitions} exhausted"
                )
            transitions += 1
            candidate = reflect_scaled_root(current, generator)
            if candidate in seen:
                continue
            candidate_depth = depth + 1
            if candidate_depth > limits.max_depth:
                raise TraversalBudgetExceeded(
                    f"depth budget {limits.max_depth} exceeded"
                )
            if len(seen) >= limits.max_nodes:
                raise TraversalBudgetExceeded(
                    f"node budget {limits.max_nodes} exhausted"
                )
            seen.add(candidate)
            depths[candidate] = candidate_depth
            pending.append(candidate)

    if len(seen) != ROOT_COUNT:
        raise TraversalBudgetExceeded(
            f"orbit closed at {len(seen)} roots; expected {ROOT_COUNT}"
        )
    return RootOrbit(
        seed=start,
        roots=tuple(sorted(seen)),
        max_depth_reached=max(depths.values()),
        transitions=transitions,
    )


def build_gosset_edges(
    roots: Sequence[Sequence[int]],
    *,
    max_edges: int = EDGE_COUNT,
) -> tuple[tuple[int, int], ...]:
    """Return stable-index undirected edges; adjacency is exact scaled dot=4."""
    if not 0 <= max_edges <= EDGE_COUNT:
        raise ValueError(f"max_edges must be in [0, {EDGE_COUNT}]")
    ordered = tuple(sorted(_as_scaled_vector(root) for root in roots))
    if len(ordered) != ROOT_COUNT or len(set(ordered)) != ROOT_COUNT:
        raise ValueError(f"edge construction requires {ROOT_COUNT} unique roots")
    if not all(is_scaled_e8_root(root) for root in ordered):
        raise ValueError("edge construction received a non-E8 root")

    edges: list[tuple[int, int]] = []
    for left, right in combinations(range(ROOT_COUNT), 2):
        if _dot(ordered[left], ordered[right]) == 4:
            if len(edges) >= max_edges:
                raise TraversalBudgetExceeded(
                    f"edge budget {max_edges} exhausted"
                )
            edges.append((left, right))
    if len(edges) != EDGE_COUNT:
        raise ArithmeticError(
            f"Gosset graph has {len(edges)} edges; expected {EDGE_COUNT}"
        )
    return tuple(edges)


class GossetGraph:
    """Explicit, implicit, or bounded-cache view over the 240-root Gosset graph.

    explicit: retain all generated roots, 6,720 edges, and adjacency lists.
    implicit: retain the seed and generators; regenerate the orbit per query.
    cached: retain the orbit and an LRU of at most max_cache_entries neighborhoods.
    """

    def __init__(
        self,
        mode: GraphMode = "implicit",
        *,
        seed: Sequence[int] | None = None,
        budget: TraversalBudget | None = None,
        max_cache_entries: int = 64,
    ) -> None:
        if mode not in ("explicit", "implicit", "cached"):
            raise ValueError("mode must be 'explicit', 'implicit', or 'cached'")
        if not 1 <= max_cache_entries <= ROOT_COUNT:
            raise ValueError(f"max_cache_entries must be in [1, {ROOT_COUNT}]")
        start = DEFAULT_SEED if seed is None else _as_scaled_vector(seed)
        if not is_scaled_e8_root(start):
            raise ValueError("seed must be one of the 240 scaled E8 roots")

        self.mode: GraphMode = mode
        self.seed = start
        self.budget = budget or TraversalBudget()
        self.max_cache_entries = max_cache_entries
        self._orbit: RootOrbit | None = None
        self._edges: tuple[tuple[int, int], ...] | None = None
        self._adjacency: dict[ScaledRoot, tuple[ScaledRoot, ...]] = {}
        self._neighbor_cache: OrderedDict[
            ScaledRoot, tuple[ScaledRoot, ...]
        ] = OrderedDict()

        if mode == "explicit":
            self._orbit = propagate_root_orbit(self.seed, budget=self.budget)
            self._edges = build_gosset_edges(self._orbit.roots)
            neighbors: list[list[ScaledRoot]] = [
                [] for _ in self._orbit.roots
            ]
            for left, right in self._edges:
                neighbors[left].append(self._orbit.roots[right])
                neighbors[right].append(self._orbit.roots[left])
            self._adjacency = {
                root: tuple(neighbors[index])
                for index, root in enumerate(self._orbit.roots)
            }

    def _get_orbit(self) -> RootOrbit:
        if self.mode == "implicit":
            return propagate_root_orbit(self.seed, budget=self.budget)
        if self._orbit is None:
            self._orbit = propagate_root_orbit(self.seed, budget=self.budget)
        return self._orbit

    def roots(self) -> tuple[ScaledRoot, ...]:
        return self._get_orbit().roots

    def neighbors(self, root: Sequence[int]) -> tuple[ScaledRoot, ...]:
        key = _as_scaled_vector(root)
        if not is_scaled_e8_root(key):
            raise ValueError("query must be one of the 240 scaled E8 roots")
        if self.mode == "explicit":
            return self._adjacency[key]
        if self.mode == "cached" and key in self._neighbor_cache:
            self._neighbor_cache.move_to_end(key)
            return self._neighbor_cache[key]

        adjacent = tuple(
            candidate
            for candidate in self.roots()
            if _dot(key, candidate) == 4
        )
        if len(adjacent) != 56:
            raise ArithmeticError(
                f"vertex degree is {len(adjacent)}; expected 56"
            )
        if self.mode == "cached":
            self._neighbor_cache[key] = adjacent
            self._neighbor_cache.move_to_end(key)
            while len(self._neighbor_cache) > self.max_cache_entries:
                self._neighbor_cache.popitem(last=False)
        return adjacent

    def edges(self) -> tuple[tuple[int, int], ...]:
        if self.mode == "explicit":
            assert self._edges is not None
            return self._edges
        return build_gosset_edges(self.roots())

    def cache_info(self) -> dict[str, int | bool | str]:
        return {
            "mode": self.mode,
            "retained_root_orbit": self._orbit is not None,
            "retained_edge_list": self._edges is not None,
            "cached_neighbor_entries": len(self._neighbor_cache),
            "max_cached_neighbor_entries": (
                self.max_cache_entries if self.mode == "cached" else 0
            ),
        }
