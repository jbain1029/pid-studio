import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import custom_symbols as symbols
import pidcore as core


class CustomSymbolCoreTests(unittest.TestCase):
    def test_fixture_document_round_trip_and_geometry(self):
        envelope = symbols.fixture()
        self.assertEqual([], symbols.validate(envelope))
        original = core.new_document()
        document = symbols.merge(original, envelope)
        self.assertNotIn('symbol_definitions', original)
        record = core.component(envelope['kind'], 100, 200, document)
        document['components'].append(record)
        self.assertEqual('SG-101', record['tag'])
        self.assertEqual((80, 185, 120, 215), core.routing_bounds(record, document=document))
        record['rotation'] = 90
        self.assertEqual((85, 180, 115, 220), core.routing_bounds(record, document=document))
        self.assertEqual('process', core.port_kind(document, {'component': record['id'], 'port': 'inlet'}))
        self.assertEqual([], core.validate(document))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'custom.pid'
            core.save(document, path)
            self.assertEqual(document, core.load(path))

    def test_symbol_file_roundtrip_and_atomic_failure(self):
        envelope = symbols.fixture()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sight.pid-symbol'
            symbols.save(envelope, path)
            self.assertEqual(envelope, symbols.load(path))
            original = path.read_bytes()
            with patch.object(symbols.os, 'replace', side_effect=OSError('locked')):
                with self.assertRaises(OSError):
                    symbols.save(envelope, path)
            self.assertEqual(original, path.read_bytes())
            self.assertEqual([path], list(Path(folder).iterdir()))

    def test_unknown_and_conflicting_definitions(self):
        envelope = symbols.fixture()
        document = symbols.merge(core.new_document(), envelope)
        self.assertEqual(document, symbols.merge(document, envelope))
        changed = copy.deepcopy(envelope)
        changed['definition']['label'] = 'Different'
        before = copy.deepcopy(document)
        with self.assertRaises(ValueError):
            symbols.merge(document, changed)
        self.assertEqual(before, document)
        document['components'].append(core.component('pump', 0, 0, document))
        document['components'][0]['type'] = 'custom:missing'
        self.assertTrue(any('Unknown component type' in e for e in core.validate(document)))

    def test_rejects_invalid_geometry_and_resources(self):
        changes = [
            ('port_kinds', {'inlet': 'process'}),
            ('ports', {'inlet': [0, 0], 'outlet': [40, 0]}),
            ('ports', {'inlet': [-5, 0], 'outlet': [40, 0]}),
            ('ports', {'inlet': [-40, 0], 'outlet': [-40, 0]}),
            ('routing_bounds', [20, -15, -20, 15]),
            ('routing_bounds', [-20, -15, 20, float('nan')]),
            ('artwork', [{'kind': 'rect', 'rect': [40, 0, 10, 10]}]),
            ('artwork', [{'kind': 'ellipse', 'rect': [0, 0, 0, 10]}]),
            ('artwork', [{'kind': 'line', 'points': [[0, 0], [float('nan'), 1]]}]),
            ('artwork', [{'kind': 'svg', 'url': 'https://example.com'}]),
            ('artwork', [{'kind': 'line', 'points': [[0, 0], [46, 1]]}]),
        ]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                envelope = symbols.fixture()
                envelope['definition'][field] = value
                self.assertTrue(symbols.validate(envelope))
                with self.assertRaises(ValueError):
                    symbols.merge(core.new_document(), envelope)

    def test_limits_and_no_builtin_shadowing(self):
        envelope = symbols.fixture()
        envelope['kind'] = 'pump'
        self.assertTrue(symbols.validate(envelope))
        document = core.new_document()
        document['symbol_definitions'] = {'pump': symbols.fixture()['definition']}
        self.assertTrue(core.validate(document))
        document['symbol_definitions'] = {f'custom:s{i}': symbols.fixture()['definition'] for i in range(65)}
        self.assertTrue(core.validate(document))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'large.pid-symbol'
            with path.open('wb') as stream:
                stream.write(b' ' * (symbols.MAX_FILE_BYTES + 1))
            with self.assertRaisesRegex(ValueError, '256 KB'):
                symbols.load(path)

    def test_outward_stubs_clear_offset_bodies(self):
        # Merely being outside the body does not ensure the inferred radial
        # direction exits it. Check all four directions and diagonal ties.
        cases = [
            ([10, -10, 30, 10], [5, 0]),
            ([-30, -10, -10, 10], [-5, 0]),
            ([-10, 10, 10, 30], [0, 5]),
            ([-10, -30, 10, -10], [0, -5]),
            ([-10, 10, 10, 30], [5, 5]),
            # At zero degrees this tie chooses clear +Y, but at90 it chooses
            # the transformed +X direction and collides with this offset body.
            ([10, -10, 30, 10], [5, 5]),
        ]
        for bounds, port in cases:
            with self.subTest(bounds=bounds, port=port):
                envelope = symbols.fixture()
                definition = envelope['definition']
                definition['routing_bounds'] = bounds
                definition['ports']['inlet'] = port
                self.assertTrue(any('outward routing stub' in e for e in symbols.validate(envelope)))
                document = core.new_document()
                document['symbol_definitions'] = {envelope['kind']: definition}
                self.assertTrue(any('outward routing stub' in e for e in core.validate(document)))
        envelope = symbols.fixture()
        envelope['definition']['ports']['inlet'] = [-20, 0]
        self.assertEqual([], symbols.validate(envelope))

    def test_deeply_nested_file_has_controlled_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'nested.pid-symbol'
            with path.open('wb') as stream:
                stream.write(b'[' * 4000 + b'0' + b']' * 4000)
            with self.assertRaisesRegex(ValueError, 'nested too deeply'):
                symbols.load(path)


if __name__ == '__main__':
    unittest.main()
