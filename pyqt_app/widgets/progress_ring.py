"""
pyqt_app/widgets/progress_ring.py
Circular progress ring widget (Profile Completeness).
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class ProgressRing(QWidget):
    """A circular progress ring that displays a percentage."""

    def __init__(self, value: int = 0, size: int = 80,
                 ring_width: int = 7, parent=None,
                 bg_color="#DFE6E1", fg_color="#F4B3AD",
                 text_color="#555555"):
        super().__init__(parent)
        self._value = value
        self._size = size
        self._ring_width = ring_width
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._text_color = text_color
        self.setFixedSize(size, size)

    def set_value(self, v: int):
        self._value = max(0, min(100, v))
        self.update()

    def set_colors(self, bg: str, fg: str, text: str):
        self._bg_color = bg
        self._fg_color = fg
        self._text_color = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        m = self._ring_width + 2
        rect = QRectF(m, m, self._size - 2 * m, self._size - 2 * m)

        # Background arc
        pen_bg = QPen(QColor(self._bg_color), self._ring_width)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        # Foreground arc
        if self._value > 0:
            pen_fg = QPen(QColor(self._fg_color), self._ring_width)
            pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_fg)
            span = int((self._value / 100) * 360 * 16)
            painter.drawArc(rect, 90 * 16, -span)

        # Center text
        painter.setPen(QColor(self._text_color))
        font = QFont("Segoe UI", 14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self._value}%")
        painter.end()
