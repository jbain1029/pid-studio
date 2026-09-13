# Component-symbol study status

## Objective

Study every component against the supplied legend and additional industry sources,
resolve alignment problems, and verify that all SVG artwork renders correctly.
The baseline findings have bounded drafting resolutions recorded below. Final
release checks are recorded separately from historical checkpoints. These
resolutions do not claim universal normative certification or construction approval.

## Initial evidence checkpoint

The inventory is 141 built-in types. The three exhaustive audits cover disjoint
sets: [45 process components](process-audit.md), [49 valve/piping/protection/steam
components](valves-audit.md), and [47 instruments](instruments-audit.md). Their
initial dispositions total 63 supported families, 34 mismatches, 37
project-specific representations, and seven unresolved cases. These are baseline
judgments, not conformity certificates; fixes below do not silently rewrite them.

The supplied file is `C:/Users/jaxon/Downloads/pid-legend.pdf`, SHA256
`21fe90dfd45c57a1c1ba141a31999ede51b9b6ca247b7399bc35fff7bb234b40`.
It is an Edrawsoft symbol chart with several alternatives, not the normative
text of ISA or ISO. The chart remains a requested project reference, but conflicts
must be resolved by an explicit drawing convention rather than cherry-picking.

## Standards scope

1. [ANSI/ISA-5.1-2024](https://www.isa.org/standards-and-publications/isa-standards/isa-5-standard)
   is the current ISA instrumentation/control identification standard listed by
   ISA. The public scope and teaching examples establish useful principles; the
   current complete normative tables have not been acquired or verified.
2. [ISO 10628-2:2012](https://www.iso.org/standard/51841.html) remains current,
   confirmed in 2024. It addresses chemical/petrochemical diagram symbols. The
   official catalogue is scope evidence, not access to each symbol definition.
3. [ISO 14617-2:2025](https://www.iso.org/standard/83364.html) is a newer consolidated
   industrial symbol library. Its official lifecycle lists older 14617 parts
   2-15 and ISO 3511 parts as withdrawn. It excludes fluid-power objects,
   electrotechnical objects, and measurement/control functions identified in its
   scope. It must not be mistaken for a blanket replacement for ISA-5.1 or the
   still-current ISO 10628-2 application standard.
4. [ISO 14617-1:2025](https://www.iso.org/standard/85641.html) supplies general rules
   for preparing and presenting industrial diagram symbols; the earlier 2005
   edition is withdrawn.
5. [DOE-HDBK-1016/1-93](https://www.energy.gov/ehss/articles/doe-hdbk-10161-93)
   is archived government training material. Its actual figures are useful
   historical primary evidence, not proof of current universal conformity.

The family audits additionally identify exact VA project legend sheets, ISA
teaching figures, and manufacturer publications. Equipment cutaways support
physical-function judgments, not automatically the correctness of a P&ID glyph.
No paywall or access control was bypassed; no standards were purchased.

## SVG evidence

`verify_svg_catalog.py` generates actual component SVGs, rasterizes them through
Qt SVG, compares their ink to the direct editor painter with one-pixel tolerance,
and checks a larger viewport for clipped artwork. It checks XML validity,
nonempty drawing content, and external-resource references. The baseline passed
568 cases: every built-in plus one custom fixture at four rotations.

Evidence is under `build/svg-audit-initial` and `build/svg-audit-browser`, with
per-case hashes, measured discrepancies, SVG files, and 15 rotation contact sheets.
All 568 images also loaded in the in-app browser. Browser screenshots independently
confirmed the initial I/P slash/text collision; loading alone is not a visual
correctness claim. Reviewers inspected every assigned component at four rotations.

## Implemented corrections

| Finding | Initial evidence | Implementation / remaining verification |
|---|---|---|
| Rotated M becomes W; S sideways | Actual SVG sheets and valve audit | Replaced vector letter strokes with upright text at the rotated actuator centre. Port positions unchanged. |
| Rotated I/P slash crosses letters | Browser and SVG sheet 14 | Slash and lettering now share the upright annotation layer. |
| Controller bars rotate inconsistently | SVG sheet 12 | Unsupported bars removed from function-only controllers. Explicit legacy Panel controller retains its upright marker. |
| Rankine F/H/T letters rotate | SVG sheets 14-15 | Lettering is upright; original labels/tags/port semantics retained pending separate engineering decision. |
| Humidity bar rotates | SVG sheet 15 | Unsupported bar removed; HS mnemonic interpretation remains project-specific. |
| Missing function and loop identification | Instrument matrix | All 30 generic bubbles now show function and instance identity; compound/arbitrary tags preserved in full. |
| PT/LT location inferred from sample | ISA Fig. 7-11 | Unsupported PT/LT bars removed. Configurable location/accessibility remains future modeling work. |
| Pump routing envelopes too small | Process matrix | Screw/reciprocating envelopes expanded to cover their actual circular bodies. |
| Tank vent and turbine outlet gaps | Process matrix | Tank rim-contact adapters and turbine wall contact added, preserving all saved ports. Tank adaptation remains project-specific. |
| Regulator and foot-valve gaps; ambiguous cross | Valve matrix | Sense paths joined to existing linkages, foot-valve bridge added, cross-junction dot filled. Exact subtype/flow interpretation caveats remain. |
| Centrifugal blower shown with propeller blades | DOE Fig. 15; supplied Centrifugal Fan | Replaced with scroll casing, inlet eye and tangential discharge; saved ports and centrifugal label preserved. |
| Thermowell and sensor conflated | DOE Fig. 9; WIKA TW 90.11 | Explicit temperature-element-in-thermowell assembly with separate inner sensing stem/tip and closed protective pocket. |
| Selected variants not shown with drawing | Reference conflicts in study | Reports > Component legend (SVG) exports each used type with its exact artwork and declared reference basis. Companion export does not certify unresolved symbols. |
| Foot-valve orientation and unresolved relief box | IXOM High Level P&ID legend; DOE Fig. 1 | Upright foot body with retained strainer composite, and DOE inline relief alternative. Separate primary-source metadata does not inflate supplied-chart coverage. |
| Radar and thermal-mass identities | Stantec I-006; DOE-hosted thermal-mass P&ID | LT plus RADAR; FT plus THERMAL MASS with full instance identity, upright in four rotations. Technology is not substituted for function. |
| Shaft/mount handles stored as signals | Legacy port audit | New connections blocked at canvas, dialogs, reconnect and proposal acceptance. Existing links preserved and flagged for review; use drawing notes for physical associations. No new relationship schema is implied. |
| Ambiguous legacy mnemonics and composite circuits | Instrument/process audits | Explicit full meanings and circuit/service pairing in tooltips and issued component legend. No silent retagging. |
| Decorative separator internals | Process audit | Removed unsubstantiated maze/disc triangle/flash zigzag; retained generic equipment boundaries and service leads, with concrete package conventions. |
| Knife gate and vacuum-breaker interpretation | Supplied Knife Valve; bounded functional abstraction | Knife U-body/blade now follows chart. Vacuum breaker explicitly admits ATM toward process. Simplified regulators declare sensing side and no implied actuator/fail state. |

## Latest source verification checkpoint

- Current source regression checkpoint: **256 tests passed**. Portable build
  verification is recorded separately; the executable build record is authoritative.
- Post-correction component audit: **568/568 passed**, evidence under
  `build/svg-audit-final` (all latest source symbol corrections and convention notes included).
- Combined legend tests confirm visible ink for every built-in and distinguish
  source conventions from supplied-chart matches. Drawing and used-library
  fingerprints are independently recorded; changed built-in definitions change
  the library fingerprint even when drawing data is unchanged.
- All 568 corrected SVG images loaded in the browser. Direct browser inspection
  confirmed upright M/S, intact I/P lettering/divider, and readable DP/controller
  identity in all four displayed rotations.
- The latest gallery served all 568 actual SVGs to the browser. A compact changed
  gallery was visually inspected for knife gate, vacuum breaker, radar and thermal
  mass in four rotations: intact geometry and upright readable captions.
- `build/reference-closeout` contains representative current SVG/PDF/PNG sheet
  exports and a visually checked component legend. PDF text extraction confirms
  RADAR/THERMAL/MASS; all visible service notes fit their legend rows.
- The final 16 convention-note cases were rendered as `final-notes.svg/png` in
  that folder and visually reviewed without clipping or row overlap. Source
  schema tests retain strict rejection of built-in-only notes in custom files.
- The [self-contained study](SYMBOL_STUDY.md) links all three complete matrices;
  an inventory regression verifies exactly one baseline assessment for every
  built-in component. Baseline dispositions are preserved, not silently recounted.
- Long-content full-scene SVG was independently rasterized and visually checked:
  four rotated pumps, complete Unicode tags and the terminal note text remained
  visible. A3 sheet output also retained its long notes and metadata within the
  frame. Representative complete drawings supplement the exhaustive isolated
  inventory; one artificially connected full-catalog diagram is not required.
- Portable checks are recorded separately in each
  `build/packaged-check-*/verified-build.json`, including executable hash and
  sanitized-runtime checks. Only a successful record for the current executable
  establishes packaged verification; source tests alone do not.

## Final scope reconciliation

- Shaft/mount relationships are explicitly unsupported for new line creation,
  with existing links preserved for review. Legacy mnemonics have full meanings
  in the issued component legend. These are bounded drafting resolutions, not
  claims of validated mechanics or automatic ISA retagging.
- Specialized unresolved cases now use inspected source selections or concrete
  package/function abstractions. The exhaustive baseline matrices and subsequent
  resolution appendices remain the evidence; no universal conformity is claimed.
- Keep instrument function, technology, location, medium, and operating state
  separate; do not infer these from a mnemonic tag or decorative line.
- Keep the published report and full 141-type matrix synchronized with further
  resolutions, not just a statement that tests pass.
- Repeat full SVG, browser, practical-size visual, sheet export and portable
  executable checks after the final corrections. Include external tags and
  complete-sheet SVGs, not only isolated component artwork.
- The final independent review identified 16 remaining note-only cases: five
  trap subtypes; pressure/vacuum vent; drain/vent/sampling duties; off-page
  connector; generic filter; open/floating tank vent adapters; level gauge;
  density identification and I/P meaning. Each now has a concrete issued legend
  interpretation. No further confirmed symbol-shape or supported-workflow
  mismatch was found within the requested simple-drafting scope.
- Normative table certification, fluid calculations, mechanical relationship
  modeling and automatic cross-sheet connectivity are explicitly outside this
  release. Drawing-specific engineering review remains necessary before issue.
- The final portable verification record must match the delivered executable.
  See the latest successful `build/packaged-check-*/verified-build.json`; a prior
  binary's success is not substituted for the current one.
