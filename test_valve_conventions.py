"""Explicit knife, atmospheric-admission and simplified regulator conventions."""
import copy
import os
import unittest
import xml.etree.ElementTree as ET

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
import legend_valves as symbols
from catalog_valves import CATALOG
import pidcore as core
from verify_svg_catalog import inspect

APP = QApplication.instance() or QApplication([])
QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
APP.setFont(QFont('Segoe UI', 9))


class ValveConventionTests(unittest.TestCase):
    def test_contract_idempotence_and_source_separation(self):
        catalog = copy.deepcopy(CATALOG)
        before = copy.deepcopy(catalog)
        symbols.apply(catalog)
        kinds = symbols.CONVENTION_KINDS | {'knife_gate_valve'}
        for kind in kinds:
            for key in ('ports', 'port_kinds', 'label', 'prefix', 'routing_bounds'):
                self.assertEqual(catalog[kind][key], before[kind][key])
        self.assertIn('Knife Valve', catalog['knife_gate_valve']['legend_reference'])
        for kind in symbols.CONVENTION_KINDS:
            self.assertNotIn('legend_reference', catalog[kind])
            self.assertNotIn('symbol_reference', catalog[kind])
            self.assertTrue(catalog[kind]['symbol_notes'])
        once = copy.deepcopy(catalog)
        symbols.apply(catalog)
        self.assertEqual(catalog, once)

    def test_knife_uses_supplied_u_body_and_filled_downward_blade(self):
        art = core.CATALOG['knife_gate_valve']['artwork']
        self.assertIn(symbols.line((-9, -18), (-9, 17), (9, 17), (9, -18)), art)
        blade = next(p for p in art if p['kind'] == 'polygon')
        self.assertEqual(blade['points'], [[-4, -2], [4, -2], [0, 11]])
        self.assertEqual(blade['fill'], 'ink')
        self.assertEqual(len([p for p in art if p['kind'] == 'polygon']), 1)

    def test_admission_arrow_points_toward_process_not_atmosphere(self):
        definition = core.CATALOG['vacuum_breaker']
        arrow = next(p for p in definition['artwork'] if p['kind'] == 'polygon')
        tip = arrow['points'][1]
        for turns in range(4):
            def rotate(point):
                x, y = point
                for _ in range(turns):
                    x, y = -y, x
                return x, y
            ax, ay = rotate([0, tip[1] - arrow['points'][0][1]])
            px, py = rotate(definition['ports']['process'])
            self.assertGreater(ax * px + ay * py, 0)
        self.assertEqual(definition['legend_labels'][0]['text'], 'ATM')
        self.assertTrue(definition['legend_labels'][0]['follow_body'])
        self.assertIn('below atmosphere', ' '.join(definition['symbol_notes']))

    def test_regulator_sensing_service_is_explicit(self):
        for kind, side in [('pressure_reducing_regulator', 'downstream / outlet'),
                           ('back_pressure_regulator', 'upstream / inlet')]:
            notes = ' '.join(core.CATALOG[kind]['symbol_notes'])
            self.assertIn(side, notes)
            self.assertIn('not a process bypass', notes)
            self.assertIn('no specific diaphragm', notes)

    def test_changed_actual_svgs_at_all_rotations(self):
        for kind in ('knife_gate_valve', 'vacuum_breaker'):
            for angle in (0, 90, 180, 270):
                doc = core.new_document()
                record = core.component(kind, 0, 0, doc)
                doc['components'].append(record)
                record['rotation'] = angle
                result, svg, _ = inspect(record, doc)
                self.assertTrue(result['passed'], result)
                if kind == 'vacuum_breaker':
                    labels = [''.join(n.itertext()) for n in ET.fromstring(svg).iter()
                              if n.tag.rsplit('}', 1)[-1] == 'text']
                    self.assertIn('ATM', labels)


if __name__ == '__main__':
    unittest.main()
