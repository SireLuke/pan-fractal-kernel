namespace PAN.ABOM

/-!
# 13_3 microtubule lattice arithmetic

Sites are integer pairs `(i, k)`: protofilament index `i` and monomer index `k`.
Going once around the cylinder (`i -> i + 13`) lands on the same site as
`k -> k + 3`, so the lattice is `Z^2` modulo the seam vector `(13, -3)`. This is
lattice arithmetic only; it makes no physical claim.
-/

/-- Signed helix index of the step `(di, dk)`; its absolute value is the start number. -/
def helixIndex (di dk : Int) : Int := 3 * di + 13 * dk

/-- The seam vector spans nothing. -/
theorem helixIndex_seam : helixIndex 13 (-3) = 0 := by decide

/-- Adding the seam vector to a step does not change its helix index. -/
theorem helixIndex_seam_invariant (di dk : Int) :
    helixIndex (di + 13) (dk - 3) = helixIndex di dk := by
  unfold helixIndex
  omega

/-- The helix index is additive. -/
theorem helixIndex_add (a b c d : Int) :
    helixIndex (a + c) (b + d) = helixIndex a b + helixIndex c d := by
  unfold helixIndex
  omega

theorem helix_three : helixIndex 1 0 = 3 := by decide

theorem helix_five : helixIndex 6 (-1) = 5 := by decide

theorem helix_eight : helixIndex (-6) 2 = 8 := by decide

theorem helix_thirteen : helixIndex 0 1 = 13 := by decide

/-- `v3 + v5 = v8` modulo the seam vector: `(7, -1) = (-6, 2) + (13, -3)`. -/
theorem v3_add_v5_eq_v8_mod_seam :
    ((1 : Int) + 6, (0 : Int) + -1) = ((-6 : Int) + 13, (2 : Int) + -3) := by decide

/-- `v5 + v8 = v13` exactly: `(6, -1) + (-6, 2) = (0, 1)`. -/
theorem v5_add_v8_eq_v13 :
    ((6 : Int) + -6, (-1 : Int) + 2) = ((0 : Int), (1 : Int)) := by decide

/-- The start numbers 3, 5, 8, 13 are consecutive Fibonacci numbers. -/
theorem fibonacci_start_numbers : (3 : Nat) + 5 = 8 ∧ (5 : Nat) + 8 = 13 := by decide

/-- Subunit type is the parity of the monomer index. Going around the seam adds 3, an odd shift, so
alpha meets beta there. -/
theorem seam_flips_type (k : Int) : (k + 3) % 2 ≠ k % 2 := by omega

/-- An even start number would keep the type across the seam. -/
theorem even_start_keeps_type (k : Int) : (k + 4) % 2 = k % 2 := by omega

/-- Axial position in units of one thirteenth of a monomer: `z = 13 k + 3 i`. -/
def axialScaled (i k : Int) : Int := 13 * k + 3 * i

/-- Going once around and dropping three monomers returns to the same height. -/
theorem axial_wraps (i k : Int) :
    axialScaled (i + 13) (k - 3) = axialScaled i k := by
  unfold axialScaled
  omega

/-- One full turn rises by three monomers (`3 * 13` units of a thirteenth). -/
theorem axial_rise_per_turn (i k : Int) :
    axialScaled (i + 13) k - axialScaled i k = 3 * 13 := by
  unfold axialScaled
  omega

/-- Neighbouring protofilaments are offset by three thirteenths of a monomer. -/
theorem axial_offset_between_neighbours (i k : Int) :
    axialScaled (i + 1) k - axialScaled i k = 3 := by
  unfold axialScaled
  omega

end PAN.ABOM
