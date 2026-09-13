import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import copy
import unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from app import Window
import editing

APP = QApplication.instance() or QApplication([])


class EditingTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()

    def tearDown(self):
        APP.clipboard().clear()
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_group_nudge_moves_internal_waypoints_and_undo(self):
        line = self.window.document['connections'][0]
        line['waypoints'] = [[50, 100]]
        ids = {line['from']['component'], line['to']['component']}
        for identifier in ids:
            self.window.symbols[identifier].setSelected(True)
        before = copy.deepcopy(self.window.document)
        self.assertTrue(editing.nudge(self.window, 10, -10))
        self.assertEqual(line['waypoints'], [[60, 90]])
        self.assertEqual({i.record['id'] for i in self.window.scene.selectedItems()}, ids)
        self.window.undo()
        self.assertEqual(self.window.document, before)

    def test_single_endpoint_does_not_move_external_waypoints(self):
        line = self.window.document['connections'][0]
        line['waypoints'] = [[50, 100]]
        self.window.symbols[line['from']['component']].setSelected(True)
        editing.nudge(self.window, 10, 0)
        self.assertEqual(line['waypoints'], [[50, 100]])

    def test_keys_and_repeated_rotation_preserve_selection(self):
        symbol = next(iter(self.window.symbols.values()))
        identifier = symbol.record['id']
        start = symbol.record['position'][:]
        symbol.setSelected(True)
        self.window.snap_spacing = 5
        QTest.keyClick(self.window.view, Qt.Key.Key_Right)
        QTest.keyClick(self.window.view, Qt.Key.Key_Down, Qt.KeyboardModifier.ShiftModifier)
        self.assertEqual(self.window.symbols[identifier].record['position'], [start[0] + 5, start[1] + 50])
        self.window.rotate()
        self.window.rotate()
        self.assertEqual(self.window.symbols[identifier].record['rotation'], 180)
        self.assertTrue(self.window.symbols[identifier].isSelected())
        QTest.keyClick(self.window.view, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(len(self.window.scene.selectedItems()), 9)

    def test_context_targets_and_disabled_actions(self):
        menu = editing.context_menu(self.window)
        actions = {action.text(): action for action in menu.actions()}
        self.assertFalse(actions['Delete'].isEnabled())
        self.assertFalse(actions['Copy'].isEnabled())
        menu.deleteLater()

    def test_reconnect_keeps_line_identity_metadata_and_undo(self):
        window = self.window
        line = window.document['connections'][0]
        line['label'] = 'W-001'
        line['metadata'] = {'size':'DN25','service':'Water'}
        line['waypoints'] = [[30,100]]
        original = copy.deepcopy(window.document)
        line_id = line['id']
        destination = window.document['components'][-1]
        self.assertTrue(editing.begin_reconnect(window,line_id,'to'))
        window.connect_port(destination['id'],'inlet')
        changed = window.document['connections'][0]
        self.assertEqual(changed['to'],{'component':destination['id'],'port':'inlet'})
        for field in ('id','label','metadata','waypoints','kind','from'):
            self.assertEqual(changed[field],line[field])
        self.assertIsNone(window.reconnecting)
        self.assertEqual([i.record['id'] for i in window.scene.selectedItems()],[line_id])
        window.undo()
        self.assertEqual(window.document,original)
        window.redo()
        self.assertEqual(window.document['connections'][0]['to']['component'],destination['id'])

    def test_reconnect_cancel_same_port_and_invalid_port_do_not_mutate(self):
        window = self.window
        line = window.document['connections'][0]
        original = copy.deepcopy(window.document)
        history_count = len(window.history)
        editing.begin_reconnect(window,line['id'],'to')
        window.connect_port(line['from']['component'],line['from']['port'])
        self.assertIsNotNone(window.reconnecting)
        self.assertEqual(window.document,original)
        window.connect_port(line['to']['component'],'missing-port')
        self.assertEqual(window.document,original)
        window.cancel()
        self.assertIsNone(window.reconnecting)
        editing.begin_reconnect(window,line['id'],'to')
        window.connect_port(line['to']['component'],line['to']['port'])
        self.assertIsNone(window.reconnecting)
        self.assertEqual(len(window.history),history_count)

    def test_process_line_cannot_reconnect_to_signal_port(self):
        import pidcore
        window = self.window
        instrument = pidcore.component('instrument',100,200,window.document)
        window.document['components'].append(instrument)
        window.rebuild()
        original = copy.deepcopy(window.document)
        line = window.document['connections'][0]
        editing.begin_reconnect(window,line['id'],'to')
        window.connect_port(instrument['id'],'signal')
        self.assertEqual(window.document,original)
        self.assertIn('Signal port',window.statusBar().currentMessage())
        self.assertIsNotNone(window.reconnecting)

    def test_pipe_context_reset(self):
        pipe = self.window.pipes[0]
        pipe.record['waypoints'] = [[50, 100]]
        menu = editing.context_menu(self.window, pipe)
        actions = {action.text(): action for action in menu.actions()}
        self.assertTrue(pipe.isSelected())
        self.assertFalse(actions['Rotate 90°'].isEnabled())
        actions['Reset to automatic routing'].trigger()
        self.assertEqual(pipe.record['waypoints'], [])
        self.window.undo()
        self.assertEqual(self.window.document['connections'][0]['waypoints'], [[50, 100]])
        menu.deleteLater()

    def test_source_reconnection_from_context_menu(self):
        pipe = self.window.pipes[0]
        old_destination = copy.deepcopy(pipe.record['to'])
        menu = editing.context_menu(self.window,pipe)
        actions = {action.text():action for action in menu.actions()}
        actions['Reconnect source…'].trigger()
        self.assertEqual(self.window.reconnecting,(pipe.record['id'],'from'))
        source = self.window.document['components'][-1]
        self.window.connect_port(source['id'],'outlet')
        self.assertEqual(self.window.document['connections'][0]['from'],{'component':source['id'],'port':'outlet'})
        self.assertEqual(self.window.document['connections'][0]['to'],old_destination)
        menu.deleteLater()
