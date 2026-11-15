# ABOM-V8 coordinate contract

Schema identifier: `urn:pan:abom-v8:state:0.1`

## Ordered coordinates

The canonical V8 vector is normalized to `[0, 1]` and ordered exactly as follows:

| Index | Name | Symbol | Contract |
|---:|---|---|---|
| 0 | coherence | `h` | Coherence coordinate |
| 1 | recursion | `R` | Recursive-depth/scale coordinate |
| 2 | construction | `u` | Construction coordinate |
| 3 | decoherence | `d` | Decoherence coordinate |
| 4 | temporal offset | `tau` | Temporal offset; persistence is not this coordinate |
| 5 | chirality | `chi` | Chirality coordinate |
| 6 | information density | `s` | Information-density coordinate |
| 7 | forcing | `f` | Forcing coordinate |

The order and meanings are preserved from the kernel's current V8 contract. The provisional input alias `T` maps to `tau`; callers must not supply both. State schemas reject non-finite values and values outside `[0, 1]`.

## Origin and occupancy

The coordinate origin is represented by eight zeros. A profile or adapter may explicitly map a selected state to Fermi occupancy (F=1/2); that mapping is not implied by the zero vector alone. Keep coordinate state and occupancy state as separate typed values.

## Versioning rules

- Add optional fields without changing existing meanings.
- Breaking coordinate semantics require a new schema version and explicit migration.
- Adapters declare supported schema versions and reject unknown breaking versions.
- Experimental profiles may add metadata but cannot redefine the canonical coordinate vector.
