"""Endpoint and geometry contracts for the supplied-legend process redraw."""
import copy
import unittest

import custom_symbols
import legend_process
import pidcore
from routing import clear


class LegendProcessTests(unittest.TestCase):
    def setUp(self):
        self.before = copy.deepcopy(pidcore.CATALOG)
        self.after = copy.deepcopy(self.before)
        legend_process.apply(self.after)

    def test_saved_identity_and_ports_are_preserved(self):
        self.assertEqual(set(self.before), set(self.after))
        covered = [k for k, d in self.after.items()
                   if d.get('legend_reference', '').startswith('pid-legend.pdf:')]
        self.assertEqual(len(covered), 30)
        for kind in covered:
            for field in ('label', 'prefix', 'ports', 'port_kinds', 'category'):
                self.assertEqual(self.before[kind][field], self.after[kind][field], (kind, field))
            self.assertEqual(custom_symbols.definition_errors(self.after[kind]), [], kind)
            # Every saved endpoint remains the exact beginning of a nozzle.
            starts = [p['points'][0] for p in self.after[kind]['artwork']
                      if p['kind'] == 'polyline']
            for point in self.after[kind]['ports'].values():
                self.assertIn(point, starts, kind)

    def test_multi_circuit_nozzles_and_stirrer_are_explicit(self):
        def nozzle(kind, port):
            d = self.after[kind]
            return next(p['points'] for p in reversed(d['artwork'])
                        if p['kind'] == 'polyline' and p['points'][0] == d['ports'][port])
        self.assertEqual(nozzle('double_pipe_exchanger', 'process_in')[-1], [-28, 0])
        self.assertEqual(nozzle('double_pipe_exchanger', 'utility_in')[-1], [28, -15])
        self.assertEqual(nozzle('jacketed_reactor', 'feed')[-1], [-23, -12])
        self.assertEqual(nozzle('jacketed_reactor', 'product')[-1], [0, 27])
        self.assertNotEqual(nozzle('agitated_tank', 'vent')[-1][0], 0)
        self.assertNotEqual(nozzle('jacketed_reactor', 'vent')[-1][0], 0)

    def test_unsupported_subtypes_not_substituted(self):
        for kind in ('lobe_pump', 'metering_pump', 'membrane_module',
                     'steam_separator', 'flash_vessel', 'conical_tank'):
            self.assertEqual(self.before[kind], self.after[kind])

    def test_open_tank_vent_adapters_touch_rim_without_dip_pipe(self):
        import catalog_process
        for kind in ('open_tank', 'floating_roof_tank'):
            definition = self.after[kind]
            original = catalog_process.CATALOG[kind]
            self.assertEqual(definition['ports'], original['ports'])
            self.assertEqual(definition['port_kinds'], original['port_kinds'])
            endpoint = definition['ports']['vent']
            adapters = [p for p in definition['artwork'] if p['kind'] == 'polyline'
                        and endpoint in (p['points'][0], p['points'][-1])]
            self.assertEqual(len(adapters), 1)
            self.assertEqual(adapters[0]['points'], [[0, -40], [28, -40], [28, -28]])
            # The adapter remains above the opening/roof, never entering liquid.
            self.assertTrue(all(y <= -28 for x, y in adapters[0]['points']))
            self.assertTrue(any(p['kind'] == 'polyline' and [28, -28] in p['points']
                                for p in original['artwork']))
            other_before = [p for p in original['artwork'] if not
                            (p['kind'] == 'polyline' and endpoint in
                             (p['points'][0], p['points'][-1]))]
            other_after = [p for p in definition['artwork'] if p is not adapters[0]]
            self.assertEqual(other_after, other_before)

    def test_round_pump_envelopes_block_near_body_routes(self):
        for kind in ('screw_pump', 'reciprocating_pump'):
            definition = self.after[kind]
            self.assertIn({'kind': 'ellipse', 'rect': [-24, -24, 48, 48]}, definition['artwork'])
            left, top, right, bottom = definition['routing_bounds']
            self.assertLessEqual(left, -25)
            self.assertLessEqual(top, -25)
            self.assertGreaterEqual(right, 25)
            self.assertGreaterEqual(bottom, 25)
            self.assertFalse(clear((-40, 22), (40, 22), [tuple(definition['routing_bounds'])]))
            self.assertEqual(custom_symbols.definition_errors(definition), [])

    def test_turbine_outlet_starts_on_sloped_body(self):
        definition = self.after['turbine']
        body = definition['artwork'][0]['points']
        lower_right, lower_left = body[2], body[3]
        x = definition['ports']['outlet'][0]
        contact_y = lower_left[1] + ((x-lower_left[0]) /
                    (lower_right[0]-lower_left[0]))*(lower_right[1]-lower_left[1])
        nozzle = next(p for p in definition['artwork'] if p['kind'] == 'polyline'
                      and p['points'][-1] == definition['ports']['outlet'])
        self.assertEqual(nozzle['points'][0], [x, contact_y])
        self.assertEqual(definition['ports']['outlet'], [0, 45])
        self.assertEqual(definition['port_kinds']['shaft'], 'signal')

    def test_repeat_application_is_stable(self):
        again = copy.deepcopy(self.after)
        legend_process.apply(again)
        self.assertEqual(again, self.after)


if __name__ == '__main__':
    unittest.main()
