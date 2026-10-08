"""
Frame renderer using Qt (HarfBuzz) so Tamil / complex scripts shape correctly.
Matches the Live Preview look.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, QRect, QRectF, QPointF
from PyQt6.QtGui import (
    QImage, QPainter, QColor, QFont, QFontDatabase, QPen, QBrush,
    QLinearGradient, QPainterPath,
)
from PyQt6.QtWidgets import QApplication

from core.design_config import DesignConfig
from core.mcq_parser import MCQ

_FONTS_DIR = Path(__file__).resolve().parent.parent / "resources" / "fonts"
_TAMIL_REG = _FONTS_DIR / "NotoSansTamil-Regular.ttf"
_TAMIL_BOLD = _FONTS_DIR / "NotoSansTamil-Bold.ttf"

_tamil_family: Optional[str] = None
_fonts_loaded = False


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def _load_fonts() -> None:
    global _fonts_loaded, _tamil_family
    if _fonts_loaded:
        return
    _ensure_app()
    for path in (_TAMIL_REG, _TAMIL_BOLD):
        if path.exists():
            fid = QFontDatabase.addApplicationFont(str(path.resolve()))
            if fid >= 0 and _tamil_family is None:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    _tamil_family = fams[0]
    _fonts_loaded = True


def _has_tamil(text: str) -> bool:
    return any("\u0b80" <= ch <= "\u0bff" for ch in (text or ""))


def _qfont(size: int, bold: bool = False, sample: str = "") -> QFont:
    _load_fonts()
    weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
    if sample and _has_tamil(sample) and _tamil_family:
        f = QFont(_tamil_family)
    else:
        f = QFont("Segoe UI")
        if _tamil_family:
            f.setFamilies([_tamil_family, "Segoe UI", "Arial", "Noto Sans"])
    f.setPixelSize(max(10, int(size)))
    f.setWeight(weight)
    return f


def _qc(hex_color: str) -> QColor:
    c = (hex_color or "#000000").strip()
    if not c.startswith("#"):
        c = "#" + c
    qc = QColor(c)
    if not qc.isValid():
        return QColor("#0f172a")
    return qc


def _rounded_rect_path(x, y, w, h, r) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(QRectF(x, y, w, h), r, r)
    return path


def _fill_background(p: QPainter, width: int, height: int, config: DesignConfig) -> None:
    bg = config.background
    if getattr(bg, "type", "solid") == "gradient":
        g = QLinearGradient(0, 0, 0, height)
        g.setColorAt(0, _qc(bg.color))
        g.setColorAt(1, _qc(getattr(bg, "color2", bg.color)))
        p.fillRect(0, 0, width, height, g)
    else:
        p.fillRect(0, 0, width, height, _qc(bg.color))


def render_intro_frame(
    width: int, height: int, config: DesignConfig
) -> QImage:
    _ensure_app()
    img = QImage(width, height, QImage.Format.Format_RGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    bg = getattr(config.intro, "background_color", None) or "#0f172a"
    p.fillRect(0, 0, width, height, _qc(bg))

    # Center card
    margin_x = int(width * 0.12)
    card_w = width - 2 * margin_x
    card_h = int(height * 0.42)
    card_x = margin_x
    card_y = (height - card_h) // 2
    r = max(12, getattr(config.border, "radius", 16))

    p.setBrush(QBrush(_qc(getattr(config, "card_bg", None) or "#1e293b")))
    p.setPen(QPen(_qc(config.border.color), max(2, config.border.thickness)))
    p.drawRoundedRect(card_x, card_y, card_w, card_h, r, r)

    title = config.intro.title or "Quiz Time!"
    subtitle = config.intro.subtitle or "Test your knowledge"
    title_color = getattr(config.intro, "title_color", "#ffffff")
    sub_color = getattr(config.intro, "subtitle_color", "#94a3b8")

    scale = width / 1920.0
    title_size = max(18, int(getattr(config.intro, "title_size", 48) * scale))
    sub_size = max(12, int(getattr(config.intro, "subtitle_size", 24) * scale))

    p.setPen(_qc(title_color))
    p.setFont(_qfont(title_size, bold=True, sample=title))
    title_rect = QRect(card_x + 24, card_y, card_w - 48, int(card_h * 0.55))
    p.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, title)

    p.setPen(_qc(sub_color))
    p.setFont(_qfont(sub_size, sample=subtitle))
    sub_rect = QRect(card_x + 24, card_y + int(card_h * 0.55), card_w - 48, int(card_h * 0.35))
    p.drawText(sub_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, subtitle)

    # Optional school / channel logo above the card
    if getattr(config.intro, "show_logo", False) and getattr(config.intro, "logo_path", ""):
        logo_file = Path(config.intro.logo_path)
        if logo_file.exists():
            logo = QImage(str(logo_file))
            if not logo.isNull():
                max_w = int(width * 0.18)
                max_h = int(height * 0.12)
                logo = logo.scaled(
                    max_w, max_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                lx = (width - logo.width()) // 2
                ly = max(16, card_y - logo.height() - int(20 * scale))
                p.drawImage(lx, ly, logo)

    p.end()
    return img


def render_outro_frame(
    width: int, height: int, config: DesignConfig
) -> QImage:
    _ensure_app()
    img = QImage(width, height, QImage.Format.Format_RGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    bg = getattr(config.outro, "background_color", None) or "#0f172a"
    p.fillRect(0, 0, width, height, _qc(bg))

    margin_x = int(width * 0.12)
    card_w = width - 2 * margin_x
    card_h = int(height * 0.42)
    card_x = margin_x
    card_y = (height - card_h) // 2
    r = max(12, getattr(config.border, "radius", 16))

    p.setBrush(QBrush(_qc(getattr(config, "card_bg", None) or "#1e293b")))
    p.setPen(QPen(_qc(config.border.color), max(2, config.border.thickness)))
    p.drawRoundedRect(card_x, card_y, card_w, card_h, r, r)

    title = config.outro.title or "Thanks for watching!"
    subtitle = config.outro.subtitle or "Subscribe for more quizzes"
    title_color = getattr(config.outro, "title_color", "#ffffff")
    sub_color = getattr(config.outro, "subtitle_color", "#94a3b8")

    scale = width / 1920.0
    title_size = max(18, int(getattr(config.outro, "title_size", 40) * scale))
    sub_size = max(12, int(getattr(config.outro, "subtitle_size", 22) * scale))

    p.setPen(_qc(title_color))
    p.setFont(_qfont(title_size, bold=True, sample=title))
    title_rect = QRect(card_x + 24, card_y, card_w - 48, int(card_h * 0.55))
    p.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, title)

    p.setPen(_qc(sub_color))
    p.setFont(_qfont(sub_size, sample=subtitle))
    sub_rect = QRect(card_x + 24, card_y + int(card_h * 0.55), card_w - 48, int(card_h * 0.35))
    p.drawText(sub_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, subtitle)

    p.end()
    return img


def render_question_frame(
    width: int,
    height: int,
    config: DesignConfig,
    mcq: MCQ,
    index: int,
    total: int,
    highlight_correct: bool = False,
    highlight_option: Optional[int] = None,
    countdown_seconds: Optional[int] = None,
) -> QImage:
    _ensure_app()
    img = QImage(width, height, QImage.Format.Format_RGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    _fill_background(p, width, height, config)

    scale = width / 1920.0
    margin = int(width * 0.05)
    card_x, card_w = margin, width - 2 * margin
    card_y, card_h = int(height * 0.08), int(height * 0.84)
    r = config.border.radius if config.border.enabled else 12

    # Card (themeable — supports light & dark themes)
    card_fill = getattr(config, "card_bg", None) or "#1e293b"
    p.setBrush(QBrush(_qc(card_fill)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(card_x, card_y, card_w, card_h, r, r)

    if config.border.enabled:
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_qc(config.border.color), max(2, config.border.thickness)))
        p.drawRoundedRect(card_x, card_y, card_w, card_h, r, r)

    # Question counter only (no format badge burned into the video)
    badge_size = max(14, int(18 * scale))
    counter = f"{index + 1}/{total}"
    p.setPen(_qc("#94a3b8"))
    p.setFont(_qfont(badge_size, bold=True))
    fm = p.fontMetrics()
    cw = fm.horizontalAdvance(counter)
    p.drawText(card_x + card_w - 24 - cw, card_y + 18 + badge_size, counter)

    # Question
    q_size = max(22, int(config.question.font_size * scale * 0.95))
    p.setPen(_qc(config.question.color))
    p.setFont(_qfont(q_size, bold=config.question.bold, sample=mcq.question))
    q_top = card_y + 36
    q_rect = QRect(card_x + 24, q_top, card_w - 48, int(height * 0.22))
    br = p.boundingRect(
        q_rect,
        Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
        mcq.question,
    )
    p.drawText(br, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, mcq.question)

    # Options
    opt_size = max(18, int(config.answers.font_size * scale * 0.95))
    opt_h = max(44, int(height * 0.075))
    gap = max(10, int(12 * scale))
    y = br.bottom() + 24
    opt_left = card_x + 24
    opt_w = card_w - 48

    for i, opt in enumerate(mcq.options[:4]):
        letter = chr(65 + i)
        label = f"{letter}) {opt}"
        is_correct = letter == mcq.correct

        if highlight_correct and is_correct:
            bg = _qc(config.correct_bg)
            fg = QColor("#ffffff")
        elif highlight_option is not None and i == highlight_option:
            bg = _qc(config.border.color)
            fg = QColor("#ffffff")
        else:
            bg = _qc(config.option_bg)
            fg = _qc(config.answers.color)

        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(opt_left, y, opt_w, opt_h, 10, 10)

        p.setPen(fg)
        p.setFont(_qfont(opt_size, sample=opt))
        p.drawText(
            QRect(opt_left + 20, y, opt_w - 40, opt_h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            label,
        )
        y += opt_h + gap

    # Countdown clock below options (think time after all answers)
    if countdown_seconds is not None and countdown_seconds >= 0:
        clock_size = max(28, int(42 * scale))
        secs = int(countdown_seconds)
        mins, sec = divmod(secs, 60)
        clock_text = f"{mins}:{sec:02d}" if mins else f"{sec}"
        # Circular badge
        cx = card_x + card_w // 2
        cy = min(y + int(28 * scale), card_y + card_h - int(50 * scale))
        radius = max(22, int(32 * scale))
        p.setBrush(QBrush(_qc("#0f172a")))
        p.setPen(QPen(_qc(config.border.color), max(2, int(3 * scale))))
        p.drawEllipse(QPointF(cx, cy), radius, radius)
        p.setPen(_qc("#f8fafc"))
        p.setFont(_qfont(clock_size, bold=True))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(clock_text)
        th = fm.height()
        p.drawText(int(cx - tw / 2), int(cy + th / 3), clock_text)

    p.end()
    return img


def save_frame(image: QImage, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path), "PNG"):
        raise RuntimeError(f"Failed to save frame: {path}")



def render_title_screen(
    width: int,
    height: int,
    config: DesignConfig,
    title: str,
    subtitle: str,
    title_color: str = "#ffffff",
    background_color: str = "",
    subtitle_color: str = "#94a3b8",
    title_size: int = 0,
) -> QImage:
    """Generic title card (intro / outro)."""
    _ensure_app()
    img = QImage(width, height, QImage.Format.Format_RGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    if background_color:
        p.fillRect(0, 0, width, height, _qc(background_color))
    else:
        _fill_background(p, width, height, config)

    margin_x = int(width * 0.12)
    card_w = width - 2 * margin_x
    card_h = int(height * 0.42)
    card_x = margin_x
    card_y = (height - card_h) // 2
    r = max(12, getattr(config.border, "radius", 16))

    p.setBrush(QBrush(_qc(getattr(config, "card_bg", None) or "#1e293b")))
    p.setPen(QPen(_qc(config.border.color), max(2, config.border.thickness)))
    p.drawRoundedRect(card_x, card_y, card_w, card_h, r, r)

    scale = width / 1920.0
    t_size = max(18, int((title_size or 52) * scale))
    sub_size = max(12, int(26 * scale))

    p.setPen(_qc(title_color or "#ffffff"))
    p.setFont(_qfont(t_size, bold=True, sample=title or ""))
    title_rect = QRect(card_x + 24, card_y, card_w - 48, int(card_h * 0.55))
    p.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, title or "")

    p.setPen(_qc(subtitle_color or "#94a3b8"))
    p.setFont(_qfont(sub_size, sample=subtitle or ""))
    sub_rect = QRect(card_x + 24, card_y + int(card_h * 0.55), card_w - 48, int(card_h * 0.35))
    p.drawText(sub_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, subtitle or "")

    p.end()
    return img


# Back-compat aliases used by tests / older code
def draw_intro_frame(*args, **kwargs):
    return render_intro_frame(*args, **kwargs)


def draw_outro_frame(*args, **kwargs):
    return render_outro_frame(*args, **kwargs)


def draw_question_frame(*args, **kwargs):
    return render_question_frame(*args, **kwargs)
