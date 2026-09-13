"""Original schematic components for process and utility service.

Coverage references (equipment families only, not copied symbol drawings):
https://www.alfalaval.com/en-us/products/separation/centrifugal-separators/separators/
https://www.spiraxsarco.com/global/en-US/products/steam-traps
https://www.spiraxsarco.com/resources-and-design-tools
These simplified original graphics are not a claim of ISO/ISA certification.
"""

import math


def line(*points):
    return {'kind': 'polyline', 'points': [list(p) for p in points]}


def polygon(*points):
    return {'kind': 'polygon', 'points': [list(p) for p in points]}


def rect(x, y, w, h):
    return {'kind': 'rect', 'rect': [x, y, w, h]}


def ellipse(x, y, w, h):
    return {'kind': 'ellipse', 'rect': [x, y, w, h]}


CATALOG = {}


def nozzle_contact(port, outline, bounds):
    """Intersect the inward radial nozzle with the actual outer body artwork.

    The routing envelope deliberately includes supports/motors and is not a
    physical wall. Only the first (outer-body) primitive determines contact;
    inner details must not accidentally extend a nozzle across an open vessel.
    An open mouth without a wall keeps its short free-ended nozzle at the rim.
    """
    x, y = port
    horizontal = abs(x) > abs(y)
    fixed = y if horizontal else x
    axis = x if horizontal else y
    candidates = []
    if outline['kind'] == 'ellipse':
        left, top, width, height = outline['rect']
        center = left + width / 2 if horizontal else top + height / 2
        cross_center = top + height / 2 if horizontal else left + width / 2
        radius = width / 2 if horizontal else height / 2
        cross_radius = height / 2 if horizontal else width / 2
        fraction = (fixed - cross_center) / cross_radius
        if abs(fraction) <= 1:
            offset = radius * math.sqrt(max(0, 1 - fraction * fraction))
            candidates = [center - offset, center + offset]
    else:
        if outline['kind'] == 'rect':
            left, top, width, height = outline['rect']
            points = [(left, top), (left + width, top),
                      (left + width, top + height), (left, top + height), (left, top)]
        else:
            points = outline['points']
            if outline['kind'] == 'polygon':
                points = points + [points[0]]
        for start, end in zip(points, points[1:]):
            a, b = (start[1], end[1]) if horizontal else (start[0], end[0])
            u, v = (start[0], end[0]) if horizontal else (start[1], end[1])
            if a == b:
                if fixed == a:
                    candidates.extend((u, v))
            elif min(a, b) <= fixed <= max(a, b):
                candidates.append(u + (fixed - a) * (v - u) / (b - a))
    # Choose the first wall encountered from the outside, on this side only.
    candidates = [value for value in candidates if 0 <= value / axis <= 1]
    if candidates:
        contact = max(candidates, key=lambda value: value / axis)
    else:
        contact = bounds[0 if axis < 0 else 2] if horizontal else bounds[1 if axis < 0 else 3]
    return (contact, y) if horizontal else (x, contact)


def add(kind, label, prefix, category, ports, artwork, bounds=(-30, -30, 30, 30)):
    # Off-axis ports stay on their dominant radial axis, so the editor can
    # route all four rotations, but leads touch the real artwork, not its box.
    leads = []
    for x, y in ports.values():
        leads.append(line(nozzle_contact((x, y), artwork[0], bounds), (x, y)))
    CATALOG[kind] = {'label': label, 'prefix': prefix, 'category': category,
                     'ports': {k: list(v) for k, v in ports.items()},
                     'port_kinds': {k: 'process' for k in ports},
                     'routing_bounds': list(bounds), 'artwork': leads + artwork}


FLOW = {'inlet': (-40, 0), 'outlet': (40, 0)}
VESSEL = {**FLOW, 'vent': (0, -40), 'drain': (0, 40)}
THERMAL = {'process_in': (-40, -15), 'process_out': (40, 15),
           'utility_in': (40, -15), 'utility_out': (-40, 15)}
TANKS = 'Vessels & Reactors'
PUMPS = 'Pumps & Compressors'
HEAT = 'Heat Transfer'
SEPARATION = 'Separation & Treatment'
STEAM = 'Steam & Utilities'

add('open_tank', 'Open-top tank', 'TK', TANKS, VESSEL,
    [line((-28, -28), (-28, 28), (28, 28), (28, -28)), line((-28, 8), (28, 8))], (-28, -28, 28, 28))
add('fixed_roof_tank', 'Fixed-roof storage tank', 'TK', TANKS, VESSEL,
    [polygon((-28, -18), (0, -30), (28, -18), (28, 28), (-28, 28)), line((-28, -18), (28, -18))])
add('floating_roof_tank', 'Floating-roof storage tank', 'TK', TANKS, VESSEL,
    [line((-28, -28), (-28, 28), (28, 28), (28, -28)), rect(-26, -5, 52, 6), line((-28, 13), (28, 13))])
add('horizontal_vessel', 'Horizontal pressure vessel', 'V', TANKS, VESSEL,
    [ellipse(-30, -20, 60, 40), line((-18, 18), (-18, 29)), line((18, 18), (18, 29))])
add('conical_tank', 'Conical-bottom tank', 'TK', TANKS, VESSEL,
    [polygon((-26, -28), (26, -28), (26, 12), (0, 30), (-26, 12)), line((-26, 12), (26, 12))])
add('agitated_tank', 'Agitated mixing tank', 'MX', TANKS, VESSEL,
    [rect(-27, -22, 54, 50), rect(-8, -30, 16, 8), line((0, -22), (0, 18)), line((-16, 12), (16, 20)), line((-16, 20), (16, 12))])
add('jacketed_reactor', 'Jacketed stirred reactor', 'R', TANKS,
    {'feed': (-40, -12), 'product': (0, 40), 'vent': (0, -40), 'jacket_in': (40, -16), 'jacket_out': (40, 16)},
    [rect(-30, -24, 60, 54), rect(-23, -24, 46, 47), line((0, -30), (0, 16)), line((-14, 9), (14, 17)), line((-14, 17), (14, 9))])
add('static_mixer', 'In-line static mixer', 'MX', TANKS, FLOW,
    [rect(-30, -16, 60, 32), line((-25, -13), (-9, 13), (8, -13), (25, 13)), line((-25, 13), (-9, -13), (8, 13), (25, -13))], (-30, -16, 30, 16))
add('diaphragm_pump', 'Diaphragm pump', 'P', PUMPS, FLOW,
    [ellipse(-27, -25, 54, 50), line((0, -25), (-8, -12), (8, 0), (-8, 12), (0, 25))], (-27, -25, 27, 25))
add('metering_pump', 'Metering / dosing pump', 'P', PUMPS, FLOW,
    [ellipse(-26, -24, 52, 48), rect(-13, -11, 22, 22), line((9, 0), (26, 0)), line((-19, 28), (19, -28)), polygon((19, -28), (9, -23), (16, -16))])
add('screw_pump', 'Screw pump', 'P', PUMPS, FLOW,
    [rect(-30, -18, 60, 36), line((-25, 0), (-15, -12), (-5, 12), (5, -12), (15, 12), (25, 0))], (-30, -18, 30, 18))
add('lobe_pump', 'Rotary lobe pump', 'P', PUMPS, FLOW,
    [ellipse(-29, -25, 58, 50), ellipse(-22, -9, 23, 18), ellipse(0, -9, 23, 18), line((-10, -18), (-10, 18)), line((12, -18), (12, 18))], (-29, -25, 29, 25))
add('peristaltic_pump', 'Peristaltic hose pump', 'P', PUMPS, FLOW,
    [ellipse(-28, -28, 56, 56), line((-28, 0), (-18, -17), (0, -22), (18, -17), (28, 0)), ellipse(-16, -13, 10, 10), ellipse(6, -13, 10, 10), ellipse(-5, 8, 10, 10)], (-28, -28, 28, 28))
add('reciprocating_pump', 'Reciprocating piston pump', 'P', PUMPS, FLOW,
    [rect(-29, -20, 58, 40), rect(-9, -17, 8, 34), line((-1, 0), (22, 0)), line((17, -8), (25, 0), (17, 8))], (-29, -20, 29, 20))
add('vacuum_pump', 'Vacuum pump', 'VP', PUMPS,
    {'suction': (-40, 0), 'exhaust': (40, 0)},
    [ellipse(-27, -27, 54, 54), polygon((-18, 0), (18, -16), (18, 16)), line((-12, 27), (-20, 30)), line((12, 27), (20, 30))])
add('reciprocating_compressor', 'Reciprocating compressor', 'K', PUMPS,
    {'suction': (-40, 0), 'discharge': (40, 0)},
    [polygon((-29, -25), (29, -15), (29, 15), (-29, 25)), rect(-12, -15, 7, 30), line((-5, 0), (24, 0))])
add('screw_compressor', 'Rotary screw compressor', 'K', PUMPS,
    {'suction': (-40, 0), 'discharge': (40, 0)},
    [polygon((-29, -25), (29, -15), (29, 15), (-29, 25)), line((-23, -12), (-12, 12), (0, -12), (12, 12), (23, -12)), line((-23, 12), (-12, -12), (0, 12), (12, -12), (23, 12))])
add('blower', 'Centrifugal blower / fan', 'B', PUMPS,
    {'suction': (-40, 0), 'discharge': (40, 0)},
    [ellipse(-27, -27, 54, 54), ellipse(-6, -6, 12, 12), polygon((-5, -6), (-20, -16), (0, -23)), polygon((6, -2), (23, -5), (17, 16)), polygon((-3, 6), (-2, 24), (-20, 12))])
add('shell_tube_exchanger', 'Shell-and-tube heat exchanger', 'HX', HEAT, THERMAL,
    [ellipse(-30, -25, 60, 50), line((-24, -15), (18, -15), (18, 0), (-18, 0), (-18, 15), (24, 15))], (-30, -25, 30, 25))
add('plate_exchanger', 'Plate heat exchanger', 'HX', HEAT, THERMAL,
    [rect(-27, -28, 54, 56)] + [line((x, -24), (x + 12, 24)) for x in (-23, -13, -3, 7)], (-27, -28, 27, 28))
add('double_pipe_exchanger', 'Double-pipe heat exchanger', 'HX', HEAT, THERMAL,
    [rect(-30, -22, 60, 44), rect(-30, -8, 60, 16), line((-20, -22), (-20, -8)), line((20, 8), (20, 22))], (-30, -22, 30, 22))
add('air_cooled_exchanger', 'Air-cooled heat exchanger', 'AC', HEAT,
    {'process_in': (-40, 0), 'process_out': (40, 0)},
    [rect(-30, -30, 60, 45), line((-30, -8), (-20, -8), (-20, -24), (-7, -24), (-7, 8), (7, 8), (7, -24), (20, -24), (20, -8), (30, -8)), ellipse(-10, 17, 20, 13), line((-9, 19), (9, 28)), line((-9, 28), (9, 19))])
add('electric_heater', 'Electric process heater', 'EH', HEAT, FLOW,
    [rect(-30, -22, 60, 44), line((-23, 0), (-15, -12), (-5, 12), (5, -12), (15, 12), (23, 0)), line((0, -22), (0, -30))])
add('fired_heater', 'Fired heater / furnace', 'H', HEAT,
    {'process_in': (-40, -12), 'process_out': (40, -12), 'fuel': (0, 40), 'flue': (0, -40)},
    [rect(-30, -30, 60, 60), line((-30, -12), (-19, -12), (-19, -23), (19, -23), (19, -12), (30, -12)), polygon((-14, 22), (-12, 10), (-4, 15), (0, 1), (8, 14), (12, 9), (14, 22))])
add('cyclone_separator', 'Cyclone separator', 'CY', SEPARATION,
    {'feed': (-40, -15), 'gas_out': (0, -40), 'solids_out': (0, 40)},
    [polygon((-25, -25), (25, -25), (25, 0), (6, 30), (-6, 30), (-25, 0)), line((-25, 0), (25, 0)), line((-12, -15), (13, -15), (13, -6), (-5, -6))])
add('centrifugal_separator', 'Centrifugal separator', 'CS', SEPARATION,
    {'feed': (-40, 0), 'light_phase': (40, -15), 'heavy_phase': (40, 15), 'solids': (0, 40)},
    [ellipse(-28, -28, 56, 56), polygon((-21, 13), (0, -20), (21, 13)), line((-15, 5), (15, 5)), line((-9, -4), (9, -4)), line((0, 13), (0, 28))])
add('knockout_drum', 'Knockout / gas-liquid separator drum', 'V', SEPARATION,
    {'feed': (-40, 0), 'gas_out': (0, -40), 'liquid_out': (0, 40)},
    [ellipse(-24, -30, 48, 60), line((-21, 12), (21, 12)), rect(-20, -19, 40, 7), line((-17, -19), (-10, -12)), line((0, -19), (7, -12)), line((12, -19), (19, -12))])
add('packed_column', 'Packed absorption / stripping column', 'C', SEPARATION,
    {'liquid_in': (-40, -18), 'gas_out': (0, -40), 'gas_in': (40, 18), 'liquid_out': (0, 40)},
    [rect(-22, -30, 44, 60), rect(-19, -20, 38, 40)] + [line((-19, y), (19, y + 14)) for y in (-20, -8, 4)], (-22, -30, 22, 30))
add('tray_column', 'Tray distillation column', 'C', SEPARATION,
    {'feed': (-40, 0), 'overhead': (0, -40), 'bottoms': (0, 40), 'reflux': (40, -20), 'reboiler_return': (40, 20)},
    [rect(-22, -30, 44, 60), line((-22, -18), (14, -18), (14, -10)), line((22, -3), (-14, -3), (-14, 5)), line((-22, 12), (14, 12), (14, 20))], (-22, -30, 22, 30))
add('membrane_module', 'Membrane / reverse-osmosis module', 'M', SEPARATION,
    {'feed': (-40, 0), 'retentate': (40, 0), 'permeate': (0, 40)},
    [rect(-30, -22, 60, 44), line((-26, 5), (26, 5)), line((-22, -16), (-22, 5)), line((-10, -16), (-10, 5)), line((2, -16), (2, 5)), line((14, -16), (14, 5)), line((0, 5), (0, 22))], (-30, -22, 30, 22))
add('cartridge_filter', 'Cartridge filter housing', 'F', SEPARATION,
    {**FLOW, 'vent': (0, -40), 'drain': (0, 40)},
    [rect(-25, -28, 50, 56), rect(-16, -21, 9, 42), rect(7, -21, 9, 42), line((-25, -23), (25, -23))], (-25, -28, 25, 28))
add('steam_separator', 'Steam moisture separator', 'SS', STEAM,
    {'steam_in': (-40, 0), 'steam_out': (40, 0), 'condensate': (0, 40)},
    [rect(-25, -27, 50, 54), line((-13, -22), (-13, 12)), line((0, -12), (0, 22)), line((13, -22), (13, 12))], (-25, -27, 25, 27))
add('steam_boiler', 'Steam boiler', 'SB', STEAM,
    {'feedwater': (-40, 0), 'steam': (0, -40), 'fuel': (40, 0), 'blowdown': (0, 40)},
    [rect(-30, -30, 60, 60), ellipse(-23, -23, 46, 22), line((-23, -12), (23, -12)), polygon((-13, 23), (-9, 9), (0, 17), (6, 4), (14, 23))])
add('cooling_tower', 'Cooling tower', 'CT', STEAM,
    {'hot_water_in': (-40, -15), 'cold_water_out': (40, 20), 'makeup': (-40, 20), 'blowdown': (0, 40)},
    [polygon((-29, 30), (-17, -28), (17, -28), (29, 30)), line((-25, 20), (25, 20)), line((-19, -15), (19, -15)), line((-17, -4), (17, 4)), line((-17, 4), (17, -4)), ellipse(-10, -27, 20, 10)])
add('flash_vessel', 'Condensate flash vessel', 'FV', STEAM,
    {'condensate_in': (-40, 0), 'flash_steam': (0, -40), 'condensate_out': (0, 40)},
    [ellipse(-25, -30, 50, 60), line((-22, 14), (22, 14)), line((-15, -10), (-8, -18), (-1, -10), (6, -18), (13, -10))])

# Adopted interpretation of composite artwork, carried into the drawing legend.
for _kind, _notes in {
    'open_tank': ['Open-top tank with an adopted rim-connected vent/service adapter. The retained vent lead reaches the upper rim; it does not assert a roof, submerged dip pipe or specific vent hardware.'],
    'floating_roof_tank': ['Floating-roof tank with an adopted rim-connected vent/service adapter above the roof region. The lead does not specify actual roof vent hardware or a submerged dip pipe.'],
    'plate_exchanger': ['Two separate circuits: process_in to process_out; utility_in to utility_out. The plate pattern does not imply mixing.'],
    'double_pipe_exchanger': ['Inner tube: process_in to process_out. Outer annulus: utility_in to utility_out. Upper/lower annulus strokes depict one annulus out of plane, not two blocked channels.'],
    'jacketed_reactor': ['Composite vessel/jacket symbol. Process feed enters the vessel, not the jacket. jacket_in and jacket_out belong to a separate utility circuit; crossing the jacket outline depicts a penetration, not a fluid junction.'],
    'steam_boiler': ['Boiler package, not detailed internals: feedwater inlet, steam outlet, fuel supply and blowdown. The top connection is steam, not a flue. No separate flue port is modeled.'],
    'fired_heater': ['Fired-heater package: process_in and process_out are the process circuit; fuel and flue are separate services. Flame/coil details are schematic, not a burner or tube-layout design.'],
    'conical_tank': ['Closed cone-bottom tank; the cone denotes the vessel bottom, not a solids-bin service requirement.'],
    'metering_pump': ['Adjustable positive-displacement pump used for metering duty. The adjustment mark does not specify a pumping mechanism or metering accuracy.'],
    'lobe_pump': ['Rotary-lobe pump family. inlet and outlet name the intended project routing, not a universal restriction against reverse operation.'],
    'electric_heater': ['Electric process-heater package. inlet and outlet are fluid services; the element strokes are not separate fluid channels. Electrical supply is not modeled.'],
    'cyclone_separator': ['Cyclone family with feed, gas_out and solids_out services. The scroll indicates cyclonic separation, not a literal internal feed tube.'],
    'centrifugal_separator': ['Centrifugal separation package with feed, light_phase, heavy_phase and solids services. Internal rotor/disc arrangement is unspecified; the casing is a generic equipment abstraction.'],
    'membrane_module': ['Membrane-module abstraction: feed and retentate are the main stream; permeate is a separate product service. Internal strokes identify membrane duty, not a detailed membrane or plenum layout.'],
    'cartridge_filter': ['Cartridge housing with inlet, outlet, vent and drain services. Cartridge marks do not specify clean/dirty plenum geometry or cartridge count.'],
    'flash_vessel': ['Vessel for flashing condensate: condensate_in feeds the vessel, flash_steam leaves the top and condensate_out leaves the bottom. The horizontal mark indicates a liquid region, not a controlled level setpoint.'],
}.items():
    CATALOG[_kind]['symbol_notes'] = _notes

# Omit unsubstantiated internal pictograms; preserve generic casing and leads.
CATALOG['centrifugal_separator']['artwork'] = [
    primitive for primitive in CATALOG['centrifugal_separator']['artwork']
    if primitive['kind'] == 'ellipse' or
    (primitive['kind'] == 'polyline' and any(list(port) in primitive['points']
     for port in CATALOG['centrifugal_separator']['ports'].values()))]
CATALOG['flash_vessel']['artwork'] = [
    primitive for primitive in CATALOG['flash_vessel']['artwork']
    if not (primitive['kind'] == 'polyline' and len(primitive['points']) == 5)]
