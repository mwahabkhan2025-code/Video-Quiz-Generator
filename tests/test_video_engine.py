import pytest
pytest.importorskip("PyQt6")

"""
Tests for video engine helpers
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_engine import detect_encoder, QUALITY_PRESETS, _correct_phrase
from core.mcq_parser import MCQ
from core.frame_renderer import render_question_frame, render_title_screen
from core.design_config import DesignConfig

import pytest
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session", autouse=True)
def qapp():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app



def test_quality_presets_exist():
    assert "basic" in QUALITY_PRESETS
    assert "standard" in QUALITY_PRESETS
    assert "high" in QUALITY_PRESETS
    assert "excellent" in QUALITY_PRESETS
    for key, meta in QUALITY_PRESETS.items():
        assert "crf" in meta
        assert "audio_bitrate" in meta
        assert "label" in meta


def test_detect_encoder():
    enc, label = detect_encoder()
    assert enc in ("libx264", "h264_nvenc", "h264_qsv", "h264_vaapi")
    assert len(label) > 0


def test_correct_phrase_english():
    mcq = MCQ("Q?", ["A1", "A2", "A3", "A4"], "B")
    phrase = _correct_phrase(mcq, "en-IN-NeerjaNeural")
    assert "correct answer is b" in phrase.lower()
    assert "A2" in phrase


def test_correct_phrase_tamil():
    mcq = MCQ("கேள்வி?", ["ஒன்று", "இரண்டு", "மூன்று", "நான்கு"], "B")
    phrase = _correct_phrase(mcq, "ta-IN-PallaviNeural")
    assert "சரியான விடை" in phrase
    assert "B" in phrase


def test_render_question_frame():
    cfg = DesignConfig()
    mcq = MCQ("Sample question?", ["One", "Two", "Three", "Four"], "B")
    img = render_question_frame(640, 360, cfg, mcq, 0, 1, highlight_correct=False)
    assert img.width() == 640 and img.height() == 360
    img2 = render_question_frame(640, 360, cfg, mcq, 0, 1, highlight_correct=True)
    assert img2.width() == 640 and img2.height() == 360


def test_render_title_screen():
    cfg = DesignConfig()
    img = render_title_screen(640, 360, cfg, "Quiz Time!", "Subtitle")
    assert img.width() == 640 and img.height() == 360
