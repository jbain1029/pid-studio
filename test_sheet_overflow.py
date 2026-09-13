import copy
import unittest
from test_editor import APP
from app import Window


class SheetOverflowTests(unittest.TestCase):
    def test_preview_clears_stale_sheet_and_recovers_without_document_loss(self):
        window = Window()
        try:
            window.example()
            window.sheet_preview.refresh()
            self.assertTrue(window.sheet_preview.scene.items())
            window.document.setdefault('metadata',{})['notes'] = 'Long metadata line\n' * 500
            before = copy.deepcopy(window.document)
            window.sheet_preview.refresh()
            self.assertEqual(window.document,before)
            self.assertFalse(window.sheet_preview.scene.items())
            self.assertIn('Cannot preview sheet',window.sheet_preview.caption.text())
            self.assertFalse(window.sheet_preview.rendering)
            self.assertFalse(window.exporting)
            window.document['metadata']['notes'] = 'Short note'
            window.sheet_preview.refresh()
            self.assertTrue(window.sheet_preview.scene.items())
            self.assertNotIn('Cannot preview',window.sheet_preview.caption.text())
        finally:
            window.saved = copy.deepcopy(window.document)
            window.close()
            APP.processEvents()
