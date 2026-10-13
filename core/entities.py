import os
from datetime import datetime

from core.base import TIME_FORMAT, Entity

KIND_ALL = "all"
KIND_SCREEN = "screen"
KIND_REGION = "region"

KINDS = frozenset((KIND_ALL, KIND_SCREEN, KIND_REGION))


class ImageFormat(Entity):
    def __init__(self, code: str, extension: str, quality: int):
        super().__init__(code)
        self._code = code.upper()
        self._extension = extension.lower()
        self._quality = 0
        self.quality = quality

    @property
    def code(self) -> str:
        return self._code

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def quality(self) -> int:
        return self._quality

    @quality.setter
    def quality(self, value: int):
        number = int(value)
        if not 0 <= number <= 100:
            raise ValueError("quality must be within 0..100")
        self._quality = number

    def summary(self) -> str:
        return f"{self._code} (.{self._extension})"

    def sort_key(self) -> tuple:
        return (self._code,)

    @staticmethod
    def catalogue() -> tuple:
        return (
            ImageFormat("PNG", "png", 100),
            ImageFormat("JPG", "jpg", 92),
            ImageFormat("BMP", "bmp", 100),
        )


class ScreenTarget(Entity):
    def __init__(self, title: str, kind: str, index: int, width: int, height: int, label: str = ""):
        super().__init__(title)
        self._kind = KIND_ALL
        self.kind = kind
        self._index = int(index)
        self._width = max(int(width), 0)
        self._height = max(int(height), 0)
        self._label = label

    @property
    def kind(self) -> str:
        return self._kind

    @kind.setter
    def kind(self, value: str):
        if value not in KINDS:
            raise ValueError(f"unknown kind: {value}")
        self._kind = value

    @property
    def index(self) -> int:
        return self._index

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def label(self) -> str:
        return self._label

    def resolution(self) -> str:
        return f"{self._width}×{self._height}"

    def summary(self) -> str:
        if self._kind == KIND_REGION:
            return self.title
        tail = f" ({self._label})" if self._label else ""
        return f"{self.title}{tail}, {self.resolution()}"

    def sort_key(self) -> tuple:
        return (self._kind, self._index, self.title)


class Shot(Entity):
    def __init__(self, title: str, path: str, width: int, height: int, target: ScreenTarget, image_format: ImageFormat):
        super().__init__(title)
        self._path = path
        self._width = max(int(width), 0)
        self._height = max(int(height), 0)
        self._target = target
        self._format = image_format

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str):
        text = str(value).strip()
        if not text:
            raise ValueError("path must not be empty")
        self._path = text

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def target(self) -> ScreenTarget:
        return self._target

    @property
    def image_format(self) -> ImageFormat:
        return self._format

    @property
    def weight(self) -> int:
        return os.path.getsize(self._path) if os.path.exists(self._path) else 0

    def summary(self) -> str:
        short_time = self.created_at.strftime("%H:%M:%S")
        return f"{self.title}   {self._width}x{self._height}   {self._target.title}   {short_time}"

    def sort_key(self) -> tuple:
        return (self.created_at, self.title)

    def __len__(self) -> int:
        return self.weight

    def __bool__(self) -> bool:
        return os.path.exists(self._path)


class LogEntry(Entity):
    def __init__(self, text: str):
        super().__init__(text)
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    def summary(self) -> str:
        return f'[{self.created_at.strftime("%H:%M:%S")}] {self._text}'

    def sort_key(self) -> tuple:
        return (self.created_at, self._text)


class UserSession(Entity):
    def __init__(self, login: str):
        super().__init__(login)
        self._login = login
        self._time_in = datetime.now()
        self._time_out = None

    @property
    def login(self) -> str:
        return self._login

    @login.setter
    def login(self, value: str):
        text = str(value).strip()
        if not text:
            raise ValueError("login must not be empty")
        self._login = text
        self.title = text

    @property
    def time_in(self) -> datetime:
        return self._time_in

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value: datetime):
        if value < self._time_in:
            raise ValueError("time_out must not precede time_in")
        self._time_out = value

    def close(self) -> datetime:
        self.time_out = datetime.now()
        return self._time_out

    def summary(self) -> str:
        finish = self._time_out.strftime(TIME_FORMAT) if self._time_out else "не закрыта"
        return f"{self._login}: вход {self._time_in.strftime(TIME_FORMAT)}, выход {finish}"

    def sort_key(self) -> tuple:
        return (self._time_in, self._login)
