# Radar level and thermal mass flow: primary drawing follow-up

2026-09-12. Research and recommendation only; no production files changed. This follow-up distinguishes actual P&ID evidence from manufacturer device illustrations. Both retrieved primary documents below contain inspectable process drawings, not merely product labels or cutaways.

## Verified primary drawing evidence

### Radar: municipal project drawing, explicit LT plus RADAR note

[City of Sandy, Alder Creek WTP Upgrade Conceptual Design Report, Attachment A](https://www.ci.sandy.or.us/sites/default/files/fileattachments/public_works/page/22679/attachment_a_-_alder_creek_wtp_upgrade_conceptual_design_report.pdf), PDF page **33**, drawing **I-006**, “Filtration Building Chemical Feed - Sodium Hypochlorite,” Stantec, project **2002006267**. Retrieved locally as `tmp/pdfs/industry-study/sandy-radar.pdf`; rendered and visually inspected `radar-page-33.png`.

At the left, above tank T-5401, the drawing shows a circular **LT / 5401** function identifier and an adjacent **RADAR** annotation. It also depicts a connection toward the tank and a separate dashed connection to LI-5401. This directly supports identifying radar measurement by a generic level-transmitter function plus technology note. It does not require the app's unlettered chevron glyph.

The drawing is prominently **DRAFT / PRELIMINARY / NOT FOR CONSTRUCTION**. It is primary evidence of how that engineering project documented radar, not a normative ISA/ISO symbol registration or evidence that the plant was built this way. Do not infer guided-wave versus non-contact radar from the word alone.

### Thermal mass: DOE-hosted research P&ID plus cross-referenced instrument list

[Ash Fouling Free Regenerative Air Preheater for Deep Cyclic Operation](https://www.osti.gov/servlets/purl/2472813), PDF/printed page **33**, **Exhibit 3.2.2, Piping & Instrumentation Diagram**, and **Exhibit 3.2.3, The Instrument List**. Retrieved locally as `tmp/pdfs/industry-study/osti-thermal.pdf`; rendered and visually inspected `thermal-page-33.png`.

The instrument list identifies **FIT-201** as a thermal mass flowmeter, Endress+Hauser T-mass I 300. The P&ID identifies that function by a circular FIT-201 bubble associated with a separate element on the air line. This substantiates a functional identifier plus identified thermal technology. It does **not** substantiate the app's original two-hanging-probe pictogram as standard P&ID geometry.

The example includes indication, so its tag is FIT rather than FT. Do not change the app's saved FT tags to FIT: indication is an additional function which the current component did not promise. The instrument list also uses other simplified project labels, reinforcing that this report is a project example, not a normative letter table.

## Current app contracts to preserve

| Component | Existing process side | Existing signal side | Existing bounds |
|---|---|---|---|
| `radar_level_transmitter` | `process: [0,40]` | `signal: [0,-40]` | `[-20,-24,20,30]` |
| `thermal_mass_flowmeter` | `inlet: [-40,0]`, `outlet: [40,0]` | `signal: [0,-40]` | `[-25,-24,25,24]` |

Keep type IDs, prefix LT/FT, all instance tags, endpoint names/positions/kinds, and saved connections. Radar's process port is a measurement association, not an inlet/outlet fluid passage. The thermal component's two process ports represent the existing inline measurement assembly, not two electrical outputs. Replacing it with a one-process-port FT would lose actual drawing topology.

## Recommended representation

**Yes: generic functional identification plus explicit technology is justified.** No source inspected establishes the current chevron or hanging-probe details as the required industry symbol. The defensible simplification is a clearly identified functional assembly, while retaining its existing topology and documenting the level of abstraction.

### Radar - recommended minimum geometry

- Replace the unlettered offset circle/chevron with a field-function circle centered at `(0,0)`, radius **20**: ellipse `[-20,-20,40,40]`.
- Preserve the process lead `(0,20)` to `(0,40)` and signal lead `(0,-40)` to `(0,-20)`.
- Keep the outline within existing bounds; no port or routing-envelope migration needed.
- Render **LT**, full instance identity, and **RADAR** as screen-upright text, without a location bar. Do not add an antenna/radiation arrow that would assert a specific measurement technology subtype or signal convention.
- State that the existing process-side connector associates the instrument with its measured equipment. Whether the installation is contact/non-contact, guided wave, or external/non-intrusive remains a property or drawing note, not an inferred fact.

### Thermal mass - safe minimal functional assembly

- Replace the unsupported hanging-probe pictogram with a field-function circle centered at `(0,0)`, radius **23**: ellipse `[-23,-23,46,46]`.
- Preserve process leads `(-40,0)` to `(-23,0)` and `(23,0)` to `(40,0)`, and signal lead `(0,-40)` to `(0,-23)`.
- Keep the original bounds `[-25,-24,25,24]` as a conservative envelope. No ports are added or removed.
- Render **FT**, full instance identity, and **THERMAL MASS** as upright text. Do not silently claim a local indicator, so do not default to FIT.
- Explicitly describe this as an **integrated measurement assembly/function**, not an exact reproduction of Exhibit 3.2.2. That source separates primary element and function bubble; the app's retained two-port component aggregates them. A circle with two process connections is the app's functional abstraction, not a proven normative thermal-flow element glyph.

### More literal thermal alternative, if exact element/function separation is desired

Keep a generic inline primary element at the horizontal process path and place a separate FT bubble above it, joined by a short association. Within the current 100-unit SVG viewport, a feasible starting geometry is a 10-by-10 element box centered at `(0,0)`, process leads from the existing ports to `x=+-5`, and a radius-12 function bubble centered at `(0,-25)`, connected from its bottom at `y=-13` to the element top at `y=-5`. The signal lead runs from `(0,-40)` to the bubble top at `(0,-37)`.

This more literal layout requires a new bubble-center/radius display capability, smaller fitted text, and an expanded top routing envelope of at least `-37`. All four rotations need a new obstacle/contact review. The source supports the separation pattern, not that exact generic box or those app coordinates. It is more invasive and may be less readable at the app's compact scale. Do not implement it as if it were a free outline-only substitution.

## Technology caption layout: avoid a new rendering defect

The current generic label renderer has two lines and assumes a radius-23 bubble. Do not draw an extra caption across the process lead or outside the fixed draw.io `[-50,50]` viewport without changing its geometry normalization.

For the minimal circle proposals, add a controlled three-line bubble-text layout:

| Text row | Suggested box for radius 23 | Text role |
|---|---|---|
| Upper | `[-18,-18,36,12]` | LT or FT, about 10 px |
| Middle | `[-20,-6,40,12]` | Complete instance identity via existing lossless fallback, about 9 px |
| Lower | `[-17,6,34,12]` | RADAR or THERMAL MASS, about 7 px, width-fitted |

For radius 20, reduce widths to the local circle chord and use 9/8/7 px text. Treat these as **layout starting points**, requiring visual verification at actual use scale; long arbitrary IDs and THERMAL MASS may become small. If captions are not legible, use a larger component/export envelope or explicit adjacent note rather than truncating technology or hiding port leads. Do not claim that three-line text layout is prescribed by a standard.

## Required verification before implementation acceptance

1. Saved LT/FT records and all old connections round-trip without retagging, endpoint renaming, or process-port loss.
2. Technology text survives PNG/PDF/SVG/draw.io, including isolated embedded SVG where external tags are intentionally hidden.
3. All four rotations keep functional text upright and process/signal leads attached; every original port retains a clear outward route.
4. Pixel comparison to actual SVG plus expanded-viewport clipping checks pass, followed by human-readable visual review at normal component scale.
5. Long/compound tags remain complete; no caption overlaps a lead, circle border, or full external tag. Custom component schema remains unchanged.
6. Provenance wording identifies the radar example and thermal functional-assembly abstraction separately; it must not turn either project drawing into an ISA/ISO exact-shape claim.

No production implementation was made in this follow-up. The strongest result is the radar LT-plus-RADAR precedent. The thermal source supports functional abstraction and primary-element separation, but not a universal exact thermal meter glyph.
