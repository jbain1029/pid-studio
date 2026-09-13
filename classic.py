"""Classic engineering workbench chrome and document navigation."""
from PySide6.QtCore import Qt, QSize, QMimeData
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QDrag, QLinearGradient
from PySide6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QDockWidget, QWidget,
    QVBoxLayout, QLabel, QTabWidget, QStyle, QToolBar, QStyledItemDelegate, QLineEdit)
import pidcore as core
import component_folders


def apply_theme(application):
    """Pin all native popup roles to light mode, independent of Windows theme."""
    from PySide6.QtGui import QPalette
    application.setStyle('Fusion')
    palette = QPalette()
    colors = {'Window':'#d4d0c8', 'WindowText':'#171717', 'Base':'#ffffff',
              'AlternateBase':'#f5f4ed', 'Text':'#171717', 'Button':'#e7e5df',
              'ButtonText':'#171717', 'ToolTipBase':'#fffde1', 'ToolTipText':'#171717',
              'Highlight':'#245b88', 'HighlightedText':'#ffffff',
              'Light':'#ffffff', 'Midlight':'#ece9e1', 'Mid':'#a0a0a0', 'Dark':'#707070',
              'PlaceholderText':'#686868', 'Link':'#174f86', 'LinkVisited':'#654878'}
    for name, color in colors.items():
        palette.setColor(getattr(QPalette.ColorRole,name), QColor(color))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor('#707070'))
    application.setPalette(palette)
    application.setStyleSheet(STYLE)

def symbol_icon(kind, catalog=None):
    image = QPixmap(20, 20)
    image.fill(Qt.GlobalColor.transparent)
    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    definition = (catalog or core.CATALOG).get(kind,{})
    if 'artwork' in definition:
        from symbol_library import draw_artwork
        p.translate(10,10)
        p.scale(.2,.2)
        p.setPen(QPen(QColor('#263238'),4))
        p.setBrush(Qt.GlobalColor.white)
        draw_artwork(p,definition)
        p.end()
        return QIcon(image)
    colors = {'tank': '#437dbe', 'pump': '#239f9c', 'instrument': '#d8ac27',
              'exchanger': '#ba6741', 'filter': '#628b41'}
    p.setPen(QPen(QColor('#344357'), 1))
    p.setBrush(QColor(colors.get(kind, '#718ca8')))
    if kind == 'tank':
        p.drawRect(4, 5, 12, 12)
        p.drawEllipse(4, 2, 12, 6)
    elif kind in ('pump', 'instrument', 'exchanger'):
        p.drawEllipse(2, 2, 16, 16)
        p.setPen(QPen(Qt.GlobalColor.white, 2))
        p.drawLine(6, 13, 14, 7)
        p.drawLine(6, 7, 14, 13)
    elif 'valve' in kind:
        p.drawLine(1, 10, 19, 10)
        p.drawLine(3, 4, 17, 16)
        p.drawLine(3, 16, 17, 4)
        p.drawLine(3, 4, 3, 16)
        p.drawLine(17, 4, 17, 16)
    elif kind == 'tee':
        p.setPen(QPen(QColor('#39845a'), 4))
        p.drawLine(2, 12, 18, 12)
        p.drawLine(10, 3, 10, 12)
    else:
        p.drawRect(3, 3, 14, 14)
        p.setPen(Qt.GlobalColor.white)
        p.drawLine(5, 14, 14, 5)
    p.end()
    return QIcon(image)

class CategoryDelegate(QStyledItemDelegate):
    """Raised category rows, like the collapsible trays in classic workbenches."""
    def paint(self, painter, option, index):
        if not index.parent().isValid():
            painter.save()
            gradient = QLinearGradient(option.rect.topLeft(), option.rect.bottomLeft())
            gradient.setColorAt(0, QColor('#ffffff'))
            gradient.setColorAt(1, QColor('#c7c6ca'))
            painter.fillRect(option.rect, gradient)
            painter.setPen(QColor('#ffffff'))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            painter.setPen(QColor('#89888d'))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
            painter.restore()
        super().paint(painter, option, index)


class Toolbox(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setIndentation(14)
        self.setDragEnabled(True)
        self.setItemDelegate(CategoryDelegate(self))
        self.catalog = None
        self.filter_text = ''
        self.set_catalog(core.CATALOG)

    def set_catalog(self, catalog):
        if self.catalog == catalog:
            return
        import copy
        self.catalog = copy.deepcopy(catalog)
        self.leaves = component_folders.populate(self,catalog,lambda kind:symbol_icon(kind,catalog))
        self.filter_symbols(self.filter_text)

    def filter_symbols(self, text):
        self.filter_text = text
        component_folders.filter_tree(self,self.catalog,text)

    def startDrag(self, actions):
        item = self.currentItem()
        kind = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if not kind:
            return
        mime = QMimeData()
        mime.setData('application/x-pid-symbol', kind.encode())
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(symbol_icon(kind,self.catalog).pixmap(24, 24))
        drag.exec(Qt.DropAction.CopyAction)

def install(window):
    window.setDockNestingEnabled(True)
    window.setCorner(Qt.Corner.BottomLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
    window.setCorner(Qt.Corner.BottomRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
    # The drawing gets a persistent active-pane strip and a conventional sheet tab.
    view = window.takeCentralWidget()
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    strip = QLabel('  Drawing Workspace')
    strip.setObjectName('activeStrip')
    strip.setFixedHeight(23)
    layout.addWidget(strip)
    tabs = QTabWidget()
    tabs.setDocumentMode(False)
    tabs.addTab(view, 'Sheet 1 : Piping & Instrumentation')
    layout.addWidget(tabs)
    window.setCentralWidget(panel)

    tree = QTreeWidget()
    tree.setHeaderLabels(['Drawing outline'])
    tree.setIndentation(15)
    window.outline = tree
    outline_dock = QDockWidget('Project Outline', window)
    outline_dock.setWidget(tree)
    window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, outline_dock)
    toolbox = next(d for d in window.findChildren(QDockWidget) if d.windowTitle().startswith('Toolbox'))
    library = toolbox.widget()
    library_panel = QWidget()
    library_layout = QVBoxLayout(library_panel)
    library_layout.setContentsMargins(2, 2, 2, 2)
    library_layout.setSpacing(2)
    search = QLineEdit()
    search.setPlaceholderText('Filter component library...')
    search.setClearButtonEnabled(True)
    search.setAccessibleName('Filter component library')
    search.textChanged.connect(library.filter_symbols)
    library_layout.addWidget(search)
    library_layout.addWidget(library)
    toolbox.setWidget(library_panel)
    window.splitDockWidget(toolbox, outline_dock, Qt.Orientation.Vertical)
    window.resizeDocks([toolbox, outline_dock], [390, 220], Qt.Orientation.Vertical)
    window.resizeDocks([toolbox], [235], Qt.Orientation.Horizontal)
    details = next(d for d in window.findChildren(QDockWidget) if d.windowTitle() == 'Details')
    details.setWindowTitle('Details of Selection')
    window.resizeDocks([details], [260], Qt.Orientation.Horizontal)
    window.properties.setAlternatingRowColors(True)
    window.properties.verticalHeader().setDefaultSectionSize(23)
    window.properties.verticalHeader().show()
    window.properties.verticalHeader().setMinimumWidth(25)
    window.properties.setColumnWidth(0, 105)

    def choose(item, column):
        object_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not object_id:
            return
        target = next((item for item in window.scene.items() if hasattr(item,'record') and item.record['id']==object_id),None)
        if target:
            window.scene.clearSelection()
            target.setSelected(True)
            window.view.ensureVisible(target)
    tree.itemClicked.connect(choose)

    toolbar = window.findChildren(QToolBar)[0]
    toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    icons = {'New': 'SP_FileIcon', 'Open…': 'SP_DirOpenIcon', 'Save': 'SP_DialogSaveButton',
             'Export SVG…': 'SP_DialogOpenButton', 'Undo': 'SP_ArrowBack', 'Redo': 'SP_ArrowForward',
             'Delete': 'SP_TrashIcon', 'Duplicate': 'SP_FileDialogNewFolder', 'Rotate 90°': 'SP_BrowserReload',
             'Fit drawing': 'SP_TitleBarMaxButton', 'Validate': 'SP_DialogApplyButton'}
    for action in toolbar.actions():
        if action.text() in icons:
            action.setIcon(window.style().standardIcon(getattr(QStyle.StandardPixmap, icons[action.text()])))
            shortcut = action.shortcut().toString()
            action.setToolTip(action.text() + (f' ({shortcut})' if shortcut else ''))
    toolbar.addSeparator()
    project_label = QLabel('  Project  |  P&ID Drafting  ')
    toolbar.addWidget(project_label)
    window.addToolBarBreak()
    taskbar = QToolBar('Drawing tools')
    taskbar.setMovable(False)
    taskbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    taskbar.setIconSize(QSize(16, 16))
    window.addToolBar(taskbar)
    for action in toolbar.actions():
        if action.text() in ('Open…', 'Save', 'Fit drawing', 'Validate', 'Export SVG…'):
            taskbar.addAction(action)
    taskbar.addSeparator()
    grid = taskbar.addAction('Grid')
    grid.setCheckable(True)
    grid.setChecked(True)
    grid.toggled.connect(lambda on: (setattr(window.view, 'show_grid', on), window.view.viewport().update(), refresh_status(window)))
    window.count_label = QLabel()
    window.statusBar().addPermanentWidget(window.count_label)
    rebuild_outline(window)

def rebuild_outline(window):
    if not hasattr(window, 'outline'):
        return
    tree = window.outline
    tree.clear()
    root = QTreeWidgetItem(tree, [window.document['title']])
    root.setIcon(0, window.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
    for label, records in [('Components', window.document['components']), ('Connections', window.document['connections']), ('Notes',window.document.get('notes',[]))]:
        group = QTreeWidgetItem(root, [f'{label} ({len(records)})'])
        for record in records:
            item = QTreeWidgetItem(group, [record.get('tag', record.get('text','').split('\n')[0][:60] or record.get('label') or record.get('kind', 'Line'))])
            item.setData(0, Qt.ItemDataRole.UserRole, record['id'])
            item.setIcon(0, symbol_icon(record.get('type', 'tee')))
        group.setExpanded(True)
    root.setExpanded(True)
    refresh_status(window)


def refresh_status(window):
    if not hasattr(window,'count_label'):
        return
    snap = str(getattr(window,'snap_spacing',10)) if getattr(window,'snap_enabled',True) else 'off'
    grid = 'on' if getattr(window.view,'show_grid',True) else 'off'
    window.count_label.setText(f"  {len(window.document['components'])} components  |  {len(window.document['connections'])} lines  |  {len(window.document.get('notes',[]))} notes  |  Selected: {len(window.scene.selectedItems())}  |  Snap: {snap}  |  Grid: {grid}  ")

STYLE = '''
QWidget { font-family: "Segoe UI"; font-size: 9pt; color: #171717; }
QMainWindow, QDialog { background: #d4d0c8; }
QMenuBar { background: #f0efed; border-bottom: 1px solid #999; }
QMenuBar::item:selected { background: #ceddec; }
QMenu { background: #f0efed; color: #171717; border: 1px solid #858585; padding: 2px; }
QMenu::item { background: transparent; color: #171717; padding: 5px 28px 5px 22px; }
QMenu::item:selected { background: #245b88; color: white; }
QMenu::item:disabled { color: #707070; }
QMenu::separator { background: #aaa; height: 1px; margin: 4px 6px; }
QComboBox QAbstractItemView { background: white; color: #171717; selection-background-color: #245b88; selection-color: white; border: 1px solid #858585; }
QComboBox QAbstractItemView::item { min-height: 20px; }
QToolBar { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #fafafa,stop:1 #e0dfdd); border-top: 1px solid white; border-bottom: 1px solid #929292; spacing: 2px; padding: 2px; }
QToolButton { padding: 3px 5px; border: 1px solid transparent; border-radius: 0; }
QToolButton:hover, QToolButton:checked { background: #dbe7f3; border: 1px solid #7995b0; }
QToolBar::separator { background: #aaa; width: 1px; margin: 3px; }
QDockWidget { border: 1px solid #969696; }
QDockWidget::title { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #b7b7b7,stop:1 #888888); color: white; padding: 4px; border-top: 1px solid #eee; }
QMainWindow::separator { background: #d4d0c8; width: 4px; height: 4px; }
QLabel#activeStrip { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #08086c,stop:1 #576ba4); color: white; border: 1px solid #737373; }
QTreeWidget, QListWidget, QTableWidget { background: white; alternate-background-color: #f5f4ed; border: 1px solid #8f8f8f; selection-background-color: #477faa; selection-color: white; }
QTreeView::item { min-height: 20px; }
QTreeView::item:selected { background: #477faa; color: white; }
QHeaderView::section { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f9f9f9,stop:1 #d4d2d0); border-right: 1px solid #aaa; border-bottom: 1px solid #999; padding: 4px; }
QTableWidget { gridline-color: #ccc; }
QTabWidget::pane { border: 1px solid #999; }
QTabBar::tab { background: #d4d0c8; border: 1px solid #999; padding: 4px 16px; margin-top: 2px; }
QTabBar::tab:selected { background: white; border-bottom-color: white; }
QStatusBar { background: #ece9e1; border-top: 1px solid #8d8d8d; }
QStatusBar::item { border: 1px solid #aaa; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit { background: white; border-top: 1px solid #787878; border-left: 1px solid #787878; border-right: 1px solid white; border-bottom: 1px solid white; border-radius: 0; padding: 3px; }
QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #fafafa,stop:1 #d4d0c8); border-top: 1px solid white; border-left: 1px solid white; border-right: 1px solid #777; border-bottom: 1px solid #777; padding: 4px 12px; border-radius: 0; }
QPushButton:pressed { background: #cac7c0; border-top-color: #777; border-left-color: #777; border-right-color: white; border-bottom-color: white; }
QPushButton:disabled { color: #888; }
QGroupBox { border: 1px solid #999; margin-top: 10px; padding-top: 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
QScrollBar:vertical { background: #e7e5df; width: 16px; }
QScrollBar:horizontal { background: #e7e5df; height: 16px; }
QScrollBar::handle { background: #c5c4c0; border: 1px solid #91918d; min-width: 18px; min-height: 18px; }
'''
