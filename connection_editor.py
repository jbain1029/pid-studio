"""Precise, staged connection editing without changing the document format."""
import copy
import math

from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout)

import pidcore as core
from connection_policy import require_supported_connection


def apply_connection(window, record, *, original=None, base_document=None):
    """Validate completely before checkpointing; retain existing line metadata."""
    if base_document is not None and window.document != base_document:
        raise ValueError('The drawing changed while this editor was open. Close and reopen the editor.')
    draft = copy.deepcopy(window.document)
    candidate = copy.deepcopy(record)
    if candidate['from'] == candidate['to']:
        raise ValueError('Choose two different ports for the connection.')
    for point in candidate['waypoints']:
        if len(point) != 2 or any(isinstance(value, bool) or not isinstance(value, (int, float))
                                  or not math.isfinite(value) for value in point):
            raise ValueError('Every waypoint needs two finite coordinates.')
    if original is not None:
        index = next((i for i, line in enumerate(draft['connections'])
                      if line['id'] == original['id']), None)
        if index is None or draft['connections'][index] != original:
            raise ValueError('This connection changed. Close and reopen the editor.')
        # Only editable fields may be changed; preserve identity and engineering data.
        replacement = copy.deepcopy(original)
        for field in ('from', 'to', 'kind', 'label', 'waypoints'):
            replacement[field] = candidate[field]
        draft['connections'][index] = replacement
        identifier = original['id']
    else:
        draft['connections'].append(candidate)
        identifier = candidate['id']
    errors = core.validate(draft)
    if errors:
        raise ValueError(errors[0])
    require_supported_connection(draft, candidate, original)
    if draft == window.document:
        return False
    window.checkpoint()
    window.document = draft
    window.rebuild()
    from editing import restore_selection
    restore_selection(window, {identifier})
    window.statusBar().showMessage('Connection applied. Undo restores the previous drawing.')
    return True


class ConnectionDialog(QDialog):
    def __init__(self, window, line_id=None):
        super().__init__(window)
        self.window = window
        self.base_document = copy.deepcopy(window.document)
        self.original = next((copy.deepcopy(line) for line in window.document['connections']
                              if line['id'] == line_id), None)
        if line_id is not None and self.original is None:
            raise ValueError('Connection no longer exists.')
        self.record = copy.deepcopy(self.original) if self.original else {
            'id': core.uid(), 'from': {}, 'to': {}, 'kind': 'process', 'label': '', 'waypoints': []}
        self.setWindowTitle('Edit connection' if self.original else 'Create connection')
        self.resize(640, 560)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.component_boxes = {}
        self.port_boxes = {}
        selected_ids = {item.record['id'] for item in window.scene.selectedItems()
                        if hasattr(item, 'record') and 'type' in item.record}
        components = list(window.document['components'])
        defaults = [c for c in components if c['id'] in selected_ids] or components
        for index, (end, title) in enumerate((('from', 'Source'), ('to', 'Destination'))):
            component_box, port_box = QComboBox(), QComboBox()
            self.component_boxes[end] = component_box
            self.port_boxes[end] = port_box
            for component in components:
                component_box.addItem(f"{component['tag']} — {core.definition(component, window.document)['label']}", component['id'])
            component_box.currentIndexChanged.connect(lambda unused, end=end: self.populate_ports(end))
            form.addRow(title + ' component', component_box)
            form.addRow(title + ' port', port_box)
            if components:
                default = self.record[end].get('component', defaults[min(index, len(defaults)-1)]['id'])
                component_box.setCurrentIndex(component_box.findData(default))
            self.populate_ports(end)
            preferred = self.record[end].get('port', 'outlet' if end == 'from' else 'inlet')
            if port_box.findData(preferred) >= 0:
                port_box.setCurrentIndex(port_box.findData(preferred))
        self.kind = QComboBox()
        self.kind.addItem('Process line', 'process')
        self.kind.addItem('Instrument / signal line', 'signal')
        self.kind.setCurrentIndex(self.kind.findData(self.record['kind']))
        self.label = QLineEdit(self.record['label'])
        form.addRow('Connection type', self.kind)
        form.addRow('Line label', self.label)
        layout.addWidget(QLabel('Routing waypoints — drawing coordinates; X increases right, Y increases down.\n'
                                'The route passes through these points in order. No points = automatic routing.'))
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['X', 'Y'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        for point in self.record['waypoints']:
            self.add_point(point)
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        for title, callback in [('Add', lambda: self.add_point()), ('Remove', self.remove_point),
                                ('Move up', lambda: self.move_point(-1)),
                                ('Move down', lambda: self.move_point(1)),
                                ('Reset automatic route', lambda: self.table.setRowCount(0)),
                                ('Reverse direction', self.reverse)]:
            button = QPushButton(title)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.status = QLabel('Changes are staged until Apply. Existing engineering properties are retained.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        footer = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        footer.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        footer.rejected.connect(self.reject)
        layout.addWidget(footer)

    def populate_ports(self, end):
        box = self.port_boxes[end]
        previous = box.currentData()
        box.clear()
        identifier = self.component_boxes[end].currentData()
        component = next((c for c in self.base_document['components'] if c['id'] == identifier), None)
        if component:
            definition = core.definition(component, self.base_document)
            for port in definition['ports']:
                meaning = definition.get('port_meanings', {}).get(port)
                role = 'illustrative attachment; no new connections' if meaning else definition['port_kinds'][port]
                box.addItem(f"{port} ({role})", port)
            if box.findData(previous) >= 0:
                box.setCurrentIndex(box.findData(previous))

    def add_point(self, point=None):
        point = [0, 0] if point is None else point
        row = self.table.rowCount()
        self.table.insertRow(row)
        for column, value in enumerate(point):
            self.table.setItem(row, column, QTableWidgetItem(str(value)))
        self.table.selectRow(row)

    def remove_point(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def move_point(self, offset):
        row = self.table.currentRow()
        destination = row + offset
        if row < 0 or not 0 <= destination < self.table.rowCount():
            return
        for column in range(2):
            first = self.table.takeItem(row, column)
            second = self.table.takeItem(destination, column)
            self.table.setItem(row, column, second)
            self.table.setItem(destination, column, first)
        self.table.selectRow(destination)

    def reverse(self):
        endpoints = {end: (self.component_boxes[end].currentData(), self.port_boxes[end].currentData())
                     for end in ('from', 'to')}
        for end, other in (('from', 'to'), ('to', 'from')):
            component, port = endpoints[other]
            self.component_boxes[end].setCurrentIndex(self.component_boxes[end].findData(component))
            self.port_boxes[end].setCurrentIndex(self.port_boxes[end].findData(port))
        rows = [[self.table.item(row, column).text() for column in range(2)]
                for row in range(self.table.rowCount())]
        self.table.setRowCount(0)
        for point in reversed(rows):
            self.add_point(point)

    def candidate(self):
        result = copy.deepcopy(self.record)
        for end in ('from', 'to'):
            result[end] = {'component': self.component_boxes[end].currentData(),
                           'port': self.port_boxes[end].currentData()}
            if not all(result[end].values()):
                raise ValueError('Choose a component and port for both ends.')
        result['kind'] = self.kind.currentData()
        result['label'] = self.label.text()
        try:
            result['waypoints'] = [[float(self.table.item(row, column).text()) for column in range(2)]
                                   for row in range(self.table.rowCount())]
        except (ValueError, AttributeError):
            raise ValueError('Every waypoint needs numeric X and Y coordinates.') from None
        return result

    def apply(self):
        try:
            apply_connection(self.window, self.candidate(), original=self.original, base_document=self.base_document)
        except ValueError as error:
            self.status.setText('Not applied: ' + str(error))
            return
        self.accept()


def edit_selected(window):
    selected = [item.record for item in window.scene.selectedItems()
                if hasattr(item, 'record') and 'waypoints' in item.record]
    if len(selected) != 1:
        window.statusBar().showMessage('Select one connection, then choose Edit selected connection.')
        return
    ConnectionDialog(window, selected[0]['id']).exec()


def install(window):
    menu = next(action.menu() for action in window.menuBar().actions() if action.text() == 'Edit')
    menu.addSeparator()
    menu.addAction('Create connection…').triggered.connect(lambda: ConnectionDialog(window).exec())
    menu.addAction('Edit selected connection…').triggered.connect(lambda: edit_selected(window))
