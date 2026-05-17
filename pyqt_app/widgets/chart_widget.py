"""
pyqt_app/widgets/chart_widget.py
Beaply — Lightweight chart widgets using QPainter (no matplotlib needed).

Widgets:
  BarChartWidget    — horizontal or vertical bar chart
  DonutChartWidget  — donut / pie chart
  MiniBarWidget     — tiny inline bar for quick comparisons
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore    import Qt, QRect, QRectF, QPointF, QTimer, pyqtProperty
from PyQt6.QtGui     import (QPainter, QColor, QFont, QPen, QBrush,
                              QLinearGradient, QPainterPath, QFontMetrics)
import math


# ─────────────────────────────────────────────────────────────────────────────
# Palette helpers
# ─────────────────────────────────────────────────────────────────────────────

CHART_COLORS = [
    "#A8C5B0", "#D4917B", "#7DB8C8", "#C8A87D",
    "#B07DB8", "#7DB87D", "#B8C87D", "#C87D7D",
    "#7D9AB8", "#B87DA0",
]


def _hex(h: str) -> QColor:
    return QColor(h)


# ─────────────────────────────────────────────────────────────────────────────
# Vertical Bar Chart
# ─────────────────────────────────────────────────────────────────────────────

class BarChartWidget(QWidget):
    """
    Vertical bar chart with animated fill.

    data   : list of (label: str, value: float)
    title  : optional chart title string
    color  : bar color hex (single) or list of hex strings
    mode   : 'light' | 'dark'
    """

    def __init__(self, data: list, title: str = "",
                 color=None, mode: str = "light",
                 show_values: bool = True,
                 parent=None):
        super().__init__(parent)
        self._data        = data or []
        self._title       = title
        self._mode        = mode
        self._show_values = show_values
        self._anim_pct    = 0.0      # 0.0 → 1.0 animation progress

        # Resolve colors
        if color is None:
            self._colors = CHART_COLORS
        elif isinstance(color, list):
            self._colors = color
        else:
            self._colors = [color] * len(self._data)

        self.setMinimumHeight(180)

        # Kick off entrance animation
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        self._anim_pct = min(1.0, self._anim_pct + 0.04)
        self.update()
        if self._anim_pct >= 1.0:
            self._timer.stop()

    # ── Colors per mode ──────────────────────────────────────
    def _bg(self):   return "#FFFFFF" if self._mode == "light" else "#292A2D"
    def _txt(self):  return "#2D2D2D" if self._mode == "light" else "#E8EAED"
    def _muted(self):return "#888888" if self._mode == "light" else "#9AA0A6"
    def _grid(self): return "#E8E0D8" if self._mode == "light" else "#3C4043"

    def paintEvent(self, _):
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        pad_l = 36; pad_r = 12; pad_t = 36; pad_b = 42

        # Title
        if self._title:
            tf = QFont("Segoe UI", 10, QFont.Weight.Bold)
            p.setFont(tf)
            p.setPen(_hex(self._txt()))
            p.drawText(pad_l, 4, W - pad_l - pad_r, pad_t - 4,
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       self._title)

        n     = len(self._data)
        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b
        max_v = max((v for _, v in self._data), default=1) or 1

        bar_w   = max(6, int(chart_w / n * 0.55))
        spacing = chart_w / n

        # Grid lines
        grid_pen = QPen(_hex(self._grid()), 1, Qt.PenStyle.DotLine)
        p.setPen(grid_pen)
        for i in range(5):
            y = pad_t + chart_h - int(chart_h * i / 4)
            p.drawLine(pad_l, y, W - pad_r, y)

        # Y-axis labels
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(_hex(self._muted()))
        for i in range(5):
            val = int(max_v * i / 4)
            y   = pad_t + chart_h - int(chart_h * i / 4)
            p.drawText(0, y - 8, pad_l - 4, 16,
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                       str(val))

        # Bars
        for idx, (label, value) in enumerate(self._data):
            x    = pad_l + spacing * idx + (spacing - bar_w) / 2
            filled_h = int(chart_h * (value / max_v) * self._anim_pct)
            y_top    = pad_t + chart_h - filled_h

            clr = _hex(self._colors[idx % len(self._colors)])

            # Gradient fill
            grad = QLinearGradient(x, y_top, x, pad_t + chart_h)
            lighter = QColor(clr)
            lighter.setAlphaF(0.6)
            grad.setColorAt(0.0, clr)
            grad.setColorAt(1.0, lighter)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(grad))
            radius = min(6, bar_w // 2)
            rect   = QRectF(x, y_top, bar_w, filled_h)
            p.drawRoundedRect(rect, radius, radius)

            # Value label above bar
            if self._show_values and value > 0 and self._anim_pct >= 0.95:
                p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
                p.setPen(_hex(self._txt()))
                p.drawText(int(x) - 4, y_top - 16, bar_w + 8, 16,
                           Qt.AlignmentFlag.AlignCenter,
                           str(int(value)))

            # X label
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(_hex(self._muted()))
            p.drawText(int(x) - 4, H - pad_b + 6, bar_w + 8, 20,
                       Qt.AlignmentFlag.AlignCenter, label)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Donut / Pie Chart
# ─────────────────────────────────────────────────────────────────────────────

class DonutChartWidget(QWidget):
    """
    Animated donut chart.

    data  : list of (label: str, value: float)
    mode  : 'light' | 'dark'
    """

    def __init__(self, data: list, mode: str = "light",
                 thickness: int = 28, colors: list = None, parent=None):
        super().__init__(parent)
        self._data      = [(l, v) for l, v in data if v > 0]
        self._mode      = mode
        self._thickness = thickness
        self._colors    = colors if colors is not None else CHART_COLORS
        self._anim_pct  = 0.0
        self.setMinimumSize(160, 160)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        self._anim_pct = min(1.0, self._anim_pct + 0.04)
        self.update()
        if self._anim_pct >= 1.0:
            self._timer.stop()

    def _bg(self):    return "#FFFFFF" if self._mode == "light" else "#292A2D"
    def _txt(self):   return "#2D2D2D" if self._mode == "light" else "#E8EAED"
    def _muted(self): return "#888888" if self._mode == "light" else "#9AA0A6"

    def paintEvent(self, _):
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H   = self.width(), self.height()
        size   = min(W, H) - 16
        x_off  = (W - size) / 2
        y_off  = (H - size) / 2
        rect   = QRectF(x_off, y_off, size, size)
        inner  = QRectF(x_off + self._thickness,
                        y_off + self._thickness,
                        size - 2 * self._thickness,
                        size - 2 * self._thickness)

        total  = sum(v for _, v in self._data) or 1
        start_angle = 90 * 16   # 12 o'clock in Qt units (1/16 degree)
        full_span   = int(360 * 16 * self._anim_pct)
        remaining   = full_span

        for i, (label, value) in enumerate(self._data):
            span = int(360 * 16 * value / total)
            span = min(span, remaining)
            remaining -= span

            clr = _hex(self._colors[i % len(self._colors)])
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(clr))
            p.drawPie(rect, start_angle - span, span)
            start_angle -= span

        # Inner circle (donut hole)
        bg = _hex(self._bg())
        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(inner)

        # Center label: largest slice %
        if self._anim_pct >= 0.95 and self._data:
            top_l, top_v = max(self._data, key=lambda x: x[1])
            pct  = int(top_v / total * 100)
            cx   = W / 2; cy = H / 2
            p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            p.setPen(_hex(self._txt()))
            p.drawText(int(cx) - 30, int(cy) - 14, 60, 20,
                       Qt.AlignmentFlag.AlignCenter, f"{pct}%")
            p.setFont(QFont("Segoe UI", 7))
            p.setPen(_hex(self._muted()))
            # Truncate label if needed
            lbl = top_l if len(top_l) <= 10 else top_l[:9] + "…"
            p.drawText(int(cx) - 30, int(cy) + 2, 60, 14,
                       Qt.AlignmentFlag.AlignCenter, lbl)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Legend Widget (horizontal list of colored bullets + labels)
# ─────────────────────────────────────────────────────────────────────────────

class ChartLegendWidget(QWidget):
    """Row of colored dot + label pairs for chart legends."""

    def __init__(self, labels: list, colors: list = None,
                 mode: str = "light", parent=None):
        super().__init__(parent)
        self._labels = labels
        self._colors = colors or CHART_COLORS
        self._mode   = mode
        self.setFixedHeight(20)

    def _txt(self): return "#2D2D2D" if self._mode == "light" else "#E8EAED"
    def _muted(self): return "#888888" if self._mode == "light" else "#9AA0A6"

    def paintEvent(self, _):
        p  = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        fm = QFontMetrics(QFont("Segoe UI", 8))
        x  = 0
        for i, label in enumerate(self._labels):
            clr = _hex(self._colors[i % len(self._colors)])
            p.setBrush(QBrush(clr))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(x, 5, 8, 8)
            x += 12
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(_hex(self._muted()))
            w = fm.horizontalAdvance(label) + 16
            p.drawText(x, 0, w, 18,
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       label)
            x += w
        p.end()
