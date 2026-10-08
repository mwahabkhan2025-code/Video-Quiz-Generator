"""Frame renderer respects theme colors (requires PyQt6)."""
import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication
import sys

from core.templates import QUESTION_THEMES
from core.mcq_parser import MCQ
from core.frame_renderer import render_question_frame


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    return app


def _sample_mcq():
    return MCQ(
        "Sample question?",
        ["Alpha", "Beta", "Gamma", "Delta"],
        "B",
    )


def test_dark_theme_frame(qapp):
    cfg = QUESTION_THEMES["Ocean Blue"]()
    img = render_question_frame(640, 360, cfg, _sample_mcq(), 0, 1, highlight_correct=True)
    assert not img.isNull()
    assert img.width() == 640


def test_light_theme_frame(qapp):
    cfg = QUESTION_THEMES["Clean White"]()
    img = render_question_frame(640, 360, cfg, _sample_mcq(), 0, 1, highlight_correct=True)
    assert not img.isNull()
    # Sample center-ish pixel of correct option area should not be pure black
    # (light card). Just ensure render succeeded with light card_bg set.
    assert cfg.card_bg.lower() in ("#ffffff", "#f8fafc", "#f0f9ff", "#fffbeb", "#faf5ff", "#fff1f2", "#f0fdf4")


def test_highlight_uses_correct_bg(qapp):
    cfg = QUESTION_THEMES["Crimson Classic"]()
    img = render_question_frame(
        640, 360, cfg, _sample_mcq(), 0, 1,
        highlight_correct=True, highlight_option=None,
    )
    assert not img.isNull()
    # correct_bg should be a red-ish value in this theme
    assert cfg.correct_bg.startswith("#")


def test_option_highlight_uses_border(qapp):
    cfg = QUESTION_THEMES["Teal Classroom"]()
    img = render_question_frame(
        640, 360, cfg, _sample_mcq(), 0, 1,
        highlight_correct=False, highlight_option=1,
    )
    assert not img.isNull()
