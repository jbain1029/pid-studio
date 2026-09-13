"""Reference-artwork regressions: visual changes must retain drawing semantics."""
import copy
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from PySide6.QtSvg import QSvgRenderer
import custom_symbols
import drawio_export
import legend_instruments
import legend_process
import legend_valves
import pidcore as core
import routing

APP = QApplication.instance() or QApplication([])


class LegendReferenceTests(unittest.TestCase):
    def test_overrides_preserve_catalog_identity_and_routing_contract(self):
        # Reconstruct the pre-reference catalog, rather than comparing against
        # an already-overridden import. The core deep-copies extension catalogs.
        with patch.object(legend_process, 'apply'), patch.object(legend_valves, 'apply'), patch.object(legend_instruments, 'apply'):
            before = runpy.run_path(str(Path(core.__file__)))['CATALOG']
        catalog = copy.deepcopy(before)
        for module in (legend_process, legend_valves, legend_instruments):
            module.apply(catalog)
        self.assertEqual(set(catalog), set(before))
        self.assertTrue(any(entry.get('artwork') != before[kind].get('artwork')
                            for kind, entry in catalog.items()))
        for kind, original in before.items():
            with self.subTest(kind=kind):
                for field in ('label', 'prefix', 'ports', 'port_kinds', 'category'):
                    self.assertEqual(catalog[kind][field], original[field], field)
        # Some process bodies enlarge their obstacle envelopes; those changes
        # are permitted provided every retained port still has a clear stub.
        self.assertEqual(catalog, core.CATALOG)
        once = copy.deepcopy(catalog)
        for module in (legend_process, legend_valves, legend_instruments):
            module.apply(catalog)
        self.assertEqual(catalog, once)

    def test_every_matched_port_has_an_artwork_lead_endpoint(self):
        matched = {kind: definition for kind, definition in core.CATALOG.items()
                   if 'legend_reference' in definition}
        self.assertGreater(len(matched), 20)
        for kind, definition in matched.items():
            endpoints = {tuple(point) for primitive in definition['artwork']
                         if primitive['kind'] in ('line', 'polyline')
                         for point in (primitive['points'][0], primitive['points'][-1])}
            for name, position in definition['ports'].items():
                with self.subTest(kind=kind, port=name):
                    self.assertIn(tuple(position), endpoints)

    def test_every_port_retains_clear_outward_stub_in_four_rotations(self):
        for kind, definition in core.CATALOG.items():
            for rotation in (0, 90, 180, 270):
                component = core.component(kind, 0, 0, core.new_document())
                component['rotation'] = rotation
                bounds = core.routing_bounds(component)
                for name, position in definition['ports'].items():
                    x, y = position
                    for unused in range(rotation // 90):
                        x, y = -y, x
                    dx, dy = ((1 if x > 0 else -1, 0) if abs(x) >= abs(y)
                              else (0, 1 if y > 0 else -1))
                    with self.subTest(kind=kind, rotation=rotation, port=name):
                        self.assertTrue(routing.clear((x, y), (x + 20*dx, y + 20*dy), [bounds]))

    def test_builtin_artwork_metadata_does_not_leak_into_saved_documents(self):
        document = core.new_document()
        for index, kind in enumerate(core.CATALOG):
            document['components'].append(core.component(kind, index*100, 0, document))
        before = copy.deepcopy(document)
        self.assertEqual(core.validate(document), [])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'reference-components.pid'
            core.save(document, path)
            self.assertEqual(core.load(path), before)
            text = path.read_text(encoding='utf-8')
            for field in ('legend_reference', 'symbol_reference', 'legend_bubble', 'legend_labels',
                          'port_meanings', 'instrument_technology', 'symbol_notes'):
                self.assertNotIn(field, text)

    def test_drawio_svg_retains_function_and_loop_text(self):
        document = core.new_document()
        record = core.component('pressure_transmitter', 0, 0, document)
        record['tag'] = 'PT-203'
        document['components'].append(record)
        for rotation in (0, 90, 180, 270):
            with self.subTest(rotation=rotation):
                record['rotation'] = rotation
                svg = drawio_export.artwork(record, document)
                self.assertTrue(QSvgRenderer(svg).isValid())
                root = ET.fromstring(svg)
                labels = [''.join(node.itertext()) for node in root.iter()
                          if node.tag.rsplit('}', 1)[-1] == 'text']
                self.assertIn('PT', labels)
                self.assertIn('203', labels)
                self.assertNotIn('PT-203', labels, 'External tag must not be duplicated in component artwork')

    def test_custom_definitions_are_unchanged_and_reject_builtin_only_metadata(self):
        envelope = custom_symbols.fixture()
        original = copy.deepcopy(envelope)
        document = custom_symbols.merge(core.new_document(), envelope)
        combined = copy.deepcopy(core.catalog_for(document))
        for module in (legend_process, legend_valves, legend_instruments):
            module.apply(combined)
        self.assertEqual(combined[envelope['kind']], original['definition'])
        self.assertEqual(document['symbol_definitions'][envelope['kind']], original['definition'])
        for field, value in [('legend_reference', 'example'), ('legend_bubble', 'field'),
                             ('symbol_reference', 'example primary source'),
                             ('legend_labels', [{'text': 'X', 'rect': [0, 0, 10, 10]}])]:
            invalid = copy.deepcopy(document)
            invalid['symbol_definitions'][envelope['kind']][field] = value
            with self.subTest(field=field):
                self.assertTrue(core.validate(invalid), 'Built-in-only display annotations must not expand custom schema')


if __name__ == '__main__':
    unittest.main()
