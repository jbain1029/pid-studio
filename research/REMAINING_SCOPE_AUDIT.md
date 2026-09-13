# Remaining scope and completion-gate audit

2026-09-12. Read-only scope review. This document does not close the goal, change a disposition, authorize a release, or modify production code. It evaluates the requested outcome against `STUDY_STATUS.md`, the three exhaustive component matrices and their resolution appendices, `SPECIALIZED_INSTRUMENT_FOLLOWUP.md`, `VALVE_DIRECTION_FOLLOWUP.md`, and `RELATIONSHIP_MODEL_PLAN.md`. Main-agent implementation is continuing; statuses quoted here are a review snapshot, not a substitute for checking the final source and evidence.

## Requested outcome

The actual task is to deeply study the component library for understandable, industry-typical P&ID drafting, taking account of the supplied legend and additional industry evidence, and to ensure the SVGs render properly. Earlier product requirements deliberately excluded fluid calculations and an advanced engineering-analysis system. The user did not request a purchased normative certification, construction approval, universal compliance across all standards, or a full mechanical/electrical simulation model.

The supplied chart is an explicit reference, not permission to repeat a misleading drawing. Conversely, absence of an exact matching proprietary symbol in a publicly accessible standard is not proof that a comprehensible project convention is unusable. The relevant distinction is **documented, recognizable family with clear meaning** versus **incorrect or unestablished meaning concealed by a label**.

## How the current gates should be applied

| Current gate in STUDY_STATUS | Real requirement to preserve | Scope boundary / finite way to satisfy it |
|---|---|---|
| Close remaining engineering-semantic mismatches | No blank/incorrect identity, contradictory flow cue, broken nozzle, or silently misleading shaft/mount connection should remain in the supported workflow. | Fix the actual representation or explicitly constrain an unsupported interaction. A complete v2 relationship schema, validated shaft couplings and installation physics are not prerequisites to a simple editor. |
| Substantiate every project-specific/unresolved case | Every type needs a recorded judgment and a defensible visible interpretation; "custom" alone is not evidence. | Accept a chosen reference alternative, a recognizable generic family plus explicit subtype/duty, or a documented composite with intact service boundaries. Do not require every valid alternative to become a uniquely universal normative glyph. |
| Separate function, technology, location, medium and state | Do not draw a location bar without basis, make a technology letter substitute for functional identity, or infer a fail state from an unrelated filled mark. | A neutral/unspecified default with explicit notes is sufficient where data is not supplied. Full configurable profiles, every actuator fail-state option and all signal-media classes are broader features, not automatic blockers. |
| Synchronize the report and 141-type matrix | Each baseline finding must have a current resolution or precisely stated residual limitation. No stale defects should be presented as still present. | Preserve the baseline matrices and add a compact current resolution ledger; rewriting historical counts or doing fresh research for already-closed geometry is unnecessary. |
| Repeat rendering, practical-size and executable checks | Test the final changed implementation, not a prior SVG or binary; inspect actual artifacts, not only XML validity or image load events. | All isolated built-in SVGs at four rotations, browser loading, visual review and representative complete-sheet exports are finite. A single drawing connecting all 141 unrelated components, every conceivable user tag, every SVG consumer or a clean-room CAD certification is not required. If shipping the portable executable, rebuild and smoke-test that exact binary. |
| Audit complete objective before completion | Confirm both drafting meaning and rendering evidence with remaining limitations disclosed. | Completion is not allowed merely because tests pass, but it also must not be deferred forever by unrequested calculations, purchased standards or speculative enterprise features. |

## Concrete remaining work with genuine drafting impact

### 1. Attachment and shaft meanings: close the visible semantic hazard, not an entire mechanics model

The process and instrument audits establish that `shaft`, `mount` and `pickup` were serialized as `signal` handles. `RELATIONSHIP_MODEL_PLAN.md` correctly explains that a mounting relationship and a control/measurement signal are different, and that old records must not be reinterpreted on file open. This is a real concern if the app automatically creates and exports a dashed instrument signal to represent physical shaft transmission or a sensor attached to a surface.

Minimum acceptable correction options are bounded:

- Introduce a clearly named graphical association with deliberate creation/classification, a distinct declared legend meaning and consistent export behavior; preserve old data and warn on ambiguous legacy usage. The existing plan's metadata-carrier option is one possible implementation, not the only required architecture.
- Alternatively, keep these components as explicitly illustrative equipment/attachment graphics and do not offer the ambiguous handles as ordinary supported signal connections. Use an explicit note/annotation workflow until a real association is supported. This must be visible in the app and issued drawing, not buried solely in the research report; it must not silently discard existing connections.

Neither option needs torque transmission, mounting geometry, a shaft-capability registry, structural/thermal calculations or a complete new document version. If a new association is implemented, however, export, undo/save/reopen and diagnostics must honor it; a hidden metadata flag with unchanged misleading output is not a fix. A full versioned relationship system and old-reader semantic downgrade tooling are valuable later work, not required merely because the word "shaft" exists in the library.

### 2. Specialized instrument identities: use the primary examples already found

The initial matrix's radar and thermal-flow glyphs were unresolved; `SPECIALIZED_INSTRUMENT_FOLLOWUP.md` now gives actual project P&IDs supporting **LT + RADAR** and **flow function + thermal-mass technology annotation**. Those are sufficient grounds for a bounded representation correction. Preserve FT rather than copying FIT and thereby inventing an indicating function; retain current process/signal topology with an explicit integrated-assembly description where necessary.

For `hall_speed_sensor`, `acoustic_sensor`, `humidity_sensor`, `thermocouple` and `inline_flowmeter`, the remaining problem is not that every historical/project mnemonic must be prohibited. It is whether a reader can determine the intended measured function without mistaking HS for hand switch or TC for temperature control. The instrument audit itself documents conflicting historical TC uses and project-specific D/density precedent. Therefore:

- Keep saved tags intact.
- Show the chosen functional meaning or explicit full device/measurement wording on the drawing or its issued legend, not only a rotating pictogram or developer ID.
- Do not invent an output type, indicator, control function or sensing technology to force the prefix into a guessed standard mapping.
- If the app adopts an ISA-oriented functional mode, distinguish that from a retained legacy mnemonic; do not claim every legacy tag was migrated merely because its text is upright.

A multi-profile ISA/ISO tag engine is not required to explain these few existing components. Unsupported location bars and missing letters were real defects and have recorded corrections; requiring every possible accessibility/location choice afterward would expand scope.

### 3. Still-unresolved specialized valve forms: finite source selection or functional abstraction

The valve follow-up provides sourced replacements for the relief and foot-valve cases, and `STUDY_STATUS.md` records implementation. Do not reopen them solely because another source uses a different inline/angle or seat convention. Verify the final shape, declared direction and preserved ports instead.

The initial matrix also identifies `knife_gate_valve` and `vacuum_breaker` as unresolved. Unless newer implementation has closed them, these deserve a bounded final decision:

- Knife gate: choose the actual supplied Knife Valve depiction or another inspected project symbol, adapt the existing endpoints, and state the selected convention. A vaguely blade-like decoration unsupported by the chosen reference should not acquire an exact match claim.
- Vacuum breaker: make **atmospheric admission into the process under vacuum** unambiguous. Do not substitute a pressure-discharge relief/check mark with the opposite service. Use an inspected vacuum-admission convention or a clearly identified generic functional assembly with explicit atmospheric/process sides; the latter must be documented as an abstraction, not a certified device symbol.

Regulator sensing-line continuity is recorded as repaired. The remaining spring-only hybrid needs one defensible actuator/sensing convention, or explicit simplified-regulator treatment that preserves downstream sensing for reducing service and upstream sensing for back-pressure service. Designing regulator control dynamics and adding relief setpoints/sizing are outside this symbol task.

### 4. Multi-circuit drawings: keep the information needed to read connections

The current process appendix documents the actual corrected generic and shell-and-tube exchanger paths. Those findings are closed at family level; a TEMA-specific nozzle schedule is not required for a generic P&ID exchanger.

The plate exchanger and straightened double-pipe adaptation need explicit process-versus-utility pairing because their internal marks do not uniquely encode every path. The small double-pipe drawing can represent upper/lower portions of one annulus out of plane; that ambiguity is not proof that the device blocks flow. A visible legend/description identifying tube and annulus, or a clearer referenced depiction, is the bounded remedy. Do not add fluid calculations to solve a drawing-interpretation problem.

The jacketed reactor likewise needs its composite/jacket indication explained; a feed line should not be interpreted as dumping into the jacket simply because it crosses the jacket outline. Boiler/furnace package symbols may expose labeled service nozzles without depicting every burner and drum. This is acceptable only if represented as an abstraction/package, not falsely advertised as a detailed internal flow diagram.

## Project-specific rows that are not automatically blockers

These are not blanket approvals. Each remains subject to the current row's actual geometry and an issued, understandable legend.

| Matrix group | Usually a convention/duty choice rather than an unsolved defect | Required evidence/communication |
|---|---|---|
| Drain, vent and sampling valve duty variants | A recognizable manual isolation body can serve these duties without a unique mechanism symbol for each duty. | Identify the assumed body/operator and duty; do not imply automatic venting, sampling package accessories or a special mechanism. |
| Steam-trap subtypes | A generic trap family plus an explicit float/bucket/thermodynamic/etc. note can be clearer than an invented mechanism pictogram. | Do not substitute a trap-set symbol and imply accessories absent from the component. Choose generic plus subtype or document the illustration; no trap sizing required. |
| Technology pictograms for magnetic/Coriolis/vortex/ultrasonic/turbine flow measurement | The supplied chart explicitly offers technology glyphs; not all are universal functional symbols. | Retain functional identity and technology distinction with the chosen project legend. Missing or misleading function is a defect; absence of an exact ISO symbol-number proof is not by itself one. |
| Tank/vessel/column/mixer/separator abstractions | A process symbol need not be a literal cutaway or include all supports, trays, heads and penetrations. | Family evidence plus named duty and correct external services. A fictitious asserted path is not cured by a disclaimer. |
| Off-page connector | A visible drawing/sheet reference can be drafted as text even when the editor does not maintain an automatic cross-sheet graph. | Clearly identify the destination/reference and avoid claiming automatic connectivity. Full multi-sheet management is separate product work. |
| Generic signal line | A declared unspecified signal connection is a useful drafting abstraction. | Do not label it electrical or pneumatic without data, and do not misuse it for physical mounting. Full media-specific validation is not implied by this task. |
| Current-pressure converter | Generic I/P identity is supported and the rotation collision was repaired. | Input current/output pressure should be identified when the drawing needs that distinction. The software need not calculate transducer performance. |
| Centrifugal separator, vortex separator, cartridge housing and other bespoke package depictions | Missing exact public glyph evidence does not prove the underlying equipment is non-industry. | Prefer a documented recognizable base family plus explicit subtype/package note when a proprietary pictogram is not substantiated. Do not promote an unexplained decorative maze/triangle into a standardized internal arrangement. |

The current component-legend exporter already provides exact artwork, component labels, selected reference basis and drawing/library fingerprints. That is useful infrastructure. Its fallback text "Verify the adopted convention" is still a request for work, not by itself the adoption of a convention. For remaining house/composite types, a short concrete meaning/nozzle note would be more useful than indefinite generic uncertainty. Conversely, a full symbol-source paragraph on every drawing is unnecessary once a concise legend defines the chosen appearance and the study retains detailed evidence.

## What should not be turned into additional mandatory gates

- Purchasing the complete latest normative ISO/ISA tables, obtaining a third-party certificate, or proving universal conformity, unless the user later explicitly chooses that target.
- Adding process calculations, relief sizing, pressure-rating verification, thermowell stress analysis, boiler controls or certified installation design.
- Implementing a full document-v2 schema, every connection-medium class, mechanical power networks or all future AI relationship operations solely to eliminate a bounded visible ambiguity.
- Making every component's subtype uniquely identifiable without labels even though the selected sources themselves use shared families and rely on identification/legends.
- Rejecting documented project variations such as inline versus angle relief bodies, different trap-versus-trap-set conventions, or historical TC/DT identification, merely because they differ from one selected chart.
- Testing unlimited tag lengths at a fixed readable font size or every third-party SVG engine. Define reasonable supported behavior: no silent truncation, faithful export, usable default sizes, and honest limitations for extreme content.
- Requiring a single artificial connected drawing containing all 141 unrelated component types. Use complete isolated inventory coverage plus representative connected fixtures for every materially distinct path: four-port exchangers, sensing lines, actuator letters, compound identity, attachments and sheet annotations.

## Recommended finite closeout sequence

1. Reconcile the latest implemented fixes against the matrices. Separate **still wrong**, **adopted convention**, **supported abstraction**, and **explicitly unsupported workflow**; preserve the original audit history.
2. Close the remaining identity/relationship/direction hazards above. Where research already supplies a usable primary example, implement and verify it rather than seek unnecessary certification. For remaining invented glyphs, adopt a defensible generic family with explicit subtype/service, not a cosmetic rename.
3. Record concrete notes for the remaining project-specific representations in the actual issued legend or documented drafting convention. Ensure ambiguous mnemonics and separate circuits are understandable in exported drawings.
4. Regenerate the final all-component/all-rotation SVG set and inspect changed families in a second renderer. Retain the full inventory coverage check and practical-size complete-drawing/legend tests. Correct actual clipping, illegibility or disappearing primitives; do not equate a load event with visual success.
5. If delivering the packaged executable, rebuild and run its current smoke/export checks. Record the exact source/library/executable evidence association.
6. Have the main agent compare those concrete results to the user's outcome and explicitly account for every residual limitation. This document does not mark the goal complete or waive any confirmed error.

## Evidence used in this scope decision

This review relies on the repository's recorded inspections rather than presenting new standards research. Exact primary-source URLs and figure locators remain in the component studies and follow-ups: DOE Figure 15 for centrifugal families; DOE Figure 1 and IXOM High Level drawing NAXXXX-03-00-002 for relief/foot-valve alternatives; ISA *Control Loop Foundation* Figures 7-9/7-11 for function and location; Stantec I-006 for LT plus RADAR; DOE-hosted Exhibit 3.2.2/3.2.3 for thermal-mass functional identification; and manufacturer references for separated circuits, mount/signal and well/sensor distinctions. Their differing scopes are material evidence for these boundaries, not reasons to weaken the requirement for coherent drawings.

File visibility: no files were hidden, moved or deleted for this review. Only this requested report was created.
