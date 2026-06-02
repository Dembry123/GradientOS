# Agent Scratchpad

Use this file as persistent, repo-local execution memory.

## File Policy

- Current policy: `COMMITTED`
- Rationale:
  - The user explicitly asked for persistent use of scratchpad/devlog skills and visible top-level references.

## How To Use

1. Read latest entries before starting meaningful work.
2. Build a short preflight checklist from recurring mistakes and preferences.
3. Re-read before risky operations (migrations, broad refactors, unfamiliar tooling, destructive commands).
4. Log high-signal learnings immediately during the task.
5. Append one new session entry before handoff.
6. Keep entries concrete, concise, and testable.

## Entry Rules

- Tag operational notes with source: `[self]`, `[user]`, or `[tool]`.
- Prefer facts tied to files, commands, and outcomes.
- Do not log low-signal reminders.

## Retained Lessons

- [user] Prefer implementation over discussion; "do it, do not only explain."
- [user] UI preferences are specific and iterative; keep changes minimal and visual hierarchy clean.
- [tool] Build and lint checks (`npm run build`, `ReadLints`) catch regressions quickly in the web-ui workflow.

## Session Entries

### 2026-02-16 00:14 +11:00 - Sidebar UX refinement and workflow persistence

#### Task Summary

- Adjusted drawer close-button placement and panel framing behavior per user screenshot feedback.
- Kept robot control right-docked and collapsible.
- Added explicit top-level workflow pointers and persistent memory files.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Initial close-button placement still appeared outside the panel because drawer width did not match panel width behavior.
- Detection:
  - User screenshot showed the close icon floating outside the card boundary.
- Fix:
  - Synchronized drawer width to panel scale and repositioned close button offsets.
- Preventive rule:
  - When overlay controls must align with a child card, validate parent width/position assumptions before tweaking z-index/offsets.

#### User Preferences

- New or reinforced preference:
  - Keep close controls on the same line as the panel title area.
  - Remove redundant visual framing (no duplicate outer border effect).
  - Keep robot control aligned on the right and collapsible.
  - Always maintain devlog/scratchpad workflow and keep `.cursor/skills` references visible.
- How it changed execution:
  - Prioritized layout simplification and added top-level workflow references.

#### What Worked

- Pattern/check that worked:
  - Small targeted CSS/class updates in drawer wrapper and deterministic build verification.

#### What Did Not Work

- Failed attempt and why:
  - Width-only tweak without checking `w-full max-w-*` interactions can leave floating controls misaligned.

#### Guardrails For Next Session

- Preflight rule:
  - Read this scratchpad + `DEVLOG.md` first, then align any overlay control to the actual rendered panel width before finalizing.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Confirm visual alignment at multiple viewport sizes after future panel style changes.

### 2026-02-16 00:20 +11:00 - Prevent tab lock from tree sync

#### Task Summary

- Fixed behavior where loading STEP or existing tree selection auto-forced Weld tab.
- Restored manual tab switching while preserving weld/tree selection sync.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Program-tree synchronization effect controlled `activePanel`, unintentionally overriding user tab changes.
- Detection:
  - User reported automatic tab jump to Weld and inability to switch tabs afterward.
- Fix:
  - Removed panel-forcing from tree-sync effect; moved panel-open behavior to explicit tree click handler.
- Preventive rule:
  - Keep sync effects state-specific (selection-to-selection), and keep view-navigation state controlled only by explicit user actions.

#### User Preferences

- New or reinforced preference:
  - Loading a STEP model must not auto-navigate to Weld.
  - User must be able to switch tabs freely at all times.
- How it changed execution:
  - Prioritized decoupling `activePanel` from background sync logic.

#### What Worked

- Pattern/check that worked:
  - Isolating tree sync side effects and validating with build quickly confirmed fix stability.

#### What Did Not Work

- Failed attempt and why:
  - Coupling panel navigation to derived tree focus caused repeated tab override loops.

#### Guardrails For Next Session

- Preflight rule:
  - Before adding `useEffect` state sync, verify it cannot override explicit user UI navigation state.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If new tree node types introduce `openPanel`, ensure only direct selection handlers apply that field.

### 2026-02-16 21:51 +11:00 - Multi-select edge flicker and panel-control placement

#### Task Summary

- Moved STEP Import `Reset Pose` control to the bottom of the panel.
- Fixed tree/weld synchronization conflict that could cause active segment flicker when two edges were selected.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Bidirectional sync lacked interaction-source gating, allowing tree and weld selection effects to fight each other.
- Detection:
  - User reported flickering behavior when two lines/segments were selected.
- Fix:
  - Added `panelSelectionOriginRef` and only applied tree->weld active-segment sync when selection originated from tree clicks.
- Preventive rule:
  - For bidirectional UI sync, always track source-of-truth per interaction to prevent feedback loops.

#### User Preferences

- New or reinforced preference:
  - Keep key panel actions (e.g. `Reset Pose`) at intuitive positions near related transform controls.
- How it changed execution:
  - Repositioned control directly in `StepImportPanel` footer.

#### What Worked

- Pattern/check that worked:
  - Interaction-origin refs are a lightweight, reliable way to stop cross-effect oscillation in React state sync.

#### What Did Not Work

- Failed attempt and why:
  - Pure dependency-based effects without origin markers were insufficient for multi-source selection flows.

#### Guardrails For Next Session

- Preflight rule:
  - When implementing two-way sync between panels/tree/scene, define and enforce a source tag before writing effects.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If GPU-specific flicker remains, replace selected line rendering with a single authoritative overlay layer and suppress base-line rendering for selected edges.

### 2026-02-17 10:32 +11:00 - Enforce automatic scratchpad and devlog context

#### Task Summary

- Added a repo-level Cursor rule to make scratchpad/devlog workflow mandatory for all meaningful tasks.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Relying on optional workflow habits instead of enforcing them through an always-apply project rule.
- Detection:
  - User explicitly requested both loops be automatic in every agent session.
- Fix:
  - Added `.cursor/rules/agent-memory-loops.md` with start/during/end requirements for both files.
  - Updated `.cursor/rules/agent-gated-checklist.md` to require scratchpad/devlog read at Gate 0 and writeback at Gate 7.
- Preventive rule:
  - When the user asks for persistent agent behavior, encode it in `.cursor/rules` instead of relying on ad-hoc reminders.

#### User Preferences

- New or reinforced preference:
  - Always use and update both `AGENT_SCRATCHPAD.md` and `DEVLOG.md`.
- How it changed execution:
  - Implemented an always-apply rule and logged this change in both memory files immediately.

#### What Worked

- Pattern/check that worked:
  - Converting skill guidance into a concise always-apply rule provides durable enforcement across sessions.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this task.

#### Guardrails For Next Session

- Preflight rule:
  - Before substantial edits, read `AGENT_SCRATCHPAD.md` + `DEVLOG.md`; before handoff, append both.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Existing active sessions may need a fresh prompt/turn to fully align with newly added rule text.

### 2026-02-17 10:45 +11:00 - Explicit skill-to-file pointers for memory loops

#### Task Summary

- Added explicit references linking each memory file to its owning skill and template.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Previous rule text enforced the workflow but did not explicitly map the exact skill files and templates.
- Detection:
  - User asked to point to the specific skills and files.
- Fix:
  - Updated `.cursor/rules/agent-memory-loops.md` with required skill/template/file mapping.
  - Updated `QUICK_START.md` workflow pointers with direct skill-to-file paths.
- Preventive rule:
  - When documenting persistent behavior from skills, always include concrete source-skill paths and destination files.

#### User Preferences

- New or reinforced preference:
  - Keep explicit references to the exact skills and the files they manage.
- How it changed execution:
  - Added direct path mapping in both the always-apply rule and top-level quick-start docs.

#### What Worked

- Pattern/check that worked:
  - Short path mapping bullets remove ambiguity and make compliance auditable in one glance.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this task.

#### Guardrails For Next Session

- Preflight rule:
  - If a process is skill-driven, verify docs include both `SKILL.md` path and target file path.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - None identified for this documentation update.

### 2026-02-17 00:12 +11:00 - Duplicate skill mapping across all always-on rules

#### Task Summary

- Added explicit scratchpad/devlog skill-to-file mapping blocks to all `alwaysApply: true` rule files.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Mapping existed in only part of the rule set, leaving room for inconsistent context anchoring.
- Detection:
  - User explicitly requested this be added to the rules (plural) so it is always in context.
- Fix:
  - Updated `.cursor/rules/agent-gated-checklist.md`, `.cursor/rules/agent-ambiguity-triggers.md`, `.cursor/rules/agent-subagents.md`, and `.cursor/rules/rtos-ethercat-readme.md` with the same required mapping block.
- Preventive rule:
  - For mandatory context anchors, mirror the same source-of-truth mapping across every `alwaysApply` rule file.

#### User Preferences

- New or reinforced preference:
  - Keep scratchpad/devlog skill links explicitly present across the entire always-on rule surface.
- How it changed execution:
  - Applied a repeated mapping section to each always-apply rule, not just memory-focused docs.

#### What Worked

- Pattern/check that worked:
  - Uniform, copy-identical mapping sections reduce ambiguity and audit time.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this task.

#### Guardrails For Next Session

- Preflight rule:
  - When user says "always in context," verify all `alwaysApply` rules carry the same mandatory pointers.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If new `alwaysApply` rules are added later, they must include the same mapping block.

### 2026-02-17 00:41 +11:00 - Weld Motion + Tree UX delivery and checklist compliance fix

#### Task Summary

- Delivered full requested pass:
  - compact + chronological Program Tree UX
  - weld section planning with transitions
  - torch-angle controls (UI -> API -> planner)
  - planner robustness and diagnostics.
- Closed workflow loop by writing explicit session entries to both `DEVLOG.md` and `AGENT_SCRATCHPAD.md`.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Completed feature implementation but initially missed the two trailing checklist items (memory writeback + future backlog todo creation).
- Detection:
  - User called it out directly ("last 2 on the list ... didn't touch").
- Fix:
  - Immediately added memory-loop writeback entry to both files and created explicit future backlog tracking todo.
- Preventive rule:
  - Before handoff, verify every visible checklist/todo item (including process tasks) is handled, not just code tasks.

#### User Preferences

- New or reinforced preference:
  - Process tasks are first-class requirements; do not skip memory/devlog updates when explicitly listed.
  - Strong preference for direct execution over explanation-only updates.
- How it changed execution:
  - Added explicit final pass for process compliance and backlog traceability in the same turn.

#### What Worked

- Pattern/check that worked:
  - Section-based weld planning model (`weld` vs `transition`) made it practical to implement contiguous weld continuation and safe-lift transitions without a full collision engine.
  - Runtime fallback from torch-angle orientation solve to orientation-lock avoided planner hard-fails.

#### What Did Not Work

- Failed attempt and why:
  - Strict torch-angle orientation path can be IK-infeasible on some geometries; required fallback behavior to keep planning usable.

#### Guardrails For Next Session

- Preflight rule:
  - Track implementation to-dos and workflow to-dos separately, and do a final checklist sweep that includes both.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Full collision-aware transition planner is still pending and should replace heuristic safe-lift logic in a future phase.

### 2026-02-17 00:47 +11:00 - Viewport-clamped sidebar drawer

#### Task Summary

- Fixed menu overflow issue where left drawer panels could exceed the viewport height.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Drawer container allowed unconstrained vertical growth when panel content (especially Weld panel with long waypoint lists) got tall.
- Detection:
  - User screenshot and explicit feedback: "can't let menus grow larger than window size."
- Fix:
  - Added viewport max-height and internal scroll behavior in `web-ui/src/components/SidebarDrawer.tsx`.
- Preventive rule:
  - Any absolute overlay panel should define a viewport max-height and internal scrolling before adding content-heavy sections.

#### User Preferences

- New or reinforced preference:
  - Keep side menus fully contained within the visible window.
- How it changed execution:
  - Prioritized layout containment fix over feature additions.

#### What Worked

- Pattern/check that worked:
  - Applying max-height at the shared drawer wrapper fixed all drawer-hosted panels at once.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this task.

#### Guardrails For Next Session

- Preflight rule:
  - For UI overlays, validate worst-case content height against viewport before handoff.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If non-drawer floating panels are expanded in future, they may need the same containment pattern.

### 2026-02-17 00:50 +11:00 - Drawer header overlap guard band

#### Task Summary

- Fixed a visual overlap where the drawer close button covered panel header controls on the right side.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - The close button was absolutely positioned over content with insufficient reserved horizontal space.
- Detection:
  - User reported overlap and shared screenshot showing Weld badge collision near the close icon.
- Fix:
  - Added a right-side content guard band in `web-ui/src/components/SidebarDrawer.tsx` by increasing inner wrapper padding to `pr-10`.
- Preventive rule:
  - Any persistent overlay control (close/help/action) must reserve explicit layout space rather than relying on visual luck.

#### User Preferences

- New or reinforced preference:
  - UI controls must never overlap; title/header actions must remain readable and clickable.
- How it changed execution:
  - Prioritized spacing/layout correction over adding new interactions.

#### What Worked

- Pattern/check that worked:
  - Shared-container spacing fixes in one wrapper corrected multiple panel variants without touching feature-specific components.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this task.

#### Guardrails For Next Session

- Preflight rule:
  - For absolute-positioned controls, verify both vertical and horizontal guard space at smallest supported drawer width.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If header content density increases (more badges/buttons), migrate to an explicit shared drawer header row to keep spacing deterministic.

### 2026-02-17 00:53 +11:00 - Escalation handoff note for next model

#### Task Summary

- Added a high-priority takeover TODO in `QUICK_START.md` so a new model can continue unresolved UI overlap cleanup immediately.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Prior spacing fix did not meet user quality expectations.
- Detection:
  - Direct user feedback: overlap still unacceptable.
- Fix:
  - Wrote explicit handoff requirements + acceptance criteria at the top of `QUICK_START.md` to avoid context loss across model handoff.
- Preventive rule:
  - When user asks for takeover, document exact failure mode + required end-state in a top-level onboarding doc.

#### User Preferences

- New or reinforced preference:
  - Do not paper over visual defects; require robust layout fixes.
- How it changed execution:
  - Prioritized cross-model continuity and clear ownership transfer instructions.

#### What Worked

- Pattern/check that worked:
  - A concrete handoff checklist in `QUICK_START.md` gives immediate actionability for the next model.

#### What Did Not Work

- Failed attempt and why:
  - Padding-only overlap mitigation was not perceived as a complete fix.

#### Guardrails For Next Session

- Preflight rule:
  - For overlay/header defects, prefer structural layout changes (shared header row) over spacing-only adjustments.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - The actual UI fix is still pending; this entry only captures handoff context.

### 2026-02-17 19:27 +11:00 - Shared drawer header row implementation

#### Task Summary

- Implemented structural drawer-header fix from `QUICK_START.md` to prevent overlap between header content and close control.
- Moved weld title/badge into shared drawer header surface and removed duplicate in-panel title rows.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Earlier workaround depended on right-side padding (`pr-10`) while keeping close action absolutely positioned.
- Detection:
  - User screenshot + takeover note confirmed overlap remained unacceptable in real weld-header content.
- Fix:
  - Replaced overlay close action with a dedicated `SidebarDrawer` header row (`headerContent` + close button) so layout guarantees non-overlap.
- Preventive rule:
  - For any dismiss/action control near dynamic header content, use structural row layout with flex constraints (`min-w-0`, `shrink-0`) instead of padding buffers.

#### User Preferences

- New or reinforced preference:
  - UI fixes should be robust by structure, not spacing hacks.
  - "Implement, do not only explain" remains the default execution style.
- How it changed execution:
  - Applied direct component refactor and validation in the same turn instead of proposing-only guidance.

#### What Worked

- Pattern/check that worked:
  - Centralizing header composition in `SidebarDrawer` allowed one fix to cover all panel types while keeping panel body logic unchanged.
  - Immediate `npm run build` + `ReadLints` checks caught regressions quickly.

#### What Did Not Work

- Failed attempt and why:
  - Keeping titles in both drawer header and panel cards created duplicated heading surfaces; removed duplicated panel titles where appropriate.

#### Guardrails For Next Session

- Preflight rule:
  - If a shared container now owns a title area, remove duplicate in-panel titles unless they carry unique controls.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Perform visual verification at narrow window widths to confirm spacing and interaction feel for all drawer panels in live UI.

### 2026-02-17 20:34 +11:00 - Drawer bottom inset alignment + AGENTS skill catalog refresh

#### Task Summary

- Corrected left drawer vertical sizing so it keeps a bottom inset instead of visually running to the edge.
- Updated `AGENTS.md` to reflect the rename from `QUICK_START.md` and documented all installed skills with usage triggers.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Previous drawer height model used viewport-based max-height math, which could feel mismatched with sibling overlays in a header+main layout.
- Detection:
  - User screenshot highlighted asymmetry between the left drawer and right robot-control panel bottom spacing.
- Fix:
  - Refactored drawer container to inset-based vertical layout (`inset-y-6`) with `flex` + `min-h-0`; retained scroll using `flex-1 overflow-y-auto`.
- Preventive rule:
  - For overlay alignment across a shared surface, prefer consistent positional insets (`top/bottom`) over independent max-height calculations.

#### User Preferences

- New or reinforced preference:
  - Visually related overlays should have matching baseline/inset behavior.
  - Agent docs must stay current when top-level onboarding files are renamed.
  - Design-oriented skill usage should be explicit and discoverable.
- How it changed execution:
  - Applied layout fix first, then codified full skill relevance in `AGENTS.md`.

#### What Worked

- Pattern/check that worked:
  - `inset-y-*` + `flex-1` scroll gives deterministic alignment while preserving long-content usability.
  - Using `frontend-design` guidance for implementation direction and `web-design-guidelines` guidance for post-change review framing kept UI decisions intentional.

#### What Did Not Work

- Failed attempt and why:
  - Treating drawer max-height independent of main container created perceived edge contact even when scroll technically worked.

#### Guardrails For Next Session

- Preflight rule:
  - If two overlay panels are expected to align, compare both vertical anchors (`top`, `bottom`, internal scroll shell) before finalizing styles.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Confirm final visual balance during live interaction at very small window heights and high content density.

### 2026-02-17 20:41 +11:00 - Themed drawer scrollbar styling

#### Task Summary

- Replaced default browser-style drawer scrollbar with a custom theme-matched scrollbar.
- Kept behavior cross-browser by styling both Firefox and WebKit engines.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Previously left the primary drawer scroller unstyled, which looked inconsistent with the polished panel visual design.
- Detection:
  - User feedback with screenshot: "scrollbar is ugly" and requested UI-consistent styling.
- Fix:
  - Added reusable `.gradient-scrollbar` utility in `web-ui/src/index.css` and applied it to the drawer scroll shell in `SidebarDrawer.tsx`.
- Preventive rule:
  - Any prominent always-visible scrollbar in core UI panels should receive explicit theme styling and not rely on OS defaults.

#### User Preferences

- New or reinforced preference:
  - Styling details (including scrollbars) must match the overall interface quality bar.
- How it changed execution:
  - Prioritized direct visual polish in production code with immediate build/lint validation.

#### What Worked

- Pattern/check that worked:
  - Utility-class approach (`gradient-scrollbar`) makes it easy to reuse consistent scrollbar styling across other scrollable panel sections.
  - Combining Firefox and WebKit declarations ensures broad browser coverage.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this change.

#### Guardrails For Next Session

- Preflight rule:
  - For UI polish requests, inspect for native browser defaults (scrollbars, focus rings, select arrows) and theme them where they are visually dominant.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If users request thicker or subtler scrollbar contrast, tune width/color alpha in `.gradient-scrollbar` rather than duplicating new classes.

### 2026-02-17 20:49 +11:00 - Scrollbar integrated into rounded drawer shell

#### Task Summary

- Integrated header and scroll body into a single drawer shell so the scrollbar appears inside the panel.
- Ensured rounded bottom corners remain visible regardless of scroll position.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Scroll region still sat outside the main framed shell, making the scrollbar appear detached and corners feel inconsistent.
- Detection:
  - User screenshot highlighted scrollbar placement and requested persistent rounded bottom corners while scrolling.
- Fix:
  - Reworked `SidebarDrawer` to a single `rounded-xl overflow-hidden` container with internal header and body scroller.
- Preventive rule:
  - If users ask for persistent corner shape during scrolling, clipping must happen at the outermost rounded container.

#### User Preferences

- New or reinforced preference:
  - Scrollbar should feel like part of the panel, not adjacent to it.
  - Rounded geometry should remain stable at all scroll offsets.
- How it changed execution:
  - Prioritized container hierarchy/layout over color-only styling tweaks.

#### What Worked

- Pattern/check that worked:
  - One-shell layout with `border-b` header divider gives cleaner structure and deterministic corner clipping.

#### What Did Not Work

- Failed attempt and why:
  - Styling the scrollbar alone without container clipping did not fully solve the visual integration request.

#### Guardrails For Next Session

- Preflight rule:
  - For any scrollable card/panel, confirm the scroll container is nested inside the same rounded element that defines the visual frame.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Optional future polish: reduce nested card framing inside drawer bodies if a flatter visual style is desired.

### 2026-02-17 21:28 +11:00 - Weld typography consistency normalization

#### Task Summary

- Applied a consistent font-size system to the Weld panel (labels, metadata, section headings, inputs, and action text).
- Kept CTA emphasis while reducing random micro-size jumps in the rest of the panel.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Weld UI accumulated mixed ad-hoc text sizes (`text-xs`, `text-[11px]`, `text-[10px]`) without shared typography tokens.
- Detection:
  - User requested consistent styling/sizing and screenshot showed uneven typography rhythm.
- Fix:
  - Added shared weld typography class constants in `App.tsx` and refactored key Weld panel elements to use them.
- Preventive rule:
  - For dense forms, define reusable typographic tokens first, then apply them consistently instead of per-control one-off sizing.

#### User Preferences

- New or reinforced preference:
  - Typography should feel intentionally consistent, not piecemeal.
- How it changed execution:
  - Prioritized text hierarchy cleanup (label/meta/control consistency) immediately after structural layout fixes.

#### What Worked

- Pattern/check that worked:
  - Local constants for panel typography made broad consistency changes safer and easier to review.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this update.

#### Guardrails For Next Session

- Preflight rule:
  - When touching any large panel, run a quick typography pass to ensure no unnecessary size variants remain.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - STEP and Trajectory panels may still contain independent typography choices and can be normalized in a dedicated follow-up.

### 2026-02-17 21:31 +11:00 - Text hierarchy correction for section title vs field label

#### Task Summary

- Adjusted typography hierarchy so `Weld Program` (section title) and `Program Name` (field label) are visually distinct.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Initial typography normalization still left section title and label weights too close, reading as both bold in practice.
- Detection:
  - User feedback called out both lines appearing bold despite hierarchy intent.
- Fix:
  - Set `WELD_LABEL_CLASS` to normal weight and strengthened `WELD_SECTION_TITLE_CLASS` size/contrast for clearer hierarchy.
- Preventive rule:
  - After typographic refactors, verify key adjacent text pairs (section title vs label) in rendered UI, not just by class names.

#### User Preferences

- New or reinforced preference:
  - Visual hierarchy should be obvious; labels should not compete with section headings.
- How it changed execution:
  - Applied immediate token-level correction instead of adding more one-off local class overrides.

#### What Worked

- Pattern/check that worked:
  - Centralized typography constants enabled a quick, low-risk hierarchy adjustment.

#### What Did Not Work

- Failed attempt and why:
  - Equalized sizing pass alone did not guarantee perceived hierarchy when both styles still had elevated weight.

#### Guardrails For Next Session

- Preflight rule:
  - For dense forms, reserve stronger weight/color for section titles and keep field labels at regular weight unless emphasis is intentional.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Consider applying the same heading-vs-label hierarchy tokens to STEP and Trajectory drawers for full consistency.

### 2026-02-17 21:34 +11:00 - Cross-panel typography alignment + living design doc

#### Task Summary

- Extended typography consistency work from Weld to STEP and Trajectory panels.
- Added `web-ui/design.md` as the living design-system document and referenced it from `AGENTS.md`.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Typography tokenization was initially panel-local (`WELD_*`) and not clearly positioned as a shared drawer system.
- Detection:
  - User approved extending hierarchy consistency across all drawer tabs and requested a persistent living design doc.
- Fix:
  - Introduced shared `DRAWER_*` tokens in `App.tsx` and aligned STEP/Trajectory class usage with those tokens.
  - Created `web-ui/design.md` with rules/checklist and linked it from `AGENTS.md`.
- Preventive rule:
  - When UI consistency request spans multiple panels, establish or update a repo-local design source-of-truth before further styling changes.

#### User Preferences

- New or reinforced preference:
  - Consistency should be systematic and documented, not just fixed one screen at a time.
- How it changed execution:
  - Combined implementation changes with living documentation in the same turn.

#### What Worked

- Pattern/check that worked:
  - Shared token strategy (`DRAWER_*`) allowed quick normalization without major component rewrites.
  - A living doc with checklist creates durable guardrails for future UI edits.

#### What Did Not Work

- Failed attempt and why:
  - N/A for this update.

#### Guardrails For Next Session

- Preflight rule:
  - Before editing drawer panel styles, read `web-ui/design.md` and use existing `DRAWER_*` tokens unless intentionally evolving the design system.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Global typography outside drawer panels still may not fully match the new panel system and can be standardized later.

### 2026-02-17 21:43 +11:00 - Hard requirement language for memory-loop completion

#### Task Summary

- Strengthened `AGENTS.md` so updating both `DEVLOG.md` and `AGENT_SCRATCHPAD.md` is explicitly non-optional.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Existing wording listed both files but was not strong enough to prevent potential omission.
- Detection:
  - User explicitly requested stronger emphasis that these tasks must never be left undone.
- Fix:
  - Added MUST language on both workflow bullets and a non-negotiable blocker rule in `AGENTS.md`.
- Preventive rule:
  - If user says "every time", encode it with explicit "MUST" + "blocker" phrasing in the top-level onboarding doc.

#### User Preferences

- New or reinforced preference:
  - Memory-loop updates are mandatory on every meaningful task with zero exceptions.
- How it changed execution:
  - Immediately hardened policy text in `AGENTS.md` and logged the change in both memory files.

#### What Worked

- Pattern/check that worked:
  - Converting soft guidance into explicit completion criteria reduces ambiguity and missed process steps.

#### What Did Not Work

- Failed attempt and why:
  - Soft descriptive wording ("maintain these files") did not clearly communicate non-negotiable enforcement.

#### Guardrails For Next Session

- Preflight rule:
  - Treat absent updates in either `DEVLOG.md` or `AGENT_SCRATCHPAD.md` as a stop condition before final handoff.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - None for this doc-policy reinforcement; now explicitly codified.

### 2026-02-17 21:46 +11:00 - Remove nested drawer shell for more usable width

#### Task Summary

- Removed the extra inner full-card shell from drawer panel content to eliminate the double-layer frame.
- Increased usable content room in the drawer without changing the outer shell behavior.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Panel content still had a nested full-shell wrapper (rounded/border/bg/shadow) inside the drawer shell, causing visual duplication.
- Detection:
  - User screenshot highlighted unnecessary double layer and requested more content room.
- Fix:
  - Removed root shell classes from drawer panel roots in `App.tsx` and reduced shelling in `TelemetryCharts.tsx`.
  - Added a permanent "no nested outer shell" rule to `web-ui/design.md`.
- Preventive rule:
  - In drawer UIs, keep one primary shell only; use section cards for grouping, not another full wrapper.

#### User Preferences

- New or reinforced preference:
  - Avoid double framing; prioritize cleaner visual hierarchy and usable space.
- How it changed execution:
  - Applied structural class removal instead of spacing-only patching.

#### What Worked

- Pattern/check that worked:
  - Removing duplicated shell classes immediately reduced visual noise and reclaimed width.

#### What Did Not Work

- Failed attempt and why:
  - Prior refinements (scrollbar, typography) improved polish but did not remove the underlying duplicated-shell structure.

#### Guardrails For Next Session

- Preflight rule:
  - Before finalizing drawer visuals, verify only one full-shell container exists in the panel stack.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Fine-tune section card spacing if certain panel states appear too sparse after shell removal.

### 2026-02-17 21:50 +11:00 - Adaptive drawer height + wider telemetry panel

#### Task Summary

- Changed drawer sizing behavior so short-content panels no longer stretch to full-height.
- Added a wider drawer width variant for telemetry/charts to avoid horizontal overflow.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Forcing drawer to `inset-y` full height made sparse panels (STEP/Trajectory/Telemetry idle) look mostly empty.
- Detection:
  - User screenshots showed excessive empty vertical space and horizontal scrollbar in charts panel.
- Fix:
  - Switched drawer to content-driven height with viewport max-height cap and internal scroll.
  - Added panel-specific width prop and set telemetry to wider width.
  - Added `overflow-x-hidden` in drawer body to suppress unintended sideways scroll.
- Preventive rule:
  - Drawer height should be content-first with max-height constraints; reserve full-height overlays only for intentionally immersive panels.

#### User Preferences

- New or reinforced preference:
  - Keep max-height safety, but avoid unnecessary empty space in light-content tabs.
  - Charts panel should prioritize readable layout over strict shared-width parity.
- How it changed execution:
  - Implemented adaptive layout plus targeted width override rather than a single global sizing rule.

#### What Worked

- Pattern/check that worked:
  - Width variant via prop (`widthClassName`) cleanly supports per-panel layout needs without duplicating drawer component logic.

#### What Did Not Work

- Failed attempt and why:
  - Earlier one-size full-height behavior suited long Weld content but degraded sparse tabs.

#### Guardrails For Next Session

- Preflight rule:
  - Validate each tab in both sparse and dense states before finalizing shared container sizing.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If telemetry charts add more columns/cards, add responsive width tiers rather than reintroducing horizontal scroll.

### 2026-02-17 22:10 +11:00 - Weld drawer baseline + tooltip clipping regression fix

#### Task Summary

- Fixed Weld drawer vertical sizing so its bottom baseline stays aligned with Robot Control.
- Fixed angle-help tooltip clipping by moving it out of the scroll container into a fixed portal overlay.
- Codified these constraints in `web-ui/design.md`.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Drawer sizing logic shifted between content-driven and max-height variants, causing bottom misalignment and visible clipping near footer-adjacent controls.
  - Tooltip was rendered inside an overflowed panel region, so it got clipped/cut off.
- Detection:
  - User screenshots clearly showed the panel extending into terminal/footer region and tooltip content cut off by panel bounds.
- Fix:
  - Anchored drawer with explicit `top-6` + `bottom-6` and `h-full` shell.
  - Rendered angle explainer tooltip via `createPortal(document.body)` with fixed positioning and viewport clamping.
  - Set tooltip to open on the right by default with left fallback only when viewport space is constrained.
- Preventive rule:
  - Never place explainer popovers inside scrolling/clipped containers; use portal overlays for any panel-help UI.
  - For consistency-critical overlays, align by shared anchor insets rather than mixing content-height and max-height modes.

#### User Preferences

- New or reinforced preference:
  - Strong preference for consistent panel baselines and no clipped UI.
  - When regressions are reported with screenshots, prioritize direct fixes over exploratory redesign.
- How it changed execution:
  - Moved from incremental class tweaks to hard layout anchoring + portalized overlay behavior.

#### What Worked

- Pattern/check that worked:
  - Using `absolute top-6 bottom-6` + internal scroll gives stable, predictable panel bounds across dense Weld content.
  - Portal + fixed positioning immediately removed tooltip clipping from drawer overflow constraints.

#### What Did Not Work

- Failed attempt and why:
  - Intermediate max-height-only tuning was not robust; it still produced inconsistent bottoms in real viewport states.

#### Guardrails For Next Session

- Preflight rule:
  - For all floating panels, verify top and bottom anchors against adjacent UI baselines before finalizing.
  - For tooltips/popovers inside drawers, require portal rendering and viewport-bound checks by default.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If additional help popovers are added, they must reuse the same portal + clamp pattern to avoid repeat clipping regressions.

### 2026-02-17 22:24 +11:00 - Weld end-action semantics correction

#### Task Summary

- Corrected weld post-action behavior so `return_to_start` means return to trajectory start/home-start pose (not weld start).
- Added new post-action mode `lift` for a small vertical retract from weld end.
- Synced backend planner semantics, API normalization, and UI enum/options.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Existing `return_to_start` behavior returned to the first weld point, which is semantically wrong for full-trajectory flow.
- Detection:
  - User provided explicit behavior definition + annotated image showing desired home-start target.
- Fix:
  - Removed frontend section-level weld-start return insertion.
  - Implemented backend post-action planning in `command_api.py`:
    - `return_to_start` now routes from weld end back to trajectory start pose (captured at planning start), using a lifted transition.
    - `lift` now performs a vertical retract by transition clearance.
  - Added `lift` normalization in `main.py` and UI type/select handling in `App.tsx`.
- Preventive rule:
  - End-action semantics must be owned by backend planner state (which has true start pose), not pre-baked by frontend geometry assumptions.

#### User Preferences

- New or reinforced preference:
  - "Return to start" must always refer to trajectory/program start, not local weld segment start.
  - Add practical post-weld finishing action(s) like lift for safer motion behavior.
- How it changed execution:
  - Prioritized behavior semantics over UI-only labeling and implemented planner-level logic.

#### What Worked

- Pattern/check that worked:
  - Centralizing end-action logic in backend keeps preview/execution behavior consistent and source-of-truth aligned.

#### What Did Not Work

- Failed attempt and why:
  - Previous frontend-only return transition generation could not represent trajectory start correctly because it lacked planner start-pose context.

#### Guardrails For Next Session

- Preflight rule:
  - For any motion semantic label (`return`, `home`, `safe`), verify mapping against planner/control definitions before shipping UI text.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If a dedicated configurable "home" waypoint is introduced later, `return_to_start` should explicitly choose between recorded trajectory start vs configured home target.

### 2026-02-17 22:57 +11:00 - Weld-program load must clear stale preview state

#### Task Summary

- Fixed stale path rendering when loading saved weld programs that do not include a planned trajectory payload.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Loading `test_0` could leave the previous preview path visible because restore logic only set new preview when present, but did not clear old preview when missing.
- Detection:
  - User reported loaded program retained prior plan/path visuals.
- Fix:
  - In weld-program restore path, explicitly clear `previewPlan` + `plannerPoints` when `pendingWeldProgramRestore.previewPlan` is null.
  - Also clear `previewPlan` + `plannerPoints` immediately after successful program payload validation so stale geometry is removed during restore.
- Preventive rule:
  - Any optional payload restore must include explicit "else clear" handling for stateful visuals.

#### User Preferences

- New or reinforced preference:
  - Loading a saved program must never retain stale path overlays from previous sessions/plans.
- How it changed execution:
  - Prioritized deterministic state reset behavior over preserving transient UI visuals between loads.

#### What Worked

- Pattern/check that worked:
  - Clearing both source states (`previewPlan` and `plannerPoints`) ensures visual path fallback logic cannot display old geometry.

#### What Did Not Work

- Failed attempt and why:
  - Implicit state replacement only on "truthy new plan" left stale values alive in null-plan restore cases.

#### Guardrails For Next Session

- Preflight rule:
  - For every restore/load flow, enumerate each visual state and handle both "present" and "absent" payload branches explicitly.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If additional derived visual states are added (e.g., cached highlight ranges), ensure they are reset alongside preview state on load.

### 2026-02-17 23:29 +11:00 - Weld-run visual flicker spike filtering

#### Task Summary

- Added runtime telemetry filtering to prevent single-frame snap-back/flicker artifacts in arm visualization during weld execution.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Visualization occasionally jumped to a stale weld-start-like pose for one frame while actual motion continued, creating star-like flicker trails.
- Detection:
  - User screenshot showed repeated visual spokes from a fixed point during weld run.
- Fix:
  - Added telemetry guards in `web-ui/src/App.tsx`:
    - drop out-of-order packets using source telemetry timestamp (`t`),
    - reject implausible one-frame joint spikes (`maxJump > 0.8 rad` within `<=0.25s`) likely caused by stale/outlier packets.
  - Reset telemetry filter refs on disconnect.
- Preventive rule:
  - Treat UI pose stream as potentially noisy/reordered; enforce monotonic timestamp acceptance and outlier rejection before rendering.

#### User Preferences

- New or reinforced preference:
  - Weld execution visualization must remain stable and trustworthy; no transient “teleport” artifacts.
- How it changed execution:
  - Added ingestion-layer robustness rather than only tuning rendering interpolation.

#### What Worked

- Pattern/check that worked:
  - Filtering at message-ingest stage avoids contaminating both immediate and smoothed pose updates.

#### What Did Not Work

- Failed attempt and why:
  - Relying on smoothing alone cannot prevent stale packet flashes because stale targets still get applied instantly.

#### Guardrails For Next Session

- Preflight rule:
  - For realtime robot UI streams, always define packet-order and spike-handling policy explicitly.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If a second legitimate telemetry source is intentionally mixed in future, add explicit source tagging/selection instead of relying on timestamp-only arbitration.

### 2026-02-18 00:08 +11:00 - Weld program run gating + start-from-current execution

#### Task Summary

- Fixed inability to run loaded weld programs when draft restoration is missing/invalid but a runnable preview trajectory exists.
- Enforced run-time re-planning from current robot state for weld preview execution.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Run button in Weld panel was gated on `draft` existence instead of actual runnable preview presence, blocking execution for some loaded programs.
  - Weld preview run path used cached planning (`use_cache: true`), which can execute stale joint paths not guaranteed to reflect current robot state.
- Detection:
  - User loaded `test_02` and observed run action unavailable despite loaded trajectory/waypoints.
- Fix:
  - Updated Weld panel run gating to use `canRunPreview` (`Boolean(previewPlan?.name)`) rather than `draft`.
  - Switched preview run request to `use_cache: false` so backend re-plans from current state, naturally including current->start motion.
- Preventive rule:
  - UI action enablement must track actual execution prerequisites (runnable plan), not adjacent editor state (draft availability).

#### User Preferences

- New or reinforced preference:
  - Loaded weld programs should be runnable even when edge-edit context is unavailable.
  - Execution should start from current robot pose with an explicit approach to program start.
- How it changed execution:
  - Prioritized run-time correctness and operability over cache-first speed.

#### What Worked

- Pattern/check that worked:
  - Decoupling run enablement from `draft` immediately restores operability for loaded plans.
  - Re-plan from current state guarantees start approach behavior without additional special-case injection.

#### What Did Not Work

- Failed attempt and why:
  - Previous cache-first preview execution assumed planning-time and run-time robot state equivalence.

#### Guardrails For Next Session

- Preflight rule:
  - For any "Run" control, verify its disabled condition maps exactly to runtime required data, then confirm loaded-from-file flows satisfy that condition.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If run latency becomes noticeable due to re-planning, introduce an explicit "replan-on-run" toggle with clear UX semantics.

### 2026-02-18 00:18 +11:00 - Panel-aware drawer height mode (keep weld full, un-stretch others)

#### Task Summary

- Fixed the drawer height regression where STEP / Trajectory / Telemetry looked stretched to the bottom with large empty space.
- Preserved Weld Planning as full-height because that dense workflow benefits from a stable full overlay band.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - A global full-height drawer shell (`h-full` inside `top-6 bottom-6`) was applied to all tabs, which regressed sparse panels into visibly stretched empty containers.
- Detection:
  - User screenshots showed STEP / Trajectory / Live Charts extending to the bottom while Weld looked acceptable.
- Fix:
  - Added `heightMode` to `SidebarDrawer`:
    - `full` for Weld (`h-full`),
    - `content` for STEP / Trajectory / Telemetry (`max-h-full` with internal scrolling preserved).
  - Kept common overlay lane (`top-6 bottom-6`) and moved pointer-event handling to panel shell so empty transparent lane area does not block workspace interaction.
  - Updated `web-ui/design.md` rules to codify mixed-mode behavior.
- Preventive rule:
  - Do not apply one global drawer height strategy across panels with different content density; explicitly model panel height intent (content-fit vs full-height).

#### User Preferences

- New or reinforced preference:
  - Weld panel baseline/behavior is acceptable and should remain unchanged when fixing other tabs.
  - Sparse panels should not appear stretched to the viewport bottom.
- How it changed execution:
  - Used panel-specific height mode instead of another global class toggle.

#### What Worked

- Pattern/check that worked:
  - Shared wrapper + per-panel shell height mode is a low-risk way to preserve weld behavior while fixing sparse tabs.
  - Keeping internal scroll inside the same shell retained dense-content safety without reintroducing clipping.

#### What Did Not Work

- Failed attempt and why:
  - Previous "all panels full-height" rule solved weld alignment but caused immediate UX regressions for sparse tabs.

#### Guardrails For Next Session

- Preflight rule:
  - For shared drawer/container refactors, validate all tabs in both sparse and dense states before finalizing.
  - If one panel is intentionally different, encode that in props rather than ad-hoc class forks.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Confirm in live UI that click-through around non-full-height drawer shell feels natural at narrow and wide viewport sizes.

### 2026-02-18 01:13 +11:00 - Local repo skill installation into Codex home

#### Task Summary

- Installed all local skills from `.cursor/skills` into `C:\Users\angus\.codex\skills`.
- Verified destination skill set matches source local skills and complies with AGENTS workflow logging requirements.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Initial assumption from AGENTS list suggested `.cursor/skills-cursor` might also require installation.
- Detection:
  - Repository inspection showed `.cursor` contains only `rules` and `skills`; no `.cursor/skills-cursor` directory exists in this workspace.
- Fix:
  - Scoped installation to `.cursor/skills` folders that contain `SKILL.md`, then audited source-vs-destination skill names.
- Preventive rule:
  - Before bulk install/sync operations, verify referenced directories exist in the current repo snapshot rather than relying only on docs.

#### User Preferences

- New or reinforced preference:
  - Use `AGENTS.md` as startup context and install all repo-local skills when requested.
- How it changed execution:
  - Followed skill-installer guidance for workflow framing, then performed local copy/install for all `.cursor/skills` folders.

#### What Worked

- Pattern/check that worked:
  - Filtering source directories by existence of `SKILL.md` prevents copying non-skill folders.
  - Compare-object audit after install quickly confirms there are no missing skill names.

#### What Did Not Work

- Failed attempt and why:
  - None in this task; install path and audit succeeded on first pass.

#### Guardrails For Next Session

- Preflight rule:
  - For skill installation requests, check both `.cursor/skills` and any AGENTS-referenced paths, but install only paths present in the active workspace.
  - Always finish by updating both `DEVLOG.md` and `AGENT_SCRATCHPAD.md` before handoff.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Codex usually loads skills at startup; restart Codex after installation to ensure all newly installed skills are available.

### 2026-02-18 01:17 +11:00 - Weld preview run should use high-fidelity cache, not sparse endpoint re-plan

#### Task Summary

- Fixed mismatch where weld preview execution diverged from previewed/interpolated path because run used endpoint re-planning.
- Added explicit cache-readiness handling for weld runs and clarified UI wording around editable weld points.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Run path used `/trajectory/run` with `use_cache: false` globally, so weld trajectories were rebuilt from sparse `trajectory.moves` endpoints (few `move_absolute` nodes) instead of using the high-fidelity cached weld path.
- Detection:
  - User screenshot + report showed large gap between expected weld curve and simulated run path, while Program Tree showed only a handful of moves.
- Fix:
  - In `web-ui/src/App.tsx`:
    - added `weldPreviewCacheReady` tracking,
    - made weld runs use `use_cache: true` so backend executes full planned steps cache,
    - when weld cache is stale, auto-refresh preview via `requestWeldPreview` before run,
    - reset cache readiness on clear/disconnect/load transitions.
  - Added UI copy update (`Editable Control Points`) to avoid implying that the list is every interpolated sample.
  - In `web-ui/src/previewUtils.ts`, surfaced path sample count in Program Tree subtitle for better operator visibility.
- Preventive rule:
  - For trajectory systems with both coarse declarative moves and dense cached execution plans, never treat them as interchangeable at run time for weld/high-fidelity workflows.

#### User Preferences

- New or reinforced preference:
  - Displayed/selected weld path and executed weld path must match; no hidden downsampling that changes robot motion.
  - If a mismatch is suspected, prioritize run-time correctness over prior convenience assumptions.
- How it changed execution:
  - Weld run path is now anchored to planned cache validity, with explicit stale-cache refresh.

#### What Worked

- Pattern/check that worked:
  - Keeping non-weld behavior unchanged while branching weld execution policy minimized regression risk.
  - Cache readiness flag cleanly coordinates plan/run state across clear/load/restore flows.

#### What Did Not Work

- Failed attempt and why:
  - Earlier global `use_cache: false` approach improved “start from current pose” semantics but broke weld trajectory fidelity by collapsing to endpoint commands.

#### Guardrails For Next Session

- Preflight rule:
  - If Program Tree move count is far smaller than expected path complexity, verify whether run path uses cached planned steps or endpoint re-planning.
  - For weld runs, treat cache freshness as a first-class precondition.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Program Tree still emphasizes operation-level moves; consider adding a dedicated interpolated-path inspector node if operators need per-sample introspection.

### 2026-02-18 01:28 +11:00 - Exact path visibility: remove planner payload downsampling + tree from path samples

#### Task Summary

- Implemented full-fidelity path visibility so Program Tree can show exact planned path samples instead of trimmed endpoint-derived approximations.
- Removed planner payload downsampling that previously hid intermediate cartesian samples.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - UI path inspection relied on lower-resolution representations (coarse move endpoints and downsampled cartesian payload), creating a trust gap for weld motion verification.
- Detection:
  - User explicitly rejected trimmed output and required exact movement visibility in Program Tree.
- Fix:
  - In `src/gradient_os/arm_controller/command_api.py`, removed `sample_stride` downsampling in `_append_cartesian_samples` so payload carries full planned cartesian samples.
  - In `web-ui/src/previewUtils.ts`, rewired `buildProgramTree` to use `plan.pathPoints` as primary execution tree content:
    - `Exact Path Samples` in grouped mode,
    - `Execution Path (Exact)` in chronological mode,
    - preserved control-point and controller-command groups as secondary views.
- Preventive rule:
  - For robotics inspection UIs, never downsample the authoritative displayed path unless user explicitly opts into a performance mode.

#### User Preferences

- New or reinforced preference:
  - Program Tree must reflect exactly where robot will move; no hidden trimming.
  - Coarse representations are acceptable only as supplemental metadata, not as the primary motion truth.
- How it changed execution:
  - Prioritized operator-trust visibility over payload compactness by default.

#### What Worked

- Pattern/check that worked:
  - Maintaining dual views (exact path + command metadata) preserved debugging utility without compromising motion fidelity visibility.

#### What Did Not Work

- Failed attempt and why:
  - Prior “show move count + path sample count” transparency helped diagnostics but did not satisfy requirement for exact per-sample tree inspection.

#### Guardrails For Next Session

- Preflight rule:
  - If a user asks for exact robot path visibility, ensure both backend payload and frontend tree model are fidelity-preserving end-to-end.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Extremely long paths can create large tree DOMs; prefer virtualization if performance issues appear, not sample trimming.

### 2026-02-18 01:42 +11:00 - Remove approximate segment highlighting when exact mapping is unavailable

#### Task Summary

- Removed approximate weld-segment path highlighting from Program Tree to keep display semantics strictly truthful.
- Preserved command-level tree data only as reference metadata when exact path samples already exist.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Weld segment nodes were still assigning proportional `pathRange` guesses, which could imply false precision even after exact-path sample support was added.
- Detection:
  - User requirement emphasized exact reflection between Program Tree and rendered path; inferred ranges violate that constraint.
- Fix:
  - Removed weld segment `pathRange` inference from `web-ui/src/previewUtils.ts`.
  - Weld segment nodes now only target weld-edge focus (`weldSegmentEdgeId`) without claiming exact path subset.
  - Simplified command grouping so command nodes are clearly labeled as reference when exact path nodes are present.
- Preventive rule:
  - If exact mapping data is not available, do not synthesize approximate range overlays in robotics inspection views.

#### User Preferences

- New or reinforced preference:
  - Program Tree must never imply precision it does not actually have.
  - Exact path truth takes precedence over convenience grouping.
- How it changed execution:
  - Removed inferred path focus fields unless backed by exact sample indices.

#### What Worked

- Pattern/check that worked:
  - Separating "exact execution samples" from "controller command metadata" keeps debugging utility while preserving trust.

#### What Did Not Work

- Failed attempt and why:
  - Earlier proportional segment-range mapping was useful visually but not acceptable for exactness-critical inspection.

#### Guardrails For Next Session

- Preflight rule:
  - Any tree node that highlights path must be backed by explicit deterministic indices from planner output; otherwise omit the highlight mapping.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If per-weld-segment exact highlighting is required later, backend should return section-to-sample index spans as part of planner payload.

### 2026-02-18 01:53 +11:00 - Waypoint editing migrated from Weld drawer into Program Tree

#### Task Summary

- Removed the `Editable Control Points` editor block from Weld drawer UI.
- Implemented Program Tree-native control-point editing flow so waypoint edits are driven from selected tree nodes.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Drawer-local waypoint editor duplicated editing context and conflicted with requirement that tree/path inspection be the source of truth.
- Detection:
  - User explicitly requested complete removal from drawer and routing edits through Program Tree.
- Fix:
  - In `web-ui/src/App.tsx`, removed Weld panel waypoint-edit props/UI and added tree-driven handlers:
    - edit selected control point coordinates,
    - add/remove control point,
    - apply edits via weld replan (or generic point replan for non-weld).
  - In `web-ui/src/components/ProgramFeatureTree.tsx`, added an inline editor section that appears when a `control_point_*` node is selected.
- Preventive rule:
  - Avoid duplicated edit surfaces for the same motion data; keep one primary editing interaction path tied to the inspection model.

#### User Preferences

- New or reinforced preference:
  - Waypoint editing should be centralized in Program Tree, not scattered in panel forms.
  - The path/tree workflow must remain coherent and trustworthy for motion changes.
- How it changed execution:
  - Shifted from drawer-local form controls to selection-driven tree editing.

#### What Worked

- Pattern/check that worked:
  - Reusing existing waypoint state and planner callbacks minimized risk while moving the UI interaction surface.

#### What Did Not Work

- Failed attempt and why:
  - Keeping both drawer and tree editors would continue UX ambiguity and contradict user’s “single source” editing requirement.

#### Guardrails For Next Session

- Preflight rule:
  - When a user requests “drive from X only,” remove parallel controls in other panels rather than trying to keep them synchronized ad hoc.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If users miss discoverability, add small guidance text in Program Tree when no control point is selected.

### 2026-02-18 01:54 +11:00 - Tree node panel focus should follow weld context

#### Task Summary

- Adjusted Program Tree node focus target so selecting control/path nodes in weld plans keeps interaction in weld context.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - After moving editing to Program Tree, control-point nodes still targeted trajectory panel by default, which could feel inconsistent for weld-first workflows.
- Detection:
  - Post-change review of `ProgramNode.focus.openPanel` mapping in `previewUtils.ts`.
- Fix:
  - Set default tree-node focus panel dynamically:
    - weld plan (`trajectory.weld` present) -> `"weld"`,
    - otherwise -> `"trajectory"`.
- Preventive rule:
  - When relocating an editing surface, re-check navigation/focus semantics so node selection context matches the new workflow.

#### User Preferences

- New or reinforced preference:
  - Program Tree should be the primary interaction context for waypoint edits.
- How it changed execution:
  - Ensured tree node selection supports weld-context editing rather than bouncing users to trajectory panel unintentionally.

#### What Worked

- Pattern/check that worked:
  - Deriving a `defaultFocusPanel` once in tree builder avoided repeated branching and kept node focus consistent.

#### What Did Not Work

- Failed attempt and why:
  - Static `openPanel: "trajectory"` across all plans was too rigid once weld editing moved to tree.

#### Guardrails For Next Session

- Preflight rule:
  - Any time node semantics change, validate both data fidelity and panel-navigation behavior together.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If users want tree selection decoupled from panel switching, add a toggle for “selection-only mode” in settings.

### 2026-02-18 02:00 +11:00 - Preview waypoint marker size reduced to 1mm

#### Task Summary

- Reduced yellow preview waypoint sphere radius to 1mm for less visual clutter in the scene.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Waypoint spheres were oversized for dense weld-path inspection.
- Detection:
  - User requested “much smaller, maybe 1mm radius.”
- Fix:
  - Updated marker mesh radius in `web-ui/src/ArmVisualizer.tsx` from `0.008` to `0.001` meters in the preview path marker block.
- Preventive rule:
  - For dense robot path overlays, keep default markers small enough to avoid obscuring the path geometry.

#### User Preferences

- New or reinforced preference:
  - Preview waypoint markers should be visually subtle and not dominate the path view.
- How it changed execution:
  - Applied a direct geometry-radius change instead of additional styling complexity.

#### What Worked

- Pattern/check that worked:
  - Single-parameter radius change in the marker geometry cleanly addressed the request.

#### What Did Not Work

- Failed attempt and why:
  - None in this task.

#### Guardrails For Next Session

- Preflight rule:
  - When adjusting 3D markers, treat units as meters and validate requested real-world sizing directly in geometry values.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Tiny markers may be hard to pick out at very wide zoom; consider optional user-adjustable marker scale if requested.

### 2026-02-18 02:04 +11:00 - Weld return_to_start must replan from current pre-run pose every run

#### Task Summary

- Fixed critical weld end-action regression where `return_to_start` could resolve to stale/wrong targets (including weld start) if an old preview plan cache was reused.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Weld run path could execute cached plan without guaranteed per-run replan from current robot state, so `return_to_start` target was not always the actual pre-weld run start pose.
- Detection:
  - User reported repeated return to weld start despite selecting `Return to trajectory start`.
- Fix:
  - In `web-ui/src/App.tsx`, updated weld run logic in `handleRunPreview`:
    - always call `requestWeldPreview(weldDraft)` immediately before running weld preview,
    - then execute with `use_cache: true` against the just-refreshed plan.
  - This forces backend planner to recapture current start pose each run and regenerate post-action transitions accordingly.
- Preventive rule:
  - For semantics that depend on runtime start context (like `return_to_start`), never allow weld execution to skip replan on run.

#### User Preferences

- New or reinforced preference:
  - `Return to trajectory start` must mean “the robot pose right before this weld run starts,” never weld-start fallback.
- How it changed execution:
  - Prioritized semantic correctness and determinism over cache-only run latency.

#### What Worked

- Pattern/check that worked:
  - Replan-then-run for weld previews preserves high-fidelity path execution while guaranteeing correct start-context capture.

#### What Did Not Work

- Failed attempt and why:
  - Conditional cache refresh based on stale flags was insufficient for strict runtime start semantics.

#### Guardrails For Next Session

- Preflight rule:
  - If an end-action references “start” and operator intent is per-run, enforce replan-at-run regardless of prior cache freshness.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Additional replan time before each weld run is expected; optimize only if needed, without compromising start-context correctness.

### 2026-02-18 02:19 +11:00 - Stabilize weld run-state lifecycle and isolate jog loop

#### Task Summary

- Fixed a backend execution-state bug that could clear motion state mid-trajectory and allow control-loop contention.
- Added trajectory-start guard to stop active jog mode before weld/trajectory playback.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Nested step execution in `trajectory_execution._execute_joint_path` reused `_open_loop_executor_thread` which could clear `trajectory_state` (`is_running`, `thread`) during a still-active multi-step weld run.
- Detection:
  - User-reported jitter/snap behavior during weld execution; code audit showed executor cleanup was tied only to thread identity, which matches nested step execution.
- Fix:
  - Added `owns_trajectory_state` parameter to open/closed executors and disabled state cleanup for nested step calls.
  - Updated `handle_run_trajectory` to stop jog mode before run and abort if jog remains active.
- Preventive rule:
  - Any low-level executor used both standalone and nested must have explicit lifecycle ownership; never let nested calls mutate global run flags.

#### User Preferences

- New or reinforced preference:
  - Execution correctness and deterministic robot behavior are higher priority than convenience/background control loops.
  - User expects direct fixes, not speculative discussion.
- How it changed execution:
  - Focused on controller run-state/jog isolation, implemented concrete backend patches first, then validated syntax/lints.

#### What Worked

- Pattern/check that worked:
  - Tracing end-to-end from UI symptom to controller state transitions exposed the lifecycle race quickly.

#### What Did Not Work

- Failed attempt and why:
  - Looking only at weld planning math was insufficient; the dominant issue was runtime executor/jog interaction, not weld geometry sampling itself.

#### Guardrails For Next Session

- Preflight rule:
  - For motion bugs with "random snaps/jitter," inspect global motion flags (`is_running`, `is_jogging`, `thread`) and thread cleanup points before tuning planners.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Validate with live weld run in simulator to confirm no residual jitter under active UI polling and no unintended return-to-weld-start behavior.

### 2026-02-18 02:26 +11:00 - Runtime confirmation: execution-state fix is primary root cause

#### Task Summary

- Recorded user confirmation that weld execution now behaves correctly after the controller patch.
- Captured that the issue previously occurred even with jog disabled, reinforcing execution-state lifecycle as primary fault domain.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Earlier suspicion that jog could be the sole cause was incomplete.
- Detection:
  - User explicitly reported prior reproduction with jog disabled.
- Fix:
  - Keep execution-state lifecycle fix as the core resolution.
  - Retain jog-stop guard as non-invasive protection against future control-loop contention.
- Preventive rule:
  - For motion jitter/snap bugs, prioritize controller state lifecycle and thread ownership analysis before attributing solely to UI-side control streams.

#### User Preferences

- New or reinforced preference:
  - Preserve practical safety guards if they do not add downside, even when not the primary fix.
- How it changed execution:
  - Kept jog isolation check in place as defense-in-depth rather than removing it after root-cause confirmation.

#### What Worked

- Pattern/check that worked:
  - Combining code-level race fix with runtime user validation quickly converged on true root cause.

#### What Did Not Work

- Failed attempt and why:
  - Treating jog contention as the only likely source would have underexplained the jog-disabled reproductions.

#### Guardrails For Next Session

- Preflight rule:
  - If a bug reproduces with a suspected subsystem disabled, immediately elevate investigation to shared/global state and thread-lifecycle paths.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - None immediate; monitor for recurrence under long runs or repeated run/stop cycles.

### 2026-02-18 11:47 +11:00 - README refresh for merge readiness

#### Task Summary

- Added a root repository `README.md` and refreshed `web-ui/README.md` to reflect current product behavior.
- Prepared branch-level merge commit message guidance.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Assuming a root README existed would have left the “main repo readme” request partially done.
- Detection:
  - File check showed no `README.md` at repository root.
- Fix:
  - Created root `README.md` and updated `web-ui/README.md` with current architecture/workflow notes.
- Preventive rule:
  - For docs requests, verify file existence first and create missing canonical docs rather than only editing submodule docs.

#### User Preferences

- New or reinforced preference:
  - Wants merge-ready artifacts: clear commit messaging plus up-to-date top-level and UI docs.
- How it changed execution:
  - Prioritized practical documentation updates and concise merge messaging over deep code changes.

#### What Worked

- Pattern/check that worked:
  - Pairing root + feature-area README updates keeps main-branch handoff clearer for maintainers/operators.

#### What Did Not Work

- Failed attempt and why:
  - None in this step.

#### Guardrails For Next Session

- Preflight rule:
  - When asked for "main repo README," explicitly confirm root-level presence and update/create accordingly.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Consider later consolidation between `README.md`, `AGENTS.md`, and `docs/README.md` to reduce duplicated startup guidance.

### 2026-02-18 11:55 +11:00 - Main README clarification: docs/README is canonical

#### Task Summary

- Updated `docs/README.md` after user clarified this is the canonical "main README" for repo-level documentation.
- Built a comprehensive commit-message draft based on full branch diff context rather than only current unstaged files.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Initial README update targeted root-level docs first; user clarified canonical main README is `docs/README.md`.
- Detection:
  - Direct user correction in follow-up message.
- Fix:
  - Added a dedicated `STEP_LOADER Branch Highlights` section in `docs/README.md` with end-to-end scope summary.
- Preventive rule:
  - In this repo, treat `docs/README.md` as the primary documentation entrypoint unless user asks otherwise.

#### User Preferences

- New or reinforced preference:
  - Wants branch merge materials to be comprehensive and grounded in the full branch scope.
- How it changed execution:
  - Used `master..HEAD` log/stat context before drafting commit message language.

#### What Worked

- Pattern/check that worked:
  - Pairing user clarification with git-range analysis produced accurate high-level change framing.

#### What Did Not Work

- Failed attempt and why:
  - A root-only README update was insufficient for this repository's doc convention.

#### Guardrails For Next Session

- Preflight rule:
  - For merge/prep requests, confirm canonical docs path and summarize against `base..HEAD` rather than local unstaged delta only.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - None immediate.

### 2026-05-14 19:48 CDT - Manual teach-and-repeat mechanism confirmed

#### Task Summary

- Investigated whether the repo has a mechanism to manually teach the robot a path and replay it.

#### Mistakes And Fixes

- Source: `[investigation]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - N/A.
- Preventive rule:
  - When asked about "recording" in this repo, distinguish trajectory replay (`recorded_trajectories/`) from telemetry episode recording (`recorded_episodes/`).

#### User Preferences

- New or reinforced preference:
  - User is evaluating practical robot bring-up workflows, so answer with operational mechanisms and caveats, not only code names.
- How it changed execution:
  - Checked UI, API, controller dispatcher, command handlers, tests, docs, and sample recorded trajectory files.

#### What Worked

- Pattern/check that worked:
  - Searching for recorder/replay commands quickly exposed the canonical flow: `PLAN_TRAJECTORY` -> `REC_POS` -> `END_TRAJECTORY` -> `RUN_TRAJECTORY`.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - For teach/replay questions, call out that existing trajectory recording captures FK waypoints and re-plans moves; it is not a continuous raw servo trace playback system.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Hardware bus reliability and calibration must be healthy before relying on replayed paths.

### 2026-05-14 19:04 CDT - Resume next-step triage from exported chat

#### Task Summary

- Reviewed exported chat history plus repo notes to answer the user's "what are my next steps?" question with current bring-up priorities.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - When user references exported chat history, read the explicit "OPEN ITEMS / WHERE WE LEFT OFF" block before inferring from older repo TODOs.

#### User Preferences

- New or reinforced preference:
  - User wants practical next actions, not broad background, when resuming hardware bring-up.
- How it changed execution:
  - Prioritized servo bus recovery, zeroing, and gripper control ahead of UI polish.

#### What Worked

- Pattern/check that worked:
  - `rg` against repo notes plus targeted `sed` windows in `/Users/dylanembry/chat-history.txt` quickly separated current hardware blockers from stale UI handoff notes.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - Treat hardware bus reliability as the first blocker when servos PING but READ fails; do not proceed to calibration until torque enable/readback works for all expected servos.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Servos 31 and 100 may still have marginal half-duplex signal/connectivity issues; calibration and gripper teach-replay remain blocked until that is resolved.

### 2026-05-14 19:19 CDT - Missing servo PING diagnosis priority

#### Task Summary

- User reported servo IDs 31 and 100 are still absent; provided likely causes and a hardware-first diagnostic order.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - Distinguish "READ register fails" from "PING absent"; absent PING should bias diagnosis toward power, cable/connector, wrong ID, baud/config mismatch, collision, or damaged servo.

#### User Preferences

- New or reinforced preference:
  - User needs bench-ready troubleshooting order for robot hardware issues.
- How it changed execution:
  - Gave likely causes by probability and a concrete isolation sequence instead of software architecture context.

#### What Worked

- Pattern/check that worked:
  - Framing scan absence as PING-level failure clarified that calibration should remain blocked.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - If IDs 31 and 100 are absent, isolate one servo at a time on a short known-good lead before changing EEPROM IDs or assuming software bugs.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need hardware scan output after isolating each affected servo, including factory-default/full-sweep results.

### 2026-05-14 19:23 CDT - Replacement STS3215 servos likely need commissioning

#### Task Summary

- User clarified that IDs 31 and 100 were separately purchased STS3215 servos, not kit-provided configured servos.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Initial diagnosis treated absent IDs mainly as connection/power faults.
- Detection:
  - User disclosed both missing units were aftermarket replacements.
- Fix:
  - Reprioritized likely cause to factory-default ID/baud/config and ID collision.
- Preventive rule:
  - Ask whether replacement bus servos were preconfigured before assuming physical failure; factory-fresh STS3215 units commonly need ID assignment.

#### User Preferences

- New or reinforced preference:
  - User provides product details to narrow diagnosis and wants concrete next bench commands.
- How it changed execution:
  - Focused on one-at-a-time servo isolation and `scripts/set_servo_id.py` usage.

#### What Worked

- Pattern/check that worked:
  - Local docs confirmed default ID `1`, default baud register value for `1 Mbps`, and canonical Gradient0 IDs.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - Never connect two new/uncommissioned STS3215 servos at the same time during ID assignment; isolate each unit before writing register `0x05`.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If an isolated replacement servo does not answer at ID `1` on 1 Mbps, test other baud rates or use vendor tooling before assuming damage.

### 2026-05-14 19:27 CDT - CH340 LED during servo power-cycle

#### Task Summary

- User asked whether the CH340 LED remaining on during 12V power cycling means servo state machines are not reset.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - Distinguish adapter USB power from servo 12V power; CH340 LED alone is not evidence that STS3215 servo MCU/RAM state persisted.

#### User Preferences

- New or reinforced preference:
  - User wants practical electrical interpretation while debugging at the bench.
- How it changed execution:
  - Explained normal CH340 behavior plus the back-powering caveat and concrete full-reset steps.

#### What Worked

- Pattern/check that worked:
  - Treating visible LEDs as power-domain clues, not proof of logical state, gives a safer diagnostic path.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - For a true servo reset, verify servo-side 12V drops and no servo LEDs/voltage remain; unplug USB only if residual/backfed power is suspected.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need confirmation whether the servo bus board can back-feed through TTL/data or a shared 5V rail.

### 2026-05-14 19:30 CDT - Servo connector and serial terminology explanation

#### Task Summary

- Explained why the opposite STS3215 connector can change detection behavior and defined MCU, baud rate, and hertz.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - When user asks foundational electronics terms, define them in practical robot-debugging language before returning to commands.

#### User Preferences

- New or reinforced preference:
  - User wants underlying electrical reasoning, not just diagnostic steps.
- How it changed execution:
  - Explained pass-through connector expectations, failure modes, and timing units.

#### What Worked

- Pattern/check that worked:
  - Framing port differences as "should not matter when healthy, so a difference is diagnostic" keeps the debugging path clear.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - For servo detection questions, always separate the three required conditions: power, common ground, and data line integrity.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need bench result from trying each replacement servo isolated on each connector/lead.

### 2026-05-14 19:39 CDT - Isolated gripper found at factory ID 1

#### Task Summary

- User isolated the replacement gripper servo and scan found only factory-default ID `1`.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - When scanning one isolated servo, expected Gradient0 IDs should be absent until the servo is renamed; do not misread that as failure.

#### User Preferences

- New or reinforced preference:
  - User benefits from interpreting command output before running the next write step.
- How it changed execution:
  - Next instruction should be the single safe EEPROM write from ID `1` to target ID `100`.

#### What Worked

- Pattern/check that worked:
  - Isolating the replacement servo proved the product is alive and configured at factory defaults.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - Keep the target replacement servo physically isolated when running `scripts/set_servo_id.py`.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need post-rename scan showing gripper at ID `100` and factory ID `1` silent.

### 2026-05-14 19:49 CDT - Rename verified then scan missed all IDs

#### Task Summary

- User renamed isolated replacement servo from ID `1` to `31`; the rename script verified new ID `31`, but a subsequent scan found no IDs.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - If `set_servo_id.py` verifies the new ID but scanner misses it afterward, separate three possibilities before rewriting: connection/power changed, scanner ping timing is flaky, or baud/config changed.

#### User Preferences

- New or reinforced preference:
  - User provides full terminal output and needs interpretation of contradictory tool results.
- How it changed execution:
  - Focused on direct verification commands before any further EEPROM writes.

#### What Worked

- Pattern/check that worked:
  - The immediate `ping new ID 31... ok` line is strong evidence the write took effect at least in the live servo state.

#### What Did Not Work

- Failed attempt and why:
  - The subsequent scan did not confirm the new ID, so scanner output alone is insufficient to decide whether EEPROM persistence succeeded.

#### Guardrails For Next Session

- Preflight rule:
  - Do not run another rename against an uncertain servo until isolated scans/direct pings establish which ID currently responds.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need direct `set_servo_id.py --from 31 --to 31` is invalid, so use scan/direct ping helper or scan across baud rates to establish current ID before continuing.

### 2026-05-14 21:13 CDT - Non-persistent replacement servo IDs

#### Task Summary

- User confirmed both replacement servos can be reassigned while powered but revert/disappear after power-cycle.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - The standalone `scripts/set_servo_id.py` wrote the ID register without explicitly unlocking EEPROM first.
- Detection:
  - User observed ID reassignment verified live but did not persist across power-cycle.
- Fix:
  - Patched `scripts/set_servo_id.py` to unlock write-lock register `0x37`, write ID register `0x05`, wait for commit, then relock via the new ID.
- Preventive rule:
  - For STS3215 EEPROM fields, mirror the backend's unlock/write/relock pattern; live verification alone does not prove persistence.

#### User Preferences

- New or reinforced preference:
  - User wants direct bench-fix commands when a hardware commissioning script is wrong.
- How it changed execution:
  - Patched the local script instead of only explaining the EEPROM lock theory.

#### What Worked

- Pattern/check that worked:
  - `rg` found existing backend EEPROM writes using `WRITE_LOCK`, confirming the expected commissioning sequence.

#### What Did Not Work

- Failed attempt and why:
  - Prior ID assignment script produced a live ID change but likely left EEPROM locked, so the change was not durable.

#### Guardrails For Next Session

- Preflight rule:
  - For replacement servos, verify persistence with power-cycle plus scan before reconnecting them into the full chain.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need user bench confirmation that patched `set_servo_id.py` makes IDs `31` and `100` persist after power-cycle.

### 2026-05-14 21:15 CDT - Gripper renamed to ID 100 with patched script

#### Task Summary

- Ran the patched ID assignment tool against the isolated gripper servo and verified full-sweep detection as ID `100`.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - Treat `scan_servo_bus.py` exit code `1` as expected during isolated-servo scans when only one of the canonical IDs is connected; inspect the printed present/factory summary.

#### User Preferences

- New or reinforced preference:
  - User is comfortable asking Codex to run bench commands directly when hardware is connected.
- How it changed execution:
  - Ran the ID assignment and sweep locally instead of only providing commands.

#### What Worked

- Pattern/check that worked:
  - The patched unlock/write/relock sequence reported `ping relocked ID 100... ok`, and the full sweep showed `ID 100` present with factory ID `1` silent.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - After any EEPROM ID write, perform a full power-cycle and rescan before reconnecting the servo into the full chain.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need to power-cycle the gripper and confirm it still scans as `100`; then repeat for servo `31`.

### 2026-05-14 21:19 CDT - Gripper ID 100 persisted after power-cycle

#### Task Summary

- Rescanned the isolated gripper after power cycle and confirmed it still responds as ID `100`.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - Count post-power-cycle scan as the persistence proof, not just immediate post-write ping.

#### User Preferences

- New or reinforced preference:
  - User wants quick command execution and concise interpretation while physically operating the hardware.
- How it changed execution:
  - Ran the sweep immediately after the user reported power was back.

#### What Worked

- Pattern/check that worked:
  - The patched EEPROM unlock/write/relock sequence persisted successfully for gripper ID `100`.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - Use the same patched isolated flow for servo `31`, then only reconnect the full chain after both replacements pass power-cycle scans.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need to commission and verify J3 secondary servo ID `31`; then scan the complete chain.

### 2026-05-14 21:34 CDT - J3 secondary renamed to ID 31 with patched script

#### Task Summary

- Ran the patched ID assignment tool against the isolated J3 secondary replacement servo and verified full-sweep detection as ID `31`.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None during this step.
- Detection:
  - Not applicable.
- Fix:
  - Not applicable.
- Preventive rule:
  - Continue requiring post-power-cycle scan before declaring replacement servo commissioning complete.

#### User Preferences

- New or reinforced preference:
  - User wants the same quick run-and-interpret loop for each hardware step.
- How it changed execution:
  - Ran rename and full sweep back-to-back, then paused for power-cycle proof.

#### What Worked

- Pattern/check that worked:
  - The patched unlock/write/relock sequence reported `ping relocked ID 31... ok`, and the full sweep showed `ID 31` present with factory ID `1` silent.

#### What Did Not Work

- Failed attempt and why:
  - None.

#### Guardrails For Next Session

- Preflight rule:
  - After the user power-cycles ID `31`, rescan before reconnecting full chain.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need to confirm ID `31` persists after power-cycle, then scan the complete chain with both replacement servos installed.

### 2026-05-14 21:48 CDT - Full robot zero and service startup

#### Task Summary

- With all servos connected and the arm held in the user-selected zero pose, scanned the bus, torque-locked all servos, sent `SET_ZERO` for joints 1-6, and started controller/API/web services.

#### Mistakes And Fixes

- Source: `[tool]`
- Mistake:
  - Detached `nohup` controller/API launches exited silently on this Mac after appearing to start.
- Detection:
  - `ps`/`lsof` showed no UDP `3000` or HTTP `4000` listener after detached startup.
- Fix:
  - Started controller and API in PTY-backed sessions; HTTP and UDP checks then passed.
- Preventive rule:
  - For this local Mac environment, verify service listeners after startup and use PTY sessions if detached `nohup` processes vanish without logs.

#### User Preferences

- New or reinforced preference:
  - User wants hardware/service operations performed directly when the robot is connected and positioned.
- How it changed execution:
  - Ran scan, torque, zero, and service startup commands instead of giving a command checklist.

#### What Worked

- Pattern/check that worked:
  - Bus scan confirmed all 9 IDs before torque/zero; `torque.py on` locked every servo; UDP `GET_POSITION` validated the controller after zeroing.

#### What Did Not Work

- Failed attempt and why:
  - `GET_ALL_POSITIONS` still reported read failures for IDs `31` and `100`, suggesting register-read reliability remains weaker than PING detection on the full chain.

#### Guardrails For Next Session

- Preflight rule:
  - Before motion tests, confirm whether IDs `31` and `100` can return position reliably on the full chain, not just PING.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Full-chain signal integrity/readback for replacement servos remains a risk; avoid demanding closed-loop motion until read reliability is checked or improved.

### 2026-02-18 11:59 +11:00 - docs/README rewritten as true onboarding entrypoint

#### Task Summary

- Replaced `docs/README.md` content with newcomer-first documentation: features, system function, and usage workflow.
- Removed release-note style sectioning that did not match the file's purpose.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Prior update style emphasized branch-change summaries instead of serving as a practical start guide.
- Detection:
  - Explicit user correction on expected README role and tone.
- Fix:
  - Full rewrite of `docs/README.md` around onboarding flow and operational usage.
- Preventive rule:
  - For canonical README files, optimize for "what it is / how it works / how to use it" before changelog-style content.

#### User Preferences

- New or reinforced preference:
  - README must function as the primary onboarding document for new repo users.
- How it changed execution:
  - Shifted from patching sections to a complete structure reset aligned to onboarding intent.

#### What Worked

- Pattern/check that worked:
  - Rebuilding the file from scratch avoided carrying over conflicting structure and tone.

#### What Did Not Work

- Failed attempt and why:
  - Incremental edits against prior structure kept reintroducing non-onboarding framing.

#### Guardrails For Next Session

- Preflight rule:
  - Before editing a "main README", define target reader and first-use journey explicitly, then shape sections around that path.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - None immediate.

### 2026-02-18 12:28 +11:00 - Diagram renderer compatibility fix only

#### Task Summary

- Applied targeted fixes to Mermaid blocks in `docs/README.md` so diagrams render in the repo preview environment.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Diagram syntax was too permissive/complex for the active markdown renderer and produced "No diagram type detected" errors.
- Detection:
  - User screenshots showed Mermaid parser failures in rendered README sections.
- Fix:
  - Rewrote Mermaid blocks with strict `flowchart TD` and simplified `sequenceDiagram` content.
  - Removed HTML line breaks and complex quoted labels from diagram text.
- Preventive rule:
  - For README diagrams, prefer conservative Mermaid syntax over decorative labels.

#### User Preferences

- New or reinforced preference:
  - Scope must stay exactly on requested fix when user asks for a targeted patch.
- How it changed execution:
  - Limited edits to diagram blocks only.

#### What Worked

- Pattern/check that worked:
  - Re-typing diagram blocks from scratch prevented hidden syntax issues from surviving.

#### What Did Not Work

- Failed attempt and why:
  - None in this step.

#### Guardrails For Next Session

- Preflight rule:
  - When diagrams fail, first simplify to minimal valid Mermaid syntax before broader doc edits.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - None immediate.

### 2026-05-14 21:32 CDT - iPhone teleop panel

#### Task Summary

- Added a phone-first Teleop drawer to `web-ui` that reuses the realtime jog API and supports touch pads plus optional iPhone tilt mode.
- Documented LAN setup and updated UI guardrails.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - First mobile screenshot showed the desktop Robot Control card peeking out behind the Teleop drawer.
- Detection:
  - Playwright mobile viewport screenshot at 390x844.
- Fix:
  - Hid the desktop Robot Control card whenever `activePanel === "teleop"`.
- Preventive rule:
  - On mobile overlay work, check for lower-z-index desktop panels still being visible behind the active panel.

#### User Preferences

- New or reinforced preference:
  - User wants direct operational setup for physical robot control, not just conceptual guidance.
- How it changed execution:
  - Implemented the iPhone path in the web UI, documented the LAN commands, and kept the dev server running for immediate trial.

#### What Worked

- Pattern/check that worked:
  - Reusing `/control/jog/start`, `/control/jog/deadman`, and `/control/jog/velocity` avoided new backend risk.
  - CDP multi-touch simulation validated deadman-held nonzero velocity and release-to-zero behavior.

#### What Did Not Work

- Failed attempt and why:
  - Single-pointer Playwright mouse simulation could not validate two-finger deadman-plus-stick behavior; CDP touch dispatch was needed.

#### Guardrails For Next Session

- Preflight rule:
  - For phone teleop changes, run mobile viewport screenshots and a multi-touch mocked request check before handoff.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Real iPhone/Safari tilt permission still needs hardware/browser validation; touch controls are the safe fallback.

### 2026-05-14 21:50 CDT - VR teleop repo research

#### Task Summary

- Researched open-source Quest/VR/XR teleoperation repos and ranked them by popularity plus production/research credibility.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - Used current GitHub metadata plus primary project pages instead of relying on memory.
- Preventive rule:
  - For ecosystem recommendations, verify stars/activity and distinguish full robot stacks from lightweight input bridges.

#### User Preferences

- New or reinforced preference:
  - User wants practical repo recommendations with an eye toward serious research/production use, not a broad list of hobby projects.
- How it changed execution:
  - Ranked Unitree/OpenTeleVision/Open Teach/OculusReader/Quest2ROS-style projects and called out best fit for GradientOS.

#### What Worked

- Pattern/check that worked:
  - Combining GitHub API metadata with README/project claims produced a grounded short list.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - When recommending robotics repos, include architecture fit, maintenance/activity, hardware assumptions, and licensing/maturity caveats.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Any adoption step should prototype against GradientOS safety/deadman semantics before connecting to hardware.

### 2026-05-14 22:05 CDT - iPhone controller teleop repo fit

#### Task Summary

- Re-ranked the teleop repo shortlist for the specific path "iPhone 16 controller -> GradientOS robot teleop."

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Initial VR/Oculus shortlist underweighted phone-first iOS options.
- Detection:
  - Follow-up review of LeRobot phone teleop docs and SpesRobotics WebXR README.
- Fix:
  - Added LeRobot/HEBI Mobile I/O and `trzy/robot-arm` to the comparison, and separated "best original WebXR-style repo" from "best actual iPhone 16 fit."
- Preventive rule:
  - For iPhone controller requests, verify iOS/WebXR/ARKit support directly before ranking a phone teleop repo.

#### User Preferences

- New or reinforced preference:
  - User wants the selected repo judged against GradientOS' actual robot control path, not just popularity.
- How it changed execution:
  - Mapped candidates to the existing `/control/jog/start`, `/control/jog/deadman`, and `/control/jog/velocity` integration surface.

#### What Worked

- Pattern/check that worked:
  - LeRobot's iOS path plus HEBI Mobile I/O gives a mature phone pose/buttons input source without replacing GradientOS control safety.

#### What Did Not Work

- Failed attempt and why:
  - SpesRobotics `teleop` is architecturally clean but explicitly unsuitable for iPhone because it depends on WebXR.

#### Guardrails For Next Session

- Preflight rule:
  - If the controller is an iPhone, prefer ARKit/native app or HEBI Mobile I/O patterns for 6-DoF pose; keep browser-only teleop to touch/DeviceOrientation unless real Safari support is proven.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Validate HEBI Mobile I/O discovery and latency on the user's LAN with the actual iPhone 16 before connecting to live servos.

### 2026-05-14 22:10 CDT - Current teleop architecture explanation

#### Task Summary

- Explained current GradientOS module responsibilities and how a LeRobot + HEBI Mobile I/O iPhone controller path would differ.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - Grounded the explanation in local files before answering.
- Preventive rule:
  - For architecture explanations, distinguish operator input, API transport, controller authority, IK/servo command layer, and telemetry flow.

#### User Preferences

- New or reinforced preference:
  - User wants conceptual clarity around the live setup before deciding whether to adopt a new teleop stack.
- How it changed execution:
  - Focused on module boundaries and data flow rather than additional repo recommendations.

#### What Worked

- Pattern/check that worked:
  - Re-reading `TeleopPanel`, FastAPI jog endpoints, controller UDP dispatch, and `command_api` jog thread made the current authority boundary clear.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - When proposing LeRobot/HEBI adoption, keep GradientOS as motion authority unless the user explicitly wants a LeRobot-native robot wrapper.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need actual HEBI Mobile I/O discovery/latency test on the iPhone 16 before implementing a hardware-facing bridge.

### 2026-05-14 22:26 CDT - Jog IK and hardware speed explanation

#### Task Summary

- Explained HEBI Mobile I/O, the current realtime jog IK loop, and how repo speed/baud/hardware limits relate to phone-pose teleop.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - Checked local jog constants, servo sync-write code, Feetech config, URDF velocity tags, and external HEBI/Feetech specs before answering.
- Preventive rule:
  - When discussing robot speed, separate communication baud, control-loop frequency, Cartesian command caps, servo speed register units, and physical no-load actuator specs.

#### User Preferences

- New or reinforced preference:
  - User wants mechanics-level explanations of the control loop, including whether commands are frame-based and how speed limiting actually happens.
- How it changed execution:
  - Answered with the exact GradientOS jog loop semantics instead of only high-level architecture.

#### What Worked

- Pattern/check that worked:
  - Reading `command_api._jog_controller_thread` showed the critical behavior: velocity integration, IK solve, joint clamp, then `set_servo_positions(..., 800, 0)`.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - Before implementing HEBI spatial teleop, add or explicitly design filtering/error limiting so phone pose jumps cannot become large IK setpoint jumps.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need empirical loaded-arm speed/latency tests; repo values and Feetech no-load specs are not enough to certify safe teleop speeds.

### 2026-05-14 23:16 CDT - HEBI Mobile I/O bridge implementation

#### Task Summary

- Implemented an optional HEBI Mobile I/O iPhone ARKit bridge into GradientOS realtime jog, plus tests and docs.

#### Mistakes And Fixes

- Source: `[tool]`
- Mistake:
  - `pytest` was not on the shell PATH.
- Detection:
  - Initial focused test run exited with `zsh:1: command not found: pytest`.
- Fix:
  - Used the repo virtualenv directly: `./.venv/bin/python -m pytest ...`.
- Preventive rule:
  - In this repo, prefer `./.venv/bin/python -m pytest` when validating tests.

- Source: `[self]`
- Mistake:
  - Existing API test fixture did not accept the current `sections=` keyword used by weld planning.
- Detection:
  - Focused API endpoint test run failed `test_trajectory_plan_weld` with unexpected keyword argument `sections`.
- Fix:
  - Updated the dummy `plan_preview_trajectory_points` fixture to accept and record `sections`.
- Preventive rule:
  - When editing API tests, keep dummy command API signatures aligned with real command API functions.

#### User Preferences

- New or reinforced preference:
  - User wants the HEBI/LeRobot phone approach made concrete in the repo, with safety reasoning preserved.
- How it changed execution:
  - Added an executable bridge that defaults to dry-run and requires `--live` before sending hardware commands.

#### What Worked

- Pattern/check that worked:
  - Implementing HEBI as an input bridge kept GradientOS as the motion authority and reused `/control/jog/*`.
  - Tests covered the LeRobot axis convention, command clamping, quaternion parsing, and API endpoint formatting without requiring HEBI hardware.

#### What Did Not Work

- Failed attempt and why:
  - Direct `pytest` command was unavailable; virtualenv invocation worked.

#### Guardrails For Next Session

- Preflight rule:
  - Before any live HEBI teleop run, first run `gradient-iphone-hebi-teleop --list-devices` in dry-run mode, verify B1/A3/B8 behavior, then start with low `--max-linear-m-s` and `--max-target-offset-m`.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Needs physical iPhone 16 + HEBI Mobile I/O discovery/latency validation on the robot LAN.
  - If live tracking feels laggy or jumpy, add measured pose feedback into the bridge instead of relying only on virtual integration.

### 2026-05-15 02:29 CDT - Browser iPhone teleop UI removal

#### Task Summary

- Removed the initial browser-based iPhone Teleop UI attempt while keeping the HEBI Mobile I/O bridge path.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - Browser/Safari iPhone teleop was the wrong abstraction once the HEBI bridge became the preferred controller path.
- Detection:
  - User explicitly asked to get rid of the initial iPhone web attempt.
- Fix:
  - Removed the untracked TeleopPanel file and all tracked web UI/sidebar/CSS/docs/guardrail references specific to that browser panel.
- Preventive rule:
  - Once a teleop path is superseded, remove alternate operator surfaces instead of keeping confusing parallel entry points.

#### User Preferences

- New or reinforced preference:
  - User wants the iPhone path centered on HEBI Mobile I/O rather than a custom browser UI.
- How it changed execution:
  - Preserved the HEBI CLI and backend jog endpoint work, but removed browser Teleop affordances and docs.

#### What Worked

- Pattern/check that worked:
  - `rg` across `web-ui`, `docs`, and `AGENTS.md` caught all remaining browser teleop labels, shortcuts, CSS hooks, and metadata.
  - Web build plus focused API/bridge tests verified the removal did not break the UI or HEBI bridge.

#### What Did Not Work

- Failed attempt and why:
  - Initial broad patch missed a slightly different Robot Control JSX block; smaller targeted patches worked.

#### Guardrails For Next Session

- Preflight rule:
  - Do not reintroduce a browser iPhone teleop drawer unless the user explicitly requests browser-only teleop again.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - HEBI Mobile I/O still needs physical discovery and dry-run validation on the user's LAN.

### 2026-05-14 22:40 CDT - Phone teleop transport latency

#### Task Summary

- Answered whether Bluetooth would reduce iPhone teleop latency compared with local Wi-Fi.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - Verified HEBI Mobile I/O is documented as a local-network/API device before recommending transport choices.
- Preventive rule:
  - For phone teleop latency, distinguish LAN routing/AP relay from internet routing, and compare against control-loop and actuator latency before changing radios.

#### User Preferences

- New or reinforced preference:
  - User wants practical latency reasoning for the physical setup, not just software stack descriptions.
- How it changed execution:
  - Focused on Wi-Fi AP topology, Bluetooth/iOS constraints, and GradientOS loop bottlenecks.

#### What Worked

- Pattern/check that worked:
  - HEBI docs make the transport assumption clear: Mobile I/O should be on the local network and accessed through HEBI APIs.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - Prefer dedicated 5/6 GHz local Wi-Fi or robot AP for iPhone teleop; do not pursue Bluetooth unless the user explicitly wants to build a custom native iOS BLE controller.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Measure actual phone-to-controller timestamp latency once HEBI Mobile I/O is installed, because RF congestion and AP behavior dominate real-world jitter.

### 2026-05-14 23:06 CDT - HEBI Mobile I/O source availability

#### Task Summary

- Checked whether HEBI Mobile I/O is open source.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - Verified against HEBI docs/downloads, App Store metadata, and GitHub-search results before answering.
- Preventive rule:
  - For "is this app open source" questions, distinguish open APIs/examples from the app binary/source itself.

#### User Preferences

- New or reinforced preference:
  - User cares about source availability and dependency risk before adopting a teleop input layer.
- How it changed execution:
  - Answered directly and called out the proprietary-app caveat.

#### What Worked

- Pattern/check that worked:
  - HEBI docs list the app as an app-store download and expose API/docs examples, but no source repo for the app itself surfaced.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - Treat HEBI Mobile I/O as a closed-source convenience dependency unless HEBI publishes app source later.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If open-source-only is required, evaluate native ARKit/WebRTC or an open iPhone sensor streaming app instead of HEBI Mobile I/O.

### 2026-05-14 23:09 CDT - Browser HTTP in teleop loop

#### Task Summary

- Clarified that browser HTTP is the current command-update path for iPhone Teleop, but not the inner servo/IK loop itself.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Prior wording could imply HTTP is the whole control loop rather than the browser-to-API update path.
- Detection:
  - User challenged whether browser HTTP requests are really part of the control loop.
- Fix:
  - Separated the browser command path from the controller's 25 Hz jog loop.
- Preventive rule:
  - Use "command update path" for browser/HTTP and reserve "inner control loop" for controller-side jog/IK/servo execution.

#### User Preferences

- New or reinforced preference:
  - User wants precise control-loop terminology and will push back on vague architecture descriptions.
- How it changed execution:
  - Answered with exact file paths and timing behavior.

#### What Worked

- Pattern/check that worked:
  - `nl -ba` on `TeleopPanel.tsx`, API jog endpoints, and `_jog_controller_thread` made the boundary crisp.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - For HEBI integration, recommend a local Python bridge that bypasses browser HTTP unless the user specifically wants browser-only teleop.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If browser teleop remains the primary path, consider WebSocket/WebRTC DataChannel to reduce per-command HTTP overhead.

### 2026-05-15 02:30 CDT - HEBI accelerometer gravity setting

#### Task Summary

- Explained the HEBI Mobile I/O "Accelerometer includes gravity?" option for the iPhone teleop setup.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - Verified HEBI docs and app notes before answering.
- Preventive rule:
  - For HEBI Mobile I/O teleop, distinguish raw accelerometer feedback from ARKit pose feedback; the latter is what should drive robot pose.

#### User Preferences

- New or reinforced preference:
  - User is actively configuring the app and needs immediate practical settings guidance.
- How it changed execution:
  - Gave a direct setting recommendation and short rationale.

#### What Worked

- Pattern/check that worked:
  - HEBI convention treats accelerometer feedback as including gravity, so leaving it enabled best matches standard API expectations.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - Unless using raw linear acceleration for a specific gesture/filter, set Mobile I/O accelerometer feedback to include gravity.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Confirm which HEBI feedback fields the LeRobot phone teleop code reads before relying on accelerometer settings.

### 2026-05-15 10:45 CDT - Remote model/gripper branch check

#### Task Summary

- Checked remote branches and open PRs for a web UI 3D model update that might include the correct gripper asset.

#### Mistakes And Fixes

- Source: `[tool]`
- Mistake:
  - A broad `find /Users/dylanembry ...` search wandered into protected macOS folders and produced permission noise.
- Detection:
  - Terminal emitted repeated `Operation not permitted` messages while searching for `robot_cad`.
- Fix:
  - Killed the noisy search and reran with pruned home folders plus targeted `/Users/dylanembry/Projects`, `Desktop`, and `Documents` checks.
- Preventive rule:
  - When looking for user CAD folders on macOS, first search likely project roots and prune `Library`, `Pictures`, and `.Trash`.

#### User Preferences

- New or reinforced preference:
  - User needs remote-branch/PR triage tied to concrete asset paths, not just PR titles.
- How it changed execution:
  - Compared active branch diffs against `web-ui/public/assets`, `ArmVisualizer.tsx`, `robots`, and local `/Users/dylanembry/robot_cad/GRIPPER` files.

#### What Worked

- Pattern/check that worked:
  - `git diff --name-status origin/master...origin/multi-robot-architecture` quickly isolated the only remote branch touching the visualizer/model asset pipeline.
  - GitHub REST API worked for open PR metadata because local `gh` was not authenticated.

#### What Did Not Work

- Failed attempt and why:
  - `gh pr list` failed without `gh auth login`; public API fallback was enough for open PRs.

#### Guardrails For Next Session

- Preflight rule:
  - For web robot model work, inspect both the robot URDF/asset index and active tool library; gripper geometry may be a separate tool mesh rather than baked into the robot URDF.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - `origin/multi-robot-architecture` appears relevant but still uses template Gradient-05 assets and a TIG torch mesh; local gripper CAD in `/Users/dylanembry/robot_cad/GRIPPER` is not yet integrated.

### 2026-05-15 10:58 CDT - URDF and gripper mesh explanation

#### Task Summary

- Explained that URDF is a robot description XML, not the mesh itself, and that web visualizer gripper work likely means creating/placing a mesh referenced by a tool or `tool0` link.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - N/A.
- Preventive rule:
  - When discussing URDF with the user, use "robot assembly recipe" language and distinguish link/joint transforms from visual mesh geometry.

#### User Preferences

- New or reinforced preference:
  - User wants plain-language CAD/robotics terms before implementation details.
- How it changed execution:
  - Framed `tool0` as the wrist/end-effector attachment link and described an incremental CAD-to-web conversion path.

#### What Worked

- Pattern/check that worked:
  - The previous branch inspection gave enough concrete paths to explain the likely implementation without guessing.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - For gripper visual integration, decide whether it should be a robot URDF visual on `tool0` or an active tool asset before converting CAD.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need to convert/merge local gripper STEP/3MF assets into a browser-loadable STL/GLB and tune origin, scale, and rotation relative to J6.

### 2026-05-15 11:07 CDT - Active tool vs URDF terminology

#### Task Summary

- Clarified that "active tool asset" means the selected end-effector/tool configuration, not "active" as in Three.js animation.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Used "active tool asset" without defining that it is runtime-selected tool metadata/mesh.
- Detection:
  - User correctly challenged whether other URDF meshes are also active because they move in Three.js.
- Fix:
  - Explained the distinction between URDF-linked moving meshes, invisible end-effector frames like `tool0`, and runtime-loaded tool meshes.
- Preventive rule:
  - Define "active tool" before using it; avoid overloading "active" around animated robot meshes.

#### User Preferences

- New or reinforced preference:
  - User wants conceptual precision around CAD/URDF/Three.js integration before changing model assets.
- How it changed execution:
  - Answered with a decision rule: permanent robot geometry belongs in URDF; interchangeable tool geometry can be a separate tool asset attached to `tool0`/J6.

#### What Worked

- Pattern/check that worked:
  - Grounding the explanation in the inspected Gradient-05 branch made it clear that `tool0` can exist as an invisible frame even when the gripper mesh is absent.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - For gripper model work, ask whether the desired first pass is static visual gripper, selectable tool, or animated finger joints before editing URDF/assets.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Static gripper mesh is straightforward; animating gripper fingers requires additional URDF links/joints or custom Three.js tool articulation driven by gripper telemetry.

### 2026-05-15 11:25 CDT - URDF excerpt and TCP definition

#### Task Summary

- Showed the Gradient-05 URDF excerpt from the remote branch and defined TCP as Tool Center Point.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - N/A.
- Preventive rule:
  - When the user asks about TCP in this robot context, clarify it is Tool Center Point, not Transmission Control Protocol.

#### User Preferences

- New or reinforced preference:
  - User wants direct visibility into the files being discussed while learning URDF concepts.
- How it changed execution:
  - Pulled the exact remote URDF and explained the `tool0`/`joint6` section from that concrete file.

#### What Worked

- Pattern/check that worked:
  - `git show origin/multi-robot-architecture:... | nl -ba` gave a precise source without switching branches.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - Prefer exact URDF snippets with line references when explaining robot link/joint structure.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need to decide whether the gripper TCP should be the fingertip/pinch point, palm center, or another operational point before setting tool offsets.

### 2026-05-15 12:02 CDT - Running UI uses mini-6dof URDF

#### Task Summary

- Checked why the user sees an end effector in the running web UI and confirmed the local visualizer loads the mini-6dof-arm URDF, not the remote Gradient-05 asset index.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Previous explanation mixed the remote `Gradient-05` branch's `tool0` structure with the current local web UI's `mini-6dof-arm` URDF.
- Detection:
  - User observed a visible end effector in the running Three.js model, contradicting the idea that the end-effector mesh was absent.
- Fix:
  - Inspected the currently loaded local URDF path and identified `wrist.stl` as the visible end-effector/wrist geometry.
- Preventive rule:
  - Before answering "what do I see in the running UI?", verify the local visualizer's current asset path rather than relying on remote branch diffs.

#### User Preferences

- New or reinforced preference:
  - User wants explanations reconciled against observed runtime behavior.
- How it changed execution:
  - Checked `ArmVisualizer.tsx` and the exact local URDF before answering.

#### What Worked

- Pattern/check that worked:
  - `rg` plus `nl -ba` quickly showed the web UI loads `/assets/mini-6dof-arm/mini-6dof-arm.urdf` and that `wrist.stl` is visible while `tool_link` is an empty fixed child frame.

#### What Did Not Work

- Failed attempt and why:
  - Treating the remote branch's Gradient-05 URDF as representative of the user's running UI caused terminology drift.

#### Guardrails For Next Session

- Preflight rule:
  - Distinguish three model contexts: current local mini-6dof UI asset, remote Gradient-05 branch asset, and CAD files in `/Users/dylanembry/robot_cad`.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - If integrating the printed gripper into the current UI, decide whether to replace/extend `wrist.stl`, attach visual geometry to `tool_link`, or adopt the remote branch's robot/tool asset index.

### 2026-05-15 12:06 CDT - HEBI iPhone teleop natural follow pass

#### Task Summary

- Implemented the requested HEBI bridge changes: identity phone-to-robot axes by default, optional inversion flags, live `/info/pose` feedback latch, and Mobile I/O reconnect scanning.
- Kept B1 as the only clutch/recenter control; no B2 recenter was added.

#### Mistakes And Fixes

- Source: `[user]`
- Mistake:
  - The first HEBI mapper used a swapped LeRobot-style axis convention that did not match the user's desired mental model.
- Detection:
  - User said robot X/Y/Z should map directly to phone X/Y/Z and observed unnatural sim motion.
- Fix:
  - Changed default mapping to identity and made sign corrections explicit via `--invert-*` flags.
- Preventive rule:
  - For teleop controls, default to the operator's stated frame model first, then add calibration flags for hardware/hold-specific sign fixes.

#### User Preferences

- New or reinforced preference:
  - B1 should remain the clutch/recenter action; avoid adding another recenter button unless explicitly requested.
- How it changed execution:
  - Implemented release + hold B1 as the documented recenter flow and did not add B2 logic.

#### What Worked

- Pattern/check that worked:
  - Targeted mapper unit tests caught the old swapped-axis assumptions and now pin identity mapping plus inversion behavior.

#### What Did Not Work

- Failed attempt and why:
  - Plain `python` was not available in this shell PATH; repo venv Python was used instead for compile validation.

#### Guardrails For Next Session

- Preflight rule:
  - When tuning live teleop feel, change only one of mapping, scaling, filtering, or speed caps at a time and validate in sim before hardware.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Needs real Mobile I/O sim/live feel test to decide whether any default sign inversions are needed for the user's preferred phone grip.

### 2026-05-15 12:09 CDT - Sim stack startup for teleop testing

#### Task Summary

- Started simulator controller, API, and web UI for the user's HEBI/iPhone teleop testing session.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - None.
- Detection:
  - N/A.
- Fix:
  - N/A.
- Preventive rule:
  - Before starting the GradientOS stack, check UDP `3000`, API `4000`, and web `8000` listeners so duplicate services do not collide.

#### User Preferences

- New or reinforced preference:
  - User wants the sim stack started directly for hands-on teleop iteration.
- How it changed execution:
  - Launched services instead of giving command instructions.

#### What Worked

- Pattern/check that worked:
  - Starting `./run-sim.sh`, then `./run-api.sh`, then `./run-web.sh -- --host 0.0.0.0 --port 8000` produced healthy listeners and a valid `/info/pose` response.

#### What Did Not Work

- Failed attempt and why:
  - N/A.

#### Guardrails For Next Session

- Preflight rule:
  - Verify `/info/pose` before running live HEBI teleop so the bridge can latch an actual robot/sim pose on B1 enable.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Keep long-running service sessions alive while testing; restarting them will reset sim state.

### 2026-05-15 12:45 CDT - Phone frame diagnostics after HEBI teleop stall

#### Task Summary

- Shut down the sim/API/web stack and added a no-motion HEBI phone-frame diagnostic path.
- Added API phone-pose storage, bridge pose publishing/calibration prompts, and a web UI phone cuboid/Phone Frame drawer.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Prior tuning jumped into robot jog behavior before the raw phone frame was visible enough to validate.
- Detection:
  - User reported unnatural motion and a stall after a few seconds; controller logs showed repeated `IK solution not found for step` while commands continued.
- Fix:
  - Added a raw phone-pose visualization/calibration path that does not command robot motion.
- Preventive rule:
  - For spatial teleop, validate raw controller pose and operator-frame mapping before tuning IK-driven robot motion.

#### User Preferences

- New or reinforced preference:
  - User wants an interactive calibration sequence phrased in human movement terms like "move left" before deciding axis mappings.
- How it changed execution:
  - Added `--calibrate-phone-frame` prompts and a Phone Frame web drawer instead of only more CLI flags.

#### What Worked

- Pattern/check that worked:
  - Reading long-running controller output after shutdown exposed the IK-failure stall signature immediately.

#### What Did Not Work

- Failed attempt and why:
  - Full 6-DoF orientation jogging appears too easy to push into unreachable IK states with the current mapping/caps.

#### Guardrails For Next Session

- Preflight rule:
  - Re-test HEBI teleop first with phone visualization and no robot motion; then test translation-only using `--rotation-scale 0` before enabling orientation.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need a real iPhone calibration run with API/web open to confirm the phone cuboid axes and choose any `--invert-*` flags.

### 2026-05-15 12:47 CDT - Complete shutdown must include HEBI bridge

#### Task Summary

- User corrected that not everything was shut down; found and terminated two leftover HEBI bridge processes.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Checked only stack listener ports and missed HEBI bridge processes that were still running without active listeners.
- Detection:
  - User said everything was not shut down.
- Fix:
  - Ran direct process sweeps for GradientOS/HEBI/Vite/API/controller names and killed the remaining bridge PIDs.
- Preventive rule:
  - For shutdown requests, always run both `lsof` port checks and `ps`/`pgrep` process-name sweeps.

#### User Preferences

- New or reinforced preference:
  - "Everything" includes controller/API/web plus HEBI bridge and other teleop helper processes.
- How it changed execution:
  - Terminated leftover bridge processes and re-verified with process and port sweeps.

#### What Worked

- Pattern/check that worked:
  - `ps -axo ... | rg 'gradient_os|hebi_mobile|iphone-hebi|vite|uvicorn'` exposed the leftover live bridge immediately.

#### What Did Not Work

- Failed attempt and why:
  - Port-only checks missed a bridge process with a closed API socket.

#### Guardrails For Next Session

- Preflight rule:
  - After stopping a teleop session, confirm no `gradient-iphone-hebi-teleop` or `hebi_mobile_io_bridge` process remains.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - None; re-check showed no remaining stack processes or listeners.

### 2026-05-15 15:33 CDT - HEBI not discovered during live-to-sim retry

#### Task Summary

- Started sim/API/web for live-to-sim testing, then attempted to launch the HEBI bridge with translation-only conservative settings.

#### Mistakes And Fixes

- Source: `[tool]`
- Mistake:
  - None in startup; HEBI discovery returned no Mobile I/O devices.
- Detection:
  - Bridge printed empty discovered-device list and exited on both default and 5-second lookup attempts.
- Fix:
  - Left sim/API/web running and did not leave a failed bridge process alive.
- Preventive rule:
  - When HEBI discovery fails, verify app foreground/network/family/name before changing teleop mapping code.

#### User Preferences

- New or reinforced preference:
  - User wants to test against the sim and see the 3D model move, not just dry-run phone diagnostics.
- How it changed execution:
  - Used `--live --rotation-scale 0` with conservative caps against the simulator.

#### What Worked

- Pattern/check that worked:
  - Stack health checks confirmed simulator pose and web/API listeners before trying the bridge.

#### What Did Not Work

- Failed attempt and why:
  - HEBI Mobile I/O was not visible on the LAN during bridge startup.

#### Guardrails For Next Session

- Preflight rule:
  - Confirm `gradient-iphone-hebi-teleop --list-devices` sees `family='HEBI' name='mobileIO'` before live-to-sim testing.

#### Follow-Ups / Risks

- Remaining risk or pending check:
  - Need user to reopen/foreground HEBI Mobile I/O or confirm the iPhone LAN/settings, then retry the live bridge.

### 2026-05-15 15:36 CDT - HEBI bridge live to sim restored

#### Trigger / Context

- User asked to rerun the bridge and clarify when the Three.js phone model appears with the robot.

#### Current State

- Sim/API/web were already running.
- Started a live HEBI bridge with translation-only conservative settings:
  - `--live`
  - `--rotation-scale 0`
  - `--max-target-offset-m 0.03`
  - `--max-linear-m-s 0.03`
  - `--translation-scale 0.5`
  - slower diagnostic publish and longer stale/reconnect settings.
- HEBI Mobile I/O was discovered at `192.168.1.221` and connected.
- `/teleop/phone-pose` returned fresh `status: ok` diagnostics.

#### Useful Mental Model

- Phone model visibility in the web UI depends on API phone-pose diagnostics, not on B1/deadman being held.
- B1 only controls live robot jog enable. Diagnostic phone samples are published while the bridge has valid Mobile I/O feedback.

#### Guardrails For Next Session

- If the user says the phone model is missing, check `/teleop/phone-pose` freshness first, then confirm the web UI is using `http://127.0.0.1:4000`/`localhost:4000` as its API host and that the browser has the UI connected.

### 2026-05-15 15:48 CDT - Full stack shutdown verified

#### Trigger / Context

- User asked to shut everything down after the live HEBI-to-sim test.

#### What Happened

- Stopped the running HEBI bridge with `Ctrl-C`; it reached the interrupt handler and closed.
- Sent `SIGINT` to the sim controller, API, and Vite web UI.
- Verified no matching GradientOS/HEBI/Vite processes remained.
- Verified UDP `3000`, TCP `4000`, and TCP `8000` were clear.

#### Observation

- Before shutdown, bridge logs showed B1-enabled commands were sent successfully for a while, then repeated stale-feedback reconnect cycles to the same Mobile I/O IP.

#### Guardrails For Next Session

- On next live test, monitor for `Feedback stale for 30s` messages; if they recur, treat Mobile I/O feedback freshness as a separate reliability issue from robot IK or Three.js visualization.

### 2026-05-15 16:14 CDT - Explain diagnostic pose versus IK control path

#### Trigger / Context

- User asked what data is posted to `/teleop/phone-pose`, how the UI GET payload differs from IK input, and how IKFast fits into the teleop stack.

#### Useful Mental Model

- `/teleop/phone-pose` is observability/debug state:
  - raw-ish HEBI/ARKit phone position in meters
  - quaternion/euler orientation
  - reference-relative deltas
  - optional mapped target and generated command velocities while B1 is active
- IK never consumes `/teleop/phone-pose`.
- IK consumes a target tool-tip position vector plus target orientation matrix created inside the controller jog loop after integrating the latest commanded Cartesian/angular velocities over `dt`.

#### Guardrails For Next Session

- When debugging teleop behavior, separate three questions:
  - Is the phone pose diagnostic fresh?
  - Is the bridge generating reasonable `/control/jog/velocity` commands?
  - Is the controller jog loop finding IK for the resulting target tool pose?

### 2026-05-15 16:26 CDT - Quaternion/Euler explanation

#### Trigger / Context

- User asked what quaternion/euler orientation means and whether those are the native ARKit/HEBI app formats.

#### Useful Mental Model

- The bridge consumes HEBI Mobile I/O as `mobile_io.position` plus `mobile_io.orientation`.
- `mobile_io.position` is treated as an XYZ position vector in meters.
- `mobile_io.orientation` is treated as a quaternion; default input order is `wxyz`.
- The bridge publishes normalized `xyzw` quaternion for Three.js/SciPy and derives Euler XYZ degrees only as a human-readable/debug fallback.

#### Guardrails For Next Session

- Do not treat Euler as the control-source format. It is derived from the quaternion and can be misleading near singularities or if rotation order expectations differ.

### 2026-05-15 17:23 CDT - Desired B1 reset semantics

#### Trigger / Context

- User emphasized that B1 re-engage/reset needs different source-of-truth behavior for translation and orientation.

#### User Intent As Understood

- Translation:
  - Robot/sim current end-effector position is source of truth on B1 re-engage.
  - Releasing B1 lets the operator move the phone physically without moving the robot.
  - Re-engaging B1 seeds the new phone position to the robot's current position so motion continues from where the robot was left.
- Orientation:
  - Physical phone orientation should be source of truth on B1 re-engage.
  - If the robot was rolled while B1 was held, then B1 is released and the phone is physically rolled back, re-engaging B1 should make the gripper target the phone's current orientation, not preserve the robot's current rolled orientation.

#### Current Code Reality

- Current bridge matches the desired translation clutch behavior.
- Current bridge does not match the desired orientation source-of-truth behavior; it latches robot orientation on every `_enable()` and uses relative phone rotation from the B1 reference.

#### Guardrails For Next Session

- Do not implement orientation by simply resetting the relative rotation reference on every B1 engage if the user confirms absolute phone orientation should own orientation.
- Likely design: persistent phone-to-tool orientation calibration plus B1 translation clutch; speed-limit orientation correction on re-engage.

### 2026-05-15 17:32 CDT - Camera selection for robot learning

#### Trigger / Context

- User asked for camera recommendations for inference, fine-tuning, and future training with VLA/WAM-style robot learning on the GradientOS CheapRobotArm setup.

#### Useful Mental Model

- For this repo and current laptop/CH340 workflow, USB/UVC cameras are the lowest-friction path because `USBCameraDriver` uses OpenCV and works on macOS/Linux/Pi.
- The servo power/USB-TTL board's open 3/4-pin connectors should not be assumed to be camera connectors; only use them for a camera if the board documentation explicitly says the header is USB 5V/D+/D-/GND and the pinout is verified.
- For learning datasets, two stable RGB views at about 30 FPS are usually more valuable than one high-end camera; add global shutter mainly for wrist/fast-motion views.

#### Guardrails For Next Session

- Recommend a staged camera setup: static RGB overview first, second RGB or wrist camera next, depth camera only after the RGB data path is reliable.
- Keep camera wiring electrically separate from noisy servo power where possible; use laptop USB/powered USB hub for cameras and keep CH340 direct if serial reliability matters.

### 2026-05-15 18:20 CDT - Implemented B1 split reset + target phone marker

#### Trigger / Context

- User confirmed B1 re-engage should immediately drive gripper orientation toward current phone orientation and asked for the Three.js phone model to sit at the desired end-effector pose.

#### What Changed

- Translation remains a B1 clutch:
  - each B1 enable latches current phone position and current robot tool position.
  - target position is `reference_robot_position + mapped_phone_translation_delta`.
- Orientation now uses persistent first-latch calibration:
  - first live latch sets `phone_to_robot_orientation = robot_orientation * phone_orientation^-1`.
  - later B1 enables do not reset this orientation calibration.
  - target orientation is derived from current physical phone orientation under speed/IK limits.
- `/teleop/phone-pose` now carries absolute desired target pose fields for UI:
  - `target_position_m`
  - `target_orientation_quat_xyzw`
  - `target_orientation_euler_deg`
- Web phone cuboid now uses target pose when present and transforms robot-local target coordinates through the URDF scene frame so it should visually clip/overlap the gripper.

#### Validation

- Focused Python tests passed: `28 passed`.
- Web UI build passed with existing OCCT/chunk warnings.
- `git diff --check` passed.

#### Guardrails For Next Session

- If orientation feels offset, check the first B1 latch posture before changing quaternion math; the first latch is now the orientation calibration moment.
- If the phone cuboid does not overlap the gripper, compare API `target_position_m` to FK/end-effector coordinates and inspect whether URDF local-to-world transform differs from solver frame.

### 2026-05-15 18:25 CDT - Full live-to-sim stack running

#### Current Running Services

- Sim controller: `python -m gradient_os.run_controller --sim`, UDP `3000`.
- API: `python -m gradient_os.api.main`, TCP `4000`.
- Web UI: Vite on TCP `8000`.
- HEBI bridge: `gradient-iphone-hebi-teleop --live` connected to `HEBI/mobileIO` at `192.168.1.221`.

#### Bridge Settings

- Conservative live-to-sim settings:
  - `--translation-scale 0.5`
  - `--max-target-offset-m 0.03`
  - `--max-linear-m-s 0.03`
  - `--max-target-rotation-deg 25`
  - `--max-angular-deg-s 20`
  - `--phone-pose-publish-interval-s 0.2`
  - `--stale-timeout-s 5`
  - `--reconnect-after-stale-s 30`

#### Guardrails For Next Session

- The phone-pose endpoint is fresh before B1 but only contains absolute target fields after B1 is held.
- Use `http://localhost:8000`, click Connect, open Phone Frame with shortcut `5`, then hold B1 for live target visualization and motion.

### 2026-05-15 18:31 CDT - Phone marker looked position-locked

#### Observation

- User reported phone model did not move positionally when B1 was engaged.
- Bridge logs showed nonzero linear commands, often near the conservative caps.
- Controller logs showed repeated IK failures, so the simulated robot pose often stayed fixed despite commands.
- `/teleop/phone-pose` became stale after feedback/reconnect churn.

#### Likely Cause

- The UI is now rendering bounded `target_position_m` when present, not raw phone position.
- The active bridge was launched with `--max-target-offset-m 0.03`; after phone delta exceeds that, the desired marker saturates near a 3 cm offset from the B1-latched robot pose.
- Rotation-enabled IK failures make the robot/target relationship look even more stuck because the robot cannot accept many commanded steps.

#### Guardrails For Next Session

- For diagnosing phone positional interpretation, either run translation-only (`--rotation-scale 0`) or show raw phone delta and bounded desired target as separate visuals.
- Do not assume locked marker means no phone data; check bridge `cmd lin=...`, endpoint `delta_m`, endpoint `target_position_m`, and controller IK warnings separately.

### 2026-05-15 18:41 CDT - Phone marker now unclamped

#### Trigger / Context

- User clarified phone model should show raw phone delta anchored to the gripper on B1 re-engage, and should remain free to move beyond the robot command clamp.

#### What Changed

- Added separate visual pose fields:
  - `visual_position_m`
  - `visual_orientation_quat_xyzw`
  - `visual_orientation_euler_deg`
- Three.js phone cuboid now uses `visual_*` first.
- Clamped robot target fields remain for debugging and motion safety:
  - `target_position_m`
  - `target_orientation_*`

#### Runtime State

- Sim/API/web are running.
- API has been restarted and returns `{"status":"none"}` for `/teleop/phone-pose`.
- HEBI bridge restart failed because Mobile I/O was not discovered; user likely needs to foreground/reopen the iPhone HEBI Mobile I/O app.

#### Guardrails For Next Session

- Explain `--max-target-offset-m` as the robot command safety radius only; it should no longer constrain the phone cuboid.
- When HEBI reconnects, confirm endpoint includes `visual_position_m` after B1 is held.

### 2026-05-15 18:55 CDT - Robot command target limits removed by default

#### Trigger / Context

- User said they do not want to limit the robot command target at all.

#### What Changed

- `max_target_offset_m` and `max_target_rotation_deg` now default to `inf`.
- Target limit flags still exist for optional experiments, but finite values must be passed deliberately.
- `0`, negative values, and `inf` mean unlimited for target offset/rotation.
- Velocity limits remain separate and still cap how fast the robot tries to approach the target.

#### Runtime State

- Sim/API/web are running.
- HEBI bridge is not running; last discovery attempt did not find Mobile I/O.

#### Guardrails For Next Session

- When rerunning HEBI bridge for the user's desired behavior, do not pass `--max-target-offset-m` or `--max-target-rotation-deg`.
- Still keep conservative `--max-linear-m-s` and `--max-angular-deg-s` unless user explicitly wants those speed limits changed.

### 2026-05-15 18:26 CDT - Camera module + model scaling consensus

#### Trigger / Context

- User asked what cameras research/production teleop setups use beyond C920-class webcams and whether higher resolution or higher framerate speeds learning for VLM/VLA/causal-video world models.

#### Useful Mental Model

- C920/C922-class webcams are common in early low-cost research because they are easy USB/UVC devices, but they are better as fixed external cameras than wrist cameras.
- For wrist mounting on a light hobby arm, compact modules matter: RealSense D405, Pi/IMX296 global-shutter modules, Arducam USB global-shutter modules, OAK-D Lite, or action-camera/fisheye designs are closer to research practice.
- Current VLA/policy training commonly sees 224x224 or 256x256 images and 10-30 Hz data, even when raw capture is higher resolution; high native resolution mainly helps crop quality, calibration, and future reprocessing.
- Higher framerate helps temporal aliasing, latency matching, and fast manipulation, but most manipulation policies still train/execute at about 10-30 Hz or use action chunks rather than consuming every high-FPS frame.

#### Guardrails For Next Session

- Do not imply 4K capture automatically improves VLA fine-tuning; cite OpenVLA's 224 vs 384 result and OpenPI's 224 preprocessing.
- Recommend spending first on camera placement, lighting, focus, synchronization, and multiple views before paying for raw megapixels.

### 2026-05-15 18:28 CDT - Gripper CAD to URDF terminology check

#### Trigger / Context

- User asked what it would take to use gripper 3D files from `/Users/dylanembry/robot_cad` as the wrist/end-effector representation in the robot URDF, replacing the weld end effector, and asked for terminology validation.

#### Useful Mental Model

- In this repo, `wrist` is an actual URDF link with a mesh; `tool_link` is an empty controlled tool frame fixed 0.180 m along +X from `wrist`.
- Runtime IK/FK does not discover that offset from the web URDF; it uses `src/gradient_os/ik_solver.py::END_EFFECTOR_OFFSET`, currently `[0.180, 0.0, 0.0]`.
- The gripper CAD is mostly STEP in millimeters, not URDF-ready render meshes. Convert to STL/OBJ/DAE/GLB or export from CAD before referencing it from URDF.

#### Guardrails For Next Session

- Prefer saying "attach the gripper assembly to the wrist/flange and set the TCP/tool frame" instead of "use files as the wrist frame" unless the user truly wants to replace the kinematic wrist link.
- Keep `web-ui/public/assets/mini-6dof-arm/mini-6dof-arm.urdf`, `mini-6dof-arm/mini-6dof-arm.urdf`, and `END_EFFECTOR_OFFSET` consistent if the controlled tool point changes.

### 2026-05-17 00:15 CDT - Animated gripper STEP conversion workflow

#### Trigger / Context

- User asked for the best way to convert the separate gripper STEP parts to STL while preserving moving parts in URDF and Three.js.

#### Useful Mental Model

- Treat the gripper like a small robot subtree:
  - fixed base/mount/housing links attach to `wrist` or a new flange/gripper mount.
  - moving finger/gear meshes stay as separate links.
  - URDF joints define pivots/axes/limits; STL files only provide shape.
- The active web visualizer currently animates only `joint1` through `joint6`; gripper joint names such as `gripper_joint` will load through `urdf-loader` but need explicit UI/telemetry mapping to move visually.
- Local converter reality:
  - `FreeCADCmd`, `freecad`, `blender`, and `meshlabserver` are not installed.
  - `assimp` is installed but fails on the gripper Autodesk STEP schema, so it is not a reliable conversion path here.

#### Guardrails For Next Session

- Recommend FreeCAD/Fusion/Onshape for authoritative STEP-to-STL export, one STL per link, with origins/pivots preserved or documented.
- Avoid one combined STL except as a temporary static visual check.
- If implementing this, update both visual assets/URDF and the frontend joint animation path; update `END_EFFECTOR_OFFSET` only after choosing the real TCP.

### 2026-05-17 13:03 CDT - FreeCAD app-bundle lookup correction

#### Trigger / Context

- User corrected the earlier claim that FreeCAD was not installed.

#### Mistakes And Fixes

- Source: `[self]`
- Mistake:
  - Checked only `which FreeCADCmd`, `which freecad`, and similar PATH-based commands.
- Detection:
  - User pointed out FreeCAD is installed; a broader app-bundle search found `/Applications/FreeCAD.app/Contents/MacOS/FreeCAD`.
- Fix:
  - Verified FreeCAD 1.1.1 runs with `-c` and successfully converted a gripper STEP file to STL.
- Preventive rule:
  - On macOS, check `/Applications/*.app/Contents/MacOS/*` and Spotlight/app-bundle paths before declaring GUI tools unavailable.

#### Guardrails For Next Session

- Use `/Applications/FreeCAD.app/Contents/MacOS/FreeCAD` for scripted gripper STEP conversion unless a cleaner `FreeCADCmd` path is added to PATH.
- Ignore the missing 3Dconnexion framework warning unless conversion actually fails.

### 2026-05-21 15:32 CDT - FreeCAD headless and rigid-link STL grouping

#### Trigger / Context

- User asked how FreeCAD works headlessly and how to combine STEP files into larger STL meshes while preserving assembled geometry and gripper motion.

#### Useful Mental Model

- Prefer `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd` for headless scripts; it exposes FreeCAD's embedded Python API in-process (`FreeCAD`, `Part`, `Mesh`, `Import`), not a network/API server.
- Combine STEP files by rigid URDF link, not by visual convenience:
  - fixed mount/housing/lid/spacers can become one `gripper_base` mesh.
  - parts moving together with a finger can become one finger mesh.
  - anything that rotates/slides relative to another part needs its own link/mesh or its own rigid group.
- Assembly geometry is preserved only if source files share a common assembly coordinate system or if explicit placements/transforms are applied before meshing.

#### Guardrails For Next Session

- If implementing, first generate an assembly manifest mapping source STEP files to URDF link names and transforms.
- Export a debug scene/combined preview before writing final URDF so misplaced part origins/pivots are caught early.
- Update the active Three.js joint animation loop for any new `gripper_*` joints because it currently drives arm joints by name.

### 2026-05-15 18:37 CDT - Frontier lab camera-strategy sources

#### Trigger / Context

- User corrected that camera research should include frontier lab blogs/papers, not only open-source/reproducible setups.

#### Useful Mental Model

- Frontier labs usually disclose visual architecture and data strategy more than exact camera SKUs.
- Physical Intelligence emphasizes heterogeneous robot action data, human/egocentric video, observation memory, and visual subgoals.
- Figure explicitly moved Helix logistics from monocular to stereo visual input and fuses stereo features before tokenization to avoid visual-token blowup.
- 1X world-model posts emphasize video frames, robot observations, action trajectories, and grounding generated rollouts in robot camera intrinsics and egocentric viewpoint.
- NVIDIA GR00T/Cosmos emphasizes visual observations through a VLM, human ego videos, synthetic/robot data, and video/world-model priors.
- Tesla publicly emphasizes vision/planning, per-camera raw-image networks, and multi-camera video fusion for cars; Optimus camera hardware details remain sparse in official sources.

#### Guardrails For Next Session

- When answering camera strategy for this user, separate "frontier lab architectural lesson" from "buyable module for GradientOS."
- Do not overclaim exact camera part numbers for PI/Figure/Tesla/1X unless an official source states them.

### 2026-05-15 18:56 CDT - BEV/depth explanation and practical camera recommendation

#### Trigger / Context

- User asked what BEV and monocular depth mean and how that changes camera recommendations.

#### Useful Mental Model

- BEV means bird's-eye view: a learned top-down spatial representation fused from one or more camera images, not necessarily a literal overhead camera.
- Monocular depth means estimating distance from a single RGB camera using learned visual cues; it is useful but less metrically reliable than stereo/depth sensors for close manipulation.
- For GradientOS, recommend RGB-first data collection: one fixed wide context view plus one light egocentric/wrist or gripper-adjacent camera, then add stereo/depth later if specific failures justify it.

#### Guardrails For Next Session

- Do not recommend a heavy webcam as the wrist camera for the CheapRobotArm; use webcams/static cameras for external context only.
- Do not imply BEV is directly necessary for tabletop manipulation; it is a useful autonomy representation but not the first hardware requirement.

### 2026-05-16 01:31 CDT - Teleop stack runtime start

#### Trigger / Context

- User asked to run the stack for sim testing after removing robot command target limits.

#### Useful Mental Model

- Starting `./run-sim.sh` / `./run-api.sh` via one-shot background shell commands can appear to exit quietly under this tool environment; detached `screen` sessions kept the stack alive cleanly after handoff.
- The stack for this workflow is simulator controller on UDP `3000`, API on TCP `4000`, Vite UI on TCP `8000`, and `gradient-iphone-hebi-teleop` posting live `/teleop/phone-pose` frames.
- With B1 released, `/teleop/phone-pose` should show `enabled:false`; this still confirms HEBI Mobile I/O discovery and pose streaming.

#### Guardrails For Next Session

- Keep HEBI bridge launches target-unlimited by default: do not pass `--max-target-offset-m` or `--max-target-rotation-deg` unless the user explicitly asks for a target leash.
- Before reporting the stack is ready, verify all three ports plus a live `/teleop/phone-pose` response.
- If raw HEBI `position_m` looks huge before B1, do not treat that as command movement by itself; the B1 latch is expected to seed the robot-relative translation baseline.

### 2026-05-16 01:56 CDT - HEBI phone-frame calibration pass

#### Trigger / Context

- User needed live calibration for iPhone/HEBI teleop after the initial sim behavior felt unintuitive.

#### Useful Mental Model

- The first calibration run was noisy because each movement was measured against the original neutral pose, not a fresh pre-move neutral. Patch the wizard to capture `return to neutral -> sample reference -> move -> sample delta` for each step.
- Clean translation result from second pass:
  - Forward/back: `+X` / `-X`
  - Left/right: `+Y` / `-Y`
  - Up/down: `+Z` / `-Z`
- Clean orientation result from second pass:
  - Yaw left/right: `+Z` / `-Z`
  - Pitch top edge up/down: `+X` / `-X`
  - Roll left: `-Y`; roll right sample was weak but expected opposite `+Y`.
- Because the live mapper uses direct phone position deltas plus quaternion orientation alignment, the correct starting launch remains default/no-invert flags.

#### Guardrails For Next Session

- Before running calibration, stop any live HEBI bridge process and send `POST /control/jog/stop`.
- If live sim movement feels reversed after this calibration, change one invert flag at a time and retest; do not add target leashes as a calibration workaround.
- Consider making calibration a web UI flow later; terminal relay is workable but slow and easy to mis-sample.

### 2026-05-16 02:03 CDT - Sim stack shutdown before real hardware

#### Trigger / Context

- User asked to shut down the sim stack and said they want to do teleop with the real robot.

#### Useful Mental Model

- Clean shutdown sequence that worked: `POST /control/jog/stop`, quit `gradient-hebi`, `gradient-web`, `gradient-api`, `gradient-sim`, then kill orphaned child processes if `screen -ls` is empty but ports remain bound.
- Verification should include no `screen` sessions, no GradientOS teleop process matches, and no listeners on UDP `3000`, TCP `4000`, or TCP `8000`.

#### Guardrails For Next Session

- Before starting real hardware, confirm the arm is powered, physically clear, and supervised.
- Start real hardware with `./run.sh`, not `./run-sim.sh`; only start API/web/HEBI bridge after the real controller reports connection.
- Preserve the calibrated/default HEBI mapping: no invert flags and no target leash flags unless live real movement proves otherwise.

### 2026-05-16 02:06 CDT - Real stack blocked by absent servos

#### Trigger / Context

- User asked to bring up the real robot stack after sim shutdown.

#### Useful Mental Model

- `./run.sh` can bind UDP `3000` and `/health` can pass even when the real arm is not actually controllable.
- In this run, `/dev/cu.usbserial-110` opened at `1000000` baud, but all expected IDs were absent: `10`, `20`, `21`, `30`, `31`, `40`, `50`, `60`, and `100`.
- `/info/pose` returned the default zero-joint FK pose; treat it as a fallback/default, not measured hardware state.

#### Guardrails For Next Session

- Do not start `gradient-iphone-hebi-teleop --live` while all servos are absent.
- Check power/wiring/baud/ID discovery first, then restart `gradient-real` and verify servo presence before live teleop.
- API/web may stay up for monitoring, but HEBI live bridge should wait for a healthy servo bus.

### 2026-05-16 02:13 CDT - Servo bus reachable, controller detection fixed

#### Trigger / Context

- User asked to try reaching the servos again after the real controller previously reported every ID absent.

#### Useful Mental Model

- `scripts/scan_servo_bus.py` originally could be fooled by CH340 half-duplex echo because it accepted any 6-byte frame with the requested ID. Patch it to skip the exact echoed PING.
- Standalone read-only position probe is the most decisive non-motion check: all 9 expected IDs returned raw positions on `/dev/cu.usbserial-110` at `1000000` baud.
- The controller failure was not the bus; it was `servo_protocol.py` delegating legacy calls to an uninitialized Feetech backend after backend auto-detection failed. Legacy serial opened the right port, but PING still called the failed backend.
- After patching backend delegation to require `is_initialized`, `./run.sh` sees all 9 servos and reads a real nonzero current arm state.

#### Guardrails For Next Session

- Do not trust PING-only scans on CH340 adapters unless echo filtering is in place; prefer a read-position probe before declaring hardware reachable.
- It is now safe to start HEBI live only after the robot is clear and B1 is released; current real controller, API, and web are up, but HEBI is off.
- Future cleanup: make the Feetech backend auto-detect macOS `/dev/cu.usbserial-*` so startup does not need the legacy fallback path.

### 2026-05-16 02:51 CDT - Real HEBI bridge live

#### Trigger / Context

- User asked to start the HEBI bridge after the real controller was confirmed healthy.

#### Useful Mental Model

- Launch command used no target leash flags and kept conservative speed caps: `--max-linear-m-s 0.03`, `--max-angular-deg-s 20`.
- `/teleop/phone-pose` with `enabled:false` means the bridge is connected and publishing diagnostics while B1 is released; real motion starts only when B1 is held.

#### Guardrails For Next Session

- Treat the current stack as physically live: `gradient-real`, `gradient-api`, `gradient-web`, and `gradient-hebi` are all running.
- If anything feels wrong, first action is `POST /control/jog/stop` and stop `gradient-hebi`.
- Preserve default/no-invert mapping unless the user reports a specific axis reversal during live hardware testing.

### 2026-05-16 02:59 CDT - IDs 20/30 latched fault during live teleop

#### Trigger / Context

- User reported many "Position Fault" / SyncRead no-feedback warnings and rapidly blinking TX/RX lights on the PCB during real HEBI teleop.

#### Useful Mental Model

- Rapid TX/RX blinking means the serial bus is busy; it is expected while controller telemetry/SyncRead is active and is not itself proof of power or baud failure.
- In this case, controller logs narrowed the issue to IDs `20` and `30`, both returning status byte `32` / `Position Fault`; SyncRead then marked those IDs invalid because packets with error bytes are discarded.
- Direct read-only probing showed the bus is still healthy: every servo responds, voltage is `11.8-11.9V`, and only IDs `20`/`30` have status `32`.
- Positions for IDs `20`/`30` were near their target positions and inside configured raw angle limits, so the likely state is a latched servo alarm after motion/load, not missing power or wrong baud.

#### Guardrails For Next Session

- Keep `gradient-hebi` and `gradient-real` stopped until IDs `20`/`30` are cleared.
- Do not issue software restart or torque changes on load-bearing IDs unless the user confirms the arm is physically supported.
- Preferred recovery: physical 12V servo power-cycle with the arm supported, then run read-only status probe before restarting controller/HEBI.

### 2026-05-16 02:16 CDT - Causal video model compute estimates

#### Trigger / Context

- User asked how much rented GPU compute a bare-bones causal video/world model would take, including Prime Intellect or other vendors.

#### Useful Mental Model

- Distinguish three budgets:
  - toy/bare-bones action-conditioned video predictor: low-res, small model, tens to hundreds of GPU-hours.
  - useful robot-domain prototype: 128-256 px latent video, action/proprio conditioning, hundreds to low-thousands of GPU-hours.
  - foundation video model from scratch: tens of thousands of H100-hours or more.
- NVIDIA Cosmos Policy gives a useful fine-tuning anchor: ALOHA-scale robot fine-tuning is listed at 8 H100s for 48 hours, while Open-Sora-scale from-scratch video pretraining is around 35k H100-hours.

#### Guardrails For Next Session

- Recommend fine-tuning/adapting pretrained video backbones before training a foundation video model from scratch.
- For GradientOS, start with 10 Hz, 128-256 px, one or two RGB views, action/proprio conditioning, and video-shard storage instead of raw JPEG frame explosions.

### 2026-05-16 14:17 CDT - B1 translation frame latch

#### Trigger / Context

- User asked whether ARKit starting with a different baseline made calibration obsolete, then asked to implement the fix.

#### Useful Mental Model

- Full axis/sign calibration should be a rare diagnostic, not required on every stack restart.
- B1 must define both translation origin and translation frame. Implementation now transforms ARKit/world position deltas through `reference_pose.orientation.inv()` before scale/invert mapping.
- This makes phone-local forward/left/up stable even when Mobile I/O starts ARKit with a different world heading.
- Orientation behavior is intentionally separate from translation: do not casually reset `phone_to_robot_orientation` on every B1, because the user wants current physical phone orientation to remain the gripper target on re-engage.

#### Guardrails For Next Session

- When starting teleop after this patch, still begin with B1 released, then hold B1 once in a comfortable neutral pose to seed translation origin/frame.
- Do not rerun the calibration wizard unless an axis sign feels wrong; use B1 latch for normal restart/session recentering.
- Current stack is fully down after this task; real hardware remains unsafe for live teleop until IDs `20`/`30` latched position faults are cleared.

### 2026-05-16 14:24 CDT - Real stack startup blocked by silent servo bus

#### Trigger / Context

- User asked to start the real stack with no simulation.

#### Useful Mental Model

- API and web can run without the hardware controller, but API health/pose will return `503` until something answers on controller UDP `3000`.
- Both macOS serial device aliases (`/dev/cu.usbserial-110` and `/dev/tty.usbserial-110`) were silent for all expected Gradient0 servo IDs.
- A probe that reports no faults but returns `None` for position/voltage is not a clean hardware-ready result; prefer the repo scanner and/or direct position reads before starting live motion.

#### Guardrails For Next Session

- Current running sessions after this attempt: `gradient-api` and `gradient-web` only.
- Do not start `gradient-real` or `gradient-hebi` until read-only scanning finds the expected servos again.
- If the user fixes power/wiring, first rerun `scripts/scan_servo_bus.py --port /dev/tty.usbserial-110 --baud 1000000` or the `/dev/cu...` equivalent, then start the real controller only after responses are clean.

### 2026-05-16 14:30 CDT - Power supply on but bus still silent

#### Trigger / Context

- User said the power supply had been off and turned it on, expecting servo discovery to work.

#### Useful Mental Model

- The USB serial adapter itself is present (`USB VID:PID=1A86:7523`, CH340-style adapter) at `/dev/cu.usbserial-110`.
- Both `cu` and `tty` device aliases remain silent for expected Gradient0 IDs, and a full `1..253` sweep at 1 Mbps found no servo responses.
- This narrows the failure below the app/controller layer: likely servo rail voltage not reaching the bus, data wire/connector issue, missing common ground, or adapter direction/wiring.

#### Guardrails For Next Session

- Keep API/web running if useful for UI viewing, but do not claim the real stack is live.
- Re-run the read-only scanner after each physical change; only start `gradient-real` once servos respond.
- Do not use HEBI live mode while servo discovery is `0 / 9`.

### 2026-05-16 14:48 CDT - Real servo bus recovered and controller running

#### Trigger / Context

- User asked to check again with the full sweep or other repo scripts.

#### Useful Mental Model

- The full sweep on `/dev/cu.usbserial-110` found all expected Gradient0 IDs and nothing extra.
- A direct read-only status/register probe showed all servo status registers at `0`, voltage around `12V`, and cool temperatures around `27-29C`.
- Real controller was started with `SERIAL_PORT=/dev/cu.usbserial-110`; this path is known-good on the Mac for the current USB-TTL adapter.
- API health is now good because the controller is answering on UDP `3000`.

#### Guardrails For Next Session

- Current running sessions: `gradient-real`, `gradient-api`, and `gradient-web`.
- HEBI bridge remains stopped; do not start live teleop unless the user is ready and B1 is released.
- If hardware warnings appear again, first action is `POST /control/jog/stop`, then inspect `.codex/run-logs/real-controller.log`.

### 2026-05-16 14:52 CDT - HEBI bridge live on real hardware

#### Trigger / Context

- User asked to start the HEBI bridge after the real controller/API/web stack was healthy.

#### Useful Mental Model

- Bridge command used: `gradient-iphone-hebi-teleop --api-host http://127.0.0.1:4000 --live`.
- Mobile I/O connected as family `HEBI`, name `mobileIO`.
- `/teleop/phone-pose` reports `enabled:false` while B1 is released; live motion begins only when B1 is held.
- The bridge is currently alive but feedback is going stale and triggering auto-reconnect every ~1.5s. This usually means the Mobile I/O app is not foregrounded/publishing fresh ARKit feedback, not that the GradientOS controller failed.

#### Guardrails For Next Session

- Current running sessions: `gradient-real`, `gradient-api`, `gradient-web`, and `gradient-hebi`.
- Treat the setup as physically live.
- If motion is wrong or warnings appear, immediately `POST /control/jog/stop` and stop `gradient-hebi` first.
- Before telling the user to hold B1, check `/teleop/phone-pose.age_s`; it should be fresh, not tens of seconds old.

### 2026-05-16 15:01 CDT - Hardware down, sim up, STOP hardened

#### Trigger / Context

- User reported the web UI STOP button did not stop physical servos and asked to shut down live hardware and run sim.

#### Useful Mental Model

- Live hardware was shut down in this order: API jog stop, stop HEBI, API jog stop again, stop real controller, then direct torque hold current positions.
- `scripts/torque.py on` held arm IDs `10,20,21,30,31,40,50,60`; gripper ID `100` failed to read twice in the direct helper.
- STOP bug root cause is likely realtime jog state: top-bar STOP only hit `/control/stop`, while controller STOP did not forcibly kill jog/deadman/velocity state before braking.
- Controller STOP now clears `is_jogging`, `jog_deadman`, `jog_velocities`, and `jog_gripper_velocity_deg_s`, joins the jog thread, then sends the current-position brake.
- Web STOP now sends deadman false, zero jog velocity, zero gripper jog velocity, jog stop, then emergency STOP.

#### Guardrails For Next Session

- Current running sessions are sim only: `gradient-sim`, `gradient-api`, `gradient-web`.
- No process should own `/dev/cu.usbserial-110` or `/dev/tty.usbserial-110`.
- Before returning to real hardware, verify STOP behavior in sim with HEBI/web jog inputs and then start hardware with B1 released.

### 2026-05-16 15:53 CDT - HEBI bridge live-to-sim

#### Trigger / Context

- User asked to run the HEBI bridge after switching to the simulator.

#### Useful Mental Model

- Bridge is running with `--live`, but the controller behind API is `gradient-sim`, not physical hardware.
- `/teleop/phone-pose.age_s` was near zero after launch, so Mobile I/O feedback is currently fresh.
- B1 is released (`enabled:false`) at launch.

#### Guardrails For Next Session

- Current sessions: `gradient-sim`, `gradient-api`, `gradient-web`, and `gradient-hebi`.
- Physical serial adapter is free; do not describe this as live hardware.
- Use the sim to reproduce STOP and mapping bugs before restarting `gradient-real`.

### 2026-05-16 16:02 CDT - Sim follow freeze was IK rejection

#### Trigger / Context

- User reported that the simulator was no longer following the phone.

#### Useful Mental Model

- HEBI feedback was fresh and the bridge did send jog commands while B1 was held.
- The sim controller received `SET_JOG_DEADMAN,true`, `SET_JOG_VELOCITY`, and `SET_GRIPPER_JOG_VELOCITY`, but the jog loop repeatedly logged `IK solution not found for step`, so pose updates froze.
- Restarted sim to neutral and relaunched HEBI with lower caps: `--max-linear-m-s 0.025 --max-angular-deg-s 12 --translation-scale 0.35 --rotation-scale 0.4`.
- After relaunch, phone pose was fresh briefly, then Mobile I/O feedback went stale again and the bridge resumed reconnecting every ~1.5s.
- Current `/teleop/phone-pose.enabled` is false; current pose sample is stale.

#### Guardrails For Next Session

- If the sim does not move, check B1 first via `/teleop/phone-pose.enabled`.
- Also check `/teleop/phone-pose.age_s`; if stale, the issue is Mobile I/O feedback, not IK.
- If B1 is true and commands appear but pose is frozen, search `.codex/run-logs/sim-controller.log` for `IK solution not found`.
- Longer-term fix should be in jog IK robustness/fallback or orientation command shaping, not in HEBI discovery.

### 2026-05-16 16:24 CDT - Clean sim-only stack

#### Trigger / Context

- User asked to start up the sim.

#### Useful Mental Model

- HEBI was intentionally stopped to make the sim clean and avoid stale phone commands.
- Sim controller was restarted and is back at neutral pose.
- API and web UI were already running and remain active.

#### Guardrails For Next Session

- Current sessions: `gradient-sim`, `gradient-api`, and `gradient-web`.
- No HEBI bridge is running and no process owns the physical serial adapter.
- If user asks for phone control next, start `gradient-hebi` explicitly against this sim stack.

### 2026-05-16 16:31 CDT - User preference: run sim includes HEBI

#### Trigger / Context

- User clarified that when they say "run the sim" they mean start the HEBI bridge too.

#### Useful Mental Model

- Future "run sim" requests should bring up `gradient-sim`, `gradient-api`, `gradient-web`, and `gradient-hebi`.
- Current HEBI sim launch uses reduced caps: `--max-linear-m-s 0.025 --max-angular-deg-s 12 --translation-scale 0.35 --rotation-scale 0.4`.
- Physical serial adapter remains free and this setup commands only the simulator.

#### Guardrails For Next Session

- If the user says "run sim", include HEBI by default unless they explicitly say no bridge.
- Still verify `/teleop/phone-pose.age_s` because Mobile I/O feedback intermittently goes stale/reconnects.

### 2026-05-16 16:42 CDT - HEBI phone axes remapped

#### Trigger / Context

- User observed that physical phone forward moved the Three.js model along robot `+Y` instead of `+X`, and physical roll around forward was displayed as pitch around `Y`.

#### Useful Mental Model

- The B1 ARKit world-frame normalization was working, but the phone-local axes were wrong for the user's held-phone convention.
- Default HEBI bridge axis map is now `y,-x,z`: source phone `Y` becomes robot `X`, source phone `X` becomes robot `-Y`, and source phone `Z` remains robot `Z`.
- The same map is applied to translation deltas and rotation-vector deltas.
- Orientation still uses first-latch phone/robot orientation as the absolute source-of-truth calibration; later B1 presses recenter translation without redefining the absolute phone orientation target.

#### Guardrails For Next Session

- Current sessions: `gradient-sim`, `gradient-api`, and `gradient-web`; HEBI is not running because Mobile I/O was not discoverable.
- When HEBI app is visible again, start bridge normally; the new default axis map should be active without extra flags.
- If lateral movement is backwards, prefer `--invert-y` first; if the physical hold convention changes, use `--phone-axis-map`.

### 2026-05-16 16:48 CDT - Phone triad fixed-heading, sim plus HEBI running

#### Trigger / Context

- User wanted the axis triad on the Three.js phone model to show fixed shared X/Y/Z headings instead of rotating with the phone body, then asked to run the sim with bridge.

#### Useful Mental Model

- The phone body remains orientation-driven by `visual_orientation_*` / `target_orientation_*`.
- The child object named `phone-world-axes` now counter-rotates with the inverse of the phone model quaternion, so its world heading stays fixed while it follows the phone position.
- HEBI bridge is running against sim with reduced caps and default `y,-x,z` axis map.

#### Guardrails For Next Session

- Current sessions: `gradient-sim`, `gradient-api`, `gradient-web`, and `gradient-hebi`.
- Physical serial adapter is free.
- If the user says the triad still rotates, inspect `web-ui/src/ArmVisualizer.tsx` around the `phone-world-axes` inverse-quaternion update.

### 2026-05-16 16:20 CDT - HEBI Mobile I/O pose source

#### Trigger / Context

- User asked whether HEBI Mobile I/O derives the phone position/orientation vectors itself or gets them from ARKit.

#### Useful Mental Model

- HEBI docs say Mobile I/O exposes device 6-DoF pose calculated using ARKit on iOS and ARCore on Android.
- HEBI Python exposes those AR values as `mobile_io.position` and `mobile_io.orientation`; GradientOS only reads them, normalizes quaternion order, and republishes JSON diagnostics.
- HEBI also exposes non-AR sensor feedback such as Core Motion 3-DoF `orientation`, IMU acceleration, gyro, and magnetometer; do not confuse that with AR `arPosition`/`arOrientation`.

#### Guardrails For Next Session

- If pose drifts, jumps, or becomes stale, investigate ARKit tracking quality/camera permission/app foreground state before changing GradientOS mapping code.
- If orientation appears rotated but position is plausible, first test `--quaternion-order wxyz|xyzw`.
- To prove the live source at runtime, add/log HEBI `arQuality` if available, or do a translation-only phone test: AR pose changes `position_m`; Core Motion 3-DoF orientation/IMU-only feedback cannot provide stable world translation.

### 2026-05-16 16:53 CDT - Real stack running, phone body length along X

#### Trigger / Context

- User wanted the simulator torn down, the real servo-backed stack restarted, and the Three.js phone cuboid reoriented because its long side was drawn along `Z` instead of `X`.

#### Useful Mental Model

- `web-ui/src/ArmVisualizer.tsx` now draws the phone body/screen with the long dimension on local `X`; the world-aligned axis triad behavior from the prior change remains separate.
- Real hardware state after startup: servo scan found IDs `10,20,21,30,31,40,50,60,100`; status bytes were all `0`; controller owns `/dev/cu.usbserial-110`.
- Current live sessions after this task are `gradient-real`, `gradient-api`, `gradient-web`, and `gradient-hebi`.
- HEBI bridge is live against real API with reduced caps and `/teleop/phone-pose` fresh, but B1 was not engaged at handoff (`enabled:false`).

#### Guardrails For Next Session

- Do not start `gradient-sim` over this unless the user explicitly asks to switch back to sim.
- B1 now commands real servos; use `/control/jog/stop`, deadman false, and `/control/stop` before any teardown or uncertainty.
- If the phone body still appears wrong, inspect the `createPhonePoseModel()` box dimensions and marker position in `web-ui/src/ArmVisualizer.tsx`.

### 2026-05-16 16:57 CDT - J4/J5 zero calibration prep

#### Trigger / Context

- User needed to reset J4/J5 zero and could not physically move them because servos were still torque-enabled.

#### Useful Mental Model

- Holding torque is not the same as jog being active; STOP intentionally sends a brake/hold command so servos stay stiff while idle.
- J4 is logical joint `4` / servo ID `40`; J5 is logical joint `5` / servo ID `50`; J6 is logical joint `6` / servo ID `60`.
- `scripts/torque.py` now accepts `--ids`, so the safe wrist-only path is `./.venv/bin/python scripts/torque.py off --ids 40,50,60` after stopping `gradient-real`.
- HEBI bridge was stopped; current sessions are `gradient-real`, `gradient-api`, and `gradient-web`.

#### Guardrails For Next Session

- Do not disable torque until the user confirms the wrist is physically supported.
- Stop `gradient-real` before running the torque helper because the controller owns `/dev/cu.usbserial-110`.
- After the user aligns J4/J5/J6, either send controller `SET_ZERO,4`, `SET_ZERO,5`, and `SET_ZERO,6` after restarting the controller, or use a direct serial zero helper if the controller remains stopped; then re-enable torque for `40,50,60`.

### 2026-05-16 17:00 CDT - J4/J5/J6 torque off

#### Trigger / Context

- User said ready after being told to physically support the wrist for J4/J5/J6 alignment.

#### Useful Mental Model

- `gradient-real` was stopped and the lingering controller process was terminated, releasing `/dev/cu.usbserial-110`.
- Ran `./.venv/bin/python scripts/torque.py off --ids 40,50,60 --port /dev/cu.usbserial-110`; output confirmed torque OFF for `40`, `50`, and `60`.
- Current sessions are only `gradient-api` and `gradient-web`; no process owns the serial adapter.

#### Guardrails For Next Session

- The wrist servos are limp. Do not leave the user stuck here; after they align and say ready, burn zero for IDs `40,50,60` using direct serial or a restarted controller, then re-enable torque hold for those same IDs.
- Prefer direct serial zeroing while the controller is stopped to avoid startup motion before calibration.

### 2026-05-16 17:02 CDT - J4/J5/J6 zeros burned

#### Trigger / Context

- User aligned J4/J5/J6 by hand and said ready.

#### Useful Mental Model

- Burned Feetech calibrate-middle zero directly over `/dev/cu.usbserial-110` for IDs `40,50,60` while controller was stopped.
- After zero, raw positions were centered: `40=2048`, `50=2047`, `60=2048`.
- Re-enabled torque hold for `40,50,60`, then restarted `gradient-real`.
- Controller startup reported all servos present and J4/J5/J6 near zero; API `/info/pose` reported wrist joints near `[-0.0008, 0.0069, -0.0008]` degrees.

#### Guardrails For Next Session

- Current sessions are `gradient-real`, `gradient-api`, and `gradient-web`; HEBI remains stopped.
- If the user wants to resume phone teleop, start `gradient-hebi` explicitly after confirming they are ready for real hardware motion.
- The real controller owns `/dev/cu.usbserial-110`; stop it before any further direct serial calibration.

### 2026-05-16 17:06 CDT - HEBI bridge restarted after wrist zero

#### Trigger / Context

- User asked to start the bridge after confirming the meaning of "near zero" readback.

#### Useful Mental Model

- Cleared jog state first, then started `gradient-hebi` live against the real API with reduced caps.
- HEBI Mobile I/O connected and `/teleop/phone-pose` was fresh with `enabled:false`.
- Current sessions are `gradient-real`, `gradient-api`, `gradient-web`, and `gradient-hebi`.

#### Guardrails For Next Session

- B1 now commands real hardware again.
- If the user reports unexpected motion, stop `gradient-hebi` and send jog stop/STOP through the API before debugging.

### 2026-05-16 17:14 CDT - J5 inversion removed

#### Trigger / Context

- User reported physical J5 appeared to turn opposite of the Three.js model.

#### Useful Mental Model

- Stopped `gradient-hebi`, cleared jog, and STOPped the controller before making the sign change.
- The web visualizer applies joint telemetry directly with no per-joint sign flip; J5 sign was coming from servo ID `50` being included in `Gradient0Config.inverted_actuator_ids`.
- Removed `50` from the inverted set; remaining inverted IDs are `{10, 20, 30, 40, 60, 100}`.
- Restarted `gradient-real`; J5 raw hardware limits changed to `[853, 3413]`, confirming the new non-inverted mapping loaded.
- Current sessions are `gradient-real`, `gradient-api`, and `gradient-web`; HEBI remains stopped.

#### Guardrails For Next Session

- If user wants to test phone control, restart `gradient-hebi` explicitly and remind them B1 commands real hardware.
- If J5 still disagrees visually, inspect `joint5` axis `xyz="0 1 0"` in both `mini-6dof-arm/mini-6dof-arm.urdf` and `web-ui/public/assets/mini-6dof-arm/mini-6dof-arm.urdf`; do not stack another servo inversion without proving whether feedback or URDF is wrong.

### 2026-05-16 17:18 CDT - J5 positive step test

#### Trigger / Context

- User said "ok lets test it" after J5 inversion was removed.

#### Useful Mental Model

- First test was contaminated by lingering live jog packets; stopped them with `pkill -f gradient-iphone-hebi-teleop`, API jog stop, and API STOP.
- Clean test commanded only J5 `+3 deg`, from `1.0994 rad` to `1.1518 rad`.
- Controller readback moved J5 positive to `1.1331 rad` / `64.92 deg`, so the controller feedback side now agrees with the requested positive direction.
- User still needs to visually say whether physical J5 and the Three.js model moved the same way.

#### Guardrails For Next Session

- HEBI is stopped. Do not restart it automatically unless the user asks.
- If user says J5 still looks backwards, investigate URDF/visualizer joint axis next; if user says it matches, the servo inversion change is likely correct.

### 2026-05-16 17:20 CDT - Full real stack restarted

#### Trigger / Context

- User asked to start the full stack after the J5 sign test.

#### Useful Mental Model

- Real controller, API, and web were already running.
- Cleared jog state, then started `gradient-hebi` live against the real API with reduced caps.
- HEBI Mobile I/O connected; `/teleop/phone-pose` was fresh and reported `enabled:true`, so B1 was held and the bridge was actively sending real jog commands.
- Current sessions are `gradient-real`, `gradient-api`, `gradient-web`, and `gradient-hebi`.

### 2026-05-21 21:14 CDT - HEBI bridge live on real hardware

#### Trigger / Context

- User asked to start the HEBI bridge after confirming it was off.

#### Useful Mental Model

- Bridge session `13998` is running in this thread.
- It discovered `HEBI/mobileIO` at `192.168.1.221` and connected.
- `/teleop/phone-pose` was fresh with `enabled:true`, meaning B1 was held and physical robot commands were flowing at validation time.
- Diagnostic logging was not enabled for this normal bridge start.

#### Guardrails For Next Session

- This is live real hardware. If anything feels wrong, interrupt bridge session `13998` first, then send API jog stop/deadman false if needed.
- Patched deadman release/brake code is loaded in the running real controller/API.

### 2026-05-21 20:47 CDT - Phone jog safety fix loaded

#### Trigger / Context

- User reported that physical servos kept moving after B1 release and that small phone movements could make the wrist do full rotations.

#### Useful Mental Model

- The live bridge was stopped first, then API zero/deadman/stop calls were sent.
- Old bridge logs showed B1 release was detected, but release sent zero velocity before deadman false. Controller-side `SET_JOG_DEADMAN,false` only zeroed rates; it did not brake a previously commanded servo target.
- Fix now has two layers:
  - Bridge release sends deadman false first, then zero velocity, then jog stop, best-effort.
  - Controller deadman false force-stops jog and brakes to current physical position immediately.
- Wrist full-rotation risk came from applying IK `q_target` directly. Jog now wraps IK targets to the nearest equivalent angle relative to current jog state, clamps to joint limits, and rejects any per-cycle joint jump over `0.35 rad`.
- Optional jog diagnostics are separate JSONL files under `diagnostics/jog_motion/`, enabled via `/control/jog/debug`. Logging is off by default; when enabled it writes buffered IK/command/q-delta data and only samples actual servo readback every 5 applied jog steps.
- Optional HEBI bridge diagnostics can be enabled with `--diagnostic-log`; those write low-rate phone pose, target pose, visual pose, and command payloads under `diagnostics/jog_motion/` for timestamp correlation with controller logs.

#### Guardrails For Next Session

- Patched real controller/API are running: real controller session `31509`, API `78083`, web `47957`.
- HEBI bridge is stopped intentionally. Starting it will re-enable live phone control against physical hardware.
- Before reproducing wrist issues, enable debug:
  `curl -sS -X POST http://127.0.0.1:4000/control/jog/debug -H 'Content-Type: application/json' -d '{"enabled":true}'`
- After reproduction, disable debug to close/flush:
  `curl -sS -X POST http://127.0.0.1:4000/control/jog/debug -H 'Content-Type: application/json' -d '{"enabled":false}'`
- If starting bridge specifically for a diagnostic repro, add `--diagnostic-log --diagnostic-log-interval-s 0.1` to the bridge command.

### 2026-05-21 20:29 CDT - Real hardware stack active

#### Trigger / Context

- User asked to start the stack after servo bus recovery.

#### Useful Mental Model

- Real controller is running with `SERIAL_PORT=/dev/cu.usbserial-110`.
- All configured servos are present: `10,20,21,30,31,40,50,60,100`.
- API is live at `http://localhost:4000`; `/health` is OK and `/info/pose` returns live robot pose.
- Web UI is at `http://localhost:8000/`, network URL `http://192.168.1.203:8000/`.
- HEBI bridge retry loop is running but has not discovered `HEBI/mobileIO` yet; `/teleop/phone-pose` is `status:none`.

#### Guardrails For Next Session

- Current visible Codex sessions: real controller `97457`, API `8457`, web `47957`, HEBI bridge `64776`.
- Bridge is live against real hardware. Once it connects, B1 commands physical robot motion.
- If anything unexpected happens, interrupt bridge first, then send jog stop/STOP through API if available, then stop controller.

### 2026-05-21 19:50 CDT - Servo bus recovered

#### Trigger / Context

- User asked to check again for servos and mentioned a sweep script.

#### Useful Mental Model

- `scripts/scan_servo_bus.py` is the read-only sweep tool; use `--full-sweep` to scan IDs `1..253`.
- `/dev/cu.usbserial-110` now responds correctly.
- Expected Gradient0 IDs found: `10,20,21,30,31,40,50,60,100`.
- Full sweep found no extra IDs, and factory-default IDs `1,2,3` were silent.

#### Guardrails For Next Session

- Real controller startup can proceed with `SERIAL_PORT=/dev/cu.usbserial-110 ./run.sh`.
- If starting the bridge after real controller/API startup, remember `--live` will command physical hardware, not sim.

### 2026-05-21 19:47 CDT - Real stack blocked by silent servo bus

#### Trigger / Context

- User asked to restart the full stack using the real robot in the loop.

#### Useful Mental Model

- Initial `./run.sh` failed because the configured `/dev/ttyUSB0` does not exist on this Mac and auto-detect did not find responsive servos.
- The USB serial adapter is present as `/dev/cu.usbserial-110` and `/dev/tty.usbserial-110`.
- Read-only scans on both aliases found `0 / 9` expected Gradient0 servo IDs.
- No API, web, or HEBI bridge was started because a real-backed stack would not be safe/useful while the servo bus is silent.

#### Guardrails For Next Session

- Before starting real hardware, rerun `./.venv/bin/python scripts/scan_servo_bus.py --port /dev/cu.usbserial-110 --baud 1000000`.
- Expected IDs are `10,20,21,30,31,40,50,60,100`; do not start the real controller/bridge until those respond or the user explicitly wants deeper diagnostics.
- Likely physical checks: robot servo power, USB-TTL adapter seating, TX/RX/direction, and common ground.

### 2026-05-21 15:11 CDT - Sim stack restarted after shutdown

#### Trigger / Context

- User asked to restart the whole stack for sim after a shutdown turn was interrupted.

#### Useful Mental Model

- Ports were clear before startup.
- Fresh visible Codex sessions now own the stack: sim `21769`, API `94340`, web `49449`, HEBI bridge retry `74663`.
- API `/health` is good and points to sim controller at `127.0.0.1:3000`.
- Web UI is at `http://localhost:8000/`, network URL `http://172.20.10.3:8000/`.
- Bridge retry loop is running, but it has not rediscovered `HEBI/mobileIO` yet; `/teleop/phone-pose` is `status:none` because the API process restarted.

#### Guardrails For Next Session

- Use `write_stdin` on session `74663` to watch bridge discovery status in this thread.
- User likely needs HEBI Mobile I/O foregrounded on the phone/hotspot again for discovery.
- Bridge uses `--live` against the sim-backed API, so once it connects B1 commands the simulator.

### 2026-05-21 15:08 CDT - Fresh visible sim stack

#### Trigger / Context

- User could not see detached sessions and asked to shut them down and restart.

#### Useful Mental Model

- Detached `screen` sessions were removed, but child processes survived until explicitly killed.
- Fresh Codex-managed sessions now own the stack: sim `71138`, API `61017`, web `60318`, bridge `28126`.
- Hotspot discovery is working: bridge found `HEBI/mobileIO` at `172.20.10.1`.
- Phone pose is fresh and live; `/teleop/phone-pose` showed `age_s` around `0.005` and `enabled:true`.
- Web UI is at `http://localhost:8000/` and network URL `http://172.20.10.3:8000/`.

#### Guardrails For Next Session

- These are visible tool sessions, not detached screen sessions. Use `write_stdin` on session IDs above if continuing in this same thread.
- Bridge is `--live` but pointed at sim-backed API, so B1 commands the simulator.
- If the user asks to stop, interrupt bridge first, then API/web/sim as needed.

### 2026-05-21 15:05 CDT - Hotspot discovery test status

#### Trigger / Context

- User asked to start the stack again after connecting laptop to personal hotspot.

#### Useful Mental Model

- Stack was already active in detached `screen` sessions: `gradient-sim`, `gradient-api`, `gradient-web`, and `gradient-hebi`.
- API health is good and points to sim controller on `127.0.0.1:3000`.
- Web UI is on `http://localhost:8000/`.
- HEBI discovery is now finding `family='HEBI' name='mobileIO'`, but feedback goes stale after about `1.5s`, causing repeated reconnect scans.

#### Guardrails For Next Session

- Do not start duplicate processes before checking `screen -ls`, ports `3000/4000/8000`, and `.codex/run-logs/hebi-bridge.log`.
- If phone pose is not live, compare `/teleop/phone-pose age_s`; current issue is stale feedback despite successful discovery.
- Next likely debugging step is iPhone-side: keep HEBI Mobile I/O foregrounded, camera/ARKit permission allowed, and confirm the app is actively streaming rather than merely discoverable.

### 2026-05-21 14:33 CDT - Sim stack with bridge retrying

#### Trigger / Context

- User asked to start the full sim stack with bridge.

#### Useful Mental Model

- `./run-sim.sh` started cleanly and owns UDP `3000`.
- API was already running on TCP `4000`; launching another API failed with address-in-use, but the existing `/health` endpoint reports it can reach the sim controller at `127.0.0.1:3000`.
- `./run-web.sh` started Vite on `http://localhost:8001/` because `8000` was already occupied.
- `gradient-iphone-hebi-teleop` is installed and can launch, but direct discovery found no HEBI Mobile I/O devices.
- A retrying bridge wrapper is running with conservative sim teleop limits: `--live --translation-scale 1.0 --max-linear-m-s 0.025 --max-angular-deg-s 12 --rotation-scale 0.4 --setup-mobile-ui --list-devices`.

#### Guardrails For Next Session

- Current Codex sessions are `94950` for sim, `97599` for web, and `60537` for the retrying HEBI bridge.
- Bridge is not connected until the iPhone app is visible as `family='HEBI' name='mobileIO'` on the same LAN.
- `/teleop/phone-pose` may return a stale old sample; check `age_s` before assuming phone visualization is live.

#### Guardrails For Next Session

- B1 currently commands real hardware. If user reports anything unexpected, stop `gradient-hebi`, send API jog stop, and send API STOP before debugging.

### 2026-05-16 18:52 CDT - Phone teleop scale, IK telemetry, and hold-still sway

#### Trigger / Context

- User reported that phone translation appeared scaled down in Three.js, IK failed often without enough UI visibility, and the robot swayed back/forth while held still.

#### Useful Mental Model

- The visible phone scale issue had two causes: bridge default `translation_scale` was `0.5`, and the last live launch used `--translation-scale 0.35`. The code default is now `1.0`, and live launches should pass `--translation-scale 1.0` unless the user explicitly asks for gain scaling.
- The bridge now applies small linear/angular target deadbands before creating velocity commands. This keeps ARKit/HEBI hold jitter from leaking into realtime jog as tiny nonzero commands.
- The controller now publishes `jog_ik` telemetry on the monitor stream. Web UI shows a Jog IK status card and colors the phone cuboid green for solved, amber for holding/timed out, and rose for IK/FK/apply failure.
- The realtime jog controller now separates arm motion from gripper motion. Zero arm velocity skips IK and arm `set_servo_positions`; gripper-only jog does not re-command the arm. This is the main mitigation for hold-position sway.
- Jog start/stop/STOP clear `weld_active` and `current_weld_type`; no weld path logic should remain active during phone teleop.

#### Guardrails For Next Session

- Current sessions are `gradient-real`, `gradient-api`, and `gradient-web`; `gradient-hebi` is not running because Mobile I/O was not discoverable on restart.
- Before restarting the bridge for real hardware, make sure the HEBI Mobile I/O app is open and discoverable, then use explicit `--translation-scale 1.0`.
- If the user still sees sway while B1 is held motionless, inspect the new Jog IK card first: `holding` means no arm command is being sent, while `ok` with tiny command rates means jitter is still escaping through the bridge.

### 2026-05-16 20:50 CDT - HEBI bridge live again

#### Trigger / Context

- User asked why skipping zero-delta IK would reduce sway, then asked to start the HEBI bridge.

#### Useful Mental Model

- Explanation given: repeated IK for a nominally identical target can still produce tiny changing joint targets because the seed/readback/noisy target changes slightly; sending those tiny servo setpoints while holding still can make the arm hunt. The new hold path avoids creating arm commands at all when arm velocity is zero.
- Cleared jog/STOP first, then started `gradient-hebi` with a retry wrapper.
- The first direct discovery found no Mobile I/O, but the retrying bridge later connected and is live.
- `/teleop/phone-pose` is fresh and currently `enabled:false`.

#### Guardrails For Next Session

- B1 now commands real hardware through `gradient-hebi`.
- Running sessions are `gradient-real`, `gradient-api`, `gradient-web`, and `gradient-hebi`.
- If the user wants to stop real phone control, stop `gradient-hebi` and send API jog stop/STOP.

### 2026-05-16 23:10 CDT - Gripper zero paused, B2/B4 implemented

#### Trigger / Context

- User wanted the phone cuboid width moved to Y, the gripper zeroed before switching to sim, and B2/B4 mapped to gripper open/close.

#### Useful Mental Model

- Gripper logical zero is intended to mean closed; `Gradient0Config.gripper_limits_rad` documents `0` closed to `pi` open.
- Servo `100` uses the same Feetech center-zero model: the calibrate-middle command makes the current physical pose raw center/zero. Therefore the user should physically close the gripper before zeroing servo `100`.
- HEBI bridge now maps B2 to `+max_gripper_deg_s` and B4 to `-max_gripper_deg_s`; A3 still works when neither B2 nor B4 is held.
- Three.js phone model dimensions are now local X length, local Y width, local Z thickness.

#### Guardrails For Next Session

- Gripper servo `100` torque is currently OFF and the real controller is stopped. Do not start real/sim stacks until zeroing is completed or the user explicitly abandons it.
- Current sessions are only `gradient-api` and `gradient-web`.
- Next step when user says `ready`: burn servo `100` calibrate-middle at the physically closed pose, re-enable torque hold on `100`, restart the real controller briefly to verify `/info/gripper` reads near `0 deg`, then shut real down and bring up sim + API/web + HEBI bridge as requested.

### 2026-05-16 23:13 CDT - Gripper zero complete, sim stack active

#### Trigger / Context

- User said `ready` after physically closing the gripper for zeroing.

#### Useful Mental Model

- Servo `100` was calibrated at the closed pose: raw readback moved from `3628` before zero to `2047` after zero.
- Re-enabled torque hold on `100`, then restarted the real controller once to reapply limits; `/info/gripper` reported `0.04 deg` at raw `2047`.
- Real hardware was then shut down and the simulator started.
- `gradient-hebi` is running as a retry wrapper against the sim-backed API. Mobile I/O discovery dropped, so the wrapper is currently retrying; it will command sim when it reconnects.

#### Guardrails For Next Session

- Current sessions: `gradient-sim`, `gradient-api`, `gradient-web`, `gradient-hebi`.
- Real controller is stopped and the hardware serial port is free.
- B2/B4 gripper mapping and phone cuboid dimension changes are already implemented and validated.

### 2026-05-21 20:44 CDT - Controller tick and IK mental model

#### Trigger / Context

- User asked what a controller tick is, why the jog loop is 25 Hz, whether that is a UART limit, and whether the IK solver is custom or imported.

#### Useful Mental Model

- In this repo, the realtime jog controller runs an application-level 25 Hz loop (`JOG_CONTROL_FREQUENCY_HZ`), reads the latest Cartesian velocity command, integrates it over `dt`, solves IK for that one small next pose, and sends a sync-write joint command.
- 25 Hz is a conservative control cadence chosen above the servo transport layer; UART/SyncWrite/SyncRead bandwidth and Python/network jitter influence the practical limit, but UART does not inherently mean 25 Hz.
- The default IK backend is IKFast: auto-generated analytic C++ from OpenRAVE, wrapped by local pybind/C++ and a Python facade. It is custom-generated for this arm, but not hand-written BFS/search code.

#### Guardrails For Next Session

- When explaining IK failures, distinguish the three layers: phone target -> Cartesian velocity -> one-step IK pose. Avoid saying the controller plans a full path to the phone target; it repeatedly solves small local steps.

### 2026-05-21 21:24 CDT - Real pose/model mismatch traced to missing shoulder feedback

#### Trigger / Context

- User reported a major difference between the real robot pose and the Three.js model, suspecting the servos may be taking too much weight.

#### Useful Mental Model

- `/monitor` joints and `/info/pose` are based on live servo readback, not just commanded setpoints.
- The UI parses `/monitor` `joints` and applies them directly to URDF `joint1..joint6`.
- If both physical servos for a logical joint fail to respond, the current Feetech conversion can leave that logical joint at `0.0`; for Gradient0 this is especially dangerous for J2 because it is driven by IDs `20` and `21`.
- During this investigation, IDs `20` and `21` repeatedly failed SyncRead and disappeared from extended telemetry, while the reported logical J2 stayed at `0.0`.

#### Guardrails For Next Session

- Treat any model-vs-real mismatch with missing servo feedback as a hardware/readback safety issue before blaming Three.js.
- Do not restart the HEBI bridge on real hardware while IDs `20`/`21` are timing out.
- If the user wants a bus scan, stop the controller first because it owns `/dev/cu.usbserial-110`; use `scripts/scan_servo_bus.py` as the read-only check.
- Be careful interpreting `unloading_condition` and `led_alarm_condition`; they appear to be condition/config masks, while active status is the `status_byte`.

### 2026-05-21 21:35 CDT - Overload status packets must still feed position readback

#### Trigger / Context

- User asked to run the read-only bus scan after the real robot/Three.js pose mismatch investigation.

#### Useful Mental Model

- IDs `20` and `21` ping and answer individual READ, so they are not absent or mis-ID'd.
- Their SyncRead status packets contain valid position bytes plus status byte `0x20`.
- The prior parser alerted on the status byte and then discarded the valid packet, so J2 fell back to `0.0` even though the raw positions were available.
- After parsing valid status-error packets, J2 reports about `35.96 deg`, matching the physical pose much better.
- Feetech status byte `0x20` is `Overload`; alarm/condition bit names are a different register namespace and should not be used for `status_names`.

#### Guardrails For Next Session

- For Feetech status packets, validate checksum first, then parse returned data even if the error byte is nonzero; keep the alert/status visible.
- If `/monitor` shows `status_names: ["Overload"]` and high current on shoulder IDs `20/21`, treat this as a physical load/mechanics problem and keep the HEBI bridge off.
- If API `/monitor` goes quiet after stopping/restarting the controller, restart the API so it reopens its telemetry subscription.

### 2026-05-21 21:40 CDT - SyncRead explanation framing

#### Trigger / Context

- User asked whether SyncRead packets are just data sent over serial UART and what overload means.

#### Useful Mental Model

- UART is the byte transport; Feetech SyncRead is a higher-level protocol frame carried over that UART.
- A SyncRead request is one broadcast packet asking specific servo IDs to return a register range; each servo replies with its own status packet.
- `Overload` is the servo's `0x20` response status bit, not a network/protocol overload. In the current robot state it means shoulder servos `20/21` are reporting excessive load while holding position.

#### Guardrails For Next Session

- When explaining bus faults, separate physical/electrical transport, packet protocol, parsed register data, and mechanical servo state.

### 2026-05-21 23:07 CDT - Overload does not block outgoing SyncWrite

#### Trigger / Context

- User asked whether overload prevents sending joint angles and what servo stall means.

#### Useful Mental Model

- In the current code, overload status is read-side information. `prepare_sync_write_commands` still generates commands for present servos, and `sync_write` still sends the broadcast write packet.
- The servo firmware may still reject, limit, fail to reach, or thermally/protectively unload under severe overload, but our host code does not stop writes solely because `0x20` was reported.
- Stalled means the servo is commanded to move or hold, but the output cannot move/reach the target because of load, binding, collision, or paired-servo fighting; current and heat rise while position error remains.

#### Guardrails For Next Session

- Explain overload as "can command, cannot trust motion/holding under load" rather than "communication is blocked."

### 2026-05-22 19:48 CDT - Baud rate explanation framing

#### Trigger / Context

- User asked what baud rate is and how it affects packets per time range.

#### Useful Mental Model

- Baud is the serial signaling speed; for typical 8N1 UART, effective payload bytes per second are roughly `baud / 10`.
- Packet throughput is bytes-per-second divided by total request/response bytes, then reduced by turnaround, servo processing, USB adapter latency, parsing, and timeouts.
- For the Feetech 1 Mbps bus, an 8-servo position SyncRead is roughly 16 request bytes plus 64 response bytes, about 80 bytes or 800 serial bits before overhead.

#### Guardrails For Next Session

- Separate ideal wire-time estimates from real controller-loop frequency; do not imply 1 Mbps means 1 million packets per second.

### 2026-05-22 19:52 CDT - UART 8N1 naming nuance

#### Trigger / Context

- User asked why `8N1` has only one non-data digit even though UART frames include start and stop bits.

#### Useful Mental Model

- `8N1` names configurable framing parameters: 8 data bits, no parity, 1 stop bit.
- The start bit is implicit in ordinary UART framing and is not included in the shorthand.

#### Guardrails For Next Session

- When estimating UART wire time, still count the implicit start bit: `8N1` is usually 10 wire bits per byte.

### 2026-05-27 20:32 CDT - UART parity bit explanation

#### Trigger / Context

- User asked what a parity bit is.

#### Useful Mental Model

- A parity bit is an optional UART error-detection bit that makes the number of `1` bits in the data plus parity bit even or odd.
- It can detect many simple bit flips but cannot identify or correct the bad bit, and it misses some multi-bit errors.

#### Guardrails For Next Session

- Explain `N` in `8N1` as no parity bit; parity variants such as `8E1`/`8O1` add one extra wire bit per byte.

### 2026-05-27 20:56 CDT - URDF frames and servo CAD explanation

#### Trigger / Context

- User asked whether the servo/servo-attachment model visible in Three.js is publicly available, whether iPhone Gaussian splatting could trivially recreate it, and how URDF mass/inertia, joint limits, and joint origins work.

#### Useful Mental Model

- The active GradientOS robot config uses Feetech STS3215 servos.
- The active web URDF references only per-link STL files (`base`, `L1`-`L5`, `wrist`); servo geometry seen in Three.js is baked into those link meshes, not separately referenced as a servo asset.
- Waveshare publishes an ST3215 Servo STEP module; public STEP is the right source for CAD-grade servo geometry.
- Phone Gaussian splats/photogrammetry are visual/reconstruction assets, not reliable mechanical CAD for URDF pivots, screw holes, mesh scale, or watertight collision.

#### Guardrails For Next Session

- Explain URDF origins as transforms between explicitly chosen link/joint frames; derive them from CAD assembly frames or measured joint axes, not 6-decimal visual eyeballing.
- Separate `visual` mesh origins, joint origins, and inertial COM origins whenever explaining URDF.

### 2026-05-27 21:19 CDT - URDF role in phone-to-IK control loop

#### Trigger / Context

- User asked whether they are right that the model is read-only and URDF should not affect dynamics because the phone dictates position to IK, which sends joint positions to servos.

#### Useful Mental Model

- Mostly correct for dynamics: the current phone/jog path does not run a physics dynamics simulation from URDF mass/inertia.
- Still important for kinematics/safety:
  - The default IKFast backend uses compiled geometry originally generated from a robot model.
  - `END_EFFECTOR_OFFSET` defines the controlled TCP offset from the wrist.
  - `utils.URDF_JOINT_LIMITS` feeds joint-limit clamps and Feetech servo EEPROM limit writes.
  - The web URDF is read by Three.js for visualization only, but if its frames diverge from the solver/real robot it can mislead debugging.

#### Guardrails For Next Session

- Say: visual meshes can be approximate; kinematic frames/TCP/joint axes/limits cannot be arbitrary if the robot should move to the phone-commanded pose accurately.
- Avoid implying inertial tags are active in the current runtime loop unless a physics simulator or dynamics controller is introduced.

### 2026-05-27 21:28 CDT - IK geometry and limit sources

#### Trigger / Context

- User asked whether joint limits or link measurements exist outside the URDF and how the IK solver knows robot dimensions.

#### Useful Mental Model

- Joint limits exist outside the URDF in `Gradient0Config.logical_joint_limits_rad` and `actuator_limits_rad`; robot config copies them into `LOGICAL_JOINT_LIMITS_RAD` and `URDF_JOINT_LIMITS`.
- Default `MINI_ARM_SOLVER=ikfast` does not read URDF at runtime; it calls compiled generated C++ through `ikfast_pybind`.
- The generated IKFast C++ has hard-coded dimensions, e.g. `0.19715`, `0.231706`, `0.0773`, `0.0455`, produced when the solver was generated.
- Numeric solver path reads `mini-6dof-arm/dh_params.csv`, which was generated from the URDF but is now its own runtime data source.

#### Guardrails For Next Session

- When discussing URDF edits, say clearly whether the edit affects only Three.js visuals, hardware limits, numeric IK, or default IKFast.
- Do not say "edit the URDF and IK changes" for the default backend unless the IKFast solver is regenerated/rebuilt.

### 2026-05-27 21:36 CDT - IKFast versus numeric backend framing

#### Trigger / Context

- User asked whether IKFast was invented by the repo creator and what "numeric solver path" means.

#### Useful Mental Model

- IKFast is an upstream OpenRAVE analytic IK generator/compiler, not custom-invented for this repo.
- The custom repo-specific part is the generated C++ solver for this robot geometry plus the pybind/Python wrapper.
- `MINI_ARM_SOLVER` selects the backend at import time:
  - `ikfast`: default generated analytic C++ wrapper.
  - `numeric`: alternate QuIK/pyquik backend using `mini-6dof-arm/dh_params.csv`.
  - `trac`: placeholder.
- Numeric IK is iterative/seeded and can adapt to changed DH data more easily, but it is generally slower/less deterministic than generated analytic IK.

#### Guardrails For Next Session

- Mention that `solve_ik_path_batch` still directly calls `IK_SOLVER.solve_ik_path` after applying `END_EFFECTOR_OFFSET`, so the batch/planning path may be more IKFast-shaped than the single-pose wrapper.

### 2026-05-27 20:58 CDT - Real stack startup with bridge discovery failure

#### Trigger / Context

- User asked to start the full stack with the real robot in the loop.

#### Useful Mental Model

- The real controller can be started with `./run.sh --serial-port /dev/cu.usbserial-110`; on this run it found all expected servos.
- API is `./run-api.sh` on port `4000`; web UI is `./run-web.sh` on `http://localhost:8000`.
- HEBI live bridge command is `./.venv/bin/gradient-iphone-hebi-teleop --api-host http://127.0.0.1:4000 --live`.
- On this run, the first one-shot attempts failed to discover `family='HEBI' name='mobileIO'`, then a visible retry loop with conservative limits connected successfully.
- After a failed bridge attempt, explicitly send the safety sequence through the API: deadman false, zero jog velocity, zero gripper velocity, and `JOG_STOP`.
- After the bridge connected, user held B1 briefly. The controller sampled `556` successes and `45` failures, then returned to `deadman:false` / stopped; sampled servo status bytes were clear.
- A later B1 run pushed failures to `554` and servo `50` reported `Overload`; stop live bridge immediately if this recurs.

#### Guardrails For Next Session

- Do not report the bridge as running unless the HEBI command stays alive and `/teleop/phone-pose` shows a live sample. For this startup, the bridge was briefly live in session `85072`, then was terminated for safety after servo `50` overload.
- Before letting the user hold B1, mention that the current startup pose readback was folded (`J2` near `-96 deg`, `J3` near `88 deg`) even though shoulder status bytes were clear during this run.
- If investigating future motion oddities from this run, check why the post-jog posture reached about `J5 = 100 deg`, why failures reached `554`, and why servo `50` hit overload under live phone jogging.

### 2026-05-27 21:20 CDT - HEBI bridge restarted with lower caps

#### Trigger / Context

- User asked to start the bridge again after the previous live run was stopped for servo `50` overload.

#### Useful Mental Model

- The real controller/API/web were already running.
- The bridge was restarted with reduced limits: `--max-linear-m-s 0.012 --max-angular-deg-s 6 --rotation-scale 0.25`.
- It connected to `HEBI/mobileIO`; `/teleop/phone-pose` was fresh with `enabled:false`.

#### Guardrails For Next Session

- Current bridge session is `4209`, wrapper PID `31011`, Python bridge PID `31021`.
- If B1 is used again, watch servo `50` first; stop the bridge immediately if `status_names` includes `Overload` or the IK failure count climbs sharply.

### 2026-05-27 21:28 CDT - Model snapped home after serial readback failure

#### Trigger / Context

- User reported the Three.js model reset to home while the real robot stayed put and they had not pressed Home.

#### Useful Mental Model

- This was not a Home command. The old real controller lost its macOS USB serial device handle and logged repeated `Errno 6 Device not configured` errors from Feetech SyncRead/SyncWrite.
- During that failure, position readback collapsed to an empty raw position map. The backend conversion path previously initialized missing logical joints to zero, so `GET_JOINT_ANGLES`, `/info/joints`, `/monitor`, and the Three.js model saw a fake all-zero pose.
- A read-only bus scan after stopping the stale controller found all expected servos on `/dev/cu.usbserial-110`, so the servo bus itself was present again; the controller process needed a restart to reopen the recreated serial device.
- After restarting controller/API, live readback returned to the physical non-home pose near `[-78.99, 13.93, 22.55, 81.10, 70.81, -111.87]` degrees.

#### Guardrails For Next Session

- HEBI bridge is off after this investigation; do not assume the previous bridge session is still live.
- If Three.js jumps to home again, immediately compare `/info/joints`, `/monitor`, and controller logs for SyncRead empty/failure lines before blaming the UI.
- Empty or partial servo feedback should preserve the last known joint values after this patch. If fake zeros reappear, inspect both `src/gradient_os/arm_controller/backends/feetech/driver.py` and legacy `src/gradient_os/arm_controller/servo_driver.py`.
- Restart API after restarting the controller if `/monitor` does not resume, because existing SSE subscriber state can prevent a fresh `START_TELEMETRY` request from being sent.

### 2026-05-27 21:39 CDT - USB serial handle vs SyncRead timeout distinction

#### Trigger / Context

- User asked whether "lost USB serial handle" just means SyncReads were failing.

#### Useful Mental Model

- The controller stores an open pyserial object in `FeetechBackend._ser`; that object wraps an OS file descriptor for the USB serial tty.
- Ordinary SyncRead failure can mean bytes were sent but one or more servos timed out, returned bad checksums, or only partially replied.
- `Errno 6 Device not configured` is lower-level: macOS invalidated the tty device under the process, usually because the USB serial adapter detached/reset/re-enumerated or the cable/hub/power path glitched.
- Once this happens, the old file descriptor does not automatically reconnect even if `/dev/cu.usbserial-110` appears again. Restarting the controller works because it opens a fresh `serial.Serial` handle.

#### Guardrails For Next Session

- Treat repeated `Device not configured` on both SyncRead and SyncWrite as an OS/device handle problem first, not just servo protocol packet loss.
- Good next code hardening: detect serial exceptions containing `Errno 6`, close/re-resolve/reopen the serial port, ping expected servos, and resume telemetry only after a successful read.

### 2026-05-27 22:14 CDT - Stack shutdown

#### Trigger / Context

- User asked to shut down the stack.

#### Useful Mental Model

- API stop calls to `:4000` failed because the API was already unreachable.
- Previous controller/API/web terminal sessions were already gone by the time shutdown was requested.
- Process and listener checks found no active GradientOS controller, API, HEBI bridge, or web server and no listeners on `4000` or `8000`.

#### Guardrails For Next Session

- Treat the stack as down. Restart explicitly before expecting `/info/joints`, `/monitor`, or web UI access.

### 2026-06-02 18:12 CDT - Fork migration blocked on GitHub auth

#### Trigger / Context

- User asked to fork the repo so local changes can be pushed to a personal remote without creating an OSS PR.

#### Useful Mental Model

- Current branch is `fix/program-tree-modal-dismissable`.
- Current `origin` is `https://github.com/terrorproforma/GradientOS.git`.
- `gh` is installed, but `gh auth status` reports no authenticated GitHub host.
- The likely personal fork URL `https://github.com/dylanembry/GradientOS.git` was not found or accessible before auth.
- A safety snapshot preserving the current state was created outside the repo at `/Users/dylanembry/Projects/GradientOS-local-snapshots/20260602-181212`.
- The snapshot contains the committed HEAD bundle, tracked working-tree diff, Git status/remotes metadata, and a tarball of untracked files.

#### Guardrails For Next Session

- Do not assume a fork exists until `gh auth status` succeeds and `gh repo view dylanembry/GradientOS` or the authenticated account's fork URL resolves.
- Before staging for a remote WIP commit, review untracked `.claude/settings.local.json` and `logs/*.pid`; these are preserved locally but may be private/runtime-only.
- Preferred remote layout after auth: `upstream` = `terrorproforma/GradientOS`, `origin` = personal fork, then push the chosen branch to `origin`.
