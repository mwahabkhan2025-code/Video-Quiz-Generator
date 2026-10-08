from pathlib import Path
"""
Preview Panel - Clean professional layout.
Toolbar on top, aspect-ratio canvas centered below.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QFontDatabase

_FONTS = Path(__file__).resolve().parent.parent / "resources" / "fonts"
_TAMIL_FONT = str(_FONTS / "NotoSansTamil-Regular.ttf") if (_FONTS / "NotoSansTamil-Regular.ttf").exists() else None
_TAMIL_BOLD = str(_FONTS / "NotoSansTamil-Bold.ttf") if (_FONTS / "NotoSansTamil-Bold.ttf").exists() else None


def _has_tamil(text: str) -> bool:
    return any("஀" <= ch <= "௿" for ch in (text or ""))


_tamil_family_cache = None

def _ensure_tamil_family():
    global _tamil_family_cache
    if _tamil_family_cache is not None:
        return _tamil_family_cache
    path = _TAMIL_FONT or _TAMIL_BOLD
    if not path:
        _tamil_family_cache = ""
        return ""
    try:
        fid = QFontDatabase.addApplicationFont(path)
        if fid >= 0:
            fams = QFontDatabase.applicationFontFamilies(fid)
            if fams:
                _tamil_family_cache = fams[0]
                return _tamil_family_cache
    except Exception:
        pass
    _tamil_family_cache = "Noto Sans Tamil"
    return _tamil_family_cache


def app_font(size: int, bold: bool = False, sample: str = "") -> QFont:
    """Prefer Noto Sans Tamil when text contains Tamil glyphs."""
    weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
    if sample and _has_tamil(sample):
        family = _ensure_tamil_family() or "Noto Sans Tamil"
        f = QFont(family)
        f.setPixelSize(max(8, size))
        f.setWeight(weight)
        return f
    f = QFont("Segoe UI")
    f.setPixelSize(max(8, size))
    f.setWeight(weight)
    return f



from core.mcq_parser import MCQ
from core.design_config import DesignConfig
from typing import List, Optional


class PreviewCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(480, 270)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.format = "youtube"
        self.mcq: Optional[MCQ] = None
        self.question_index = 0
        self.total_questions = 0
        self.config = DesignConfig()
        self.show_mode = "question"

    def set_format(self, fmt: str):
        self.format = fmt
        self.updateGeometry()
        self.update()

    def set_config(self, config: DesignConfig):
        self.config = config
        self.update()

    def set_mcq(self, mcq, index=0, total=0):
        self.mcq = mcq
        self.question_index = index
        self.total_questions = total
        self.update()

    def set_show_mode(self, mode: str):
        self.show_mode = mode
        self.update()

    def heightForWidth(self, w):
        if self.format == "youtube":
            return int(w * 9 / 16)
        return int(w * 16 / 9)

    def hasHeightForWidth(self):
        return True

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cfg = self.config

        # letterbox: draw content in correct aspect rect centered
        if self.format == "youtube":
            target_ratio = 16 / 9
        else:
            target_ratio = 9 / 16

        if w / max(h, 1) > target_ratio:
            cw = int(h * target_ratio)
            ch = h
        else:
            cw = w
            ch = int(w / target_ratio)
        ox = (w - cw) // 2
        oy = (h - ch) // 2

        # outer background (letterbox)
        p.fillRect(0, 0, w, h, QColor("#e2e8f0"))

        # content area
        bg = QColor(cfg.background.color)
        p.fillRect(ox, oy, cw, ch, bg)
        if cfg.background.type == "gradient":
            g = QLinearGradient(ox, oy, ox, oy + ch)
            g.setColorAt(0, QColor(cfg.background.color))
            g.setColorAt(1, QColor(cfg.background.color2))
            p.fillRect(ox, oy, cw, ch, g)

        p.translate(ox, oy)
        if self.show_mode == "intro":
            bg = getattr(cfg.intro, "background_color", None) or cfg.background.color
            p.fillRect(0, 0, cw, ch, QColor(bg))
            self._draw_title_screen(
                p, cw, ch, cfg.intro.title, cfg.intro.subtitle,
                cfg.intro.title_color,
                getattr(cfg.intro, "subtitle_color", "#94a3b8"),
                "Intro",
                title_size=getattr(cfg.intro, "title_size", 48),
                subtitle_size=getattr(cfg.intro, "subtitle_size", 24),
            )
        elif self.show_mode == "outro":
            bg = getattr(cfg.outro, "background_color", None) or cfg.background.color
            p.fillRect(0, 0, cw, ch, QColor(bg))
            self._draw_title_screen(
                p, cw, ch, cfg.outro.title, cfg.outro.subtitle,
                getattr(cfg.outro, "title_color", "#ffffff"),
                getattr(cfg.outro, "subtitle_color", "#94a3b8"),
                "Outro",
                title_size=getattr(cfg.outro, "title_size", 40),
                subtitle_size=getattr(cfg.outro, "subtitle_size", 22),
            )
        else:
            self._draw_question(p, cw, ch)
        p.end()

    def _draw_title_screen(self, p, w, h, title, subtitle, color, sub_color, badge,
                           title_size=48, subtitle_size=24):
        p.setPen(QPen(QColor("#0d9488")))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.drawText(16, 28, badge)

        # Map design sizes (tuned for 1920px video) into live preview width
        scale = w / 1920.0
        t_px = max(12, int((title_size or 48) * scale))
        s_px = max(10, int((subtitle_size or 24) * scale))

        p.setPen(QPen(QColor(color)))
        p.setFont(app_font(t_px, bold=True, sample=title))
        p.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, title)

        p.setPen(QPen(QColor(sub_color or "#94a3b8")))
        p.setFont(app_font(s_px, sample=subtitle))
        p.drawText(0, int(h * 0.58), w, max(40, s_px + 16), Qt.AlignmentFlag.AlignCenter, subtitle)

    def _draw_question(self, p, w, h):
        cfg = self.config
        margin = int(w * 0.05)
        card_x, card_w = margin, w - 2 * margin
        card_y, card_h = int(h * 0.08), int(h * 0.84)

        card_fill = getattr(cfg, "card_bg", None) or "#1e293b"
        p.setBrush(QBrush(QColor(card_fill)))
        p.setPen(Qt.PenStyle.NoPen)
        r = cfg.border.radius if cfg.border.enabled else 10
        p.drawRoundedRect(card_x, card_y, card_w, card_h, r, r)

        if cfg.border.enabled:
            pen = QPen(QColor(cfg.border.color), max(1, cfg.border.thickness))
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(card_x, card_y, card_w, card_h, r, r)

        label = "YouTube 16:9" if self.format == "youtube" else "Reel 9:16"
        p.setPen(QPen(QColor(cfg.border.color)))
        p.setFont(QFont("Segoe UI", max(8, int(w * 0.015)), QFont.Weight.Bold))
        p.drawText(card_x + 14, card_y + 22, label)

        if self.total_questions > 0:
            p.setPen(QPen(QColor("#94a3b8")))
            p.setFont(QFont("Segoe UI", max(8, int(w * 0.015))))
            p.drawText(card_x + card_w - 60, card_y + 22,
                       f"{self.question_index + 1}/{self.total_questions}")

        if not self.mcq:
            p.setPen(QPen(QColor("#64748b")))
            p.setFont(QFont("Segoe UI", 13))
            p.drawText(card_x, card_y, card_w, card_h,
                       Qt.AlignmentFlag.AlignCenter, "Load questions to preview")
            return

        qy = card_y + 40
        weight = QFont.Weight.Bold if cfg.question.bold else QFont.Weight.Normal
        fs = max(11, int(cfg.question.font_size * 0.45))
        p.setPen(QPen(QColor(cfg.question.color)))
        p.setFont(app_font(fs, bold=cfg.question.bold, sample=self.mcq.question))
        qr = p.boundingRect(card_x + 16, qy, card_w - 32, int(h * 0.22),
                            Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                            self.mcq.question)
        p.drawText(qr, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                   self.mcq.question)

        oy = qr.bottom() + 16
        oh = max(28, int(h * 0.07))
        gap = 8
        afs = max(10, int(cfg.answers.font_size * 0.45))
        for i, opt in enumerate(self.mcq.options):
            letter = chr(65 + i)
            ok = letter == self.mcq.correct
            y = oy + i * (oh + gap)
            if y + oh > card_y + card_h - 12:
                break
            bg = QColor(cfg.correct_bg) if ok else QColor(cfg.option_bg)
            p.setBrush(QBrush(bg))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(card_x + 16, y, card_w - 32, oh, 6, 6)
            p.setPen(QPen(QColor("#ffffff" if ok else cfg.answers.color)))
            p.setFont(app_font(afs, sample=opt))
            p.drawText(card_x + 28, y, card_w - 48, oh,
                       Qt.AlignmentFlag.AlignVCenter, f"{letter}) {opt}")


class PreviewPanel(QWidget):
    format_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mcqs: List[MCQ] = []
        self.current_index = 0
        self.config = DesignConfig()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Header
        head = QHBoxLayout()
        t = QLabel("Live Preview")
        t.setObjectName("sectionTitle")
        head.addWidget(t)
        head.addStretch()
        self.btn_prev = QPushButton("← Prev")
        self.btn_prev.setObjectName("secondaryButton")
        self.btn_prev.clicked.connect(self._prev)
        head.addWidget(self.btn_prev)
        self.lbl_nav = QLabel("—")
        head.addWidget(self.lbl_nav)
        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("secondaryButton")
        self.btn_next.clicked.connect(self._next)
        head.addWidget(self.btn_next)
        layout.addLayout(head)

        # Toolbar
        bar = QHBoxLayout()
        bar.setSpacing(6)
        self.btn_yt = QPushButton("YouTube 16:9")
        self.btn_yt.setCheckable(True)
        self.btn_yt.setChecked(True)
        self.btn_yt.clicked.connect(lambda: self._fmt("youtube"))
        bar.addWidget(self.btn_yt)

        self.btn_reel = QPushButton("Reel 9:16")
        self.btn_reel.setCheckable(True)
        self.btn_reel.setObjectName("secondaryButton")
        self.btn_reel.clicked.connect(lambda: self._fmt("reel"))
        bar.addWidget(self.btn_reel)

        bar.addSpacing(12)
        self.btn_q = QPushButton("Question")
        self.btn_q.setCheckable(True)
        self.btn_q.setChecked(True)
        self.btn_q.clicked.connect(lambda: self._mode("question"))
        bar.addWidget(self.btn_q)

        self.btn_intro = QPushButton("Intro")
        self.btn_intro.setCheckable(True)
        self.btn_intro.setObjectName("secondaryButton")
        self.btn_intro.clicked.connect(lambda: self._mode("intro"))
        bar.addWidget(self.btn_intro)

        self.btn_outro = QPushButton("Outro")
        self.btn_outro.setCheckable(True)
        self.btn_outro.setObjectName("secondaryButton")
        self.btn_outro.clicked.connect(lambda: self._mode("outro"))
        bar.addWidget(self.btn_outro)

        bar.addStretch()
        self.lbl_res = QLabel("1920 × 1080")
        self.lbl_res.setStyleSheet("color:#64748b;font-size:12px;")
        bar.addWidget(self.lbl_res)
        layout.addLayout(bar)

        # Canvas frame
        frame = QFrame()
        frame.setObjectName("card")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(8, 8, 8, 8)
        self.canvas = PreviewCanvas()
        fl.addWidget(self.canvas)
        layout.addWidget(frame, 1)

        hint = QLabel("Styles update from the Design tab. Use Question / Intro / Outro to switch screens.")
        hint.setStyleSheet("color:#64748b;font-size:12px;")
        layout.addWidget(hint)

    def set_mcqs(self, mcqs):
        self.mcqs = mcqs or []
        self.current_index = 0
        self._refresh()

    def set_config(self, config):
        self.config = config
        self.canvas.set_config(config)
        if self.mcqs:
            self.canvas.set_mcq(
                self.mcqs[self.current_index],
                self.current_index,
                len(self.mcqs),
            )

    def _fmt(self, fmt):
        self.canvas.set_format(fmt)
        self.btn_yt.setChecked(fmt == "youtube")
        self.btn_reel.setChecked(fmt == "reel")
        self.btn_yt.setObjectName("" if fmt == "youtube" else "secondaryButton")
        self.btn_reel.setObjectName("" if fmt == "reel" else "secondaryButton")
        for b in (self.btn_yt, self.btn_reel):
            b.style().unpolish(b)
            b.style().polish(b)
        self.lbl_res.setText("1920 × 1080" if fmt == "youtube" else "1080 × 1920")
        self.format_changed.emit(fmt)

    def _mode(self, mode):
        self.canvas.set_show_mode(mode)
        for btn, m in [(self.btn_q, "question"), (self.btn_intro, "intro"), (self.btn_outro, "outro")]:
            btn.setObjectName("" if mode == m else "secondaryButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _refresh(self):
        n = len(self.mcqs)
        if n == 0:
            self.canvas.set_mcq(None)
            self.lbl_nav.setText("No questions")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return
        self.current_index = max(0, min(self.current_index, n - 1))
        self.canvas.set_mcq(self.mcqs[self.current_index], self.current_index, n)
        self.canvas.set_config(self.config)
        self.lbl_nav.setText(f"{self.current_index + 1} / {n}")
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < n - 1)

    def _prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._refresh()

    def _next(self):
        if self.current_index < len(self.mcqs) - 1:
            self.current_index += 1
            self._refresh()
