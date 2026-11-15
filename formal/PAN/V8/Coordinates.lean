namespace PAN
/-- Canonical PAN V8 state. Coordinate order is fixed and versioned:
    h, R, u, d, tau, chi, s, f. -/
structure V8State where
  h : Float
  R : Float
  u : Float
  d : Float
  tau : Float
  chi : Float
  s : Float
  f : Float
  deriving Repr

/-- Serialization order is part of the schema contract. -/
def V8State.coordinates (x : V8State) : List Float :=
  [x.h, x.R, x.u, x.d, x.tau, x.chi, x.s, x.f]

theorem v8_coordinate_count (x : V8State) :
    x.coordinates.length = 8 := by
  rfl

/-- tau is the temporal-offset coordinate. The provisional alias T (formerly
    glossed as persistence) is not a schema change. -/
def V8State.temporal (x : V8State) : Float := x.tau
end PAN
