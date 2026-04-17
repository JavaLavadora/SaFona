# Handoff Report: Na Francina -- Deliverable Planning (Phase 1)

**Date**: 2026-04-17
**Author**: Na Francina (Project Manager)
**Action**: MODE A -- Deliverable Planning for Phase 1 Vertical Slice

---

## What Was Done

Broke the GDD v3.0 and Software Architecture v1.0 into 10 incremental deliverables covering the Phase 1 vertical slice:
- World 1 complete (4 levels + Es Bou de Pedra boss)
- World 2 stub (1 level to validate Stone Slam in Roman context)
- All core engine systems to support the above

The plan was audited by N'Aina (Auditor) over 2 rounds of review. All critical findings were addressed. The roadmap was written to `docs/implementation_roadmap.md` and a PR created for user approval.

## Planning Process

### Input Analysis

Read the full GDD (v3.0, ~1300 lines) and Software Architecture (v1.0, ~2000 lines). Key takeaways for planning:

1. **Phase 1 scope is well-defined** (GDD Section 1.6): W1 complete + W2 stub. No ambiguity.
2. **W1 has NO masks**: Pure movement + sling combat. This simplifies the first 7 deliverables significantly.
3. **Stone Slam is earned post-boss only**: The mask system, shop, and W2 stub are all gated behind the boss fight.
4. **Architecture is highly modular**: Systems communicate via EventBus, making them relatively independent and allowing parallel development.
5. **Data-driven design**: Everything from economy values to enemy definitions to level layouts lives in JSON. This means data format definitions are as important as code implementations.

### Deliverable Sequencing Rationale

The 10 deliverables follow a strict dependency order on the critical path:

**D1 (Core Engine)** -- Nothing else can exist without the game loop, window, input, scene management, and event bus. This is the foundation.

**D2 (Tilemap, Physics, Camera)** -- The level world. Without tile geometry and physics, nothing can be placed in a level. Camera makes it scrollable.

**D3 (Player & Movement)** -- The first visible, interactive element. This is where the user first sees "a game" -- a character moving in a tile world. Critical for early visual feedback.

**D4 (Sling Combat)** -- The primary gameplay verb. Tap + charge + projectiles. This makes the game feel like a game, not just a movement demo.

**D5 (HUD, Pickups, Economy)** -- Feedback systems. The player needs to see health, collect things, and have a currency system. Parallel with D4.

**D6 (Enemies & Combat)** -- The first opposition. Without enemies, there is no game challenge. Depends on both D4 (sling) and D5 (economy for drops).

**D7 (Dialogue & Companion)** -- The narrative layer. Bep's hints are the tutorial mechanism. Parallel with D4-D6.

**D8 (W1 Levels)** -- Content. The four levels use all systems from D1-D7. This is where level design meets engine.

**D9 (Boss)** -- The climax. Tests all systems working together. The most complex single entity.

**D10 (Masks, Shop, Save, W2)** -- The reward loop. This completes the vertical slice by showing the "earn mask -> use mask" progression.

### Audit Iterations

**Round 1 (8 findings):**
- 5 accepted (EventBus in D1, SpriteRenderer in D1, merge InputHandler into D1, merge Tilemap+Physics+Camera, LevelLoader in D2)
- 2 rejected with reasoning (D10 size: keep as one deliverable; integration checkpoint: boss IS the integration test)
- 1 accepted (shield behavior scoped to D10, not D6)

**Round 2 (5 findings):**
- 2 acknowledged (parallel opportunities, MaskSystem scope)
- 1 confirmed intentional (no audio in Phase 1)
- 1 accepted (economy.json incremental definition)
- 1 rejected with reasoning (integration checkpoint redundant with D9)

No Round 3 was needed -- N'Aina approved after Round 2.

## Decisions Made

1. **10 deliverables, not more**: Resisted the temptation to split further. Each deliverable produces a demonstrable increment. Fewer than 10 would make individual deliverables too large to review.

2. **D10 stays large**: The alternative was 2-3 smaller deliverables, but the mask + shop + save + W2 flow only makes sense as an integrated experience. The payoff of Phase 1 is the complete loop.

3. **No audio in Phase 1**: AudioManager exists in the architecture but is not worth implementing until real assets or placeholder generation is needed. Silence is fine for a vertical slice.

4. **Level Select deferred to Phase 2**: The GDD describes level select and replay, but Phase 1 is a linear experience (W1-L1 through W2-L1). Level select adds complexity without answering the vertical slice questions.

5. **Special ammo deferred to Phase 2**: The GDD describes explosive/piercing/frozen rocks, but these unlock in W2+ and are not needed for the Phase 1 vertical slice.

6. **Consumable system is minimal in Phase 1**: Only ensaimada (heal 2 hearts) and heart upgrade 1 are available. The full consumable system with buffs and refund mechanics is D10 scope but kept simple.

## Open Questions

None at this time. All design questions from the GDD and architecture have been resolved in their respective Issues. If implementation reveals gaps, they will be filed as new Issues.

## Risks

1. **D10 scope creep**: D10 is the largest deliverable. If the mask + shop + save + cutscene + W2 stub integration proves harder than expected, it may need to be split during implementation. Mitigation: N'Andreu can flag this early in the PR.

2. **Movement feel**: D3 is the first moment where "does the game feel good?" can be answered. If movement feels wrong, it may require iteration before proceeding. Mitigation: movement parameters are in settings.py for easy tuning.

3. **Boss complexity**: Es Bou de Pedra has 3 phases with 7 attack patterns. This is a complex entity. Mitigation: the boss JSON format is well-defined in the architecture, and the phased approach (each phase is a set of patterns) lends itself to incremental implementation.

## Current State

- Roadmap written to `docs/implementation_roadmap.md`
- PR created for user review
- NO work has been assigned to developers
- Waiting for user approval before D1 begins

## What's Next

Once the user approves the roadmap:
1. Create GitHub Issue for D1
2. Assign D1 to N'Andreu
3. Update roadmap to show D1 as "In Progress"
4. After D1 is delivered and verified, proceed to D2 (and potentially D5/D7 in parallel once D3 is done)
