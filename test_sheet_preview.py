import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import copy
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QTabWidget
from PySide6.QtGui import QImage, QFontDatabase
from app import Window
import deliverables
import sheet_preview

APP = QApplication.instance() or QApplication([])
for filename in ('segoeui.ttf', 'segoeuib.ttf'):
    QFontDatabase.addApplicationFont(str(Path('C:/Windows/Fonts') / filename))


class SheetPreviewTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_preview_matches_png_and_preserves_editor(self):
        window = self.window
        window.document['metadata'] = {'drawing_number': 'PID-001', 'notes': 'Confirm connections.'}
        symbol = next(iter(window.symbols.values()))
        symbol.setSelected(True)
        before = copy.deepcopy(window.document)
        history = copy.deepcopy(window.history)
        image = sheet_preview.render_image(window)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sheet.png'
            deliverables.export_sheet(window, path)
            self.assertEqual(image, QImage(str(path)).convertToFormat(image.format()))
        self.assertEqual(window.document, before)
        self.assertEqual(window.history, history)
        self.assertTrue(symbol.isSelected())
        self.assertFalse(window.exporting)

    def test_all_paper_ratios_and_empty_document(self):
        for name, (width, height, _) in deliverables.PAGES.items():
            self.window.document['metadata'] = {'paper_size': name}
            image = sheet_preview.render_image(self.window)
            self.assertEqual(image.width(), 2800)
            self.assertEqual(image.height(), round(2800 * height / width))
        self.window.document['components'] = []
        self.window.document['connections'] = []
        self.window.rebuild()
        self.assertFalse(sheet_preview.render_image(self.window).isNull())

    def test_tab_refreshes_after_drawing_changes(self):
        window = self.window
        window.show()
        tabs = window.centralWidget().findChild(QTabWidget)
        tabs.setCurrentWidget(window.sheet_preview)
        APP.processEvents()
        self.assertEqual(len(window.sheet_preview.scene.items()), 1)
        window.document['metadata'] = {'paper_size': 'ANSI B'}
        window.changed()
        self.assertIn('ANSI B', window.sheet_preview.caption.text())
        self.assertEqual(window.sheet_preview.scene.sceneRect().height(), round(2800 * 279.4 / 431.8))
