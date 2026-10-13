from PyQt6.QtCore import QEvent, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QStatusBar,
)

from ui.theme import Theme


class ActionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._hovered = False
        self.setMinimumHeight(34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    @property
    def hovered(self):
        return self._hovered

    def enterEvent(self, event: QEvent):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def sizeHint(self):
        hint = super().sizeHint()
        return QSize(max(hint.width(), 150), max(hint.height(), 34))


class HeaderLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setMinimumHeight(28)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Theme.BORDER, 2))
        painter.drawLine(0, self.height() - 2, self.width(), self.height() - 2)
        painter.end()

    def sizeHint(self):
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), 28))


class PreviewArea(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._source = QPixmap()
        self._placeholder = "Снимков пока нет"
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(420, 300)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, pixmap: QPixmap):
        self._source = pixmap
        self._rescale()

    def _rescale(self):
        if self._source.isNull():
            self.setPixmap(QPixmap())
            return
        self.setPixmap(
            self._source.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Theme.BORDER, 1))
        painter.setBrush(Theme.SURFACE)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), Theme.RADIUS, Theme.RADIUS)
        painter.end()
        if self._source.isNull():
            painter = QPainter(self)
            painter.setPen(Theme.MUTED)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._placeholder)
            painter.end()
            return
        super().paintEvent(event)


class DelaySpin(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 60)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def textFromValue(self, value):
        return "без задержки" if value == 0 else f"{value} c"

    def valueFromText(self, text):
        digits = "".join(symbol for symbol in text if symbol.isdigit())
        return int(digits) if digits else 0

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class EntityCombo(QComboBox):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._items = ()
        self.fill(items)

    @property
    def items(self):
        return self._items

    def fill(self, items):
        previous = self.currentText()
        self._items = tuple(items)
        self.blockSignals(True)
        self.clear()
        for item in self._items:
            self.addItem(str(item))
        restored = self.findText(previous)
        self.setCurrentIndex(restored if restored >= 0 else 0)
        self.blockSignals(False)

    def current_item(self):
        index = self.currentIndex()
        if not self._items:
            return None
        return self._items[index] if 0 <= index < len(self._items) else self._items[0]

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()

    def showPopup(self):
        self.setMaxVisibleItems(max(len(self._items), 1))
        super().showPopup()


class ScreenCombo(EntityCombo):
    def __init__(self, targets, parent=None):
        super().__init__(targets, parent)
        self.setMinimumWidth(280)

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        return QSize(max(hint.width(), 280), hint.height())


class FormatCombo(EntityCombo):
    def __init__(self, formats, parent=None):
        super().__init__(formats, parent)
        self.setMinimumWidth(140)

    def current_extension(self):
        item = self.current_item()
        return item.extension if item is not None else "png"


class ShotList(QListWidget):
    removeRequested = pyqtSignal(int)
    openRequested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setMinimumWidth(320)

    def add_shot(self, shot):
        item = QListWidgetItem(str(shot))
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.addItem(item)
        self.setCurrentItem(item)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete and self.currentRow() >= 0:
            self.removeRequested.emit(self.currentRow())
            return
        super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.currentRow() >= 0:
            self.openRequested.emit(self.currentRow())
            return
        super().mouseDoubleClickEvent(event)


class StatusPanel(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._counter = 0

    @property
    def counter(self):
        return self._counter

    def showMessage(self, message, timeout: int = 6000):
        self._counter += 1
        super().showMessage(f"[{self._counter}] {message}", timeout)


class SidePanel(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)


class CursorCheck(QCheckBox):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._states = 0

    @property
    def states(self):
        return self._states

    def nextCheckState(self):
        self._states += 1
        super().nextCheckState()

    def enterEvent(self, event: QEvent):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
