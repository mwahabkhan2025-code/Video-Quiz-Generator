"""
Theme Manager - Light and Dark themes (polished)
"""

from PyQt6.QtWidgets import QApplication


class ThemeManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def apply_light(self):
        self.main_window.setStyleSheet("""
        * { font-family: "Segoe UI", "Noto Sans", sans-serif; }

        QMainWindow, QWidget {
            background-color: #f0f2f5;
            color: #1a1a2e;
            font-size: 13px;
        }

        QTabWidget::pane {
            border: none;
            background: #f0f2f5;
            top: -1px;
        }

        QTabBar::tab {
            background: transparent;
            color: #64748b;
            padding: 12px 28px;
            margin-right: 2px;
            border: none;
            font-size: 14px;
            font-weight: 500;
        }

        QTabBar::tab:selected {
            color: #0d9488;
            border-bottom: 3px solid #0d9488;
            background: #ffffff;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }

        QTabBar::tab:hover:!selected {
            color: #0f766e;
            background: #e0f2f1;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }

        QPushButton {
            background-color: #0d9488;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            min-height: 20px;
        }

        QPushButton:hover { background-color: #0f766e; }
        QPushButton:pressed { background-color: #115e59; }
        QPushButton:disabled { background-color: #94a3b8; color: #e2e8f0; }

        QPushButton#ColorSwatch {
            /* keep swatch fill from inline style; neutralize theme button chrome */
            min-width: 40px;
            max-width: 40px;
            min-height: 28px;
            max-height: 28px;
            padding: 0px;
        }


        QPushButton#secondaryButton {
            background-color: #ffffff;
            color: #334155;
            border: 1px solid #cbd5e1;
            font-weight: 500;
        }
        QPushButton#secondaryButton:hover {
            background-color: #f1f5f9;
            border-color: #94a3b8;
        }

        QPushButton#iconButton {
            background-color: #ffffff;
            color: #475569;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 4px;
            font-size: 14px;
            font-weight: 600;
            min-width: 28px;
            max-width: 32px;
            min-height: 28px;
            max-height: 32px;
        }
        QPushButton#iconButton:hover {
            background-color: #f0fdfa;
            border-color: #0d9488;
            color: #0d9488;
        }

        QFrame#card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
        }

        QLabel {
            background: transparent;
        }
        QLabel#sectionTitle {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            background: transparent;
        }
        QFormLayout QLabel, QWidget QLabel {
            background: transparent;
        }

        QStatusBar {
            background: #ffffff;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #64748b;
            padding: 4px 8px;
        }

        QMenuBar {
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            font-size: 13px;
            padding: 4px;
        }
        QMenuBar::item:selected { background: #e0f2f1; color: #0d9488; border-radius: 4px; }

        QMenu {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 4px;
        }
        QMenu::item { padding: 8px 24px; border-radius: 4px; }
        QMenu::item:selected { background: #e0f2f1; color: #0d9488; }

        QScrollArea { border: none; background: transparent; }
        QScrollBar:vertical {
            background: transparent; width: 8px; margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1; border-radius: 4px; min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background: #94a3b8; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

        QTextEdit, QPlainTextEdit, QLineEdit {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: #99f6e4;
        }
        QTextEdit:focus, QLineEdit:focus { border-color: #0d9488; }

        QComboBox {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 6px 12px;
            min-height: 20px;
        }
        QComboBox:hover { border-color: #94a3b8; }
        QComboBox::drop-down { border: none; width: 24px; }

        QSpinBox, QDoubleSpinBox {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 4px 8px;
        }

        QCheckBox { spacing: 8px; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 2px solid #cbd5e1;
            border-radius: 4px;
            background: #ffffff;
        }
        QCheckBox::indicator:checked {
            background: #0d9488;
            border-color: #0d9488;
        }

        QGroupBox {
            font-weight: 600;
            font-size: 13px;
            color: #334155;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            margin-top: 16px;
            padding-top: 28px;
            padding-bottom: 10px;
            padding-left: 4px;
            padding-right: 4px;
            background: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 6px;
            top: 0px;
            padding: 2px 6px 8px 6px;
            color: #0f766e;
            background: transparent;
        }
        QGroupBox QLabel {
            background: transparent;
        }

        QProgressBar {
            border: none;
            border-radius: 6px;
            background: #e2e8f0;
            height: 10px;
            text-align: center;
        }
        QProgressBar::chunk {
            background: #0d9488;
            border-radius: 6px;
        }

        QRadioButton { spacing: 8px; }
        QRadioButton::indicator {
            width: 16px; height: 16px;
            border: 2px solid #cbd5e1;
            border-radius: 9px;
            background: #ffffff;
        }
        QRadioButton::indicator:checked {
            background: #0d9488;
            border-color: #0d9488;
        }

        /* Focus rings */
        QPushButton:focus, QComboBox:focus, QLineEdit:focus, QSpinBox:focus,
        QDoubleSpinBox:focus, QCheckBox:focus, QRadioButton:focus, QTabBar::tab:focus {
            outline: none;
            border: 2px solid #0d9488;
        }
        QPushButton#secondaryButton:focus {
            border: 2px solid #0d9488;
        }
        QPushButton#iconButton:focus {
            border: 2px solid #0d9488;
            color: #0d9488;
        }

        QLabel#mutedLabel {
            color: #64748b;
            font-size: 12px;
            background: transparent;
        }
        QLabel#questionBadge {
            background: #0d9488;
            color: white;
            border-radius: 14px;
            font-weight: 700;
            font-size: 12px;
        }
        QLabel#questionText {
            font-size: 13px;
            font-weight: 600;
            color: #0f172a;
            background: transparent;
        }
        QLabel#optionChip {
            background: #f1f5f9;
            color: #475569;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 12px;
        }
        QLabel#optionChipCorrect {
            background: #d1fae5;
            color: #065f46;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        QFrame#undoBar {
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            border-radius: 8px;
        }
        QFrame#emptyState {
            background: transparent;
            border: none;
        }
        QListWidget#questionList {
            background: transparent;
            border: none;
            outline: none;
        }
        QListWidget#questionList::item {
            background: transparent;
            border: none;
            padding: 0;
            margin: 2px 0;
        }
        QListWidget#questionList::item:selected {
            background: transparent;
        }

        """)

    def apply_dark(self):
        self.main_window.setStyleSheet("""
        * { font-family: "Segoe UI", "Noto Sans", sans-serif; }

        QMainWindow, QWidget {
            background-color: #0f172a;
            color: #e2e8f0;
            font-size: 13px;
        }

        QTabWidget::pane {
            border: none;
            background: #0f172a;
        }

        QTabBar::tab {
            background: transparent;
            color: #94a3b8;
            padding: 12px 28px;
            margin-right: 2px;
            border: none;
            font-size: 14px;
            font-weight: 500;
        }

        QTabBar::tab:selected {
            color: #2dd4bf;
            border-bottom: 3px solid #2dd4bf;
            background: #1e293b;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }

        QTabBar::tab:hover:!selected {
            color: #5eead4;
            background: #1e293b;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }

        QPushButton {
            background-color: #0d9488;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
        }
        QPushButton:hover { background-color: #14b8a6; }
        QPushButton:pressed { background-color: #0f766e; }
        QPushButton:disabled { background-color: #475569; color: #94a3b8; }

        QPushButton#secondaryButton {
            background-color: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            font-weight: 500;
        }
        QPushButton#secondaryButton:hover {
            background-color: #334155;
            border-color: #475569;
        }

        QPushButton#iconButton {
            background-color: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 4px;
            font-size: 14px;
            font-weight: 600;
            min-width: 28px; max-width: 32px;
            min-height: 28px; max-height: 32px;
        }
        QPushButton#iconButton:hover {
            background-color: #134e4a;
            border-color: #2dd4bf;
            color: #2dd4bf;
        }

        QFrame#card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
        }

        QLabel {
            background: transparent;
        }
        QLabel#sectionTitle {
            font-size: 18px;
            font-weight: 700;
            color: #f1f5f9;
            background: transparent;
        }

        QStatusBar {
            background: #1e293b;
            border-top: 1px solid #334155;
            font-size: 12px;
            color: #94a3b8;
        }

        QMenuBar {
            background: #1e293b;
            border-bottom: 1px solid #334155;
            color: #e2e8f0;
        }
        QMenuBar::item:selected { background: #334155; color: #2dd4bf; }

        QMenu {
            background: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
        }
        QMenu::item:selected { background: #334155; color: #2dd4bf; }

        QScrollArea { border: none; background: transparent; }
        QScrollBar:vertical { background: transparent; width: 8px; }
        QScrollBar::handle:vertical {
            background: #475569; border-radius: 4px; min-height: 30px;
        }

        QTextEdit, QPlainTextEdit, QLineEdit {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 8px 12px;
            color: #e2e8f0;
        }
        QTextEdit:focus, QLineEdit:focus { border-color: #2dd4bf; }

        QComboBox {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 6px 12px;
            color: #e2e8f0;
        }

        QSpinBox, QDoubleSpinBox {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 4px 8px;
            color: #e2e8f0;
        }

        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 2px solid #475569;
            border-radius: 4px;
            background: #1e293b;
        }
        QCheckBox::indicator:checked {
            background: #0d9488;
            border-color: #0d9488;
        }

        QGroupBox {
            font-weight: 600;
            color: #94a3b8;
            border: 1px solid #334155;
            border-radius: 10px;
            margin-top: 16px;
            padding-top: 28px;
            padding-bottom: 10px;
            padding-left: 4px;
            padding-right: 4px;
            background: #1e293b;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 6px;
            top: 0px;
            padding: 2px 6px 8px 6px;
            color: #2dd4bf;
            background: transparent;
        }
        QGroupBox QLabel {
            background: transparent;
        }

        QProgressBar {
            border: none;
            border-radius: 6px;
            background: #334155;
            height: 10px;
        }
        QProgressBar::chunk {
            background: #0d9488;
            border-radius: 6px;
        }

        QRadioButton::indicator {
            width: 16px; height: 16px;
            border: 2px solid #475569;
            border-radius: 9px;
            background: #1e293b;
        }
        QRadioButton::indicator:checked {
            background: #0d9488;
            border-color: #0d9488;
        }

        /* Focus rings */
        QPushButton:focus, QComboBox:focus, QLineEdit:focus, QSpinBox:focus,
        QDoubleSpinBox:focus, QCheckBox:focus, QRadioButton:focus, QTabBar::tab:focus {
            outline: none;
            border: 2px solid #2dd4bf;
        }
        QPushButton#secondaryButton:focus {
            border: 2px solid #2dd4bf;
        }
        QPushButton#iconButton:focus {
            border: 2px solid #2dd4bf;
            color: #2dd4bf;
        }

        QLabel#mutedLabel {
            color: #94a3b8;
            font-size: 12px;
            background: transparent;
        }
        QLabel#questionBadge {
            background: #0d9488;
            color: white;
            border-radius: 14px;
            font-weight: 700;
            font-size: 12px;
        }
        QLabel#questionText {
            font-size: 13px;
            font-weight: 600;
            color: #e2e8f0;
            background: transparent;
        }
        QLabel#optionChip {
            background: #334155;
            color: #cbd5e1;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 12px;
        }
        QLabel#optionChipCorrect {
            background: #064e3b;
            color: #6ee7b7;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        QFrame#undoBar {
            background: #134e4a;
            border: 1px solid #0d9488;
            border-radius: 8px;
        }
        QFrame#emptyState {
            background: transparent;
            border: none;
        }
        QListWidget#questionList {
            background: transparent;
            border: none;
            outline: none;
        }
        QListWidget#questionList::item {
            background: transparent;
            border: none;
            padding: 0;
            margin: 2px 0;
        }
        QListWidget#questionList::item:selected {
            background: transparent;
        }

        """)
