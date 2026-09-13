"""Exercise the real assistant workflow without networking or credential access."""
import base64
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_editor import APP
from PySide6.QtCore import QObject, Signal, QSettings, QByteArray
from PySide6.QtGui import QImage
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QDialog
from app import Window
from assistant_ui import AssistantDialog
import pidcore
import sketch


class FakeReply(QObject):
    finished = Signal()
    downloadProgress = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.status_code = 200
        self.error_code = QNetworkReply.NetworkError.NoError
        self.payload = b''
        self.aborted = False
        self.deleted = False

    def attribute(self, attribute):
        return self.status_code

    def error(self):
        return self.error_code

    def readAll(self):
        return QByteArray(self.payload)

    def abort(self):
        self.aborted = True
        self.finished.emit()

    def deleteLater(self):
        self.deleted = True


class FakeManager:
    def __init__(self, parent):
        self.calls = []
        self.reply = FakeReply()

    def post(self, request, payload):
        self.calls.append((request, bytes(payload)))
        return self.reply


class AssistantLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        for target in ('get_password', 'set_password', 'delete_password'):
            self.enterContext(patch('keyring.' + target, return_value=None))
        self.enterContext(patch.dict('os.environ', {'OPENAI_API_KEY': '', 'OPENAI_MODEL': ''}))
        self.enterContext(patch('assistant_ui.QNetworkAccessManager', FakeManager))
        # Qt reports uncaught Python slot exceptions through excepthook instead of
        # propagating them to Signal.emit; those must fail this test suite too.
        self.slot_errors = self.enterContext(patch('sys.excepthook'))
        self.window = Window()
        self.window.workbench_settings = QSettings(str(Path(self.folder.name) / 'settings.ini'), QSettings.Format.IniFormat)
        self.window.example()
        self.before = copy.deepcopy(self.window.document)
        self.dialog = AssistantDialog(self.window)
        self.dialog.model.setText('offline-test-model')
        self.dialog.key.setText('synthetic-key-not-real')
        self.dialog.instructions.setPlainText('Change the title to Reviewed fixture')
        self.reply = self.dialog.manager.reply

    def tearDown(self):
        self.dialog.reject()
        self.dialog.timer.stop()
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()
        APP.clipboard().clear()
        self.slot_errors.assert_not_called()

    def complete(self, **overrides):
        value = {'components': [], 'connections': [], 'removed_component_ids': [],
                 'removed_connection_ids': [], 'title': 'Reviewed fixture',
                 'issues': [], 'review_findings': []}
        response = {'status': 'completed', 'id': 'resp_offline', 'model': 'offline-response-model',
                    'usage': None, 'output': [{'type': 'message', 'content': [
                        {'type': 'output_text', 'text': json.dumps(value)}]}]}
        response.update(overrides)
        self.reply.payload = json.dumps(response).encode()
        self.reply.finished.emit()

    def test_actual_posted_bytes_and_single_inflight_request(self):
        self.dialog.start()
        self.dialog.start()
        self.assertEqual(len(self.dialog.manager.calls), 1)
        request, payload = self.dialog.manager.calls[0]
        self.assertEqual(request.url().toString(), 'https://api.openai.com/v1/responses')
        self.assertEqual(request.attribute(QNetworkRequest.Attribute.RedirectPolicyAttribute),
                         QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        self.assertEqual(self.dialog.generation['request_fingerprint'], hashlib.sha256(payload).hexdigest())
        self.assertNotIn(self.dialog.key.text(), json.dumps(self.dialog.generation))
        self.assertNotIn(self.dialog.key.text().encode(), payload)
        self.assertFalse(self.dialog.generate.isEnabled())
        self.assertTrue(self.dialog.timer.isActive())
        self.assertEqual(self.window.document, self.before)

    def test_completed_reply_with_null_usage_passes_generation_to_review(self):
        self.dialog.start()
        with patch('assistant_ui.sketch.review', return_value=False) as review:
            self.complete()
        generation = review.call_args.kwargs['generation']
        self.assertEqual(generation['response_id'], 'resp_offline')
        self.assertEqual(generation['response_model'], 'offline-response-model')
        self.assertIsNone(generation['total_tokens'])
        self.assertIsNotNone(generation['received_at'])
        self.assertNotIn('synthetic-key-not-real', json.dumps(generation))
        self.assertEqual(self.window.document, self.before)
        self.assertIn('discarded', self.dialog.status.text())
        self.assertIsNone(self.dialog.reply)
        self.assertTrue(self.dialog.generate.isEnabled())
        self.assertFalse(self.dialog.timer.isActive())
        self.assertTrue(self.reply.deleted)

    def test_sent_image_fingerprint_matches_actual_normalized_payload(self):
        self.window.reference_image = QImage(20, 10, QImage.Format.Format_RGB32)
        self.window.reference_image.fill(0xffffff)
        self.window.document['reference'] = {'data': 'different-source-encoding', 'filename': 'fixture.png',
                                             'width': 100, 'position': [0, 0], 'opacity': .5}
        self.dialog.use_image.setEnabled(True)
        self.dialog.use_image.setChecked(True)
        self.dialog.start()
        body = json.loads(self.dialog.manager.calls[0][1])
        image_url = body['input'][0]['content'][1]['image_url']
        actual = base64.b64decode(image_url.split(',', 1)[1])
        self.assertTrue(self.dialog.generation['image_included'])
        self.assertEqual(self.dialog.generation['sent_image_fingerprint'], hashlib.sha256(actual).hexdigest())

    def test_reject_aborts_without_review_or_mutation(self):
        self.dialog.start()
        with patch('assistant_ui.sketch.review') as review:
            self.dialog.reject()
            self.complete()
        review.assert_not_called()
        self.assertTrue(self.reply.aborted)
        self.assertTrue(self.reply.deleted)
        self.assertIsNone(self.dialog.reply)
        self.assertEqual(self.window.document, self.before)

    def test_timeout_and_oversize_abort_without_review(self):
        for action, expected in ((lambda: self.dialog.timeout(), 'timed out'),
                                 (lambda: self.dialog.check_size(8_000_001, -1), 'size limit')):
            with self.subTest(expected=expected):
                self.dialog.start()
                with patch('assistant_ui.sketch.review') as review:
                    action()
                review.assert_not_called()
                self.assertIn(expected, self.dialog.status.text())
                self.assertEqual(self.window.document, self.before)

    def test_errors_and_redirect_do_not_open_review(self):
        for code in (401, 403, 429, 500, 302):
            with self.subTest(code=code):
                self.dialog.start()
                self.reply.status_code = code
                self.reply.error_code = QNetworkReply.NetworkError.UnknownNetworkError
                with patch('assistant_ui.sketch.review') as review:
                    self.reply.finished.emit()
                review.assert_not_called()
                self.assertEqual(self.window.document, self.before)
                self.assertTrue(self.dialog.generate.isEnabled())

    def test_malformed_reply_leaves_drawing_unchanged(self):
        for payload in (b'not JSON', b'[]', b'null', b'{"output":null}'):
            with self.subTest(payload=payload):
                self.dialog.start()
                self.reply.payload = payload
                with patch('assistant_ui.sketch.review') as review:
                    self.reply.finished.emit()
                review.assert_not_called()
                self.assertEqual(self.window.document, self.before)
                self.assertTrue(self.reply.deleted)

    def test_real_review_accept_persists_generation_and_undo_restores(self):
        self.dialog.start()
        with patch.object(sketch.QDialog, 'exec', return_value=QDialog.DialogCode.Accepted):
            self.complete(usage={'input_tokens': 10, 'output_tokens': 3, 'total_tokens': 13})
        self.assertEqual(self.window.document['title'], 'Reviewed fixture')
        generation = self.window.document['review_history'][-1]['generation']
        self.assertEqual(generation['total_tokens'], 13)
        self.assertEqual(generation['response_id'], 'resp_offline')
        path = Path(self.folder.name) / 'reviewed.pid'
        pidcore.save(self.window.document, path)
        self.assertEqual(pidcore.load(path)['review_history'][-1]['generation'], generation)
        self.window.undo()
        self.assertEqual(self.window.document, self.before)

    def test_real_review_cancel_does_not_persist_generation(self):
        self.dialog.start()
        with patch.object(sketch.QDialog, 'exec', return_value=QDialog.DialogCode.Rejected):
            self.complete()
        self.assertEqual(self.window.document, self.before)
        self.assertNotIn('review_history', self.window.document)


if __name__ == '__main__':
    unittest.main()
