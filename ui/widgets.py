"""
Shared UI widgets used across panels.
"""

from PyQt6.QtWidgets import QPushButton, QColorDialog, QApplication, QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class ColorButton(QPushButton):
    """Theme-safe color swatch. ObjectName ColorSwatch so global QSS does not override fill."""

    color_changed = pyqtSignal(str)

    def __init__(self, color: str = "#ffffff", parent=None):
        super().__init__(parent)
        self._color = color or "#ffffff"
        self.setObjectName("ColorSwatch")
        self.setFixedSize(40, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to choose color")
        self.setAccessibleName("Color swatch")
        self.setAccessibleDescription("Opens a color picker")
        self.clicked.connect(self._pick)
        self._style()

    def _style(self):
        self.setStyleSheet(
            f"""
            QPushButton#ColorSwatch {{
                background-color: {self._color};
                border: 2px solid #94a3b8;
                border-radius: 6px;
                min-width: 40px;
                max-width: 40px;
                min-height: 28px;
                max-height: 28px;
                padding: 0px;
            }}
            QPushButton#ColorSwatch:hover {{
                border: 2px solid #0d9488;
            }}
            QPushButton#ColorSwatch:focus {{
                border: 2px solid #0d9488;
                outline: none;
            }}
            """
        )

    def _pick(self):
        # Scope-clear only for the dialog: avoid app-wide flicker by using native dialog when possible
        app = QApplication.instance()
        old_ss = app.styleSheet() if app else ""
        try:
            if app:
                # Soften only dialog-hostile rules instead of wiping everything when possible
                app.setStyleSheet("")
            c = QColorDialog.getColor(
                QColor(self._color),
                self,
                "Select Color",
                QColorDialog.ColorDialogOption.DontUseNativeDialog,
            )
        finally:
            if app:
                app.setStyleSheet(old_ss)
        if c.isValid():
            self._color = c.name()
            self._style()
            self.color_changed.emit(self._color)

    def color(self) -> str:
        return self._color

    def set_color(self, c: str):
        self._color = c or "#000000"
        self._style()


class EmptyState(QFrame):
    """Centered empty-state with title, hint, and optional action buttons."""

    def __init__(self, title: str, hint: str, parent=None):
        super().__init__(parent)
        self.setObjectName("emptyState")
        self.setStyleSheet("QFrame#emptyState { background: transparent; border: none; }")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(32, 40, 32, 40)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.hint_label = QLabel(hint)
        self.hint_label.setObjectName("mutedLabel")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        self.btn_row = QHBoxLayout()
        self.btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_row.setSpacing(10)
        layout.addLayout(self.btn_row)

    def add_button(self, btn: QPushButton):
        self.btn_row.addWidget(btn)
