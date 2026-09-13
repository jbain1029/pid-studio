"""Instrumentation artwork matched to the user's pid-legend.pdf, Instrument table.

The supplied chart is a project reference, not a certification of ISA compliance.
Existing named attachment points remain stable; leads are adapted around them.
"""
import math
from catalog_instruments import line, ellipse, rect


def apply(catalog):
    for kind, meaning in {
        'density_transmitter': 'DT means density transmitter in this project; D is the adopted density-variable convention, not a universal assignment.',
        'current_pressure_converter': 'I/P denotes current input at input and pressure output at output. FY is a retained loop/project identifier, not proof of a flow loop. Generic signal lines do not specify electrical or pneumatic line notation.',
        'level_gauge': 'Adopted sight-glass illustration with upper and lower process taps. Internal strokes indicate the viewing/liquid region, not a T function code or a level-control setpoint.',
    }.items():
        catalog[kind]['symbol_notes'] = [meaning]
    bubbles = {
        'instrument': ('Indicator', False),
        'pressure_indicator': ('PI / Pressure Indicator', False),
        'pressure_transmitter': ('PT / Pressure Transmitter', False),
        'temperature_indicator': ('TI / Temp Indicator', False),
        'temperature_transmitter': ('TT / Temp Transmitter', False),
        'flow_indicator': ('FI / Flow Indicator', False),
        'flow_transmitter': ('FT / Flow Transmitter', False),
        'level_indicator': ('LI / Level Indicator', False),
        'level_transmitter': ('LT / Level Transmitter', False),
        'analysis_transmitter': ('AT / Analyzer Transmitter', False),
        'pressure_controller': ('PIC / Pressure Indicating', False),
        'controller': ('PIC / Pressure Indicating', True),
    }
    for kind, (reference, divided) in bubbles.items():
        entry = catalog[kind]
        radius = 23
        artwork = [ellipse(-radius, -radius, radius*2, radius*2)]
        for x, y in entry['ports'].values():
            length = math.hypot(x, y)
            artwork.append(line((x, y), (x*radius/length, y*radius/length)))
        entry.update(artwork=artwork, legend_reference='Instrument: '+reference,
                     legend_bubble='divided' if divided else 'field')

    # A function bubble must not become anonymous merely because it was absent
    # from the project chart. The bar is location information, not a text rule.
    generic = ('pressure_switch_high', 'pressure_switch_low',
        'temperature_switch_high', 'temperature_switch_low', 'flow_switch_low',
        'level_switch_high', 'level_switch_low', 'analysis_indicator',
        'ph_transmitter', 'conductivity_transmitter', 'density_transmitter',
        'differential_pressure_indicator', 'differential_pressure_transmitter',
        'temperature_controller', 'flow_controller', 'level_controller',
        'analysis_controller', 'humidity_sensor')
    for kind in generic:
        entry = catalog[kind]
        radius = 22 if kind == 'humidity_sensor' else 23
        artwork = [ellipse(-radius, -radius, radius*2, radius*2)]
        for x, y in entry['ports'].values():
            length = math.hypot(x, y)
            artwork.append(line((x,y), (x*radius/length,y*radius/length)))
        entry['artwork'] = artwork
        entry['legend_bubble'] = 'field'
        entry.pop('upright_artwork', None)
        if kind.startswith('differential_pressure_'):
            entry['legend_labels'] = [
                {'text':'H','rect':[-40,4,14,12],'pixel_size':9,'follow_body':True},
                {'text':'L','rect':[26,4,14,12],'pixel_size':9,'follow_body':True}]

    replacements = {
        'magnetic_flowmeter': ('Magnetic', [rect(-25,-24,50,48)], 'M'),
        'vortex_flowmeter': ('Vortex Sensor', [rect(-25,-24,50,48),
            {'kind':'polygon','points':[[-12,-15],[15,0],[-12,15]]}], None),
        'ultrasonic_flowmeter': ('Ultrasonic Meter', [rect(-25,-24,50,48),
            line((-19,0),(-16,-3),(-12,-3),(-8,3),(-4,3),(-1,0)),
            line((3,0),(6,-3),(10,-3),(14,3),(18,3),(21,0))], None),
        'coriolis_meter': ('Coriolis Flow Sensor', [rect(-25,-24,50,48),
            line((-19,0),(-12,0),(-6,-9),(4,9),(10,0),(19,0)),
            line((-19,0),(-10,0),(-4,-9),(6,9),(12,0),(19,0))], None),
        'turbine_flowmeter': ('Turbine Meter', [rect(-25,-24,50,48),
            line((0,0),(-7,-10),(-7,-15),(0,-18),(7,-15),(7,-10),
                 (0,0),(-7,10),(-7,15),(0,18),(7,15),(7,10),(0,0))], None),
        'rotameter': ('Rotometer', [
            {'kind':'polygon','points':[[-10,-22],[25,0],[-10,22]]},
            ellipse(-25,-22,36,44)], None),
    }
    for kind, (reference, body, label) in replacements.items():
        entry = catalog[kind]
        leads = [line((-40,0),(-25,0)), line((25,0),(40,0))]
        if 'signal' in entry['ports']:
            leads.append(line((0,-40),(0,-24)))
        entry.update(artwork=leads+body, legend_reference='Instrument: '+reference)
        if label:
            entry['legend_labels'] = [{'text':label,'rect':[-20,-16,40,32]}]

    # Keep real HP/LP taps even though the compact reference omits them. The
    # low-pressure lead reaches the throat, not the diverging Venturi wall.
    catalog['venturi_meter'].update(artwork=[
        line((-40,0),(-25,0)), line((25,0),(40,0)),
        line((-25,0), *[(x,-8-12*(x/25)**2) for x in range(-25,26,5)], (25,0)),
        line((-25,0), *[(x,8+12*(x/25)**2) for x in range(-25,26,5)], (25,0)),
        line((-15,-40),(-15,-12.32)), line((15,-40),(15,-29),(0,-29),(0,-8))],
        legend_reference='Instrument: Venturi Meter (adapted with retained pressure taps)')
    catalog['orifice_plate'].update(artwork=[
        line((-40,0),(40,0)), line((-8,-23),(-8,23)),
        line((0,-17),(0,17)), line((8,-23),(8,23)),
        line((-15,-40),(-15,0)), line((15,-40),(15,0))],
        legend_reference='Piping and Connecting Shapes: Orifice Plate (retained pressure taps)')
    catalog['current_pressure_converter'].update(artwork=[
        ellipse(-23,-23,46,46),
        line((-40,0),(-23,0)), line((23,0),(40,0))],
        legend_labels=[{'text':'I','rect':[-19,-19,20,20]},
                       {'text':'P','rect':[0,0,20,20]}],
        legend_reference='Instrument: Transducer I/P')
    catalog['current_pressure_converter']['upright_artwork'] = [line((-16,16),(16,-16))]

    # Readability corrections for existing project symbols; these do not add
    # reference-match claims or change their existing identity/port contracts.
    for kind,letter,indices in (('inline_flowmeter','F',(3,4,5)),
                                ('hall_speed_sensor','H',(2,3,4)),
                                ('thermocouple','T',(1,2))):
        # Use pristine definitions so repeated application remains stable.
        from catalog_rankine import CATALOG as rankine
        from copy import deepcopy
        entry = catalog[kind]
        entry['artwork'] = [deepcopy(p) for i,p in enumerate(rankine[kind]['artwork']) if i not in indices]
        entry['legend_labels'] = [{'text':letter,'rect':[-18,-18,36,36],'pixel_size':23}]

    # Primary project drawings substantiate function + explicit technology,
    # not the previous invented antenna/probe pictograms. Keep all old ports.
    for kind, radius, technology, reference in (
        ('radar_level_transmitter', 20, ['RADAR'],
         'City of Sandy / Stantec, Alder Creek WTP conceptual design, PDF page 33, I-006, LT-5401 plus RADAR; https://www.ci.sandy.or.us/sites/default/files/fileattachments/public_works/page/22679/attachment_a_-_alder_creek_wtp_upgrade_conceptual_design_report.pdf'),
        ('thermal_mass_flowmeter', 23, ['THERMAL','MASS'],
         'DOE-hosted Ash Fouling Free Regenerative Air Preheater report, page 33, Exhibits 3.2.2-3.2.3; functional assembly abstraction, not exact element glyph; https://www.osti.gov/servlets/purl/2472813')):
        entry = catalog[kind]
        artwork = [ellipse(-radius,-radius,2*radius,2*radius)]
        for x,y in entry['ports'].values():
            length = math.hypot(x,y)
            artwork.append(line((x,y),(x*radius/length,y*radius/length)))
        entry.update(artwork=artwork, legend_bubble='field',
                     instrument_technology=technology, symbol_reference=reference)
        entry.pop('legend_reference',None)
