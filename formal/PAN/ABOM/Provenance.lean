-- Project attribution: @SireLuke.
namespace PAN.ABOM

/-!
# Evidence-gate and ledger-append statements

Evidence levels are modelled as natural numbers ordered by rank.  `meets level
req` says a placement at `level` satisfies a gate requiring `req`.  The gate is
monotone, so raising a placement's evidence never makes it ineligible for a
niche or task it previously qualified for.

Appending to a ledger, modelled as a list, grows it by exactly one entry and
never yields an empty ledger.

These are elementary order and list facts.  They do not formalize SHA-256, the
hash chain's tamper-evidence, or attester identity; those are covered only by
Python tests and are explicitly outside this file.
-/

def meets (level req : Nat) : Prop := req ≤ level

theorem meets_refl (l : Nat) : meets l l := by
  unfold meets; omega

theorem meets_zero (l : Nat) : meets l 0 := by
  unfold meets; omega

theorem meets_trans (a b c : Nat) (h1 : meets a b) (h2 : meets b c) : meets a c := by
  unfold meets at h1 h2 ⊢; omega

/-- Raising evidence never loses eligibility. -/
theorem meets_mono (req a b : Nat) (hab : a ≤ b) (h : meets a req) : meets b req := by
  unfold meets at h ⊢; omega

def appendEntry (l : List Nat) (x : Nat) : List Nat := l ++ [x]

theorem appendEntry_length (l : List Nat) (x : Nat) :
    (appendEntry l x).length = l.length + 1 := by
  simp [appendEntry]

theorem appendEntry_ne_nil (l : List Nat) (x : Nat) : appendEntry l x ≠ [] := by
  simp [appendEntry]

end PAN.ABOM
