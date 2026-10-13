import os
import subprocess
import sys

from PyQt6.QtCore import QRect, Qt, QTimer
from PyQt6.QtGui import QGuiApplication, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from core.capture import ScreenCapturer, ScreenCatalog
from core.entities import KIND_REGION, ImageFormat, LogEntry, UserSession
from core.mapping import PairMap
from core.report import SessionReport
from ui.overlay import RegionOverlay
from ui.widgets import (
    ActionButton,
    CursorCheck,
    DelaySpin,
    FormatCombo,
    HeaderLabel,
    PreviewArea,
    ScreenCombo,
    ShotList,
    SidePanel,
    StatusPanel,
)


class AppWindow(QMainWindow):
    def __init__(self, login, folder: str, report_path: str):
        super().__init__()
        self._formats = ImageFormat.catalogue()
        self._targets = ScreenCatalog.targets()
        self._shots = []
        self._journal = []
        self._stats = PairMap()
        self._capturer = ScreenCapturer(folder)
        self._session = UserSession(login)
        self._report = SessionReport(report_path, (self._session,))
        self._overlay = None
        self._pending = None

        self.setWindowTitle(f"Framer [{self._session.login}]")
        self.resize(1040, 620)
        self._build()
        self._watch_screens()
        self._note(f"Сессия {self._session.login} открыта")

    @property
    def shots(self):
        return tuple(self._shots)

    @property
    def journal(self):
        return tuple(self._journal)

    @property
    def session(self):
        return self._session

    def _build(self):
        root = QWidget(self)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self._build_controls(), 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self._build_view(), 1)
        self.setCentralWidget(root)

        self._status = StatusPanel(self)
        self.setStatusBar(self._status)

    def _build_controls(self):
        panel = SidePanel("Параметры", self)
        panel.setFixedWidth(320)
        box = QVBoxLayout(panel)
        box.setContentsMargins(12, 18, 12, 12)
        box.setSpacing(8)

        self._screen = ScreenCombo(self._targets, panel)
        self._screen.currentIndexChanged.connect(self._on_target)
        self._format = FormatCombo(self._formats, panel)
        self._delay = DelaySpin(panel)
        self._cursor = CursorCheck("Прятать окно перед снимком", panel)
        self._cursor.setChecked(True)

        self.btn_shot = ActionButton("Сделать снимок", panel)
        self.btn_shot.setShortcut("Ctrl+N")
        self.btn_shot.clicked.connect(self._on_shoot)
        self.btn_copy = ActionButton("Копировать в буфер", panel)
        self.btn_copy.setShortcut("Ctrl+C")
        self.btn_copy.clicked.connect(self._on_copy)
        self.btn_delete = ActionButton("Удалить снимок", panel)
        self.btn_delete.clicked.connect(lambda: self._on_drop(self._list.currentRow()))
        self.btn_folder = ActionButton("Папка сохранения", panel)
        self.btn_folder.clicked.connect(self._on_folder)
        self.btn_open = ActionButton("Открыть папку", panel)
        self.btn_open.clicked.connect(lambda: self._reveal(self._capturer.folder))

        top = Qt.AlignmentFlag.AlignTop

        box.addWidget(HeaderLabel("Экран", panel), 0, top)
        box.addWidget(self._screen, 0, top)
        box.addWidget(HeaderLabel("Формат", panel), 0, top)
        box.addWidget(self._format, 0, top)
        box.addWidget(HeaderLabel("Задержка", panel), 0, top)
        box.addWidget(self._delay, 0, top)
        box.addWidget(self._cursor, 0, top)
        box.addSpacing(6)
        box.addWidget(HeaderLabel("Действия", panel), 0, top)
        box.addWidget(self.btn_shot, 0, top)
        box.addWidget(self.btn_copy, 0, top)
        box.addWidget(self.btn_delete, 0, top)
        box.addWidget(self.btn_folder, 0, top)
        box.addWidget(self.btn_open, 0, top)
        box.addStretch(1)
        return panel

    def _build_view(self):
        column = QVBoxLayout()
        column.setSpacing(8)
        self._preview = PreviewArea(self)
        self._list = ShotList(self)
        self._list.currentRowChanged.connect(self._on_select)
        self._list.removeRequested.connect(self._on_drop)
        self._list.openRequested.connect(lambda row: self._reveal(self._shots[row].path))
        column.addWidget(HeaderLabel("Просмотр", self), 0, Qt.AlignmentFlag.AlignTop)
        column.addWidget(self._preview, 3)
        column.addWidget(HeaderLabel("Снимки сессии", self), 0, Qt.AlignmentFlag.AlignTop)
        column.addWidget(self._list, 2)
        return column

    def _watch_screens(self):
        app = QApplication.instance()
        app.screenAdded.connect(self._refresh_targets)
        app.screenRemoved.connect(self._refresh_targets)

    def _refresh_targets(self, _screen=None):
        self._targets = ScreenCatalog.targets()
        self._screen.fill(self._targets)
        self._note(f"Список экранов обновлён: {len(self._targets)} пункта(ов)")

    def _note(self, text):
        entry = LogEntry(text)
        self._journal.append(entry)
        self._status.showMessage(text)

    def _on_target(self, _index):
        target = self._screen.current_item()
        if target is not None:
            self._note(f"Выбрано: {target}")

    def _on_select(self, row):
        if 0 <= row < len(self._shots):
            self._preview.source = QPixmap(self._shots[row].path)
        else:
            self._preview.source = QPixmap()

    def _on_shoot(self):
        target = self._screen.current_item()
        if target is None:
            self._note("Экран не выбран")
            return
        self._pending = target
        if self._cursor.isChecked():
            self.hide()
        QTimer.singleShot(self._delay.value() * 1000 + 300, self._run)

    def _run(self):
        target = self._pending
        try:
            pixmap = self._capturer.grab(target)
        except OSError as error:
            self._fail(str(error))
            return
        if target.kind == KIND_REGION:
            self._ask_region(pixmap)
            return
        self._finish(pixmap, target)

    def _ask_region(self, pixmap: QPixmap):
        self._overlay = RegionOverlay(pixmap, ScreenCatalog.virtual_geometry(), None)
        self._overlay.selected.connect(lambda rect: self._on_region(pixmap, rect))
        self._overlay.cancelled.connect(self._on_cancel)
        self._overlay.show()
        self._overlay.activateWindow()
        self._overlay.setFocus()

    def _on_region(self, source: QPixmap, rect: QRect):
        scale = source.width() / max(self._overlay.width(), 1)
        area = QRect(
            int(rect.x() * scale),
            int(rect.y() * scale),
            int(rect.width() * scale),
            int(rect.height() * scale),
        )
        self._overlay = None
        self._finish(ScreenCapturer.crop(source, area), self._pending)

    def _on_cancel(self):
        self._overlay = None
        self.show()
        self._note("Съёмка области отменена")

    def _finish(self, pixmap: QPixmap, target):
        image_format = self._format.current_item()
        try:
            shot = self._capturer.store(pixmap, target, image_format)
        except OSError as error:
            self._fail(str(error))
            return
        self._shots.append(shot)
        self._stats.bump(target.title)
        self._list.add_shot(shot)
        self.show()
        self.activateWindow()
        self._note(f"Сохранено: {shot.path} ({len(shot)} байт)")

    def _fail(self, message):
        self.show()
        self._note(f"Ошибка: {message}")
        QMessageBox.critical(self, "Ошибка", message)

    def _on_copy(self):
        row = self._list.currentRow()
        if not 0 <= row < len(self._shots):
            self._note("Снимок не выбран")
            return
        QGuiApplication.clipboard().setPixmap(QPixmap(self._shots[row].path))
        self._note(f"В буфере: {self._shots[row].title}")

    def _on_drop(self, row):
        if not 0 <= row < len(self._shots):
            self._note("Снимок не выбран")
            return
        shot = self._shots.pop(row)
        self._list.takeItem(row)
        if os.path.exists(shot.path):
            os.remove(shot.path)
        self._note(f"Удалён: {shot.title}")

    def _on_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Папка сохранения", self._capturer.folder)
        if folder:
            self._capturer.folder = folder
            self._note(str(self._capturer))

    def _reveal(self, path):
        target = path if os.path.isdir(path) else os.path.dirname(path)
        try:
            if sys.platform == "win32":
                os.startfile(target)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([opener, target])
        except OSError as error:
            self._note(f"Не открыть {target}: {error}")

    def stats_line(self):
        if not self._stats:
            return "Снимков не сделано"
        return ", ".join(f"{key}: {self._stats[key]}" for key in self._stats)

    def closeEvent(self, event):
        if self._overlay is not None:
            self._overlay.close()
        self._session.close()
        try:
            path = self._report.save()
        except OSError as error:
            QMessageBox.critical(self, "Отчёт", f"Не удалось сохранить отчёт: {error}")
            event.accept()
            return
        QMessageBox.information(
            self,
            "Отчёт сохранён",
            f"{path}\n\nСнимков: {len(self._shots)}\n{self.stats_line()}\nСобытий в журнале: {len(self._journal)}",
        )
        event.accept()
        QApplication.quit()
