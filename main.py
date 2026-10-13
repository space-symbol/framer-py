import getpass
import os
import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import AppWindow
from ui.theme import Theme

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOTS_DIR = os.path.join(BASE_DIR, "shots")
REPORT_PATH = os.path.join(BASE_DIR, "report.txt")


class Launcher:
    def __init__(self, argv):
        self._argv = list(argv)

    @staticmethod
    def detect_login():
        try:
            return getpass.getuser()
        except OSError:
            return "user"

    def run(self):
        app = QApplication(self._argv)
        app.setApplicationName("Framer")
        Theme.apply(app)
        window = AppWindow(self.detect_login(), SHOTS_DIR, REPORT_PATH)
        window.show()
        return app.exec()


if __name__ == "__main__":
    sys.exit(Launcher(sys.argv).run())
