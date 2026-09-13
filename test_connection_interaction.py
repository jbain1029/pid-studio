"""Viewport-level connection regressions (no direct connect_port calls)."""
import copy
import unittest

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtTest import QTest

from test_editor import APP
from app import Window
import pidcore as core


class ConnectionInteractionTests(unittest.TestCase):
    def setUp(self):
        self.window = Window()
        self.window.resize(1280, 800)
        self.window.show()
        APP.processEvents()

    def tearDown(self):
        APP.clipboard().clear()
        self.window.saved = copy.deepcopy(self.window.document)
        self.window.close()
        APP.processEvents()

    def layout(self, distance=240, zoom=1):
        window = self.window
        window.document = core.new_document()
        source = core.component('pump', 0, 0, window.document)
        window.document['components'].append(source)
        target = core.component('valve', distance, 0, window.document)
        window.document['components'].append(target)
        window.rebuild()
        window.view.resetTransform()
        window.view.scale(zoom, zoom)
        window.view.centerOn(QPointF(distance / 2, 0))
        APP.processEvents()
        return source['id'], target['id']

    def port_position(self, identifier, port):
        view = self.window.view
        position = view.mapFromScene(self.window.symbols[identifier].port(port))
        self.assertTrue(view.viewport().rect().contains(position))
        return position

    def click_port(self, identifier, port, offset=QPoint()):
        QTest.mouseClick(self.window.view.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier,
                         self.port_position(identifier, port) + offset)
        APP.processEvents()

    def assert_connection(self, source, target):
        connections = self.window.document['connections']
        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0]['from'], {'component': source, 'port': 'outlet'})
        self.assertEqual(connections[0]['to'], {'component': target, 'port': 'inlet'})
        self.assertIsNone(self.window.pending)

    def test_two_exact_port_clicks_connect(self):
        source, target = self.layout()
        self.click_port(source, 'outlet')
        self.click_port(target, 'inlet')
        self.assert_connection(source, target)

    def test_port_inside_neighbor_invisible_bounds_connects(self):
        # Source outlet x=40 lies in the later valve's invisible x=35..165
        # bounding box; valve's actual body starts at x=78.
        source, target = self.layout(distance=100)
        self.click_port(source, 'outlet')
        self.assertEqual(self.window.pending, {'component': source, 'port': 'outlet'})
        self.click_port(target, 'inlet')
        self.assert_connection(source, target)

    def test_zoomed_out_exact_port_clicks_connect(self):
        source, target = self.layout(zoom=.25)
        self.click_port(source, 'outlet')
        self.click_port(target, 'inlet')
        self.assert_connection(source, target)

    def test_zoomed_out_port_has_screen_space_click_tolerance(self):
        for zoom in (.25, .4):
            with self.subTest(zoom=zoom):
                source, target = self.layout(zoom=zoom)
                self.click_port(source, 'outlet', QPoint(0, 5))
                self.assertEqual(self.window.pending, {'component': source, 'port': 'outlet'})
                self.click_port(target, 'inlet', QPoint(0, 5))
                self.assert_connection(source, target)

    def test_existing_pipe_does_not_block_endpoint_click(self):
        source, target = self.layout()
        self.window.document['connections'].append({
            'id':core.uid(), 'from':{'component':source,'port':'outlet'},
            'to':{'component':target,'port':'inlet'}, 'kind':'process',
            'label':'', 'waypoints':[],
        })
        self.window.rebuild()
        APP.processEvents()
        self.click_port(source, 'outlet')
        self.assertEqual(self.window.pending, {'component':source,'port':'outlet'})

    def test_drag_between_ports_connects_without_moving_equipment(self):
        source, target = self.layout()
        before_positions = [r['position'][:] for r in self.window.document['components']]
        viewport = self.window.view.viewport()
        start = self.port_position(source, 'outlet')
        end = self.port_position(target, 'inlet')
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, start)
        QTest.mouseMove(viewport, (start + end) / 2)
        QTest.mouseMove(viewport, end)
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton,
                           Qt.KeyboardModifier.NoModifier, end)
        APP.processEvents()
        self.assert_connection(source, target)
        self.assertEqual([r['position'] for r in self.window.document['components']], before_positions)

    def test_escape_cancels_then_connection_can_be_undone_and_redone(self):
        source, target = self.layout()
        before = copy.deepcopy(self.window.document)
        self.click_port(source, 'outlet')
        QTest.keyClick(self.window.view, Qt.Key.Key_Escape)
        APP.processEvents()
        self.assertIsNone(self.window.pending)
        self.assertEqual(self.window.document, before)
        self.click_port(source, 'outlet')
        self.click_port(target, 'inlet')
        self.assert_connection(source, target)
        QTest.keyClick(self.window.view, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        APP.processEvents()
        self.assertEqual(self.window.document, before)
        QTest.keyClick(self.window.view, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
        APP.processEvents()
        self.assert_connection(source, target)

    def test_dragging_equipment_body_still_moves_it_with_undo(self):
        source, target = self.layout()
        before = copy.deepcopy(self.window.document)
        viewport = self.window.view.viewport()
        start = self.window.view.mapFromScene(self.window.symbols[source].pos())
        end = start + QPoint(60, 40)
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, start)
        QTest.mouseMove(viewport, end)
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton,
                           Qt.KeyboardModifier.NoModifier, end)
        APP.processEvents()
        self.assertEqual(self.window.symbols[source].record['position'], [60, 40])
        self.assertEqual(self.window.symbols[target].record['position'], [240, 0])
        self.assertIsNone(self.window.pending)
        self.assertEqual(self.window.document['connections'], [])
        self.window.undo()
        self.assertEqual(self.window.document, before)

    def test_zoomed_out_body_center_selects_without_starting_connection(self):
        source, _ = self.layout(zoom=.2)
        before = copy.deepcopy(self.window.document)
        position = self.window.view.mapFromScene(self.window.symbols[source].pos())
        QTest.mouseClick(self.window.view.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, position)
        APP.processEvents()
        self.assertTrue(self.window.symbols[source].isSelected())
        self.assertIsNone(self.window.pending)
        self.assertEqual(self.window.document, before)

    def test_zoomed_in_click_outside_pixel_tolerance_does_not_start_connection(self):
        source, _ = self.layout(zoom=2)
        before = copy.deepcopy(self.window.document)
        viewport = self.window.view.viewport()
        # Eight scene units is inside the former Symbol fallback hit test,
        # but 16 screen pixels is outside the Canvas port target.
        start = self.port_position(source, 'outlet') + QPoint(0, 16)
        end = start + QPoint(40, 40)
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, start)
        self.assertIsNone(self.window.pending)
        QTest.mouseMove(viewport, end)
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton,
                           Qt.KeyboardModifier.NoModifier, end)
        APP.processEvents()
        self.assertIsNone(self.window.pending)
        self.assertEqual(self.window.document['connections'], [])
        self.assertEqual(self.window.symbols[source].record['position'], [20, 20])
        self.window.undo()
        self.assertEqual(self.window.document, before)


if __name__ == '__main__':
    unittest.main()
