import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import copy
from pathlib import Path
import tempfile
import unittest

from PySide6.QtWidgets import QApplication
from app import Window
import connection_editor as editor
import pidcore as core

APP = QApplication.instance() or QApplication([])


class ConnectionEditorTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_edit_preserves_metadata_identity_save_undo_redo(self):
        line = self.window.document['connections'][0]
        line['metadata'] = {'size': 'DN25', 'service': 'Water'}
        before = copy.deepcopy(self.window.document)
        count = len(self.window.history)
        dialog = editor.ConnectionDialog(self.window, line['id'])
        dialog.label.setText('W-025')
        dialog.add_point([20, 100])
        dialog.add_point([180, 100])
        dialog.apply()
        changed = self.window.document['connections'][0]
        self.assertEqual(changed['metadata'], line['metadata'])
        self.assertEqual(changed['id'], line['id'])
        self.assertEqual(changed['label'], 'W-025')
        self.assertEqual(changed['waypoints'], [[20, 100], [180, 100]])
        self.assertEqual(len(self.window.history), count + 1)
        self.assertEqual({i.record['id'] for i in self.window.scene.selectedItems()}, {line['id']})
        after = copy.deepcopy(self.window.document)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'edited.pid'
            core.save(after, path)
            self.assertEqual(core.load(path), after)
        self.window.undo()
        self.assertEqual(self.window.document, before)
        self.window.redo()
        self.assertEqual(self.window.document, after)

    def test_invalid_same_endpoint_and_nonfinite_are_atomic(self):
        before = copy.deepcopy(self.window.document)
        history = copy.deepcopy(self.window.history)
        original = before['connections'][0]
        candidate = copy.deepcopy(original)
        candidate['to'] = copy.deepcopy(candidate['from'])
        with self.assertRaisesRegex(ValueError, 'different ports'):
            editor.apply_connection(self.window, candidate, original=original)
        candidate = copy.deepcopy(original)
        candidate['waypoints'] = [[float('nan'), 0]]
        with self.assertRaisesRegex(ValueError, 'finite'):
            editor.apply_connection(self.window, candidate, original=original)
        self.assertEqual(self.window.document, before)
        self.assertEqual(self.window.history, history)

    def test_create_signal_connection_requires_correct_kind(self):
        instrument = core.component('instrument', 0, 200, self.window.document)
        self.window.document['components'].append(instrument)
        controller = core.component('controller', 180, 200, self.window.document)
        self.window.document['components'].append(controller)
        self.window.rebuild()
        before = copy.deepcopy(self.window.document)
        dialog = editor.ConnectionDialog(self.window)
        for end, component, port in [('from', instrument, 'signal'), ('to', controller, 'input')]:
            box = dialog.component_boxes[end]
            box.setCurrentIndex(box.findData(component['id']))
            ports = dialog.port_boxes[end]
            ports.setCurrentIndex(ports.findData(port))
        dialog.apply()
        self.assertIn('Signal port', dialog.status.text())
        self.assertEqual(self.window.document, before)
        dialog.kind.setCurrentIndex(dialog.kind.findData('signal'))
        dialog.apply()
        self.assertEqual(len(self.window.document['connections']), len(before['connections']) + 1)
        self.assertEqual(self.window.document['connections'][-1]['kind'], 'signal')
        self.window.undo()
        self.assertEqual(self.window.document, before)

    def test_waypoint_order_reverse_and_cancel_stay_staged(self):
        before = copy.deepcopy(self.window.document)
        line = before['connections'][0]
        dialog = editor.ConnectionDialog(self.window, line['id'])
        dialog.add_point([1, 2])
        dialog.add_point([3, 4])
        dialog.move_point(-1)
        self.assertEqual(dialog.candidate()['waypoints'], [[3, 4], [1, 2]])
        dialog.reverse()
        candidate = dialog.candidate()
        self.assertEqual(candidate['from'], line['to'])
        self.assertEqual(candidate['to'], line['from'])
        self.assertEqual(candidate['waypoints'], [[1, 2], [3, 4]])
        dialog.remove_point()
        self.assertEqual(len(dialog.candidate()['waypoints']), 1)
        dialog.reject()
        self.assertEqual(self.window.document, before)

    def test_noop_and_stale_edit_do_not_checkpoint(self):
        line = self.window.document['connections'][0]
        count = len(self.window.history)
        self.assertFalse(editor.apply_connection(self.window, line, original=copy.deepcopy(line)))
        self.assertEqual(len(self.window.history), count)
        dialog = editor.ConnectionDialog(self.window, line['id'])
        self.window.document['title'] = 'Changed elsewhere'
        before = copy.deepcopy(self.window.document)
        dialog.label.setText('New label')
        dialog.apply()
        self.assertIn('drawing changed', dialog.status.text())
        self.assertEqual(self.window.document, before)
        self.assertEqual(len(self.window.history), count)

    def test_empty_drawing_reports_missing_components_without_mutation(self):
        self.window.document = core.new_document()
        self.window.rebuild()
        dialog = editor.ConnectionDialog(self.window)
        before = copy.deepcopy(self.window.document)
        dialog.apply()
        self.assertIn('Choose a component', dialog.status.text())
        self.assertEqual(self.window.document, before)


if __name__ == '__main__':
    unittest.main()
