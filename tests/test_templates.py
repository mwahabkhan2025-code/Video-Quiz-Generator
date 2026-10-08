"""Template / theme application tests."""
from core.templates import TEMPLATES, QUESTION_THEMES, INTRO_THEMES, OUTRO_THEMES
from core.design_config import DesignConfig


def test_question_theme_count():
    assert len(QUESTION_THEMES) >= 20


def test_has_light_themes():
    light_names = [n for n in QUESTION_THEMES if any(
        k in n.lower() for k in ("white", "soft", "paper", "cream", "light", "lavender light", "rose light")
    )]
    assert len(light_names) >= 4, f"expected light themes, got {light_names}"


def test_each_theme_builds():
    for name, factory in QUESTION_THEMES.items():
        cfg = factory()
        assert isinstance(cfg, DesignConfig), name
        assert cfg.correct_bg.startswith("#"), name
        assert cfg.option_bg.startswith("#"), name
        assert getattr(cfg, "card_bg", None), name
        assert cfg.question.color.startswith("#"), name
        assert cfg.border.color.startswith("#"), name


def test_light_theme_card_is_light():
    cfg = QUESTION_THEMES["Clean White"]()
    # card should be light (high luminance approx by high hex values)
    assert cfg.card_bg.lower() in ("#ffffff", "#f8fafc", "#f0f9ff", "#fffbeb", "#faf5ff", "#fff1f2", "#f0fdf4")
    # question text should be dark on light card
    assert cfg.question.color.lower() in ("#0f172a", "#0c4a6e", "#064e3b", "#78350f", "#4c1d95", "#9f1239")


def test_themes_differ_in_highlight():
    a = QUESTION_THEMES["Ocean Blue"]()
    b = QUESTION_THEMES["Crimson Classic"]()
    assert a.correct_bg != b.correct_bg
    assert a.border.color != b.border.color


def test_templates_combo_includes_all_question_themes():
    for name in QUESTION_THEMES:
        assert name in TEMPLATES


def test_intro_outro_theme_counts():
    assert len(INTRO_THEMES) >= 10
    assert len(OUTRO_THEMES) >= 10


def test_default_config_has_card_bg():
    c = DesignConfig()
    assert c.card_bg
    assert c.correct_bg
