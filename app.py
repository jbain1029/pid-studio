"""PID Studio — compact desktop P&ID drafting editor."""
import copy
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QPointF, QRectF, QMimeData, QSize
from PySide6.QtGui import QAction, QColor, QDrag, QPainter, QPainterPath, QPen, QPolygonF, QKeySequence, QFontDatabase, QFont
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsObject, QGraphicsItem, QGraphicsPathItem, QGraphicsSimpleTextItem,
    QListWidget, QListWidgetItem, QDockWidget, QTableWidget, QTableWidgetItem,
    QToolBar, QFileDialog, QMessageBox, QAbstractItemView, QMenu)
import pidcore as core
import classic
import routing
import workspace
import deliverables
import sketch
import assistant_ui
import symbol_art
import drafting
import annotations
import diagnostics
import drawio_export
import editing
import sheet_preview
import symbol_library
import connection_editor
import component_browser

BLUE = QColor('#24659b')
INK = QColor('#263238')

class Palette(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        for kind, definition in core.CATALOG.items():
            item = QListWidgetItem(definition['label'])
            item.setData(Qt.ItemDataRole.UserRole, kind)
            self.addItem(item)
        self.setSpacing(2)

    def startDrag(self, actions):
        if not self.currentItem():
            return
        data = QMimeData()
        data.setData('application/x-pid-symbol', self.currentItem().data(Qt.ItemDataRole.UserRole).encode())
        drag = QDrag(self)
        drag.setMimeData(data)
        drag.exec(Qt.DropAction.CopyAction)

class Symbol(QGraphicsObject):
    def __init__(self, record, window):
        super().__init__()
        self.record, self.window = record, window
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setPos(*record['position'])
        self.definition = core.definition(record,getattr(window,'document',None))
        self.setToolTip(f"{record['tag']} — {self.definition['label']}\nClick a blue port, then another port to connect.")
        if self.definition.get('legend_reference'):
            self.setToolTip(self.toolTip()+'\nReference: pid-legend.pdf — '+self.definition['legend_reference'])
        if self.definition.get('symbol_reference'):
            self.setToolTip(self.toolTip()+'\nSource convention: '+self.definition['symbol_reference'])
        for port,meaning in self.definition.get('port_meanings',{}).items():
            self.setToolTip(self.toolTip()+f'\n{port}: {meaning} Illustrative handle only; new connections are unsupported. Use a drawing note.')
        for note in self.definition.get('symbol_notes',[]):
            self.setToolTip(self.toolTip()+'\nConvention: '+note)

    def boundingRect(self):
        return QRectF(-65, -65, 130, 140)

    def port_local(self, name):
        x, y = self.definition['ports'][name]
        for _ in range(self.record['rotation'] // 90):
            x, y = -y, x
        return QPointF(x, y)

    def port(self, name):
        return self.mapToScene(self.port_local(name))

    def paint(self, p, option, widget):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isSelected() and not self.window.exporting:
            p.setPen(QPen(BLUE, 1, Qt.PenStyle.DashLine))
            p.setBrush(QColor('#edf5fb'))
            p.drawRect(QRectF(-48, -46, 96, 92))
        p.save()
        p.rotate(self.record['rotation'])
        p.setPen(QPen(INK, 2))
        p.setBrush(Qt.GlobalColor.white)
        kind = self.record['type']
        extended = symbol_library.draw_artwork(p,self.definition,labels=False) if 'artwork' in self.definition else symbol_art.draw(p,kind)
        if not extended and kind not in ('instrument', 'tee'):
            p.drawLine(-40, 0, 40, 0)
        if extended:
            pass
        elif kind == 'tank':
            p.drawRect(-28, -30, 56, 60)
            p.drawEllipse(-28, -36, 56, 12)
        elif kind in ('pump', 'exchanger', 'instrument'):
            p.drawEllipse(-26, -26, 52, 52)
            if kind == 'pump':
                p.drawPolygon(QPolygonF([QPointF(-12, -17), QPointF(20, 0), QPointF(-12, 17)]))
            elif kind == 'exchanger':
                p.drawPolyline(QPolygonF([QPointF(-18, 0), QPointF(-9, -12), QPointF(0, 12), QPointF(9, -12), QPointF(18, 0)]))
                p.drawLine(0, -30, 0, -26)
                p.drawLine(0, 26, 0, 30)
            else:
                p.drawLine(0, -30, 0, -26)
                p.drawLine(0, 26, 0, 30)
        elif kind in ('valve', 'control_valve', 'check_valve'):
            p.drawPolygon(QPolygonF([QPointF(-22, -16), QPointF(22, 16), QPointF(22, -16), QPointF(-22, 16)]))
            if kind == 'control_valve':
                p.drawLine(0, 0, 0, -30)
                p.drawRect(-15, -38, 30, 10)
            elif kind == 'check_valve':
                p.drawLine(24, -18, 24, 18)
        elif kind == 'filter':
            p.drawRect(-25, -21, 50, 42)
            p.drawLine(-22, 18, 22, -18)
        elif kind == 'tee':
            p.drawLine(-40, 0, 40, 0)
            p.drawLine(0, 0, 0, -30)
            p.setBrush(INK)
            p.drawEllipse(-4, -4, 8, 8)
        else:
            p.drawPolygon(QPolygonF([QPointF(-25, -15), QPointF(15, -15), QPointF(30, 0), QPointF(15, 15), QPointF(-25, 15)]))
        p.restore()
        p.setPen(INK)
        symbol_library.draw_legend_labels(p,self.definition,self.record['tag'],self.record['rotation'])
        if not getattr(self.window, 'hide_external_tags', False):
            p.drawText(QRectF(-65, 44, 130, 31), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.record['tag'])
        if not self.window.exporting:
            p.setPen(QPen(BLUE, 1))
            p.setBrush(Qt.GlobalColor.white)
            for name in self.definition['ports']:
                p.drawEllipse(self.port_local(name), 4, 4)

    def mousePressEvent(self, e):
        self.window.before_drag = copy.deepcopy(self.window.document)
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)
        self.setPos(drafting.snap(self.window,self.x()), drafting.snap(self.window,self.y()))
        self.record['position'] = [self.x(), self.y()]
        self.window.update_lines(interactive=True)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        # Group movement must update every selected record, not just the grabbed symbol.
        for symbol in self.window.symbols.values():
            symbol.record['position'] = [symbol.x(), symbol.y()]
        for item in self.window.scene.selectedItems():
            if isinstance(item,annotations.Note):
                item.record['position'] = [item.x(),item.y()]
        self.window.update_lines()
        if self.window.before_drag is not None and self.window.before_drag != self.window.document:
            self.window.history.append(self.window.before_drag)
            self.window.future.clear()
            self.window.changed()
        self.window.before_drag = None

class Pipe(QGraphicsPathItem):
    def __init__(self, record, window):
        super().__init__()
        self.record, self.window = record, window
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)
        self.label = QGraphicsSimpleTextItem(self)
        self.handles = []
        self.route_error = None
        self.update_route()

    def update_route(self, interactive=False):
        r = self.record
        a = self.window.symbols[r['from']['component']].port(r['from']['port'])
        b = self.window.symbols[r['to']['component']].port(r['to']['port'])
        def direction(endpoint):
            symbol = self.window.symbols[endpoint['component']]
            local = symbol.port_local(endpoint['port'])
            return (1 if local.x()>0 else -1, 0) if abs(local.x())>abs(local.y()) else (0, 1 if local.y()>0 else -1)
        boxes = [core.routing_bounds(s.record, (s.x(), s.y()),getattr(self.window,'document',None)) for s in self.window.symbols.values()]
        anchors = ((a.x(), a.y()), (b.x(), b.y()), direction(r['from']),
                   direction(r['to']), tuple(tuple(p) for p in r['waypoints']))
        # During dragging, retain only routes whose endpoints, directions and
        # waypoints are unchanged and whose EVERY segment is still clear.
        # Release always uses the canonical router again (no persisted cache).
        previous = getattr(self, '_valid_points', None)
        reuse = (interactive and previous and getattr(self, '_anchors', None) == anchors
                 and all(routing.clear(p, q, boxes) for p, q in zip(previous, previous[1:])))
        self.route_error = None
        try:
            points = previous if reuse else routing.route(*anchors[:4], boxes, r['waypoints'])
            self._valid_points = points
        except routing.RouteError as error:
            self._valid_points = None
            self.route_error = str(error)
            points = [(a.x(),a.y()), (b.x(),a.y()), (b.x(),b.y())]
        self._anchors = anchors
        path = QPainterPath(QPointF(*points[0]))
        for v in points[1:]:
            path.lineTo(QPointF(*v))
        self.setPath(path)
        self.setPen(QPen(QColor('#b53624') if self.route_error else BLUE if self.isSelected() else INK, 2, Qt.PenStyle.DashLine if r['kind']=='signal' else Qt.PenStyle.SolidLine))
        self.setToolTip(self.route_error or 'Double-click to add a routing waypoint. Right-click for routing commands.')
        self.label.setText(r['label'])
        self.label.setPos(path.pointAtPercent(.5)+QPointF(6, -22))
        if len(self.handles) != len(r['waypoints']):
            for handle in self.handles:
                if handle.scene():
                    handle.scene().removeItem(handle)
            self.handles = [Waypoint(self, index) for index in range(len(r['waypoints']))]
        for handle, point in zip(self.handles, r['waypoints']):
            handle.setPos(*point)
            handle.setVisible(self.isSelected() and not self.window.exporting)

    def mouseDoubleClickEvent(self, event):
        self.window.checkpoint()
        point = event.scenePos()
        waypoint = [drafting.snap(self.window,point.x()), drafting.snap(self.window,point.y())]
        # Insert near the route location, preserving existing waypoint order.
        polyline = list(self.path().toSubpathPolygons()[0])
        def along(pos):
            best, distance, chosen = float('inf'), 0, 0
            for a, b in zip(polyline, polyline[1:]):
                dx, dy = b.x()-a.x(), b.y()-a.y()
                length2 = dx*dx+dy*dy
                t = max(0, min(1, ((pos[0]-a.x())*dx+(pos[1]-a.y())*dy)/length2)) if length2 else 0
                gap = (pos[0]-a.x()-t*dx)**2+(pos[1]-a.y()-t*dy)**2
                if gap < best:
                    best, chosen = gap, distance+t*length2**.5
                distance += length2**.5
            return chosen
        self.record['waypoints'].append(waypoint)
        self.record['waypoints'].sort(key=along)
        self.update_route()
        self.setSelected(True)
        self.window.changed()
        event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu()
        reset = menu.addAction('Reset to automatic routing')
        if menu.exec(event.screenPos()) == reset and self.record['waypoints']:
            self.window.checkpoint()
            self.record['waypoints'] = []
            self.update_route()
            self.window.changed()

class Waypoint(QGraphicsObject):
    def __init__(self, pipe, index):
        super().__init__(pipe)
        self.pipe, self.index = pipe, index
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setZValue(5)
        self.setToolTip('Drag to reroute. Right-click to remove waypoint.')

    def boundingRect(self):
        return QRectF(-6,-6,12,12)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(BLUE, 1))
        painter.setBrush(QColor('#fff9c7'))
        painter.drawRect(QRectF(-4,-4,8,8))

    def mousePressEvent(self, event):
        self.before = copy.deepcopy(self.pipe.window.document)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.pipe.record['waypoints'][self.index] = [drafting.snap(self.pipe.window,self.x()), drafting.snap(self.pipe.window,self.y())]
        self.pipe.update_route()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        window = self.pipe.window
        if self.before != window.document:
            window.history.append(self.before)
            window.future.clear()
            window.changed()

    def contextMenuEvent(self, event):
        menu = QMenu()
        remove = menu.addAction('Remove waypoint')
        if menu.exec(event.screenPos()) == remove:
            self.pipe.window.checkpoint()
            del self.pipe.record['waypoints'][self.index]
            self.pipe.window.changed()
            # Rebuild after the current item's event handler has returned.
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self.pipe.window.rebuild)

class Canvas(QGraphicsView):
    def __init__(self, window):
        super().__init__(window.scene)
        self.window = window
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.connection_cursor = None
        self.port_press = False
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(Qt.GlobalColor.white)

    def keyPressEvent(self, event):
        directions = {Qt.Key.Key_Left: (-1, 0), Qt.Key.Key_Right: (1, 0),
                      Qt.Key.Key_Up: (0, -1), Qt.Key.Key_Down: (0, 1)}
        if event.matches(QKeySequence.StandardKey.SelectAll):
            editing.select_all(self.window)
            event.accept()
            return
        if event.key() in directions and not event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            step = self.window.snap_spacing if self.window.snap_enabled else 1
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                step *= 10
            dx, dy = directions[event.key()]
            if editing.nudge(self.window, dx * step, dy * step):
                event.accept()
                return
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        target = self.itemAt(event.pos())
        if isinstance(target, Waypoint):
            super().contextMenuEvent(event)
            return
        while target is not None and not hasattr(target, 'record'):
            target = target.parentItem()
        menu = editing.context_menu(self.window, target)
        menu.exec(event.globalPos())
        menu.deleteLater()
        event.accept()

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, Qt.GlobalColor.white)
        sketch.background(self.window,painter)
        painter.setPen(QPen(QColor('#e2e6e9'), 0))
        if getattr(self, 'show_grid', True):
            step = drafting.grid_spacing(self.window)
            for x in range(int(rect.left())//step*step, int(rect.right())+step, step):
                for y in range(int(rect.top())//step*step, int(rect.bottom())+step, step):
                    painter.drawPoint(x, y)

    def wheelEvent(self, e):
        factor = 1.15 if e.angleDelta().y() > 0 else 1/1.15
        if .15 < self.transform().m11()*factor < 5:
            self.scale(factor, factor)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('application/x-pid-symbol') or self.dropped_document(e.mimeData()):
            e.acceptProposedAction()

    def dragMoveEvent(self, e):
        if e.mimeData().hasFormat('application/x-pid-symbol') or self.dropped_document(e.mimeData()):
            e.acceptProposedAction()

    @staticmethod
    def dropped_document(mime):
        urls = mime.urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            path = urls[0].toLocalFile()
            if Path(path).suffix.lower() in ('.pid','.json'):
                return path
        return None

    def dropEvent(self, e):
        path = self.dropped_document(e.mimeData())
        if path:
            if self.window.open_path(path):
                e.acceptProposedAction()
            return
        if not e.mimeData().hasFormat('application/x-pid-symbol'):
            return
        kind = bytes(e.mimeData().data('application/x-pid-symbol')).decode()
        point = self.mapToScene(e.position().toPoint())
        self.window.add_symbol(kind, point)
        e.acceptProposedAction()

    def port_at(self, position):
        # Hit-test in screen pixels before scene items: pipes and overlapping
        # symbol bounding boxes must not steal clicks on a visible port.
        nearest, distance = None, 11 ** 2
        for symbol in self.window.symbols.values():
            for name in symbol.definition['ports']:
                point = self.mapFromScene(symbol.port(name))
                delta = point - position
                squared = delta.x() ** 2 + delta.y() ** 2
                center_delta = point - self.mapFromScene(symbol.scenePos())
                center_distance = center_delta.x() ** 2 + center_delta.y() ** 2
                # Preserve a selectable body at small scales: the padded port
                # target must not grow all the way to the equipment center.
                radius_squared = min(11 ** 2, center_distance * .75 ** 2) if center_distance else 11 ** 2
                if squared < min(distance, radius_squared):
                    nearest, distance = (symbol.record['id'], name), squared
        return nearest

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        pending = self.window.pending
        if self.window.exporting or not pending:
            return
        symbol = self.window.symbols.get(pending['component'])
        if symbol is None:
            return
        start = symbol.port(pending['port'])
        pen = QPen(BLUE, 1, Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(QColor('#b8dcf5'))
        radius = 7 / self.transform().m11()
        painter.drawEllipse(start, radius, radius)
        if self.connection_cursor is not None:
            painter.drawLine(start, self.connection_cursor)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.MiddleButton:
            self.pan_start = e.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            e.accept()
        elif e.button() == Qt.MouseButton.LeftButton and (port := self.port_at(e.position().toPoint())):
            self.port_press = True
            self.connection_cursor = self.mapToScene(e.position().toPoint())
            self.window.connect_port(*port)
            self.viewport().update()
            e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        self.connection_cursor = self.mapToScene(e.position().toPoint())
        if self.window.pending:
            self.viewport().update()
        if self.port_press:
            e.accept()
            return
        if e.buttons() & Qt.MouseButton.MiddleButton:
            delta = e.position()-self.pan_start
            self.pan_start = e.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-int(delta.y()))
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.port_press:
            self.port_press = False
            port = self.port_at(e.position().toPoint())
            pending = self.window.pending
            if port and pending and port != (pending['component'], pending['port']):
                self.window.connect_port(*port)
            self.viewport().update()
            e.accept()
            return
        self.unsetCursor()
        super().mouseReleaseEvent(e)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.document = core.new_document()
        self.path = None
        self.saved = copy.deepcopy(self.document)
        self.history, self.future = [], []
        self.pending = self.before_drag = None
        self.reconnecting = None
        self.exporting = False
        self.symbols = {}
        self.pipes = []
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-3000, -3000, 6000, 6000)
        self.view = Canvas(self)
        self.setCentralWidget(self.view)
        self.resize(1280, 820)
        palette = classic.Toolbox()
        self.palette = palette
        palette.itemDoubleClicked.connect(lambda i, column: self.add_symbol(i.data(0, Qt.ItemDataRole.UserRole), self.view.mapToScene(self.view.viewport().rect().center())))
        self.dock('Toolbox — Components', palette, Qt.DockWidgetArea.LeftDockWidgetArea)
        self.properties = QTableWidget(0, 2)
        self.properties.setHorizontalHeaderLabels(['Property', 'Value'])
        self.properties.horizontalHeader().setStretchLastSection(True)
        self.properties.verticalHeader().hide()
        self.properties.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.properties.cellChanged.connect(self.edit_property)
        self.dock('Details', self.properties, Qt.DockWidgetArea.RightDockWidgetArea)
        self.messages = QListWidget()
        self.messages.setMaximumHeight(110)
        self.dock('Messages', self.messages, Qt.DockWidgetArea.BottomDockWidgetArea)
        toolbar = QToolBar('Standard')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        groups = [('File', [('New', 'Ctrl+N', self.new), ('Open…', 'Ctrl+O', self.open), ('Save', 'Ctrl+S', self.save), ('Save As…', 'Ctrl+Shift+S', lambda: self.save(True)), ('Export SVG…', '', self.export)]),
                  ('Edit', [('Undo', 'Ctrl+Z', self.undo), ('Redo', 'Ctrl+Y', self.redo), ('Delete', 'Del', self.delete), ('Duplicate', 'Ctrl+D', self.duplicate), ('Rotate 90°', 'R', self.rotate), ('Cancel connection', 'Esc', self.cancel)]),
                  ('View', [('Fit drawing', 'F', self.fit), ('Validate', 'F7', self.validate), ('Example system', '', self.example)])]
        for group, items in groups:
            menu = self.menuBar().addMenu(group)
            for label, shortcut, callback in items:
                action = QAction(label, self)
                if shortcut:
                    action.setShortcut(QKeySequence(shortcut))
                action.triggered.connect(lambda checked=False, cb=callback: cb())
                menu.addAction(action)
                if label not in ('Save As…', 'Cancel connection', 'Example system'):
                    toolbar.addAction(action)
            toolbar.addSeparator()
        self.scene.selectionChanged.connect(self.selection)
        self.changed()
        self.statusBar().showMessage('Drag components from Toolbox. Click two ports to connect. Wheel: zoom | Middle drag: pan | R: rotate')
        self.view.centerOn(0, 0)
        classic.install(self)
        workspace.install(self)
        deliverables.install(self)
        sketch.install(self)
        assistant_ui.install(self)
        drafting.install(self)
        annotations.install(self)
        diagnostics.install(self)
        drawio_export.install(self)
        sheet_preview.install(self)
        symbol_library.install(self)
        connection_editor.install(self)
        component_browser.install(self)

    def dock(self, title, widget, area):
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setMinimumWidth(205)
        self.addDockWidget(area, dock)

    def checkpoint(self):
        self.history.append(copy.deepcopy(self.document))
        self.future.clear()

    def changed(self):
        dirty = self.document != self.saved
        self.setWindowTitle(f"{self.document['title']}{' *' if dirty else ''} — PID Studio")
        classic.rebuild_outline(self)
        if hasattr(self, 'sheet_preview') and self.sheet_preview.isVisible():
            self.sheet_preview.refresh()

    def rebuild(self):
        self.pending = None
        self.reconnecting = None
        self.palette.set_catalog(core.catalog_for(self.document))
        self.scene.blockSignals(True)
        self.scene.clear()
        self.symbols = {}
        self.pipes = []
        for r in self.document['components']:
            obj = Symbol(r, self)
            self.symbols[r['id']] = obj
            self.scene.addItem(obj)
        for r in self.document['connections']:
            obj = Pipe(r, self)
            self.pipes.append(obj)
            self.scene.addItem(obj)
        for record in self.document.get('notes',[]):
            self.scene.addItem(annotations.Note(record,self))
        self.scene.blockSignals(False)
        self.selection()
        self.changed()
        sketch.refresh(self)

    def add_symbol(self, kind, point):
        if kind not in core.catalog_for(self.document):
            return
        self.checkpoint()
        self.document['components'].append(core.component(kind, drafting.snap(self,point.x()), drafting.snap(self,point.y()), self.document))
        self.rebuild()

    def connect_port(self, node, port):
        endpoint = {'component': node, 'port': port}
        component = next((record for record in self.document['components'] if record['id'] == node), None)
        if component is None or port not in core.definition(component,self.document).get('ports', {}):
            self.statusBar().showMessage('Cannot connect: that component or port no longer exists. Choose another port or press Escape.')
            return False
        if self.reconnecting:
            return editing.finish_reconnect(self,endpoint)
        from connection_policy import attachment_reason
        reason = attachment_reason(self.document, endpoint)
        if reason:
            self.statusBar().showMessage('Cannot connect: ' + reason)
            return False
        if self.pending is None:
            self.pending = endpoint
            self.statusBar().showMessage(f"Connecting {component['tag']}.{port} — click destination port; Escape cancels")
            self.view.viewport().update()
            return
        if self.pending == endpoint:
            self.cancel()
            return
        draft = copy.deepcopy(self.document)
        line = {'id': core.uid(), 'from': copy.deepcopy(self.pending), 'to': endpoint,
                'kind': 'signal' if any(core.port_kind(draft,e)=='signal' for e in (endpoint,self.pending)) else 'process',
                'label': '', 'waypoints': []}
        draft['connections'].append(line)
        errors = core.validate(draft)
        if errors:
            self.statusBar().showMessage('Cannot connect: '+errors[0]+'. Choose another port or press Escape.')
            return False
        self.checkpoint()
        self.document = draft
        self.rebuild()
        editing.restore_selection(self, {line['id']})
        self.statusBar().showMessage('Connection created. Set its label and kind in Details of Selection; Undo removes it.')
        return True

    def cancel(self):
        self.pending = None
        self.reconnecting = None
        self.statusBar().showMessage('Connection cancelled')
        self.view.viewport().update()

    def update_lines(self, interactive=False):
        for pipe in self.pipes:
            pipe.update_route(interactive=interactive)

    def selection(self):
        self.update_lines()
        items = self.scene.selectedItems()
        self.selected = items[0] if len(items)==1 else None
        self.properties.blockSignals(True)
        self.properties.setRowCount(0)
        if self.selected:
            record = self.selected.record
            keys = ['text','width'] if isinstance(self.selected,annotations.Note) else ['tag', 'description', 'rotation'] if isinstance(self.selected, Symbol) else ['label', 'kind']
        else:
            record, keys = self.document, ['title']
        for key in keys:
            row = self.properties.rowCount()
            self.properties.insertRow(row)
            label = QTableWidgetItem(key.title())
            label.setFlags(label.flags() & ~Qt.ItemFlag.ItemIsEditable)
            label.setData(Qt.ItemDataRole.UserRole, key)
            self.properties.setItem(row, 0, label)
            self.properties.setItem(row, 1, QTableWidgetItem(str(record[key])))
        self.properties.blockSignals(False)
        classic.refresh_status(self)

    def edit_property(self, row, col):
        if col != 1:
            return
        key = self.properties.item(row, 0).data(Qt.ItemDataRole.UserRole)
        value = self.properties.item(row, 1).text()
        try:
            if key == 'width':
                value = float(value)
            if key == 'rotation':
                value = int(value)
                if value not in (0, 90, 180, 270):
                    raise ValueError('Rotation must be 0, 90, 180, or 270')
            if key == 'kind' and value not in ('process', 'signal'):
                raise ValueError('Line kind must be process or signal')
            old = copy.deepcopy(self.document)
            record = self.selected.record if self.selected else self.document
            record[key] = value
            errors = core.validate(self.document)
            if errors:
                self.document = old
                self.rebuild()
                raise ValueError('\n'.join(errors))
            self.history.append(old)
            self.future.clear()
            self.rebuild()
        except ValueError as e:
            QMessageBox.warning(self, 'Invalid property', str(e))
            self.selection()

    def delete(self):
        ids = {i.record['id'] for i in self.scene.selectedItems()}
        if not ids:
            return
        self.checkpoint()
        self.document['components'] = [r for r in self.document['components'] if r['id'] not in ids]
        self.document['connections'] = [r for r in self.document['connections'] if r['id'] not in ids and r['from']['component'] not in ids and r['to']['component'] not in ids]
        if 'notes' in self.document:
            self.document['notes'] = [r for r in self.document['notes'] if r['id'] not in ids]
        self.rebuild()

    def duplicate(self):
        selected = [i.record for i in self.scene.selectedItems() if isinstance(i, Symbol)]
        notes = [i.record for i in self.scene.selectedItems() if isinstance(i,annotations.Note)]
        if not selected and not notes:
            return
        self.checkpoint()
        mapping = {}
        for record in notes:
            new = copy.deepcopy(record)
            new['id'] = core.uid()
            new['position'] = [v+40 for v in new['position']]
            self.document.setdefault('notes',[]).append(new)
        for r in selected:
            c = core.component(r['type'], r['position'][0]+100, r['position'][1]+100, self.document)
            c['rotation'], c['description'] = r['rotation'], r['description']
            if 'metadata' in r:
                c['metadata'] = copy.deepcopy(r['metadata'])
            mapping[r['id']] = c['id']
            self.document['components'].append(c)
        for line in list(self.document['connections']):
            if line['from']['component'] in mapping and line['to']['component'] in mapping:
                c = copy.deepcopy(line)
                c['id'] = core.uid()
                for end in ('from', 'to'):
                    c[end]['component'] = mapping[c[end]['component']]
                c['waypoints'] = [[x+100, y+100] for x, y in c['waypoints']]
                self.document['connections'].append(c)
        self.rebuild()

    def rotate(self):
        symbols = [i for i in self.scene.selectedItems() if isinstance(i, Symbol)]
        if symbols:
            selected_ids = {i.record['id'] for i in self.scene.selectedItems()}
            self.checkpoint()
            for item in symbols:
                item.record['rotation'] = (item.record['rotation']+90)%360
            self.rebuild()
            editing.restore_selection(self, selected_ids)

    def undo(self):
        if self.history:
            self.future.append(copy.deepcopy(self.document))
            self.document = self.history.pop()
            self.rebuild()

    def redo(self):
        if self.future:
            self.history.append(copy.deepcopy(self.document))
            self.document = self.future.pop()
            self.rebuild()

    def confirm_discard(self):
        if self.document == self.saved:
            return True
        answer = QMessageBox.question(self, 'Unsaved drawing', 'Save changes to this drawing?', QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Save:
            return self.save()
        return answer == QMessageBox.StandardButton.Discard

    def new(self):
        if self.confirm_discard():
            self.document = core.new_document()
            self.saved = copy.deepcopy(self.document)
            self.path = None
            self.history.clear()
            self.future.clear()
            self.rebuild()

    def open(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open P&ID', '', 'PID Studio (*.pid *.json)')
        if path:
            return self.open_path(path)
        return False

    def open_path(self, path):
        try:
            path = str(Path(path).resolve())
            document = core.load(path)
        except (ValueError,OSError) as error:
            QMessageBox.warning(self,'Cannot open drawing',str(error))
            return False
        if not self.confirm_discard():
            return False
        self.document, self.path = document, path
        self.saved = copy.deepcopy(document)
        self.history.clear()
        self.future.clear()
        self.rebuild()
        self.fit()
        workspace.update_recent(self,path)
        return True

    def save(self, save_as=False):
        path = self.path
        if not path or save_as:
            path, _ = QFileDialog.getSaveFileName(self, 'Save P&ID', path or 'drawing.pid', 'PID Studio (*.pid)')
        if not path:
            return False
        if not Path(path).suffix:
            path += '.pid'
        try:
            core.save(self.document, path)
            self.path = path
            workspace.update_recent(self,path)
            self.saved = copy.deepcopy(self.document)
            self.changed()
            self.statusBar().showMessage(f'Saved {path}')
            return True
        except Exception as e:
            QMessageBox.warning(self, 'Cannot save drawing', str(e))
            return False

    def fit(self):
        if self.symbols or self.document.get('notes'):
            self.view.fitInView(self.scene.itemsBoundingRect().adjusted(-80, -80, 80, 80), Qt.AspectRatioMode.KeepAspectRatio)

    def validate(self):
        diagnostics.populate(self)

    def export_to(self, path):
        bounds = self.scene.itemsBoundingRect().adjusted(-30, -30, 30, 30)
        if not self.symbols and not self.document.get('notes'):
            raise ValueError('Add components before exporting')
        generator = QSvgGenerator()
        generator.setFileName(str(path))
        generator.setSize(QSize(int(bounds.width()), int(bounds.height())))
        generator.setViewBox(QRectF(0, 0, bounds.width(), bounds.height()))
        generator.setTitle(self.document['title'])
        selected = list(self.scene.selectedItems())
        self.scene.clearSelection()
        self.exporting = True
        painter = QPainter(generator)
        try:
            painter.fillRect(QRectF(0, 0, bounds.width(), bounds.height()), Qt.GlobalColor.white)
            self.scene.render(painter, QRectF(0, 0, bounds.width(), bounds.height()), bounds)
        finally:
            painter.end()
            self.exporting = False
            for item in selected:
                item.setSelected(True)
            self.scene.update()

    def export(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Export SVG', 'drawing.svg', 'SVG image (*.svg)')
        if path:
            try:
                self.export_to(path)
            except Exception as e:
                QMessageBox.warning(self, 'Export failed', str(e))

    def example(self):
        if not self.confirm_discard():
            return
        self.document = core.new_document()
        self.document['title'] = 'Transfer System — Example'
        for kind, x in [('tank', 0), ('valve', 160), ('pump', 320), ('check_valve', 480), ('tank', 680)]:
            self.document['components'].append(core.component(kind, x, 0, self.document))
        for a, b in zip(self.document['components'], self.document['components'][1:]):
            self.document['connections'].append({'id': core.uid(), 'from': {'component': a['id'], 'port': 'outlet'}, 'to': {'component': b['id'], 'port': 'inlet'}, 'kind': 'process', 'label': '', 'waypoints': []})
        self.path = None
        self.history.clear()
        self.future.clear()
        self.rebuild()
        self.fit()

    def closeEvent(self, event):
        if self.confirm_discard():
            workspace.close(self)
            event.accept()
        else:
            event.ignore()

def main(document_path=None):
    app = QApplication(sys.argv)
    # Register fonts explicitly so offscreen exports use the same legible text as the desktop.
    for filename in ('segoeui.ttf', 'segoeuib.ttf'):
        font_path = Path('C:/Windows/Fonts') / filename
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))
    app.setFont(QFont('Segoe UI', 9))
    classic.apply_theme(app)
    window = Window()
    window.show()
    if document_path:
        window.open_path(document_path)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
