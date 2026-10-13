import os
from datetime import datetime

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QCursor, QGuiApplication, QPainter, QPixmap

from core.entities import KIND_ALL, KIND_REGION, KIND_SCREEN, ScreenTarget, Shot


class ScreenCatalog:
    @staticmethod
    def screens() -> tuple:
        return tuple(QGuiApplication.screens())

    @staticmethod
    def current():
        return QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()

    @staticmethod
    def virtual_geometry() -> QRect:
        area = QRect()
        for screen in ScreenCatalog.screens():
            area = area.united(screen.geometry())
        return area

    @staticmethod
    def geometry_of(target: ScreenTarget) -> QRect:
        screens = ScreenCatalog.screens()
        if target.kind == KIND_SCREEN and 0 <= target.index < len(screens):
            return screens[target.index].geometry()
        return ScreenCatalog.virtual_geometry()

    @staticmethod
    def targets() -> tuple:
        screens = ScreenCatalog.screens()
        area = ScreenCatalog.virtual_geometry()
        items = []
        if len(screens) > 1:
            items.append(ScreenTarget("Все экраны", KIND_ALL, -1, area.width(), area.height()))
        for index, screen in enumerate(screens, start=0):
            geometry = screen.geometry()
            items.append(
                ScreenTarget(
                    f"Экран {index + 1}",
                    KIND_SCREEN,
                    index,
                    geometry.width(),
                    geometry.height(),
                    screen.name(),
                )
            )
        items.append(ScreenTarget("Выделенная область", KIND_REGION, -1, area.width(), area.height()))
        return tuple(items)


class ScreenCapturer:
    def __init__(self, folder: str):
        self._folder = folder
        self.folder = folder

    @property
    def folder(self) -> str:
        return self._folder

    @folder.setter
    def folder(self, value: str):
        text = str(value).strip()
        if not text:
            raise ValueError("folder must not be empty")
        os.makedirs(text, exist_ok=True)
        self._folder = text

    @staticmethod
    def grab_all() -> QPixmap:
        area = ScreenCatalog.virtual_geometry()
        canvas = QPixmap(area.size())
        canvas.fill()
        painter = QPainter(canvas)
        for screen in ScreenCatalog.screens():
            geometry = screen.geometry()
            painter.drawPixmap(geometry.topLeft() - area.topLeft(), screen.grabWindow(0))
        painter.end()
        return canvas

    @staticmethod
    def grab_index(index: int) -> QPixmap:
        screens = ScreenCatalog.screens()
        if not 0 <= index < len(screens):
            raise OSError(f"Экран {index + 1} недоступен")
        return screens[index].grabWindow(0)

    @staticmethod
    def crop(source: QPixmap, rect: QRect) -> QPixmap:
        return source.copy(rect.normalized())

    @staticmethod
    def build_name(extension: str) -> str:
        moment = datetime.now().strftime("%d.%m.%Y_%H-%M-%S")
        return f"shot_{moment}.{extension}"

    def grab(self, target: ScreenTarget) -> QPixmap:
        if target.kind == KIND_SCREEN:
            pixmap = self.grab_index(target.index)
        elif target.kind in (KIND_ALL, KIND_REGION):
            pixmap = self.grab_all()
        else:
            raise ValueError(f"unknown kind: {target.kind}")
        if pixmap.isNull() or pixmap.width() == 0:
            raise OSError("Пустой снимок: сеанс Wayland не отдаёт экран через Qt, нужен X11")
        return pixmap

    def store(self, pixmap: QPixmap, target: ScreenTarget, image_format) -> Shot:
        name = self.build_name(image_format.extension)
        path = os.path.join(self._folder, name)
        if not pixmap.save(path, image_format.code, image_format.quality):
            raise OSError(f"cannot save {path}")
        return Shot(name, path, pixmap.width(), pixmap.height(), target, image_format)

    def __repr__(self) -> str:
        return f"ScreenCapturer(folder={self._folder!r})"

    def __str__(self) -> str:
        return f"Папка снимков: {self._folder}"
