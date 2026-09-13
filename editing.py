"""Canvas-local editing commands; property editors keep their normal keys."""
from PySide6.QtCore import Qt
import copy
from PySide6.QtWidgets import QMenu, QApplication
import workspace
import deliverables
import pidcore as core
import connection_editor


def begin_reconnect(window, line_id, end):
    if end not in ('from','to'):
        return False
    line = next((line for line in window.document['connections'] if line['id']==line_id),None)
    if line is None:
        return False
    window.pending = None
    window.reconnecting = (line_id,end)
    window.scene.clearSelection()
    restore_selection(window,{line_id})
    window.view.setFocus()
    window.statusBar().showMessage(f"Reconnect {'source' if end=='from' else 'destination'} of {line['label'] or line_id}: click a replacement port. Escape cancels; line properties are retained.")
    return True


def finish_reconnect(window, endpoint):
    line_id, end = window.reconnecting
    line = next((line for line in window.document['connections'] if line['id']==line_id),None)
    if line is None:
        window.cancel()
        return False
    if line[end] == endpoint:
        window.cancel()
        return False
    other = 'to' if end=='from' else 'from'
    if line[other] == endpoint:
        window.statusBar().showMessage('Both ends cannot use the same port. Choose another port or press Escape.')
        return False
    draft = copy.deepcopy(window.document)
    changed = next(line for line in draft['connections'] if line['id']==line_id)
    changed[end] = copy.deepcopy(endpoint)
    from connection_policy import require_supported_connection
    try:
        require_supported_connection(draft, changed, line)
    except ValueError as error:
        window.statusBar().showMessage('Cannot reconnect: ' + str(error))
        return False
    errors = core.validate(draft)
    if errors:
        window.statusBar().showMessage('Cannot reconnect: '+errors[0]+'. Choose another port or press Escape.')
        return False
    window.checkpoint()
    window.document = draft
    window.rebuild()
    restore_selection(window,{line_id})
    window.statusBar().showMessage('Pipe reconnected. Line label, type, properties and waypoints retained; Undo restores the previous endpoint.')
    return True


def restore_selection(window, identifiers):
    for item in window.scene.items():
        if hasattr(item, 'record') and item.record['id'] in identifiers:
            item.setSelected(True)


def nudge(window, dx, dy):
    selected = {i.record['id'] for i in window.scene.selectedItems() if hasattr(i, 'record')}
    records = [r for r in window.document['components'] + window.document.get('notes', [])
               if r['id'] in selected]
    if not records:
        return False
    window.checkpoint()
    moved = {r['id'] for r in records}
    for record in records:
        record['position'] = [record['position'][0] + dx, record['position'][1] + dy]
    for line in window.document['connections']:
        if line['from']['component'] in moved and line['to']['component'] in moved:
            line['waypoints'] = [[x + dx, y + dy] for x, y in line['waypoints']]
    window.rebuild()
    restore_selection(window, selected)
    return True


def select_all(window):
    for item in window.scene.items():
        if hasattr(item, 'record'):
            item.setSelected(True)


def context_menu(window, target=None):
    if target is not None and not target.isSelected():
        window.scene.clearSelection()
        target.setSelected(True)
    menu = QMenu(window)
    selected = window.scene.selectedItems()
    positioned = any(hasattr(i, 'record') and 'position' in i.record for i in selected)
    components = any(hasattr(i, 'record') and 'type' in i.record for i in selected)
    def command(label, callback, enabled=True):
        action = menu.addAction(label)
        action.setEnabled(enabled)
        action.triggered.connect(lambda checked=False: callback())
        return action
    command('Copy', lambda: workspace.copy_selection(window), positioned)
    command('Paste', lambda: workspace.paste_selection(window),
            bool(QApplication.clipboard().mimeData() and QApplication.clipboard().mimeData().hasFormat('application/x-pid-document')))
    command('Duplicate', window.duplicate, positioned)
    command('Delete', window.delete, bool(selected))
    menu.addSeparator()
    command('Rotate 90°', window.rotate, components)
    command('Engineering properties…', lambda: deliverables.edit_metadata(window),
            len(selected) == 1 and 'text' not in selected[0].record)
    command('Create connection…', lambda: connection_editor.ConnectionDialog(window).exec(),
            bool(window.document['components']))
    if target is not None and 'waypoints' in target.record:
        command('Edit connection…', lambda: connection_editor.ConnectionDialog(window, target.record['id']).exec())
        for label, end in [('Reconnect source…','from'),('Reconnect destination…','to')]:
            command(label, lambda end=end:begin_reconnect(window,target.record['id'],end))
        def reset():
            window.checkpoint()
            target.record['waypoints'] = []
            target.update_route()
            window.changed()
        command('Reset to automatic routing', reset, bool(target.record['waypoints']))
    menu.addSeparator()
    command('Select all', lambda: select_all(window))
    command('Fit drawing', window.fit)
    return menu
