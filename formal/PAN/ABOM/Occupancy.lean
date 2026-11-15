namespace PAN.ABOM

/-- Integer-percentage occupancy used for finite contract checks. -/
def complementPercent (n : Nat) : Nat := 100 - n

/-- Occupancy and its complement sum to the full percentage when bounded. -/
theorem occupancy_complement_sum (n : Nat) (h : n ≤ 100) :
    n + complementPercent n = 100 := by
  rw [complementPercent]
  calc
    n + (100 - n) = (100 - n) + n := Nat.add_comm _ _
    _ = 100 := Nat.sub_add_cancel h

/-- Complementing a bounded percentage twice returns the original value. -/
theorem occupancy_complement_involution (n : Nat) (h : n ≤ 100) :
    complementPercent (complementPercent n) = n := by
  simp [complementPercent, Nat.sub_sub_self h]

/-- The equilibrium percentage is self-complementary. -/
theorem half_occupancy_is_fixed :
    complementPercent 50 = 50 := by
  rfl

end PAN.ABOM
