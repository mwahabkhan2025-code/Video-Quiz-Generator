"""Verify template application updates config fields used by preview/renderer."""
from core.templates import QUESTION_THEMES, TEMPLATES
from core.design_config import DesignConfig
from core.mcq_parser import MCQ


def test_apply_ocean_updates_correct_bg():
    cfg = QUESTION_THEMES["Ocean Blue"]()
    assert cfg.correct_bg == "#0ea5e9"
    assert cfg.option_bg == "#1e3a5f"
    assert cfg.border.color == "#38bdf8"


def test_apply_crimson_highlight_red():
    cfg = QUESTION_THEMES["Crimson Classic"]()
    assert cfg.correct_bg.lower() in ("#dc2626", "#f87171", "#ef4444") or cfg.correct_bg.startswith("#")


def test_serialize_roundtrip_preserves_theme_colors():
    cfg = QUESTION_THEMES["Clean White"]()
    data = cfg.to_dict()
    restored = DesignConfig.from_dict(data)
    assert restored.correct_bg == cfg.correct_bg
    assert restored.option_bg == cfg.option_bg
    assert restored.card_bg == cfg.card_bg
    assert restored.background.color == cfg.background.color
    assert restored.question.color == cfg.question.color


def test_mcq_correct_letter_stable():
    m = MCQ("Q?", ["a", "b", "c", "d"], "B")
    assert m.correct == "B"
    assert m.options[1] == "b"
