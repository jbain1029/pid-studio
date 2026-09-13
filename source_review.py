"""Source-region review UI for validated offline proposals."""
import base64
from PySide6.QtCore import Qt, QRectF, Signal, QTimer
from PySide6.QtGui import QImage, QPixmap, QPen, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QGraphicsView, QGraphicsScene


class SourceReview(QWidget):
    reviewed = Signal(bool)

    def __init__(self, document, findings, parent=None):
        super().__init__(parent)
        self.findings = findings
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        label = QLabel('Source checks — select each item, compare it with the draft, then mark it reviewed. A checkmark records your review, not engineering approval.')
        label.setWordWrap(True)
        layout.addWidget(label)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setMinimumHeight(160)
        self.image = QImage()
        try:
            self.image.loadFromData(base64.b64decode(document.get('reference',{}).get('data',''),validate=True))
        except (ValueError,TypeError):
            pass
        if not self.image.isNull():
            self.scene.addPixmap(QPixmap.fromImage(self.image))
        else:
            self.scene.addText('No readable reference image attached')
        self.highlight = self.scene.addRect(QRectF(),QPen(QColor('#b53624'),3))
        self.highlight.setZValue(1)
        self.highlight.hide()
        layout.addWidget(self.view,1)
        self.list = QListWidget()
        for finding in findings:
            item = QListWidgetItem(finding['message'],self.list)
            item.setToolTip('Draft object IDs: '+', '.join(finding['object_ids']))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.list.currentRowChanged.connect(self.focus_region)
        self.list.itemChanged.connect(lambda *_: self.reviewed.emit(self.complete()))
        layout.addWidget(self.list)
        if findings:
            QTimer.singleShot(0,lambda:self.list.setCurrentRow(0))

    def complete(self):
        if self.image.isNull() and any(f['region'] for f in self.findings):
            return False
        return all(self.list.item(i).checkState()==Qt.CheckState.Checked for i in range(self.list.count()))

    def focus_region(self, index):
        self.highlight.hide()
        if index < 0 or self.image.isNull():
            return
        region = self.findings[index]['region']
        if region:
            rect = QRectF(region['x']*self.image.width(),region['y']*self.image.height(),
                          region['width']*self.image.width(),region['height']*self.image.height())
            self.highlight.setRect(rect)
            self.highlight.show()
            self.view.fitInView(rect.adjusted(-20,-20,20,20),Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.view.fitInView(QRectF(0,0,self.image.width(),self.image.height()),Qt.AspectRatioMode.KeepAspectRatio)
