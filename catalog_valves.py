"""Original schematic artwork for valves, pipe fittings and steam auxiliaries.

Coverage references (product families, not copied symbol artwork or a frequency
ranking): https://www.spiraxsarco.com/global/en-US/products/steam-traps
https://www.emerson.com/en/final-control/catalog/products-and-software/pressure-regulators
https://www.emerson.com/en/final-control/catalog/solutions/common-applications/tank-pressure-and-flame-protection
These are editable schematic conventions, not certified ISA/ISO symbols.
"""
from copy import deepcopy


def line(*points):
    return {'kind': 'polyline', 'points': [list(p) for p in points]}


def polygon(*points):
    return {'kind': 'polygon', 'points': [list(p) for p in points]}


def rect(x, y, w, h):
    return {'kind': 'rect', 'rect': [x, y, w, h]}


def ellipse(x, y, w, h):
    return {'kind': 'ellipse', 'rect': [x, y, w, h]}


CATALOG = {}
VALVES = 'Valves & Actuators'
PIPING = 'Piping & Connections'
STEAM = 'Steam & Condensate'
PROTECTION = 'Pressure Protection'
TWO = {'inlet': [-40, 0], 'outlet': [40, 0]}
LEADS = [line((-40, 0), (-22, 0)), line((22, 0), (40, 0))]
BOW = [polygon((-22, -13), (0, 0), (-22, 13)),
       polygon((22, -13), (0, 0), (22, 13))]


def add(kind, label, artwork, *, prefix='HV', category=VALVES, ports=None,
        signal=(), bounds=(-25, -30, 25, 20), leads=True):
    ports = deepcopy(TWO if ports is None else ports)
    CATALOG[kind] = {'label': label, 'prefix': prefix, 'category': category,
                     'ports': ports,
                     'port_kinds': {key: 'signal' if key in signal else 'process' for key in ports},
                     'routing_bounds': list(bounds),
                     'artwork': deepcopy((LEADS if leads else []) + artwork)}


add('gate_valve', 'Gate valve', BOW + [line((0, -1), (0, -26)), line((-10, -26), (10, -26))])
add('globe_valve', 'Globe valve', BOW + [ellipse(-5, -5, 10, 10), line((0, -5), (0, -26)), line((-10, -26), (10, -26))])
add('needle_valve', 'Needle valve', BOW + [polygon((-5, -20), (5, -20), (0, 8)), line((0, -20), (0, -28))])
add('plug_valve', 'Plug valve', BOW + [rect(-5, -9, 10, 18), line((0, -9), (0, -26)), line((0, -26), (13, -26))])
add('diaphragm_valve', 'Diaphragm valve', BOW + [line((-13, -7), (-7, -15), (7, -15), (13, -7)), line((0, -15), (0, -27))])
add('pinch_valve', 'Pinch valve', [line((-22, -10), (-8, -10), (0, -3), (8, -10), (22, -10)), line((-22, 10), (-8, 10), (0, 3), (8, 10), (22, 10)), line((0, -3), (0, -26)), line((-8, -26), (8, -26))])
add('knife_gate_valve', 'Knife gate valve', BOW + [polygon((-5, -26), (5, -26), (5, 4), (-5, 12))])
add('angle_globe_valve', 'Angle globe valve', [line((-40, 0), (-20, 0)), line((0, 20), (0, 40)), polygon((-20, -12), (0, 0), (-20, 12)), polygon((-12, 20), (0, 0), (12, 20)), ellipse(-4, -4, 8, 8), line((0, -4), (0, -25)), line((-9, -25), (9, -25))], ports={'inlet': [-40, 0], 'outlet': [0, 40]}, leads=False, bounds=(-23, -28, 16, 23))
add('three_way_valve', 'Three-way valve', BOW + [polygon((-12, 22), (0, 0), (12, 22)), line((0, 22), (0, 40))], ports={**TWO, 'branch': [0, 40]}, bounds=(-25, -16, 25, 25))
add('four_way_valve', 'Four-way valve', BOW + [polygon((-12, 22), (0, 0), (12, 22)), polygon((-12, -22), (0, 0), (12, -22)), line((0, 22), (0, 40)), line((0, -22), (0, -40))], ports={**TWO, 'branch_a': [0, -40], 'branch_b': [0, 40]}, bounds=(-25, -25, 25, 25))
add('motor_operated_valve', 'Motor-operated valve', BOW + [line((0, 0), (0, -18)), rect(-11, -34, 22, 16), line((-6, -21), (-6, -30), (0, -24), (6, -30), (6, -21)), line((0, -34), (0, -44))], prefix='MOV', ports={**TWO, 'command': [0, -44]}, signal=('command',), bounds=(-25, -36, 25, 16))
add('solenoid_valve', 'Solenoid valve', BOW + [line((0, 0), (0, -18)), rect(-10, -32, 20, 14), line((-8, -19), (8, -31)), line((0, -32), (0, -44))], prefix='SV', ports={**TWO, 'command': [0, -44]}, signal=('command',), bounds=(-25, -34, 25, 16))
add('pneumatic_piston_valve', 'Pneumatic piston valve', BOW + [line((0, 0), (0, -28)), rect(-12, -34, 24, 17), line((-12, -26), (12, -26)), line((0, -34), (0, -44))], prefix='XV', ports={**TWO, 'command': [0, -44]}, signal=('command',), bounds=(-25, -36, 25, 16))
add('pressure_reducing_regulator', 'Pressure-reducing regulator', BOW + [line((0, 0), (0, -15), (-5, -18), (5, -22), (-5, -26), (5, -30)), line((8, -18), (28, -18), (28, 0))], prefix='PCV')
add('back_pressure_regulator', 'Back-pressure regulator', BOW + [line((0, 0), (0, -15), (-5, -18), (5, -22), (-5, -26), (5, -30)), line((-8, -18), (-28, -18), (-28, 0))], prefix='PCV')
add('rupture_disc', 'Rupture disc', [line((-22, 0), (-8, 0)), line((8, 0), (22, 0)), line((-8, -18), (-8, 18)), line((8, -18), (8, 18)), line((0, -18), (5, -9), (7, 0), (5, 9), (0, 18))], prefix='RD', category=PROTECTION, bounds=(-10, -20, 10, 20))
add('flame_arrester', 'Flame arrester', [rect(-20, -16, 40, 32)] + [line((x, -16), (x, 16)) for x in (-12, -6, 0, 6, 12)], prefix='FA', category=PROTECTION, bounds=(-22, -18, 22, 18))
add('vacuum_breaker', 'Vacuum breaker', [line((0, 40), (0, 18)), polygon((-14, 18), (0, 0), (14, 18)), line((-15, 0), (15, 0)), line((0, 0), (0, -20)), line((-16, -20), (16, -20))], prefix='VB', category=PROTECTION, ports={'process': [0, 40]}, bounds=(-19, -23, 19, 21), leads=False)
add('pressure_vacuum_vent', 'Pressure/vacuum conservation vent', [line((0, 40), (0, 20)), rect(-23, -15, 46, 35), line((-10, 13), (-10, -9)), polygon((-15, -3), (-10, -10), (-5, -3)), line((10, -9), (10, 13)), polygon((5, 7), (10, 14), (15, 7)), line((-28, -22), (28, -22))], prefix='PVV', category=PROTECTION, ports={'tank': [0, 40]}, bounds=(-30, -24, 30, 22), leads=False)

TRAP = [rect(-22, -17, 44, 34)]
add('float_steam_trap', 'Float steam trap', TRAP + [ellipse(-12, -7, 18, 18), line((6, 2), (19, -5))], prefix='ST', category=STEAM, bounds=(-24, -19, 24, 19))
add('inverted_bucket_trap', 'Inverted bucket steam trap', TRAP + [line((-12, 11), (-12, -9), (10, -9), (10, 11)), line((10, -9), (19, -13))], prefix='ST', category=STEAM, bounds=(-24, -19, 24, 19))
add('thermodynamic_steam_trap', 'Thermodynamic steam trap', TRAP + [line((-15, -3), (15, -3)), line((-12, 5), (12, 5)), line((-7, 5), (-7, 14)), line((7, 5), (7, 14))], prefix='ST', category=STEAM, bounds=(-24, -19, 24, 19))
add('thermostatic_steam_trap', 'Thermostatic steam trap', TRAP + [line((-14, -9), (-10, 9), (-5, -9), (0, 9), (5, -9), (10, 9), (14, -9))], prefix='ST', category=STEAM, bounds=(-24, -19, 24, 19))
add('bimetallic_steam_trap', 'Bimetallic steam trap', TRAP + [line((-13, -9), (13, -3)), line((-13, -3), (13, 3)), line((-13, 3), (13, 9))], prefix='ST', category=STEAM, bounds=(-24, -19, 24, 19))

add('flanged_joint', 'Flanged joint', [line((-5, -17), (-5, 17)), line((5, -17), (5, 17)), line((-22, 0), (22, 0))], prefix='FL', category=PIPING, bounds=(-8, -19, 8, 19))
add('pipe_union', 'Pipe union', [line((-22, 0), (-17, 0)), line((17, 0), (22, 0)), polygon((-12, -10), (12, -10), (17, 0), (12, 10), (-12, 10), (-17, 0)), line((0, -10), (0, 10))], prefix='UN', category=PIPING, bounds=(-19, -12, 19, 12))
add('spectacle_blind', 'Spectacle blind', [ellipse(-11, -30, 22, 22), ellipse(-11, -7, 22, 22), line((-8, -4), (8, 12)), line((-22, 0), (-11, 0)), line((11, 0), (22, 0))], prefix='SB', category=PIPING, bounds=(-13, -32, 13, 17))
add('blind_flange', 'Blind flange', [line((-40, 0), (0, 0)), rect(0, -17, 5, 34)], prefix='BF', category=PIPING, ports={'process': [-40, 0]}, bounds=(-2, -19, 7, 19), leads=False)
add('pipe_cap', 'Pipe cap', [line((-40, 0), (8, 0)), line((-15, -14), (-2, -14), (8, -8), (8, 8), (-2, 14), (-15, 14))], prefix='CAP', category=PIPING, ports={'process': [-40, 0]}, bounds=(-17, -16, 10, 16), leads=False)
add('expansion_joint', 'Bellows expansion joint', [line((-22, 0), (-18, 0), (-14, -12), (-7, 12), (0, -12), (7, 12), (14, -12), (18, 0), (22, 0)), line((-22, -16), (-22, 16)), line((22, -16), (22, 16))], prefix='EJ', category=PIPING, bounds=(-24, -18, 24, 18))
add('flexible_hose', 'Flexible hose', [line((-22, 0), (-16, -8), (-8, -8), (0, 8), (8, 8), (16, -8), (22, 0)), line((-22, 5), (-16, -3), (-8, -3), (0, 13), (8, 13), (16, -3), (22, 5))], prefix='HO', category=PIPING, bounds=(-24, -10, 24, 15))
add('eccentric_reducer', 'Eccentric reducer', [line((-22, -14), (22, -14)), line((-22, 14), (22, -2)), line((-22, -14), (-22, 14)), line((22, -14), (22, -2)), line((22, -8), (40, -8)), line((-40, 0), (-22, 0))], prefix='RED', category=PIPING, ports={'large': [-40, 0], 'small': [40, -8]}, bounds=(-24, -16, 24, 16), leads=False)
add('pipe_cross', 'Four-way pipe junction', [line((-40, 0), (40, 0)), line((0, -40), (0, 40)), ellipse(-3, -3, 6, 6)], prefix='J', category=PIPING, ports={**TWO, 'branch_a': [0, -40], 'branch_b': [0, 40]}, bounds=(-5, -5, 5, 5), leads=False)
add('basket_strainer', 'Basket strainer', [rect(-20, -13, 40, 31), line((-12, -6), (-9, 12), (9, 12), (12, -6)), line((-5, -6), (-5, 12)), line((5, -6), (5, 12)), line((0, 18), (0, 40))], prefix='STR', category=PIPING, ports={**TWO, 'drain': [0, 40]}, bounds=(-22, -15, 22, 20))
add('duplex_strainer', 'Duplex strainer', [rect(-21, -20, 18, 40), rect(3, -20, 18, 40), line((-18, -12), (-6, 12)), line((6, -12), (18, 12)), line((-3, -15), (3, -15)), line((-3, 15), (3, 15))], prefix='STR', category=PIPING, bounds=(-23, -22, 23, 22))
add('drain_valve', 'Drain valve', [line((0, -40), (0, -20)), polygon((-12, -20), (0, 0), (12, -20)), polygon((-12, 20), (0, 0), (12, 20)), line((0, 20), (0, 40)), line((0, 0), (23, 0)), line((23, -10), (23, 10))], prefix='DV', ports={'process': [0, -40], 'drain': [0, 40]}, bounds=(-15, -22, 26, 22), leads=False)
add('vent_valve', 'Vent valve', [line((0, -40), (0, -20)), polygon((-12, -20), (0, 0), (12, -20)), polygon((-12, 20), (0, 0), (12, 20)), line((0, 20), (0, 40)), line((0, 0), (-23, 0)), line((-23, -10), (-23, 10))], prefix='VV', ports={'vent': [0, -40], 'process': [0, 40]}, bounds=(-26, -22, 15, 22), leads=False)
add('sampling_valve', 'Sampling valve', BOW + [line((-40, 0), (-22, 0)), line((0, 0), (0, -25)), line((-10, -25), (10, -25)), line((22, 0), (28, 0), (28, 20), (40, 20))], prefix='HV', ports={'process': [-40, 0], 'sample': [40, 20]}, leads=False, bounds=(-25, -28, 30, 23))
add('foot_valve', 'Foot valve with strainer', [line((0, -40), (0, -18)), polygon((-13, -18), (0, 0), (13, -18)), line((-14, 0), (14, 0)), rect(-18, 7, 36, 18), line((-12, 7), (-12, 25)), line((-4, 7), (-4, 25)), line((4, 7), (4, 25)), line((12, 7), (12, 25)), line((0, 25), (0, 40))], prefix='FV', ports={'discharge': [0, -40], 'suction': [0, 40]}, bounds=(-20, -20, 20, 27), leads=False)

for _kind in ('float_steam_trap', 'inverted_bucket_trap', 'thermodynamic_steam_trap',
              'thermostatic_steam_trap', 'bimetallic_steam_trap'):
    CATALOG[_kind]['symbol_notes'] = [
        'Adopted bare steam-trap illustration: internal marks identify the named '
        'mechanism subtype, not standardized internal flow passages. This is not '
        'a trap set; no isolation valves, strainer or bypass accessories are included.']
for _kind, _duty in (('drain_valve', 'drain'), ('vent_valve', 'vent'),
                     ('sampling_valve', 'sampling')):
    CATALOG[_kind]['symbol_notes'] = [
        f'Adopted manual gate/isolation body for {_duty} duty. The duty name does '
        'not specify a unique mechanism, automatic operation or accessory assembly.']
CATALOG['pressure_vacuum_vent']['symbol_notes'] = [
    'Adopted tank-to-atmosphere functional package. Opposed arrows denote outward '
    'pressure venting and inward vacuum admission; atmosphere is implicit and '
    'tank is the only routable port. No setpoints, capacity or protection rating is implied.']
