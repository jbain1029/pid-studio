"""Compatibility and distinctive-reference checks for valve/fitting overrides."""
import copy
import unittest

import legend_valves
from catalog_valves import CATALOG


class LegendValveTests(unittest.TestCase):
    def test_metadata_and_ports_are_preserved(self):
        catalog = copy.deepcopy(CATALOG)
        original = copy.deepcopy(catalog)
        legend_valves.apply(catalog)
        for kind, definition in original.items():
            for field, value in definition.items():
                if field != 'artwork':
                    self.assertEqual(catalog[kind][field], value, (kind, field))

    def test_apply_is_idempotent_and_does_not_change_uncovered_types(self):
        catalog = copy.deepcopy(CATALOG)
        original = copy.deepcopy(catalog)
        legend_valves.apply(catalog)
        first = copy.deepcopy(catalog)
        legend_valves.apply(catalog)
        self.assertEqual(first, catalog)
        for kind in set(catalog) - set(legend_valves.MATCHES) - legend_valves.REPAIRED_KINDS - legend_valves.PRIMARY_KINDS - legend_valves.CONVENTION_KINDS:
            self.assertEqual(original[kind], catalog[kind])

    def test_repairs_do_not_claim_new_reference_coverage(self):
        catalog = copy.deepcopy(CATALOG)
        legend_valves.apply(catalog)
        for kind in legend_valves.REPAIRED_KINDS:
            self.assertNotIn(kind, legend_valves.MATCHES)
            self.assertNotIn('legend_reference', catalog[kind])

    def test_regulator_sensing_sides_join_existing_linkage(self):
        catalog = copy.deepcopy(CATALOG)
        legend_valves.apply(catalog)
        for kind, side in (('pressure_reducing_regulator', 1),
                           ('back_pressure_regulator', -1)):
            artwork = catalog[kind]['artwork']
            path = [[0, -15], [side * 8, -18], [side * 28, -18], [side * 28, 0]]
            self.assertIn(path, [p.get('points') for p in artwork])
            linkage = next(p['points'] for p in artwork
                           if p.get('points', [])[:2] == [[0, 0], [0, -15]])
            self.assertIn(path[0], linkage)
            # Geometric continuity is invariant under every supported rotation.
            for turns in range(4):
                def rotate(point):
                    x, y = point
                    for _ in range(turns):
                        x, y = -y, x
                    return [x, y]
                self.assertIn(rotate(path[0]), [rotate(p) for p in linkage])
                self.assertEqual(rotate(path[-1]), rotate([side * 28, 0]))

    def test_cross_is_filled_and_foot_gap_is_bridged_once(self):
        catalog = copy.deepcopy(CATALOG)
        legend_valves.apply(catalog)
        legend_valves.apply(catalog)
        mark = next(p for p in catalog['pipe_cross']['artwork']
                    if p.get('kind') == 'ellipse')
        self.assertEqual(mark['fill'], 'ink')
        bridge = legend_valves.line((0, 0), (0, 7))
        self.assertEqual(catalog['foot_valve']['artwork'].count(bridge), 1)
        self.assertIn(legend_valves.line((-14, -18), (14, -18)),
                      catalog['foot_valve']['artwork'])
        self.assertIn(legend_valves.rect(-18, 7, 36, 18),
                      catalog['foot_valve']['artwork'])

    def test_all_ports_retain_visible_lead_endpoints(self):
        # Legacy definitions are included after the main integration applies.
        import pidcore
        for kind, (_, artwork) in legend_valves.MATCHES.items():
            points = [point for primitive in artwork
                      for point in primitive.get('points', [])]
            for name, position in pidcore.CATALOG[kind]['ports'].items():
                self.assertIn(position, points, (kind, name))

    def test_distinguishing_globe_and_solenoid_marks(self):
        globe = legend_valves.MATCHES['globe_valve'][1]
        ball = legend_valves.MATCHES['ball_valve'][1]
        self.assertTrue(any(p.get('fill') == 'ink' for p in globe))
        self.assertFalse(any(p.get('fill') == 'ink' for p in ball))
        catalog = copy.deepcopy(CATALOG)
        legend_valves.apply(catalog)
        self.assertEqual(catalog['solenoid_valve']['legend_labels'][0]['text'],'S')
        self.assertTrue(catalog['solenoid_valve']['legend_labels'][0]['follow_body'])


if __name__ == '__main__':
    unittest.main()
