from PyQt6.QtGui import QColor


class Theme:
    BACKGROUND = QColor(14, 14, 14)
    PANEL = QColor(22, 22, 22)
    SURFACE = QColor(18, 18, 18)
    BORDER = QColor(58, 58, 58)
    TEXT = QColor(232, 232, 232)
    MUTED = QColor(150, 150, 150)
    ACCENT = QColor(255, 255, 255)

    @staticmethod
    def qss():
        return f"""
        QWidget {{
            background-color: {Theme.BACKGROUND.name()};
            color: {Theme.TEXT.name()};
            font-size: 13px;
        }}
        QMainWindow, QDialog {{
            background-color: {Theme.BACKGROUND.name()};
        }}
        QGroupBox {{
            background-color: {Theme.PANEL.name()};
            border: 1px solid {Theme.BORDER.name()};
            border-radius: 2px;
            margin-top: 10px;
            padding-top: 8px;
            font-weight: 600;
            letter-spacing: 1px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px;
            color: {Theme.MUTED.name()};
            background-color: {Theme.PANEL.name()};
        }}
        QLabel {{
            background-color: transparent;
            color: {Theme.TEXT.name()};
        }}
        QPushButton {{
            background-color: {Theme.SURFACE.name()};
            color: {Theme.TEXT.name()};
            border: 1px solid {Theme.BORDER.name()};
            border-radius: 2px;
            padding: 6px 12px;
            text-align: center;
        }}
        QPushButton:hover {{
            background-color: {Theme.BORDER.name()};
            border-color: {Theme.ACCENT.name()};
        }}
        QPushButton:pressed {{
            background-color: {Theme.ACCENT.name()};
            color: {Theme.BACKGROUND.name()};
        }}
        QPushButton:disabled {{
            color: {Theme.MUTED.name()};
            border-color: {Theme.SURFACE.name()};
        }}
        QLineEdit, QSpinBox, QComboBox {{
            background-color: {Theme.SURFACE.name()};
            color: {Theme.TEXT.name()};
            border: 1px solid {Theme.BORDER.name()};
            border-radius: 2px;
            padding: 5px 8px;
            selection-background-color: {Theme.ACCENT.name()};
            selection-color: {Theme.BACKGROUND.name()};
        }}
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border-color: {Theme.ACCENT.name()};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 18px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {Theme.TEXT.name()};
            margin-right: 6px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Theme.SURFACE.name()};
            color: {Theme.TEXT.name()};
            border: 1px solid {Theme.BORDER.name()};
            selection-background-color: {Theme.ACCENT.name()};
            selection-color: {Theme.BACKGROUND.name()};
            outline: none;
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {Theme.PANEL.name()};
            border-left: 1px solid {Theme.BORDER.name()};
            width: 16px;
        }}
        QSpinBox::up-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 5px solid {Theme.TEXT.name()};
        }}
        QSpinBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {Theme.TEXT.name()};
        }}
        QCheckBox {{
            background-color: transparent;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border: 1px solid {Theme.BORDER.name()};
            background-color: {Theme.SURFACE.name()};
        }}
        QCheckBox::indicator:hover {{
            border-color: {Theme.ACCENT.name()};
        }}
        QCheckBox::indicator:checked {{
            background-color: {Theme.ACCENT.name()};
            border-color: {Theme.ACCENT.name()};
        }}
        QListWidget {{
            background-color: {Theme.SURFACE.name()};
            alternate-background-color: {Theme.PANEL.name()};
            border: 1px solid {Theme.BORDER.name()};
            border-radius: 2px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 6px 8px;
            border-bottom: 1px solid {Theme.BACKGROUND.name()};
        }}
        QListWidget::item:hover {{
            background-color: {Theme.BORDER.name()};
        }}
        QListWidget::item:selected {{
            background-color: {Theme.ACCENT.name()};
            color: {Theme.BACKGROUND.name()};
        }}
        QScrollBar:vertical, QScrollBar:horizontal {{
            background-color: {Theme.BACKGROUND.name()};
            width: 10px;
            height: 10px;
            margin: 0;
        }}
        QScrollBar::handle {{
            background-color: {Theme.BORDER.name()};
            min-height: 24px;
            min-width: 24px;
        }}
        QScrollBar::handle:hover {{
            background-color: {Theme.MUTED.name()};
        }}
        QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
            border: none;
            height: 0;
            width: 0;
        }}
        QStatusBar {{
            background-color: {Theme.PANEL.name()};
            color: {Theme.MUTED.name()};
            border-top: 1px solid {Theme.BORDER.name()};
        }}
        QStatusBar::item {{
            border: none;
        }}
        QMessageBox {{
            background-color: {Theme.PANEL.name()};
        }}
        QToolTip {{
            background-color: {Theme.SURFACE.name()};
            color: {Theme.TEXT.name()};
            border: 1px solid {Theme.BORDER.name()};
        }}
        """

    @staticmethod
    def apply(app):
        app.setStyle("Fusion")
        app.setStyleSheet(Theme.qss())
