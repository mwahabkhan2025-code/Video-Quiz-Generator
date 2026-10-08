"""
Visual theme gallery — clickable color previews for templates.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QBrush, QPen, QFont, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QGridLayout, QFrame, QPushButton, QSizePolicy, QLineEdit,
)

from core.templates import TEMPLATES, QUESTION_THEME_NAMES
from core.design_config import DesignConfig


def _swatch_pixmap(cfg: DesignConfig, w: int = 160, h: int = 100) -> QPixmap:
    """Mini preview of a theme (bg + card + accent)."""
    pm = QPixmap(w, h)
    pm.fill(QColor("#0f172a"))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    bg1 = QColor(getattr(cfg.background, "color", None) or "#0f172a")
    bg2 = QColor(getattr(cfg.background, "color2", None) or bg1.name())
    grad = QLinearGradient(0, 0, w, h)
    grad.setColorAt(0, bg1)
    grad.setColorAt(1, bg2)
    p.fillRect(0, 0, w, h, QBrush(grad))

    card = QColor(getattr(cfg, "card_bg", None) or "#1e293b")
    margin = 12
    cw, ch = w - 2 * margin, h - 2 * margin - 8
    p.setBrush(QBrush(card))
    border = QColor(getattr(cfg.border, "color", None) or "#0d9488")
    p.setPen(QPen(border, 2))
    p.drawRoundedRect(margin, margin, cw, ch, 10, 10)

    # Sample question line
    p.setPen(QColor(getattr(cfg.question, "color", None) or "#f8fafc"))
    p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    p.drawText(margin + 10, margin + 22, "Question text")

    # Option chips
    opt_bg = QColor(getattr(cfg, "option_bg", None) or "#334155")
    correct = QColor(getattr(cfg, "correct_bg", None) or "#0d9488")
    ans = QColor(getattr(cfg.answers, "color", None) or "#e2e8f0")
    y = margin + 34
    for i, label in enumerate(("A  Option", "B  Correct")):
        bg = correct if i == 1 else opt_bg
        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(margin + 10, y, cw - 20, 18, 4, 4)
        p.setPen(QColor("#ffffff") if i == 1 else ans)
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(margin + 16, y + 13, label)
        y += 22

    p.end()
    return pm


class ThemeCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, name: str, cfg: DesignConfig, parent=None):
        super().__init__(parent)
        self.name = name
        self.setObjectName("themeCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(150, 128)
        self.setStyleSheet(
            "QFrame#themeCard {"
            "  background: #ffffff; border: 2px solid #e2e8f0; border-radius: 10px;"
            "}"
            "QFrame#themeCard:hover { border-color: #0d9488; }"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        self.preview = QLabel()
        self.preview.setFixedSize(138, 88)
        self.preview.setPixmap(_swatch_pixmap(cfg, 138, 88))
        self.preview.setScaledContents(True)
        lay.addWidget(self.preview, 0, Qt.AlignmentFlag.AlignCenter)

        title = QLabel(name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #334155; background: transparent;"
        )
        title.setWordWrap(True)
        lay.addWidget(title)

        self._selected = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.name)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.setStyleSheet(
                "QFrame#themeCard {"
                "  background: #f0fdfa; border: 2px solid #0d9488; border-radius: 10px;"
                "}"
            )
        else:
            self.setStyleSheet(
                "QFrame#themeCard {"
                "  background: #ffffff; border: 2px solid #e2e8f0; border-radius: 10px;"
                "}"
                "QFrame#themeCard:hover { border-color: #0d9488; }"
            )


class ThemeGallery(QWidget):
    """Scrollable grid of theme previews."""
    theme_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: Dict[str, ThemeCard] = {}
        self._current = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Search / filter
        top = QHBoxLayout()
        top.addWidget(QLabel("Theme gallery"))
        top.addStretch()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter themes…")
        self.search.setMaximumWidth(180)
        self.search.textChanged.connect(self._filter)
        top.addWidget(self.search)
        root.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(host)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setSpacing(10)
        scroll.setWidget(host)
        root.addWidget(scroll, 1)

        self._build_cards()

    def _build_cards(self):
        # Clear
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._cards.clear()

        names = list(TEMPLATES.keys())
        cols = 2
        row = col = 0
        for name in names:
            factory = TEMPLATES[name]
            try:
                cfg = factory() if callable(factory) else DesignConfig()
            except Exception:
                cfg = DesignConfig()
            card = ThemeCard(name, cfg)
            card.clicked.connect(self._on_click)
            self.grid.addWidget(card, row, col)
            self._cards[name] = card
            col += 1
            if col >= cols:
                col = 0
                row += 1
        self.grid.setRowStretch(row + 1, 1)

    def _on_click(self, name: str):
        self.set_current(name)
        self.theme_selected.emit(name)

    def set_current(self, name: str):
        self._current = name
        for n, card in self._cards.items():
            card.set_selected(n == name)

    def _filter(self, text: str):
        q = (text or "").strip().lower()
        for name, card in self._cards.items():
            card.setVisible(not q or q in name.lower())
