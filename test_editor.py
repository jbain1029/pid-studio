import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from app import Window
import pidcore as core
import workspace

APP = QApplication.instance() or QApplication([])
APP.setStyle('Fusion')

class EditorTests(unittest.TestCase):
    def setUp(self):
        self.w = Window()
        self.w.example()

    def tearDown(self):
        APP.clipboard().clear()
        self.w.saved = copy.deepcopy(self.w.document)
        self.w.close()

    def test_roundtrip_and_export(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'test.pid'
            core.save(self.w.document, path)
            self.assertEqual(core.load(path), self.w.document)
            self.w.export_to(Path(folder)/'drawing.svg')
            self.assertIn('<svg', (Path(folder)/'drawing.svg').read_text())

    def test_delete_cascades_undo_restores(self):
        original = copy.deepcopy(self.w.document)
        pump = next(s for s in self.w.symbols.values() if s.record['type']=='pump')
        pump.setSelected(True)
        self.w.delete()
        self.assertEqual(len(self.w.document['connections']), 2)
        self.assertFalse(core.validate(self.w.document))
        self.w.undo()
        self.assertEqual(self.w.document, original)
        self.w.redo()
        self.assertEqual(len(self.w.document['components']), 4)

    def test_ports_follow_movement_and_rotation(self):
        pump = next(s for s in self.w.symbols.values() if s.record['type']=='pump')
        pump.setPos(350, 200)
        pump.record['position'] = [350, 200]
        pump.record['rotation'] = 90
        self.w.update_lines()
        self.assertEqual(pump.port('outlet'), QPointF(350, 240))
        pipe = next(p for p in self.w.pipes if p.record['from']['component']==pump.record['id'])
        self.assertEqual(pipe.path().pointAtPercent(0), pump.port('outlet'))

    def test_invalid_import_preserves_document(self):
        original = copy.deepcopy(self.w.document)
        bad = copy.deepcopy(original)
        bad['connections'][0]['to']['port'] = 'invented'
        with self.assertRaises(ValueError):
            core.apply_proposal(original, {'base_revision': 0, 'document': bad})
        self.assertEqual(original, self.w.document)
        with self.assertRaises(ValueError):
            core.apply_proposal(original, {'base_revision': 2, 'document': original})

    def test_connect_duplicate_and_undo(self):
        self.w.add_symbol('instrument', QPointF(320, -200))
        instrument = self.w.document['components'][-1]
        pump = next(r for r in self.w.document['components'] if r['type']=='pump')
        self.w.connect_port(instrument['id'], 'process')
        self.w.connect_port(pump['id'], 'outlet')
        self.assertFalse(core.validate(self.w.document))

    def test_clipboard_remaps_connections_and_tags(self):
        for symbol in self.w.symbols.values():
            symbol.setSelected(True)
        old_ids = {c['id'] for c in self.w.document['components']}
        workspace.copy_selection(self.w)
        workspace.paste_selection(self.w)
        self.assertEqual(len(self.w.document['components']), 10)
        self.assertEqual(len(self.w.document['connections']), 8)
        self.assertFalse(core.validate(self.w.document))
        for line in self.w.document['connections'][4:]:
            self.assertNotIn(line['from']['component'], old_ids)
            self.assertNotIn(line['to']['component'], old_ids)
        self.w.undo()
        self.assertEqual(len(self.w.document['components']), 5)

    def test_recovery_snapshot_is_readable(self):
        with tempfile.TemporaryDirectory() as folder:
            self.w.recovery_file = Path(folder)/'recovery.pid'
            self.w.recovery_timer.timeout.emit()
            self.assertEqual(core.load(self.w.recovery_file), self.w.document)

    def test_waypoint_handles_and_route_survive_save(self):
        pipe = self.w.pipes[0]
        pipe.record['waypoints'] = [[80,-100]]
        pipe.setSelected(True)
        pipe.update_route()
        self.assertEqual(len(pipe.handles), 1)
        self.assertTrue(pipe.handles[0].isVisible())
        self.assertIsNone(pipe.route_error)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'route.pid'
            core.save(self.w.document, path)
            self.assertEqual(core.load(path)['connections'][0]['waypoints'], [[80,-100]])
        for s in self.w.symbols.values():
            s.setSelected(True)
        count = len(self.w.document['connections'])
        self.w.duplicate()
        self.assertEqual(len(self.w.document['connections']), count*2)
        self.assertFalse(core.validate(self.w.document))

    def test_double_click_inserts_waypoint_with_undo(self):
        pipe = self.w.pipes[0]
        original = copy.deepcopy(self.w.document)
        class Event:
            def scenePos(self):
                return QPointF(80,0)
            def accept(self):
                pass
        pipe.mouseDoubleClickEvent(Event())
        self.assertEqual(pipe.record['waypoints'],[[80,0]])
        self.w.undo()
        self.assertEqual(self.w.document,original)

if __name__ == '__main__':
    unittest.main()
