import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from app import Window
import pidcore as core
import recovery

APP = QApplication.instance() or QApplication([])


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()
        self.temp.cleanup()

    def test_browser_lists_invalid_snapshot_and_readable_contents(self):
        core.save(self.window.document, self.folder / 'good.pid')
        (self.folder / 'broken.pid').write_text('{broken', encoding='utf-8')
        dialog = recovery.RecoveryDialog(self.window, self.folder)
        self.assertEqual(dialog.tree.topLevelItemCount(), 2)
        for index in range(2):
            item = dialog.tree.topLevelItem(index)
            dialog.tree.setCurrentItem(item)
            if item.text(3) == 'Ready':
                self.assertTrue(dialog.open_button.isEnabled())
                self.assertIn('TK-101', dialog.details.toPlainText())
            else:
                self.assertFalse(dialog.open_button.isEnabled())
                self.assertIn('Cannot recover', dialog.details.toPlainText())
        dialog.close()

    def test_cancel_and_invalid_load_preserve_current_work(self):
        before = copy.deepcopy(self.window.document)
        path = self.folder / 'empty.pid'
        core.save(core.new_document(), path)
        with patch.object(self.window, 'confirm_discard', return_value=False):
            self.assertFalse(recovery.restore(self.window, path))
        self.assertEqual(self.window.document, before)
        with patch.object(self.window, 'confirm_discard') as confirm, patch('recovery.QMessageBox.warning'):
            self.assertFalse(recovery.restore(self.window, self.folder / 'missing.pid'))
            confirm.assert_not_called()
        self.assertEqual(self.window.document, before)

    def test_recover_empty_snapshot_requires_save_and_keeps_original(self):
        path = self.folder / 'empty.pid'
        document = core.new_document()
        core.save(document, path)
        before = path.read_bytes()
        with patch.object(self.window, 'confirm_discard', return_value=True):
            self.assertTrue(recovery.restore(self.window, path))
        self.assertEqual(self.window.document, document)
        self.assertNotEqual(self.window.document, self.window.saved)
        self.assertIsNone(self.window.path)
        self.assertEqual(self.window.history, [])
        self.assertEqual(path.read_bytes(), before)

    def test_reloads_snapshot_at_recovery_time(self):
        path = self.folder / 'drawing.pid'
        core.save(self.window.document, path)
        dialog = recovery.RecoveryDialog(self.window, self.folder)
        revised = copy.deepcopy(self.window.document)
        revised['title'] = 'Updated while browser was open'
        core.save(revised, path)
        with patch.object(self.window, 'confirm_discard', return_value=True):
            dialog.recover()
        self.assertEqual(self.window.document, revised)

    def test_empty_browser(self):
        dialog = recovery.RecoveryDialog(self.window, self.folder)
        self.assertFalse(dialog.open_button.isEnabled())
        self.assertIn('No autosaved', dialog.details.toPlainText())
        dialog.close()
