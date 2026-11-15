"""Combinatorial geometry of the 13-protofilament, 3-start (13_3) microtubule lattice.

Pure lattice arithmetic. Nothing here is a physical or biological claim beyond
the nominal literature layout below, and nothing here is evidence for any
quantum or field-theoretic hypothesis.

Model
-----
Subunit sites are integer pairs ``(i, k)``: ``i`` is the protofilament index
(angle ``2*pi*i/13`` around the cylinder) and ``k`` is the monomer index along
the protofilament. Axial position is

    z(i, k) = monomer_nm * (k + start * i / n_protofilaments)

so neighbouring protofilaments are offset by ``start * monomer_nm / 13``
(12/13 nm ~ 0.92 nm for the nominal values). Going once around the cylinder
(``i -> i + 13``) lands on the same physical site as ``k -> k + start``, so the
lattice is ``Z^2`` modulo the *seam vector* ``(13, -3)``.

Subunit type alternates along a protofilament (alpha, beta, ...): type is the
parity of ``k`` on the strip ``i = 0..12``. Lateral neighbours then match
(alpha-alpha, beta-beta: the B-lattice) except across the seam, where the
identification shifts ``k`` by ``start = 3`` (odd) and alpha meets beta.

Helix families
--------------
A step ``(di, dk)`` generates a helix family with start number
``S = |start * di + n * dk|`` (the index of the sublattice it spans together
with the seam vector). ``(1, 0)`` is the 3-start monomer helix, ``(0, 1)`` the
13 straight protofilaments, and ``(6, -1)``, ``(-6, 2)`` are 5- and 8-start
families. The start numbers 3, 5, 8, 13 are consecutive Fibonacci numbers and
the generating vectors satisfy ``v3 + v5 = v8`` and ``v5 + v8 = v13`` modulo
the seam vector. This is an exact lattice identity. 5- and 8-start helices are
long paths, not nearest-neighbour bonds, so their Fibonacci pattern is a
property of the integers (13 = 5 + 8, 8 = 5 + 3), not a structural claim.

Nominal geometry (literature-typical, stated as parameters, not measured here):
monomer axial repeat 4.0 nm, dimer 8.0 nm, centreline radius 10.0 nm.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

N_PROTOFILAMENTS = 13
START_NUMBER = 3
MONOMER_NM = 4.0
CENTRELINE_RADIUS_NM = 10.0

ALPHA = "alpha"
BETA = "beta"

Step = tuple[int, int]


@dataclass(frozen=True, slots=True)
class MicrotubuleLattice:
    n_protofilaments: int = N_PROTOFILAMENTS
    start: int = START_NUMBER
    monomer_nm: float = MONOMER_NM
    radius_nm: float = CENTRELINE_RADIUS_NM

    def __post_init__(self) -> None:
        if not isinstance(self.n_protofilaments, int) or self.n_protofilaments < 2:
            raise ValueError("n_protofilaments must be an integer >= 2")
        if not isinstance(self.start, int) or self.start < 1:
            raise ValueError("start must be a positive integer")
        if not math.isfinite(self.monomer_nm) or self.monomer_nm <= 0.0:
            raise ValueError("monomer_nm must be finite and positive")
        if not math.isfinite(self.radius_nm) or self.radius_nm <= 0.0:
            raise ValueError("radius_nm must be finite and positive")

    # --- scalar geometry -------------------------------------------------
    @property
    def seam_vector(self) -> Step:
        """Lattice vector that closes the cylinder: (n, -start)."""
        return (self.n_protofilaments, -self.start)

    @property
    def dimer_nm(self) -> float:
        return 2.0 * self.monomer_nm

    @property
    def rise_per_turn_nm(self) -> float:
        """Axial rise of the primary helix per full turn: start * monomer."""
        return self.start * self.monomer_nm

    @property
    def protofilament_offset_nm(self) -> float:
        """Axial offset between neighbouring protofilaments."""
        return self.rise_per_turn_nm / self.n_protofilaments

    @property
    def seam_shift_dimers(self) -> float:
        """Seam stagger in dimer repeats: start / 2 (1.5 for the 13_3 lattice)."""
        return self.start / 2.0

    @property
    def seam_is_heterotypic(self) -> bool:
        """True when the seam joins alpha to beta (odd start number)."""
        return self.start % 2 == 1

    @property
    def pitch_angle_deg(self) -> float:
        """Angle of the primary helix against the circumferential direction."""
        circumference = 2.0 * math.pi * self.radius_nm
        return math.degrees(math.atan2(self.rise_per_turn_nm, circumference))

    # --- site addressing -------------------------------------------------
    def canonical(self, i: int, k: int) -> Step:
        """Reduce ``(i, k)`` to protofilament ``0 <= i < n`` using the seam identification."""
        _check_int(i, "i")
        _check_int(k, "k")
        turns, i0 = divmod(i, self.n_protofilaments)
        return (i0, k + self.start * turns)

    def axial_nm(self, i: int, k: int) -> float:
        _check_int(i, "i")
        _check_int(k, "k")
        return self.monomer_nm * (k + self.start * i / self.n_protofilaments)

    def angle_rad(self, i: int) -> float:
        _check_int(i, "i")
        return 2.0 * math.pi * (i % self.n_protofilaments) / self.n_protofilaments

    def subunit_type(self, i: int, k: int) -> str:
        """alpha/beta by parity of the canonical monomer index."""
        _, kc = self.canonical(i, k)
        return ALPHA if kc % 2 == 0 else BETA

    def position(self, i: int, k: int) -> tuple[float, float, float]:
        """Cartesian (x, y, z) in nm on the centreline cylinder."""
        theta = self.angle_rad(i)
        return (self.radius_nm * math.cos(theta),
                self.radius_nm * math.sin(theta),
                self.axial_nm(i, k))

    def unwrapped(self, i: int, k: int) -> tuple[int, float]:
        """Unwrapped-strip coordinates: (protofilament index 0..n-1, axial nm)."""
        i0, k0 = self.canonical(i, k)
        return (i0, self.axial_nm(i0, k0))

    def lateral_neighbour(self, i: int, k: int) -> Step:
        """Canonical site one protofilament over: ``(i + 1, k)``."""
        return self.canonical(i + 1, k)

    def lateral_contact_is_homotypic(self, i: int, k: int) -> bool:
        """True for alpha-alpha / beta-beta lateral contacts, False across the seam."""
        return self.subunit_type(i, k) == self.subunit_type(*self.lateral_neighbour(i, k))

    # --- helix families --------------------------------------------------
    def start_number(self, di: int, dk: int) -> int:
        """Number of strands of the helix family generated by step (di, dk)."""
        _check_int(di, "di")
        _check_int(dk, "dk")
        return abs(self.start * di + self.n_protofilaments * dk)

    def reduce_step(self, di: int, dk: int) -> Step:
        """Representative of the step modulo the seam vector with ``-n//2 <= di < n - n//2``."""
        _check_int(di, "di")
        _check_int(dk, "dk")
        n = self.n_protofilaments
        turns = (di + n // 2) // n          # floor: whole seam vectors to remove
        return (di - turns * n, dk + self.start * turns)

    def canonical_helix(self, start_number: int) -> Step:
        """Shortest-lateral step (di, dk) whose signed index ``start*di + n*dk`` equals +S.

        Ties in |di| prefer the smaller |dk|. Raises if no such step exists
        (it always does when gcd(start, n) divides S).
        """
        if isinstance(start_number, bool) or not isinstance(start_number, int) or start_number < 1:
            raise ValueError("start_number must be a positive integer")
        n, s = self.n_protofilaments, self.start
        best: Step | None = None
        for dk in range(-s - 1, s + 2):
            for di in range(-(n // 2), n // 2 + 1):
                if s * di + n * dk == start_number:
                    if best is None or (abs(di), abs(dk)) < (abs(best[0]), abs(best[1])):
                        best = (di, dk)
        if best is None:
            raise ValueError(f"no helix family with start number {start_number}")
        return best

    def handedness(self, di: int, dk: int) -> int:
        """+1 if the family winds the same way as the primary helix, -1 if opposite, 0 if straight.

        Relative to the primary (1, 0) step, using the given representative.
        Handedness depends on the representative chosen modulo the seam
        vector, so use ``canonical_helix`` for a convention-fixed answer.
        """
        _check_int(di, "di")
        _check_int(dk, "dk")
        rise = self.start * di + self.n_protofilaments * dk
        if di == 0 or rise == 0:
            return 0
        return 1 if (di > 0) == (rise > 0) else -1

    def families_are_fibonacci_closed(self) -> bool:
        """Check v3 + v5 = v8 and v5 + v8 = v13 modulo the seam vector (13_3 only)."""
        if (self.n_protofilaments, self.start) != (13, 3):
            return False
        v3, v5, v8, v13 = (self.canonical_helix(s) for s in (3, 5, 8, 13))
        return (self.reduce_step(v3[0] + v5[0], v3[1] + v5[1]) == self.reduce_step(*v8)
                and self.reduce_step(v5[0] + v8[0], v5[1] + v8[1]) == self.reduce_step(*v13))


def _check_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")


FIBONACCI_START_NUMBERS = (3, 5, 8, 13)
