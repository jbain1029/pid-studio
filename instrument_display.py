"""Lossless display choices for built-in instrument tags, not tag validation."""
import re


def tag_lines(tag, function):
    """Keep familiar simple IDs compact; retain compound/arbitrary IDs in full.

    A component's declared function is authoritative. A user-entered tag is not
    reinterpreted as a new device function, nor are area numbers discarded.
    """
    if tag is None or tag == '':
        return function, ''
    simple = re.fullmatch(re.escape(function) + r'-?(\d+[A-Za-z]?)', tag)
    if simple:
        return function, simple.group(1)
    return function, tag


def draw_fitted_text(painter, box, text):
    """Keep complete text in exported SVG while fitting the available width."""
    from PySide6.QtCore import Qt
    if not text:
        return
    painter.save()
    width = painter.fontMetrics().horizontalAdvance(text)
    scale = min(1.0, box.width() / max(1, width))
    painter.translate(box.center())
    painter.scale(scale, 1)
    from PySide6.QtCore import QRectF
    painter.drawText(QRectF(-box.width()/scale/2, -box.height()/2,
                           box.width()/scale, box.height()), Qt.AlignmentFlag.AlignCenter, text)
    painter.restore()


def technology_rows(function, identity, technology):
    """Short technology captions fit within the circle, never across leads."""
    if technology == ['RADAR']:
        return [(function, [-12,-16,24,11],10), (identity,[-19,-5,38,10],9),
                ('RADAR',[-12,5,24,11],7)]
    if technology == ['THERMAL','MASS']:
        return [(function,[-11,-20,22,10],9), (identity,[-19,-10,38,10],8),
                ('THERMAL',[-19,0,38,10],8), ('MASS',[-11,10,22,10],8)]
    raise ValueError('Unknown built-in instrument technology layout')


def draw_technology_bubble(painter, function, identity, technology):
    from PySide6.QtCore import QRectF
    painter.save()
    for text, coordinates, size in technology_rows(function, identity, technology):
        font = painter.font()
        font.setPixelSize(size)
        painter.setFont(font)
        draw_fitted_text(painter,QRectF(*coordinates),text)
    painter.restore()
