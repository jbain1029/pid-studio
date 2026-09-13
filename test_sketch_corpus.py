"""Synthetic offline pipeline corpus; never a recognition accuracy benchmark."""
import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_editor import APP
from test_assistant_lifecycle import FakeManager
from PySide6.QtCore import QBuffer, QIODevice, QRectF, QSettings, QTimer, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QDialogButtonBox
from app import Window
from assistant_ui import AssistantDialog
from source_review import SourceReview
import openai_bridge
import operations
import pidcore
import sketch

ROOT = Path(__file__).parent / 'examples' / 'sketch-corpus'
CASES = json.loads((ROOT / 'cases.json').read_text(encoding='utf-8'))


def raster(case):
    renderer = QSvgRenderer(str(ROOT / (case['name'] + '.svg')))
    if not renderer.isValid():
        raise ValueError('Invalid corpus SVG')
    image = QImage(3200, 1600, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return image


def response(case):
    value = {'components': [dict(id=id_, type=kind, tag=tag, description='',
                position={'x': x, 'y': y}, rotation=0)
                for id_, kind, tag, x, y in case['components']],
             'connections': [{'id': id_, 'from': {'component': a, 'port': ap},
                'to': {'component': b, 'port': bp}, 'kind': kind, 'label': '', 'waypoints': []}
                for id_, a, ap, b, bp, kind in case['connections']],
             'removed_component_ids': [], 'removed_connection_ids': [],
             'title': case['name'], 'issues': [], 'review_findings': case['findings']}
    return {'status': 'completed', 'output': [{'type': 'message', 'content': [
        {'type': 'output_text', 'text': json.dumps(value)}]}]}


class SketchCorpusTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.window = Window()
        self.window.workbench_settings = QSettings(str(Path(self.folder.name) / 'settings.ini'), QSettings.Format.IniFormat)
        self.enterContext(patch('keyring.get_password', return_value=None))
        self.enterContext(patch.dict('os.environ', {'OPENAI_API_KEY': '', 'OPENAI_MODEL': ''}))
        self.enterContext(patch('assistant_ui.QNetworkAccessManager', FakeManager))
        self.slot_errors = self.enterContext(patch('sys.excepthook'))

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()
        self.slot_errors.assert_not_called()

    def load_case(self, case):
        image = raster(case)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, 'BMP')
        self.window.document = pidcore.new_document()
        self.window.document['reference'] = {'filename': case['name'] + '.bmp',
            'data': base64.b64encode(bytes(buffer.data())).decode(),
            'position': [-500, -350], 'width': 1000, 'opacity': .35}
        self.window.rebuild()
        return openai_bridge.decode_response(self.window.document, response(case), image_included=True)

    def test_expected_components_tags_and_named_port_connections(self):
        for case in CASES:
            with self.subTest(case=case['name']):
                proposal = self.load_case(case)
                before = copy.deepcopy(self.window.document)
                draft = operations.apply(before, proposal)
                self.assertEqual(pidcore.validate(draft), [])
                self.assertEqual([c['tag'] for c in draft['components']], case['expected_tags'])
                self.assertEqual([c['type'] for c in draft['components']], case['expected_types'])
                tags = {c['id']: c['tag'] for c in draft['components']}
                edges = [f"{tags[c['from']['component']]}.{c['from']['port']}>"
                         f"{tags[c['to']['component']]}.{c['to']['port']}:{c['kind']}"
                         for c in draft['connections']]
                self.assertEqual(edges, case['expected_edges'])
                self.assertEqual(self.window.document, before)

    def test_actual_image_normalization_retains_original_and_region_coordinates(self):
        for case in CASES:
            with self.subTest(case=case['name']):
                self.load_case(case)
                before = copy.deepcopy(self.window.document)
                dialog = AssistantDialog(self.window)
                try:
                    dialog.model.setText('offline-test-model')
                    dialog.key.setText('synthetic-no-real-key')
                    dialog.instructions.setPlainText('Transcribe the synthetic reference; flag ambiguities.')
                    dialog.start()
                    self.assertEqual(len(dialog.manager.calls), 1)
                    body = json.loads(dialog.manager.calls[0][1])
                    url = body['input'][0]['content'][1]['image_url']
                    self.assertTrue(url.startswith('data:image/png;base64,'))
                    data = base64.b64decode(url.split(',', 1)[1])
                    self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
                    sent = QImage.fromData(data)
                    self.assertEqual((sent.width(), sent.height()), (2400, 1200))
                    # Not a blank placeholder: actual graphite marks survive resizing.
                    self.assertTrue(any(sent.pixelColor(x, y).lightness() < 150
                        for y in range(150, 1050, 15) for x in range(150, 2250, 15)))
                    payload = json.loads(body['input'][0]['content'][0]['text'])
                    self.assertEqual(payload['image_placement']['position'], [-500, -350])
                    self.assertEqual(self.window.document, before)
                finally:
                    dialog.reject()

    def test_all_ambiguities_gate_apply_and_acceptance_is_undoable(self):
        case = CASES[2]
        proposal = self.load_case(case)
        before = copy.deepcopy(self.window.document)
        observed = []
        rectangles = []
        def accept():
            dialog = QApplication.activeModalWidget()
            panel = dialog.findChild(SourceReview)
            button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Apply)
            observed.append(button.isEnabled())
            for i, finding in enumerate(case['findings']):
                panel.focus_region(i)
                region = finding['region']
                rectangles.append((panel.highlight.rect(), QRectF(region['x'] * 3200, region['y'] * 1600,
                    region['width'] * 3200, region['height'] * 1600)))
                panel.list.item(i).setCheckState(Qt.CheckState.Checked)
                observed.append(button.isEnabled())
            button.click()
        QTimer.singleShot(0, accept)
        self.assertTrue(sketch.review(self.window, proposal))
        self.assertEqual(observed, [False, False, True])
        for actual, expected in rectangles:
            self.assertEqual(actual, expected)
        self.assertEqual(self.window.document['connections'], [])
        self.assertEqual(self.window.document['review_history'][-1]['acknowledged_ids'],
                         ['unreadable-tag', 'crossing-topology'])
        self.window.undo()
        self.assertEqual(self.window.document, before)

    def test_cancel_and_incomplete_review_leave_original_unchanged(self):
        proposal = self.load_case(CASES[2])
        before = copy.deepcopy(self.window.document)
        for accepted in (False, True):
            def close():
                dialog = QApplication.activeModalWidget()
                panel = dialog.findChild(SourceReview)
                panel.list.item(0).setCheckState(Qt.CheckState.Checked)
                dialog.accept() if accepted else dialog.reject()
            QTimer.singleShot(0, close)
            self.assertFalse(sketch.review(self.window, proposal))
            self.assertEqual(self.window.document, before)

    def test_invalid_regions_and_image_free_response_are_rejected(self):
        proposal = self.load_case(CASES[2])
        before = copy.deepcopy(self.window.document)
        with self.assertRaises(ValueError):
            openai_bridge.decode_response(before, response(CASES[2]), image_included=False)
        for box in ({'x': .95, 'y': 0, 'width': .2, 'height': .2},
                    {'x': 0, 'y': 0, 'width': 0, 'height': .2}):
            invalid = copy.deepcopy(proposal)
            invalid['review_findings'][0]['region'] = box
            with self.assertRaises(ValueError):
                operations.apply(before, invalid)
        self.assertEqual(self.window.document, before)


if __name__ == '__main__':
    unittest.main()
