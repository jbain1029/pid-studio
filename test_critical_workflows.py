"""Real Qt event delivery for critical editor gestures (no native dialogs)."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_editor import APP
from PySide6.QtCore import QPointF, Qt, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox
from app import Window
import pidcore as core


class CriticalWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.window = Window()
        self.window.recovery_file = self.folder / 'owned.pid'
        self.window.resize(1280, 900)
        self.window.show()
        APP.processEvents()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()
        APP.processEvents()
        self.temp.cleanup()

    def test_toolbox_double_click_inserts_and_undo_restores(self):
        palette = self.window.palette
        item = palette.leaves['tank']
        parent = item.parent()
        while parent:
            parent.setExpanded(True)
            parent = parent.parent()
        palette.scrollToItem(item)
        APP.processEvents()
        point = palette.visualItemRect(item).center()
        before = copy.deepcopy(self.window.document)
        QTest.mouseClick(palette.viewport(), Qt.MouseButton.LeftButton, pos=point)
        QTest.mouseDClick(palette.viewport(), Qt.MouseButton.LeftButton, pos=point)
        QTest.mouseRelease(palette.viewport(), Qt.MouseButton.LeftButton, pos=point)
        APP.processEvents()
        self.assertEqual(len(self.window.document['components']), 1)
        self.assertEqual(self.window.document['components'][0]['type'], item.data(0, Qt.ItemDataRole.UserRole))
        self.assertFalse(core.validate(self.window.document))
        self.window.undo()
        self.assertEqual(self.window.document, before)

    def test_symbol_drop_delivered_through_viewport_inserts_at_snapped_position(self):
        # Exercise Qt's viewport drag/drop dispatch, not a direct dropEvent call.
        view = self.window.view
        point = view.viewport().rect().center()
        scene_point = view.mapToScene(point)
        mime = QMimeData()
        mime.setData('application/x-pid-symbol', b'pump')
        enter = QDragEnterEvent(point, Qt.DropAction.CopyAction, mime,
                               Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        APP.sendEvent(view.viewport(), enter)
        self.assertTrue(enter.isAccepted())
        drop = QDropEvent(QPointF(point), Qt.DropAction.CopyAction, mime,
                          Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        APP.sendEvent(view.viewport(), drop)
        APP.processEvents()
        self.assertTrue(drop.isAccepted())
        self.assertEqual(len(self.window.document['components']), 1)
        record = self.window.document['components'][0]
        self.assertEqual(record['type'], 'pump')
        self.assertEqual(record['position'], [round(scene_point.x()/10)*10, round(scene_point.y()/10)*10])
        self.assertFalse(core.validate(self.window.document))

    def test_pipe_double_click_and_waypoint_drag_are_undoable(self):
        self.window.example()
        self.window.view.resetTransform()
        self.window.view.centerOn(320, 0)
        APP.processEvents()
        pipe = self.window.pipes[1]
        view = self.window.view
        point = view.mapFromScene(pipe.path().pointAtPercent(.5))
        before = copy.deepcopy(self.window.document)
        QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton, pos=point)
        QTest.mouseDClick(view.viewport(), Qt.MouseButton.LeftButton, pos=point)
        QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, pos=point)
        APP.processEvents()
        self.assertEqual(len(pipe.record['waypoints']), 1)
        self.assertTrue(pipe.handles[0].isVisible())
        waypoint_added = copy.deepcopy(self.window.document)
        start = view.mapFromScene(pipe.handles[0].scenePos())
        end = view.mapFromScene(pipe.handles[0].scenePos() + QPointF(0, 80))
        QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(view.viewport(), end, delay=20)
        QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, pos=end)
        APP.processEvents()
        self.assertEqual(pipe.record['waypoints'][0][1], waypoint_added['connections'][1]['waypoints'][0][1] + 80)
        self.assertFalse(pipe.route_error)
        self.assertFalse(core.validate(self.window.document))
        moved = copy.deepcopy(self.window.document)
        self.window.undo()
        self.assertEqual(self.window.document, waypoint_added)
        self.window.undo()
        self.assertEqual(self.window.document, before)
        self.window.redo()
        self.window.redo()
        self.assertEqual(self.window.document, moved)

    def test_dirty_close_cancel_and_save_dialog_cancel_preserve_work_and_recovery(self):
        self.window.add_symbol('pump', QPointF(0, 0))
        self.window.recovery_timer.timeout.emit()
        before = copy.deepcopy(self.window.document)
        snapshot = self.window.recovery_file.read_bytes()
        history = copy.deepcopy(self.window.history)
        with patch('app.QMessageBox.question', return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.window.close())
        with patch('app.QMessageBox.question', return_value=QMessageBox.StandardButton.Save), \
             patch('app.QFileDialog.getSaveFileName', return_value=('', '')):
            self.assertFalse(self.window.close())
        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.recovery_timer.isActive())
        self.assertIsNone(self.window.path)
        self.assertEqual(self.window.document, before)
        self.assertEqual(self.window.history, history)
        self.assertEqual(self.window.recovery_file.read_bytes(), snapshot)

    def test_successful_save_on_close_removes_only_owned_snapshot(self):
        self.window.add_symbol('tank', QPointF(0, 0))
        self.window.recovery_timer.timeout.emit()
        other = self.folder / 'another-session.pid'
        core.save(core.new_document(), other)
        other_bytes = other.read_bytes()
        target = self.folder / 'saved drawing.pid'
        expected = copy.deepcopy(self.window.document)
        with patch('app.QMessageBox.question', return_value=QMessageBox.StandardButton.Save), \
             patch('app.QFileDialog.getSaveFileName', return_value=(str(target), '')):
            self.assertTrue(self.window.close())
        self.assertEqual(core.load(target), expected)
        self.assertFalse(self.window.recovery_file.exists())
        self.assertEqual(other.read_bytes(), other_bytes)
        self.assertFalse(self.window.recovery_timer.isActive())

    def test_failed_save_on_close_preserves_document_and_snapshot(self):
        self.window.add_symbol('pump', QPointF(0, 0))
        self.window.recovery_timer.timeout.emit()
        expected = copy.deepcopy(self.window.document)
        snapshot = self.window.recovery_file.read_bytes()
        with patch('app.QMessageBox.question', return_value=QMessageBox.StandardButton.Save), \
             patch('app.QFileDialog.getSaveFileName', return_value=(str(self.folder / 'target.pid'), '')), \
             patch('app.core.save', side_effect=OSError('Synthetic disk full')), \
             patch('app.QMessageBox.warning') as warning:
            self.assertFalse(self.window.close())
        warning.assert_called_once()
        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.recovery_timer.isActive())
        self.assertIsNone(self.window.path)
        self.assertEqual(self.window.document, expected)
        self.assertNotEqual(self.window.document, self.window.saved)
        self.assertEqual(self.window.recovery_file.read_bytes(), snapshot)


if __name__ == '__main__':
    unittest.main()
