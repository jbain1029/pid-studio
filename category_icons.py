"""Small engineering-navigation glyphs, not standardized P&ID artwork.

These icons identify catalog categories only; they never enter drawing exports.
"""
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF


_ROOTS = {
    'Process components': ('tank', '#356791'),
    'Valves': ('valve', '#856023'),
    'Piping': ('elbow', '#526b70'),
    'Instrumentation': ('gauge', '#396e89'),
    'Steam & utilities': ('steam', '#96602a'),
    'Pressure protection': ('shield', '#956043'),
    'Custom components': ('blocks', '#735b8e'),
}
_GROUPS = {
    'Tanks & vessels': 'tank', 'Pumps': 'pump',
    'Compressors & blowers': 'fan', 'Reactors & mixers': 'mixer',
    'Heat transfer': 'exchanger', 'Separation & treatment': 'filter',
    'Manual valves': 'valve', 'Actuated & control': 'actuator',
    'Regulators': 'regulator', 'Check valves': 'check',
    'Fittings & joints': 'elbow', 'Junctions & connectors': 'junction',
    'Strainers': 'strainer', 'Pressure': 'gauge',
    'Temperature': 'thermometer', 'Level': 'level', 'Flow': 'flow',
    'Analysis': 'flask', 'Controllers': 'controller',
    'General & signal conversion': 'signal', 'Steam traps': 'trap',
    'Utility equipment': 'utility', 'Relief & venting': 'relief',
    'Flame protection': 'flame',
}


def category_icon(path: tuple) -> QIcon:
    """Return a two-resolution icon for a root or nested category path."""
    root = path[0] if path else ''
    glyph, color = _ROOTS.get(root, ('blocks', '#735b8e'))
    # User-defined category names must not accidentally impersonate built-ins.
    if len(path) > 1 and root != 'Custom components':
        glyph = _GROUPS.get(path[-1], glyph)
    return QIcon(_icon(glyph, color))


@lru_cache(maxsize=64)
def _icon(glyph, color):
    icon = QIcon()
    for pixels in (20, 40):
        pixmap = QPixmap(pixels, pixels)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.scale(pixels / 20, pixels / 20)
        _paint(painter, glyph, QColor(color))
        painter.end()
        icon.addPixmap(pixmap)
    return icon


def _paint(p, glyph, accent):
    dark = QColor('#253a48')
    pale = QColor('#f5f7f8')
    p.setPen(QPen(dark, 1.35, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))
    p.setBrush(accent.lighter(170))

    def line(x1, y1, x2, y2):
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def rect(x, y, w, h):
        p.drawRect(QRectF(x, y, w, h))

    def ellipse(x, y, w, h):
        p.drawEllipse(QRectF(x, y, w, h))

    def poly(points):
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))

    def tank():
        rect(4, 5, 12, 10)
        ellipse(4, 3, 12, 4)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(QRectF(4, 13, 12, 4), 180 * 16, 180 * 16)
        line(4, 13, 4, 15)
        line(16, 13, 16, 15)

    def valve():
        line(1, 11, 19, 11)
        poly([(3, 6), (10, 11), (3, 16)])
        poly([(17, 6), (10, 11), (17, 16)])

    if glyph == 'tank':
        tank()
    elif glyph in ('valve', 'actuator', 'regulator', 'check'):
        valve()
        if glyph == 'valve':
            line(10, 5, 10, 10)
            line(6, 4, 14, 4)
        elif glyph == 'actuator':
            rect(7, 1, 6, 4)
            line(10, 5, 10, 10)
        elif glyph == 'regulator':
            p.setBrush(pale)
            ellipse(6, 1, 8, 5)
            line(10, 6, 10, 10)
        else:
            p.setPen(QPen(accent, 2))
            line(7, 3, 13, 3)
            line(11, 1, 13, 3)
            line(11, 5, 13, 3)
    elif glyph == 'elbow':
        poly([(2, 3), (7, 3), (7, 12), (18, 12), (18, 17), (2, 17)])
        line(1, 3, 8, 3)
        line(18, 11, 18, 18)
    elif glyph == 'junction':
        poly([(8, 2), (12, 2), (12, 8), (18, 8), (18, 12),
              (12, 12), (12, 18), (8, 18), (8, 12), (2, 12), (2, 8), (8, 8)])
    elif glyph == 'gauge':
        line(10, 16, 10, 19)
        ellipse(3, 2, 14, 14)
        line(10, 9, 14, 5)
        p.setBrush(accent)
        ellipse(8.5, 7.5, 3, 3)
        line(5, 9, 6, 9)
        line(10, 4, 10, 5)
    elif glyph == 'thermometer':
        p.setBrush(pale)
        p.drawRoundedRect(QRectF(8, 2, 4, 12), 2, 2)
        ellipse(6, 11, 8, 7)
        p.setPen(QPen(accent, 2))
        line(10, 6, 10, 14)
        line(14, 4, 17, 4)
        line(14, 8, 16, 8)
    elif glyph == 'level':
        rect(3, 2, 14, 16)
        p.fillRect(QRectF(4, 10, 12, 7), accent.lighter(160))
        line(4, 10, 16, 10)
        for y in (5, 8, 11, 14):
            line(12, y, 15, y)
    elif glyph == 'flow':
        line(2, 4, 18, 4)
        line(2, 16, 18, 16)
        p.setBrush(accent)
        poly([(3, 8), (12, 8), (12, 5), (18, 10), (12, 15), (12, 12), (3, 12)])
    elif glyph in ('pump', 'fan'):
        line(1, 10, 4, 10)
        line(14, 4, 18, 4)
        ellipse(3, 3, 14, 14)
        if glyph == 'pump':
            p.setBrush(accent)
            poly([(7, 6), (14, 10), (7, 14)])
        else:
            for rotation in (0, 120, 240):
                p.save()
                p.translate(10, 10)
                p.rotate(rotation)
                poly([(0, 0), (-3, -5), (2, -5), (3, -2)])
                p.restore()
        line(5, 18, 15, 18)
    elif glyph == 'mixer':
        tank()
        line(10, 1, 10, 13)
        line(6, 11, 14, 13)
        line(6, 13, 14, 11)
    elif glyph == 'exchanger':
        ellipse(2, 3, 16, 14)
        for y in (7, 10, 13):
            line(1, y, 19, y)
    elif glyph in ('filter', 'strainer'):
        poly([(3, 3), (17, 3), (17, 13), (10, 18), (3, 13)])
        for x in (6, 10, 14):
            line(x, 5, x, 12)
        for y in (7, 10):
            line(5, y, 15, y)
        if glyph == 'strainer':
            line(10, 16, 10, 19)
    elif glyph == 'flask':
        poly([(7, 2), (13, 2), (12, 3), (12, 8), (17, 16),
              (16, 18), (4, 18), (3, 16), (8, 8), (8, 3)])
        line(6, 12, 14, 12)
    elif glyph == 'controller':
        rect(2, 3, 16, 14)
        p.setBrush(pale)
        rect(5, 6, 10, 5)
        for x in (5, 10, 15):
            line(x, 14, x + 1, 14)
    elif glyph == 'signal':
        rect(2, 3, 16, 14)
        path = QPainterPath(QPointF(3, 11))
        path.cubicTo(6, 1, 7, 18, 10, 9)
        path.lineTo(12, 9)
        path.lineTo(12, 6)
        path.lineTo(16, 6)
        path.lineTo(16, 12)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
    elif glyph in ('steam', 'utility', 'trap'):
        rect(3, 12, 14, 6)
        if glyph == 'trap':
            ellipse(7, 13, 6, 4)
        else:
            line(6, 15, 14, 15)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for x in (5, 10, 15):
            path = QPainterPath(QPointF(x, 10))
            path.cubicTo(x - 4, 7, x + 4, 5, x, 2)
            p.drawPath(path)
    elif glyph in ('shield', 'relief', 'flame'):
        poly([(3, 3), (10, 1), (17, 3), (16, 12), (10, 18), (4, 12)])
        if glyph == 'shield':
            line(6, 9, 9, 12)
            line(9, 12, 14, 6)
        elif glyph == 'relief':
            line(10, 14, 10, 5)
            line(6, 9, 10, 5)
            line(14, 9, 10, 5)
        else:
            p.setBrush(accent)
            poly([(10, 4), (13, 9), (12, 13), (8, 13), (6, 10), (8, 7), (8, 10)])
    else:
        rect(2, 2, 6, 6)
        rect(12, 2, 6, 6)
        rect(7, 12, 6, 6)
        line(5, 8, 5, 10)
        line(15, 8, 15, 10)
        line(5, 10, 15, 10)
        line(10, 10, 10, 12)
