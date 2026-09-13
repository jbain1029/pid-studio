import copy
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from test_editor import APP
from app import Window
from annotations import Note
import pidcore as core
import workspace
import deliverables

class NoteTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.document['notes'] = [{'id':core.uid(),'text':'NOTE 1: VERIFY FLOW DIRECTION','position':[0,0],'width':240}]
        self.window.rebuild()

    def tearDown(self):
        APP.clipboard().clear()
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()

    def test_note_selection_duplicate_delete_undo(self):
        note = next(i for i in self.window.scene.items() if isinstance(i,Note))
        note.setSelected(True)
        self.assertEqual(self.window.properties.item(0,0).text(),'Text')
        self.window.duplicate()
        self.assertEqual(len(self.window.document['notes']),2)
        self.window.undo()
        note = next(i for i in self.window.scene.items() if isinstance(i,Note))
        note.setSelected(True)
        self.window.delete()
        self.assertFalse(self.window.document['notes'])
        self.window.undo()
        self.assertEqual(len(self.window.document['notes']),1)

    def test_note_clipboard_roundtrip_and_exports(self):
        next(i for i in self.window.scene.items() if isinstance(i,Note)).setSelected(True)
        workspace.copy_selection(self.window)
        workspace.paste_selection(self.window)
        self.assertEqual(len(self.window.document['notes']),2)
        self.assertFalse(core.validate(self.window.document))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'notes.pid'
            core.save(self.window.document,path)
            self.assertEqual(core.load(path),self.window.document)
            self.window.export_to(Path(folder)/'notes.svg')
            text = ' '.join(''.join(node.itertext()) for node in ET.parse(Path(folder)/'notes.svg').iter('{http://www.w3.org/2000/svg}text'))
            self.assertIn('VERIFY FLOW DIRECTION',' '.join(text.split()))
            deliverables.export_sheet(self.window,Path(folder)/'notes.png')
            self.assertGreater((Path(folder)/'notes.png').stat().st_size,1000)

    def test_recent_menu_opens_saved_document(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'notes.pid'
            core.save(self.window.document,path)
            self.window.saved = copy.deepcopy(self.window.document)
            workspace.update_recent(self.window,path)
            self.assertEqual(len(self.window.recent_menu.actions()),1)
            workspace.open_recent(self.window,str(path))
            self.assertEqual(self.window.path,str(path))
            self.assertEqual(self.window.document,core.load(path))

if __name__=='__main__':
    unittest.main()
