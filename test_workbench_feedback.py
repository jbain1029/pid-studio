import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLineEdit
from PySide6.QtTest import QTest
from app import Window
import drafting
import classic

APP = QApplication.instance() or QApplication([])


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_grid_spacing_is_snap_multiple_and_bounded_in_pixels(self):
        for spacing in (1,5,10,25,100):
            self.window.snap_spacing = spacing
            for scale in (.15,.5,1,4):
                self.window.view.resetTransform()
                self.window.view.scale(scale,scale)
                step = drafting.grid_spacing(self.window)
                self.assertEqual(step % spacing,0)
                self.assertGreaterEqual(step*scale,8)

    def test_status_follows_real_selection_and_snap_controls(self):
        w = self.window
        next(iter(w.symbols.values())).setSelected(True)
        self.assertIn('Selected: 1',w.count_label.text())
        arrange = next(action.menu() for action in w.menuBar().actions() if action.text()=='Arrange')
        actions = {action.text():action for action in arrange.actions()}
        with patch('drafting.QInputDialog.getInt',return_value=(25,True)):
            actions['Snap spacing…'].trigger()
        self.assertIn('Snap: 25',w.count_label.text())
        actions['Snap to grid'].setChecked(False)
        self.assertIn('Snap: off',w.count_label.text())
        w.view.show_grid = False
        classic.refresh_status(w)
        self.assertIn('Grid: off',w.count_label.text())

    def test_typing_does_not_rotate_or_delete_selection(self):
        w = self.window
        symbol = next(iter(w.symbols.values()))
        symbol.setSelected(True)
        original = copy.deepcopy(w.document)
        field = QLineEdit(w)
        field.show()
        w.show()
        w.activateWindow()
        field.setFocus()
        APP.processEvents()
        QTest.keyClicks(field,'FR')
        QTest.keyClick(field,Qt.Key.Key_Delete)
        self.assertEqual(field.text(),'FR')
        self.assertEqual(w.document,original)

    def test_outline_can_select_notes(self):
        w = self.window
        w.document['notes'] = [{'id':'n1','text':'Review note','position':[100,100],'width':200}]
        w.rebuild()
        group = w.outline.topLevelItem(0).child(2)
        self.assertEqual(group.text(0),'Notes (1)')
        w.outline.itemClicked.emit(group.child(0),0)
        self.assertEqual(w.selected.record['id'],'n1')
        self.assertIn('1 notes',w.count_label.text())
