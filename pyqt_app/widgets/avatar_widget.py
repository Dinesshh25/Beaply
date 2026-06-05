from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap, QColor
from PyQt6.QtCore import Qt, QSize

class AvatarWidget(QLabel):
    def __init__(self, size=100, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self._pixmap = None
        self.setStyleSheet("background: transparent;")
        
    def set_avatar(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self.update()
        
    def paintEvent(self, event):
        if not self._pixmap:
            # Draw a default placeholder if no pixmap
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor("#E2E8E2"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, self._size, self._size)
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        path = QPainterPath()
        path.addEllipse(0, 0, self._size, self._size)
        painter.setClipPath(path)
        
        # Scale pixmap to cover the circle
        scaled_pixmap = self._pixmap.scaled(
            self._size, self._size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Center the pixmap
        x = (self._size - scaled_pixmap.width()) // 2
        y = (self._size - scaled_pixmap.height()) // 2
        
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
