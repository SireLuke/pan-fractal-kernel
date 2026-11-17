namespace PAN.ABOM

/-!
# Menger sponge surface area

In units of one level-`n` cell face (area `9^(-n)` of the unit cube) the surface
of the level-`n` sponge is `2 * 20^n + 4 * 8^n` faces, so its area is the exact
fraction `surfNum n / surfDen n` with `surfDen n = 9^n`.  The volume fraction
`volNum n / volDen n = 20^n / 27^n` is in `MengerVolume.lean`.

This file proves arithmetic about those integers.  It does not prove that the
closed form counts the faces of the geometric sponge; the Python test recounts
faces directly from the cell coordinates for levels 0 to 3.
-/

/-- Exposed cell faces of the level-`n` sponge: `2 * 20^n + 4 * 8^n`. -/
def surfNum (n : Nat) : Nat := 2 * 20 ^ n + 4 * 8 ^ n

/-- Faces per unit-cube area at level `n`: `9^n`. -/
def surfDen (n : Nat) : Nat := 9 ^ n

private theorem pow_pos' (b n : Nat) (hb : 0 < b) : 0 < b ^ n := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Nat.pow_succ]
    exact Nat.mul_pos ih hb

private theorem lt_two_pow' (n : Nat) : n < 2 ^ n := by
  induction n with
  | zero => decide
  | succ k ih =>
    rw [Nat.pow_succ]
    omega

/-- Level 0 is the unit cube: six faces, denominator one. -/
theorem surf_level_zero : surfNum 0 = 6 ∧ surfDen 0 = 1 := by decide

/-- Level 1: `72 / 9 = 8`. -/
theorem surf_level_one : surfNum 1 = 72 ∧ surfDen 1 = 9 := by decide

/-- Level 2: `1056 / 81 = 352 / 27`. -/
theorem surf_level_two : surfNum 2 = 1056 ∧ surfDen 2 = 81 := by decide

/-- Level 3: `18048 / 729 = 6016 / 243`. -/
theorem surf_level_three : surfNum 3 = 18048 ∧ surfDen 3 = 729 := by decide

theorem surfDen_succ (n : Nat) : surfDen (n + 1) = surfDen n * 9 := by
  unfold surfDen
  exact Nat.pow_succ 9 n

theorem surfNum_succ (n : Nat) : surfNum (n + 1) = 40 * 20 ^ n + 32 * 8 ^ n := by
  have e1 : 20 ^ (n + 1) = 20 ^ n * 20 := Nat.pow_succ 20 n
  have e2 : 8 ^ (n + 1) = 8 ^ n * 8 := Nat.pow_succ 8 n
  unfold surfNum
  omega

/-- Surface area strictly increases with the level: `surfNum (n+1) / surfDen (n+1) > surfNum n / surfDen n`,
written without division as `9 * surfNum n < surfNum (n+1)`. -/
theorem surf_strictly_increasing (n : Nat) : 9 * surfNum n < surfNum (n + 1) := by
  have h : 8 ^ n ≤ 20 ^ n := Nat.pow_le_pow_left (by decide) n
  have hp : 0 < 20 ^ n := pow_pos' 20 n (by decide)
  rw [surfNum_succ]
  unfold surfNum
  omega

/-- The surface area exceeds the level: `n < surfNum n / surfDen n`, so it is unbounded. -/
theorem surf_exceeds_level (n : Nat) : n * surfDen n < surfNum n := by
  have h18 : 18 ^ n ≤ 20 ^ n := Nat.pow_le_pow_left (by decide) n
  have hm : 18 ^ n = 9 ^ n * 2 ^ n := Nat.mul_pow 9 2 n
  have h2 : n < 2 ^ n := lt_two_pow' n
  have h3 : 9 ^ n * (n + 1) ≤ 9 ^ n * 2 ^ n := Nat.mul_le_mul_left _ h2
  have hp : 0 < 9 ^ n := pow_pos' 9 n (by decide)
  have h4 : 9 ^ n * (n + 1) = 9 ^ n * n + 9 ^ n := by rw [Nat.mul_add, Nat.mul_one]
  have h5 : n * 9 ^ n = 9 ^ n * n := Nat.mul_comm _ _
  unfold surfNum surfDen
  omega

/-- Volume fraction and surface area move in opposite directions: `20^n / 27^n ≤ 1`
while `n < surfNum n / surfDen n`. -/
theorem volume_bounded_surface_unbounded (n : Nat) :
    20 ^ n ≤ 27 ^ n ∧ n * surfDen n < surfNum n :=
  ⟨Nat.pow_le_pow_left (by decide) n, surf_exceeds_level n⟩

end PAN.ABOM
