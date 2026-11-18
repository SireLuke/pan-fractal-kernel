-- Project attribution: @SireLuke.
namespace PAN.ABOM

/-!
# Capability-distance and niche-seating statements

Capability coordinates are real numbers in [0, 1]; the Lean statements use an
exact integer model (each coordinate scaled to a Nat) so the metric facts are
proved without floating point.  `adist a b` is the absolute difference on Nat,
written as a sum of two truncated subtractions (one of which is always zero).

These statements cover the per-axis distance used by the router and the
occupancy-preservation property of seating a model.  They do not formalize the
Python floating-point implementation, benchmark placement, or any claim about
how well a coordinate describes a model.
-/

def adist (a b : Nat) : Nat := (a - b) + (b - a)

theorem adist_self (a : Nat) : adist a a = 0 := by
  unfold adist; omega

theorem adist_comm (a b : Nat) : adist a b = adist b a := by
  unfold adist; omega

theorem adist_eq_zero_iff (a b : Nat) : adist a b = 0 ↔ a = b := by
  unfold adist; omega

theorem adist_triangle (a b c : Nat) : adist a c ≤ adist a b + adist b c := by
  unfold adist; omega

/-- A positive per-axis weight preserves the triangle inequality. -/
theorem wdist_triangle (w a b c : Nat) :
    w * adist a c ≤ w * adist a b + w * adist b c := by
  have h := Nat.mul_le_mul (Nat.le_refl w) (adist_triangle a b c)
  rw [Nat.mul_add] at h
  exact h

/-- Occupancy as a partial map from niche index to model index. -/
def seatAt (m : Nat → Option Nat) (niche model : Nat) : Nat → Option Nat :=
  fun n => if n = niche then some model else m n

theorem seatAt_same (m : Nat → Option Nat) (niche model : Nat) :
    seatAt m niche model niche = some model := by
  simp [seatAt]

theorem seatAt_other (m : Nat → Option Nat) (niche model n : Nat) (h : n ≠ niche) :
    seatAt m niche model n = m n := by
  simp [seatAt, h]

/-- Replacing the occupant of an occupied niche leaves the set of occupied
niches unchanged: swapping a model never changes the topology. -/
theorem seatAt_preserves_occupied (m : Nat → Option Nat) (niche model : Nat)
    (h : (m niche).isSome = true) (n : Nat) :
    (seatAt m niche model n).isSome = (m n).isSome := by
  by_cases hn : n = niche
  · subst hn
    simp [seatAt, h]
  · simp [seatAt, hn]

end PAN.ABOM
