import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
import tempfile
import unittest

from PySide6.QtWidgets import QApplication
import pidcore as core
import routing
from verify_svg_catalog import inspect

APP = QApplication.instance() or QApplication([])


class ThermowellAssemblyTests(unittest.TestCase):
    def test_assembly_name_and_legacy_identity_contract(self):
        entry = core.CATALOG['thermowell']
        self.assertEqual(entry['label'], 'Temperature element in thermowell (assembly)')
        self.assertEqual(entry['prefix'], 'TE')
        self.assertEqual(entry['ports'], {'process':[0,40], 'sensor':[0,-40]})
        self.assertEqual(entry['port_kinds'], {'process':'process', 'sensor':'signal'})
        self.assertEqual(entry['routing_bounds'], [-17,-24,17,24])

    def test_sensor_tip_is_inside_closed_pocket_not_through_boundary(self):
        artwork = core.CATALOG['thermowell']['artwork']
        self.assertIn({'kind':'line', 'points':[[0,-40],[0,10]]}, artwork)
        self.assertIn({'kind':'ellipse', 'rect':[-2,10,4,4]}, artwork)
        self.assertIn({'kind':'polyline', 'points':[[-10,-24],[-10,15],[0,24],[10,15],[10,-24]]}, artwork)
        self.assertIn({'kind':'line','points':[[0,24],[0,40]]}, artwork)
        self.assertNotIn({'kind':'line','points':[[0,22],[0,40]]}, artwork)
        tip = next(p['rect'] for p in artwork if p['kind']=='ellipse')
        pocket = next(p['points'] for p in artwork if p['kind']=='polyline')
        self.assertLess(tip[1]+tip[3], max(y for x,y in pocket),
                        'Sensing tip must not breach the closed protective end')

    def test_four_rotation_svg_fidelity_and_outward_ports(self):
        record = core.component('thermowell',0,0,core.new_document())
        for rotation in (0,90,180,270):
            record['rotation'] = rotation
            with self.subTest(rotation=rotation):
                report, svg, raster = inspect(record,core.new_document())
                self.assertTrue(report['passed'], report)
                for position in core.CATALOG['thermowell']['ports'].values():
                    x,y = position
                    for _ in range(rotation//90):
                        x,y = -y,x
                    dx,dy = ((0,1 if y>0 else -1) if y else (1 if x>0 else -1,0))
                    self.assertTrue(routing.clear((x,y),(x+20*dx,y+20*dy),[core.routing_bounds(record)]))

    def test_saved_legacy_record_and_connections_remain_unchanged(self):
        document = core.new_document()
        element = core.component('thermowell',0,0,document)
        element['id'],element['tag'] = 'legacy-well','TE-42A'
        document['components'].append(element)
        instrument = core.component('temperature_transmitter',100,100,document)
        document['components'].append(instrument)
        document['connections'].append({'id':'legacy-wire','from':{'component':element['id'],'port':'sensor'},
            'to':{'component':instrument['id'],'port':'signal'},'kind':'signal','label':'legacy','waypoints':[]})
        before = copy.deepcopy(document)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'legacy.pid'
            core.save(document,path)
            self.assertEqual(core.load(path),before)


if __name__ == '__main__':
    unittest.main()
