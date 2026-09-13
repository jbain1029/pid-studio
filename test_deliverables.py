import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import csv
import copy
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize
from PySide6.QtPdf import QPdfDocument
from PySide6.QtGui import QImage, QFontDatabase
from app import Window
import pidcore as core
import deliverables

APP = QApplication.instance() or QApplication([])
for filename in ('segoeui.ttf','segoeuib.ttf'):
    QFontDatabase.addApplicationFont(str(Path('C:/Windows/Fonts')/filename))

class DeliverableTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()
        self.window.document['metadata'] = {'drawing_number':'PID-100','revision_label':'A','notes':'Verify valve positions.','project':'Cooling water'}

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_pdf_and_png_render(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf, png = Path(folder)/'sheet.pdf', Path(folder)/'sheet.png'
            deliverables.export_sheet(self.window,pdf)
            deliverables.export_sheet(self.window,png)
            reader = QPdfDocument()
            self.assertEqual(reader.load(str(pdf)),QPdfDocument.Error.None_)
            self.assertEqual(reader.pageCount(),1)
            self.assertFalse(reader.render(0,QSize(1400,990)).isNull())
            text = reader.getAllText(0).text()
            reader.close()
            import shiboken6
            shiboken6.delete(reader)
            self.assertIn('PID-100',text)
            self.assertIn('Verify valve positions.',text)
            self.assertEqual(QImage(str(png)).size(),QSize(2800,1980))

    def test_metadata_roundtrip_and_registers(self):
        self.window.document['components'][0]['metadata'] = {'service':'Water','manufacturer':'=unsafe spreadsheet formula'}
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder)/'drawing.pid'
            core.save(self.window.document,file)
            self.assertEqual(core.load(file),self.window.document)
            file = Path(folder)/'equipment.csv'
            deliverables.export_register(self.window,file,'equipment')
            with file.open(encoding='utf-8-sig') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows),5)
            self.assertEqual(rows[0]['service'],'Water')
            self.assertTrue(rows[0]['manufacturer'].startswith("'="))
            deliverables.export_register(self.window,file,'valves')
            with file.open(encoding='utf-8-sig') as stream:
                self.assertEqual(len(list(csv.DictReader(stream))),2)

    def test_all_paper_sizes_have_correct_physical_dimensions(self):
        import shiboken6
        with tempfile.TemporaryDirectory() as folder:
            for name,(width,height,_) in deliverables.PAGES.items():
                self.window.document['metadata']['paper_size'] = name
                path = Path(folder)/(name+'.pdf')
                deliverables.export_sheet(self.window,path)
                reader = QPdfDocument()
                try:
                    self.assertEqual(reader.load(str(path)),QPdfDocument.Error.None_)
                    size = reader.pagePointSize(0)
                    self.assertAlmostEqual(size.width()*25.4/72,width,delta=1)
                    self.assertAlmostEqual(size.height()*25.4/72,height,delta=1)
                    self.assertIn('PID-100',reader.getAllText(0).text())
                    self.assertFalse(reader.render(0,QSize(1000,700)).isNull())
                finally:
                    reader.close()
                    shiboken6.delete(reader)

if __name__ == '__main__':
    unittest.main()
