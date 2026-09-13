# Instrumentation audit: industry alignment and actual SVG rendering

Date: 2026-09-12. Read-only production audit of all **47** built-in components whose category is `Instrumentation`, including the five Rankine instrumentation additions. This is an engineering-documentation review, not certification, a completed ISA-5.1 conformity assessment, or verification of a plant design.

Inspected `catalog_instruments.py`, `catalog_rankine.py`, `legend_instruments.py`, the built-in definitions in `pidcore.py`, and `symbol_library.draw_legend_labels`; visually inspected `build/catalog-gallery/Instrumentation.png` and actual exported SVG contact sheets `build/svg-audit-initial/sheet-10.png` through `sheet-15.png` at 0/90/180/270 degrees. Inspected the supplied Edraw chart's Instrument and Piping tables in `tmp/pdfs/industry-study/part1.png` and `part4.png`. The chart is evidence of the requested project appearance, not authority to assign operational meanings.

## Outcome

Classification of the current implementation, one primary disposition per component: **9 supported-family, 23 mismatch, 12 project-specific, 3 unresolved**. Supported-family means the basic functional family is substantiated, not that every displayed detail is correct. Several retain the shared tag-display limitation below. Mismatch includes missing functional lettering and unsupported location assumptions; it does not mean the named physical device does not exist.

The most important findings are not differences in artistic style:

1. **PT and LT acquire an unrequested location/accessibility claim.** `legend_instruments.py` hardcodes `legend_bubble='divided'` for both. The supplied chart also shows their barred examples, but does not establish that every PT/LT belongs in that location. Location must be an explicit property or a declared project convention, independent of the measured variable.
2. **Numerous distinct functions become anonymous circles in SVG.** PSH, PSL, TSH, TSL, FSL, LSH, LSL, AI, the two AT analyzer variants, DT, four controller variants, and DP variants lack appropriate internal function identification. In the app their external tags partly rescue readability; in isolated draw.io artwork those tags are intentionally suppressed.
3. **Instrument tag display has two incompatible paths.** Field bubbles display only the text before the first hyphen; divided bubbles display the remainder below. A plant tag such as `10-PT-203A` consequently becomes `10` over `PT-203A`. A tag without a hyphen is not parsed. This is a code finding, not a claim that every project requires one exact typography. Separate function/loop/area representation, preserve the full tag, and use a safe fallback for unparsed IDs.
4. **A protective well is conflated with a temperature element.** The `thermowell` label and TE prefix hide whether the drawing contains a well alone or a sensor assembly. Keep their identities distinct; do not silently rename existing saved IDs.
5. **Signal media are not modeled.** The I/P component labels current and pressure but both endpoint kinds are merely `signal`. That is insufficient to select electrical versus pneumatic connection notation. Its fixed FY prefix also assumes a flow-related function without knowing the loop context.
6. **Physical mounting is not an electrical signal.** The Rankine `mount`/`pickup` endpoints provide useful attachment handles, but categorizing them as signal ports must not imply that a surface contact or mechanical speed pickup connection is an electrical wire.

## Primary evidence and its limits

- **S1 - Current scope, not shape proof:** [ISA5.1 committee page](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa5-1), listing ANSI/ISA-5.1-2024 and the 2024 identification and graphic-symbol technical reports. It establishes the relevant standard family; its public summary does not certify these drawings or provide all current normative tables.
- **S2 - Publisher-provided actual figures:** [ISA, Control Loop Foundation, Chapter 7, Control and Field Instrumentation Documentation](https://www.isa.org/getmedia/e122051e-8c8c-48be-97ef-5d344c585771/Chapter7_ControlLoop-1.pdf), printed pp. 104-107, Figures 7-9, 7-10, 7-11. Visually inspected PDF pages 16-19. The horizontal bar carries accessibility/location information. Electrical and pneumatic signal conventions differ. Functional-letter positions matter; H is hand, S can denote switch, and T followed by C identifies temperature control. Its table lists D as user choice, although the prose beneath contains an inconsistent statement forbidding initial D. Therefore that prose is not a sound basis for rejecting DT. These are historical publisher examples, not the full 2024 standard.
- **S3 - Government training drawings:** [DOE-HDBK-1016/1-93, Engineering Symbology, Prints, and Drawings, Volume 1](https://www.energy.gov/sites/default/files/2026-04/DOE-HDBK-1016-93_VOL1.pdf), Module 2, printed pp. 10-12, Figures 9-13 (PDF pages 62-64). Visually inspected. These show local/board/behind-board forms, lettered instruments, orifice and Venturi elements, a temperature element with/without well, and I/P. Importantly, Figure 9 uses TC for thermocouple while Figure 12 uses TC for temperature controller. That historical ambiguity reinforces the need for a declared project profile. The handbook is archived training, not current normative authority.
- **S4 - Actual DOE project legend:** [Fernald project drawing collection, Revised 112452](https://lmpublicsearch.lm.doe.gov/SiteDocs/Revised%20112452.pdf), indexed drawing **92X-5900-N-00142**, Mechanical Process Piping and Instrumentation Diagram Symbols and Legend Sheet, sheet II-26. Search-index extraction identifies first-letter D as density and second-letter D as differential. This supports a documented project-specific DT convention, not a universal current rule. The full 417-page PDF was retrieved; targeted visual verification of that sheet was not completed during the initial audit.
- **S5 - Manufacturer distinction, not a P&ID glyph standard:** [WIKA, Thermowells / protection tubes](https://www.wika.com/en-us/thermowells_protection_tubes.WIKA), sections explaining the protective process boundary and removable sensor. This supports separating a well from its measuring element, not a particular proprietary outline.
- **S6 - Manufacturer hardware evidence:** [Fisher 846 I/P Transducer instruction manual, D102005X012](https://documentation.emersonprocess.com/intradoc-cgi/groups/public/documents/instruction_manuals/d102005x012.pdf), Table 3 and Figure 9, published May 2023 in the fetched text. Electrical input and pressure output are distinct. The manual does not validate the app's FY loop tag or its choice of generic dashed lines.
- **S7 - Manufacturer measurement-family evidence:** [Endress+Hauser, Coriolis flow measuring principle](https://www.endress.com/en/support-overview/learning-center/flow-measuring-principle-coriolis), Figures 2-3 and density section. Supports the physical measuring technology, not the app's zigzag glyph. [Flow and Level Instrument Verification in the Pharmaceutical Industry](https://www.us.endress.com/_storage/asset/3671095/storage/master/file/47932149/download/WP01059L24EN0117-Flow%20and%20Level%20Instrument%20Verification%20in%20the%20Pharmaceutical%20Industry-v001.pdf), Flowmeter Verification section, independently names the Coriolis, electromagnetic, ultrasonic, vortex and thermal families. Again, these are not symbol-geometry approvals.
- **S8 - Manufacturer mounting evidence:** [Emerson, Acoustic Transmitters](https://www.emerson.com/en/measurement-instrumentation/catalog/industrial-wireless-technology/acoustic-transmitters), non-intrusive installation section, identifies an external clamp-on ultrasonic sensor and separate wireless communication. Supports the distinction between mount and signal, not the UAC mnemonic or wave glyph.
- **S9 - Manufacturer sensor evidence:** [WIKA, Thermocouples](https://www-prod.wika.com/en-us/thermocouples.WIKA), overview and surface-probe discussion. Supports thermocouples as sensors and surface-mounted variants; not the app's T pictogram or a claim that TC is a universal P&ID tag.
- **E - User-supplied visual reference:** `C:/Users/jaxon/Downloads/pid-legend.pdf`, one-page EdrawSoft chart, Instrument table and Piping and Connecting Shapes table. Used as a project-specific appearance reference. No named ISA/ISO clause or symbol registration accompanies individual cells.

## Exhaustive component disposition

The evidence column points to the precise source/figure above. Repeated recommendations are our implementation assessment, not reproductions of standards tables. `SF` = supported family; `M` = mismatch requiring correction for the intended industry-oriented profile; `P` = project-specific; `U` = unresolved exact glyph.

| Component ID | Disposition | Current observation and corrective action | Evidence |
|---|---|---|---|
| `instrument` | SF | PI bubble is actually pressure-specific despite generic label. Rename the visible option or allow an explicit function; fix shared full-tag fallback. | S3 Fig. 11; E Indicator |
| `controller` | SF | Explicit panel-controller label makes its bar defensible. Retain an explicit location setting rather than inferring it from all controller types. | S3 Figs. 10-12 |
| `pressure_indicator` | SF | Readable PI field bubble; full loop identity must remain available in exports. | S3 Fig. 11 |
| `pressure_transmitter` | M | Hardcoded divided bubble adds a location claim. Default field or require location choice, with PT and loop lettering independent of the bar. | S2 Fig. 7-11; E PT example |
| `pressure_switch_high` | M | Empty bubble in SVG. Render PSH and full instance identity. | S2 Fig. 7-9; gallery |
| `pressure_switch_low` | M | Empty bubble. Render PSL; retain low-condition meaning rather than an anonymous device. | S2 Fig. 7-9; gallery |
| `temperature_indicator` | SF | TI family readable. Shared field-loop display limitation remains. | S3 Fig. 11 |
| `temperature_transmitter` | SF | TT family readable, but internal loop identity omitted. | S2 Fig. 7-5; E TT |
| `temperature_switch_high` | M | Empty bubble. Render TSH and instance identity. | S2 Fig. 7-9; gallery |
| `temperature_switch_low` | M | Empty bubble. Render TSL and instance identity. | S2 Fig. 7-9; gallery |
| `flow_indicator` | SF | FI family readable; do not imply a specific inline technology from this function alone. | S3 Fig. 11 |
| `flow_transmitter` | SF | FT family readable; technology and physical element remain separate facts. | S3 Fig. 10 |
| `flow_switch_low` | M | Empty bubble. Render FSL and instance identity. | S2 Fig. 7-9; gallery |
| `level_indicator` | SF | LI family readable. Full-loop fallback remains necessary. | S2 Fig. 7-9; E LI |
| `level_transmitter` | M | Same hardcoded location error as PT. Remove unconditional bar or expose a location property. | S2 Fig. 7-11; E LT example |
| `level_switch_high` | M | Empty bubble. Render LSH and instance identity. | S2 Fig. 7-9; gallery |
| `level_switch_low` | M | Empty bubble. Render LSL and instance identity. | S2 Fig. 7-9; gallery |
| `analysis_indicator` | M | Empty bubble while related AT receives lettering. Apply the same function-rendering path to AI. | S2 Fig. 7-9; gallery |
| `analysis_transmitter` | SF | AT readable. Identify measured analyte in a note/property, not by inventing an unrelated pictogram. | S2 Fig. 7-9; E AT |
| `ph_transmitter` | M | Empty bubble despite AT prefix; not visually identified as an analyzer in isolated SVG. Render AT and explicit pH annotation. | S2 functional identification; code |
| `conductivity_transmitter` | M | Empty AT bubble. Render function and technology/measurement annotation; allow a documented project convention rather than claiming a universal CT replacement. | S2 Fig. 7-9; code |
| `density_transmitter` | M | Blank bubble is the defect. DT itself has project precedent; document the D convention or expose profile-specific tagging, not a blanket rename. | S2 table/prose inconsistency; S4 |
| `differential_pressure_indicator` | M | Only plus/minus marks, no PDI function. Keep HP/LP port identity but move polarity outside the functional text area. | S3 Fig. 9; S2 identification; gallery |
| `differential_pressure_transmitter` | M | Same missing PDT lettering. Preserve two process taps and separate signal output. | S3 Figs. 9-10; code |
| `pressure_controller` | M | PIC is present but a panel location is assumed although label only specifies function. Offer location independently. | S2 Fig. 7-11 |
| `temperature_controller` | M | Empty barred circle; the bar rotates vertically. Render TIC and a screen-upright location marker. | S3 Fig. 12; SVG sheet 12 |
| `flow_controller` | M | Empty barred circle with rotating bar. Render FIC independently of body rotation. | S2 Fig. 7-9; SVG sheet 12 |
| `level_controller` | M | Empty barred circle with rotating bar. Render LIC and explicit location. | S3 Fig. 12; SVG sheet 12 |
| `analysis_controller` | M | Empty barred circle with rotating bar. Render AIC and explicit location. | S2 Fig. 7-9; SVG sheet 12 |
| `orifice_plate` | P | Three-stroke project/reference alternative has generic family corroboration. Retain HP/LP taps; document the chosen alternative, not universal exact geometry. | E piping Orifice Plate; S3 Fig. 9 |
| `venturi_meter` | P | Curved throat is a recognized family; nozzle closures and retained tap adaptation are app-specific. Label FE and preserve tap polarity/context. | E Venturi Meter; S3 Fig. 9 |
| `coriolis_meter` | P | Zigzag inside box follows E only. Keep as declared technology pictogram or replace with a verified profile element/function assembly. | E Coriolis Flow Sensor; S7 supports technology only |
| `magnetic_flowmeter` | P | Box with M is E's visual. M alone is not a complete instrument functional identity. Keep FT externally/within a verified function assembly. | E Magnetic; S7 family only |
| `vortex_flowmeter` | P | Triangle-in-box is E's technology pictogram. Do not advertise ISA/ISO geometry from the device label. | E Vortex Sensor; S7 family only |
| `ultrasonic_flowmeter` | P | Wave-in-box is E's pictogram. Do not confuse ultrasonic measurement technology with a sonic signal connection. | E Ultrasonic Meter; S7 family only |
| `turbine_flowmeter` | P | Figure-eight glyph matches E. Exact industry-standard basis not established. Retain only with project legend. | E Turbine Meter |
| `rotameter` | P | Circle-and-triangle follows E but differs from DOE's rectangular float example. Both require chosen project semantics; no universal match claim. | E Rotometer; S3 Fig. 9 |
| `thermal_mass_flowmeter` | U | Two hanging probes are original illustration, not a verified P&ID symbol here. Retain labeled illustration pending an exact profile source or use generic FT with technology note. | S7 validates device family, not glyph |
| `thermowell` | M | TE, protective pocket, and combined label conflate distinct items. Separate well from sensor/assembly without mutating existing IDs. | S3 Fig. 9; S5 |
| `level_gauge` | P | Two-tap glass illustration conveys physical arrangement; current internal T-like stroke is not a substantiated function mark. Keep as declared sight-glass pictogram with LG identity. | Code/gallery; S2 G viewing-device family |
| `radar_level_transmitter` | U | Circle with chevron lacks verified reference basis and LT inside. Technology exists, exact glyph unresolved. Prefer LT plus radar note until sourced. | S8-related manufacturer non-intrusive discussion; code |
| `current_pressure_converter` | P | I/P family supported, but fixed FY and generic signal media are project assumptions. Slash crosses letters at quarter-turn rotations; correct composition. | S3 Fig. 13; S6; E Transducer |
| `inline_flowmeter` | P | FM and geometric F are mnemonic/project-specific; F rotates sideways. Prefer a declared FI/FT/FE function once known, preserving existing tags. | Code; S2 functional-identification principle |
| `acoustic_sensor` | P | Wave bubble/UAC are bespoke. Keep as explicit surface sensor; distinguish mounting link from actual output signal. | S8; code |
| `hall_speed_sensor` | U | H rectangle and EHS mnemonic do not establish a P&ID speed function. Exact technology symbol unsourced; use an explicit speed-function profile plus Hall note. | S2 Fig. 7-9 speed family; code |
| `humidity_sensor` | M | HS is ambiguous with a hand switch, blank barred bubble suggests unsupported location, and bar rotates. Require declared humidity convention and remove accidental location cue. | S2 Fig. 7-9; code |
| `thermocouple` | M | Geometric T rotates; TC conflicts with temperature-control reading in a functional profile. DOE also uses TC historically, so label the profile; prefer a temperature-element function plus surface/thermocouple note for the ISA-oriented mode. | S3 Figs. 9 and 12; S9 |

## SVG-specific verification findings

These findings are from the actual exported SVG contact sheets, not only source inspection:

- Sheet 12: TIC/FIC/LIC/AIC horizontal bars turn vertical at 90/270 degrees. PIC is rendered by another path and stays horizontal. This inconsistency changes the symbol's readable semantics.
- Sheet 14: the I/P slash is rotated with the body, but I and P remain at fixed upper-left/lower-right positions. At 90/270 degrees the slash passes through the letters. Keep slash and labels in a consistent upright annotation layer, or rotate their positions together while keeping glyphs readable.
- Sheets 14-15: inline-flowmeter F, Hall-sensor H, and thermocouple T are strokes inside artwork, not text, so they rotate sideways/upside-down. If retained as letters, render them upright; if retained as pictograms, explicitly define their meaning in the project legend.
- Sheets 10-12: missing internal labels are faithfully reproduced by SVG. Passing raster-equality tests cannot certify that source content is semantically complete.
- All inspected component outlines, leads and already-enabled letter glyphs appear present; no obvious SVG clipping or dropped primitive was visible in these sheets. This is visual evidence for this fixture only, not a universal renderer guarantee or independent browser verification.

## Recommended implementation boundary

Keep existing component IDs, named ports and saved tags stable. Add a declarative instrumentation display model shared by every built-in function: function text, complete instance identity, location/accessibility, and optional technology annotation. Derive none of those from an arbitrary hyphen position or a sample drawing's loop number. Add project-profile options instead of making the Edraw examples the sole industry truth.

For the minimal safe correction, remove unsupported PT/LT bars, fill all missing function text, keep text and location graphics upright, fix I/P composition, distinguish thermowell labeling, and explicitly mark unresolved technology glyphs/project mnemonics. Full standards alignment additionally needs connection media and installation semantics; it cannot be achieved by changing outlines alone. No production files were modified in this audit.

## Resolution append - instrument display implementation, 2026-09-12

The preceding 47-row matrix is the **baseline audit**, not a current defect count. Following that read-only audit, the authorized minimal display correction was implemented in `legend_instruments.py`, `instrument_display.py`, and `symbol_library.draw_legend_labels`.

Resolved in this pass:

- All 30 generic instrument bubbles now show their declared functional prefix and an instance-identity line. This includes the previously blank switch, analyzer, density, DP, controller and humidity bubbles.
- PT, LT, function-only controllers, and humidity no longer acquire an unsupported location bar. Only the explicitly labeled legacy Panel controller retains its bar. No new location property or formal standards profile is claimed.
- Simple tags such as PT-203 and PT203A display PT above 203 or 203A. Compound and arbitrary tags are retained verbatim on the lower line, with the declared component function above; area/suffix information is not discarded. Text is width-fitted rather than truncated. Extremely long arbitrary tags necessarily become small; the original saved/external tag remains unchanged.
- DP component H/L marks remain adjacent to the existing named taps, outside the central function text. Port IDs, positions and signal/process kinds are unchanged.
- The main agent's I/P upright slash and Rankine F/H/T upright text corrections are preserved. Non-panel controller bars are removed rather than merely rotated upright.
- Five new tests cover tag fallback, every bubble in four SVG rotations, location-bar policy, document nonmutation, and retained orientation fixes. Together with the six earlier reference tests, all 11 focused tests pass.

Still unresolved by this display-only pass: thermowell versus temperature-element identity, project-specific TC/HS/FM/UAC/EHS/DT conventions, unsupported technology glyphs, meaningful mount versus signal semantics, electrical/pneumatic signal media, configurable location/accessibility, and full normative-profile validation. These require explicit modeling/profile decisions, not speculative renaming of existing components. Custom definition schemas and saved component identities/tags were not changed.

## Resolution append - temperature element in protective well, 2026-09-12

The legacy `thermowell` component is now explicitly labeled **Temperature element in thermowell (assembly)**, retaining type ID `thermowell`, prefix TE, existing saved tags, both named ports, their positions/kinds, and the original routing envelope. This resolves the earlier ambiguity by identifying the modeled object as the combined sensing assembly rather than falsely equating a bare well with a sensor. Existing records are not retagged to TW.

Evidence for that interpretation is the actual DOE Figure 9 temperature-element-with-well example (S3), considered alongside [WIKA data sheet TW 90.11, January 2026, page 1](https://shop.wika.com/media/Data-sheets/Temperature/Thermowells/ds_tw9011_en_co.pdf). The manufacturer's description distinguishes the process-isolating protective tube from the thermometer it accommodates. That evidence supports the assembly's physical distinction; it is not evidence that the app's detailed pocket outline is a registered ISA/ISO glyph.

The corrected artwork shows a closed outer protective pocket and a separate internal sensing stem/tip. The stem connects to the existing `sensor` attachment and stops inside the pocket, before the closed end. The `process` lead begins at the exterior end instead of entering the pocket interior. It remains a schematic process association, not an open fluid conduit through the sensor. No particular sensor technology, transmitter electronics, construction rating or thermowell calculation is implied.

Four new tests verify legacy identity/port contracts, separate sensor and pocket geometry, unchanged file/connection round-trip, and all-four-rotation SVG fidelity/clipping and clear outward stubs. All four pass. The generated four-rotation rendering `build/thermowell-assembly.png` was visually inspected: the internal tip remains separate from the protective boundary in each rotation. Bare-well-only inventory and detailed mechanical installation modeling remain outside this combined component's scope.

## Final note-only closeout, 2026-09-12

DT is explicitly adopted as density transmitter in this project's vocabulary,
not claimed as a universal letter assignment. I/P identifies current input and
pressure output; retained FY does not establish a flow loop or medium-specific
line notation. The level-gauge internal mark is explicitly a sight-glass/liquid
region illustration, not a T function or control setpoint. These meanings are
included in the issued legend; no new geometry or automatic retagging was needed.

## Resolution append - legacy identifiers and attachment constraints, 2026-09-12

Issued legends and component tooltips now explicitly define HS as humidity sensing,
TC as surface thermocouple, FM as unspecified inline flow measurement, UAC as
surface acoustic measurement and EHS as Hall rotational speed sensing. They are
retained project mnemonics, not automatic ISA functional assignments. Existing
tags remain unchanged; hand switching, temperature control and invented output
signals are not inferred from these letters.

Shaft/mount/pickup handles are visibly illustrative and cannot accept new line
connections in canvas gestures, connection dialogs, reconnection or proposal
acceptance. Drawing notes describe physical associations until such relationships
are modeled. Existing legacy endpoint pairs remain editable/saveable/undoable
and flagged for review, not silently removed or reclassified. This closes the
supported-workflow ambiguity without claiming physical installation validation.

## Resolution append - radar and thermal mass functional assemblies, 2026-09-12

Implemented the recommendations in `research/SPECIALIZED_INSTRUMENT_FOLLOWUP.md` after primary drawing inspection. `radar_level_transmitter` now uses a radius-20 field-function circle with LT, instance identity and RADAR. `thermal_mass_flowmeter` uses a radius-23 field-function circle with FT, instance identity, THERMAL and MASS on separate short lines. The thermal component is an integrated measurement-assembly abstraction, not a claim to reproduce the source's separate element/function glyph exactly; no FIT retagging or indication function was added.

Both changes preserve component IDs, saved tags, all named process/signal ports and their positions/kinds, and existing routing bounds. Radial leads terminate at the field circle. Technology captions and instance text stay upright in every rotation and lie inside the circle, not across the connection leads or beyond the SVG viewport. Only these two built-ins use the new layout; ordinary generic bubbles keep their existing two-line rendering. Built-in-only `instrument_technology` layout metadata does not expand the custom definition schema.

Provenance uses `symbol_reference`: City of Sandy / Stantec I-006, PDF page 33, for LT plus RADAR, and DOE-hosted OSTI 2472813 page 33, Exhibits 3.2.2-3.2.3, for thermal mass functional identification. The prior radar chevron and invented hanging thermal probes are no longer used. These references substantiate the function/technology interpretation, not universal exact artwork conformity.

Four new specialized tests cover retained contracts, caption boxes within the circle, simple and long compound IDs in actual SVG at four rotations, nonmutation, and rejection of built-in layout metadata in custom definitions. All four pass; the combined specialized/display/reference set passes 15 tests. `build/specialized-instruments.png`, rendered with the application's Segoe UI font setup, was visually inspected: LT/FT, normal loop numbers and all technology words are legible and upright without crossing leads or borders. Arbitrarily long identity strings remain complete but are necessarily width-fitted; the saved/external tag is unchanged.
