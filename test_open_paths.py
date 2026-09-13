import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QMimeData, QUrl
from PySide6.QtWidgets import QApplication
from app import Window, Canvas
import pidcore

APP = QApplication.instance() or QApplication([])


class OpenPathTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/'drawing with spaces.pid'
        self.document = pidcore.new_document()
        self.document['title'] = 'Direct open fixture'
        pidcore.save(self.document,self.path)

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()
        self.temp.cleanup()

    def test_invalid_file_does_not_prompt_to_discard(self):
        before = copy.deepcopy(self.window.document)
        with patch.object(self.window,'confirm_discard') as confirm, patch('app.QMessageBox.warning'):
            self.assertFalse(self.window.open_path(self.path.with_name('missing.pid')))
            confirm.assert_not_called()
        self.assertEqual(self.window.document,before)

    def test_cancel_preserves_work_and_success_updates_recent(self):
        before = copy.deepcopy(self.window.document)
        with patch.object(self.window,'confirm_discard',return_value=False):
            self.assertFalse(self.window.open_path(self.path))
        self.assertEqual(self.window.document,before)
        with patch.object(self.window,'confirm_discard',return_value=True):
            self.assertTrue(self.window.open_path(self.path))
        self.assertEqual(self.window.document,self.document)
        self.assertEqual(self.window.saved,self.document)
        self.assertEqual(self.window.path,str(self.path.resolve()))
        self.assertEqual(self.window.session_recent[0],str(self.path.resolve()))

    def test_drop_accepts_one_local_document_only(self):
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(self.path))])
        self.assertEqual(Path(Canvas.dropped_document(mime)),self.path)
        mime.setUrls([QUrl('https://example.com/drawing.pid')])
        self.assertIsNone(Canvas.dropped_document(mime))
        mime.setUrls([QUrl.fromLocalFile(str(self.path))]*2)
        self.assertIsNone(Canvas.dropped_document(mime))

    def test_command_line_opens_document_before_event_loop(self):
        root = Path(__file__).parent.resolve()
        script = '''import sys,runpy,json
from PySide6.QtCore import QTimer
import app
show = app.Window.show
def capture(window):
    show(window)
    def done():
        print(json.dumps({'title':window.document['title'],'path':window.path}))
        window.close()
    QTimer.singleShot(100,done)
app.Window.show = capture
runpy.run_path('run_studio.py',run_name='__main__')
'''
        result = subprocess.run([sys.executable,'-c',script,str(self.path)],cwd=root,
                                capture_output=True,text=True,timeout=20,check=True)
        data = json.loads(result.stdout.strip())
        self.assertEqual(data['title'],self.document['title'])
        self.assertEqual(data['path'],str(self.path.resolve()))
