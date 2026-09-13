# Critical-feature acceptance record

Local personal-editor development and offline validation completed September 11,
2026. Every requested local feature is implemented; no known critical local
failure remains from the final sweep. External checks below are explicitly not
claimed successful.

## Final evidence

- Final source suite: 178 tests passed; portable runtime verification passed.
- Evidence: build/packaged-check-x1t9yjwo/verified-build.json.
- Executable SHA-256: 906f9b553a441d8130871f052bc87ab395a9921d740f3244ed92ba91c2ed09eb.
- Runtime verification used a separate working directory and Windows-only PATH.
- Packaged workbench and sheet-preview screenshots inspected.
- Long-content source PDF/PNG renderings inspected across A4/A3/ANSI B/ANSI D.
- Supplier notice and bundled binary hashes verified against the actual package.

## Completed local gates

| Requirement | Final evidence |
| --- | --- |
| Classic light offline editor | Packaged workbench inspected; no key or network required for editing. |
| Create/modify/save/open | test_editor, test_open_paths; validated atomic saves and preserved state on invalid/cancelled open. |
| Place and edit equipment | test_critical_workflows, test_drafting, test_editing, test_workbench_feedback; toolbox double-click and Qt drag/drop dispatch, properties and keyboard focus. |
| Connect equipment | test_connection_interaction and test_connection_validation; viewport click-click/drag, overlap/reduced zoom, preview/cancel and transactional rejection. |
| Routing and route editing | test_routing, test_route_geometry, test_editing, test_critical_workflows; ports follow movement/rotation, waypoint gestures, reconnect/reset. |
| Dense movement | test_dense_drag plus benchmark_dense_drag; 96 components/16 pipes, clear attached routes each move, canonical release, exact undo/redo/save. Moves measured 6-35 ms, release 617 ms here. |
| Clipboard and ordinary editing | test_editor, test_notes, test_drafting, test_editing; remapped identity, metadata, selection, nudge/align/distribute/rotation and undo/redo. |
| Custom symbol library | test_custom_symbol_core/clipboard/integration; bounded primitives/ports/envelopes, import/export, protected in-use definitions, contextual catalog, all rotations and conflict remapping. |
| Notes/metadata/outline/validation | test_notes, test_deliverables, test_diagnostics, test_workbench_feedback; notes, reports and clickable review warnings. |
| Recovery/file safety | test_recovery, test_open_paths, test_critical_workflows; invalid snapshots, unsaved-copy recovery, cancel/save failure and only-own-snapshot removal. |
| Exports/preview | test_deliverables, test_sheet_preview, test_drawio, test_long_exports, test_sheet_overflow; physical page sizes, content, all-paper text cell geometry, DPI-independent pixels and stale-preview clearing. |
| Reference and offline authoring | test_proposals, test_sketch_corpus; actual format/catalog/instructions/fingerprint, original image retained and normalized payload, known graphs and ambiguities. |
| Mandatory review/history | test_source_review, test_review_history, test_proposals; invalid/stale/cancel is nonmutating, mandatory checks, one-transaction acceptance, save/undo. |
| Optional API pathway | test_openai_bridge, test_assistant_lifecycle; mocked actual Qt signals, one in-flight request, malformed/refused/errors/redirect/cancel/timeout/limits and review. No live request. |
| Format/provenance infrastructure | test_generation_provenance and packaged context/history; request-time hashes, normalized image distinction, allowlisted response metadata, no credentials/raw replies retained. |
| Portable package/notices | verify_build plus test_distribution_notices; actual executable startup/edit/roundtrip/export, supplied notices and final binary inventory. |
| Documentation | README, ROADMAP, PACKAGING, SYMBOLS, DENSE_ROUTING and corpus instructions reconciled to current behavior and limitations. |

The full suite covers the listed modules; test names alone were not treated as
visual proof. Long-export inspection caught PDF text that was extractable but
clipped visually. That defect was fixed and re-rendered, with actual pixel/cell
geometry regressions added. Excessive metadata is rejected before export output
is opened, preserving existing files.

Native OS drag initiation was not automated; Qt viewport drag/drop dispatch was.
Physical printing uses the shared renderer but is not equivalent to testing a
real printer. Same-machine sanitized PATH tests are not a clean-machine check.

## External/human-enabled checks not claimed passed

- Live API provider behavior with an explicitly authorized key/model: strict
  schema acceptance, text/photo requests, service errors/cancellation/billing.
- Recognition evaluation on user-approved real sketches with known expected
  components/tags/connections and ambiguous cases. Synthetic fixtures are not a
  recognition benchmark.
- Physical printer scale/margins/clipping.
- Separate clean supported Windows machine without development dependencies.
- draw.io Device file-open/edit/save/reopen interoperability. Synthetic graph XML
  editing/artwork/attached movement were observed, but the supported browser
  file-chooser event timed out on Device and native-app controls are unavailable.
  No cloud sign-in or credentials were used. XML/file structure tests pass; this
  exact target-file roundtrip remains unverified. Route vertices may need manual
  adjustment after target-editor moves.
- Public redistribution legal readiness. Supplier notices and hashes are
  included, but the Qt wheels' commercial-reference notice does not establish a
  commercial license or complete alternative-license/source obligations.
  THIRD_PARTY_NOTICES.md records those gaps without claiming compliance.

These are explicit limits of the personal local package acceptance, not hidden
successes or reasons to request unavailable user input. No solver, hosted backend,
DEXPI, marketplace or standards certification is required for the agreed scope.

## Expanded component library follow-up

133 built-in types (114 additions), plus portable custom definitions. New process,
valve/fitting and instrument catalogs include original vector artwork, named ports
and explicit process/signal kinds. Every added definition passes schema and
four-rotation port-clearance checks. All types roundtrip and feed reports and
authoring context. Search supports labels, categories, type words and tag prefixes;
Browse components previews ports and inserts in one undoable step.

Final visual QA corrected nozzle-to-body gaps and preview resize clipping.
All 133 packaged catalog definitions were compared to final source and match
exactly, including those corrections. Packaged catalog screenshot was inspected.
COMPONENTS.md gives inventory, primary family references and limitations;
comprehensive coverage is not a claim of every industry type or ISA/ISO certification.
New supporting files are hidden; Launch remains the only visible app entry point.
User drawing folders are left untouched.

## Component folder organization follow-up

Toolbox and catalog browser now share collapsed, expandable folders/subfolders for all 133 built-in types and separate category folders for custom components. Folder-aware search temporarily opens matches and restores the previous expansion state when cleared. Only component leaves can be inserted or dragged; saved file identifiers are unchanged.

Verification: 182 tests passed. Rebuilt portable application passed its isolated runtime checks; collapsed-folder and filtered-preview screenshots were inspected in `build/packaged-check-punrbkbo/results`. Current executable SHA-256: `4c78f9437efcfc4fb0146e7a8ae2ca4b6fe2ecbe96b9ec9ef65bb6f663e07759`. Supporting files remain hidden; unrelated user files were preserved.
