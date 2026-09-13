"""Local recovery, persistent layout and structured clipboard editing."""
import copy
import json
import os
from pathlib import Path
from PySide6.QtCore import QTimer, QSettings, QStandardPaths, QMimeData
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
import pidcore as core
import recovery

def install(window):
    settings = QSettings('PIDStudio', 'Workbench')
    window.workbench_settings = settings
    window.persist_layout = QApplication.platformName() != 'offscreen'
    geometry = settings.value('geometry') if window.persist_layout else None
    state = settings.value('state') if window.persist_layout else None
    if geometry:
        window.restoreGeometry(geometry)
    # Stable dock object names allow Qt to restore the arrangement.
    from PySide6.QtWidgets import QDockWidget, QToolBar
    for widget in window.findChildren(QDockWidget) + window.findChildren(QToolBar):
        widget.setObjectName(widget.windowTitle())
    if state:
        window.restoreState(state)
    folder = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)) / 'PIDStudio' / 'Recovery'
    folder.mkdir(parents=True, exist_ok=True)
    window.recovery_file = folder / f'session-{os.getpid()}.pid'
    window.recovered_snapshot = None

    def autosave():
        if window.document == window.saved or window.document == window.recovered_snapshot:
            return
        try:
            core.save(window.document, window.recovery_file)
            window.recovered_snapshot = copy.deepcopy(window.document)
        except (OSError, ValueError) as error:
            window.statusBar().showMessage(f'Recovery save failed: {error}')
    timer = QTimer(window)
    timer.timeout.connect(autosave)
    timer.start(30000)
    window.recovery_timer = timer

    def recover():
        recovery.show(window, folder)

    menus = {a.text(): a.menu() for a in window.menuBar().actions()}
    def action(menu, label, shortcut, function):
        item = QAction(label, window)
        if shortcut:
            item.setShortcut(shortcut)
        item.triggered.connect(lambda checked=False: function())
        menus[menu].addAction(item)
    menus['File'].addSeparator()
    window.recent_menu = menus['File'].addMenu('Recent drawings')
    update_recent(window)
    action('File', 'Recover autosaved drawing…', '', recover)
    menus['Edit'].addSeparator()
    action('Edit', 'Copy', 'Ctrl+C', lambda: copy_selection(window))
    action('Edit', 'Paste', 'Ctrl+V', lambda: paste_selection(window))
    action('Edit', 'Cut', 'Ctrl+X', lambda: (copy_selection(window), window.delete()))
    prior = [p for p in folder.glob('*.pid') if p != window.recovery_file]
    if prior:
        window.messages.addItem(f'{len(prior)} recovery file(s) available: File > Recover autosaved drawing.')

def copy_selection(window):
    selected = {i.record['id'] for i in window.scene.selectedItems() if hasattr(i, 'record')}
    draft = core.new_document()
    draft['components'] = [copy.deepcopy(c) for c in window.document['components'] if c['id'] in selected]
    used_types = {c['type'] for c in draft['components']}
    definitions = {kind: copy.deepcopy(definition)
                   for kind, definition in window.document.get('symbol_definitions', {}).items()
                   if kind in used_types}
    if definitions:
        draft['symbol_definitions'] = definitions
    draft['notes'] = [copy.deepcopy(c) for c in window.document.get('notes',[]) if c['id'] in selected]
    ids = {c['id'] for c in draft['components']}
    draft['connections'] = [copy.deepcopy(c) for c in window.document['connections'] if c['from']['component'] in ids and c['to']['component'] in ids]
    if not ids and not draft['notes']:
        return
    mime = QMimeData()
    mime.setData('application/x-pid-document', json.dumps(draft).encode('utf-8'))
    QApplication.clipboard().setMimeData(mime)

def merge_clipboard_definitions(result, draft):
    """Merge only imported symbols, preserving destination definitions on conflict."""
    mapping = {}
    used_types = {record['type'] for record in draft['components']}
    for kind in sorted(used_types & draft.get('symbol_definitions', {}).keys()):
        definition = draft['symbol_definitions'][kind]
        destination = result.setdefault('symbol_definitions', {})
        imported_kind = kind
        if kind in destination and destination[kind] != definition:
            slug = kind.removeprefix('custom:')
            index = 2
            while True:
                suffix = f'_{index}'
                imported_kind = 'custom:' + slug[:48-len(suffix)] + suffix
                # Reserve incoming keys too, so one remap cannot capture another
                # definition imported in the same clipboard operation.
                if imported_kind not in destination and imported_kind not in used_types:
                    break
                index += 1
        destination[imported_kind] = copy.deepcopy(definition)
        mapping[kind] = imported_kind
    return mapping


def paste_selection(window):
    mime = QApplication.clipboard().mimeData()
    if not mime or not mime.hasFormat('application/x-pid-document'):
        return
    try:
        draft = json.loads(bytes(mime.data('application/x-pid-document')))
        errors = core.validate(draft)
        if errors:
            raise ValueError('\n'.join(errors))
    except (ValueError, TypeError) as error:
        QMessageBox.warning(window, 'Invalid clipboard drawing', str(error))
        return
    if not draft['components'] and not draft.get('notes'):
        return
    result = copy.deepcopy(window.document)
    type_mapping = merge_clipboard_definitions(result, draft)
    mapping = {}
    center = window.view.mapToScene(window.view.viewport().rect().center())
    positioned = draft['components']+draft.get('notes',[])
    cx = sum(c['position'][0] for c in positioned)/len(positioned)
    cy = sum(c['position'][1] for c in positioned)/len(positioned)
    dx, dy = round((center.x()-cx)/10)*10, round((center.y()-cy)/10)*10
    for record in draft['components']:
        c = core.component(type_mapping.get(record['type'], record['type']), record['position'][0]+dx, record['position'][1]+dy, result)
        mapping[record['id']] = c['id']
        c['description'], c['rotation'] = record['description'], record['rotation']
        if 'metadata' in record:
            c['metadata'] = copy.deepcopy(record['metadata'])
        result['components'].append(c)
    for record in draft['connections']:
        record['id'] = core.uid()
        for end in ('from','to'):
            record[end]['component'] = mapping[record[end]['component']]
        record['waypoints'] = [[x+dx,y+dy] for x,y in record['waypoints']]
        result['connections'].append(record)
    new_note_ids = []
    for record in draft.get('notes',[]):
        record['id'] = core.uid()
        new_note_ids.append(record['id'])
        record['position'] = [record['position'][0]+dx,record['position'][1]+dy]
        result.setdefault('notes',[]).append(record)
    errors = core.validate(result)
    if errors:
        QMessageBox.warning(window, 'Invalid clipboard drawing', '\n'.join(errors))
        return
    window.checkpoint()
    window.document = result
    window.rebuild()
    for new_id in mapping.values():
        window.symbols[new_id].setSelected(True)
    for item in window.scene.items():
        if hasattr(item,'record') and item.record['id'] in new_note_ids:
            item.setSelected(True)

def update_recent(window,path=None):
    if not hasattr(window,'recent_menu'):
        return
    paths = window.workbench_settings.value('recent_files',[]) if window.persist_layout else getattr(window,'session_recent',[])
    if not isinstance(paths,list):
        paths = []
    if path:
        path = str(Path(path).resolve())
        paths = [path]+[p for p in paths if p!=path]
    paths = paths[:10]
    window.session_recent = paths
    if window.persist_layout:
        window.workbench_settings.setValue('recent_files',paths)
    window.recent_menu.clear()
    for filename in paths:
        action = window.recent_menu.addAction(filename)
        action.triggered.connect(lambda checked=False,p=filename:open_recent(window,p))
    window.recent_menu.setEnabled(bool(paths))

def open_recent(window,path):
    return window.open_path(path)

def close(window):
    if window.persist_layout:
        window.workbench_settings.setValue('geometry', window.saveGeometry())
        window.workbench_settings.setValue('state', window.saveState())
    window.recovery_timer.stop()
    # Only this process's recovery snapshot is removed after an explicit clean close.
    try:
        window.recovery_file.unlink(missing_ok=True)
    except OSError:
        pass
