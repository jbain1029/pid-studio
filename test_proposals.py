import copy
import base64
import tempfile
import unittest
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox
from test_editor import APP
from app import Window
import pidcore as core
import operations
import sketch

class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()
        self.before = copy.deepcopy(self.window.document)

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def proposal(self, edits):
        return {'contract_version':1,'base_fingerprint':operations.fingerprint(self.window.document),'operations':edits,'issues':['Review tags against the source sketch.']}

    def test_transaction_rejects_partial_invalid_change(self):
        proposal = self.proposal([{'operation':'update_drawing','changes':{'title':'New title'}},{'operation':'remove_component','id':self.before['components'][0]['id']}])
        with self.assertRaises(ValueError):
            operations.apply(self.window.document,proposal)
        self.assertEqual(self.before,self.window.document)

    def test_stale_rejected_even_without_revision_change(self):
        proposal = self.proposal([])
        self.window.document['components'][0]['position'][0] += 10
        with self.assertRaisesRegex(ValueError,'Drawing changed'):
            operations.apply(self.window.document,proposal)

    def test_review_accept_and_undo(self):
        proposal = self.proposal([{'operation':'update_drawing','changes':{'title':'Reviewed title'}}])
        def accept():
            dialog = APP.activeModalWidget()
            self.assertIsInstance(dialog,QDialog)
            dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Apply).click()
        QTimer.singleShot(30,accept)
        self.assertTrue(sketch.review(self.window,proposal))
        self.assertEqual(self.window.document['title'],'Reviewed title')
        self.window.undo()
        self.assertEqual(self.before,self.window.document)

    def test_review_cancel_leaves_document_unchanged(self):
        proposal = self.proposal([{'operation':'update_drawing','changes':{'title':'Cancelled'}}])
        QTimer.singleShot(30,lambda:APP.activeModalWidget().reject())
        self.assertFalse(sketch.review(self.window,proposal))
        self.assertEqual(self.before,self.window.document)

    def test_context_and_reference_roundtrip(self):
        # A small genuine PNG fixture, retained inside the saved document.
        png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aPioAAAAASUVORK5CYII=')
        self.window.document['reference'] = {'filename':'reference.png','data':base64.b64encode(png).decode(),'position':[0,0],'width':500,'opacity':.4}
        bundle = operations.context(self.window.document)
        self.assertIn('instructions',bundle)
        self.assertIn('proposal_schema',bundle)
        self.assertEqual(bundle['catalog'],core.CATALOG)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'embedded.pid'
            core.save(self.window.document,path)
            self.assertEqual(core.load(path),self.window.document)

if __name__ == '__main__':
    unittest.main()
