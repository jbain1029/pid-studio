import copy
import unittest

from catalog_instruments import CATALOG
import custom_symbols


class InstrumentCatalogTests(unittest.TestCase):
    def test_all_definitions_are_valid_portable_geometry(self):
        self.assertGreaterEqual(len(CATALOG), 35)
        for kind, definition in CATALOG.items():
            with self.subTest(kind=kind):
                envelope = {'format': 'pid-studio-symbol', 'version': 1,
                            'kind': 'custom:' + kind, 'definition': definition}
                self.assertEqual([], custom_symbols.validate(envelope))

    def test_controllers_only_accept_signal_connections(self):
        for kind in ('pressure_controller', 'temperature_controller', 'flow_controller',
                     'level_controller', 'analysis_controller', 'current_pressure_converter'):
            self.assertEqual({'signal'}, set(CATALOG[kind]['port_kinds'].values()))

    def test_dp_impulse_ports_and_meter_outputs(self):
        for kind in ('pressure_indicator', 'temperature_indicator', 'flow_indicator',
                     'level_indicator', 'analysis_indicator', 'differential_pressure_indicator'):
            self.assertNotIn('signal', CATALOG[kind]['ports'])
        for kind in ('differential_pressure_indicator', 'differential_pressure_transmitter',
                     'orifice_plate', 'venturi_meter'):
            self.assertEqual('process', CATALOG[kind]['port_kinds']['high_pressure'])
            self.assertEqual('process', CATALOG[kind]['port_kinds']['low_pressure'])
        for kind in ('coriolis_meter', 'magnetic_flowmeter', 'vortex_flowmeter',
                     'ultrasonic_flowmeter', 'turbine_flowmeter', 'thermal_mass_flowmeter'):
            self.assertEqual({'inlet': 'process', 'outlet': 'process', 'signal': 'signal'},
                             CATALOG[kind]['port_kinds'])

    def test_definitions_are_independent_and_functional_tags_are_explicit(self):
        first = copy.deepcopy(CATALOG['pressure_transmitter'])
        self.assertIsNot(CATALOG['pressure_transmitter']['artwork'], CATALOG['temperature_transmitter']['artwork'])
        self.assertEqual('PT', first['prefix'])
        self.assertEqual('TT', CATALOG['temperature_transmitter']['prefix'])
        self.assertNotEqual(CATALOG['pressure_transmitter']['artwork'], CATALOG['pressure_controller']['artwork'])


if __name__ == '__main__':
    unittest.main()
