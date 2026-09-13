import copy
from pathlib import Path
import tempfile
import unittest

from test_editor import APP
from app import Window
import connection_editor
import connection_policy
import diagnostics
import editing
import operations
import pidcore as core


class AttachmentConnectionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.document = core.new_document()
        self.turbine = core.component('turbine', 0, 0, self.window.document)
        self.sensor = core.component('hall_speed_sensor', 160, 0, self.window.document)
        self.instrument = core.component('instrument', 320, 0, self.window.document)
        self.window.document['components'] = [self.turbine, self.sensor, self.instrument]
        self.window.rebuild()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def line(self):
        return {'id': core.uid(), 'from': {'component': self.turbine['id'], 'port': 'shaft'},
                'to': {'component': self.sensor['id'], 'port': 'pickup'},
                'kind': 'signal', 'label': 'Legacy', 'waypoints': [], 'metadata': {'service': 'Historic'}}

    def test_all_five_illustrative_handles_reject_new_links(self):
        for kind in ('turbine', 'hall_speed_sensor', 'acoustic_sensor', 'heating_coil', 'thermocouple'):
            component = core.component(kind, 0, 0, self.window.document)
            self.window.document['components'].append(component)
            for port in core.CATALOG[kind]['port_meanings']:
                line = self.line()
                line['from'] = {'component': component['id'], 'port': port}
                with self.assertRaisesRegex(ValueError, 'drawing note'):
                    connection_policy.require_supported_connection(self.window.document, line)

    def test_click_guard_is_atomic_for_source_and_destination(self):
        before = copy.deepcopy(self.window.document)
        count = len(self.window.history)
        self.assertFalse(self.window.connect_port(self.turbine['id'], 'shaft'))
        self.assertIsNone(self.window.pending)
        self.assertIn('illustrative attachment', self.window.statusBar().currentMessage())
        self.window.connect_port(self.instrument['id'], 'signal')
        pending = copy.deepcopy(self.window.pending)
        self.assertFalse(self.window.connect_port(self.sensor['id'], 'pickup'))
        self.assertEqual(self.window.pending, pending)
        self.assertEqual(self.window.document, before)
        self.assertEqual(len(self.window.history), count)

    def test_dialog_creation_rejected_and_port_description_explicit(self):
        before = copy.deepcopy(self.window.document)
        with self.assertRaisesRegex(ValueError, 'no.*|does not support'):
            connection_editor.apply_connection(self.window, self.line())
        dialog = connection_editor.ConnectionDialog(self.window)
        box = dialog.component_boxes['from']
        box.setCurrentIndex(box.findData(self.turbine['id']))
        ports = dialog.port_boxes['from']
        self.assertIn('illustrative attachment', ports.itemText(ports.findData('shaft')))
        self.assertEqual(self.window.document, before)
        dialog.reject()

    def test_legacy_edit_save_reopen_undo_and_review_preserved(self):
        original = self.line()
        self.window.document['connections'] = [original]
        self.window.rebuild()
        before = copy.deepcopy(self.window.document)
        changed = copy.deepcopy(original)
        changed['label'] = 'Explicit legacy review'
        changed['waypoints'] = [[80, 120]]
        self.assertTrue(connection_editor.apply_connection(self.window, changed, original=original))
        after = copy.deepcopy(self.window.document)
        self.assertEqual(after['connections'][0]['metadata'], original['metadata'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'legacy.pid'
            core.save(after, path)
            self.assertEqual(core.load(path), after)
        self.assertTrue(any('Legacy attachment semantics' in text for _, _, text in diagnostics.inspect(after)))
        self.window.undo()
        self.assertEqual(self.window.document, before)
        self.window.redo()
        self.assertEqual(self.window.document, after)

    def test_reconnect_legacy_link_cannot_create_new_pair(self):
        original = self.line()
        self.window.document['connections'] = [original]
        self.window.rebuild()
        before = copy.deepcopy(self.window.document)
        count = len(self.window.history)
        editing.begin_reconnect(self.window, original['id'], 'to')
        self.assertFalse(editing.finish_reconnect(self.window,
            {'component': self.instrument['id'], 'port': 'signal'}))
        self.assertIn('drawing note', self.window.statusBar().currentMessage())
        self.assertEqual(self.window.document, before)
        self.assertEqual(len(self.window.history), count)

    def test_legacy_direction_reverse_does_not_create_a_new_relationship(self):
        original = self.line()
        self.window.document['connections'] = [original]
        self.window.rebuild()
        candidate = copy.deepcopy(original)
        candidate['from'], candidate['to'] = candidate['to'], candidate['from']
        self.assertTrue(connection_editor.apply_connection(self.window, candidate, original=original))
        self.assertEqual(self.window.document['connections'][0]['from'], original['to'])
        self.assertEqual(self.window.document['connections'][0]['metadata'], original['metadata'])

    def test_authoring_rejects_new_link_but_retains_legacy_label_edit(self):
        document = self.window.document
        before = copy.deepcopy(document)
        line = self.line()
        proposal = {'contract_version': 1, 'base_fingerprint': operations.fingerprint(document),
                    'operations': [{'operation': 'add_connection', 'value': line}], 'issues': []}
        with self.assertRaisesRegex(ValueError, 'illustrative attachment'):
            operations.apply(document, proposal)
        self.assertEqual(document, before)
        document['connections'].append(line)
        proposal['base_fingerprint'] = operations.fingerprint(document)
        proposal['operations'] = [{'operation': 'update_connection', 'id': line['id'],
                                   'changes': {'label': 'Retained for review'}}]
        result = operations.apply(document, proposal)
        self.assertEqual(result['connections'][0]['from'], line['from'])
        self.assertEqual(result['connections'][0]['label'], 'Retained for review')


if __name__ == '__main__':
    unittest.main()
