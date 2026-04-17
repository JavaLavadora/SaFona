# Handoff Report: Design Decisions #10-13

> **Author**: En Miquel (Software Architect)
> **Date**: 2026-04-16
> **Branch**: `feature/architecture-design-decisions`
> **PR**: #15
> **Issues Closed**: #10, #11, #12, #13

---

## What Was Produced

- Updated `docs/software_architecture.md` with 4 design decisions marked as "Decided"
- Added 2 new extension points (6.10 and 6.11) documenting future extensibility paths
- Commented on and closed all 4 GitHub issues
- Created PR #15 targeting master

---

## Decisions Applied

### Issue #10 -- Level File Format: Custom JSON (Decided)

**Decision**: Custom JSON is the level file format. No runtime TMX parsing.

**Rationale**: Full control over the schema, no external dependency on Tiled libraries, and the format is already thoroughly defined in Section 4.1 of the architecture. If En Tomeu (Level Designer) later needs a visual editor, a Tiled-to-JSON converter script can be added as a dev tool without changing the engine.

**Changes**: Added "Decided" callout in Section 4.1.

### Issue #11 -- Hot-Reload Scope: economy.json + audio_config.json Only (Decided)

**Decision**: Hot-reload is limited to `economy.json` and `audio_config.json`. Other data files require a level/game restart.

**Rationale**: These two files are the most frequently tweaked during playtesting (balance values and audio). Full hot-reload of all data files (levels, enemies, masks, dialogue) would require file watchers, careful state management to avoid mid-level inconsistencies, and significant engineering time -- all for marginal benefit since level restart is fast.

**Changes**: Added "Decided" callout after Section 3.10 (EconomySystem). No code-level changes needed; the architecture already had the correct `reload_config()` methods.

### Issue #12 -- Consumable Usage: Pause Menu Only (Decided)

**Decision**: Consumables are used exclusively via the pause menu. No quick-use keybind. The ConsumableSystem interface is designed to be keybind-agnostic so a quick-use feature can be added later without refactoring.

**Rationale**: Pause-menu-only usage preserves the tension loop -- the player must deliberately pause to heal, which creates a meaningful cost to using consumables. This prevents consumable spam during combat and maintains the retro game feel. The `use_item()` method accepts no input-source parameter, making it callable from any future context.

**Changes**:
- Section 3.14: Added "Decided" callout and updated ConsumableSystem docstring
- Section 3.14: Updated `use_item()` docstring to note input-agnosticism
- Section 5: Annotated `scenes/pause.py` as the consumable usage entry point
- Section 6.10: New extension point "Adding a Quick-Use Keybind for Consumables (Future)" with step-by-step instructions

### Issue #13 -- Save Slots: Single Slot (Decided)

**Decision**: Single save slot. The SaveSystem takes `save_path` as a constructor parameter, so multi-slot support is a UI-only change later.

**Rationale**: Building multi-slot infrastructure now (slot selection UI, slot management, slot deletion) wastes time that should go toward the vertical slice. The `save_path` parameter already provides the extensibility hook -- adding slots later means creating a slot selection scene that passes different file paths.

**Changes**:
- Section 1: Updated Technical Constraints table
- Section 3.11: Added "Decided" callout and updated SaveSystem docstring
- Section 6.11: New extension point "Adding Multiple Save Slots (Future)" with step-by-step instructions

---

## Trade-offs and Considerations

1. **Extension points as documentation**: By adding Sections 6.10 and 6.11, future developers have a clear recipe for adding quick-use keybinds and multiple save slots. This is cheaper than building the features now, while ensuring the architecture does not accidentally close off these paths.

2. **No code changes**: All 4 decisions resulted in documentation-only changes. The architecture was already designed with these extensibility paths in mind; the decisions simply confirmed and documented them.

3. **Callout formatting**: Used blockquote "Decided" callouts rather than inline text to make decisions visually scannable in the architecture document. Each callout references the issue number for traceability.

---

## Open Questions

None. All 4 design questions are now resolved.

---

## Next Steps

- PR #15 needs review from En Pau (Senior Engineer) and merge to master
- Na Francina (PM) can proceed with breaking the architecture into deliverables
- N'Aina (Auditor) can audit the implementation plan knowing these decisions are final
