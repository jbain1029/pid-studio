# PID Studio - local package completion

The requested personal offline editor is implemented and locally verified as of
September 11, 2026. The compact light engineering-workbench UI is retained.
This does not certify engineering correctness or any external acceptance checks.

## Delivered scope

- Python/PySide6 editor and standalone portable Windows application.
- Drag/drop and double-click insertion; click-click and drag-to-connect named ports.
- Editable equipment, piping, tags, notes, waypoints and engineering metadata.
- Move/rotate, reconnect endpoints, alignment/distribution, clipboard, undo/redo.
- Readable validated .pid JSON, atomic save, open/recent files, recovery browser.
- 133 built-in components and drawing-local custom vector definitions with portable
  .pidsymbol import/export, preview, conflict-safe clipboard and validation.
- Orthogonal obstacle-aware routing and clear failure diagnostics. Crossings do
  not connect; explicit tees express branching. No fluid calculation.
- Shared sheet preview/PDF/PNG/printing layout, SVG, draw.io and CSV registers.
- Reference sketch attachment and offline typed proposal context/review workflow.
- Optional asynchronous OpenAI photo/text pathway with schema/catalog/instructions,
  bounded requests, credential separation, source-region review and local provenance.
- Supplier notice and bundled-binary inventories; no public redistribution approval.

## Final local evidence

User-requested follow-up: explicit light popup palette, precise staged connection
editor, consistent component terminology and a ruled industry-informed sheet
template with document-control fields and line legend. New tests cover popup
colors under a dark initial palette, atomic connection editing, and sheet
numbering/layout. Packaged menu, connection editor and sheet preview captured;
menu and sheet screenshot visually inspected. SHEET_STANDARDS.md records ISO/ISA
reference scope without claiming certified compliance.

The final source suite passed 178 tests. The actual portable executable passed its checks from a separate working directory with Windows-only PATH.
Evidence: build/packaged-check-x1t9yjwo/verified-build.json.
Executable SHA-256:
906f9b553a441d8130871f052bc87ab395a9921d740f3244ed92ba91c2ed09eb

Packaged workbench and sheet-preview images were inspected. Checks include
connection viewport events, selected new lines, undo, save/reopen, recovery,
custom-symbol context, review/history, readable PDF text, image loading,
preview/export equality and supplied-notice/binary hashes.

Final workflow tests also exercise toolbox insertion/drop dispatch, waypoint
dragging, save/close cancellation, failed saves and recovery snapshot ownership.
The synthetic sketch corpus covers three known process/signal/ambiguity cases;
it establishes local pipeline behavior, not model recognition accuracy.

Visual long-content PDF testing found a real DPI/font clipping bug. Fixed using
device-independent vector scene staging and measured metadata cells. All four
paper-size renderings were inspected with complete notes/title/identity visible.
Raster equality at 96/150/1200 output DPI and cell geometry tests protect the fix.
Excessive metadata produces an actionable preview/export error before overwriting
an export; it is not silently clipped or squeezed into illegibility.

The valid dense viewport fixture contains 96 components and 16 crossing routes.
Measured movement fell from 586-629 ms to 6-35 ms using only still-clear unaffected
routes during movement. Release recomputes canonical routes (~617 ms here).
Per-event clearance/attachment and exact history/save checks pass. See
DENSE_ROUTING.md; these are local measurements, not a frame-rate guarantee.

## Explicitly unverified or limited

- Real API keys/provider schema acceptance, billing/cancellation behavior and real
  hand-sketch recognition. No live calls or real credentials were used.
- Physical printer output and a separate clean Windows machine.
- draw.io file-open/save/reopen roundtrip: the approved synthetic graph was loaded
  through Edit Diagram, with artwork/label editing/attached movement observed.
  The browser Device file chooser timed out; native app controls are unavailable.
  This tooling-limited interoperability check is not marked passed. Exported
  vertices may require manual routing adjustment after moves in draw.io.
- Public redistribution licensing readiness: supplied notices are included, but
  applicable Qt/native-library license paths and source obligations need review.
  See THIRD_PARTY_NOTICES.md.
- No solver, DEXPI interchange, hosted backend, collaboration service, automatic
  symbol recognition accuracy claim or standards certification is included.

See CRITICAL_FEATURES.md for final acceptance mapping, PACKAGING.md for launch
instructions and SYMBOLS.md for the bounded custom-definition contract.

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
