namespace PAN.ABOM

/-!
# Menger sponge cell counts and volume fractions

A `d`-dimensional Menger step keeps the sub-cells of `{0,1,2}^d` with at most
one coordinate equal to `1`: `2^d` with none and `d * 2^(d-1)` with exactly one.
For `d = 3` that is `20` of `27`. Level-`n` volume is `(20/27)^n`, stored as the
natural-number pair `(20^n, 27^n)`.
-/

/-- Kept sub-cells per subdivision step in dimension `d`. -/
def cellsPerLevel (d : Nat) : Nat := 2 ^ d + d * 2 ^ (d - 1)

theorem cellsPerLevel_two : cellsPerLevel 2 = 8 := by decide

theorem cellsPerLevel_three : cellsPerLevel 3 = 20 := by decide

theorem cellsPerLevel_four : cellsPerLevel 4 = 48 := by decide

/-- For `d = 3` the removed cells are one body centre and six face centres. -/
theorem menger_three_removed : 3 ^ 3 - cellsPerLevel 3 = 7 := by decide

/-- The similarity dimension of the `d = 3` sponge lies strictly between 2 and 3. -/
theorem menger_dimension_between_two_and_three :
    3 ^ 2 < cellsPerLevel 3 ∧ cellsPerLevel 3 < 3 ^ 3 := by decide

/-- Numerator of the level-`n` volume fraction `(20/27)^n`. -/
def volNum (n : Nat) : Nat := 20 ^ n

/-- Denominator of the level-`n` volume fraction `(20/27)^n`. -/
def volDen (n : Nat) : Nat := 27 ^ n

theorem volNum_succ (n : Nat) : volNum (n + 1) = volNum n * 20 := by
  unfold volNum
  exact Nat.pow_succ 20 n

theorem volDen_succ (n : Nat) : volDen (n + 1) = volDen n * 27 := by
  unfold volDen
  exact Nat.pow_succ 27 n

/-- The volume fraction never exceeds one. -/
theorem vol_le_one (n : Nat) : volNum n ≤ volDen n := by
  unfold volNum volDen
  exact Nat.pow_le_pow_left (by decide) n

/-- Level 2 volume fraction is `400 / 729`. -/
theorem vol_level_two : volNum 2 = 400 ∧ volDen 2 = 729 := by decide

end PAN.ABOM
