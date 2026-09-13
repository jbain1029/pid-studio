"""Process artwork redrawn from the user's pid-legend.pdf.

The reference mixes multiple drafting conventions. References identify the
selected illustration, not certification. Nozzle adapters preserve saved ports.
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


def arrow(x, y, dx=1, dy=0):
    shape = polygon((x, y), (x-6*dx+3*dy, y-6*dy-3*dx),
                    (x-6*dx-3*dy, y-6*dy+3*dx))
    shape['fill'] = 'ink'
    return shape


def vessel(w=24, h=30):
    # Straight shell with shallow, curved heads, as in the legend.
    top = [(w*math.cos(t), -h+6+6*math.sin(t))
           for t in [math.pi+i*math.pi/12 for i in range(13)]]
    bottom = [(w*math.cos(t), h-6+6*math.sin(t))
              for t in [i*math.pi/12 for i in range(13)]]
    return polygon(*(top+bottom))


def apply(catalog):
    """Replace covered definitions in-place without changing saved endpoints."""
    def put(kind, reference, body, contacts=None):
        definition = catalog[kind]
        leads = []
        for name, port in definition['ports'].items():
            target = (contacts or {}).get(name)
            if target is None:
                x, y = port
                if abs(x) >= abs(y):
                    target = [(24 if x > 0 else -24), y]
                else:
                    target = [x, (30 if y > 0 else -30)]
            # A sequence supports existing endpoints with routed nozzle adapters.
            path = target if isinstance(target[0], (tuple, list)) else [target]
            leads.append(line(tuple(port), *path))
        definition['artwork'] = body + leads
        definition['legend_reference'] = 'pid-legend.pdf: ' + reference

    def round_machine(kind, reference, inside, radius=24, feet=False):
        body = [ellipse(-radius, -radius, radius*2, radius*2)] + inside
        if feet:
            body += [line((-17, 18), (-24, 27), (24, 27), (17, 18))]
        contacts = {}
        for name, (x, y) in catalog[kind]['ports'].items():
            if abs(x) >= abs(y):
                contacts[name] = ((1 if x > 0 else -1)*math.sqrt(radius**2-y**2), y)
            else:
                contacts[name] = (x, (1 if y > 0 else -1)*math.sqrt(radius**2-x**2))
        put(kind, reference, body, contacts)

    round_machine('pump', 'Pumps / Centrifugal pump (tangential discharge)',
                  [line((-24, 0), (0, 0)), arrow(0, 0)])
    # Tangential discharge mapped back to the existing right-side outlet.
    catalog['pump']['artwork'][-1] = line((40, 0), (34, 0), (34, -24), (0, -24))
    round_machine('compressor', 'Compressors / Compressor', [], feet=True)
    round_machine('gear_pump', 'Pumps / ISO positive displacement pump', [rect(-8, -8, 16, 16)])
    round_machine('diaphragm_pump', 'Pumps / ISO diaphragm pump',
                  [line((0, -24), (23, 0), (0, 24)),
                   line((0, -24), (-7, -12), (-9, 0), (-7, 12), (0, 24))])
    round_machine('reciprocating_pump', 'Pumps / ISO reciprocating piston pump',
                  [line((-12, 0), (10, 0)), line((10, -13), (10, 13)),
                   line((-12, -7), (-6, 0), (-12, 7))])
    round_machine('reciprocating_compressor', 'Compressors / Piston Compressor',
                  [line((-12, 0), (10, 0)), line((10, -13), (10, 13)),
                   line((-12, -7), (-6, 0), (-12, 7))])
    screw = [line((-15, y), (-10, y-4), (-5, y+4), (0, y-4),
                  (5, y+4), (10, y-4), (15, y)) for y in (-3, 3)]
    round_machine('screw_pump', 'Pumps / ISO screw pump', screw)
    # These redraws replaced short rectangular bodies with 24-unit circles.
    # Include the stroke in the routing envelope rather than retaining the
    # former half-heights of 18 and 20.
    for kind in ('screw_pump', 'reciprocating_pump'):
        left, top, right, bottom = catalog[kind]['routing_bounds']
        catalog[kind]['routing_bounds'] = [min(left, -25), min(top, -25),
                                            max(right, 25), max(bottom, 25)]
    round_machine('screw_compressor', 'Compressors / Screw Compressor', screw)
    round_machine('peristaltic_pump', 'Pumps / Peristaltic pump',
                  [ellipse(-20, -20, 40, 40), ellipse(-6, -23, 12, 12),
                   ellipse(-21, 2, 12, 12), ellipse(9, 2, 12, 12)], feet=True)
    round_machine('vacuum_pump', 'Pumps / Vacuum pump', [])
    catalog['vacuum_pump']['artwork'] += [rect(-29, -7, 5, 14), rect(24, -7, 5, 14)]
    # DOE-HDBK-1016/1-93, PR-02 p14 Fig15, FAN / CENTRIFUGAL:
    # circular scroll casing, axial suction indication, tangential discharge.
    # The supplied legend's Centrifuges / Centrifugal Fan corroborates the
    # scroll family. Keep the saved right-hand discharge through an adapter.
    scroll_arc = [(26*math.cos(math.radians(degrees)),
                   26*math.sin(math.radians(degrees)))
                  for degrees in range(-40, 271, 10)]
    eye_arc = [(5*math.cos(math.radians(degrees)),
                5*math.sin(math.radians(degrees)))
               for degrees in range(-90, 91, 15)]
    put('blower', 'Centrifuges / Centrifugal Fan; DOE-HDBK-1016/1-93 PR-02 p14 Fig15 FAN / CENTRIFUGAL',
        [polygon((0, -26), (28, -26), (28, -10), (20, -17), *scroll_arc),
         ellipse(-20, -20, 40, 40), line(*eye_arc),
         line((-26, 0), (0, 0)), arrow(0, 0), arrow(40, 0)],
        {'suction': (-26, 0), 'discharge': [(34, 0), (34, -18), (28, -18)]})
    # ISO gear pump is more specific than the existing broad PD type; do not
    # silently relabel the rotary-lobe component as gear machinery.

    put('tank', 'Vessels / Covered Tank', [rect(-24, -28, 48, 56),
         line((-28, -23), (-28, -31), (28, -31), (28, -23))])
    put('vessel', 'Vessels / Vertical Vessel', [vessel()])
    put('horizontal_vessel', 'Vessels / Drum',
        [polygon(*[(y, x) for x, y in vessel(19, 29)['points']])],
        {'inlet': (-29, 0), 'outlet': (29, 0), 'vent': (0, -19), 'drain': (0, 19)})
    put('fixed_roof_tank', 'Vessels / Cone Roof Tank',
        [polygon((-24, -18), (0, -25), (24, -18), (24, 28), (-24, 28))],
        {'vent': (0, -25), 'drain': (0, 28)})
    # Preserve the existing open/roof artwork and vent service. Route the
    # existing vent endpoint to the actual upper shell rim, never down into
    # the liquid as a dip pipe. This is an explicit project nozzle adapter,
    # not a claim that the supplied chart specifies these saved ports.
    for kind in ('open_tank', 'floating_roof_tank'):
        definition = catalog[kind]
        endpoint = definition['ports']['vent']
        definition['artwork'] = [
            primitive for primitive in definition['artwork']
            if not (primitive['kind'] == 'polyline' and
                    (primitive['points'][0] == endpoint or
                     primitive['points'][-1] == endpoint))]
        definition['artwork'].append(line(tuple(endpoint), (28, -40), (28, -28)))
    # Leave unsupported conical-bottom closed tank rather than substituting Bin.
    mixer = [ellipse(-12, 14, 12, 5), ellipse(0, 14, 12, 5),
             line((0, -30), (0, 17)), rect(-4, -35, 8, 5)]
    put('agitated_tank', 'Vessels / Mixing Vessel', [vessel(24, 28)] + mixer,
        {'vent': [(14, -40), (14, -26)], 'drain': (0, 28)})
    catalog['agitated_tank']['routing_bounds'] = [-25, -36, 25, 29]
    # Explicit process lines cross the jacket and terminate at the inner wall.
    put('jacketed_reactor', 'Vessels / Heating-cooling Jacket Vessel + Mixers / Agitator, Propeller (composite)',
        [vessel(23, 27), line((-23, -20), (-29, -20), (-29, 23), (-23, 23)),
         line((23, -20), (29, -20), (29, 23), (23, 23))] + mixer,
        {'feed': (-23, -12), 'product': (0, 27),
         'vent': [(13, -40), (13, -25)], 'jacket_in': (29, -16), 'jacket_out': (29, 16)})
    catalog['jacketed_reactor']['routing_bounds'] = [-30, -36, 30, 28]
    put('static_mixer', 'Mixers / In-line Mixer',
        [rect(-28, -12, 56, 24), line((-26, 7), (-18, -7), (-9, 7), (0, -7), (9, 7), (18, -7), (26, 7))],
        {'inlet': (-28, 0), 'outlet': (28, 0)})
    put('packed_column', 'Vessels / Packing column (stacked cross hatch)',
        [vessel(21, 30)] + [rect(-21, y, 42, 13) for y in (-20, -7, 6)] +
        [line((-21, y), (21, y+13)) for y in (-20, -7, 6)] +
        [line((21, y), (-21, y+13)) for y in (-20, -7, 6)],
        {'liquid_in': (-21, -18), 'gas_in': (21, 18)})
    put('tray_column', 'Vessels / Tray Column',
        [vessel(21, 30), line((-21, -20), (21, -20)), line((-21, 20), (21, 20))] +
        [line((-15, y+9), (15, y-9)) for y in (-9, 0, 9)],
        {'feed': (-21, 0), 'reflux': (21, -20), 'reboiler_return': (21, 20)})
    put('knockout_drum', 'Vessels / Knock-out drum',
        [vessel(24, 30), rect(-24, -17, 48, 6)] +
        [line((x, -17), (x+8, -11)) for x in (-24, -12, 0, 12)] +
        [line((x+8, -17), (x, -11)) for x in (-24, -12, 0, 12)])

    # Heat Exchanger 2 has continuous coil contact at left/right shell walls.
    round_machine('exchanger', 'Heat Exchanges / Heat Exchanger 2',
                  [line((-24, 0), (-12, -12), (0, 12), (12, -12), (24, 0))])
    # Preserve four saved offset ports through short adapters to the selected
    # reference's process left/right and utility top/bottom nozzles.
    put('shell_tube_exchanger', 'Heat Exchanges / Shell and Tube Heat',
        [ellipse(-24, -24, 48, 48), line((-24, 0), (-12, -12), (0, 12), (12, -12), (24, 0))],
        {'process_in': [(-30, -15), (-30, 0), (-24, 0)],
         'process_out': [(30, 15), (30, 0), (24, 0)],
         'utility_in': [(30, -15), (30, -30), (0, -30), (0, -24)],
         'utility_out': [(-30, 15), (-30, 30), (0, 30), (0, 24)]})
    catalog['shell_tube_exchanger']['routing_bounds'] = [-31, -31, 31, 31]
    put('plate_exchanger', 'Heat Exchanges / Plate Heat Exchanger',
        [rect(-27, -24, 54, 48), line((-16, -24), (-16, 24)), line((16, -24), (16, 24)),
         line((-16, -24), (16, 0), (-16, 24)), line((16, -24), (-16, 0), (16, 24))],
        {'process_in': (-27, -15), 'process_out': (27, 15),
         'utility_in': (27, -15), 'utility_out': (-27, 15)})
    # Double-pipe reference represented with separated inner and annulus ports.
    put('double_pipe_exchanger', 'Heat Exchanges / Double Pipe Heat Exchanger (straightened nozzle adaptation)',
        [line((-28, -7), (-28, -20), (28, -20), (28, -7)),
         line((-28, 7), (-28, 20), (28, 20), (28, 7)),
         line((-28, -7), (28, -7)), line((-28, 7), (28, 7))],
        {'process_in': [(-34, -15), (-34, 0), (-28, 0)],
         'process_out': [(34, 15), (34, 0), (28, 0)],
         'utility_in': (28, -15), 'utility_out': (-28, 15)})
    put('air_cooled_exchanger', 'Heat Exchanges / Air-blown Cooler',
        [rect(-27, -21, 54, 33), line((-18, -21), (-18, 12)), line((18, -21), (18, 12)),
         line((-27, 12), (-30, 27)), line((27, 12), (30, 27)),
         polygon((-12, 19), (12, 27), (12, 19), (-12, 27))],
        {'process_in': (-27, 0), 'process_out': (27, 0)})
    put('electric_heater', 'Heat Exchanges / Electric Heater (element-bank detail)',
        [rect(-24, -22, 48, 44), rect(-20, -17, 40, 8), rect(-20, -4, 40, 8), rect(-20, 9, 40, 8)] +
        [line((x, y), (x, y+8)) for x in (-12, -4, 4, 12) for y in (-17, -4, 9)],
        {'inlet': (-24, 0), 'outlet': (24, 0)})
    put('fired_heater', 'Heat Exchanges / Fired Heater',
        [polygon((-24, -16), (-9, -26), (-9, -30), (9, -30), (9, -26), (24, -16), (24, 28), (-24, 28)),
         line((-24, -12), (-12, -12), (12, 0), (-12, 12), (18, 12), (18, -12), (24, -12)),
         line((-16, 22), (-16, 28)), line((-8, 22), (-8, 28)), line((0, 22), (0, 28)), line((8, 22), (8, 28)), line((16, 22), (16, 28))],
        {'process_in': (-24, -12), 'process_out': (24, -12), 'fuel': (0, 28), 'flue': (0, -30)})
    put('steam_boiler', 'Heat Exchanges / Boiler (package boundary; added service nozzles)',
        [polygon((-24, -16), (-8, -26), (-8, -30), (8, -30), (8, -26), (24, -16), (24, 28), (-24, 28))],
        {'steam': (0, -30), 'blowdown': (0, 28)})
    put('cooling_tower', 'Heat Exchanges / Cooling Tower 3',
        [polygon((-28, 28), (-16, -28), (16, -28), (28, 28)), line((-25, 16), (25, 16))],
        {'hot_water_in': (-18.786, -15), 'cold_water_out': (26.286, 20),
         'makeup': (-26.286, 20), 'blowdown': (0, 28)})
