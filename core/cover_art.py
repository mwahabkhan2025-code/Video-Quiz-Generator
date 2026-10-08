"""YouTube cover art (1280x720) from project meta + theme colors."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QRect, QRectF
from PyQt6.QtGui import (
    QImage, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QPixmap,
)


def _cfg_get(cover: Any, key: str, default):
    if cover is None:
        return default
    if isinstance(cover, dict):
        return cover.get(key, default)
    return getattr(cover, key, default)


def _h_align(align: str):
    a = (align or "center").lower()
    if a == "left":
        return Qt.AlignmentFlag.AlignLeft
    if a == "right":
        return Qt.AlignmentFlag.AlignRight
    return Qt.AlignmentFlag.AlignHCenter


def render_youtube_cover(
    out_path: str | Path | None = None,
    *,
    title: str = "Class Quiz",
    subject: str = "",
    class_name: str = "",
    lesson: str = "",
    school: str = "",
    question_count: int = 0,
    show_question_count: bool = True,
    accent: str = "#0d9488",
    bg1: str = "#0f172a",
    bg2: str = "#1e293b",
    title_color: str = "#ffffff",
    subtitle_color: str = "#94a3b8",
    meta_color: str = "#e2e8f0",
    title_size: int = 42,
    lesson_size: int = 22,
    meta_size: int = 18,
    font_family: str = "Segoe UI",
    text_align: str = "center",
    logo_path: str = "",
    width: int = 1280,
    height: int = 720,
    cover: Any = None,
) -> Path | QImage:
    """Render cover to file (if out_path) or return QImage when out_path is None."""
    if cover is not None:
        title = _cfg_get(cover, "title", title) or title
        subject = _cfg_get(cover, "subject", subject) or ""
        class_name = _cfg_get(cover, "class_name", class_name) or ""
        lesson = _cfg_get(cover, "lesson", lesson) or ""
        school = _cfg_get(cover, "school", school) or ""
        show_question_count = bool(_cfg_get(cover, "show_question_count", show_question_count))
        accent = _cfg_get(cover, "accent_color", accent) or accent
        bg1 = _cfg_get(cover, "background_color", bg1) or bg1
        bg2 = _cfg_get(cover, "background_color2", bg2) or bg2
        title_color = _cfg_get(cover, "title_color", title_color) or title_color
        subtitle_color = _cfg_get(cover, "subtitle_color", subtitle_color) or subtitle_color
        meta_color = _cfg_get(cover, "meta_color", meta_color) or meta_color
        title_size = int(_cfg_get(cover, "title_size", title_size) or title_size)
        lesson_size = int(_cfg_get(cover, "lesson_size", lesson_size) or lesson_size)
        meta_size = int(_cfg_get(cover, "meta_size", meta_size) or meta_size)
        font_family = _cfg_get(cover, "font_family", font_family) or font_family
        text_align = _cfg_get(cover, "text_align", text_align) or text_align
        if _cfg_get(cover, "show_logo", False):
            logo_path = _cfg_get(cover, "logo_path", logo_path) or logo_path
        elif not logo_path:
            logo_path = ""

    align = _h_align(text_align)
    margin = 64
    content_w = width - 2 * margin

    img = QImage(width, height, QImage.Format.Format_RGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    grad = QLinearGradient(0, 0, width, height)
    grad.setColorAt(0, QColor(bg1))
    grad.setColorAt(1, QColor(bg2))
    p.fillRect(0, 0, width, height, QBrush(grad))

    # Accent bar always on left edge (branding)
    p.fillRect(0, 0, 12, height, QColor(accent))

    # Logo top — follow horizontal alignment
    logo_h = 0
    if logo_path and Path(logo_path).exists():
        logo = QImage(str(logo_path))
        if not logo.isNull():
            lw = 100
            logo_h = int(logo.height() * (lw / max(1, logo.width())))
            if text_align == "right":
                lx = width - margin - lw
            elif text_align == "center":
                lx = (width - lw) // 2
            else:
                lx = margin
            p.drawImage(QRect(lx, 40, lw, logo_h), logo)

    # Measure block heights to vertically center the main stack
    chips = [c for c in (class_name, subject) if c]
    chip_h = 36 if chips else 0
    chip_gap = 12

    p.setFont(QFont(font_family, max(12, title_size), QFont.Weight.Bold))
    title_rect = QRect(0, 0, content_w, 200)
    title_br = p.boundingRect(
        title_rect,
        int(align | Qt.TextFlag.TextWordWrap),
        title or "Class Quiz",
    )
    title_h = max(title_br.height(), int(title_size * 1.2))

    lesson_h = 0
    if lesson:
        p.setFont(QFont(font_family, max(10, lesson_size)))
        lr = p.boundingRect(
            QRect(0, 0, content_w, 80),
            int(align | Qt.TextFlag.TextWordWrap),
            lesson,
        )
        lesson_h = max(lr.height(), lesson_size + 8)

    meta_h = (meta_size + 12) if (show_question_count and question_count) else 0
    school_h = 28 if school else 0
    accent_line_h = 16
    gap = 20

    block_h = chip_h + (gap if chips else 0) + title_h + gap
    if lesson:
        block_h += lesson_h + gap
    if meta_h:
        block_h += meta_h + 8
    block_h += accent_line_h
    if school_h:
        block_h += school_h + 8

    # Vertical center (leave room for logo if present)
    top_pad = 40 + (logo_h + 16 if logo_h else 0)
    y = max(top_pad, (height - block_h) // 2)

    # Chips
    if chips:
        p.setFont(QFont(font_family, 14, QFont.Weight.Bold))
        widths = []
        for chip in chips:
            fm = p.fontMetrics()
            widths.append(fm.horizontalAdvance(chip) + 28)
        total_chips_w = sum(widths) + chip_gap * (len(chips) - 1)
        if text_align == "right":
            chip_x = width - margin - total_chips_w
        elif text_align == "center":
            chip_x = (width - total_chips_w) // 2
        else:
            chip_x = margin
        for chip, tw in zip(chips, widths):
            p.setBrush(QBrush(QColor(accent)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(chip_x, y, tw, chip_h, 8, 8)
            p.setPen(QColor("#ffffff"))
            p.drawText(QRect(chip_x, y, tw, chip_h), Qt.AlignmentFlag.AlignCenter, chip)
            chip_x += tw + chip_gap
        y += chip_h + gap

    # Title
    p.setPen(QColor(title_color))
    p.setFont(QFont(font_family, max(12, title_size), QFont.Weight.Bold))
    p.drawText(
        QRect(margin, y, content_w, title_h + 20),
        int(align | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
        title or "Class Quiz",
    )
    y += title_h + gap

    # Lesson
    if lesson:
        p.setPen(QColor(subtitle_color))
        p.setFont(QFont(font_family, max(10, lesson_size)))
        p.drawText(
            QRect(margin, y, content_w, lesson_h + 10),
            int(align | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
            lesson,
        )
        y += lesson_h + gap

    # Question count
    if show_question_count and question_count:
        p.setPen(QColor(meta_color))
        p.setFont(QFont(font_family, max(10, meta_size), QFont.Weight.Bold))
        count_text = f"{question_count} questions"
        p.drawText(
            QRect(margin, y, content_w, meta_h),
            int(align | Qt.AlignmentFlag.AlignVCenter),
            count_text,
        )
        y += meta_h + 8

    # Accent underline
    line_w = 120
    if text_align == "right":
        lx = width - margin - line_w
    elif text_align == "center":
        lx = (width - line_w) // 2
    else:
        lx = margin
    p.setPen(QPen(QColor(accent), 3))
    p.drawLine(lx, y + 4, lx + line_w, y + 4)
    y += accent_line_h + 8

    # School
    if school:
        p.setPen(QColor(subtitle_color))
        p.setFont(QFont(font_family, 14))
        p.drawText(
            QRect(margin, min(y, height - 48), content_w, 30),
            int(align | Qt.AlignmentFlag.AlignVCenter),
            school,
        )

    p.end()

    if out_path is None:
        return img

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out), "PNG")
    return out


def cover_preview_pixmap(
    cover: Any = None,
    question_count: int = 0,
    max_width: int = 960,
    max_height: int = 540,
) -> QPixmap:
    """Scaled 16:9 preview pixmap for the Design tab (fits question-preview size)."""
    img = render_youtube_cover(None, cover=cover, question_count=question_count)
    if not isinstance(img, QImage):
        return QPixmap()
    pm = QPixmap.fromImage(img)
    # Fit inside max box keeping 16:9
    pm = pm.scaled(
        max_width,
        max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    return pm
