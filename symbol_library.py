"""Drawing-local vector symbol library; definitions are data, never executable code."""
import copy
import json
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPolygonF, QPainter
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QPlainTextEdit, QPushButton, QLabel, QFileDialog, QMessageBox, QGraphicsScene, QGraphicsView)
import pidcore as core
import custom_symbols


def draw_artwork(painter, definition, *, labels=True):
    for primitive in definition['artwork']:
        painter.save()
        if primitive.get('fill') == 'ink':
            painter.setBrush(painter.pen().color())
        kind = primitive['kind']
        if kind in ('line','polyline','polygon'):
            points = QPolygonF([QPointF(*point) for point in primitive['points']])
            if kind == 'polygon':
                painter.drawPolygon(points)
            else:
                painter.drawPolyline(points)
        elif kind == 'rect':
            painter.drawRect(QRectF(*primitive['rect']))
        elif kind == 'ellipse':
            painter.drawEllipse(QRectF(*primitive['rect']))
        painter.restore()
    if labels:
        draw_legend_labels(painter, definition)
    return True


def draw_legend_labels(painter, definition, tag=None, rotation=0):
    """Builtin reference lettering; custom files keep their bounded schema."""
    if not (definition.get('legend_bubble') or definition.get('legend_labels') or definition.get('upright_artwork')):
        return
    painter.save()
    font = painter.font()
    font.setPixelSize(12)
    painter.setFont(font)
    if definition.get('upright_artwork'):
        draw_artwork(painter, {'artwork':definition['upright_artwork']}, labels=False)
    if definition.get('legend_bubble'):
        from instrument_display import tag_lines, draw_fitted_text
        prefix, number = tag_lines(tag, definition['prefix'])
        if definition['legend_bubble'] == 'divided':
            painter.drawLine(-23,0,23,0)
        if definition.get('instrument_technology'):
            from instrument_display import draw_technology_bubble
            draw_technology_bubble(painter,prefix,number,definition['instrument_technology'])
        elif number:
            draw_fitted_text(painter, QRectF(-20,-20,40,19), prefix)
            draw_fitted_text(painter, QRectF(-20,1,40,19), number)
        else:
            draw_fitted_text(painter, QRectF(-20,-14,40,28), prefix)
    for label in definition.get('legend_labels', []):
        box = QRectF(*label['rect'])
        if label.get('follow_body'):
            center = box.center()
            x,y = center.x(),center.y()
            for _ in range(rotation//90):
                x,y = -y,x
            width,height = box.width(),box.height()
            if rotation%180:
                width,height = height,width
            box = QRectF(x-width/2,y-height/2,width,height)
        label_font = painter.font()
        label_font.setPixelSize(label.get('pixel_size',12))
        painter.setFont(label_font)
        painter.drawText(box, Qt.AlignmentFlag.AlignCenter, label['text'])
    painter.restore()


def apply_definition(window, envelope, *, replace_kind=None):
    """Apply one definition as an undoable transaction, validating all instances."""
    validated = custom_symbols.merge(core.new_document(), envelope)
    kind = envelope['kind']
    if replace_kind is not None:
        if kind != replace_kind:
            raise ValueError('Keep the existing kind ID when editing. Use New for a new kind.')
        candidate = copy.deepcopy(window.document)
        candidate.setdefault('symbol_definitions',{})[kind] = validated['symbol_definitions'][kind]
        errors = core.validate(candidate)
        if errors:
            raise ValueError('\n'.join(errors))
    else:
        candidate = custom_symbols.merge(window.document,envelope)
    if candidate == window.document:
        return False
    window.checkpoint()
    window.document = candidate
    window.rebuild()
    window.statusBar().showMessage('Component definition applied. It is embedded in this drawing and available in Toolbox.')
    return True


class LibraryDialog(QDialog):
    def __init__(self,window):
        super().__init__(window)
        self.window = window
        self.editing_kind = None
        self.setWindowTitle('Drawing component library')
        self.resize(1000,680)
        layout = QVBoxLayout(self)
        note = QLabel('Custom component definitions are embedded in the drawing. Import/export .pidsymbol files for reuse.\nEdit the bounded JSON definition below; Preview validates without changing the drawing. Applying edits updates all components of that kind.')
        note.setWordWrap(True)
        layout.addWidget(note)
        split = QSplitter()
        layout.addWidget(split,1)
        self.list = QListWidget()
        self.list.setMaximumWidth(240)
        split.addWidget(self.list)
        self.editor = QPlainTextEdit()
        self.editor.setAccessibleName('Component definition JSON')
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        split.addWidget(self.editor)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setInteractive(False)
        self.view.setMinimumWidth(200)
        split.addWidget(self.view)
        split.setSizes([200,540,260])
        self.status = QLabel('Choose a definition or create a new one.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        for title, callback in [('New',self.new),('Import…',self.import_file),('Export…',self.export_file),
                                ('Remove unused',self.remove),('Preview',self.preview),('Apply to drawing',self.apply)]:
            button = QPushButton(title)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        buttons.addStretch()
        close = QPushButton('Close')
        close.clicked.connect(self.accept)
        buttons.addWidget(close)
        self.list.currentRowChanged.connect(self.select)
        self.refresh()
        if self.list.count():
            self.list.setCurrentRow(0)
        else:
            self.new()

    def refresh(self):
        self.list.blockSignals(True)
        self.list.clear()
        self.kinds = sorted(self.window.document.get('symbol_definitions',{}))
        for kind in self.kinds:
            self.list.addItem(kind)
        self.list.blockSignals(False)

    def select(self,index):
        if index < 0 or index >= len(self.kinds):
            return
        kind = self.kinds[index]
        self.editing_kind = kind
        self.editor.setPlainText(json.dumps({'format':'pid-studio-symbol','version':1,'kind':kind,
            'definition':self.window.document['symbol_definitions'][kind]},indent=2))
        self.preview()

    def new(self):
        self.editing_kind = None
        envelope = custom_symbols.fixture()
        base = envelope['kind']
        suffix = 2
        while envelope['kind'] in self.window.document.get('symbol_definitions',{}):
            envelope['kind'] = base+'_'+str(suffix)
            suffix += 1
        self.editor.setPlainText(json.dumps(envelope,indent=2))
        self.preview()

    def parsed(self):
        text = self.editor.toPlainText()
        if len(text.encode('utf-8')) > 256*1024:
            raise ValueError('Component definition exceeds 256 KB.')
        try:
            envelope = json.loads(text)
        except RecursionError as error:
            raise ValueError('Component definition is nested too deeply.') from error
        custom_symbols.merge(core.new_document(),envelope)
        return envelope

    def preview(self):
        try:
            envelope = self.parsed()
            document = custom_symbols.merge(core.new_document(),envelope)
            record = core.component(envelope['kind'],0,0,document)
            from app import Symbol
            class Preview:
                exporting = False
            self.renderer = Preview()
            self.renderer.document = document
            self.scene.clear()
            self.scene.addItem(Symbol(record,self.renderer))
            self.view.fitInView(self.scene.itemsBoundingRect().adjusted(-15,-15,15,15),Qt.AspectRatioMode.KeepAspectRatio)
            self.status.setText('Valid definition. Blue circles are named ports; use Apply to add it to this drawing.')
            return True
        except (ValueError,TypeError,KeyError) as error:
            self.scene.clear()
            self.status.setText('Definition not applied: '+str(error))
            return False

    def apply(self):
        try:
            envelope = self.parsed()
            apply_definition(self.window,envelope,replace_kind=self.editing_kind)
            self.refresh()
            self.list.setCurrentRow(self.kinds.index(envelope['kind']))
            self.status.setText('Applied to the drawing. Save the drawing to retain this library.')
        except (ValueError,TypeError,KeyError) as error:
            self.status.setText('Definition not applied: '+str(error))

    def import_file(self):
        path,_ = QFileDialog.getOpenFileName(self,'Import component definition','','PID component definition (*.pidsymbol);;JSON (*.json)')
        if not path:
            return
        try:
            envelope = custom_symbols.load(path)
            self.editing_kind = None
            self.editor.setPlainText(json.dumps(envelope,indent=2))
            self.preview()
        except (OSError,ValueError,TypeError) as error:
            self.status.setText('Import failed: '+str(error))

    def export_file(self):
        try:
            envelope = self.parsed()
            path,_ = QFileDialog.getSaveFileName(self,'Export component definition',envelope['kind'].replace(':','-')+'.pidsymbol','PID component definition (*.pidsymbol)')
            if path:
                custom_symbols.save(envelope,path)
                self.status.setText('Component definition exported.')
        except (OSError,ValueError,TypeError) as error:
            self.status.setText('Export failed: '+str(error))

    def remove(self):
        kind = self.editing_kind
        if not kind:
            return
        if any(record['type']==kind for record in self.window.document['components']):
            self.status.setText('This definition is in use. Remove its components first; no components were changed.')
            return
        self.window.checkpoint()
        self.window.document['symbol_definitions'].pop(kind,None)
        self.window.rebuild()
        self.refresh()
        self.new()
        self.status.setText('Unused definition removed. Undo restores it.')


def install(window):
    menu = next(action.menu() for action in window.menuBar().actions() if action.text()=='Edit')
    menu.addSeparator()
    menu.addAction('Drawing component library…').triggered.connect(lambda:LibraryDialog(window).exec())
