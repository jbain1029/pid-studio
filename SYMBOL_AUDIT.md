# Component symbol audit

Audit date: 2026-09-11. Scope: all **133 built-in component types** in the current source library. Drawing-local custom components are outside this fixed inventory. Three parallel reviewers covered 42 process, 49 valve/piping/protection/steam, and 42 instrumentation types. The main review reconciled their findings against code, actual gallery output, and selected reference figures.

## Result

**The complete library cannot currently be verified as industry-typical.** Software tests passed previously, but those tests establish rendering, file handling and routing behavior, not correctness of engineering symbology. Earlier product-family references established coverage, not symbol provenance.

| Disposition | Count | Meaning |
| --- | ---: | --- |
| Recognizable | 15 | Familiar conventional family or baseline outline; NOT exact-standard approval. |
| Ambiguous | 69 | Simplified, inconsistent, insufficiently identified, or needs an adopted project convention. |
| Mismatch | 8 | Visible geometry or semantic discrepancy requiring correction/review. |
| Unverified | 41 | Insufficient directly inspected evidence for this exact glyph; does NOT mean proved wrong. |
| Total | 133 | Every built-in type appears once below. |

These are conservative audit judgments, not a compliance certificate or a claim that only 15 components could be usable. Multiple legitimate symbol conventions exist. No app, library definitions, or user drawings were changed during this audit.

## Priority findings

### I1 - Instrument identification

The renderer places every tag below the symbol ([app.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/app.py:122)). Conventional field/controller bubbles are largely blank, and the legacy panel controller contains a literal C independent of its editable PIC tag ([symbol_art.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/symbol_art.py:14)). pH and conductivity components also share generic AT identification without automatic measurement annotations. ISA's instructional examples put functional identification within instrument bubbles and distinguish location/display forms. This is an identification improvement, not proof that every external-label convention is prohibited. [ISA Control Loop Foundation, chapter 7](https://www.isa.org/getmedia/e122051e-8c8c-48be-97ef-5d344c585771/Chapter7_ControlLoop-1.pdf).

### I2 - Disconnected differential-pressure taps

Both orifice and Venturi HP/LP artwork ends at y=-20 rather than joining the drawn process body ([catalog_instruments.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/catalog_instruments.py:158)). The orifice process line is y=0. Venturi's LP position is also on the drawn diverging region, not its throat. These are source-and-rendered-geometry findings; routing to a valid port does not repair the internal gap.

### I3 - Instrument semantics needing qualification

Electrical and pneumatic signals currently share the same dashed connection style ([app.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/app.py:195)); an I/P converter therefore cannot visibly distinguish its two media. ISA's cited chapter illustrates distinct conventions. Density's DT default requires a project-specific definition; thermowell and temperature element are combined under TE. Specialty meter pictograms remain unverified, rather than automatically rejected. [ISA chapter 7](https://www.isa.org/getmedia/e122051e-8c8c-48be-97ef-5d344c585771/Chapter7_ControlLoop-1.pdf).

### V1-V4 - Valves, piping and protective components

**V3:** The check valve is the isolation bowtie plus a near-adjacent vertical bar ([app.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/app.py:103)), and is almost indistinguishable in the gallery. It does not clearly convey one-way checking. This differs from the explicit directional check depiction in [Swagelok's valve guide](https://www.swagelok.com/en/blog/valve-selection-fluid-systems).

**V1:** Several basic valve and junction families are recognizable. **V2:** Globe/angle-globe hollow centers resemble the app's ball valve; the generic control actuator lacks type identification; some actuator variants require a selected legend; pipe-cross uses a hollow junction circle whereas tee uses a filled dot. These are ambiguity/inconsistency findings, not blanket declarations that alternate conventions are invalid. Comparison sources: [Tameson's valve chart](https://tameson.com/pages/valve-symbols-pid) and its [ball-valve variants guide](https://tameson.com/pages/ball-valve-symbols).

**V4:** Exact relief/regulator, specialty steam-trap, protection and several fitting glyphs lack sufficient corroboration. In particular, mechanism-like drawings and default tags do not establish standard artwork. Do not treat protection/positive-isolation symbols as approved without a selected convention.

### P1-P3 - Process components

**P1:** Many silhouettes suggest the intended family without establishing the named subtype. Examples in this library include a triangle-style centrifugal pump, propeller-style centrifugal blower, near-identical screw-pump/heater internals, and gear/lobe pump similarity. **P3:** Six specialty subtype drawings could not be matched sufficiently to inspected references.

**P2 - Five additional correction candidates:**

| Component | Observed issue | Source |
| --- | --- | --- |
| Generic heat exchanger | Zigzag ends at x=+-18, short of body/nozzles at +-26. | [app.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/app.py:96) |
| Agitated mixing tank | Vent lies on motor/agitator axis and appears connected to drive. | [catalog_process.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/catalog_process.py:113) |
| Jacketed reactor | Feed/product lead generation stops on outer jacket instead of inner process vessel; vent also overlaps shaft. | [catalog_process.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/catalog_process.py:115) |
| Double-pipe exchanger | All four nozzles meet annulus at y=+-15; none reaches inner tube at y=+-8. | [catalog_process.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/catalog_process.py:148) |
| Air-cooled exchanger | Process nozzles terminate at body y=0, but coil tips are y=-8. | [catalog_process.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/catalog_process.py:150) |

The shared first-outline nozzle generator is unsuitable as a universal rule for nested vessels and multiple internal circuits ([catalog_process.py](C:/Users/jaxon/Desktop/P&ID/pid-studio/catalog_process.py:81)). These are drawing-meaning problems even though the document connection graph is valid.

**Important non-finding:** Shell-and-tube exchanger coil tips meet its circular body and match its declared process pair. It must NOT be included in the detached-coil defect list.

DOE's training figures provide a baseline for common equipment and instrument conventions; they are not a current comprehensive standard. Figure 15's generic exchanger comparison and Figures 10-13 were visually inspected. Source PDF: :codex-file-citation{path="C:/Users/jaxon/Desktop/P&ID/pid-studio/build/symbol-audit-reference/doe-volume1.pdf" purpose="source"}.

Selected pump and exchanger charts were also visually inspected at [Vista Projects](https://www.vistaprojects.com/common-pid-symbols/). Those illustrate equipment variants, not a requirement that every simplified depiction be identical. North Ridge charts could not be visually retrieved reliably and were NOT counted as verified evidence.

## Standards scope and next correction pass

[ANSI/ISA-5.1-2024](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa5-1) covers instrumentation identification; [ISO 10628-2](https://www.iso.org/standard/51841.html) addresses chemical/petrochemical diagram symbols. This audit did not obtain and check every current normative symbol table, so no complete ISA/ISO conformity claim is warranted.

Recommended implementation order (not implemented): adopt a documented reference/legend; repair the eight drawing discrepancies; standardize bubble labels and signal media; disambiguate named equipment/valve subtypes; attach provenance and review status to each library definition; then check every component in exported sheets at practical print size. Preserve existing type IDs and port compatibility or provide explicit migrations. Real project approval still requires the applicable owner/engineering conventions.

## Exhaustive inventory

Status applies to the current rendered depiction, not the physical suitability of the component. I/V/P codes refer to the findings above.

| Type ID | Component | Disposition | Audit note |
| --- | --- | --- | --- |
| tank | Tank | Ambiguous | Cylindrical pictogram; plan/section convention unspecified (P1). |
| pump | Centrifugal pump | Ambiguous | Generic circular triangle pump depiction; centrifugal-specific convention unconfirmed (P1). |
| valve | Isolation valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| check_valve | Check valve | Mismatch | Almost identical to isolation bowtie; directional check feature unclear (V3). |
| control_valve | Control valve | Ambiguous | Unlabelled rectangular actuator does not establish actuator type (V2). |
| filter | Filter | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| exchanger | Heat exchanger | Mismatch | Internal zigzag ends before the body/nozzle contact points; clarify stream depiction (P2). |
| instrument | Instrument | Ambiguous | I1: identification/layout qualification. |
| tee | Junction / tee | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| connector | Off-page connector | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| vessel | Pressure vessel | Recognizable | Conventional vessel/tank outline recognizable; not exact-standard certification (P1). |
| gear_pump | Positive-displacement pump | Ambiguous | Rotary elements imply rotary PD, not every positive-displacement subtype (P1). |
| compressor | Compressor | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| ball_valve | Ball valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| butterfly_valve | Butterfly valve | Ambiguous | Variant, identification or internal-consistency qualification needed (V2). |
| relief_valve | Pressure relief valve | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| reducer | Reducer | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| strainer | Y-strainer | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| controller | Panel controller | Ambiguous | Literal C inside bubble does not follow editable PIC tag; external identification (I1). |
| open_tank | Open-top tank | Ambiguous | Open outline recognizable, but an isolated vent stub needs qualification (P1). |
| fixed_roof_tank | Fixed-roof storage tank | Recognizable | Conventional vessel/tank outline recognizable; not exact-standard certification (P1). |
| floating_roof_tank | Floating-roof storage tank | Ambiguous | Floating-roof cue recognizable; open-ended vent depiction needs qualification (P1). |
| horizontal_vessel | Horizontal pressure vessel | Ambiguous | Full ellipse with legs loses straight-shell/dished-head silhouette (P1). |
| conical_tank | Conical-bottom tank | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| agitated_tank | Agitated mixing tank | Mismatch | Vent is colocated with the agitator drive/shaft (P2). |
| jacketed_reactor | Jacketed stirred reactor | Mismatch | Feed and product leads stop at outer jacket, not process vessel (P2). |
| static_mixer | In-line static mixer | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| diaphragm_pump | Diaphragm pump | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| metering_pump | Metering / dosing pump | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| screw_pump | Screw pump | Ambiguous | Zigzag rectangle resembles this library's electric heater (P1). |
| lobe_pump | Rotary lobe pump | Ambiguous | Paired ellipses resemble legacy gear/PD artwork (P1). |
| peristaltic_pump | Peristaltic hose pump | Unverified | Exact subtype artwork not corroborated by inspected reference (P3). |
| reciprocating_pump | Reciprocating piston pump | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| vacuum_pump | Vacuum pump | Ambiguous | Reverse triangle alone does not reliably distinguish vacuum duty (P1). |
| reciprocating_compressor | Reciprocating compressor | Unverified | Exact subtype artwork not corroborated by inspected reference (P3). |
| screw_compressor | Rotary screw compressor | Unverified | Exact subtype artwork not corroborated by inspected reference (P3). |
| blower | Centrifugal blower / fan | Ambiguous | Propeller-style blades under centrifugal-blower label (P1). |
| shell_tube_exchanger | Shell-and-tube heat exchanger | Ambiguous | Coil connects process endpoints correctly; exact shell/tube variant still not verified (P1). |
| plate_exchanger | Plate heat exchanger | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| double_pipe_exchanger | Double-pipe heat exchanger | Mismatch | All four nozzles meet annulus; no nozzle reaches inner tube (P2). |
| air_cooled_exchanger | Air-cooled heat exchanger | Mismatch | Process nozzle ends at body y=0; drawn coil tips are y=-8 (P2). |
| electric_heater | Electric process heater | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| fired_heater | Fired heater / furnace | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| cyclone_separator | Cyclone separator | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| centrifugal_separator | Centrifugal separator | Unverified | Exact subtype artwork not corroborated by inspected reference (P3). |
| knockout_drum | Knockout / gas-liquid separator drum | Ambiguous | Demister rectangle partly protrudes beyond oval wall (P1). |
| packed_column | Packed absorption / stripping column | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| tray_column | Tray distillation column | Ambiguous | Simplified internals; supplied reboiler return has no corresponding draw-off nozzle (P1). |
| membrane_module | Membrane / reverse-osmosis module | Unverified | Exact subtype artwork not corroborated by inspected reference (P3). |
| cartridge_filter | Cartridge filter housing | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| steam_separator | Steam moisture separator | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| steam_boiler | Steam boiler | Ambiguous | Nozzles terminate enclosure rather than internal drum; package interpretation needed (P1). |
| cooling_tower | Cooling tower | Ambiguous | Simplified equipment depiction; exact subtype/connections need adopted convention (P1). |
| flash_vessel | Condensate flash vessel | Unverified | Exact subtype artwork not corroborated by inspected reference (P3). |
| gate_valve | Gate valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| globe_valve | Globe valve | Ambiguous | Small hollow circle can be confused with ball-valve center (V2). |
| needle_valve | Needle valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| plug_valve | Plug valve | Ambiguous | Variant, identification or internal-consistency qualification needed (V2). |
| diaphragm_valve | Diaphragm valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| pinch_valve | Pinch valve | Ambiguous | Variant, identification or internal-consistency qualification needed (V2). |
| knife_gate_valve | Knife gate valve | Ambiguous | Variant, identification or internal-consistency qualification needed (V2). |
| angle_globe_valve | Angle globe valve | Ambiguous | Shares hollow-circle globe/ball ambiguity (V2). |
| three_way_valve | Three-way valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| four_way_valve | Four-way valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| motor_operated_valve | Motor-operated valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| solenoid_valve | Solenoid valve | Ambiguous | Variant, identification or internal-consistency qualification needed (V2). |
| pneumatic_piston_valve | Pneumatic piston valve | Ambiguous | Variant, identification or internal-consistency qualification needed (V2). |
| pressure_reducing_regulator | Pressure-reducing regulator | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| back_pressure_regulator | Back-pressure regulator | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| rupture_disc | Rupture disc | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| flame_arrester | Flame arrester | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| vacuum_breaker | Vacuum breaker | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| pressure_vacuum_vent | Pressure/vacuum conservation vent | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| float_steam_trap | Float steam trap | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| inverted_bucket_trap | Inverted bucket steam trap | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| thermodynamic_steam_trap | Thermodynamic steam trap | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| thermostatic_steam_trap | Thermostatic steam trap | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| bimetallic_steam_trap | Bimetallic steam trap | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| flanged_joint | Flanged joint | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| pipe_union | Pipe union | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| spectacle_blind | Spectacle blind | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| blind_flange | Blind flange | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| pipe_cap | Pipe cap | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| expansion_joint | Bellows expansion joint | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| flexible_hose | Flexible hose | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| eccentric_reducer | Eccentric reducer | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| pipe_cross | Four-way pipe junction | Ambiguous | Hollow junction circle differs from filled tee dot (V2). |
| basket_strainer | Basket strainer | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| duplex_strainer | Duplex strainer | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| drain_valve | Drain valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| vent_valve | Vent valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| sampling_valve | Sampling valve | Recognizable | Conventional family recognizable; subtype/service still depends on project legend (V1). |
| foot_valve | Foot valve with strainer | Unverified | Exact artwork not corroborated by inspected symbol reference (V4). |
| pressure_indicator | Pressure indicator / gauge | Ambiguous | I1: identification/layout qualification. |
| pressure_transmitter | Pressure transmitter | Ambiguous | I1: identification/layout qualification. |
| pressure_switch_high | Pressure switch — high | Ambiguous | I1: identification/layout qualification. |
| pressure_switch_low | Pressure switch — low | Ambiguous | I1: identification/layout qualification. |
| temperature_indicator | Temperature indicator | Ambiguous | I1: identification/layout qualification. |
| temperature_transmitter | Temperature transmitter | Ambiguous | I1: identification/layout qualification. |
| temperature_switch_high | Temperature switch — high | Ambiguous | I1: identification/layout qualification. |
| temperature_switch_low | Temperature switch — low | Ambiguous | I1: identification/layout qualification. |
| flow_indicator | Flow indicator | Ambiguous | I1: identification/layout qualification. |
| flow_transmitter | Flow transmitter | Ambiguous | I1: identification/layout qualification. |
| flow_switch_low | Flow switch — low | Ambiguous | I1: identification/layout qualification. |
| level_indicator | Level indicator | Ambiguous | I1: identification/layout qualification. |
| level_transmitter | Level transmitter | Ambiguous | I1: identification/layout qualification. |
| level_switch_high | Level switch — high | Ambiguous | I1: identification/layout qualification. |
| level_switch_low | Level switch — low | Ambiguous | I1: identification/layout qualification. |
| analysis_indicator | Analysis indicator | Ambiguous | I1: identification/layout qualification. |
| analysis_transmitter | Analysis transmitter | Ambiguous | I1: identification/layout qualification. |
| ph_transmitter | pH analyzer / transmitter | Ambiguous | Same bubble and AT prefix as generic analyzer; no automatic pH annotation (I1). |
| conductivity_transmitter | Conductivity analyzer / transmitter | Ambiguous | Same bubble and AT prefix as generic analyzer; no automatic conductivity annotation (I1). |
| density_transmitter | Density transmitter | Ambiguous | DT prefix is a project choice, not established universal density designation (I3). |
| differential_pressure_indicator | Differential pressure indicator | Ambiguous | I1: identification/layout qualification. |
| differential_pressure_transmitter | Differential pressure transmitter | Ambiguous | I1: identification/layout qualification. |
| pressure_controller | Pressure indicating controller | Ambiguous | I1: identification/layout qualification. |
| temperature_controller | Temperature indicating controller | Ambiguous | I1: identification/layout qualification. |
| flow_controller | Flow indicating controller | Ambiguous | I1: identification/layout qualification. |
| level_controller | Level indicating controller | Ambiguous | I1: identification/layout qualification. |
| analysis_controller | Analysis indicating controller | Ambiguous | I1: identification/layout qualification. |
| orifice_plate | Orifice plate with pressure taps | Mismatch | HP/LP tap artwork floats clear of process graphic (I2). |
| venturi_meter | Venturi flow element | Mismatch | Floating HP/LP taps; LP point also lies off drawn throat (I2). |
| coriolis_meter | Coriolis mass flowmeter | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| magnetic_flowmeter | Electromagnetic flowmeter | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| vortex_flowmeter | Vortex flowmeter | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| ultrasonic_flowmeter | Ultrasonic flowmeter | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| turbine_flowmeter | Turbine flowmeter | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| rotameter | Variable-area flowmeter / rotameter | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| thermal_mass_flowmeter | Thermal mass flowmeter | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| thermowell | Thermowell / temperature element | Unverified | Combines well and sensing element under TE; qualification needed (I3). |
| level_gauge | Level gauge / sight glass | Unverified | Exact specialty pictogram not corroborated; see I3 for additional limitations. |
| radar_level_transmitter | Radar level transmitter | Ambiguous | I1: identification/layout qualification. |
| current_pressure_converter | Current-to-pressure converter | Unverified | Exact pictogram unverified; electrical/pneumatic outputs have same line style (I3). |

