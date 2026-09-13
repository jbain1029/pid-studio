"""Real Qt viewport event benchmark, synthetic 96-equipment/16-pipe document."""
import copy
import json
import time
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtTest import QTest
from test_editor import APP
from app import Window
import pidcore as core
import routing
from benchmark_dense_routing import fixture


def document():
    result = core.new_document()
    for y in range(8):
        for x in range(8):
            node = core.component('tank', x*100+(y%3)*7, y*100+(x%3)*9, result)
            node['rotation'] = 90 if (x+y)%2 else 0
            result['components'].append(node)
    for start, finish, sd, fd in fixture()[1]:
        ends = []
        for point, direction in ((start, sd), (finish, fd)):
            rotation = {(1,0):0, (0,1):90, (-1,0):180, (0,-1):270}[direction]
            node = core.component('valve', point[0]-direction[0]*40,
                                  point[1]-direction[1]*40, result)
            node['rotation'] = rotation
            result['components'].append(node)
            ends.append({'component':node['id'], 'port':'outlet'})
        result['connections'].append({'id':core.uid(), 'from':ends[0], 'to':ends[1],
                                      'kind':'process', 'label':'', 'waypoints':[]})
    assert not core.validate(result)
    return result


def assert_routes(window):
    boxes = [core.routing_bounds(s.record, (s.x(),s.y())) for s in window.symbols.values()]
    for pipe in window.pipes:
        assert not pipe.route_error, pipe.route_error
        points = pipe._valid_points
        assert all(routing.clear(p,q,boxes) for p,q in zip(points,points[1:]))
        for point, endpoint in ((points[0],pipe.record['from']), (points[-1],pipe.record['to'])):
            port = window.symbols[endpoint['component']].port(endpoint['port'])
            assert point == (port.x(),port.y())


def run():
    window = Window()
    try:
        window.resize(1400,900)
        window.document = document()
        window.rebuild()
        window.show()
        window.view.resetTransform()
        window.view.scale(.65,.65)
        window.view.centerOn(QPointF(350,350))
        APP.processEvents()
        assert_routes(window)
        original = copy.deepcopy(window.document)
        target = window.document['components'][36]
        start = window.view.mapFromScene(window.symbols[target['id']].pos())
        viewport = window.view.viewport()
        assert viewport.rect().contains(start)
        QTest.mousePress(viewport, Qt.LeftButton, Qt.NoModifier, start)
        timings = []
        for offset in (QPoint(7,0),QPoint(13,3),QPoint(20,7),QPoint(26,10)):
            began = time.perf_counter()
            QTest.mouseMove(viewport,start+offset,delay=1)
            APP.processEvents()
            timings.append(time.perf_counter()-began)
            assert_routes(window)
        began = time.perf_counter()
        QTest.mouseRelease(viewport,Qt.LeftButton,Qt.NoModifier,start+QPoint(26,10))
        APP.processEvents()
        release = time.perf_counter()-began
        assert_routes(window)
        assert window.document != original
        changed = copy.deepcopy(window.document)
        window.undo()
        assert window.document == original
        window.redo()
        assert window.document == changed
        assert_routes(window)
        return {'components':96,'pipes':16,'move_event_seconds':timings,
                'release_event_seconds':release,'routes_clear_each_event':True,
                'undo_redo_exact':True}
    finally:
        window.saved = copy.deepcopy(window.document)
        window.close()
        APP.processEvents()


if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
