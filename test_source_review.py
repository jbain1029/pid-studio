import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import base64
import copy
import unittest
from PySide6.QtCore import QBuffer, QIODevice, Qt, QRectF, QTimer
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QDialogButtonBox
from app import Window
import operations
import sketch
from source_review import SourceReview

APP = QApplication.instance() or QApplication([])


class SourceReviewTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()
        image = QImage(400,200,QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.white)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer,'PNG')
        self.window.document['reference'] = {'filename':'fixture.png','data':base64.b64encode(bytes(buffer.data())).decode(),'position':[0,0],'width':400,'opacity':0.35}
        self.finding = {'id':'check-1','message':'Confirm tag against sketch','region':{'x':0.25,'y':0.25,'width':0.5,'height':0.5},'object_ids':[self.window.document['components'][0]['id']]}
        self.proposal = {'contract_version':1,'base_fingerprint':operations.fingerprint(self.window.document),'operations':[], 'review_findings':[self.finding]}

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_region_bounds_and_references_validated(self):
        original = copy.deepcopy(self.window.document)
        for change in ({'region':{'x':0.9,'y':0,'width':0.2,'height':0.5}}, {'object_ids':['missing']}):
            proposal = copy.deepcopy(self.proposal)
            proposal['review_findings'][0].update(change)
            with self.assertRaises(ValueError):
                operations.apply(self.window.document,proposal)
        self.assertEqual(self.window.document,original)

    def test_region_mapping_and_acknowledgment(self):
        panel = SourceReview(self.window.document,[self.finding])
        panel.focus_region(0)
        self.assertEqual(panel.highlight.rect(),QRectF(100,50,200,100))
        self.assertFalse(panel.complete())
        panel.list.item(0).setCheckState(Qt.CheckState.Checked)
        self.assertTrue(panel.complete())
        panel.close()

    def test_apply_is_gated_and_undoable(self):
        original = copy.deepcopy(self.window.document)
        observed = []
        def accept():
            dialog = QApplication.activeModalWidget()
            panel = dialog.findChild(SourceReview)
            button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Apply)
            observed.append(button.isEnabled())
            panel.list.item(0).setCheckState(Qt.CheckState.Checked)
            observed.append(button.isEnabled())
            button.click()
        QTimer.singleShot(0,accept)
        self.assertTrue(sketch.review(self.window,self.proposal))
        self.assertEqual(observed,[False,True])
        self.assertEqual(self.window.document['review_history'][-1]['acknowledged_ids'],['check-1'])
        self.window.undo()
        self.assertEqual(self.window.document,original)

    def test_programmatic_accept_cannot_bypass_review(self):
        original = copy.deepcopy(self.window.document)
        QTimer.singleShot(0,lambda:QApplication.activeModalWidget().accept())
        self.assertFalse(sketch.review(self.window,self.proposal))
        self.assertEqual(self.window.document,original)
