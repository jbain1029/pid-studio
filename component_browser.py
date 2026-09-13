"""Searchable, read-only catalog preview with one-click component insertion."""
import copy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLineEdit,QTreeWidget,
    QGraphicsScene,QGraphicsView,QLabel,QPushButton,QDialogButtonBox)
import pidcore as core
import classic
import component_folders


class ComponentPreview(QGraphicsView):
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self.scene() and not self.scene().sceneRect().isEmpty():
            self.fitInView(self.scene().sceneRect(),Qt.KeepAspectRatio)


class CatalogDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.catalog = copy.deepcopy(core.catalog_for(window.document))
        self.setWindowTitle('Component catalog')
        self.resize(860,580)
        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search component, category or tag prefix (e.g. flow, gate valve, PT)...')
        layout.addWidget(self.search)
        row = QHBoxLayout()
        layout.addLayout(row,1)
        self.list = QTreeWidget()
        self.list.setHeaderHidden(True)
        self.list.setIndentation(16)
        self.list.setMinimumWidth(320)
        row.addWidget(self.list,1)
        right = QVBoxLayout()
        row.addLayout(right,1)
        self.scene = QGraphicsScene(self)
        self.view = ComponentPreview(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setBackgroundBrush(Qt.white)
        self.view.setInteractive(False)
        right.addWidget(self.view,1)
        self.details = QLabel()
        self.details.setWordWrap(True)
        right.addWidget(self.details)
        self.count = QLabel()
        layout.addWidget(self.count)
        note = QLabel('Original schematic artwork. Select the applicable component and verify project conventions; no sizing or standards certification is implied.')
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.insert = buttons.addButton('Insert component',QDialogButtonBox.ActionRole)
        self.insert.clicked.connect(self.insert_component)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.leaves = component_folders.populate(self.list,self.catalog,lambda kind:classic.symbol_icon(kind,self.catalog))
        self.search.textChanged.connect(self.filter)
        self.list.currentItemChanged.connect(lambda current,previous:self.preview())
        self.list.itemDoubleClicked.connect(lambda item,column:self.insert_component())
        self.filter('')

    def filter(self,text):
        matches = component_folders.filter_tree(self.list,self.catalog,text)
        self.count.setText(f'{len(matches)} of {len(self.catalog)} component types')
        current = self.list.currentItem()
        if not text.strip():
            self.list.setCurrentItem(None)
        elif current not in matches:
            self.list.setCurrentItem(matches[0] if matches else None)
        self.preview()

    def preview(self):
        self.scene.clear()
        item = self.list.currentItem()
        kind = item.data(0,Qt.UserRole) if item else None
        self.insert.setEnabled(bool(kind and not item.isHidden()))
        if not kind or item.isHidden():
            self.details.setText('Open a folder and select a component.' if not self.search.text().strip() or item else 'No matching components.')
            return
        definition = self.catalog[kind]
        from app import Symbol
        class Context:
            exporting = False
        self.context = Context()
        self.context.document = copy.deepcopy(self.window.document)
        record = core.component(kind,0,0,self.context.document)
        self.scene.addItem(Symbol(record,self.context))
        self.scene.setSceneRect(-80,-75,160,165)
        self.view.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
        ports = ', '.join(f'{name}: {definition["port_kinds"][name]}' for name in definition['ports'])
        self.details.setText(f"{definition['label']}\nCategory: {definition['category']}\nTag prefix: {definition['prefix']}\nPorts: {ports}")

    def insert_component(self):
        item = self.list.currentItem()
        if item is None or item.isHidden() or not item.data(0,Qt.UserRole):
            return
        center = self.window.view.mapToScene(self.window.view.viewport().rect().center())
        self.window.add_symbol(item.data(0,Qt.UserRole),center)
        self.accept()


def install(window):
    menu = next(action.menu() for action in window.menuBar().actions() if action.text()=='View')
    menu.addAction('Component catalog…').triggered.connect(lambda:CatalogDialog(window).exec())
    button = QPushButton('Browse components…',window.palette.parentWidget())
    button.clicked.connect(lambda:CatalogDialog(window).exec())
    window.palette.parentWidget().layout().insertWidget(1,button)
