# P&ID component symbol study

## Executive assessment

The 141-component library has been reviewed against the supplied reference and
additional industry evidence. The exhaustive baseline review identified 63 supported
symbol families, 34 mismatches, 37 project-specific representations, and seven
unresolved cases. These classifications describe engineering meaning as well as
appearance; subsequent resolutions are recorded below and in each appendix.
A valid SVG alone does not establish correct symbology or normative certification.

The supplied Edrawsoft legend is a useful project reference, but it is not a
normative ISA or ISO publication. Eighty-one definitions identify a selected
entry from that chart. Some preserve existing connection points through adapted
leads. The remaining definitions must not be described as chart matches merely
because they depict familiar equipment.[^1]

Two separate acceptance questions are necessary. First, does the drawing use an
explicit, defensible convention for each component and connection? Second, do
the editor and exports reproduce that convention without omissions, collisions,
or clipping? The adopted source/family/package conventions address the first;
exhaustive rotation checks and representative sheet exports address the second.
Neither is a blanket claim that all symbols universally satisfy all standards.

## Inventory and scope

| Component group | Types | Supported family | Mismatch | Project-specific | Unresolved |
|---|---:|---:|---:|---:|---:|
| Process equipment | 45 | 22 | 7 | 15 | 1 |
| Valves, piping, protection and steam | 49 | 32 | 4 | 10 | 3 |
| Instruments and related sensors | 47 | 9 | 23 | 12 | 3 |
| Total | 141 | 63 | 34 | 37 | 7 |

These are baseline dispositions, not a count of remaining defects after each
correction. A supported family can still have a rendering defect, an ambiguous
installation detail, or a project-dependent variant. Resolution records in the
appendices identify subsequent changes without erasing the baseline evidence.

The complete, disjoint component matrices are:

- [Process equipment: 45 individual assessments](process-audit.md).
- [Valves, piping, protection and steam: 49 individual assessments](valves-audit.md).
- [Instrumentation: 47 individual assessments](instruments-audit.md).

The assessment covers built-in component geometry, functional lettering,
attachment geometry, routing envelopes, rotation and exported SVGs. It does not
certify process safety, sizing, pressure ratings, material suitability, fluid
calculations, or construction readiness. Custom component definitions require
their own engineering review; one custom fixture is included only to exercise
the common renderer.

## Standards and evidence hierarchy

ANSI/ISA-5.1-2024 is the instrumentation and control identification standard
currently listed by ISA. Public ISA teaching material provides inspectable
examples of functional identification and instrument location/accessibility.
Those examples are useful evidence, but they do not substitute for a clause-by-
clause assessment against the full current normative tables.[^2][^3]

ISO 10628-2:2012 remains current and was confirmed in 2024. Its scope addresses
graphical symbols for chemical and petrochemical diagrams. ISO 14617-2:2025
provides a consolidated industrial symbol library, while ISO 14617-1:2025 gives
general preparation and presentation rules. The consolidation of older ISO
14617 parts does not make ISA-5.1 or ISO 10628-2 obsolete. The ISO catalogue pages
establish edition and scope, not the exact geometry of every symbol.[^4][^5][^6]

DOE-HDBK-1016/1-93 supplies publicly inspectable historical training figures for
valves, piping, instruments and equipment. It is archived material, not a current
universal design mandate. VA standard-detail sheets are valuable examples of
actual government project conventions. Manufacturer publications establish
device function and physical arrangements; a cutaway of a device is not, by
itself, evidence that a miniature cutaway is its standardized P&ID symbol.[^7][^8][^9]

The appropriate order of authority for an issued drawing is its contractual
drawing specification and adopted standards, followed by its approved project
legend. Generic charts and teaching material help interpret and compare those
choices; they should not silently override them. This is an assessment
recommendation, not a claim that one project legend governs all industries.

## Conflicting conventions

### Valve variants

The supplied chart and the VA valve sheet do not assign every similar-looking
glyph to the same valve family. A hollow circle within a bow-tie body is a
particularly important example: the chart's ball-valve representation cannot be
treated as a universal interpretation when another published project legend
uses a comparable form for a globe valve. Retaining a selected variant is
reasonable only when the drawing's legend identifies it.[^1][^8]

Relief devices also have multiple arrangements. Historical DOE figures include
alternatives that prevent a simple rule that every inline relief representation
is incorrect. The baseline spring/arrow composition lacked specific corroboration.
It has now been replaced by DOE Figure 1's middle inline alternative, preserving
the saved horizontal ports. This is a selected historical convention, not a
claim that every relief device must use this glyph.[^7]

Steam-trap installation sets should not be mistaken for individual trap symbols.
A manufacturer schematic can substantiate the operation of a float, bucket or
thermostatic mechanism without proving that the app's mechanism illustration is
an established P&ID glyph. The valve appendix retains this distinction.

### Instrument identity and location

A horizontal line inside an instrument bubble communicates location or
operator-accessibility information in the inspected ISA teaching convention.
It is not merely a visual separator between letters and a loop number. The
baseline PT and LT definitions therefore overstate installation information by
hardcoding bars from sample chart entries. Function and location must be
independent decisions.[^3]

Instrument function, loop identity, measurement technology and location are
different facts. A pressure transmitter does not become panel-mounted because
its function is PT. A generic FT does not identify Coriolis, magnetic or ultrasonic
technology. Conversely, a technology pictogram does not supply a complete
functional instrument identity.

Arbitrary saved tags must not be split at the first hyphen and then presented as
unambiguous functional identification. Area-prefixed tags such as `10-PT-203A`
and free-form labels require a documented parsing convention or a lossless
fallback. Display corrections must preserve the saved tag and component ID.

The letters TC and DT demonstrate why automatic renaming is unsafe. DOE uses TC
in a historical thermocouple example and also in a controller context; D has
project-dependent uses. The appropriate correction is explicit interpretation
and complete identification, not an unsupported blanket declaration that these
letters can never be used.[^7]

### Physical connections and other relationships

A process nozzle, electrical signal, pneumatic signal, shaft coupling and sensor
mount are not interchangeable relationships. The current two-kind process/signal
model cannot fully express those distinctions. In particular, a shaft or mounting
attachment represented by the generic signal kind needs a separate model and
migration decision before the software can make stronger semantic claims.

The geometry review can correct a detached lead without inventing a new service.
It cannot infer flow direction, signal medium, actuator failure position or a
thermal circuit from a suggestive silhouette. Existing attachment names and
coordinates are therefore preserved during the geometry corrections.

## Engineering findings

The process appendix identifies detached vent indications, undersized pump
routing envelopes, a turbine outlet gap and questionable subtype depictions.
It also separates previously repaired exchanger connections from remaining
project adaptations. An exchanger's recognizable outer shape is insufficient
if its process and utility paths imply an unintended intersection.

The valve appendix identifies detached regulator sensing paths, an ambiguous
cross-junction marker and a foot-valve gap. It distinguishes upstream and
downstream regulator sensing; joining a line to the wrong side would be a
semantic error even if the drawing looked tidier.

The instrument appendix identifies anonymous bubbles, incomplete loop
identification, unsupported location bars and several technology illustrations
without exact symbol evidence. It also flags the conflation of a thermowell with
a sensing element. These findings require more than cosmetic resemblance to a
catalogue picture.

## SVG and rotation evidence

The repeatable component audit exports every built-in definition and one custom
fixture at 0, 90, 180 and 270 degrees: 568 cases. Each actual SVG is checked for
valid XML, valid Qt SVG rendering, nonempty ink and external-resource references.
Its rendered ink is compared against the direct editor painter with a one-pixel
tolerance; a larger direct-render viewport tests for artwork outside the export
boundary. Per-case hashes and measured differences are retained with the SVGs.

The initial 568 cases passed the mechanical checks, and all 568 images loaded in
a browser. Nevertheless, visual review found real source-composition defects:
the motor actuator's M became W at 180 degrees; the I/P divider crossed its
letters at quarter turns; controller bars changed orientation; and several
sensor letters turned sideways. These are examples of why successful loading
and editor/export agreement are necessary but not sufficient.

The readability corrections place letters and semantic annotation strokes in an
upright layer. Actuator lettering follows its rotated actuator position while
remaining readable. The corrected orientation checkpoint also passed all 568
mechanical cases. Later engineering changes require another full run; an older
pass must not be presented as validation of a newer executable.

The isolated-component test deliberately excludes external tags. Complete-scene
tests additionally need labels, notes, routed connections, sheet framing and
practical print sizes. Small-font legibility, extreme user tags, font substitution
and other SVG consumers remain distinct concerns. Test coverage and visual
evidence should be reported with their fixture and version, not as a guarantee
for every possible drawing.

## Release acceptance

The drawing-specific SVG legend is available under Reports > Component legend.
It includes each used component type once, renders the same artwork as the editor,
identifies the selected reference entry where recorded, and retains independent
drawing and component-library fingerprints. It is a companion artifact, not automatically appended to sheet
exports. Issuing the matching legend makes the chosen variants explicit, but
does not certify unresolved symbols merely by displaying them.

Subsequent corrections replace the blower's propeller-like illustration with a
centrifugal scroll-casing convention corroborated by DOE Figure 15 and the supplied
chart. The thermowell component now explicitly represents a temperature element
inside a protective well, with distinct sensing and pocket geometry; its exact
adaptation and physical source are recorded in the instrument appendix.

The foot-valve body now follows an inspected IXOM project-legend orientation,
composed with the retained strainer. Its provenance explicitly identifies that
composition rather than claiming the source depicts the full assembly. The
[valve-direction follow-up](VALVE_DIRECTION_FOLLOWUP.md) records the primary
drawings, alternative conventions, and limits. These primary-source selections
are recorded separately from matches to the supplied chart.

The minimum defensible release retains an explicit project convention, stable
saved drawings, continuous attachment geometry and readable instrument identity.
Every confirmed mismatch needs a recorded resolution or an explicit remaining
limitation. Project-specific and unresolved representations must not acquire a
standards claim merely by being renamed or marked custom.

A stronger standards-aligned release requires a selected normative profile and
access to its exact applicable tables; explicit location and relationship
semantics; and a drawing legend covering selected variants. It also requires
regression tests proving the built application matches the reviewed source.
No standards have been purchased and no inaccessible tables are claimed to have
been verified.

The latest reference pass also resolves radar/thermal identity, knife-gate
appearance and atmospheric-admission direction. Concrete legend notes define
composite service circuits and legacy mnemonic meanings. Unsubstantiated
separator internals were replaced by named generic equipment packages. Physical
attachment handles are explicitly unsupported for new line creation; existing
legacy links remain preserved with review warnings. This is a deliberately bounded
drafting workflow, not a new mechanical model or silent document migration.

The resulting disposition is **reviewed project drafting conventions**, not
universal standards certification. The final note pass also explicitly defines
bare steam-trap subtypes, manual valve duties, tank venting, graphical off-page
continuation, filter/sight-glass illustrations, retained DT identification and
I/P port meanings. No sizing, operating state or automated cross-sheet network
is inferred from these drawings.
[The resolution ledger](STUDY_STATUS.md) records verification evidence, and each
appendix retains the evidence for individual components. This is preferable to
a single unqualified assertion that the entire library matches industry.

## Sources

[^1]: Edrawsoft, *Standard P&ID Symbols Legend*, supplied single-page `pid-legend.pdf`; publication date not stated. Local source: `C:/Users/jaxon/Downloads/pid-legend.pdf`. SHA256: `21fe90dfd45c57a1c1ba141a31999ede51b9b6ca247b7399bc35fff7bb234b40`. Equipment, valve, piping and instrument tables; selected variants documented in the appendices.
[^2]: International Society of Automation, [ISA5 committee and standards listing](https://www.isa.org/standards-and-publications/isa-standards/isa-5-standard), listing ANSI/ISA-5.1-2024. Edition/scope evidence, not full normative-table access.
[^3]: International Society of Automation, [*Control Loop Foundation*, Chapter 7: Control and Field Instrumentation Documentation](https://www.isa.org/getmedia/e122051e-8c8c-48be-97ef-5d344c585771/Chapter7_ControlLoop-1.pdf), especially Figures 7-9 and 7-11; Figure 7-11 appears on printed page 107. Public teaching excerpt, not a claim to reproduce the 2024 normative tables.
[^4]: International Organization for Standardization, [ISO 10628-2:2012](https://www.iso.org/standard/51841.html), *Diagrams for the chemical and petrochemical industry — Part 2: Graphical symbols*. Official catalogue; confirmed 2024.
[^5]: International Organization for Standardization, [ISO 14617-2:2025](https://www.iso.org/standard/83364.html), *Graphical symbols for diagrams — Part 2: Graphical symbols*. Official catalogue, scope and lifecycle.
[^6]: International Organization for Standardization, [ISO 14617-1:2025](https://www.iso.org/standard/85641.html), *Graphical symbols for diagrams — Part 1: General rules*. Official catalogue.
[^7]: U.S. Department of Energy, [DOE-HDBK-1016/1-93 catalogue](https://www.energy.gov/ehss/articles/doe-hdbk-10161-93) and [Volume 1 PDF](https://www.energy.gov/sites/default/files/2026-04/DOE-HDBK-1016-93_VOL1.pdf), 1993, archived. Module 2, Figures 1-2, 7-13 and 15. Exact figure applications appear in the component appendices.
[^8]: U.S. Department of Veterans Affairs, [SD230511-17, Valve Symbols](https://www.cfm.va.gov/til/sDetail/Div23HVACSteam/SD230511-17.pdf), November 1, 2017. Project/detail convention, not universal valve taxonomy.
[^9]: U.S. Department of Veterans Affairs, [SD230511-16, General Piping Symbols](https://www.cfm.va.gov/til/sDetail/Div23HVACSteam/SD230511-16.pdf), November 1, 2017. Further exact manufacturer publications and equipment-function evidence are cited in the three appendices.
