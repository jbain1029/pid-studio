# Component library

PID Studio includes 141 built-in component types plus drawing-local custom definitions.
Both the Toolbox and catalog browser use expandable folders, with subfolders such as Pumps, Manual valves, and Pressure. Folders start collapsed; search includes folder names, component names, types, and tag prefixes, opening matches automatically. Clearing search restores the earlier expansion state. Custom components have their own folder, grouped by category. This organization does not alter saved component identifiers or drawings.
Use **Browse components** above the Toolbox (or View > Component catalog) for a large
preview, named-port list and Insert button. Search accepts multiple words, categories
and tag prefixes; for example `gate valve`, `flow`, `PT` or `heat transfer`.
The Toolbox still supports drag/drop and double-click insertion.

## Coverage and limitations

This is broad process-industry coverage, not a statistical ranking of usage or an
exhaustive catalog of every industry's equipment. Original simplified schematic
artwork is used; no manufacturer geometry or licensed symbol tables were copied.
Functionally different instruments may share a field bubble and are distinguished
by their component type and tag prefix. Default prefixes are editable project
conventions, not a guaranteed ISA/plant tagging implementation.

Common families were checked against primary manufacturer references:
[Emerson valves](https://www.emerson.com/en/final-control/catalog/products-and-software/valves/control-valves),
[Endress+Hauser measurement families](https://www.endress.com/en/field-instruments-overview),
[Spirax Sarco steam traps](https://www.spiraxsarco.com/global/en-US/products/steam-traps),
[Alfa Laval separation](https://www.alfalaval.com/en-us/products/separation/centrifugal-separators/separators/).
These references establish relevant component families, not certified artwork or
frequency of use. More source links are in the catalog modules.

Each component has named process/signal ports and an obstacle envelope checked
at all four rotations. Local gauges have no fictitious signal output; transmitters
and switches expose signal connections; panel controllers use signal-only ports.
DP devices and multi-stream exchangers expose separate named connections.
Do not interpret displayed nozzle count as a complete vendor nozzle schedule,
flow capacity, allowed process condition or safety suitability. Verify actual
project requirements. No internal flow-state switching or calculations are simulated.

Existing original type IDs and user-defined .pidsymbol files remain compatible.
The expanded catalog is shared by rendering, routing, reports, saved-file validation
and exported AI authoring context. Older app versions cannot open newly added
built-in types; use the updated app. API/recognition behavior is not newly certified.

## Inventory

### Process Equipment (7)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Tank | TK | inlet, outlet |
| Centrifugal pump | P | inlet, outlet |
| Filter | F | inlet, outlet |
| Heat exchanger | HX | inlet, outlet, utility_in, utility_out |
| Pressure vessel | V | inlet, outlet, vent, drain |
| Positive-displacement pump | P | inlet, outlet |
| Compressor | K | inlet, outlet |

### Valves & Actuators (25)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Isolation valve | HV | inlet, outlet |
| Check valve | CV | inlet, outlet |
| Control valve | FV | inlet, outlet, signal (signal) |
| Ball valve | HV | inlet, outlet |
| Butterfly valve | HV | inlet, outlet |
| Pressure relief valve | PSV | inlet, outlet |
| Gate valve | HV | inlet, outlet |
| Globe valve | HV | inlet, outlet |
| Needle valve | HV | inlet, outlet |
| Plug valve | HV | inlet, outlet |
| Diaphragm valve | HV | inlet, outlet |
| Pinch valve | HV | inlet, outlet |
| Knife gate valve | HV | inlet, outlet |
| Angle globe valve | HV | inlet, outlet |
| Three-way valve | HV | inlet, outlet, branch |
| Four-way valve | HV | inlet, outlet, branch_a, branch_b |
| Motor-operated valve | MOV | inlet, outlet, command (signal) |
| Solenoid valve | SV | inlet, outlet, command (signal) |
| Pneumatic piston valve | XV | inlet, outlet, command (signal) |
| Pressure-reducing regulator | PCV | inlet, outlet |
| Back-pressure regulator | PCV | inlet, outlet |
| Drain valve | DV | process, drain |
| Vent valve | VV | vent, process |
| Sampling valve | HV | process, sample |
| Foot valve with strainer | FV | discharge, suction |

### Instrumentation (42)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Instrument | PI | process, signal (signal) |
| Panel controller | PIC | input (signal), signal (signal) |
| Pressure indicator / gauge | PI | process |
| Pressure transmitter | PT | process, signal (signal) |
| Pressure switch — high | PSH | process, signal (signal) |
| Pressure switch — low | PSL | process, signal (signal) |
| Temperature indicator | TI | process |
| Temperature transmitter | TT | process, signal (signal) |
| Temperature switch — high | TSH | process, signal (signal) |
| Temperature switch — low | TSL | process, signal (signal) |
| Flow indicator | FI | process |
| Flow transmitter | FT | process, signal (signal) |
| Flow switch — low | FSL | process, signal (signal) |
| Level indicator | LI | process |
| Level transmitter | LT | process, signal (signal) |
| Level switch — high | LSH | process, signal (signal) |
| Level switch — low | LSL | process, signal (signal) |
| Analysis indicator | AI | process |
| Analysis transmitter | AT | process, signal (signal) |
| pH analyzer / transmitter | AT | process, signal (signal) |
| Conductivity analyzer / transmitter | AT | process, signal (signal) |
| Density transmitter | DT | process, signal (signal) |
| Differential pressure indicator | PDI | high_pressure, low_pressure |
| Differential pressure transmitter | PDT | high_pressure, low_pressure, signal (signal) |
| Pressure indicating controller | PIC | input (signal), output (signal) |
| Temperature indicating controller | TIC | input (signal), output (signal) |
| Flow indicating controller | FIC | input (signal), output (signal) |
| Level indicating controller | LIC | input (signal), output (signal) |
| Analysis indicating controller | AIC | input (signal), output (signal) |
| Orifice plate with pressure taps | FE | inlet, outlet, high_pressure, low_pressure |
| Venturi flow element | FE | inlet, outlet, high_pressure, low_pressure |
| Coriolis mass flowmeter | FT | inlet, outlet, signal (signal) |
| Electromagnetic flowmeter | FT | inlet, outlet, signal (signal) |
| Vortex flowmeter | FT | inlet, outlet, signal (signal) |
| Ultrasonic flowmeter | FT | inlet, outlet, signal (signal) |
| Turbine flowmeter | FT | inlet, outlet, signal (signal) |
| Variable-area flowmeter / rotameter | FI | inlet, outlet |
| Thermal mass flowmeter | FT | inlet, outlet, signal (signal) |
| Thermowell / temperature element | TE | process, sensor (signal) |
| Level gauge / sight glass | LG | upper_tap, lower_tap |
| Radar level transmitter | LT | process, signal (signal) |
| Current-to-pressure converter | FY | input (signal), output (signal) |

### Piping & Connections (15)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Junction / tee | J | left, right, branch |
| Off-page connector | OP | inlet, outlet |
| Reducer | R | inlet, outlet |
| Y-strainer | ST | inlet, outlet |
| Flanged joint | FL | inlet, outlet |
| Pipe union | UN | inlet, outlet |
| Spectacle blind | SB | inlet, outlet |
| Blind flange | BF | process |
| Pipe cap | CAP | process |
| Bellows expansion joint | EJ | inlet, outlet |
| Flexible hose | HO | inlet, outlet |
| Eccentric reducer | RED | large, small |
| Four-way pipe junction | J | inlet, outlet, branch_a, branch_b |
| Basket strainer | STR | inlet, outlet, drain |
| Duplex strainer | STR | inlet, outlet |

### Vessels & Reactors (8)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Open-top tank | TK | inlet, outlet, vent, drain |
| Fixed-roof storage tank | TK | inlet, outlet, vent, drain |
| Floating-roof storage tank | TK | inlet, outlet, vent, drain |
| Horizontal pressure vessel | V | inlet, outlet, vent, drain |
| Conical-bottom tank | TK | inlet, outlet, vent, drain |
| Agitated mixing tank | MX | inlet, outlet, vent, drain |
| Jacketed stirred reactor | R | feed, product, vent, jacket_in, jacket_out |
| In-line static mixer | MX | inlet, outlet |

### Pumps & Compressors (10)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Diaphragm pump | P | inlet, outlet |
| Metering / dosing pump | P | inlet, outlet |
| Screw pump | P | inlet, outlet |
| Rotary lobe pump | P | inlet, outlet |
| Peristaltic hose pump | P | inlet, outlet |
| Reciprocating piston pump | P | inlet, outlet |
| Vacuum pump | VP | suction, exhaust |
| Reciprocating compressor | K | suction, discharge |
| Rotary screw compressor | K | suction, discharge |
| Centrifugal blower / fan | B | suction, discharge |

### Heat Transfer (6)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Shell-and-tube heat exchanger | HX | process_in, process_out, utility_in, utility_out |
| Plate heat exchanger | HX | process_in, process_out, utility_in, utility_out |
| Double-pipe heat exchanger | HX | process_in, process_out, utility_in, utility_out |
| Air-cooled heat exchanger | AC | process_in, process_out |
| Electric process heater | EH | inlet, outlet |
| Fired heater / furnace | H | process_in, process_out, fuel, flue |

### Separation & Treatment (7)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Cyclone separator | CY | feed, gas_out, solids_out |
| Centrifugal separator | CS | feed, light_phase, heavy_phase, solids |
| Knockout / gas-liquid separator drum | V | feed, gas_out, liquid_out |
| Packed absorption / stripping column | C | liquid_in, gas_out, gas_in, liquid_out |
| Tray distillation column | C | feed, overhead, bottoms, reflux, reboiler_return |
| Membrane / reverse-osmosis module | M | feed, retentate, permeate |
| Cartridge filter housing | F | inlet, outlet, vent, drain |

### Steam & Utilities (4)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Steam moisture separator | SS | steam_in, steam_out, condensate |
| Steam boiler | SB | feedwater, steam, fuel, blowdown |
| Cooling tower | CT | hot_water_in, cold_water_out, makeup, blowdown |
| Condensate flash vessel | FV | condensate_in, flash_steam, condensate_out |

### Pressure Protection (4)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Rupture disc | RD | inlet, outlet |
| Flame arrester | FA | inlet, outlet |
| Vacuum breaker | VB | process |
| Pressure/vacuum conservation vent | PVV | tank |

### Steam & Condensate (5)

| Component | Default prefix | Named ports |
| --- | --- | --- |
| Float steam trap | ST | inlet, outlet |
| Inverted bucket steam trap | ST | inlet, outlet |
| Thermodynamic steam trap | ST | inlet, outlet |
| Thermostatic steam trap | ST | inlet, outlet |
| Bimetallic steam trap | ST | inlet, outlet |

Separator instrumentation additions: vortex phase separator, turbine / expander, surface heating coil, generic inline flowmeter, humidity sensor, surface acoustic sensor, Hall speed sensor and surface thermocouple. These are built-in types available in new drawings; restart an already-running app to refresh its catalog.
