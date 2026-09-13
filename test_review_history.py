import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app import Window
import pidcore
import operations
import review_history

APP = QApplication.instance() or QApplication([])


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()
        self.before = copy.deepcopy(self.window.document)
        self.proposal = {'contract_version':1,'base_fingerprint':operations.fingerprint(self.before),
                         'operations':[{'operation':'update_drawing','changes':{'title':'Reviewed drawing'}}],
                         'review_findings':[{'id':'tag-check','message':'Confirm tag','region':None,'object_ids':[]}]}

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def recorded(self):
        return review_history.append(operations.apply(self.before,self.proposal),self.before,self.proposal)

    def test_record_roundtrips_and_inputs_remain_unchanged(self):
        before = copy.deepcopy(self.before)
        result = self.recorded()
        self.assertEqual(self.before,before)
        record = result['review_history'][0]
        self.assertEqual(record['base_fingerprint'],operations.fingerprint(before))
        self.assertEqual(record['proposal_fingerprint'],operations.fingerprint(self.proposal))
        self.assertEqual(record['acknowledged_ids'],['tag-check'])
        self.assertIsNone(record['source_fingerprint'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'history.pid'
            pidcore.save(result,path)
            self.assertEqual(pidcore.load(path),result)

    def test_viewer_checks_content_fingerprint(self):
        self.window.document = self.recorded()
        dialog = review_history.HistoryDialog(self.window)
        self.assertIn('stored content: yes',dialog.details.toPlainText())
        dialog.close()
        self.window.document['review_history'][0]['proposal_json'] = '{}'
        dialog = review_history.HistoryDialog(self.window)
        self.assertIn('stored content: NO',dialog.details.toPlainText())
        dialog.close()

    def test_history_is_preserved_through_later_operations(self):
        first = self.recorded()
        proposal = {'contract_version':1,'base_fingerprint':operations.fingerprint(first),'operations':[]}
        second = review_history.append(operations.apply(first,proposal),first,proposal)
        self.assertEqual(second['review_history'][0],first['review_history'][0])
        self.assertEqual(len(second['review_history']),2)
        self.assertEqual(second['review_history'][1]['base_fingerprint'],operations.fingerprint(first))
