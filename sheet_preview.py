"""Read-only in-workspace preview using the exact exported sheet renderer."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsView, QGraphicsScene, QTabWidget, QGraphicsPixmapItem
import deliverables


def render_image(window):
    width, height, _ = deliverables.page_spec(window.document)
    image = QImage(2800, round(2800 * height / width), QImage.Format.Format_ARGB32)
    selected = list(window.scene.selectedItems())
    exporting = window.exporting
    painter = None
    try:
        window.scene.clearSelection()
        window.exporting = True
        window.update_lines()
        painter = QPainter(image)
        deliverables.render_sheet(window, painter, image.width(), image.height())
    finally:
        if painter is not None:
            painter.end()
        window.exporting = exporting
        for item in selected:
            item.setSelected(True)
        window.scene.update()
    return image


class SheetImage(QGraphicsPixmapItem):
    """Area-downsample before painting so thin borders survive Fit page zoom."""
    def __init__(self, image):
        super().__init__(QPixmap.fromImage(image))
        self.image = image
        self.scaled = image
        self.cached_width = image.width()

    def paint(self, painter, option, widget=None):
        scale = abs(painter.deviceTransform().m11())
        width = max(1, min(self.image.width(), round(self.image.width() * scale)))
        if width != self.cached_width:
            self.scaled = self.image.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
            self.cached_width = width
        painter.drawImage(self.boundingRect(), self.scaled)


class SheetView(QGraphicsView):
    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        if .08 < self.transform().m11() * factor < 4:
            self.scale(factor, factor)
        event.accept()


class SheetPreview(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.rendering = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        controls = QHBoxLayout()
        self.caption = QLabel('Sheet preview — read only')
        self.caption.setWordWrap(True)
        controls.addWidget(self.caption, 1)
        for text, callback in [('Drawing settings…', self.settings), ('Fit page', self.fit)]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            controls.addWidget(button)
        layout.addLayout(controls)
        self.scene = QGraphicsScene(self)
        self.view = SheetView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setBackgroundBrush(Qt.GlobalColor.gray)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        layout.addWidget(self.view)

    def refresh(self):
        if self.rendering:
            return
        self.rendering = True
        try:
            image = render_image(self.window)
            self.scene.clear()
            self.scene.addItem(SheetImage(image))
            self.scene.setSceneRect(0, 0, image.width(), image.height())
            paper = self.window.document.get('metadata', {}).get('paper_size', 'A3')
            identity = deliverables.sheet_identity(self.window.document.get('metadata',{}))
            self.caption.setText(f'{paper} landscape — {identity} (drawing set) — read only')
            self.fit()
        except ValueError as error:
            # Never leave an old successful sheet visible for invalid new data.
            self.scene.clear()
            self.scene.setSceneRect(0, 0, 1, 1)
            self.caption.setText('Cannot preview sheet: ' + str(error))
        finally:
            self.rendering = False

    def fit(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def settings(self):
        deliverables.edit_metadata(self.window, True)
        self.refresh()


def install(window):
    tabs = window.centralWidget().findChild(QTabWidget)
    window.sheet_preview = SheetPreview(window)
    index = tabs.addTab(window.sheet_preview, 'Sheet preview')
    tabs.currentChanged.connect(lambda current: window.sheet_preview.refresh() if current == index else None)
    view_menu = next(a.menu() for a in window.menuBar().actions() if a.text() == 'View')
    action = view_menu.addAction('Sheet preview')
    action.triggered.connect(lambda: tabs.setCurrentIndex(index))
