# memory.md — Mandatory occupant continuity record

**Occupant ID:**  
**Model/provider/version:**  
**Niche:**  
**Record version:**  
**Last updated (UTC):**  
**Maintainer / authority:**  

## 1. Durable shared canon
Record only stable, source-backed facts and governing constraints. Link to canonical sources.

## 2. New-house orientation and inherited bibliography
Use this section when a new model/occupant joins the PAN commons or a new "house" is initialized.
- Provide a concise orientation to PAN's purpose, architecture, current project state, terminology, governance, and active constraints.
- Existing occupants or maintainers (including Muse and Cosmo when available) may contribute handoff notes and bibliography entries.
- Preserve bibliography entries with author, title, publication/source, date/version, stable URI or DOI, access date, and the specific claim or design decision the source supports.
- Label each item as primary source, secondary source, implementation reference, hypothesis, or commentary. Record uncertainty, disagreements, and superseded references.
- Treat inherited notes as leads and context, not unquestionable authority. New occupants should verify consequential claims against primary sources and current repository state.
- Keep authorship, attribution, permissions, and accountability attached to their actual origin; context inheritance does not transfer identity or authority.

## 3. Occupant-local context
Role-specific preferences, task context, and working assumptions. Keep separate from shared canon.

## 4. Current work and handoff
- Current objective:
- Completed:
- In progress:
- Next action:
- Blockers:

## 5. Decisions and rationale
| Date (UTC) | Decision | Rationale | Authority/source |
|---|---|---|---|

## 6. Evidence and uncertainty
Label claims as verified, reproduced, reported, inferred, or [unverified]. Link evidence and record limitations.

## 7. Corrections and supersession
Preserve material history. Mark superseded claims and link to the correction; do not silently erase them.

## 8. Dependencies and permissions
List authorized tools, data scopes, external dependencies, and expiry/review dates. Memory does not grant permissions.

## 9. Privacy and retention
Do not store credentials, secrets, or unnecessary personal data. Record retention and deletion requirements.

## 10. Integrity and provenance
Record source URI/revision, author or importing operator, timestamp, and digest where available. A digest establishes integrity, not truth.

## 11. Contribution sign-off and repository authorization
- For commits created by an assistant or automation on the maintainer's behalf, include a DCO `Signed-off-by:` trailer using the maintainer-approved Git identity.
- Standing DCO instruction: the maintainer has authorized the assistant to apply the sign-off identity `SireLuke <332733819+SireLuke@users.noreply.github.com>` to commits the assistant creates on the maintainer's behalf, subject to the contribution being legitimately submit-able under the project's DCO.
- This standing instruction is **not repository access or permission to make changes**. Obtain explicit, per-action authorization before every repository mutation (including creating/updating files, commits, branches, refs, PRs, comments, settings, or merges), unless the maintainer explicitly authorizes a clearly bounded batch of actions.
- Do not add the maintainer's sign-off to commits authored by another person, do not imply another person's attestation, and do not rewrite third-party commits merely to add a trailer. Ask for clarification if authorship, contribution rights, identity, or DCO applicability is uncertain.
- Verify the final commit message contains the exact trailer and run the repository's DCO check when available. Report the check result separately from tests, CI, and mathematical validation.

## 12. Handoff checklist
- [ ] Shared canon distinguished from local context
- [ ] New-house orientation and bibliography provenance included when relevant
- [ ] Unverified claims labeled
- [ ] Open work and blockers recorded
- [ ] Permissions independently re-authorized
- [ ] DCO policy and approved sign-off identity carried forward
- [ ] Recipient identity/provenance not inherited from this record
