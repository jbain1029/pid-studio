"""Remaining adopted illustrative conventions must accompany issued drawings."""
import copy
import unittest
import xml.etree.ElementTree as ET
from test_deliverables import APP
import component_legend
import pidcore as core


PHRASES = {
    **{kind: 'not a trap set' for kind in (
        'float_steam_trap', 'inverted_bucket_trap', 'thermodynamic_steam_trap',
        'thermostatic_steam_trap', 'bimetallic_steam_trap')},
    **{kind: 'manual gate/isolation' for kind in ('drain_valve', 'vent_valve', 'sampling_valve')},
    'pressure_vacuum_vent': 'inward vacuum admission',
    'filter': 'solid diagonal',
    'connector': 'Graphic-only off-page',
    'open_tank': 'rim-connected',
    'floating_roof_tank': 'rim-connected',
    'density_transmitter': 'DT means density transmitter',
    'current_pressure_converter': 'current input at input',
    'level_gauge': 'not a T function code',
}


class FinalConventionNoteTests(unittest.TestCase):
    def test_conventions_export_without_document_mutation(self):
        document = core.new_document()
        for kind in PHRASES:
            document['components'].append(core.component(kind, 0, 0, document))
        before = copy.deepcopy(document)
        root = ET.fromstring(component_legend.artwork(document))
        text = ' '.join(' '.join(root.itertext()).split())
        for kind, phrase in PHRASES.items():
            self.assertIn(phrase, ' '.join(core.CATALOG[kind]['symbol_notes']), kind)
            self.assertIn(phrase, text, kind)
        self.assertNotIn('Verify the adopted convention.', text)
        self.assertEqual(document, before)
        self.assertEqual(core.validate(document), [])

    def test_builtin_notes_do_not_enter_component_save_records(self):
        document = core.new_document()
        for kind in PHRASES:
            record = core.component(kind, 0, 0, document)
            self.assertNotIn('symbol_notes', record)
            document['components'].append(record)
        self.assertEqual(core.validate(document), [])


if __name__ == '__main__':
    unittest.main()
