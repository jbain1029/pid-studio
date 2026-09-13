"""Non-destructive recovery browser; opening never consumes a snapshot."""
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTreeWidget,
    QTreeWidgetItem, QPlainTextEdit, QDialogButtonBox, QPushButton, QMessageBox)
import pidcore as core


def entries(folder):
    results = []
    for path in Path(folder).glob('*.pid'):
        entry = {'path': path, 'modified': 0, 'document': None, 'error': ''}
        try:
            stat = path.stat()
            entry['modified'] = stat.st_mtime
            if stat.st_size > 32 * 1024 * 1024:
                raise ValueError('Snapshot exceeds the 32 MB recovery-browser limit.')
            entry['document'] = core.load(path)
        except (OSError, ValueError) as error:
            entry['error'] = str(error)
        results.append(entry)
    return sorted(results, key=lambda entry: entry['modified'], reverse=True)


def restore(window, path):
    # Read first: a missing or invalid snapshot must not prompt to discard work.
    try:
        document = core.load(path)
    except (OSError, ValueError) as error:
        QMessageBox.warning(window, 'Recovery failed', str(error))
        return False
    if not window.confirm_discard():
        return False
    window.document, window.path = document, None
    window.saved = {}  # Even an empty recovered drawing needs a new save location.
    window.recovered_snapshot = None
    window.history.clear()
    window.future.clear()
    window.rebuild()
    window.fit()
    window.statusBar().showMessage('Recovered as an unsaved drawing. Use Save to choose a file; the recovery snapshot is retained.')
    return True


class RecoveryDialog(QDialog):
    def __init__(self, window, folder):
        super().__init__(window)
        self.window, self.folder = window, Path(folder)
        self.setWindowTitle('Recover autosaved drawing')
        self.resize(780, 510)
        layout = QVBoxLayout(self)
        notice = QLabel('Select a snapshot to inspect it. Recover opens an unsaved copy; no snapshot is deleted.\nSnapshots from another running editor may still be updating.')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Drawing', 'Saved locally', 'Contents', 'Status'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 220)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 210)
        self.tree.currentItemChanged.connect(self.inspect)
        self.tree.itemDoubleClicked.connect(lambda *_: self.recover())
        layout.addWidget(self.tree, 1)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setMaximumHeight(140)
        layout.addWidget(self.details)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.open_button = buttons.addButton('Recover copy', QDialogButtonBox.ButtonRole.AcceptRole)
        self.open_button.clicked.connect(self.recover)
        refresh = buttons.addButton('Refresh', QDialogButtonBox.ButtonRole.ActionRole)
        refresh.clicked.connect(self.refresh)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh()

    def refresh(self):
        self.tree.clear()
        self.details.clear()
        self.open_button.setEnabled(False)
        for entry in entries(self.folder):
            document = entry['document']
            title = document['title'] if document is not None else entry['path'].name
            contents = f"{len(document['components'])} components, {len(document['connections'])} lines" if document is not None else 'Unavailable'
            date = datetime.fromtimestamp(entry['modified']).strftime('%Y-%m-%d %H:%M:%S') if entry['modified'] else 'Unavailable'
            item = QTreeWidgetItem(self.tree, [title, date, contents, 'Invalid' if entry['error'] else 'Ready'])
            item.setData(0, Qt.ItemDataRole.UserRole, entry)
            item.setToolTip(0, str(entry['path']))
        if self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))
        else:
            self.details.setPlainText('No autosaved drawings found. Recovery snapshots are created every 30 seconds while a drawing has unsaved changes.')

    def inspect(self, item, previous=None):
        if item is None:
            self.open_button.setEnabled(False)
            return
        entry = item.data(0, Qt.ItemDataRole.UserRole)
        self.open_button.setEnabled(not entry['error'])
        lines = [str(entry['path'])]
        if entry['error']:
            lines += ['Cannot recover this snapshot:', entry['error']]
        else:
            document = entry['document']
            lines += [f"Drawing: {document['title']}", f"Notes: {len(document.get('notes', []))}; reference sketch: {'yes' if 'reference' in document else 'no'}",
                      'Components: ' + ', '.join(record['tag'] for record in document['components'])]
        self.details.setPlainText('\n'.join(lines))

    def recover(self):
        item = self.tree.currentItem()
        if item is None or not self.open_button.isEnabled():
            return
        if restore(self.window, item.data(0, Qt.ItemDataRole.UserRole)['path']):
            self.accept()


def show(window, folder):
    RecoveryDialog(window, folder).exec()
