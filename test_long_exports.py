"""Synthetic long-content export regressions; no user drawing data."""
import copy
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from test_deliverables import APP
from PySide6.QtGui import QImage, QPainter, QFontMetricsF
from PySide6.QtPdf import QPdfDocument
import shiboken6
from app import Window
import pidcore as core
import deliverables


OUTPUT = Path(__file__).parent / 'build' / 'long-exports'
TITLE = 'Cooling water circulation and instrument isolation - auxiliary transfer header - TITLE-END'
NOTE = ('Verify isolation and flow direction before connection. '
        'Temperature ΔT = 20 °C; instrument reference Ω-101. ') * 5 + 'NOTE-END'
GENERAL = '\n'.join(f'{i:02d}. Verify isolation and identification on branch {i}.' for i in range(1, 13)) + '\nGENERAL-END'


class LongExportTests(unittest.TestCase):
    def setUp(self):
        OUTPUT.mkdir(parents=True, exist_ok=True)
        self.window = Window()
        self.window.document['title'] = TITLE
        self.window.document['metadata'] = {
            'project': 'Utilities - cooling water circulation and secondary supply headers - PROJECT-END',
            'drawn_by': 'Synthetic drafter', 'checked_by': 'Synthetic checker',
            'drawing_number': 'PID-UTILITY-COOLING-TRANSFER-0001',
            'revision_label': 'A', 'date': '2026-09-11', 'notes': GENERAL}
        for index, rotation in enumerate((0, 90, 180, 270)):
            record = core.component('pump', index * 220, 0, self.window.document)
            record['tag'] = f'P-Δ{index + 1}-Ω'
            record['rotation'] = rotation
            self.window.document['components'].append(record)
        self.window.document['notes'] = [{'id': core.uid(), 'text': NOTE,
                                          'position': [-50, 120], 'width': 760}]
        self.window.rebuild()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_long_scene_svg_and_sheet_exports_preserve_document(self):
        before = copy.deepcopy(self.window.document)
        self.assertFalse(core.validate(before))
        symbol = next(iter(self.window.symbols.values()))
        symbol.setSelected(True)
        self.window.export_to(OUTPUT / 'long-content.svg')
        svg_text = ' '.join(''.join(node.itertext()) for node in
                            ET.parse(OUTPUT / 'long-content.svg').iter('{http://www.w3.org/2000/svg}text'))
        normalized = ' '.join(svg_text.split())
        self.assertIn('NOTE-END', normalized)
        for record in before['components']:
            # Qt emits separate text runs for fallback Unicode glyphs.
            self.assertIn(record['tag'], ''.join(svg_text.split()))
        for paper in deliverables.PAGES:
            self.window.document['metadata']['paper_size'] = paper
            stem = 'long-content-' + paper.replace(' ', '-')
            deliverables.export_sheet(self.window, OUTPUT / (stem + '.png'))
            deliverables.export_sheet(self.window, OUTPUT / (stem + '.pdf'))
            image = QImage(str(OUTPUT / (stem + '.png')))
            self.assertFalse(image.isNull())
            self.assertEqual(image.width(), 2800)
            self.assertTrue(symbol.isSelected())
            self.assertFalse(self.window.exporting)
        self.window.document['metadata'].pop('paper_size')
        self.assertEqual(self.window.document, before)

    def test_long_metadata_pdf_contains_terminal_markers(self):
        path = OUTPUT / 'long-metadata.pdf'
        deliverables.export_sheet(self.window, path)
        reader = QPdfDocument()
        try:
            self.assertEqual(reader.load(str(path)), QPdfDocument.Error.None_)
            self.assertEqual(reader.pageCount(), 1)
            text = ' '.join(reader.getAllText(0).text().split())
            for marker in ('TITLE-END', 'PROJECT-END', 'NOTE-END', 'GENERAL-END'):
                with self.subTest(marker=marker):
                    self.assertIn(marker, text)
        finally:
            reader.close()
            shiboken6.delete(reader)

    def test_device_dpi_does_not_change_raster_typography_or_geometry(self):
        # Changing only output-device DPI formerly enlarged/clipped PDF notes
        # and labels while SVG/PDF extraction still reported hidden text.
        images = []
        self.window.exporting = True
        try:
            for dpi in (96, 150, 1200):
                image = QImage(1400, 990, QImage.Format.Format_ARGB32)
                image.setDotsPerMeterX(round(dpi / .0254))
                image.setDotsPerMeterY(round(dpi / .0254))
                painter = QPainter(image)
                try:
                    deliverables.render_sheet(self.window, painter, 1400, 990)
                finally:
                    painter.end()
                images.append(image)
            # Compare actual pixels, not device metadata embedded in QImage.
            baseline = bytes(images[0].constBits())
            self.assertEqual(baseline, bytes(images[1].constBits()))
            self.assertEqual(baseline, bytes(images[2].constBits()))
        finally:
            self.window.exporting = False

    def test_measured_cells_fit_all_papers_and_excessive_notes_fail_before_overwrite(self):
        for paper, (width, height, _) in deliverables.PAGES.items():
            layout = deliverables.sheet_layout(self.window.document, 1400 * height / width)
            self.assertGreaterEqual(layout['drawing'].height(), 180)
            cells = layout['cells']
            for index, (rect, text, font) in enumerate(cells):
                needed = QFontMetricsF(font).boundingRect(rect, deliverables.TEXT_FLAGS, text)
                self.assertLessEqual(needed.height(), rect.height())
                self.assertLessEqual(needed.width(), rect.width())
                for other, _, _ in cells[index + 1:]:
                    self.assertFalse(rect.intersects(other), paper)
        path = OUTPUT / 'overflow-preserves-existing.pdf'
        deliverables.export_sheet(self.window, path)
        before = path.read_bytes()
        self.window.document['metadata']['notes'] = '\n'.join(['Excessive synthetic notes'] * 1000)
        with self.assertRaisesRegex(ValueError, 'available sheet space'):
            deliverables.export_sheet(self.window, path)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(self.window.exporting)


if __name__ == '__main__':
    unittest.main()
