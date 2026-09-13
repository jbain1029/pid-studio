"""Local sketch attachment and transactional proposal review workbench."""
import base64
import copy
import json
from pathlib import Path
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QAction, QImage
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPlainTextEdit, QDialogButtonBox,
    QFileDialog, QMessageBox, QFormLayout, QDoubleSpinBox, QGraphicsView, QGraphicsScene, QSplitter)
import pidcore as core
import operations
import review_history

def refresh(window):
    reference = window.document.get('reference')
    cache = reference.get('data') if reference else None
    if getattr(window,'reference_cache',None) != cache:
        window.reference_cache = cache
        window.reference_image = QImage()
        if reference:
            try:
                data = base64.b64decode(cache, validate=True)
                window.reference_image.loadFromData(data)
            except (ValueError,TypeError):
                pass
    window.view.viewport().update()

def background(window, painter):
    ref = window.document.get('reference')
    image = getattr(window,'reference_image',None)
    if not ref or image is None or image.isNull() or not getattr(window,'show_reference',True):
        return
    painter.save()
    painter.setOpacity(ref['opacity'])
    x,y = ref['position']
    painter.drawImage(QRectF(x,y,ref['width'],ref['width']*image.height()/image.width()),image)
    painter.restore()

def attach(window):
    path,_ = QFileDialog.getOpenFileName(window,'Attach reference sketch','','Images (*.png *.jpg *.jpeg *.bmp *.webp)')
    if not path:
        return
    try:
        if Path(path).stat().st_size>20_000_000:
            raise ValueError('Use a reference image under 20 MB.')
        data = Path(path).read_bytes()
        if len(data)>20_000_000:
            raise ValueError('Use a reference image under 20 MB.')
        image = QImage.fromData(data)
        if image.isNull():
            raise ValueError('This image could not be read.')
        window.checkpoint()
        window.document['reference'] = {'filename':Path(path).name,'data':base64.b64encode(data).decode(), 'position':[-500,-350], 'width':1000, 'opacity':0.35}
        window.rebuild()
    except (ValueError,OSError) as error:
        QMessageBox.warning(window,'Cannot attach image',str(error))

def placement(window):
    ref = window.document.get('reference')
    if not ref:
        QMessageBox.information(window,'Reference sketch','Attach a reference sketch first.')
        return
    dialog = QDialog(window)
    dialog.setWindowTitle('Reference image placement')
    form = QFormLayout(dialog)
    controls = []
    for name, value, lower, upper in [('Left',ref['position'][0],-10000,10000),('Top',ref['position'][1],-10000,10000),('Width',ref['width'],100,10000),('Opacity',ref['opacity'],0,1)]:
        spin = QDoubleSpinBox()
        spin.setRange(lower,upper)
        spin.setValue(value)
        spin.setSingleStep(.05 if name=='Opacity' else 10)
        form.addRow(name,spin)
        controls.append(spin)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    form.addRow(buttons)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        window.checkpoint()
        ref['position'] = [controls[0].value(),controls[1].value()]
        ref['width'],ref['opacity'] = controls[2].value(),controls[3].value()
        window.rebuild()

def review(window, proposal, *, generation=None):
    """Preview a validated proposal; modal acceptance is a single undo transaction."""
    draft = operations.apply(window.document,proposal)
    import generation_provenance
    if generation is not None:
        generation = copy.deepcopy(generation)
        generation_provenance.validate(generation,proposal['base_fingerprint'])
    dialog = QDialog(window)
    dialog.setWindowTitle('Review proposed drawing changes')
    dialog.resize(1000,650)
    layout = QVBoxLayout(dialog)
    introduction = QLabel('Review the draft and listed changes before applying. The current drawing is retained until Apply.')
    introduction.setMaximumHeight(35)
    layout.addWidget(introduction)
    split = QSplitter()
    layout.addWidget(split,1)
    # A lightweight rendering context shares the actual editor symbol and pipe renderer.
    from app import Symbol, Pipe
    class Preview:
        exporting = True
        symbols = {}
    renderer = Preview()
    renderer.document = draft
    renderer.symbols = {}
    scene = QGraphicsScene(dialog)
    for record in draft['components']:
        item = Symbol(record,renderer)
        item.setFlags(item.flags() & ~item.GraphicsItemFlag.ItemIsMovable & ~item.GraphicsItemFlag.ItemIsSelectable)
        renderer.symbols[record['id']] = item
        scene.addItem(item)
    for record in draft['connections']:
        item = Pipe(record,renderer)
        item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        scene.addItem(item)
    from annotations import Note
    for record in draft.get('notes',[]):
        scene.addItem(Note(record,renderer))
    view = QGraphicsView(scene)
    view.setInteractive(False)
    split.addWidget(view)
    details = QPlainTextEdit()
    details.setReadOnly(True)
    issue_lines = proposal.get('issues',[])
    details.setPlainText('\n'.join(operations.diff(window.document,draft))+'\n\nIMPORT NOTES\n'+'\n'.join(str(i) for i in issue_lines)+'\n\n'+generation_provenance.describe(generation))
    split.addWidget(details)
    split.setSizes([650,350])
    findings = proposal.get('review_findings', [])
    source_checks = None
    if findings:
        from source_review import SourceReview
        source_checks = SourceReview(window.document, findings, dialog)
        split.addWidget(source_checks)
        dialog.resize(1250,720)
        split.setSizes([500,300,450])
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel)
    apply_button = buttons.button(QDialogButtonBox.StandardButton.Apply)
    apply_button.clicked.connect(dialog.accept)
    if source_checks:
        apply_button.setEnabled(source_checks.complete())
        source_checks.reviewed.connect(apply_button.setEnabled)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    from PySide6.QtCore import QTimer
    QTimer.singleShot(0,lambda:view.fitInView(scene.itemsBoundingRect().adjusted(-30,-30,30,30),Qt.AspectRatioMode.KeepAspectRatio))
    if dialog.exec() == QDialog.DialogCode.Accepted:
        if source_checks and not source_checks.complete():
            return False
        # Recheck the fingerprint at the commit boundary, even after a modal review.
        accepted = operations.apply(window.document,proposal)
        accepted = review_history.append(accepted,window.document,proposal,generation=generation)
        window.checkpoint()
        window.document = accepted
        window.rebuild()
        window.fit()
        return True
    return False

def install(window):
    menu = window.menuBar().addMenu('Sketch / AI')
    def add(label, callback):
        action = QAction(label,window)
        action.triggered.connect(lambda checked=False:callback())
        menu.addAction(action)
        return action
    add('Attach reference sketch…',lambda:attach(window))
    add('Reference placement…',lambda:placement(window))
    toggle = add('Show reference sketch',lambda:None)
    toggle.setCheckable(True)
    toggle.setChecked(True)
    toggle.toggled.connect(lambda on:(setattr(window,'show_reference',on),window.view.viewport().update()))
    def remove():
        if 'reference' in window.document:
            window.checkpoint()
            window.document.pop('reference')
            window.rebuild()
    add('Remove reference sketch',remove)
    menu.addSeparator()
    def export_context():
        path,_ = QFileDialog.getSaveFileName(window,'Export authoring context','authoring-context.json','JSON (*.json)')
        if path:
            try:
                Path(path).write_text(json.dumps(operations.context(window.document),indent=2),encoding='utf-8')
            except OSError as error:
                QMessageBox.warning(window,'Cannot export',str(error))
    def import_proposal():
        path,_ = QFileDialog.getOpenFileName(window,'Review edit proposal','','JSON (*.json)')
        if path:
            try:
                proposal = json.loads(Path(path).read_text(encoding='utf-8'))
                review(window,proposal)
            except (ValueError,TypeError,KeyError,OSError) as error:
                QMessageBox.warning(window,'Cannot apply proposal',str(error))
    add('Export authoring context…',export_context)
    add('Review edit proposal…',import_proposal)
    add('Accepted proposal history…',lambda:review_history.show(window))
    refresh(window)
