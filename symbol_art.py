"""Original vector drafting geometry for extended library symbols."""
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPolygonF

KINDS = {'vessel','gear_pump','compressor','ball_valve','butterfly_valve','relief_valve','reducer','strainer','controller'}

def draw(p, kind):
    if kind not in KINDS:
        return False
    if kind == 'controller':
        p.drawLine(0,-40,0,40)
        p.drawEllipse(-25,-25,50,50)
        p.drawLine(-25,0,25,0)
        p.drawText(QRectF(-23,-22,46,20),Qt.AlignmentFlag.AlignCenter,'C')
        return True
    p.drawLine(-40,0,40,0)
    if kind == 'vessel':
        p.drawLine(0,-40,0,40)
        p.drawRoundedRect(QRectF(-24,-32,48,64),17,17)
    elif kind == 'gear_pump':
        p.drawEllipse(-28,-25,56,50)
        p.drawEllipse(-18,-10,20,20)
        p.drawEllipse(-2,-10,20,20)
        p.drawLine(-8,-13,-8,13)
        p.drawLine(8,-13,8,13)
    elif kind == 'compressor':
        p.drawEllipse(-27,-27,54,54)
        p.drawPolygon(QPolygonF([QPointF(-18,-18),QPointF(19,-8),QPointF(19,8),QPointF(-18,18)]))
    elif kind == 'ball_valve':
        p.drawPolygon(QPolygonF([QPointF(-22,-16),QPointF(22,16),QPointF(22,-16),QPointF(-22,16)]))
        p.drawEllipse(-10,-10,20,20)
        p.drawLine(0,-10,0,-28)
        p.drawLine(-12,-28,12,-28)
    elif kind == 'butterfly_valve':
        p.drawEllipse(-23,-23,46,46)
        p.drawLine(-15,-18,15,18)
        p.drawEllipse(-3,-3,6,6)
    elif kind == 'relief_valve':
        p.drawRect(-20,-15,40,30)
        p.drawLine(-12,8,12,-8)
        p.drawLine(12,-8,4,-8)
        p.drawLine(12,-8,10,0)
        p.drawLine(0,-15,0,-20)
        p.drawPolyline(QPolygonF([QPointF(0,-20),QPointF(-8,-24),QPointF(8,-28),QPointF(-8,-32),QPointF(8,-36),QPointF(0,-40)]))
    elif kind == 'reducer':
        p.drawPolygon(QPolygonF([QPointF(-24,-18),QPointF(24,-8),QPointF(24,8),QPointF(-24,18)]))
    elif kind == 'strainer':
        p.drawPolygon(QPolygonF([QPointF(-23,-10),QPointF(23,-10),QPointF(23,10),QPointF(3,10),QPointF(-12,29),QPointF(-23,20),QPointF(-10,5)]))
        p.drawLine(-16,19,0,0)
    return True
