"""Explicit project conventions and representative issued-sheet regression."""
import copy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from test_deliverables import APP
from app import Window
from PySide6.QtGui import QImage, QPainter
from PySide6.QtPdf import QPdfDocument
from PySide6.QtSvg import QSvgRenderer
import shiboken6
import component_legend
import deliverables
import pidcore as core


class ProjectConventionTests(unittest.TestCase):
    def test_package_artwork_keeps_all_service_leads(self):
        for kind in ('vortex_separator','centrifugal_separator','flash_vessel'):
            definition = core.CATALOG[kind]
            endpoints = [point for primitive in definition['artwork']
                         if primitive['kind'] == 'polyline'
                         for point in (primitive['points'][0],primitive['points'][-1])]
            for port in definition['ports'].values():
                self.assertIn(list(port),endpoints,kind)
            self.assertTrue(definition['symbol_notes'])
        self.assertEqual(len(core.CATALOG['vortex_separator']['artwork']),5)
        self.assertFalse(any(p['kind']=='polygon' for p in core.CATALOG['centrifugal_separator']['artwork']))

    def test_legacy_mnemonics_are_explicit_in_issued_legend(self):
        document = core.new_document()
        for kind in ('humidity_sensor','thermocouple','inline_flowmeter','hall_speed_sensor','acoustic_sensor'):
            document['components'].append(core.component(kind,0,0,document))
        data = component_legend.artwork(document)
        for phrase in (b'not hand switch',b'not temperature controller',b'FM is',b'EHS identifies',b'UAC identifies'):
            self.assertIn(phrase,data)

    def test_specialized_instruments_and_conventions_export(self):
        folder = Path(__file__).parent / 'build' / 'reference-closeout'
        folder.mkdir(parents=True,exist_ok=True)
        window = Window()
        reader = QPdfDocument()
        try:
            document = core.new_document()
            for index,kind in enumerate(('radar_level_transmitter','thermal_mass_flowmeter',
                    'plate_exchanger','double_pipe_exchanger','vortex_separator','centrifugal_separator')):
                record = core.component(kind,(index%3)*220,(index//3)*210,document)
                record['rotation'] = (index%4)*90
                document['components'].append(record)
            window.document = document
            window.rebuild()
            before = copy.deepcopy(document)
            window.export_to(folder/'drawing.svg')
            labels = ' '.join(''.join(n.itertext()) for n in ET.parse(folder/'drawing.svg').iter()
                              if n.tag.rsplit('}',1)[-1]=='text')
            for word in ('RADAR','THERMAL','MASS'):
                self.assertIn(word,labels)
            deliverables.export_sheet(window,folder/'drawing.pdf')
            deliverables.export_sheet(window,folder/'drawing.png')
            self.assertEqual(reader.load(str(folder/'drawing.pdf')),QPdfDocument.Error.None_)
            text = reader.getAllText(0).text()
            for word in ('RADAR','THERMAL','MASS'):
                self.assertIn(word,text)
            component_legend.export(document,folder/'legend.svg')
            renderer = QSvgRenderer(str(folder/'legend.svg'))
            self.assertTrue(renderer.isValid())
            image = QImage(renderer.defaultSize(),QImage.Format.Format_ARGB32)
            image.fill(0xffffffff)
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
            self.assertTrue(image.save(str(folder/'legend.png')))
            self.assertEqual(document,before)
        finally:
            reader.close()
            shiboken6.delete(reader)
            window.saved = copy.deepcopy(window.document)
            window.close()


if __name__ == '__main__':
    unittest.main()
