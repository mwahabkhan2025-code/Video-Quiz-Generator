"""YouTube cover art renderer."""
from pathlib import Path
import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication
from core.cover_art import render_youtube_cover


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_render_youtube_cover(qapp, tmp_path):
    out = tmp_path / "cover.png"
    path = render_youtube_cover(
        out,
        title="Class 10 Science Quiz",
        subject="Science",
        class_name="Class 10",
        lesson="Chapter 3",
        question_count=12,
        accent="#0d9488",
        bg1="#0f172a",
        bg2="#134e4a",
    )
    assert path.exists()
    assert path.stat().st_size > 1000
