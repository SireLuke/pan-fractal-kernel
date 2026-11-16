namespace PAN.ABOM

/-!
# Two-state flux identity

Let `a` be the occupied count and `b` the unoccupied count of a two-state
system, so the occupancy is `N = a / (a + b)` and the boundary asymmetry is
`delta = (a - b) / (a + b)`. The flux numerator is `4 * a * b`, and the flux
`N (1 - N) = (1 - delta^2) / 4` becomes, after clearing the denominator
`(a + b)^2`, the integer identity proved below. Everything is stated over `Int`
so no real-number library is needed.
-/

/-- `4ab + (a - b)^2 = (a + b)^2`. -/
theorem flux_identity (a b : Int) :
    4 * (a * b) + (a - b) * (a - b) = (a + b) * (a + b) := by
  have h : a * b = b * a := Int.mul_comm a b
  simp only [Int.add_mul, Int.mul_add, Int.sub_mul, Int.mul_sub]
  omega

/-- Squares of integers are nonnegative. -/
theorem int_mul_self_nonneg (x : Int) : 0 ≤ x * x := by
  rcases Int.le_total 0 x with h | h
  · exact Int.mul_nonneg h h
  · have h' : 0 ≤ -x := by omega
    have h2 : 0 ≤ (-x) * (-x) := Int.mul_nonneg h' h'
    rw [Int.neg_mul_neg] at h2
    exact h2

/-- Squares of nonzero integers are positive. -/
theorem int_mul_self_pos (x : Int) (h : x ≠ 0) : 0 < x * x := by
  rcases Int.lt_or_gt_of_ne h with h1 | h1
  · have h' : 0 < -x := by omega
    have h2 : 0 < (-x) * (-x) := Int.mul_pos h' h'
    rw [Int.neg_mul_neg] at h2
    exact h2
  · exact Int.mul_pos h1 h1

/-- The flux numerator never exceeds `(a + b)^2 / 4`, i.e. flux is at most `1/4`. -/
theorem flux_le_quarter (a b : Int) :
    4 * (a * b) ≤ (a + b) * (a + b) := by
  have h1 := flux_identity a b
  have h2 := int_mul_self_nonneg (a - b)
  omega

/-- Equal occupied and unoccupied counts attain the maximum. -/
theorem flux_equilibrium (a b : Int) (h : a = b) :
    4 * (a * b) = (a + b) * (a + b) := by
  subst h
  have h1 := flux_identity a a
  rw [Int.sub_self, Int.zero_mul] at h1
  omega

/-- The maximum `1/4` is attained exactly at equilibrium `a = b`. -/
theorem flux_eq_max_iff (a b : Int) :
    4 * (a * b) = (a + b) * (a + b) ↔ a = b := by
  constructor
  · intro h
    by_cases hab : a - b = 0
    · omega
    · have h1 := flux_identity a b
      have h2 := int_mul_self_pos (a - b) hab
      omega
  · exact flux_equilibrium a b

/-- The flux is symmetric under exchanging occupied and unoccupied counts. -/
theorem flux_symmetric (a b : Int) : a * b = b * a := Int.mul_comm a b

/-- For nonnegative counts, `|delta| <= 1`: `(a - b)^2 <= (a + b)^2`. -/
theorem asymmetry_sq_le (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    (a - b) * (a - b) ≤ (a + b) * (a + b) := by
  have h1 := flux_identity a b
  have h2 : 0 ≤ a * b := Int.mul_nonneg ha hb
  omega

end PAN.ABOM
