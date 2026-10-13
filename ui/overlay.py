from PyQt6.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QWidget

from ui.theme import Theme


class RegionOverlay(QWidget):
    selected = pyqtSignal(QRect)
    cancelled = pyqtSignal()

    def __init__(self, background: QPixmap, geometry: QRect, parent=None):
        super().__init__(parent)
        self._background = background
        self._origin = QPoint()
        self._current = QPoint()
        self._active = False
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setGeometry(geometry)

    @property
    def selection(self) -> QRect:
        return QRect(self._origin, self._current).normalized()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._background)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        area = self.selection
        if self._active and area.width() > 0 and area.height() > 0:
            painter.drawPixmap(area, self._background, area)
            painter.setPen(QPen(Theme.ACCENT, 2))
            painter.drawRect(area)
            painter.setPen(Theme.TEXT)
            painter.drawText(
                area.adjusted(4, -22, 0, 0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                f"{area.width()}×{area.height()}",
            )
        else:
            painter.setPen(Theme.TEXT)
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Выделите область мышью, Esc отменяет",
            )
        painter.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._active = True
        self._origin = event.position().toPoint()
        self._current = self._origin
        self.update()

    def mouseMoveEvent(self, event):
        if not self._active:
            return
        self._current = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or not self._active:
            return
        self._active = False
        area = self.selection
        self.close()
        if area.width() < 4 or area.height() < 4:
            self.cancelled.emit()
            return
        self.selected.emit(area)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.cancelled.emit()
            return
        super().keyPressEvent(event)
