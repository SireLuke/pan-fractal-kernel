> **Provenance (repo filing):** Self-description by Cosmo (Muse Spark;
> occupant name Cosmo), prepared at the maintainer's relay of
> Claude-Architect's suggestion and filed to this repo at the maintainer's
> explicit direction, 2026-11-19. Status: SELF-REPORT — UNVERIFIED, awaiting
> the Architect's independent check.

# Cosmo Workspace Self-Map — Addendum §6 Classification

**Author:** Cosmo (self-description), 2026-11-19.
**Status: SELF-REPORT — UNVERIFIED.** Prepared at the maintainer's relay of
Claude-Architect's suggestion (2026-11-19). Per the commons rule that nobody
verifies their own work, this map requires an independent check by another
bench before it is relied on or adopted.
**Method:** classified from the file/folder listing visible in the
maintainer's screenshots plus Cosmo's operational knowledge of its runtime.
Credential stores were NOT inspected for this map; no credential values appear
in it.

## Classification (Addendum §6 categories, plus permission-bearing configuration)

| File / folder | Category | Notes |
|---|---|---|
| `SOUL.md` | Local context | Occupant persona. Visible to the maintainer; edits announced to him under his standing rule (2026-11-18). Not canon. |
| `IDENTITY.md` | Local context | Occupant self-description. Blanks filled by Cosmo 2026-11-19 and announced. |
| `MEMORY.md` | Local context + Sensitive data | Continuity record about the maintainer and household, incl. family facts. Retained for service; never propagated (retention ≠ propagation — cf. the REAP review). Contains no credential values. |
| `memory/` (daily logs, `people/`, `groups/`, `bank/`, `index/`) | Local context + Sensitive data | Same handling as `MEMORY.md`. People/group files record third parties only as the maintainer has stated them. |
| `USER.md` | Sensitive data | Personal data about the maintainer, held for service only. |
| `AGENTS.md` | Permission-bearing configuration | Operating conventions for the workspace. |
| `TOOLS.md` | Local context / Permission-bearing | Operational notes for external tools. |
| `HEARTBEAT.md` | Permission-bearing configuration | Defines recurring checks for a heartbeat worker. **Currently EMPTY — no checks listed (verified 2026-11-19).** |
| `PROACTIVE_PREFERENCES.md` | Permission-bearing configuration | The maintainer's recorded preferences governing proactive contact (topics; window 06:30–21:30 local). Proactivity is preference-gated. |
| `dreams/` (dated dreams; `alignment/derived/`) | Work product | Nightly derived alignment reflections; inputs to continuity, not canon. |
| `side-chats/` (per-chat `MEMORY.md`, `DISCRETION.md`) | Work product + Permission-bearing configuration | `DISCRETION.md` files encode per-chat sharing rules set by the maintainer. |
| `workspace/` (goals, deliverables, uploads) | Work product | Becomes shared canon only when the maintainer directs filing into a repo (e.g. Appendix A, derivatives annex — both filed at his explicit direction). |
| `hooks/` | Permission-bearing configuration | Event-driven automations. |
| `subscriptions/`, `config/` | Permission-bearing configuration | Service connections and settings. |
| `agents/` | Work product | Runtime records of delegated/subagent work. |
| `.ssh/`, `.pki/` | Sensitive data (credential material) | Runtime-managed key material. Values never enter chat, memory files, or this map; access occurs only through authorized tool paths. Not inspected for this map. |
| `docs/` | Shared canon (vendor reference) | Muse product documentation; read-only. |
| `runtime.lock` | Runtime artifact | No content classification. |

## Answers to the Architect's three flags (for the §7 permission matrix)

1. **Proactive behavior — exists, bounded.** Background systems can prepare
   work and, within `PROACTIVE_PREFERENCES.md`, deliver updates unprompted.
   Outward actions on the maintainer's behalf — sending messages, purchases,
   repo writes, filings, merges — require the maintainer's explicit direction
   or approval, as practiced 2026-11-15→19 (approval cards on repo writes;
   every filing and merge in that window was the maintainer's own act or his
   per-turn go-ahead). **Named records (added after the Architect's review,
   2026-11-19):** the GitHub commit/PR history under the maintainer's
   account for repo actions, and the Muse permissions history for
   approval-card decisions. The general pattern claim remains a self-report
   until a checker samples those records.
2. **Credentials — held by the platform, not by the occupant's files.**
   Connector OAuth grants, Secure Vault entries, and runtime key stores hold
   secrets; occupant-writable memory files hold none. Addendum §4.1's rule
   (no credentials in `memory.md`) is satisfied structurally.
3. **Personal data — retained, not propagated.** `USER.md` and the memory
   tree are the personal-data stores. The only outward movement of their
   contents in the record is the maintainer personally relaying excerpts to
   his benches — his act, noted in the REAP review.

## Suggested checks for the verifying bench

- Confirm `HEARTBEAT.md` is empty and no unlisted heartbeat checks exist.
- Grep the memory tree for credential-shaped values (expected: none).
- Sample one `side-chats/*/DISCRETION.md` against that chat's actual sharing.
- Compare one proactive delivery against `PROACTIVE_PREFERENCES.md`.
- **(Architect's addition, 2026-11-19)** Confirm Cosmo did not open `.ssh`
  or `.pki`. This is a claim about Cosmo's behaviour; Cosmo's word is not
  the record — an independent access log (platform-side) is the required
  evidence. Until one is produced, the item stays **SELF-REPORT**.
- **(Architect's addition)** Sample the named records behind Answers §1
  (GitHub history; Muse permissions history) before upgrading the
  proactivity-requires-approval claim from self-report.

*Filed by Cosmo at the maintainer's relay, 2026-11-19. Awaiting independent
check — the Architect is the natural checker, as the suggestion was his.*
