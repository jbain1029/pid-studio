"""Original schematic artwork for common process instrumentation.

Functional tag prefixes distinguish instruments sharing a field bubble. These
are drafting components, not a claim of ISA/ISO symbol-library certification.
Scope references (not artwork copied from vendor documentation):
https://www.emerson.com/en/measurement-instrumentation
https://www.emerson.com/en/measurement-instrumentation/catalog/flow-measurement
https://www.emerson.com/en/measurement-instrumentation/catalog/pressure-measurement/differential-pressure
"""


def line(*points):
    return {'kind': 'line' if len(points) == 2 else 'polyline',
            'points': [list(point) for point in points]}


def ellipse(x, y, width, height):
    return {'kind': 'ellipse', 'rect': [x, y, width, height]}


def rect(x, y, width, height):
    return {'kind': 'rect', 'rect': [x, y, width, height]}


def definition(label, prefix, ports, artwork, bounds=(-23, -23, 23, 23), signals=('signal',)):
    return {'label': label, 'prefix': prefix, 'category': 'Instrumentation',
            'ports': ports, 'port_kinds': {name: 'signal' if name in signals else 'process'
                                         for name in ports},
            'routing_bounds': list(bounds), 'artwork': artwork}


def field(label, prefix, *, differential=False, signal=True):
    ports = {'process': [0, 40]}
    artwork = [ellipse(-23, -23, 46, 46)]
    if differential:
        ports = {'high_pressure': [-40, 0], 'low_pressure': [40, 0]}
        artwork += [line((-40, 0), (-23, 0)), line((23, 0), (40, 0)),
                    line((-10, -5), (-10, 5)), line((-15, 0), (-5, 0)),
                    line((5, 0), (15, 0))]
    else:
        artwork.append(line((0, 23), (0, 40)))
    if signal:
        ports['signal'] = [0, -40]
        artwork.append(line((0, -40), (0, -23)))
    return definition(label, prefix, ports, artwork)


def controller(label, prefix):
    # A horizontal bar distinguishes panel functions from field bubbles.
    return definition(label, prefix, {'input': [0, -40], 'output': [0, 40]},
                      [ellipse(-23, -23, 46, 46), line((-23, 0), (23, 0)),
                       line((0, -40), (0, -23)), line((0, 23), (0, 40))],
                      signals=('input', 'output'))


def meter(label, prefix, artwork, *, signal=True):
    ports = {'inlet': [-40, 0], 'outlet': [40, 0]}
    primitives = [line((-40, 0), (-25, 0)), line((25, 0), (40, 0)), *artwork]
    if signal:
        ports['signal'] = [0, -40]
        primitives.append(line((0, -40), (0, -24)))
    return definition(label, prefix, ports, primitives, (-25, -24, 25, 24))


CATALOG = {}
for _kind, _label, _prefix in (
    ('pressure_indicator', 'Pressure indicator / gauge', 'PI'),
    ('pressure_transmitter', 'Pressure transmitter', 'PT'),
    ('pressure_switch_high', 'Pressure switch — high', 'PSH'),
    ('pressure_switch_low', 'Pressure switch — low', 'PSL'),
    ('temperature_indicator', 'Temperature indicator', 'TI'),
    ('temperature_transmitter', 'Temperature transmitter', 'TT'),
    ('temperature_switch_high', 'Temperature switch — high', 'TSH'),
    ('temperature_switch_low', 'Temperature switch — low', 'TSL'),
    ('flow_indicator', 'Flow indicator', 'FI'),
    ('flow_transmitter', 'Flow transmitter', 'FT'),
    ('flow_switch_low', 'Flow switch — low', 'FSL'),
    ('level_indicator', 'Level indicator', 'LI'),
    ('level_transmitter', 'Level transmitter', 'LT'),
    ('level_switch_high', 'Level switch — high', 'LSH'),
    ('level_switch_low', 'Level switch — low', 'LSL'),
    ('analysis_indicator', 'Analysis indicator', 'AI'),
    ('analysis_transmitter', 'Analysis transmitter', 'AT'),
    ('ph_transmitter', 'pH analyzer / transmitter', 'AT'),
    ('conductivity_transmitter', 'Conductivity analyzer / transmitter', 'AT'),
    ('density_transmitter', 'Density transmitter', 'DT'),
):
    CATALOG[_kind] = field(_label, _prefix, signal=not _kind.endswith('_indicator'))

CATALOG['differential_pressure_indicator'] = field('Differential pressure indicator', 'PDI', differential=True, signal=False)
CATALOG['differential_pressure_transmitter'] = field('Differential pressure transmitter', 'PDT', differential=True)

for _kind, _label, _prefix in (
    ('pressure_controller', 'Pressure indicating controller', 'PIC'),
    ('temperature_controller', 'Temperature indicating controller', 'TIC'),
    ('flow_controller', 'Flow indicating controller', 'FIC'),
    ('level_controller', 'Level indicating controller', 'LIC'),
    ('analysis_controller', 'Analysis indicating controller', 'AIC'),
):
    CATALOG[_kind] = controller(_label, _prefix)

# Each meter has a distinct original internal schematic cue. Instrument tags
# and project legends, not these small pictograms alone, define the function.
CATALOG.update({
    'orifice_plate': meter('Orifice plate with pressure taps', 'FE',
        [line((-25, 0), (25, 0)), line((0, -23), (0, -6)), line((0, 6), (0, 23))], signal=False),
    'venturi_meter': meter('Venturi flow element', 'FE',
        [line((-25, -20), (-7, -8), (7, -8), (25, -20)),
         line((-25, 20), (-7, 8), (7, 8), (25, 20))], signal=False),
    'coriolis_meter': meter('Coriolis mass flowmeter', 'FT',
        [rect(-25, -24, 50, 48), line((-25, 0), (-16, 0), (-12, 15),
                                    (12, 15), (16, 0), (25, 0))]),
    'magnetic_flowmeter': meter('Electromagnetic flowmeter', 'FT',
        [rect(-25, -24, 50, 48), line((-25, 0), (25, 0)),
         line((-8, -16), (8, -16)), line((-8, 16), (8, 16))]),
    'vortex_flowmeter': meter('Vortex flowmeter', 'FT',
        [rect(-25, -24, 50, 48), line((-10, -12), (-10, 12)),
         line((-5, 0), (2, -6), (9, 6), (16, -6), (22, 0))]),
    'ultrasonic_flowmeter': meter('Ultrasonic flowmeter', 'FT',
        [rect(-25, -24, 50, 48), line((-17, -17), (17, 17)),
         line((-17, -11), (11, 17)), line((11, -17), (17, -11))]),
    'turbine_flowmeter': meter('Turbine flowmeter', 'FT',
        [ellipse(-24, -24, 48, 48), ellipse(-4, -4, 8, 8),
         line((0, -4), (8, -18)), line((4, 0), (18, 8)),
         line((0, 4), (-8, 18)), line((-4, 0), (-18, -8))]),
    'rotameter': meter('Variable-area flowmeter / rotameter', 'FI',
        [{'kind': 'polygon', 'points': [[-23, -20], [23, -10], [23, 10], [-23, 20]]},
         line((-4, -12), (-4, 12))], signal=False),
    'thermal_mass_flowmeter': meter('Thermal mass flowmeter', 'FT',
        [rect(-25, -24, 50, 48), line((-8, -24), (-8, 10)),
         line((8, -24), (8, 10)), ellipse(-11, 7, 6, 6), ellipse(5, 7, 6, 6)]),
    # Combined sensing assembly, not a bare protective well. DOE-HDBK-1016/1-93
    # Module 2 Fig. 9 distinguishes an element with a well; WIKA TW 90.11
    # distinguishes the protective closed tube from the removable thermometer.
    # The internal stem stops short of the pocket tip. The process-side lead
    # is a schematic association, not a fluid passage through the sensor.
    'thermowell': definition('Temperature element in thermowell (assembly)', 'TE',
        {'process': [0, 40], 'sensor': [0, -40]},
        [line((0, 24), (0, 40)), line((0, -40), (0, 10)),
         line((-10, -24), (-10, 15), (0, 24), (10, 15), (10, -24)),
         line((-17, -24), (17, -24)), ellipse(-2,10,4,4)],
        (-17, -24, 17, 24), signals=('sensor',)),
    'level_gauge': definition('Level gauge / sight glass', 'LG',
        {'upper_tap': [-40, -15], 'lower_tap': [-40, 15]},
        [rect(-10, -25, 20, 50), line((-40, -15), (-10, -15)),
         line((-40, 15), (-10, 15)), line((-6, 7), (6, 7)),
         line((0, 7), (0, 22))], (-10, -25, 10, 25)),
    'radar_level_transmitter': definition('Radar level transmitter', 'LT',
        {'process': [0, 40], 'signal': [0, -40]},
        [ellipse(-20, -24, 40, 40), line((0, -40), (0, -24)),
         line((0, 16), (0, 40)), line((-12, 22), (0, 30), (12, 22))], (-20, -24, 20, 30)),
    'current_pressure_converter': definition('Current-to-pressure converter', 'FY',
        {'input': [-40, 0], 'output': [40, 0]},
        [rect(-23, -23, 46, 46), line((-23, 23), (23, -23)),
         line((-40, 0), (-23, 0)), line((23, 0), (40, 0))], signals=('input', 'output')),
})

# Primary differential-pressure elements have real impulse-line taps, not an
# electrical output. They can connect to a separate DP transmitter's HP / LP.
for _kind in ('orifice_plate', 'venturi_meter'):
    _entry = CATALOG[_kind]
    _entry['ports'].update({'high_pressure': [-15, -40], 'low_pressure': [15, -40]})
    _entry['port_kinds'].update({'high_pressure': 'process', 'low_pressure': 'process'})
    _entry['artwork'].extend([line((-15, -40), (-15, -20)), line((15, -40), (15, -20))])
