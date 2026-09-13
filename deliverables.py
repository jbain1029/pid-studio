"""Drawing settings, engineering metadata and portable deliverables."""
import csv
import pidcore as core
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QSizeF, QMarginsF, QByteArray, QBuffer, QIODevice, QSize, QLineF
from PySide6.QtGui import QAction, QPainter, QPen, QColor, QFont, QFontMetricsF, QImage, QPdfWriter, QPageSize, QPageLayout
from PySide6.QtSvg import QSvgGenerator, QSvgRenderer
from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPlainTextEdit, QDialogButtonBox,
    QFileDialog, QMessageBox, QComboBox, QScrollArea, QWidget, QVBoxLayout, QLabel)

PAGES = {'A4':(297,210,QPageSize.PageSizeId.A4),'A3':(420,297,QPageSize.PageSizeId.A3),
         'ANSI B':(431.8,279.4,QPageSize.PageSizeId.Tabloid),'ANSI D':(863.6,558.8,QPageSize.PageSizeId.AnsiD)}

def page_spec(document):
    return PAGES.get(document.get('metadata',{}).get('paper_size','A3'),PAGES['A3'])

FIELDS = {
    'document': [('drawing_number','Drawing number'), ('revision_label','Revision'), ('owner','Owner / organization'), ('project','Project'), ('drawn_by','Prepared by'), ('checked_by','Checked by'), ('approved_by','Approved by'), ('document_status','Document status'), ('date','Issue date'), ('sheet_number','Sheet number in drawing set'), ('sheet_total','Total sheets in drawing set'), ('drawing_basis','Project drafting specification'), ('notes','General notes')],
    'component': [('service','Service'), ('manufacturer','Manufacturer'), ('model','Model'), ('size','Size / capacity'), ('material','Material'), ('normal_position','Normal position'), ('fail_position','Fail position')],
    'connection': [('size','Nominal size'), ('service','Service'), ('material','Material'), ('specification','Specification'), ('insulation','Insulation'), ('design_pressure','Design pressure'), ('design_temperature','Design temperature')],
}

def edit_metadata(window, drawing=False):
    selected = window.scene.selectedItems()
    if drawing:
        target, kind = window.document, 'document'
    elif len(selected)==1 and hasattr(selected[0], 'record'):
        target = selected[0].record
        if 'text' in target:
            QMessageBox.information(window,'Drawing note','Edit note text and width in Details, or double-click the note.')
            return
        kind = 'component' if 'type' in target else 'connection'
    else:
        QMessageBox.information(window, 'Engineering properties', 'Select one component or line first.')
        return
    dialog = QDialog(window)
    dialog.setWindowTitle('Drawing settings' if drawing else f"Engineering properties — {target.get('tag', target.get('label') or 'Line')}")
    dialog.setMinimumWidth(460)
    outer = QVBoxLayout(dialog)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content = QWidget()
    form = QFormLayout(content)
    scroll.setWidget(content)
    outer.addWidget(scroll)
    dialog.resize(620, 700 if drawing else 500)
    editors = {}
    if drawing:
        title = QLineEdit(target['title'])
        form.addRow('Drawing title', title)
        paper = QComboBox()
        paper.addItems(list(PAGES))
        paper.setCurrentText(target.get('metadata',{}).get('paper_size','A3'))
        form.addRow('Paper size (landscape)',paper)
        guidance = QLabel('Schematic: NOT TO SCALE. Sheet numbering identifies this drawing within a set; exports remain one page. Blank status prints DRAFT - NOT FOR CONSTRUCTION. See SHEET_STANDARDS.md for conventions and limits.')
        guidance.setWordWrap(True)
        form.addRow(guidance)
    for key, label in FIELDS[kind]:
        editor = QPlainTextEdit() if key == 'notes' else QLineEdit()
        value = target.get('metadata', {}).get(key, '')
        if key == 'notes':
            editor.setPlainText(value)
            editor.setMaximumHeight(120)
        else:
            editor.setText(value)
        form.addRow(label, editor)
        editors[key] = editor
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    outer.addWidget(buttons)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        if drawing:
            try:
                sheet_identity({key: editor.text() for key, editor in editors.items() if key != 'notes'})
            except ValueError as error:
                QMessageBox.warning(window, 'Invalid sheet numbering', str(error))
                return
        window.checkpoint()
        target['metadata'] = dict(target.get('metadata', {}), **{key: editor.toPlainText() if key=='notes' else editor.text() for key,editor in editors.items()})
        if drawing:
            target['title'] = title.text()
            target['metadata']['paper_size'] = paper.currentText()
        window.rebuild()

def sheet_font(pixels, bold=False):
    font = QFont('Segoe UI')
    font.setPixelSize(pixels)
    font.setBold(bold)
    return font


TEXT_FLAGS = Qt.TextFlag.TextWordWrap | Qt.TextFlag.TextWrapAnywhere


def text_height(text, font, width):
    return QFontMetricsF(font).boundingRect(QRectF(0, 0, width, 1000000), TEXT_FLAGS, text).height() + 3


def sheet_identity(metadata):
    """Set membership only; never imply that this renderer generates more pages."""
    values = []
    for key in ('sheet_number', 'sheet_total'):
        raw = metadata.get(key, '').strip() or '1'
        if not raw.isascii() or not raw.isdigit() or len(raw) > 4 or not 1 <= int(raw) <= 9999:
            raise ValueError('Sheet number and total sheets must be whole numbers from 1 to 9999.')
        values.append(int(raw))
    if values[0] > values[1]:
        raise ValueError('Sheet number cannot exceed total sheets in the drawing set.')
    return f'Sheet: {values[0]} of {values[1]}'


def sheet_layout(document, logical_height):
    """Original engineering template, not a certified ISO/ISA implementation.

    Frame margins are physical (20 mm binding edge, 10 mm other edges).
    Every variable field is measured and overflow is refused before export.
    """
    metadata = document.get('metadata', {})
    unit = 1400 / page_spec(document)[0]
    frame = QRectF(20 * unit, 10 * unit, 1400 - 30 * unit, logical_height - 20 * unit)
    left, right = frame.left(), frame.right()
    split = left + frame.width() * .32
    block_width = right - split
    font = sheet_font(13)
    rows = [
        [(1, 'PIPING & INSTRUMENTATION DIAGRAM\n' + document['title'], sheet_font(17, True))],
        [(.5, 'Owner / organization: ' + metadata.get('owner', ''), font),
         (.5, 'Project: ' + metadata.get('project', ''), font)],
        [(.65, 'Drawing: ' + metadata.get('drawing_number', ''), sheet_font(15, True)),
         (.35, 'Rev: ' + metadata.get('revision_label', ''), font)],
        [(1/3, 'Prepared: ' + metadata.get('drawn_by', ''), font),
         (1/3, 'Checked: ' + metadata.get('checked_by', ''), font),
         (1/3, 'Approved: ' + metadata.get('approved_by', ''), font)],
        [(.65, 'Status: ' + (metadata.get('document_status', '').strip() or 'DRAFT - NOT FOR CONSTRUCTION'), font),
         (.35, 'Date: ' + metadata.get('date', ''), font)],
        [(.35, sheet_identity(metadata), font), (.4, 'Scale: NOT TO SCALE', font),
         (.25, 'Size: ' + metadata.get('paper_size', 'A3'), font)],
    ]
    if metadata.get('drawing_basis'):
        rows.append([(1, 'Project drafting specification: ' + metadata['drawing_basis'], font)])
    heights = [max(text_height(text, cell_font, block_width * fraction - 16) + 12
                   for fraction, text, cell_font in row) for row in rows]
    footer_height = max(sum(heights), 205)
    footer_top = frame.bottom() - footer_height
    cells, rules = [], []
    y = footer_top
    for row, row_height in zip(rows, heights):
        x = split
        for fraction, text, cell_font in row:
            width = block_width * fraction
            cells.append((QRectF(x + 8, y + 6, width - 16, row_height - 12), text, cell_font))
            if x > split:
                rules.append((x, y, x, y + row_height))
            x += width
        y += row_height
        rules.append((split, y, right, y))
    legend_width = split - left - 20
    cells.append((QRectF(left + 10, footer_top + 8, legend_width, 20), 'LINE LEGEND / DRAWING CONVENTIONS', sheet_font(13, True)))
    legend = [(False, 'Process / fluid connection'), (True, 'Generic instrument / control signal')]
    for index, (_, label) in enumerate(legend):
        cells.append((QRectF(left + 85, footer_top + 37 + index * 30, legend_width - 75, 24), label, sheet_font(12)))
    conventions = ('Signal medium is unspecified.\nCrossing lines are not connected.\nUse a junction component for a branch.\nComponent tags identify equipment / instruments.\nVerify project-specific conventions before issue.')
    convention_height = text_height(conventions, sheet_font(12), legend_width)
    cells.append((QRectF(left + 10, footer_top + 101, legend_width, convention_height), conventions, sheet_font(12)))
    notes = 'GENERAL NOTES\n' + metadata['notes'] if metadata.get('notes') else ''
    notes_height = text_height(notes, font, frame.width() - 20) + 20 if notes else 0
    notes_top = footer_top - notes_height
    drawing = QRectF(left + 20, frame.top() + 20, frame.width() - 40, notes_top - frame.top() - 40)
    if drawing.height() < 180:
        raise ValueError('Drawing title or general notes exceed the available sheet space. '
                         'Shorten the sheet metadata or move notes into the drawing before exporting.')
    if notes:
        cells.append((QRectF(left + 10, notes_top + 10, frame.width() - 20, notes_height - 20), notes, font))
    rules.extend([(left, notes_top, right, notes_top), (left, footer_top, right, footer_top),
                  (split, footer_top, split, frame.bottom())])
    return {'drawing': drawing, 'footer_top': footer_top, 'notes_top': notes_top,
            'frame': frame, 'rules': rules, 'legend': legend, 'cells': cells}


def render_scene_vector(window, painter, target, bounds):
    # Normalize scene point-font layout at 96 DPI before painting onto printers
    # or PDF devices. Replaying SVG retains vector paths and searchable text,
    # unlike rasterizing the scene; destination DPI cannot enlarge its fonts.
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    generator = QSvgGenerator()
    generator.setOutputDevice(buffer)
    generator.setResolution(96)
    generator.setSize(QSize(max(1, round(bounds.width())), max(1, round(bounds.height()))))
    generator.setViewBox(bounds)
    recording = QPainter(generator)
    try:
        window.scene.render(recording, bounds, bounds, Qt.AspectRatioMode.KeepAspectRatio)
    finally:
        recording.end()
        buffer.close()
    renderer = QSvgRenderer(data)
    if not renderer.isValid():
        raise ValueError('Could not render the drawing as a vector sheet.')
    renderer.render(painter, target)


def render_sheet(window, painter, width, height):
    """Shared preview/PNG/PDF renderer with measured, DPI-independent text."""
    logical_height = 1400*height/width
    layout = sheet_layout(window.document, logical_height)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.fillRect(QRectF(0,0,width,height), Qt.GlobalColor.white)
    painter.save()
    painter.scale(width/1400, width/1400)
    painter.setPen(QPen(QColor('#202020'), 1))
    painter.drawRect(layout['frame'])
    drawing_area = layout['drawing']
    bounds = window.scene.itemsBoundingRect().adjusted(-30,-30,30,30)
    if window.symbols or window.document.get('notes'):
        scale = min(drawing_area.width()/bounds.width(), drawing_area.height()/bounds.height())
        target = QRectF(0,0,bounds.width()*scale,bounds.height()*scale)
        target.moveCenter(drawing_area.center())
        render_scene_vector(window, painter, target, bounds)
    for x1, y1, x2, y2 in layout['rules']:
        painter.drawLine(QLineF(x1, y1, x2, y2))
    for index, (dashed, _) in enumerate(layout['legend']):
        painter.setPen(QPen(QColor('#202020'), 2, Qt.PenStyle.DashLine if dashed else Qt.PenStyle.SolidLine))
        x, y = layout['frame'].left() + 10, layout['footer_top'] + 48 + index * 30
        painter.drawLine(QLineF(x, y, x + 60, y))
    painter.setPen(QPen(QColor('#202020'), 1))
    for rectangle, text, font in layout['cells']:
        painter.setFont(font)
        painter.drawText(rectangle, TEXT_FLAGS, text)
    painter.restore()

def export_sheet(window, path):
    path = Path(path)
    page_width, page_height, _ = page_spec(window.document)
    # Validate before opening the destination (especially an existing PDF).
    sheet_layout(window.document, 1400 * page_height / page_width)
    selected = list(window.scene.selectedItems())
    window.scene.clearSelection()
    window.exporting = True
    window.update_lines()
    painter = None
    try:
        if path.suffix.lower() == '.pdf':
            device = QPdfWriter(str(path))
            device.setPageSize(QPageSize(page_spec(window.document)[2]))
            device.setPageOrientation(QPageLayout.Orientation.Landscape)
            device.setPageMargins(QMarginsF(0,0,0,0))
            device.setResolution(150)
            device.setTitle(window.document['title'])
            painter = QPainter(device)
            render_sheet(window, painter, device.width(), device.height())
        else:
            w,h,_ = page_spec(window.document)
            device = QImage(2800,round(2800*h/w),QImage.Format.Format_ARGB32)
            painter = QPainter(device)
            render_sheet(window, painter, device.width(), device.height())
        if not painter.isActive():
            raise OSError('Could not create export file')
        painter.end()
        painter = None
        if path.suffix.lower() != '.pdf' and not device.save(str(path), 'PNG'):
            raise OSError('Could not save PNG file')
    finally:
        if painter and painter.isActive():
            painter.end()
        window.exporting = False
        for item in selected:
            item.setSelected(True)
        window.scene.update()

def export_register(window, path, category):
    columns = ['tag','type','description'] if category != 'lines' else ['label','from','to','kind']
    kind = 'component' if category != 'lines' else 'connection'
    columns += [key for key,label in FIELDS[kind]]
    nodes = {c['id']: c['tag'] for c in window.document['components']}
    records = window.document['connections'] if category == 'lines' else window.document['components']
    def safe(value):
        text = str(value)
        return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text
    with open(path,'w',newline='',encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream,fieldnames=columns)
        writer.writeheader()
        for record in records:
            symbol_category = core.definition(record,window.document)['category'] if category != 'lines' else None
            if category == 'instruments' and not symbol_category.startswith('Instrumentation'):
                continue
            if category == 'valves' and not symbol_category.startswith('Valves'):
                continue
            values = dict(record, **record.get('metadata', {}))
            if category == 'lines':
                for end in ('from','to'):
                    ref = record[end]
                    values[end] = f"{nodes[ref['component']]}.{ref['port']}"
            writer.writerow({key:safe(values.get(key,'')) for key in columns})

def install(window):
    menus = {a.text():a.menu() for a in window.menuBar().actions()}
    def add(menu, title, callback):
        item = QAction(title,window)
        item.triggered.connect(lambda checked=False: callback())
        menu.addAction(item)
    menus['Edit'].addSeparator()
    add(menus['Edit'], 'Engineering properties…', lambda: edit_metadata(window))
    add(menus['File'], 'Drawing settings…', lambda: edit_metadata(window,True))
    def export(extension):
        path,_ = QFileDialog.getSaveFileName(window, f'Export {extension.upper()} sheet', 'drawing.'+extension, f'{extension.upper()} (*.{extension})')
        if not path:
            return
        try:
            export_sheet(window,path)
        except (ValueError,OSError) as error:
            QMessageBox.warning(window,'Export failed',str(error))
    add(menus['File'],'Export PDF sheet…',lambda: export('pdf'))
    add(menus['File'],'Export PNG sheet…',lambda: export('png'))
    def print_sheet():
        from PySide6.QtPrintSupport import QPrinter,QPrintDialog
        try:
            page_width, page_height, _ = page_spec(window.document)
            sheet_layout(window.document, 1400 * page_height / page_width)
        except ValueError as error:
            QMessageBox.warning(window, 'Print failed', str(error))
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(page_spec(window.document)[2]))
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        dialog = QPrintDialog(printer,window)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = list(window.scene.selectedItems())
        window.scene.clearSelection()
        window.exporting = True
        painter = QPainter(printer)
        try:
            if not painter.isActive():
                raise OSError('Printer could not start this job')
            rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            render_sheet(window,painter,rect.width(),rect.height())
        except (OSError, ValueError) as error:
            QMessageBox.warning(window,'Print failed',str(error))
        finally:
            painter.end()
            window.exporting = False
            for item in selected:
                item.setSelected(True)
    add(menus['File'],'Print…',print_sheet)
    reports = window.menuBar().addMenu('Reports')
    import component_legend
    add(reports, 'Component legend (SVG)…', lambda: component_legend.choose_export(window))
    def register(category):
        path,_ = QFileDialog.getSaveFileName(window,'Export register',category+'.csv','CSV (*.csv)')
        if path:
            try:
                export_register(window,path,category)
            except OSError as error:
                QMessageBox.warning(window,'Export failed',str(error))
    for category in ('equipment','valves','instruments','lines'):
        add(reports,('Component' if category == 'equipment' else category.title())+' register…',lambda c=category: register(c))
