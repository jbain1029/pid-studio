"""Every added valve/fitting is safe declarative geometry with useful ports."""
import unittest

import custom_symbols
from catalog_valves import CATALOG


class ValveCatalogTests(unittest.TestCase):
    def test_complete_definitions(self):
        self.assertGreaterEqual(len(CATALOG), 38)
        for kind, definition in CATALOG.items():
            with self.subTest(kind=kind):
                envelope = {'format': 'pid-studio-symbol', 'version': 1,
                            'kind': 'custom:' + kind,
                            'definition': {k: v for k, v in definition.items() if k != 'symbol_notes'}}
                self.assertEqual(custom_symbols.validate(envelope), [])
                if 'symbol_notes' in definition:
                    envelope['definition'] = definition
                    self.assertTrue(custom_symbols.validate(envelope))

    def test_ports_and_distinct_artwork(self):
        self.assertEqual(len(CATALOG['four_way_valve']['ports']), 4)
        self.assertEqual(CATALOG['solenoid_valve']['port_kinds']['command'], 'signal')
        self.assertEqual(CATALOG['basket_strainer']['port_kinds']['drain'], 'process')
        self.assertEqual(len(CATALOG['blind_flange']['ports']), 1)
        self.assertNotEqual(CATALOG['float_steam_trap']['artwork'], CATALOG['inverted_bucket_trap']['artwork'])
        self.assertNotEqual(CATALOG['pressure_reducing_regulator']['artwork'], CATALOG['back_pressure_regulator']['artwork'])
        self.assertEqual(CATALOG['gate_valve']['prefix'], 'HV')
        self.assertEqual(CATALOG['motor_operated_valve']['prefix'], 'MOV')
        self.assertEqual(CATALOG['solenoid_valve']['prefix'], 'SV')
        self.assertEqual(CATALOG['pneumatic_piston_valve']['prefix'], 'XV')
        self.assertEqual(CATALOG['sampling_valve']['prefix'], 'HV')
        self.assertEqual(CATALOG['pipe_cap']['artwork'][0]['points'], [[-40, 0], [8, 0]])


if __name__ == '__main__':
    unittest.main()
