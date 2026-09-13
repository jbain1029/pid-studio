"""Text and directional markings must not change meaning when ports rotate."""
import unittest
import xml.etree.ElementTree as ET
from PySide6.QtGui import QFont
from test_editor import APP
import pidcore as core
import drawio_export
from symbol_library import draw_legend_labels
from verify_svg_catalog import inspect


class LabelRecorder:
    def __init__(self):
        self.labels = []
    def save(self): pass
    def restore(self): pass
    def font(self): return QFont('Segoe UI',9)
    def setFont(self,font): pass
    def drawText(self,rect,alignment,text):
        self.labels.append((text,rect.center().x(),rect.center().y()))


class SvgOrientationTests(unittest.TestCase):
    def test_actuator_letters_follow_center_without_becoming_rotated_glyphs(self):
        for kind,letter,y in [('motor_operated_valve','M',-26),('solenoid_valve','S',-25)]:
            for rotation,center in [(0,(0,y)),(90,(-y,0)),(180,(0,-y)),(270,(y,0))]:
                recorder = LabelRecorder()
                draw_legend_labels(recorder,core.CATALOG[kind],rotation=rotation)
                self.assertEqual(recorder.labels,[(letter,*center)])
                record = core.component(kind,0,0,core.new_document())
                record['rotation'] = rotation
                root = ET.fromstring(drawio_export.artwork(record))
                labels = [''.join(n.itertext()) for n in root.iter() if n.tag.endswith('}text')]
                self.assertIn(letter,labels)

    def test_instrument_dividers_live_in_upright_layer(self):
        converter = core.CATALOG['current_pressure_converter']
        diagonal = {'kind':'line','points':[[-16,16],[16,-16]]}
        self.assertNotIn(diagonal,converter['artwork'])
        self.assertIn(diagonal,converter['upright_artwork'])
        for kind in ('temperature_controller','flow_controller','level_controller','analysis_controller'):
            self.assertEqual(core.CATALOG[kind]['legend_bubble'], 'field')
            self.assertFalse(core.CATALOG[kind].get('upright_artwork'))

    def test_corrected_svg_rasters_are_unclipped_and_faithful(self):
        for kind in ('motor_operated_valve','solenoid_valve','current_pressure_converter',
                     'temperature_controller','inline_flowmeter','hall_speed_sensor','thermocouple'):
            for rotation in (0,90,180,270):
                record = core.component(kind,0,0,core.new_document())
                record['rotation'] = rotation
                report,_,_ = inspect(record,core.new_document())
                self.assertTrue(report['passed'],report)
