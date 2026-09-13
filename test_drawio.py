import base64
import copy
import math
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from test_editor import APP
from app import Window
from annotations import Note
from PySide6.QtSvg import QSvgRenderer
import drawio_export
import pidcore as core

class DrawioTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_export_keeps_objects_connections_and_vector_art(self):
        self.window.document['components'][0]['tag'] = 'TK<&101'
        self.window.document['components'][2]['rotation'] = 90
        self.window.document['notes'] = [{'id':'note1','text':'Review < & >','position':[0,150],'width':200}]
        self.window.rebuild()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'test.drawio'
            drawio_export.export(self.window,path)
            file = ET.parse(path)
            wrappers = file.findall('.//object')
            self.assertEqual(len(wrappers),9)
            ids = {w.attrib['id'] for w in wrappers}
            self.assertEqual(len(ids),9)
            for cell in file.findall('.//mxCell[@edge="1"]'):
                self.assertIn(cell.attrib['source'],ids)
                self.assertIn(cell.attrib['target'],ids)
                self.assertIn('exitPerimeter=0;',cell.attrib['style'])
            for cell in file.findall('.//object/mxCell[@vertex="1"]'):
                style = cell.attrib['style']
                encoded = style.split('image=data:image/svg+xml,')[1].split(';')[0]
                self.assertTrue(QSvgRenderer(base64.b64decode(encoded)).isValid())
            self.assertEqual(wrappers[0].attrib['label'],'TK<&101')
            note = file.find('.//mxCell[@id="pid-note1"]')
            self.assertEqual(note.attrib['value'],'Review < & >')

    def test_all_symbol_artwork_is_valid_svg(self):
        for kind in core.CATALOG:
            record = core.component(kind,0,0,self.window.document)
            for rotation in (0,90,180,270):
                record['rotation'] = rotation
                self.assertTrue(QSvgRenderer(drawio_export.artwork(record)).isValid(),(kind,rotation))

    def test_note_height_follows_wrapped_and_multiline_text(self):
        long_text = 'Verify valve orientation and confirm all instrument tags. ' * 12
        notes = [
            {'id':'short','text':'Short note','position':[0,150],'width':200},
            {'id':'wrapped','text':long_text,'position':[0,200],'width':180},
            {'id':'wide','text':long_text,'position':[250,200],'width':360},
            {'id':'multiline','text':'\n'.join(f'Inspection item {n}' for n in range(12)),
             'position':[650,200],'width':200},
        ]
        self.window.document['notes'] = notes
        self.window.rebuild()
        before = copy.deepcopy(self.window.document)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'notes.drawio'
            drawio_export.export(self.window,path)
            file = ET.parse(path)
        heights = {}
        for record in notes:
            cell = file.find(f'.//mxCell[@id="pid-{record["id"]}"]')
            geometry = cell.find('mxGeometry')
            heights[record['id']] = float(geometry.attrib['height'])
            self.assertEqual(cell.attrib['value'],record['text'])
            self.assertEqual(float(geometry.attrib['width']),record['width'])
            self.assertEqual(heights[record['id']],math.ceil(Note(record,self.window).boundingRect().height()))
            self.assertIn('fontFamily=Segoe UI;',cell.attrib['style'])
            self.assertIn('spacing=0;',cell.attrib['style'])
        self.assertLess(heights['short'],80)
        self.assertGreater(heights['wrapped'],80)
        self.assertGreater(heights['multiline'],80)
        self.assertGreater(heights['wrapped'],heights['wide'])
        self.assertEqual(self.window.document,before)

if __name__=='__main__':
    unittest.main()
