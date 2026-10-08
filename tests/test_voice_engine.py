"""Voice / timing helpers (no network required for pure helpers)."""
from core.video_engine import (
    _correct_phrase, _speakable, _is_tamil_voice,
    _option_speech, _TAMIL_LETTER,
)
from core.mcq_parser import MCQ


def test_speakable_expands_initials():
    assert "பி ஆர்" in _speakable("டாக்டர் பி.ஆர். அம்பேத்கர்")


def test_correct_phrase_tamil():
    m = MCQ("Q", ["a", "நேரு", "c", "d"], "B")
    phrase = _correct_phrase(m, "ta-IN-PallaviNeural")
    assert "சரியான விடை" in phrase
    assert ("பீ" in phrase or "B" in phrase)
    assert "நேரு" in phrase


def test_correct_phrase_english():
    m = MCQ("Q", ["a", "Nehru", "c", "d"], "B")
    phrase = _correct_phrase(m, "en-IN-NeerjaNeural")
    assert "correct answer" in phrase.lower()
    assert "Nehru" in phrase


def test_is_tamil_voice():
    assert _is_tamil_voice("ta-IN-PallaviNeural")
    assert not _is_tamil_voice("en-IN-NeerjaNeural")


def test_tamil_letter_d_uses_long_vowel():
    """D must not use short டி (often misread); prefer டீ."""
    assert _TAMIL_LETTER["D"] == "டீ"
    assert _TAMIL_LETTER["A"] == "ஏ"
    assert _TAMIL_LETTER["B"] == "பீ"
    assert _TAMIL_LETTER["C"] == "சீ"


def test_option_speech_tamil_d():
    line = _option_speech("D", "சென்னை", "ta-IN-PallaviNeural")
    assert "டீ" in line
    assert "டி." not in line  # avoid short form as the letter token
    assert "சென்னை" in line
    assert "விருப்பம்" not in line
    assert line.startswith("டீ")


def test_option_speech_english():
    line = _option_speech("D", "Chennai", "en-IN-NeerjaNeural")
    assert "Option D" in line
    assert "Chennai" in line


def test_correct_phrase_tamil_d():
    m = MCQ("Q", ["a", "b", "c", "சென்னை"], "D")
    phrase = _correct_phrase(m, "ta-IN-PallaviNeural")
    assert "டீ" in phrase
    assert "சென்னை" in phrase
