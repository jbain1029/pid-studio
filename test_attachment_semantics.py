import copy
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET

from test_editor import APP
from app import Symbol
import component_legend
import custom_symbols
import diagnostics
import pidcore as core


class AttachmentSemanticsTests(unittest.TestCase):
    def fixture(self):
        document = core.new_document()
        turbine = core.component('turbine',0,0,document)
        document['components'].append(turbine)
        pickup = core.component('hall_speed_sensor',160,0,document)
        document['components'].append(pickup)
        document['connections'].append({'id':core.uid(),'from':{'component':turbine['id'],'port':'shaft'},
            'to':{'component':pickup['id'],'port':'pickup'},'kind':'signal','label':'','waypoints':[]})
        return document

    def test_legacy_link_is_reviewed_without_reclassification(self):
        document = self.fixture()
        before = copy.deepcopy(document)
        self.assertEqual(core.validate(document),[])
        findings = diagnostics.inspect(document)
        matches = [(severity,identifier,text) for severity,identifier,text in findings
                   if 'Legacy attachment semantics' in text]
        self.assertEqual(len(matches),1)
        self.assertEqual(matches[0][0],'Review')
        self.assertEqual(matches[0][1],document['connections'][0]['id'])
        self.assertIn('not a torque-transmitting',matches[0][2])
        self.assertEqual(document,before)

    def test_meaning_visible_in_tooltip_and_companion_legend(self):
        document = self.fixture()
        symbol = Symbol(document['components'][0],SimpleNamespace(document=document))
        self.assertIn('Mechanical shaft attachment',symbol.toolTip())
        self.assertIn(b'Mechanical shaft attachment',component_legend.artwork(document))
        for kind in ('turbine','hall_speed_sensor','acoustic_sensor','heating_coil','thermocouple'):
            definition = core.CATALOG[kind]
            self.assertTrue(definition['port_meanings'])
            self.assertLessEqual(set(definition['port_meanings']),set(definition['ports']))

    def test_custom_definitions_cannot_inject_builtin_semantics(self):
        envelope = custom_symbols.fixture()
        document = custom_symbols.merge(core.new_document(),envelope)
        document['symbol_definitions'][envelope['kind']]['port_meanings'] = {'inlet':'arbitrary'}
        self.assertTrue(core.validate(document))

    def test_composite_circuits_are_explicit_in_exported_legend(self):
        document = core.new_document()
        kinds = ('plate_exchanger','double_pipe_exchanger','jacketed_reactor','steam_boiler','fired_heater')
        document['components'] = [core.component(kind,0,0,document) for kind in kinds]
        data = component_legend.artwork(document)
        text = ' '.join(''.join(node.itertext()) for node in ET.fromstring(data).iter()
                        if node.tag.rsplit('}',1)[-1]=='text')
        text = ' '.join(text.split())
        for phrase in ('Inner tube','Outer annulus','not the jacket','not a flue','separate services'):
            self.assertIn(phrase,text)
        for kind in kinds:
            self.assertTrue(core.CATALOG[kind]['symbol_notes'])


if __name__ == '__main__':
    unittest.main()
