# Project Ideas & Todo

Freeform backlog of ideas and future improvements. Not tied to any active sprint.

---

## Gameplay Mechanics

### NPC Conversation Pressure System
Instead of binary "on-topic / off-topic", model NPC engagement as a **continuum**:

- One axis: **pushiness** (how hard the player is pressing for information)
- Other axis: **relevance** (how on-topic the conversation is)
- The sweet spot is the **middle** — too pushy and the NPC gets defensive/suspicious; too off-topic and you burn turns without gaining intel
- Could surface as a visual meter or purely through NPC dialogue tone shifts
- Makes conversations feel like a real social skill challenge rather than a quiz

---

## Quick Start Scenarios (Pre-Baked)

Pre-generate 2–3 "ready to play" scenarios per player count so the game starts instantly — no generation wait, no role picking confusion.

### Concept
Each quick scenario is a fixed bundle: scenario ID + role set + all generated files already committed to the repo. Players open the app, tap a player count, see 2–3 scenario cards, pick one, claim a role from the fixed cast, and hit go.

### Pre-baked bundles (proposed)
| Players | Scenario | Roles |
|---------|----------|-------|
| 2 | Museum Heist | Hacker + Mastermind |
| 2 | Bank Vault | Safe Cracker + Driver |
| 3 | Museum Heist | Hacker + Mastermind + Lookout |
| 3 | Train Robbery | Muscle + Grifter + Fence |
| 4 | Museum Gala Vault | Hacker + Mastermind + Cat Burglar + Insider |
| 4 | Casino | Mastermind + Pickpocket + Grifter + Lookout |

### What "pre-baked" includes per scenario
- `experiences/generated_{id}_{roles}.md` + `.json` — scenario graph
- `generated_images/{id}/` — NPC portraits + location scene images
- Validated: playability sim passes, 0 critical issues

### Open questions
- Do we version/checksum pre-baked files so we know when they're stale after generator changes?
- Should the frontend show a "Custom Game" path separately from "Quick Start" to keep the UI clean?
- Do pre-baked scenarios need a short flavor description + cover image on the selection card?

---


