import copy
import unittest
from test_editor import APP
from app import Window
import pidcore as core
import diagnostics

class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.example()

    def tearDown(self):
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_unused_ports_are_review_items_not_errors(self):
        findings = diagnostics.inspect(self.window.document)
        self.assertEqual(len(findings),2)
        self.assertTrue(all(severity=='Review' for severity,_,_ in findings))
        self.assertFalse(core.validate(self.window.document))

    def test_duplicate_connection_and_number_detected(self):
        line = copy.deepcopy(self.window.document['connections'][0])
        line['id'] = core.uid()
        line['label'] = 'CW-100'
        self.window.document['connections'][0]['label'] = 'CW-100'
        self.window.document['connections'].append(line)
        messages = '\n'.join(text for _,_,text in diagnostics.inspect(self.window.document))
        self.assertIn('Duplicate connections',messages)
        self.assertIn('CW-100 appears',messages)
        self.assertIn('explicit tee',messages)

    def test_message_locates_object(self):
        self.window.validate()
        item = self.window.messages.item(0)
        self.window.messages.itemClicked.emit(item)
        self.assertEqual(len(self.window.scene.selectedItems()),1)

if __name__=='__main__':
    unittest.main()
