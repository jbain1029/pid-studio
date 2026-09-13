"""New connections must be validated transactions, not partial document edits."""
import copy
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt

from app import Window
import pidcore as core
from test_editor import APP


class ConnectionValidationTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.document = core.new_document()
        for kind, x in [('pump', 0), ('tank', 240), ('instrument', 480), ('controller', 720)]:
            self.window.document['components'].append(core.component(kind, x, 0, self.window.document))
        self.window.rebuild()
        self.window.history.clear()
        # A rejection must not erase the user's redo branch.
        self.window.future = [core.new_document()]
        self.nodes = {record['type']: record['id'] for record in self.window.document['components']}

    def tearDown(self):
        APP.clipboard().clear()
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def snapshot(self):
        return copy.deepcopy((self.window.document, self.window.history, self.window.future, self.window.pending))

    def test_invalid_source_does_not_start_or_mutate_connection(self):
        for node, port in [('missing-component', 'outlet'), (self.nodes['pump'], 'missing-port')]:
            with self.subTest(node=node, port=port):
                before = self.snapshot()
                self.window.connect_port(node, port)
                self.assertEqual(self.snapshot(), before)

    def test_invalid_destination_preserves_pending_and_redo_branch(self):
        self.window.connect_port(self.nodes['pump'], 'outlet')
        for node, port in [('missing-component', 'inlet'), (self.nodes['tank'], 'missing-port')]:
            with self.subTest(node=node, port=port):
                before = self.snapshot()
                self.window.connect_port(node, port)
                self.assertEqual(self.snapshot(), before)

    def test_same_endpoint_cancels_without_undo_checkpoint(self):
        before = self.snapshot()
        self.window.connect_port(self.nodes['pump'], 'outlet')
        self.window.connect_port(self.nodes['pump'], 'outlet')
        self.assertEqual(self.snapshot(), before)

    def test_full_candidate_is_validated_before_checkpoint(self):
        self.window.connect_port(self.nodes['pump'], 'outlet')
        before = self.snapshot()

        def reject_candidate(candidate):
            self.assertEqual(self.snapshot(), before)
            self.assertIsNot(candidate, self.window.document)
            self.assertEqual(len(candidate['connections']), 1)
            self.assertEqual(candidate['components'], self.window.document['components'])
            return ['Synthetic validation rejection']

        with patch('app.core.validate', side_effect=reject_candidate) as validator:
            self.window.connect_port(self.nodes['tank'], 'inlet')
        validator.assert_called_once()
        self.assertEqual(self.snapshot(), before)

    def test_duplicate_generated_id_rejected_by_real_document_validation(self):
        self.window.connect_port(self.nodes['pump'], 'outlet')
        before = self.snapshot()
        with patch('app.core.uid', return_value=self.nodes['pump']):
            self.window.connect_port(self.nodes['tank'], 'inlet')
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(core.validate(self.window.document))

    def test_signal_kind_inferred_from_either_endpoint(self):
        cases = [
            ('instrument', 'signal', 'controller', 'input'),
            ('pump', 'outlet', 'instrument', 'signal'),
            ('instrument', 'signal', 'tank', 'inlet'),
        ]
        for start_kind, start_port, end_kind, end_port in cases:
            with self.subTest(start=start_kind, destination=end_kind):
                self.window.connect_port(self.nodes[start_kind], start_port)
                self.window.connect_port(self.nodes[end_kind], end_port)
                line = self.window.document['connections'][-1]
                self.assertEqual(line['kind'], 'signal')
                self.assertFalse(core.validate(self.window.document))
                self.assertIsNone(self.window.pending)

    def test_process_connection_selected_editable_and_undo_redo(self):
        before = copy.deepcopy(self.window.document)
        self.window.connect_port(self.nodes['pump'], 'outlet')
        self.window.connect_port(self.nodes['tank'], 'inlet')
        created = copy.deepcopy(self.window.document)
        line = created['connections'][0]
        self.assertEqual(line['kind'], 'process')
        self.assertEqual(line['from'], {'component': self.nodes['pump'], 'port': 'outlet'})
        self.assertEqual(line['to'], {'component': self.nodes['tank'], 'port': 'inlet'})
        self.assertEqual(len(self.window.history), 1)
        self.assertEqual(self.window.future, [])
        self.assertIsNone(self.window.pending)
        self.assertEqual([item.record['id'] for item in self.window.scene.selectedItems()], [line['id']])
        self.assertEqual(self.window.selected.record['id'], line['id'])
        label_row = next(row for row in range(self.window.properties.rowCount())
                         if self.window.properties.item(row, 0).data(Qt.ItemDataRole.UserRole) == 'label')
        self.window.properties.item(label_row, 1).setText('W-101')
        edited = copy.deepcopy(self.window.document)
        self.assertEqual(edited['connections'][0]['label'], 'W-101')
        self.assertFalse(core.validate(edited))
        self.window.undo()
        self.assertEqual(self.window.document, created)
        self.window.undo()
        self.assertEqual(self.window.document, before)
        self.window.redo()
        self.assertEqual(self.window.document, created)
        self.window.redo()
        self.assertEqual(self.window.document, edited)


if __name__ == '__main__':
    unittest.main()
