namespace PAN.ABOM

/-!
# Finite Menger-mask transmission bounds

The numerical coupling uses a binary retained/void mask. For an exact rational
reference, represent opacity as opacityUnits / denominator, where
0 ≤ opacityUnits ≤ denominator. The amplitude transmission numerator is
denominator - opacityUnits in a retained cell and denominator in a void.

These integer statements establish bounded amplitude transmission for the
finite two-state model. They do not formalize the Python floating-point or
complex-valued operator, its FFT, or a physical wave equation.
-/

def mengerTransmissionNumerator
    (opacityUnits denominator : Nat) (occupied : Bool) : Nat :=
  if occupied then denominator - opacityUnits else denominator

theorem menger_transmission_bounds
    (opacityUnits denominator : Nat)
    (h : opacityUnits ≤ denominator)
    (occupied : Bool) :
    0 ≤ mengerTransmissionNumerator opacityUnits denominator occupied ∧
    mengerTransmissionNumerator opacityUnits denominator occupied ≤ denominator := by
  cases occupied <;> simp [mengerTransmissionNumerator] <;> omega

theorem menger_void_transmission
    (opacityUnits denominator : Nat) :
    mengerTransmissionNumerator opacityUnits denominator false = denominator := by
  simp [mengerTransmissionNumerator]

theorem menger_full_opacity_blocks_retained
    (denominator : Nat) :
    mengerTransmissionNumerator denominator denominator true = 0 := by
  simp [mengerTransmissionNumerator]

theorem menger_zero_opacity_identity
    (denominator : Nat) (occupied : Bool) :
    mengerTransmissionNumerator 0 denominator occupied = denominator := by
  cases occupied <;> simp [mengerTransmissionNumerator]

end PAN.ABOM
