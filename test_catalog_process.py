import json
import unittest

import custom_symbols
from catalog_process import CATALOG


class ProcessCatalogTests(unittest.TestCase):
    def test_all_definitions_pass_portable_schema_and_rotated_stub_checks(self):
        self.assertEqual(len(CATALOG), 35)
        for kind, definition in CATALOG.items():
            with self.subTest(kind=kind):
                envelope = {'format': 'pid-studio-symbol', 'version': 1,
                            'kind': 'custom:' + kind,
                            # Provenance/convention notes are built-in metadata,
                            # not part of the portable custom-artwork contract.
                            'definition': {key:value for key,value in definition.items()
                                           if key != 'symbol_notes'}}
                self.assertEqual(custom_symbols.validate(envelope), [])

    def test_distinct_components_have_distinct_geometry_and_labels(self):
        self.assertEqual(len({d['label'] for d in CATALOG.values()}), len(CATALOG))
        self.assertEqual(len({json.dumps(d['artwork'], sort_keys=True)
                              for d in CATALOG.values()}), len(CATALOG))

    def test_multistream_connections_are_explicit(self):
        for kind in ('plate_exchanger', 'shell_tube_exchanger', 'double_pipe_exchanger'):
            self.assertEqual(set(CATALOG[kind]['ports']),
                             {'process_in', 'process_out', 'utility_in', 'utility_out'})
        self.assertEqual(set(CATALOG['jacketed_reactor']['ports']),
                         {'feed', 'product', 'vent', 'jacket_in', 'jacket_out'})
        self.assertEqual(set(CATALOG['membrane_module']['ports']),
                         {'feed', 'retentate', 'permeate'})
        for definition in CATALOG.values():
            self.assertEqual(set(definition['port_kinds'].values()), {'process'})

    def test_nozzles_touch_curved_and_tapered_body_not_routing_box(self):
        definition = CATALOG['shell_tube_exchanger']
        for lead in definition['artwork'][:4]:
            (x, y), port = lead['points']
            self.assertAlmostEqual((x / 30) ** 2 + (y / 25) ** 2, 1)
            self.assertAlmostEqual(abs(x), 24)
            self.assertEqual(y, port[1])
        vessel = CATALOG['horizontal_vessel']
        self.assertEqual(vessel['artwork'][2]['points'][0], [0, -20])
        self.assertEqual(vessel['artwork'][3]['points'][0], [0, 20])
        # Cooling tower's sloping walls, not x = +/-30 bounding box.
        tower = CATALOG['cooling_tower']
        for lead in tower['artwork'][:3]:
            (x, y), port = lead['points']
            self.assertAlmostEqual(abs(x), 17 + (y + 28) * 12 / 58)
            self.assertEqual(y, port[1])
        # Open tank vent intentionally ends at the open rim; it does not run
        # through the vessel all the way to the opposite bottom wall.
        self.assertEqual(CATALOG['open_tank']['artwork'][2]['points'][0], [0, -28])


if __name__ == '__main__':
    unittest.main()
