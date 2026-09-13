import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
import xml.etree.ElementTree as ET

from PySide6.QtWidgets import QApplication
from PySide6.QtSvg import QSvgRenderer
import drawio_export
import instrument_display
import pidcore as core

APP = QApplication.instance() or QApplication([])


class InstrumentDisplayTests(unittest.TestCase):
    def test_simple_compound_and_arbitrary_ids_are_not_truncated(self):
        for tag, expected in [('PT-203', ('PT','203')), ('PT203A', ('PT','203A')),
                ('10-PT-203A', ('PT','10-PT-203A')), ('plant alpha sensor', ('PT','plant alpha sensor')),
                ('FT-203', ('PT','FT-203')), ('custom-tag-12-B', ('PT','custom-tag-12-B')),
                (' PT-203 ', ('PT',' PT-203 ')), ('', ('PT',''))]:
            with self.subTest(tag=tag):
                self.assertEqual(instrument_display.tag_lines(tag, 'PT'), expected)

    def test_all_generic_bubbles_render_function_and_instance_in_all_rotations(self):
        for kind, definition in core.CATALOG.items():
            if not definition.get('legend_bubble'):
                continue
            document = core.new_document()
            record = core.component(kind, 0, 0, document)
            record['tag'] = definition['prefix'] + '-203'
            document['components'].append(record)
            for rotation in (0,90,180,270):
                with self.subTest(kind=kind,rotation=rotation):
                    record['rotation'] = rotation
                    svg = drawio_export.artwork(record,document)
                    self.assertTrue(QSvgRenderer(svg).isValid())
                    labels = [''.join(node.itertext()) for node in ET.fromstring(svg).iter()
                              if node.tag.rsplit('}',1)[-1]=='text']
                    self.assertIn(definition['prefix'], labels)
                    self.assertIn('203', labels)

    def test_only_explicit_legacy_panel_controller_has_location_bar(self):
        for kind, entry in core.CATALOG.items():
            if entry.get('legend_bubble'):
                with self.subTest(kind=kind):
                    self.assertEqual(entry['legend_bubble'], 'divided' if kind=='controller' else 'field')
                    self.assertFalse(entry.get('upright_artwork'))
                    if kind != 'controller':
                        self.assertFalse(any(p.get('points') in ([[-23,0],[23,0]], [[-22,0],[22,0]])
                                             for p in entry['artwork']))

    def test_compound_tag_remains_complete_in_svg_without_mutation(self):
        document = core.new_document()
        record = core.component('pressure_transmitter',0,0,document)
        record['tag'] = 'AREA-10-PT-203A-extra'
        document['components'].append(record)
        before = copy.deepcopy(document)
        svg = drawio_export.artwork(record, document)
        labels = [''.join(n.itertext()) for n in ET.fromstring(svg).iter() if n.tag.rsplit('}',1)[-1]=='text']
        self.assertIn(record['tag'], labels)
        self.assertIn('PT', labels)
        self.assertEqual(document, before)

    def test_existing_upright_ip_and_rankine_fixes_retained(self):
        converter = core.CATALOG['current_pressure_converter']
        self.assertTrue(converter['upright_artwork'])
        self.assertEqual([label['text'] for label in converter['legend_labels']], ['I','P'])
        for kind, letter in [('inline_flowmeter','F'),('hall_speed_sensor','H'),('thermocouple','T')]:
            self.assertEqual(core.CATALOG[kind]['legend_labels'][0]['text'], letter)


if __name__ == '__main__':
    unittest.main()
