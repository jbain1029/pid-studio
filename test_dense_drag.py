import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QPointF
from test_editor import APP
from app import Window
import pidcore as core
import routing
import benchmark_dense_drag as benchmark


class DenseDragTests(unittest.TestCase):
    def test_dense_viewport_events_and_history(self):
        result = benchmark.run()
        self.assertTrue(result['routes_clear_each_event'])
        self.assertTrue(result['undo_redo_exact'])

    def test_reuse_invalidates_for_obstacles_endpoints_and_final_refresh(self):
        window = Window()
        try:
            window.document = core.new_document()
            for kind,x,y in [('pump',0,0),('valve',300,0),('tank',150,200)]:
                window.document['components'].append(core.component(kind,x,y,window.document))
            a,b,obstacle = window.document['components']
            window.document['connections'].append({'id':core.uid(),
                'from':{'component':a['id'],'port':'outlet'},
                'to':{'component':b['id'],'port':'inlet'},'kind':'process','label':'','waypoints':[]})
            window.rebuild()
            pipe = window.pipes[0]
            with patch('app.routing.route', wraps=routing.route) as solve:
                window.update_lines(interactive=True)
                self.assertEqual(solve.call_count,0)
                window.symbols[obstacle['id']].setPos(QPointF(150,0))
                obstacle['position'] = [150,0]
                window.update_lines(interactive=True)
                self.assertEqual(solve.call_count,1)
                benchmark.assert_routes(window)
                window.symbols[a['id']].setPos(QPointF(-20,0))
                a['position'] = [-20,0]
                window.update_lines(interactive=True)
                self.assertEqual(solve.call_count,2)
                benchmark.assert_routes(window)
                window.update_lines()
                self.assertEqual(solve.call_count,3)
            expected = copy.deepcopy(pipe._valid_points)
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder)/'dense.pid'
                core.save(window.document,path)
                window.document = core.load(path)
                window.rebuild()
                self.assertEqual(window.pipes[0]._valid_points,expected)
        finally:
            window.saved = copy.deepcopy(window.document)
            window.close()
            APP.processEvents()
