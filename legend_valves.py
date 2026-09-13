"""Valve and fitting artwork matched to the user's pid-legend.pdf, page 1.

The legend offers alternatives, not a certification standard.  Port locations
are deliberately retained for compatibility with existing drawings.  Curves are
sampled vector polylines, keeping the same portable primitive vocabulary.
"""
from copy import deepcopy
from math import cos, sin, pi


def line(*points):
    return {'kind': 'polyline', 'points': [list(p) for p in points]}


def polygon(*points):
    return {'kind': 'polygon', 'points': [list(p) for p in points]}


def ellipse(x, y, w, h, fill=None):
    result = {'kind': 'ellipse', 'rect': [x, y, w, h]}
    if fill:
        result['fill'] = fill
    return result


def rect(x, y, w, h):
    return {'kind': 'rect', 'rect': [x, y, w, h]}


def arc(cx, cy, rx, ry, start, stop, steps=16):
    return line(*[(round(cx + rx*cos(start+(stop-start)*i/steps), 4),
                   round(cy + ry*sin(start+(stop-start)*i/steps), 4))
                  for i in range(steps+1)])


LEADS = [line((-40, 0), (-22, 0)), line((22, 0), (40, 0))]
BOW = [polygon((-22, -13), (0, 0), (-22, 13)),
       polygon((22, -13), (0, 0), (22, 13))]
HAND = [line((0, 0), (0, -26)), line((-10, -26), (10, -26))]

# Mapping strings name the actual cell used rather than suggesting that all
# library types, or all possible industry conventions, occur in this legend.
MATCHES = {}

# These are continuity/consistency repairs to existing house artwork, not new
# matches to the supplied PDF. Keep them out of MATCHES and its coverage count.
REPAIRED_KINDS = frozenset({'pressure_reducing_regulator',
                          'back_pressure_regulator', 'pipe_cross', 'foot_valve'})

PRIMARY_KINDS = frozenset({'foot_valve', 'relief_valve'})
CONVENTION_KINDS = frozenset({'vacuum_breaker', 'pressure_reducing_regulator',
                            'back_pressure_regulator'})
FOOT_REFERENCE = (
    'IXOM, High Level MIEX P&ID Symbols, NAXXXX-03-00-002 rev B, '
    'FOOT VALVE cell; Town of High Level agenda PDF page 118. '
    'Upright body with app-added strainer: composite, not an exact assembly symbol. '
    'https://www.highlevel.ca/AgendaCenter/ViewFile/Agenda/_01132025-351')
RELIEF_REFERENCE = (
    'DOE-HDBK-1016/1-93, PR-02 page 3, Figure 1, RELIEF alternatives, '
    'middle inline form (PDF page 55). '
    'https://www.energy.gov/sites/default/files/2026-04/DOE-HDBK-1016-93_VOL1.pdf')


def match(kind, label, artwork, section='Valves'):
    MATCHES[kind] = (f'pid-legend.pdf, page 1, {section}: {label}', artwork)


match('valve', 'Gate Valve (generic isolation body)', LEADS + BOW)
match('gate_valve', 'Hand-Operated Gate Valve', LEADS + BOW + HAND)
match('globe_valve', 'Hand-Operated Globe Valve',
      LEADS + BOW + HAND + [ellipse(-4, -4, 8, 8, 'ink')])
match('ball_valve', 'Ball', LEADS + BOW + [ellipse(-7, -7, 14, 14)])
match('needle_valve', 'Needle Valve (first alternative)',
      LEADS + BOW + [line((0, -15), (0, 15))])
match('plug_valve', 'Plug Valve', LEADS + BOW +
      [polygon((0, -8), (5, 0), (0, 8), (-5, 0))])
match('diaphragm_valve', 'Diaphragm (inline alternative)',
      LEADS + BOW + [ellipse(-8, -10, 16, 20)])
match('pinch_valve', 'Pinch Valve', LEADS + BOW +
      [line((-19, -9), (19, 9)), line((-19, 9), (19, -9))])
_knife = polygon((-4, -2), (4, -2), (0, 11))
_knife['fill'] = 'ink'
match('knife_gate_valve', 'Knife Valve (lead-length adaptation)',
      [line((-40, 0), (-9, 0)), line((9, 0), (40, 0)),
       line((-9, -18), (-9, 17), (9, 17), (9, -18)),
       line((0, -29), (0, -2)), line((-8, -29), (8, -29)), _knife])
match('check_valve', 'Check Valve 2', LEADS +
      [line((-22, 0), (-20, 0), (-20, -12)),
       line((22, 0), (20, 0), (20, 12)),
       line((-20, -12), (20, 12)), ellipse(-23, -15, 6, 6, 'ink'),
       line((12, 11), (20, 12), (19, 4))])
match('butterfly_valve', 'Butterfly Valve', LEADS +
      [line((-22, -13), (-22, 13)), line((22, -13), (22, 13)),
       line((-22, 13), (22, -13)), ellipse(-4, -4, 8, 8, 'ink')])
match('control_valve', 'Control Valve', LEADS + BOW +
      [line((0, 0), (0, -24)), arc(0, -24, 11, 8, pi, 2*pi),
       line((-11, -24), (11, -24)), line((0, -38), (0, -32))])
match('angle_globe_valve', 'Angle Globe Valve (rotated to existing ports)',
      [line((-40, 0), (-20, 0)), line((0, 20), (0, 40)),
       polygon((-20, -12), (0, 0), (-20, 12)),
       polygon((-12, 20), (0, 0), (12, 20)), ellipse(-4, -4, 8, 8, 'ink')])
match('three_way_valve', '3-Way Valve (rotated to existing ports)',
      LEADS + BOW + [polygon((-12, 22), (0, 0), (12, 22)), line((0, 22), (0, 40))])
match('four_way_valve', '4-way Plug Valve (four-port body alternative)',
      LEADS + BOW + [polygon((-12, 22), (0, 0), (12, 22)),
                    polygon((-12, -22), (0, 0), (12, -22)),
                    line((0, 22), (0, 40)), line((0, -22), (0, -40))])

match('motor_operated_valve', 'Motor-Operated Valve', LEADS + BOW +
      [line((0, 0), (0, -18)), rect(-10, -34, 20, 16),
       line((0, -44), (0, -34))])
match('solenoid_valve', 'Solenoid Valve', LEADS + BOW +
      [line((0, 0), (0, -18)), rect(-10, -32, 20, 14),
       line((0, -44), (0, -32))])
match('pneumatic_piston_valve', 'Piston-Operated Valve', LEADS + BOW +
      [line((0, 0), (0, -22)), rect(-9, -34, 18, 16),
       line((-9, -26), (9, -26)), line((0, -26), (0, -18)),
       line((9, -30), (17, -30)), line((11, -34), (15, -26)),
       line((15, -34), (19, -26)), line((0, -44), (0, -34))])

PIPING = 'Piping and Connecting Shapes'
match('flanged_joint', 'Flange',
      [line((-40, 0), (40, 0)), line((-5, -17), (-5, 17)),
       line((5, -17), (5, 17))], PIPING)
match('pipe_union', 'Union',
      [line((-40, 0), (40, 0)), line((-5, -8), (-5, 8)),
       line((0, -11), (0, 11)), line((5, -8), (5, 8))], PIPING)
match('blind_flange', 'Flanged Dummy Cover (terminal adaptation)',
      [line((-40, 0), (0, 0)), line((0, -17), (0, 17)),
       line((5, -17), (5, 17))], PIPING)
match('pipe_cap', 'End Caps (rotated for left-hand connection)',
      [line((-40, 0), (-6, 0)), line((-6, -14), (-6, 14)),
       arc(-6, 0, 14, 14, -pi/2, pi/2)], PIPING)
match('spectacle_blind', 'Spectacle Blind',
      [line((-40, 0), (40, 0)), line((-6, -8), (-6, 14)),
       line((6, -8), (6, 14)), line((0, -12), (0, 10)),
       ellipse(-5, -22, 10, 10), ellipse(-5, -32, 10, 10, 'ink')], PIPING)
match('expansion_joint', 'Expansion Joint', LEADS +
      [line((-22, -16), (-22, 16)), line((22, -16), (22, 16)),
       line((-22, 0), (-20, 0)), line((20, 0), (22, 0))] +
      [ellipse(x, -13, 10, 26) for x in (-20, -10, 0, 10)], PIPING)
match('flexible_hose', 'Flexible Hose',
      [line((-40, 0), (-22, 0)), line((22, 0), (40, 0)),
       line((-22, -9), (-22, 9)), line((22, -9), (22, 9)),
       line(*[(x, round(7*sin((x+22)*pi/22), 4)) for x in range(-22, 23, 2)])] +
      [line((x-1, round(7*sin((x+22)*pi/22)-3, 4)),
            (x+1, round(7*sin((x+22)*pi/22)+3, 4))) for x in range(-18, 19, 6)], PIPING)
match('reducer', 'Reducer (piping alternative)', LEADS +
      [polygon((-22, -16), (22, -8), (22, 8), (-22, 16))], PIPING)
match('strainer', 'Y-type Strainer', LEADS +
      [line((-22, -8), (22, -8)), line((-22, -8), (-22, 8)),
       line((22, -8), (22, 8)), line((-10, -8), (15, 17)),
       line((8, 24), (22, 10))], PIPING)
match('basket_strainer', 'Basket Strainer (cup alternative)', LEADS +
      [line((-22, 0), (-15, 0)), line((15, 0), (22, 0)),
       line((-15, 10), (-15, -12), (15, -12), (15, 10)),
       arc(0, 10, 15, 8, 0, pi), line((0, 18), (0, 40))], PIPING)
match('duplex_strainer', 'Duplex Strainer', LEADS +
      [line((-22, -10), (-22, 10)), line((22, -10), (22, 10)),
       line((-22, 0), (22, 0)), ellipse(-10, -20, 20, 20),
       ellipse(-10, 0, 20, 20)], PIPING)
match('flame_arrester', 'Flame Arrestor (barred inline alternative)', LEADS +
      [polygon((-22, 0), (-15, -14), (15, -14), (22, 0), (15, 14), (-15, 14))] +
      [line((x, -14), (x, 14)) for x in (-12, -6, 0, 6, 12)], 'Peripheral')


def apply(catalog):
    """Apply only visual overrides; never rename or move an existing port."""
    for kind, (reference, artwork) in MATCHES.items():
        if kind in catalog:
            catalog[kind]['artwork'] = deepcopy(artwork)
            catalog[kind]['legend_reference'] = reference
    for kind,letter,box in (('motor_operated_valve','M',[-10,-34,20,16]),
                            ('solenoid_valve','S',[-10,-32,20,14])):
        if kind in catalog:
            catalog[kind]['legend_labels'] = [
                {'text':letter,'rect':box,'follow_body':True,'pixel_size':11}]
    _repair_house_artwork(catalog)
    _apply_primary_artwork(catalog)
    _apply_declared_conventions(catalog)


def _apply_declared_conventions(catalog):
    """Concrete functional abstractions, not invented exact source matches."""
    for kind, side in (('pressure_reducing_regulator', 'downstream / outlet'),
                       ('back_pressure_regulator', 'upstream / inlet')):
        if kind in catalog:
            catalog[kind]['symbol_notes'] = [
                'Adopted simplified self-operated regulator: generic valve body, '
                'spring/loading mark and connected sensing path; no specific '
                'diaphragm, pilot or fail position is asserted.',
                f'Senses the {side} pressure. The sense path is not a process bypass.']
    if 'vacuum_breaker' in catalog:
        arrow = polygon((-4, 6), (0, 13), (4, 6))
        arrow['fill'] = 'ink'
        catalog['vacuum_breaker']['artwork'] = [
            rect(-14, -11, 28, 30), line((0, -6), (0, 9)), arrow,
            line((0, 19), (0, 40))]
        catalog['vacuum_breaker']['legend_labels'] = [
            {'text': 'ATM', 'rect': [-10, -31, 20, 20],
             'follow_body': True, 'pixel_size': 8}]
        catalog['vacuum_breaker']['symbol_notes'] = [
            'Adopted functional assembly, not a standardized internal valve symbol: '
            'ATM identifies atmospheric air admission; the arrow points toward '
            'the process connection when process pressure is below atmosphere.',
            'One modeled process port; the atmospheric opening is implicit, not '
            'a second routable port. No outward pressure-relief duty or setpoint is implied.']


def _repair_house_artwork(catalog):
    """Repair confirmed gaps while preserving the original symbol vocabulary."""
    for kind, side in (('pressure_reducing_regulator', 1),
                       ('back_pressure_regulator', -1)):
        if kind not in catalog:
            continue
        artwork = deepcopy(catalog[kind]['artwork'])
        old = [[side * 8, -18], [side * 28, -18], [side * 28, 0]]
        for primitive in artwork:
            if primitive.get('points') == old:
                # Join the retained sense line to the existing stem/spring
                # linkage junction. Do not invent a new diaphragm or medium.
                primitive['points'] = [[0, -15]] + old
        catalog[kind]['artwork'] = artwork
    if 'pipe_cross' in catalog:
        artwork = deepcopy(catalog['pipe_cross']['artwork'])
        for primitive in artwork:
            if primitive.get('kind') == 'ellipse' and primitive.get('rect') == [-3, -3, 6, 6]:
                primitive['fill'] = 'ink'
        catalog['pipe_cross']['artwork'] = artwork
    if 'foot_valve' in catalog:
        artwork = deepcopy(catalog['foot_valve']['artwork'])
        bridge = line((0, 0), (0, 7))
        if bridge not in artwork:
            # This only closes the existing seat-to-strainer gap. It does not
            # change, or certify, the retained nonreturn-direction convention.
            artwork.append(bridge)
        catalog['foot_valve']['artwork'] = artwork


def _apply_primary_artwork(catalog):
    """Selected primary-project alternatives, separate from Edraw coverage."""
    if 'foot_valve' in catalog:
        # IXOM's upper-connected upright body, composed with the pre-existing
        # strainer. Keep both saved ports, body extent and strainer unchanged.
        catalog['foot_valve']['artwork'] = [
            line((0, -40), (0, -18)),
            polygon((-13, 0), (0, -18), (13, 0)),
            line((-14, -18), (14, -18)), line((0, 0), (0, 7)),
            rect(-18, 7, 36, 18),
            *[line((x, 7), (x, 25)) for x in (-12, -4, 4, 12)],
            line((0, 25), (0, 40))]
        catalog['foot_valve']['symbol_reference'] = FOOT_REFERENCE
    if 'relief_valve' in catalog:
        right = polygon((18, -11), (0, 0), (18, 11))
        right['fill'] = 'ink'
        # Sample the DOE central curved mark with a cubic Bezier. It is a
        # distinguishing relief mark, not a flow-direction arrow or actuator.
        control = ((8, -24), (-11, -24), (11, 14), (-8, 14))
        curve = []
        for step in range(25):
            t = step / 24
            weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
            curve.append(tuple(round(sum(w*p[axis] for w, p in zip(weights, control)), 4)
                               for axis in (0, 1)))
        catalog['relief_valve']['artwork'] = [
            line((-40, 0), (-18, 0)), line((18, 0), (40, 0)),
            polygon((-18, -11), (0, 0), (-18, 11)), right, line(*curve)]
        catalog['relief_valve']['symbol_reference'] = RELIEF_REFERENCE
