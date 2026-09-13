# Valve, piping, pressure-protection and steam-trap symbol audit

Audit date: 2026-09-12. Read-only production review; no production files changed.

## Scope and verdict

The authoritative `pidcore.CATALOG` contains 49 components in the four assigned categories: 25 Valves & Actuators, 15 Piping & Connections, four Pressure Protection, and five Steam & Condensate. None of the eight Rankine additions belongs to these categories. This audit inspected the current rendered gallery, not the pre-reference artwork: `build/catalog-gallery/Valves and Actuators.png`, `Piping and Connections.png`, `Pressure Protection.png`, and `Steam and Condensate.png`; then checked `pidcore.py`, `catalog_valves.py`, `legend_valves.py`, `symbol_art.py`, and the line renderer in `app.py`.

| Individual result | Count | Meaning |
|---|---:|---|
| Supported family | 32 | Recognizable match to an inspected named symbol or alternative; not a certification claim. Some have only the user-selected Edraw reference. |
| Mismatch | 4 | Demonstrable graphical/semantic inconsistency described below, not merely absence from a reference. |
| Project-specific | 10 | Understandable local convention or duty-specific composition requiring the project legend. |
| Unresolved | 3 | Exact intended symbol is not substantiated by the inspected evidence. This is not proof that no valid convention exists. |
| Total | 49 | Every assigned component appears once below. |

The 29 recent reference overlays improved consistency with the supplied legend, but that does not establish universal industry validity. A particularly important conflict: the hollow circle on a bow-tie used here for **ball valve** is also used for **globe valve** in the VA sheet. The selected project legend must therefore travel with the drawing.

## Evidence register

All figure and cell references below refer to these exact sources. Sources were inspected visually where used for artwork support.

- **E**: User-supplied `C:/Users/jaxon/Downloads/pid-legend.pdf`, one tall page, titled *Standard P&ID Symbols Legend | Industry Standardized P&ID Symbols*, with Edrawsoft footer. Relevant sections: Valves; Peripheral; Piping and Connecting Shapes. Inspected source renders `tmp/pdfs/legend/part1.png` and `part4.png`. This is the requested house reference, not the text of ISA/ISO. The advertised title alone is not evidence of normative compliance. An online copy is [Standard P&ID Symbols Legend](https://blog.projectmaterials.com/wp-content/uploads/2016/06/Pid-symbols-PDF.pdf); the local supplied file, not an assumed online identity, controls this comparison.
- **D1/D2/D7/D8**: U.S. Department of Energy, [DOE Fundamentals Handbook, Engineering Symbology, Prints, and Drawings, Volume 1, DOE-HDBK-1016/1-93](https://www.energy.gov/sites/default/files/2026-04/DOE-HDBK-1016-93_VOL1.pdf), January 1993, Module PR-02. Figure 1 *Valve Symbols*, printed page 3/PDF page 55; Figure 2 *Valve Actuator Symbols*, printed page 4/PDF page 56; Figure 7 *Piping Symbols*, printed page 7/PDF page 59; Figure 8 *More Piping Symbols*, printed page 8/PDF page 60. All four figures visually inspected from local renders. This is authoritative government training material showing alternatives, not a claim to cover every current plant convention.
- **V17**: U.S. Department of Veterans Affairs, [Valve Symbols, SD230511-17](https://www.cfm.va.gov/til/sDetail/Div23HVACSteam/SD230511-17.pdf), sheet dated 11/01/2017, one page. Visually inspected complete sheet after direct download (`tmp/pdfs/industry-study/va-valve-symbols.pdf`). Row labels cited below are exact locating references. A government HVAC/steam project convention, not a universal process-industry symbol mandate.
- **V16**: U.S. Department of Veterans Affairs, [General Symbols / General Piping Symbols, SD230511-16](https://www.cfm.va.gov/til/sDetail/Div23HVACSteam/SD230511-16.pdf), sheet dated 11/01/2017, one page. Visually inspected complete sheet (`tmp/pdfs/industry-study/va-general-symbols.pdf`). Its steam-trap symbols denote **trap sets including piping accessories**, not bare individual traps; this distinction prevents false matching.
- **F**: Emerson, [Sizing Differential Pressure Regulators in Seal Oil Service for Turbomachinery, D352289X012](https://www.emerson.com/is/content/emerson/en/final-control/pressure-management/regulators/fisher/others/documents/d352289x012-prm-wtp-sizing-differential-pressure-regulators-in-seal-oil-service-for-turbomachinery.pdf), September 2015. Page 1, Figure 1 *Essential Elements of a Standard Pressure Controlling Regulator* and pages 2-3 forward/backpressure discussion. Used only for sensing-side semantics: reducing senses downstream; backpressure senses upstream. It does not validate our spring-and-bow-tie artwork.
- **I**: ISO, [ISO 10628-2:2012, Diagrams for the chemical and petrochemical industry - Part 2: Graphical symbols](https://www.iso.org/standard/51841.html). The official catalogue states that it applies the ISO 14617 series and was confirmed in 2024. Full symbol tables were not acquired, so **no individual component here is declared ISO-conformant** on this source's strength.

Additional searches covered Assured Automation's P&ID desk reference, Vista Projects' engineering symbol library, and Spirax Sarco material. Assured Automation's own site returned an access block; no attempt was made to bypass it. Vista's parsed page labels were insufficient to establish additional valve geometry, and Spirax product/cutaway material was not promoted to P&ID-symbol evidence. Those searches therefore do not inflate the supported count.

## Exhaustive component table

Port directions in this table describe intended function inferred from the catalogue names and artwork. The current schema records only process versus signal, not an enforced input/output direction, operating state, or medium.

| ID / component | Status | Exact visual evidence and present finding | Action |
|---|---|---|---|
| `valve` / Isolation valve | Supported family | E Valves, Gate Valve; D1 Gate. Plain opposed triangles are recognizable isolation artwork. Isolation describes duty, not an independently proven valve mechanism. | Retain; identify intended body in schedule/legend. |
| `check_valve` / Check valve | Supported family | E Valves, Check Valve 2; D1 Check alternatives; V17 Check Valve. Hinged oblique member and right-facing arrow detail support left inlet/right outlet. | Retain family; add explicit flow-direction metadata/validation. A reversed line creation order must not redefine allowed flow. |
| `control_valve` / Control valve | Supported family | E Control Valve; D2 Diaphragm. Dome identifies actuator family, not fail position. | Retain; identify pneumatic diaphragm in properties and add optional FO/FC/FL state, rather than assuming one. |
| `ball_valve` / Ball valve | Supported family | E Ball supports bow-tie plus open circle. D1 Ball instead uses a circle between end marks; V17 Globe Valve uses an open bow-tie circle too. | Retain only with declared E convention, or adopt a consistent alternative project pack. Do not call this uniquely universal. |
| `butterfly_valve` / Butterfly valve | Supported family | E Butterfly Valve; D1 Butterfly alternatives; V17 Butterfly Valve support slanted disc/central mark/end marks. | Retain. |
| `relief_valve` / Pressure relief valve | Unresolved | Current spring-over-rectangle with diagonal arrow is not the relief artwork in E Relief Valve, D1 Relief alternatives, or V17 Pressure Safety Valve. Those include angle bodies, and D1 also includes an inline alternative. Mere inline port placement is therefore not itself wrong. | Select and document a process-P&ID relief convention. Do not move ports just because E's particular example is angle-type; offer an explicit angle variant if wanted. |
| `gate_valve` / Gate valve | Supported family | E Hand-Operated Gate Valve; D1 Gate plus D2 Manual. | Retain. |
| `globe_valve` / Globe valve | Supported family | E Hand-Operated Globe Valve; D1 Globe uses the filled central mark. | Retain filled mark; keep distinction clear at small print size. |
| `needle_valve` / Needle valve | Supported family | E first Needle Valve alternative; D1 Needle. The central crossing mark distinguishes it from plain gate. | Retain chosen alternative. |
| `plug_valve` / Plug valve | Supported family | E Plug Valve; D1 Plug uses central diamond-like insert. V17 uses another plug convention. | Retain with selected legend. |
| `diaphragm_valve` / Diaphragm valve | Supported family | E inline Diaphragm cell supports oval centre. D1 Diaphragm uses other forms; the oval centre must not be confused with a diaphragm actuator. | Retain E alternative; keep actuator/body terminology separate. |
| `pinch_valve` / Pinch valve | Supported family | E Pinch Valve, doubled crossing body outlines. No independent exact primary-reference corroboration obtained. | Retain as E house symbol; do not infer regulatory approval. |
| `knife_gate_valve` / Knife gate valve | Unresolved | Current bow-tie plus upright blade does not match E's Knife Valve graphic. D1/V17 do not substantiate this specific blade-body combination. | Obtain project/manufacturer P&ID legend or select an explicit documented variant; lack of a matching inspected source is not proof of invalidity. |
| `angle_globe_valve` / Angle globe valve | Supported family | E Angle Globe Valve; D1 Angle plus globe mark; V17 Angle Globe Valve. Ninety-degree branches connect left inlet to bottom outlet. | Retain; preserve orientation and port semantics. |
| `three_way_valve` / Three-way valve | Supported family | E 3-Way Valve; D1 Three-Way. Three opposed ports/body triangles. | Retain generic body; add mixing/diverting/L/T-path designation if required. Three ports do not establish every internal route is always open. |
| `four_way_valve` / Four-way valve | Supported family | E 4-way Plug Valve body; D1 Four-Way corroborates generic four-port form. | Retain generic family, but avoid calling it an ISO directional-control state diagram. Define switching paths separately when needed. |
| `motor_operated_valve` / Motor-operated valve | Supported family | E Motor-Operated Valve and D2 Electric Motor use M actuator. | Retain; command is signal, not process. Electrical supply/feedback are not represented by the single command port. |
| `solenoid_valve` / Solenoid valve | Supported family | E Solenoid Valve and D2 Solenoid use S actuator. | Retain; record normal/fail state separately. A single S does not identify a multiport pilot circuit. |
| `pneumatic_piston_valve` / Pneumatic piston valve | Supported family | E Piston-Operated Valve; D2 Piston supports rectangular cylinder actuator. Small slash-marked side detail comes from E. | Retain family; distinguish pneumatic command from motor/solenoid electrical command at connection level. Single/double acting and spring return remain unspecified. |
| `pressure_reducing_regulator` / Pressure-reducing regulator | Mismatch | Catalogue puts sense takeoff on downstream/right side, semantically consistent with F. However line begins at (8,-18), detached from both stem and spring; there is no diaphragm/sensing body. D1 Pressure Regulator and V17 Pressure Regulating Valve visibly include sensing actuator. | Complete the sensing connection and use a documented regulator/actuator form. Preserve downstream sensing, do not simply mirror blindly. |
| `back_pressure_regulator` / Back-pressure regulator | Mismatch | Left/upstream sensing side agrees with F, but takeoff ending at (-8,-18) is detached from actuator geometry. E Back Pressure Regulator is a different diaphragm/linkage symbol, not the current spring-only hybrid. | Complete source-to-sensor visual path using selected reference; retain upstream sensing. |
| `drain_valve` / Drain valve | Project-specific | Rotated gate body plus hand operator is composable from E Hand-Operated Gate Valve / D2 Manual. Drain is a duty, not a separately supported mechanism glyph. | Retain as a named duty variant, state gate/manual assumption in component description. |
| `vent_valve` / Vent valve | Project-specific | Same manual gate family as drain, rotated. V16 Manual Air Vent is another function-specific convention, not an exact match. | Retain with explicit manual isolation/vent duty; do not equate with automatic vent. |
| `sampling_valve` / Sampling valve | Project-specific | Manual gate composition plus turned outlet. No inspected source establishes that geometry as a special sampling mechanism. | Label generic manual sampling isolation; add real sampling assemblies as separate documented types if required. |
| `foot_valve` / Foot valve with strainer | Mismatch | Artwork has a visible gap from seat at y=0 to strainer top y=7, without a connecting lead. This is a local continuity defect independent of which standard is selected. E/D1 check symbols do not establish that the downward-pointing triangle correctly expresses upward suction-to-discharge flow. | Join the body sections; select a documented nonreturn/strainer combination and verify bottom suction to top discharge. Do not infer allowed direction from the current triangle alone. |
| `tee` / Junction / tee | Supported family | Filled intersection with three process arms is a clear node; compatible with connected branch conventions (D8 fittings / V16 Side Connection). E Welded Connection uses a dot, but that cell is not proof that every dot denotes a weld here. | Retain; declare dot means connected junction, not automatically welded construction. |
| `connector` / Off-page connector | Project-specific | Directional outline is recognizable continuation notation, but no corresponding cross-sheet identity/link field is present; two local ports alone do not establish an off-page pair. | Keep as graphic-only until sheet/drawing reference and counterpart identity are supported. Clearly avoid claiming topology continues between sheets automatically. |
| `reducer` / Reducer | Supported family | E Piping Reducer; D1 Pipe Reducer; D8 Pipe Reducer. Tapered body. | Retain; generic label leaves concentric geometry inferred rather than specifying sizes. |
| `strainer` / Y-strainer | Supported family | E Y-type Strainer. V17 Wye Strainer variants confirm Y-branch family, but include accessories that ours does not claim. | Retain plain Y type; do not imply supplied drain valve/quick coupling. |
| `flanged_joint` / Flanged joint | Supported family | E Flange; D8 Flange. Twin transverse bars. | Retain; not a pressure-class specification. |
| `pipe_union` / Pipe union | Supported family | E Union; D8 Union, Screwed; V16 Union. | Retain; clarify screwed convention if project distinguishes connection method. |
| `spectacle_blind` / Spectacle blind | Supported family | E Spectacle Blind open/filled disc pair with stem to line. Current graphic follows that alternative. | Retain; add operating position metadata before using it to imply open or blinded status. |
| `blind_flange` / Blind flange | Supported family | E Flanged Dummy Cover adapted to terminal port; D8 Blank Flange directly corroborates terminal twin bars. | Retain one process port, no downstream port. |
| `pipe_cap` / Pipe cap | Supported family | E End Caps; D8 Weld Cap. Curved terminal cap with one process port. | Retain; generic label should note selected welded-cap family if construction matters. |
| `expansion_joint` / Bellows expansion joint | Supported family | E Expansion Joint. Repeated bellows lobes between end marks. | Retain as E bellows convention; no claim of physical convolution count. |
| `flexible_hose` / Flexible hose | Supported family | E Flexible Hose supplies curved line/slash marks. D8 Flexible Connection is a different acceptable family. | Retain E form; do not confuse slash marks with pneumatic signal because this has process ports. |
| `eccentric_reducer` / Eccentric reducer | Supported family | Flat side plus taper is the eccentric-family cue; V16 Eccentric Reducer independently shows asymmetric reduction, although not the same double-line outline. | Retain family; indicate flat-on-top/flat-on-bottom orientation if needed. Old outlet offset (-8 y) is compatible with this selected geometry. |
| `pipe_cross` / Four-way pipe junction | Mismatch | Actual gallery shows a hollow circle where `tee` shows a solid dot. Source draws `ellipse(-3,-3,6,6)` with default white fill. That contradicts this application's own connected-junction vocabulary; no inspected source is being asserted to ban every hollow-node convention. | Make junction notation consistent or explicitly distinguish the meaning. Verify connected graph versus mere line crossings separately. |
| `basket_strainer` / Basket strainer | Supported family | E Basket Strainer cup alternative. Current bottom drain is an additional explicit port, not shown in that particular cell. | Retain family, disclose added drain; add drain valve only as a separate component. |
| `duplex_strainer` / Duplex strainer | Supported family | E Duplex Strainer uses paired circles transverse to process line. | Retain E family; current single inlet/outlet does not model internal changeover valves or duty/standby paths. |
| `rupture_disc` / Rupture disc | Supported family | E Peripheral Rupture Disc supports bowed membrane at holder; current curved membrane and paired holder bars are recognizable, though not identical proportions. D1 shows other rupture-disc alternatives. | Retain family with local legend; no material, set pressure, vacuum support, or installed orientation inferred. |
| `flame_arrester` / Flame arrester | Supported family | E Peripheral Flame Arrestor uses barred inline cartridge with tapered ends. | Retain generic type; do not imply detonation-proof, endurance-burning, or certification class. E has separately labelled specialized alternatives. |
| `vacuum_breaker` / Vacuum breaker | Unresolved | Current open-topped stem/seat/triangle with one process port is not a clearly labelled match in E, D1 or V17. | Obtain a primary project symbol or retain explicit unverified status. Verify atmospheric admission versus process discharge before substituting any check/relief glyph. |
| `pressure_vacuum_vent` / Pressure/vacuum conservation vent | Project-specific | Opposed arrows in a box describe bidirectional function pictorially; no exact inspected legend validates the combination as a conservation-vent symbol. | Keep only as declared project symbol. Add actual relief/vacuum setpoints as data later; do not claim equipment protection performance from icon. |
| `float_steam_trap` / Float steam trap | Project-specific | Box containing float/lever is mechanism illustration. E has only generic boxed T Steam Trap; V16 Float & Thermostatic Trap Set is a different, accessory-inclusive symbol. | Choose generic trap glyph plus subtype annotation, or a documented bare-trap convention. Do not substitute VA trap-set symbol as if it were a bare float trap. |
| `inverted_bucket_trap` / Inverted bucket steam trap | Project-specific | Box with inverted bucket pictogram is not E's generic boxed T or V16 Inverted Bucket Trap Set with X. | Same: document illustrative subtype or use generic trap + type data; keep trap versus assembly distinction. |
| `thermodynamic_steam_trap` / Thermodynamic steam trap | Project-specific | Box/disc-seat illustration has no exact symbol support in inspected source figures. This is missing evidence, not a proved wrong operating mechanism. | Generic trap plus thermodynamic subtype is defensible pending a project symbol source. |
| `thermostatic_steam_trap` / Thermostatic steam trap | Project-specific | Zigzag inside box is mechanism-like. V16 Thermostatic Trap Set has filled opposed triangles, and describes an assembly rather than our bare trap. | Keep explicitly illustrative or replace with selected generic trap/type annotation. |
| `bimetallic_steam_trap` / Bimetallic steam trap | Project-specific | Three slanted strips in box suggest bimetal element but are not substantiated as a P&ID symbol by inspected figures. | Same generic-trap/type approach; do not relabel a generic T as proof of this subtype. |

## Cross-cutting findings and priorities

### 1. Graph identity is not flow direction

All relevant ports presently have `port_kinds` of process or signal. `pidcore.validate` checks endpoint existence and prohibits process connections at signal ports; it does not enforce suction/discharge, nonreturn direction, command/output, or phase. `app.py` constructs `from` and `to` from click order. Consequently the check-valve drawing can point right while the stored edge runs right-to-left. This is not itself a wrong topology in an undirected drafting app, but any future AI importer or simulator must not read edge serialization order as permitted fluid direction. Explicit `direction` or `role` metadata and suitable validation are needed first.

### 2. Signal medium and actuator mode are missing

`control_valve.signal`, and MOV/SV/piston `command`, are signal ports. `app.py` renders all signal connections with the same dashed line, while process is solid. D7 visibly distinguishes multiple line conventions, and D2 distinguishes actuator types. The present app can represent a generic control connection, but cannot claim to distinguish electric, pneumatic, hydraulic, instrument capillary, or physical shaft links. Do not silently add supply ports to saved types; add backward-compatible optional medium/role fields and explicit variants. Actuator symbol is not a fail-open/fail-closed declaration. No observed type establishes default fail position, single/double action, feedback availability, or a real valve state machine.

### 3. Regulator sensing geometry should be repaired, not merely renamed

The reducing/backpressure sense lines are correctly on opposite downstream/upstream sides, but terminate away from the sensing element. The two current spring-only forms lack the diaphragm depiction of the compared P&ID examples. A repair should choose one complete convention, bring the line to that convention's sensor, and keep the intended sensing side. A spring by itself must not accidentally suggest that the sense line is a physical open pipe.

### 4. PSV and protective devices need conservative defaults

The unresolved rectangle-arrow relief artwork resembles another schematic vocabulary, but no inspected primary P&ID reference here establishes it. Conversely, the mere presence of straight-through ports does not prove a pressure relief valve invalid: D1 explicitly shows an inline alternative. The safe action is to choose a cited complete P&ID form, not force every relief valve into an angle shape. Vacuum breakers, conservation vents and flame arresters also need precisely scoped type names. Generic icons never establish sizing, discharge routing, set pressures, materials, operating temperature, code compliance, or certification.

### 5. Steam-trap detail should not be mistaken for standard symbology

Five individually named traps currently use mechanism pictograms. The available government source deliberately draws different **trap sets**, and the user legend provides only a generic trap. This is a good case for a simple shared, sourced base glyph with subtype metadata, rather than asserting five standard images from mechanically plausible sketches. If mechanism sketches remain, mark them as house conventions and include them in the drawing legend.

### 6. Release tests should address meaning as well as endpoints

Recommended tests before claiming improved alignment: (a) each junction variant has the same declared connection marker; (b) no visible gaps between foot-valve and strainer sections; (c) both regulator sense paths visibly terminate on the correct actuator; (d) check-valve orientation remains unambiguous after 0/90/180/270-degree rotations; (e) all actuator command ports retain role and medium through save/load/export; (f) direction is not inferred from line creation order; (g) one-page drawing legend contains the selected non-universal ball/globe conventions; and (h) unsupported types remain labelled unsupported in any coverage report. Existing endpoint tests alone cannot establish these properties.

### 7. Actual exported SVG rotation review

Visually inspected `build/svg-audit-initial/sheet-01.png`, `sheet-02.png`, and `sheet-06.png` through `sheet-10.png`, which show actual exported SVG artwork at 0, 90, 180 and 270 degrees. All 49 assigned types were included. No clipped, omitted, or visibly corrupted SVG-specific primitive was observed. The check-valve hinge/arrow and angled body connections rotate coherently. The regulator sense-path gaps, foot-valve gap, and hollow pipe-cross marker persist in these SVGs: they are source artwork defects, not export codec defects.

One additional drawing-readability problem is important: the MOV actuator letter is a vector path that rotates with the body. At 180 degrees its M becomes W, which is also E's explicit Weight Gate Valve designator. M and S are sideways at quarter turns. Keep letter centres attached to the rotated actuator boxes but counter-rotate the lettering to remain upright, as the app already does for instrument letters. Add visual tests at every rotation; raster equivalence between painter and SVG cannot detect this semantic problem because both currently render the same rotated letter. The table's supported-family classification describes the base symbol; it does not waive this rotation defect.

## Limits

This is a source-backed drafting audit, not engineering approval or a process-safety review. It does not certify ISO/ISA compliance. Multiple published conventions can be valid within their declared project context; disagreement between two charts is not automatically an error. Findings called mismatch are tied to the current app's actual geometry/semantics, while unsupported source claims are classified separately. The full ISO symbol tables, proprietary owner legends, specialized vendor P&IDs and operating data remain outside this evidence set.

## Bounded implementation resolution, 2026-09-12

The table and counts above preserve the **pre-repair audit snapshot**. Subsequently authorized continuity/consistency changes were implemented in `legend_valves.py`; they are deliberately recorded in `REPAIRED_KINDS`, not `MATCHES`, and do not receive `legend_reference` metadata or inflate the 29 reference-match count.

| Component | Exact correction | Remaining limit |
|---|---|---|
| `pressure_reducing_regulator` | Prepended (0,-15) to sense path [(8,-18),(28,-18),(28,0)], joining the existing stem/spring linkage junction continuously to the downstream/right takeoff. | Original spring-only house glyph retained; no new diaphragm or certified regulator symbol claimed. |
| `back_pressure_regulator` | Prepended (0,-15) to sense path [(-8,-18),(-28,-18),(-28,0)], joining the linkage to the upstream/left takeoff. | Same: sensing-side continuity repaired, exact industry glyph still project-specific. |
| `pipe_cross` | Changed only centre ellipse [-3,-3,6,6] to ink fill, matching the app's tee connected-junction dot. | This establishes consistent app notation, not a universal rule for every industry drawing. |
| `foot_valve` | Added a single short centreline from (0,0), on the existing seat, to (0,7), on the existing strainer top. Existing outline and ports untouched. | The visible gap is repaired. The retained nonreturn-direction convention still requires a chosen primary reference; no geometry reversal or mechanism claim was made. |

All IDs, labels, categories, ports, port kinds and routing bounds were preserved. Existing M/S upright-letter handling from the parallel readability correction was preserved. Repairs are idempotent. Seven valve regression tests pass, including preservation, sensing junctions at all four rotations, fill, one-and-only-one foot bridge, and no false reference coverage. Combined `test_legend_valves`, `test_catalog_valves`, and `test_legend_reference`: **15 tests passed**. Visually inspected all 16 repaired-component rotation renders: sense paths continuous, foot sections joined, cross nodes solid, no clipping apparent. Root-level full-suite and SVG/package verification remain the release gate, not these bounded tests alone.

## Final note-only closeout, 2026-09-12

The five steam-trap subtypes now explicitly adopt bare-trap illustrations, not
trap sets containing unmodeled accessories. Drain/vent/sampling variants identify
manual gate/isolation bodies and their service duties. The pressure/vacuum vent
declares opposed tank/atmosphere functions without sizing or setpoints. The
off-page connector is a graphic continuation requiring a destination note, not
an automatic document-to-document network. These notes appear in the actual
component legend and do not acquire false source-match metadata.

## Latest chart/convention resolution, 2026-09-12

The knife-gate component now adopts the supplied Knife Valve U-shaped body,
filled downward blade and hand stem, with retained side ports. This adds one
chart match: 30 valve/piping and 81 total built-ins now have a supplied-chart basis.
The vacuum breaker instead uses an explicitly declared functional package:
ATM admission points toward the process under vacuum, with one routable process
port and an implicit atmospheric opening. It claims neither an exact standardized
device glyph nor outward pressure-relief service. Its ATM label stays upright.
Both regulators now declare simplified self-operated/loading conventions and
the appropriate downstream or upstream sensing side, without asserting a pilot,
diaphragm, fail state or process bypass. These are adopted drafting abstractions,
not outstanding claims that their house internals exactly match a normative table.
Five `test_valve_conventions.py` tests and visual review cover the changes.

## Primary-source replacements, 2026-09-12

Following the additional inspected figures documented in `research/VALVE_DIRECTION_FOLLOWUP.md`, two source-led replacements were authorized and implemented. This supersedes the earlier retained foot-valve orientation and unresolved rectangle relief artwork; original audit counts remain a historical snapshot, not the final coverage tally.

- `foot_valve`: triangle now has vertices (-13,0),(0,-18),(13,0), with seat at y=-18 and upper discharge lead. The original lower strainer and its short bridge remain. This adopts IXOM's upright, upper-connected foot-valve body from the High Level project legend, **composed with an app-added strainer**. Metadata explicitly calls it a composite rather than an exact source assembly. It does not claim universal direction rules or equipment approval.
- `relief_valve`: replaced the rectangle/arrow/spring artwork with DOE Figure 1's middle inline RELIEF alternative: open left triangle, filled right triangle, curved central relief mark. The curve is a sampled cubic, and both original horizontal process ports remain. The filled half is part of that selected glyph, not an inferred full-valve fail-state declaration.

Both use the new built-in `symbol_reference` metadata with specific source/figure and URL. Neither is added to the user-PDF `MATCHES` mapping or assigned `legend_reference`, so supplied-chart coverage does not increase. No IDs, ports, routing bounds, custom schema, or unrelated M/S orientation changes were altered.

Added `test_primary_valve_symbols.py` covering exact distinguishing shapes, source separation, unchanged contracts, idempotence and all rotated lead endpoints. Combined focused primary/valve/catalog/reference suite: **19 tests passed**. Eight actual SVG exports (two components, all four rotations) passed the existing SVG/direct-painter fidelity and clipping checks; all eight rasterized SVGs were visually inspected. The upright seat/strainer composition and DOE curved relief mark remain complete and legible in each orientation. Full-suite/package verification remains a separate release check.
