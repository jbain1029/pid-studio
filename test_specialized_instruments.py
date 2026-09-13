import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import QApplication
import custom_symbols
import instrument_display
import pidcore as core
from verify_svg_catalog import inspect

APP = QApplication.instance() or QApplication([])


class SpecializedInstrumentTests(unittest.TestCase):
    def test_legacy_ports_and_kinds_preserved(self):
        for kind,ports,kinds in [
            ('radar_level_transmitter',{'process':[0,40],'signal':[0,-40]}, {'process':'process','signal':'signal'}),
            ('thermal_mass_flowmeter',{'inlet':[-40,0],'outlet':[40,0],'signal':[0,-40]},
             {'inlet':'process','outlet':'process','signal':'signal'})]:
            entry = core.CATALOG[kind]
            self.assertEqual(entry['ports'],ports)
            self.assertEqual(entry['port_kinds'],kinds)
            self.assertIn('symbol_reference',entry)
            self.assertNotIn('legend_reference',entry)

    def test_technology_boxes_inside_borders(self):
        for technology,radius in [(['RADAR'],20),(['THERMAL','MASS'],23)]:
            rows = instrument_display.technology_rows('FT','203',technology)
            for text,(x,y,w,h),size in rows:
                for px,py in [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]:
                    self.assertLessEqual(px*px+py*py,radius*radius)
                self.assertGreaterEqual(size,7)

    def test_svg_full_identity_and_technology_four_rotations(self):
        for kind,prefix,words in [('radar_level_transmitter','LT',['RADAR']),
                                  ('thermal_mass_flowmeter','FT',['THERMAL','MASS'])]:
            document = core.new_document()
            record = core.component(kind,0,0,document)
            document['components'].append(record)
            for tag in (prefix+'-203','AREA-10-'+prefix+'-203A-long-identity'):
                record['tag'] = tag
                for rotation in (0,90,180,270):
                    record['rotation'] = rotation
                    before = copy.deepcopy(document)
                    with self.subTest(kind=kind,tag=tag,rotation=rotation):
                        report,svg,raster = inspect(record,document)
                        self.assertTrue(report['passed'],report)
                        labels = [''.join(n.itertext()) for n in ET.fromstring(svg).iter()
                                  if n.tag.rsplit('}',1)[-1]=='text']
                        for word in [prefix,*words,'203' if tag==prefix+'-203' else tag]:
                            self.assertIn(word,labels)
                        self.assertEqual(document,before)

    def test_custom_schema_does_not_accept_builtin_layout_metadata(self):
        envelope = custom_symbols.fixture()
        document = custom_symbols.merge(core.new_document(),envelope)
        self.assertEqual(core.validate(document),[])
        document['symbol_definitions'][envelope['kind']]['instrument_technology'] = ['RADAR']
        self.assertTrue(core.validate(document))


if __name__=='__main__':
    unittest.main()
