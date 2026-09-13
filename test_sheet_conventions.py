"""Original sheet template conventions; not standards certification tests."""
import copy
import tempfile
import unittest
from pathlib import Path
from test_deliverables import APP
from PySide6.QtCore import QSize
from PySide6.QtPdf import QPdfDocument
from PySide6.QtGui import QFontMetricsF
import shiboken6
from app import Window
import deliverables


class SheetConventionTests(unittest.TestCase):
    def test_identity_defaults_and_invalid_numbering(self):
        self.assertEqual(deliverables.sheet_identity({}), 'Sheet: 1 of 1')
        self.assertEqual(deliverables.sheet_identity({'sheet_number': '2', 'sheet_total': '7'}), 'Sheet: 2 of 7')
        for metadata in ({'sheet_number': '0'}, {'sheet_number': '2'}, {'sheet_total': 'x'},
                         {'sheet_total': '1.5'}, {'sheet_total': '10000'}, {'sheet_number': '-1'}):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                deliverables.sheet_identity(metadata)

    def test_frame_and_cells_inside_all_papers(self):
        for paper, (width, height, _) in deliverables.PAGES.items():
            document = {'title': 'Cooling water transfer', 'metadata': {'paper_size': paper}}
            layout = deliverables.sheet_layout(document, 1400 * height / width)
            frame = layout['frame']
            self.assertAlmostEqual(frame.left() * width / 1400, 20)
            self.assertAlmostEqual(frame.top() * width / 1400, 10)
            self.assertTrue(frame.contains(layout['drawing']))
            for rect, text, font in layout['cells']:
                self.assertTrue(frame.contains(rect), (paper, text))
                measured = QFontMetricsF(font).boundingRect(rect, deliverables.TEXT_FLAGS, text)
                self.assertLessEqual(measured.height(), rect.height(), text)
            texts = '\n'.join(text for _, text, _ in layout['cells'])
            for required in ('NOT TO SCALE', 'DRAFT - NOT FOR CONSTRUCTION', 'LINE LEGEND',
                             'Crossing lines are not connected', 'Generic instrument / control signal'):
                self.assertIn(required, texts)

    def test_pdf_records_set_identity_but_exports_only_one_page(self):
        window = Window()
        try:
            window.example()
            window.document['metadata'] = {
                'drawing_number': 'PID-207', 'owner': 'Example Utilities', 'project': 'Water transfer',
                'drawn_by': 'Drafter A', 'checked_by': 'Checker B', 'approved_by': 'Approver C',
                'document_status': 'FOR REVIEW', 'revision_label': 'B', 'date': '2026-09-11',
                'sheet_number': '2', 'sheet_total': '7', 'drawing_basis': 'PROJECT-DRG-001'}
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'conventions.pdf'
                deliverables.export_sheet(window, path)
                reader = QPdfDocument()
                try:
                    self.assertEqual(reader.load(str(path)), QPdfDocument.Error.None_)
                    self.assertEqual(reader.pageCount(), 1)
                    text = ' '.join(reader.getAllText(0).text().split())
                    for value in window.document['metadata'].values():
                        self.assertIn(value, text)
                    self.assertIn('Sheet: 2 of 7', text)
                    self.assertIn('Scale: NOT TO SCALE', text)
                    image = reader.render(0, QSize(1400, 990))
                    self.assertFalse(image.isNull())
                    output = Path(__file__).parent / 'build' / 'sheet-conventions-preview.png'
                    self.assertTrue(image.save(str(output)))
                finally:
                    reader.close()
                    shiboken6.delete(reader)
        finally:
            window.saved = copy.deepcopy(window.document)
            window.close()


if __name__ == '__main__':
    unittest.main()
