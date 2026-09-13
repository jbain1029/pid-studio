"""Embedded symbol definitions must travel with copied drawing objects."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_editor import APP
from app import Window
import pidcore as core
import custom_symbols
import workspace


class CustomSymbolClipboardTests(unittest.TestCase):
    def setUp(self):
        self.windows = []
        self.catalog_before = copy.deepcopy(core.CATALOG)

    def tearDown(self):
        APP.clipboard().clear()
        for window in self.windows:
            window.saved = copy.deepcopy(window.document)
            window.close()
        self.assertEqual(core.CATALOG, self.catalog_before)

    def window(self, definitions=None):
        window = Window()
        self.windows.append(window)
        if definitions:
            window.document['symbol_definitions'] = copy.deepcopy(definitions)
        return window

    def definitions(self):
        fixture = custom_symbols.fixture()
        return {fixture['kind']: copy.deepcopy(fixture['definition'])}

    def add(self, window, kind, x=0):
        record = core.component(kind, x, 0, window.document)
        window.document['components'].append(record)
        return record

    def copy_all(self, window):
        window.rebuild()
        for item in window.symbols.values():
            item.setSelected(True)
        workspace.copy_selection(window)

    def test_cross_window_paste_roundtrip_and_undo_redo(self):
        definitions = self.definitions()
        kind = next(iter(definitions))
        source = self.window(definitions)
        first = self.add(source, kind)
        second = self.add(source, 'tank', 200)
        ports = list(definitions[kind]['ports'])
        source.document['connections'].append({
            'id': core.uid(), 'from': {'component': first['id'], 'port': ports[-1]},
            'to': {'component': second['id'], 'port': 'inlet'},
            'label': 'L-101', 'kind': 'process', 'waypoints': [],
        })
        original = copy.deepcopy(source.document)
        self.copy_all(source)
        target = self.window()
        before = copy.deepcopy(target.document)
        workspace.paste_selection(target)
        after = copy.deepcopy(target.document)
        self.assertEqual(after['symbol_definitions'], definitions)
        self.assertEqual(len(after['components']), 2)
        self.assertEqual(len(after['connections']), 1)
        self.assertFalse(core.validate(after))
        self.assertEqual(source.document, original)
        self.assertTrue({r['id'] for r in original['components']}.isdisjoint(
            {r['id'] for r in after['components']}))
        target.undo()
        self.assertEqual(target.document, before)
        target.redo()
        self.assertEqual(target.document, after)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'custom copy.pid'
            core.save(after, path)
            reopened = self.window()
            self.assertTrue(reopened.open_path(path))
            self.assertEqual(reopened.document, after)

    def test_only_selected_definitions_are_copied(self):
        definitions = self.definitions()
        kind = next(iter(definitions))
        definitions['custom:unused'] = copy.deepcopy(definitions[kind])
        source = self.window(definitions)
        self.add(source, kind)
        self.copy_all(source)
        payload = json.loads(bytes(APP.clipboard().mimeData().data('application/x-pid-document')))
        self.assertEqual(set(payload['symbol_definitions']), {kind})

    def test_conflict_remaps_without_overwriting_and_respects_slug_limit(self):
        definition = next(iter(self.definitions().values()))
        kind = 'custom:' + 'a' * 48
        source = self.window({kind: definition})
        self.add(source, kind)
        self.copy_all(source)
        changed = copy.deepcopy(definition)
        changed['label'] += ' different'
        target = self.window({kind: changed, 'custom:' + 'a'*46 + '_2': changed})
        existing = self.add(target, kind)
        original = copy.deepcopy(target.document)
        workspace.paste_selection(target)
        imported = target.document['components'][-1]
        expected = 'custom:' + 'a'*46 + '_3'
        self.assertEqual(imported['type'], expected)
        self.assertEqual(target.document['symbol_definitions'][expected], definition)
        self.assertEqual(target.document['symbol_definitions'][kind], changed)
        self.assertEqual(target.document['components'][0], existing)
        self.assertFalse(core.validate(target.document))
        target.undo()
        self.assertEqual(target.document, original)

    def test_duplicate_and_same_definition_paste_reuse(self):
        definitions = self.definitions()
        kind = next(iter(definitions))
        window = self.window(definitions)
        self.add(window, kind)
        self.copy_all(window)
        window.duplicate()
        self.assertEqual(len(window.document['components']), 2)
        workspace.paste_selection(window)
        self.assertEqual(len(window.document['components']), 3)
        self.assertEqual(window.document['symbol_definitions'], definitions)
        self.assertEqual({r['type'] for r in window.document['components']}, {kind})
        self.assertFalse(core.validate(window.document))

    def test_invalid_combined_drawing_does_not_checkpoint(self):
        source = self.window(self.definitions())
        self.add(source, next(iter(source.document['symbol_definitions'])))
        self.copy_all(source)
        target = self.window()
        before = copy.deepcopy(target.document)
        with patch.object(core, 'validate', side_effect=[[], ['Combined drawing rejected']]), \
                patch.object(workspace.QMessageBox, 'warning') as warning:
            workspace.paste_selection(target)
        self.assertEqual(target.document, before)
        self.assertEqual(target.history, [])
        warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()
