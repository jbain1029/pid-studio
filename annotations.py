"""Movable, persisted drawing notes using the same undo history as equipment."""
import copy
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QFont,QFontMetricsF,QPen,QColor
from PySide6.QtWidgets import QGraphicsObject,QGraphicsItem,QInputDialog
import pidcore as core
import drafting

class Note(QGraphicsObject):
    def __init__(self,record,window):
        super().__init__()
        self.record,self.window = record,window
        self.setPos(*record['position'])
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable|QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setZValue(2)

    def boundingRect(self):
        metrics = QFontMetricsF(QFont('Segoe UI',10))
        bounds = metrics.boundingRect(QRectF(0,0,self.record['width'],10000),Qt.TextFlag.TextWordWrap,self.record['text'])
        return QRectF(-5,-5,self.record['width']+10,max(25,bounds.height())+10)

    def paint(self,painter,option,widget):
        painter.setFont(QFont('Segoe UI',10))
        if self.isSelected() and not self.window.exporting:
            painter.setPen(QPen(QColor('#24659b'),1,Qt.PenStyle.DashLine))
            painter.drawRect(self.boundingRect())
        painter.setPen(QColor('#222222'))
        painter.drawText(self.boundingRect().adjusted(5,5,-5,-5),Qt.TextFlag.TextWordWrap,self.record['text'])

    def mousePressEvent(self,event):
        self.before = copy.deepcopy(self.window.document)
        super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        super().mouseMoveEvent(event)
        self.setPos(drafting.snap(self.window,self.x()),drafting.snap(self.window,self.y()))
        self.record['position'] = [self.x(),self.y()]
        self.window.update_lines()

    def mouseReleaseEvent(self,event):
        super().mouseReleaseEvent(event)
        for item in self.window.scene.selectedItems():
            if hasattr(item,'record') and 'position' in item.record:
                item.record['position'] = [item.x(),item.y()]
        if self.before != self.window.document:
            self.window.history.append(self.before)
            self.window.future.clear()
            self.window.changed()

    def mouseDoubleClickEvent(self,event):
        text,ok = QInputDialog.getMultiLineText(self.window,'Edit drawing note','Note text',self.record['text'])
        if ok:
            self.window.checkpoint()
            self.prepareGeometryChange()
            self.record['text'] = text
            self.update()
            self.window.changed()

def install(window):
    menu = next(a.menu() for a in window.menuBar().actions() if a.text()=='Edit')
    def add():
        text,ok = QInputDialog.getMultiLineText(window,'Add drawing note','Note text')
        if ok and text.strip():
            point = window.view.mapToScene(window.view.viewport().rect().center())
            window.checkpoint()
            window.document.setdefault('notes',[]).append({'id':core.uid(),'text':text,'position':[point.x(),point.y()],'width':240})
            window.rebuild()
    menu.addAction('Add drawing note…').triggered.connect(add)
