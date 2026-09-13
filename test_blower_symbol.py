"""Centrifugal blower geometry, endpoint and SVG rotation regression checks."""
import copy
import os
from pathlib import Path
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QFont, QFontDatabase, QImage, QPainter
from PySide6.QtWidgets import QApplication

import catalog_process
import custom_symbols
import pidcore
import verify_svg_catalog


class BlowerSymbolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])
        QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')

    def test_identity_and_services_are_preserved(self):
        before, after = catalog_process.CATALOG['blower'], pidcore.CATALOG['blower']
        for field in ('label', 'prefix', 'category', 'ports', 'port_kinds', 'routing_bounds'):
            self.assertEqual(before[field], after[field], field)
        self.assertEqual(custom_symbols.definition_errors(after), [])
        self.assertIn('Fig15 FAN / CENTRIFUGAL', after['legend_reference'])

    def test_scroll_and_tangential_discharge_replace_propeller(self):
        artwork = pidcore.CATALOG['blower']['artwork']
        self.assertEqual(artwork[0]['kind'], 'polygon')
        self.assertGreater(len(artwork[0]['points']), 25)
        self.assertEqual(artwork[0]['points'][:3], [[0, -26], [28, -26], [28, -10]])
        # There are no old blade triangles: only the inlet/outlet arrowheads.
        self.assertEqual(len([p for p in artwork if p['kind'] == 'polygon'
                              and len(p['points']) == 3]), 2)
        discharge = next(p for p in artwork if p['kind'] == 'polyline'
                         and p['points'][0] == [40, 0])
        self.assertEqual(discharge['points'], [[40, 0], [34, 0], [34, -18], [28, -18]])
        self.assertTrue(-26 <= discharge['points'][-1][1] <= -10)
        self.assertIn({'kind': 'polyline', 'points': [[-40, 0], [-26, 0]]}, artwork)

    def test_svg_rotation_fidelity_and_review_sheet(self):
        document = pidcore.new_document()
        record = pidcore.component('blower', 0, 0, document)
        document['components'].append(record)
        sheet = QImage(800, 220, QImage.Format.Format_ARGB32)
        sheet.fill(Qt.GlobalColor.white)
        painter = QPainter(sheet)
        painter.setFont(QFont('Segoe UI', 9))
        try:
            for index, rotation in enumerate((0, 90, 180, 270)):
                current = copy.deepcopy(record)
                current['rotation'] = rotation
                result, data, raster = verify_svg_catalog.inspect(current, document)
                self.assertTrue(result['passed'], result)
                self.assertEqual(result['clipped_pixels'], 0)
                painter.drawImage(QRectF(index*200, 0, 200, 200), raster)
                painter.drawText(QRectF(index*200, 200, 200, 20), Qt.AlignmentFlag.AlignCenter, str(rotation))
        finally:
            painter.end()
        output = Path(__file__).parent/'build'/'blower-review'
        output.mkdir(parents=True, exist_ok=True)
        self.assertTrue(sheet.save(str(output/'rotations.png')))


if __name__ == '__main__':
    unittest.main()
