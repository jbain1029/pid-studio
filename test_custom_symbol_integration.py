"""Custom symbol integration through editor, export, and local AI contracts."""
import copy
import json
import unittest
import csv
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer
from test_editor import APP
from app import Window
from classic import Toolbox
import custom_symbols
import drawio_export
import operations
import openai_bridge as bridge
import pidcore as core
import symbol_library
import deliverables


class CustomSymbolIntegrationTests(unittest.TestCase):
    def test_specialized_registers_use_custom_category(self):
        envelope = custom_symbols.fixture()
        for category, report in [('Instrumentation','instruments'),('Valves & Actuators','valves')]:
            envelope['definition']['category'] = category
            self.window.document = custom_symbols.merge(core.new_document(),envelope)
            record = core.component(envelope['kind'],0,0,self.window.document)
            self.window.document['components'].append(record)
            self.window.rebuild()
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder)/'register.csv'
                deliverables.export_register(self.window,path,report)
                with path.open(encoding='utf-8-sig',newline='') as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual([row['tag'] for row in rows],[record['tag']])

    def setUp(self):
        self.window = Window()
        self.envelope = custom_symbols.fixture()
        self.kind = self.envelope['kind']
        self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs:
            dialog.close()
        APP.clipboard().clear()
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def library(self):
        dialog = symbol_library.LibraryDialog(self.window)
        self.dialogs.append(dialog)
        return dialog

    def install_component(self):
        symbol_library.apply_definition(self.window, self.envelope)
        record = core.component(self.kind, 0, 0, self.window.document)
        self.window.document['components'].append(record)
        self.window.rebuild()
        return record

    def test_new_preview_is_nonmutating_apply_populates_palette(self):
        original = copy.deepcopy(self.window.document)
        dialog = self.library()
        self.assertEqual(dialog.windowTitle(), 'Drawing component library')
        self.assertEqual(dialog.editor.accessibleName(), 'Component definition JSON')
        edit_menu = next(action.menu() for action in self.window.menuBar().actions() if action.text() == 'Edit')
        self.assertIn('Drawing component library…', [action.text() for action in edit_menu.actions()])
        dialog.new()
        self.assertTrue(dialog.preview())
        self.assertEqual(self.window.document, original)
        self.assertEqual(self.window.history, [])
        self.assertEqual(len(dialog.scene.items()), 1)
        dialog.apply()
        self.assertIn(self.kind, self.window.document['symbol_definitions'])
        palette = self.window.findChild(Toolbox)
        kinds = set(palette.leaves)
        self.assertIn(self.kind, kinds)
        self.window.undo()
        self.assertEqual(self.window.document, original)

    def test_definition_update_protects_connected_ports_and_is_undoable(self):
        record = self.install_component()
        tank = core.component('tank', 200, 0, self.window.document)
        self.window.document['components'].append(tank)
        port = list(self.envelope['definition']['ports'])[-1]
        self.window.document['connections'].append({
            'id': core.uid(), 'from': {'component': record['id'], 'port': port},
            'to': {'component': tank['id'], 'port': 'inlet'},
            'label': '', 'kind': 'process', 'waypoints': []})
        self.window.rebuild()
        original = copy.deepcopy(self.window.document)
        history = copy.deepcopy(self.window.history)
        invalid = copy.deepcopy(self.envelope)
        del invalid['definition']['ports'][port]
        del invalid['definition']['port_kinds'][port]
        with self.assertRaises(ValueError):
            symbol_library.apply_definition(self.window, invalid, replace_kind=self.kind)
        self.assertEqual(self.window.document, original)
        self.assertEqual(self.window.history, history)
        changed = copy.deepcopy(self.envelope)
        changed['definition']['label'] = 'Updated sight glass'
        self.assertTrue(symbol_library.apply_definition(self.window, changed, replace_kind=self.kind))
        self.assertEqual(self.window.document['components'], original['components'])
        self.window.undo()
        self.assertEqual(self.window.document, original)

    def test_renderer_and_drawio_artwork_all_rotations(self):
        record = self.install_component()
        rendered = []
        for rotation in (0, 90, 180, 270):
            record['rotation'] = rotation
            self.window.rebuild()
            item = self.window.symbols[record['id']]
            self.assertFalse(item.boundingRect().isEmpty())
            svg = drawio_export.artwork(record, self.window.document)
            self.assertTrue(QSvgRenderer(svg).isValid())
            self.assertIn(b'<rect', svg)
            rendered.append(svg)
        self.assertEqual(len(set(rendered)), 4)

    def test_local_ai_catalog_wire_and_decode_use_embedded_definition(self):
        self.install_component()
        document = self.window.document
        original = copy.deepcopy(document)
        self.assertEqual(operations.context(document)['catalog'][self.kind], self.envelope['definition'])
        enum = bridge.wire_schema(document)['properties']['components']['items']['properties']['type']['enum']
        self.assertIn(self.kind, enum)
        record = core.component(self.kind, 100, 0, document)
        record['position'] = {'x': 100, 'y': 0}
        value = {'components': [record], 'connections': [], 'removed_component_ids': [],
                 'removed_connection_ids': [], 'title': None, 'issues': [], 'review_findings': []}
        response = {'status': 'completed', 'output': [{'type': 'message', 'content': [
            {'type': 'output_text', 'text': json.dumps(value)}]}]}
        proposal = bridge.decode_response(document, response)
        result = operations.apply(document, proposal)
        self.assertEqual(len(result['components']), 2)
        self.assertEqual(result['components'][-1]['type'], self.kind)
        self.assertEqual(document, original)
        self.assertFalse(core.validate(result))
        missing = copy.deepcopy(document)
        del missing['symbol_definitions']
        self.assertTrue(core.validate(missing))
        with self.assertRaises(ValueError):
            bridge.decode_response(missing, response)

    def test_remove_unused_cannot_delete_instantiated_definition(self):
        record = self.install_component()
        dialog = self.library()
        original = copy.deepcopy(self.window.document)
        history = copy.deepcopy(self.window.history)
        dialog.remove()
        self.assertIn('in use', dialog.status.text())
        self.assertEqual(self.window.document, original)
        self.assertEqual(self.window.history, history)
        self.window.symbols[record['id']].setSelected(True)
        self.window.delete()
        before_removal = copy.deepcopy(self.window.document)
        dialog.remove()
        self.assertNotIn(self.kind, self.window.document['symbol_definitions'])
        self.window.undo()
        self.assertEqual(self.window.document, before_removal)


if __name__ == '__main__':
    unittest.main()
