# Mechanical and mounting relationships: backward-compatible model plan

2026-09-12. Read-only preparation; no implementation authorization or production changes. Scope: distinguish mechanical shaft associations and physical surface mounting from process-fluid and instrument-signal connections. No fluid, electrical, structural, torque, thermal, or sensor-performance calculations.

## Current constraints verified in source

- `document.schema.json` permits only `process` and `signal` connection kinds; each endpoint is exactly a component ID plus an existing named port. Connections and components already support arbitrary string-valued `metadata`.
- `catalog_rankine.py` labels turbine `shaft`, acoustic-sensor `mount`, Hall-speed-sensor `pickup`, heating-coil `mount`, and thermocouple `mount` as signal ports. These are useful attachment handles, not evidence that a physical shaft or mounting surface is an electrical signal. No other built-in catalog defines a named shaft or mount port.
- `pidcore.validate()` requires a signal line whenever either port is signal. `app.Window.connect_port()` infers this automatically. The current validator intentionally allows signal lines between two process ports, with a diagnostic warning.
- `app.Pipe.update_route()` uses the same orthogonal routing and solid/dashed styling for every connection. `drawio_export.export()` independently uses a dashed style for signal. The generic kind is therefore both topology and appearance today.
- `diagnostics.inspect()` counts every line as a port occupation and recommends a tee whenever a non-tee port has multiple connections. That is inappropriate for an independent mounting association attached to the same graphical location.
- `workspace.py` preserves connection metadata and rewrites the two existing endpoint IDs during copy/paste. It does **not** rewrite arbitrary component IDs hidden inside metadata strings.
- `openai_bridge.py` wire version 2 omits connection metadata from generated records, retaining existing metadata locally during updates. Local `operations.py` proposals already accept connection metadata through the document schema.

## Recommended minimum: explicit semantic annotation, not a disguised new fluid line

Use a reserved, documented string metadata key such as `pid_relationship` on existing connection records, with values `surface_mount` or `shaft_association`. Absence means the existing interpretation. Keep `kind='signal'` only as the legacy serialization carrier for these annotated records, and never show that carrier as their engineering meaning in the new UI. A central helper must return an effective relationship category rather than having each consumer inspect raw `kind`.

This is the smallest **file-open-compatible** extension: older apps still accept the JSON and preserve metadata in normal save/copy workflows. It is **not semantically compatible rendering**: older apps will draw it as a signal line and may include it in a piping register. The new app must state that limitation whenever these annotations are used, particularly for legacy export. A generic metadata string is not a magic compatibility solution.

This first increment should describe associations only. It should not claim to model a certified shaft coupling, a nozzle, an electrical terminal, an instrument-air circuit, or a mechanical installation detail. Retaining an existing endpoint port as a graphical anchor must not imply that the mount penetrates that fluid port. The user-visible relationship label and exported legend should explicitly say “mounting association” or “shaft association.”

### Why not immediately add connection kinds?

Adding `mechanical`/`mounting` values directly to the existing `kind` enum causes older readers to reject otherwise valid drawings. Changing existing built-in `port_kinds` to those values also invalidates legacy files under the current semantic validator, changes the AI catalog fingerprint, and affects custom definitions. A versioned migration can do this correctly, but it is not the minimum low-risk correction.

### Why not store host component IDs only in metadata?

That creates hidden references. Copy/paste, duplicate, deletion, diagnostics, AI removal and reconnection would no longer see them. Prefer the existing `from`/`to` references for the additive annotation phase. Never introduce a `mounted_on='component-id'` string without central reference discovery/remapping and corresponding tests.

## Endpoint policy

1. Preserve every existing component ID, tag, port name, position, rotation and port kind on load. Do not automatically recategorize old signal lines merely because one endpoint is named `shaft`, `mount` or `pickup`; older drawings may use them differently.
2. Offer an explicit, undoable “Classify relationship” action for existing lines. Preview both endpoints and the proposed semantic category before applying. An unclassified legacy use of a known non-fluid handle gets a review warning, not a save failure.
3. For a new `surface_mount` relationship, require one end to be a declared built-in mounting/pickup handle. The other endpoint is a graphical host anchor on the target component; show that it is not a fluid connection. Do not reuse process-branch rules or claim a tee is required for this association.
4. For `shaft_association`, require a declared shaft handle at one end. The current catalog has only the turbine shaft, so the other end cannot be claimed to be a validated mechanical shaft interface without adding an appropriate target capability. Initially label it an association to equipment, not “shaft coupling validated.” Do not silently turn a pump inlet into a shaft.
5. A later proper endpoint-capability model should distinguish `process`, `signal`, `shaft`, `mount` and `pickup`, with explicit compatible targets. Mechanical sensing and torque transmission must remain separate: a Hall pickup measures a rotating target, not a mechanical power connection.
6. Reject a relationship whose two endpoints are identical, missing, or whose reserved metadata value is unknown. Unrecognized unrelated metadata remains preserved. Do not hard-fail all unannotated legacy shaft/mount lines.

## Exact implementation impact

| Files / area | Minimum additive change | Important compatibility risk |
|---|---|---|
| New `relationships.py`; `pidcore.py` | Central category resolver, declared built-in handle roles, relationship validation, topology classification. Validate annotated records before the legacy signal rule; keep carrier kind consistent. | Every consumer must distinguish semantic category from stored kind. Do not infer migration on read. |
| `document.schema.json` | Existing metadata can carry the string without a structural change. Document reserved keys. If reserving enum validation in JSON Schema, ensure unknown historical strings are handled deliberately. | New reserved-key rules can reject old arbitrary metadata with the same key; choose a sufficiently distinctive key and migration policy. |
| `catalog_rankine.py` | Optional built-in-only capability annotations or centralized role mapping; do not alter legacy port kinds. | Custom schemas currently prohibit extra definition fields; no accidental custom schema expansion. |
| `connection_editor.py` | Add an explicit relationship choice, clear source/host labels, and staged validation. Ensure Apply updates reserved metadata while preserving all other metadata. | Current `apply_connection()` intentionally copies only from/to/kind/label/waypoints from the candidate; new relationship edits would otherwise be silently discarded. |
| `app.py` | Update click/drag creation guidance, kind property validation, and Pipe tooltip/style through shared helpers. Keep ordinary connect behavior unchanged unless relationship mode was chosen. | A new relationship must not be auto-created from any generic signal endpoint. |
| `editing.py` | Reconnection validation must retain relationship classification and reject incompatible target changes atomically. | Current reconnection copies the document and retains metadata, which is a useful base. |
| `diagnostics.py` | Separate process/signal connectivity from association occupancy. Add missing-host/ambiguous-legacy warnings. Exclude associations from tee and signal-with-process-end warnings. | Do not make a mount count as a connected/closed process port or satisfy an unconnected fluid-port review. |
| `app.Pipe`, `routing.py` | Reuse geometry initially with a distinct, declared association appearance and label. Keep routing obstacles and waypoint behavior unchanged. | A generic dashed line would remain indistinguishable from the existing signal convention. Do not claim an unsourced line pattern is normative. |
| `deliverables.py` | Show effective relationship category in register output, exclude associations from piping line lists or provide a separate association register, and include a legend note. PDF/PNG/SVG share the scene renderer. | Existing CSV includes all connections and raw `kind`; omitting this work produces false piping records. |
| `drawio_export.py` | Match the new appearance and label; preserve relationship metadata explicitly. Existing object `pid_metadata` already carries metadata, but style is still raw-kind-driven. | Draw.io geometry/metadata retention is not a supported round-trip importer into PID Studio. |
| `workspace.py`; deletion/nudge logic in `app.py`/`editing.py` | Existing endpoint rewriting, copying and group waypoint movement should remain correct; assert reserved metadata survives. Delete attached associations with the same deliberate behavior as other references. | Avoid hidden component IDs in metadata. |
| `operations.py`; `ai/AUTHORING.md` | Explain the annotation contract and forbid invented physical associations. Add relationship constraints and review findings. Existing local proposals can carry metadata. | AI-generated defaults must not silently reclassify saved connections. |
| `openai_bridge.py` | Either leave creation/classification human-only initially, with clear unsupported-operation guidance, or add a nullable strict wire relationship field in a new wire version and map it to metadata. | Wire v2 cannot create these annotations; changing schema requires schema/provenance tests and provider validation. No real API call needed for local tests. |
| `review_history.py`; `generation_provenance.py` | Fingerprints already cover document metadata; test acceptance/cancel/stale guards with annotations. | Do not rewrite historical accepted proposals or hashes during migration. |
| `run_studio.py`; `PIDStudio.spec`; docs | Add a synthetic classification/save/reopen/export/undo packaged smoke case and include any new module/documentation. | A source-only pass does not verify the distributed executable. |

## Migration and downgrade behavior

- New reader + old file: no mutation, original interpretation preserved; diagnostics identify ambiguous shaft/mount use.
- Explicit classification: one undoable change to the selected connection's metadata and carrier kind only. Preserve full original metadata, IDs, endpoints, waypoints and label; provide an informative default visible association label only if the user explicitly accepts it.
- New reader + annotated file: validate and render associations using the new helper; no hidden automatic migration.
- Old reader + annotated file: structurally readable but semantically degraded. Warn in the new app/documentation. A legacy export should be a separate copy with explicit textual relationship notes; do not silently strip annotations and claim fidelity.
- Clipboard: copy annotated links only when both referenced components are copied, matching current behavior. Remap both endpoint IDs, preserve annotation values, and keep the source drawing unchanged.

## Proper long-term model, only after the additive phase is accepted

A native v2 drawing could introduce a separate `relationships` collection with component/anchor references independent of fluid ports, and typed relationships for shaft coupling, surface mounting, and sensor observation. This avoids overloading `signal` and allows an equipment-body anchor. It also requires generic reference traversal across collections, new selectable scene items, copy/delete/undo handling, all exporters, AI contracts, schema migration, and an explicit v1 compatibility export. Keep a v1 reader; never rewrite the source file merely by opening it. That is a broader feature, not a small enum edit.

## Required tests before enabling the minimum extension

- Old fixtures save/open byte-equivalent as data; no automatic classification or tag/port changes; historical review records untouched.
- Explicit classify/unclassify preserves arbitrary metadata, line identity, endpoints and waypoints; one undo/redo step; cancel and invalid changes leave history and document unchanged.
- Compatible mounting/shaft-association sources accepted; unknown values, same-port endpoints, missing targets and invalid reconnections rejected without mutation.
- Association does not count as fluid continuity, close an open process port, or trigger a tee requirement. Existing process/signal diagnostics remain unchanged.
- Copy/paste between drawings remaps both endpoints and preserves annotations; delete and duplicate behavior has no dangling links.
- All four component rotations, group movement, waypoint edits, selection and route errors remain visible and correct; no regressions to ordinary connection gestures.
- PNG/PDF/SVG/draw.io show a clearly identified association consistently; CSV does not misreport it as a process pipe. Test long labels and exports after save/reopen.
- Local AI proposal can carry an explicit annotation safely; wire v2 cannot invent it. If wire schema changes, test strict decode, null/default behavior, stale fingerprints, preserved metadata, rejection/cancel and provenance schema hashes without a live key.
- Packaged executable smoke verifies the actual new helper, sample file and export behavior, not only the source environment.

Recommendation: implement the additive **association annotation** first only if its semantic downgrade limitation is acceptable. Otherwise implement a clean v2 relationship collection rather than disguising mechanical relationships as signal lines. Neither path should change existing drawings without an explicit editing action.
