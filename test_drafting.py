import copy
import json
import unittest
from pathlib import Path
from test_editor import APP
from app import Window
import pidcore as core
import drafting
import deliverables
from PySide6.QtGui import QImage,QPainter

class DraftingTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        for n,kind in enumerate(core.CATALOG):
            self.window.document['components'].append(core.component(kind,(n%5)*180,(n//5)*170,self.window.document))
        self.window.rebuild()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_catalog_schema_and_all_symbols_render(self):
        schema = json.loads(Path(core.__file__).with_name('document.schema.json').read_text())
        self.assertEqual(schema['$defs']['component']['properties']['type']['type'],'string')
        self.assertEqual(set(core.CATALOG),set(core.catalog_for(self.window.document)))
        invalid = copy.deepcopy(self.window.document)
        invalid['components'][0]['type'] = 'custom:not_installed'
        self.assertTrue(core.validate(invalid))
        self.assertFalse(core.validate(self.window.document))
        image = QImage(1400,990,QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        deliverables.render_sheet(self.window,painter,1400,990)
        painter.end()
        self.assertFalse(image.isNull())

    def test_align_and_distribution_undo(self):
        items = list(self.window.symbols.values())[:3]
        items[1].record['position'] = [40,70]
        self.window.rebuild()
        ids = [i.record['id'] for i in items]
        for identifier in ids:
            self.window.symbols[identifier].setSelected(True)
        original = copy.deepcopy(self.window.document)
        drafting.arrange(self.window,'horizontal')
        self.assertEqual(len({self.window.symbols[i].record['position'][1] for i in ids}),1)
        drafting.arrange(self.window,'distribute_horizontal')
        self.assertEqual([self.window.symbols[i].record['position'][0] for i in ids],[0,180,360])
        self.window.undo()
        self.window.undo()
        self.assertEqual(self.window.document,original)

    def test_snap_controls_and_signal_ports(self):
        self.window.snap_spacing = 25
        self.assertEqual(drafting.snap(self.window,38),50)
        self.window.snap_enabled = False
        self.assertEqual(drafting.snap(self.window,38),38)
        controller = next(c for c in self.window.document['components'] if c['type']=='controller')
        instrument = next(c for c in self.window.document['components'] if c['type']=='instrument')
        self.window.connect_port(instrument['id'],'signal')
        self.window.connect_port(controller['id'],'input')
        line = self.window.document['connections'][-1]
        self.assertEqual(line['kind'],'signal')
        line['kind'] = 'process'
        self.assertTrue(core.validate(self.window.document))

if __name__=='__main__':
    unittest.main()
