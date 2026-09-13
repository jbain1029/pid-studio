"""Primary-source alternatives preserve saved connection contracts."""
import copy
import unittest

import legend_valves
from catalog_valves import CATALOG


class PrimaryValveSymbolsTests(unittest.TestCase):
    def catalog(self):
        catalog = copy.deepcopy(CATALOG)
        catalog['relief_valve'] = {
            'label': 'Pressure relief valve', 'prefix': 'PSV',
            'category': 'Valves & Actuators',
            'ports': {'inlet': [-40, 0], 'outlet': [40, 0]},
            'port_kinds': {'inlet': 'process', 'outlet': 'process'},
            'routing_bounds': [-21, -41, 21, 16]}
        return catalog

    def test_contract_and_coverage_are_preserved(self):
        catalog = self.catalog()
        before = copy.deepcopy(catalog)
        legend_valves.apply(catalog)
        for kind in legend_valves.PRIMARY_KINDS:
            for key in ('label', 'prefix', 'category', 'ports', 'port_kinds', 'routing_bounds'):
                self.assertEqual(catalog[kind][key], before[kind][key])
            self.assertNotIn(kind, legend_valves.MATCHES)
            self.assertNotIn('legend_reference', catalog[kind])
            self.assertIn('https://', catalog[kind]['symbol_reference'])
        first = copy.deepcopy(catalog)
        legend_valves.apply(catalog)
        self.assertEqual(first, catalog)

    def test_foot_upright_seat_and_composite_strainer(self):
        catalog = self.catalog()
        legend_valves.apply(catalog)
        definition = catalog['foot_valve']
        self.assertIn('composite', definition['symbol_reference'])
        self.assertIn(legend_valves.polygon((-13, 0), (0, -18), (13, 0)), definition['artwork'])
        self.assertIn(legend_valves.line((-14, -18), (14, -18)), definition['artwork'])
        self.assertIn(legend_valves.rect(-18, 7, 36, 18), definition['artwork'])
        self.assertIn(legend_valves.line((0, 0), (0, 7)), definition['artwork'])

    def test_relief_right_half_and_curve_are_distinct(self):
        catalog = self.catalog()
        legend_valves.apply(catalog)
        artwork = catalog['relief_valve']['artwork']
        bodies = [p for p in artwork if p['kind'] == 'polygon']
        self.assertEqual(len(bodies), 2)
        self.assertNotIn('fill', bodies[0])
        self.assertEqual(bodies[1]['fill'], 'ink')
        self.assertEqual(bodies[1]['points'], [[18, -11], [0, 0], [18, 11]])
        self.assertFalse(any(p['kind'] == 'rect' for p in artwork))
        curve = artwork[-1]['points']
        self.assertEqual(len(curve), 25)
        self.assertEqual(curve[0], [8, -24])
        self.assertEqual(curve[-1], [-8, 14])

    def test_all_rotated_ports_still_have_lead_endpoints(self):
        catalog = self.catalog()
        legend_valves.apply(catalog)
        for kind in legend_valves.PRIMARY_KINDS:
            points = [point for primitive in catalog[kind]['artwork']
                      for point in primitive.get('points', [])]
            for turns in range(4):
                def rotate(point):
                    x, y = point
                    for _ in range(turns):
                        x, y = -y, x
                    return [x, y]
                for position in catalog[kind]['ports'].values():
                    self.assertIn(rotate(position), [rotate(p) for p in points])


if __name__ == '__main__':
    unittest.main()
