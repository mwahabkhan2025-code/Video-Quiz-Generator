"""
Unit tests for MCQ parser (Phase 1)
"""

import pytest
from pathlib import Path
import sys

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mcq_parser import MCQ, parse_mcq_text, parse_mcq_file, detect_language


SAMPLE_ENGLISH = """
Who was the first female Prime Minister of India?
A) Sarojini Naidu
B) Sucheta Kripalani
C) Indira Gandhi
D) Pratibha Patil
Answer: C

Who was the first female President of India?
A) Indira Gandhi
B) Droupadi Murmu
C) Pratibha Patil
D) Sarojini Naidu
Answer: C
"""

SAMPLE_TAMIL = """
இந்தியாவின் மிக நீளமான நதி எது?
A) யமுனா 
B) கோதாவரி 
C) கங்கை 
D) பிரம்மபுத்திரா
சரியான பதில்: C) கங்கை

இந்தியாவின் முதல் குடியரசுத் தலைவர் யார்?
A) ஜவஹர்லால் நேரு 
B) சர்தார் வல்லபாய் படேல் 
C) டாக்டர் சர்வபள்ளி ராதாகிருஷ்ணன் 
D) டாக்டர் ராஜேந்திர பிரசாத்
சரியான பதில்: D) டாக்டர் ராஜேந்திர பிரசாத்
"""


def test_parse_english():
    mcqs = parse_mcq_text(SAMPLE_ENGLISH)
    assert len(mcqs) == 2
    assert mcqs[0].question.startswith("Who was the first female Prime Minister")
    assert mcqs[0].options[2] == "Indira Gandhi"
    assert mcqs[0].correct == "C"
    assert mcqs[1].correct == "C"


def test_parse_tamil():
    mcqs = parse_mcq_text(SAMPLE_TAMIL)
    assert len(mcqs) == 2
    assert "நதி" in mcqs[0].question
    assert mcqs[0].correct == "C"
    assert mcqs[1].correct == "D"


def test_detect_language_english():
    assert detect_language("Who was the first female Prime Minister?") == "English"


def test_detect_language_tamil():
    assert detect_language("இந்தியாவின் மிக நீளமான நதி எது?") == "Tamil"


def test_empty_text():
    with pytest.raises(ValueError):
        parse_mcq_text("")


def test_mcq_to_text():
    mcq = MCQ(
        question="Test question?",
        options=["One", "Two", "Three", "Four"],
        correct="B"
    )
    text = mcq.to_text()
    assert "Test question?" in text
    assert "B) Two" in text
    assert "Answer: B" in text


def test_real_english_file():
    path = Path(__file__).resolve().parent.parent / "samples" / "english_gk_sample.txt"
    assert path.exists(), f"Missing sample: {path}"
    mcqs = parse_mcq_file(str(path))
    assert len(mcqs) >= 1
    assert all(len(m.options) == 4 for m in mcqs)
    assert all(m.correct in "ABCD" for m in mcqs)


def test_real_tamil_file():
    path = Path(__file__).resolve().parent.parent / "samples" / "tamil_gk_sample.txt"
    assert path.exists(), f"Missing sample: {path}"
    mcqs = parse_mcq_file(str(path))
    assert len(mcqs) >= 1
    assert all(len(m.options) == 4 for m in mcqs)
    assert all(m.correct in "ABCD" for m in mcqs)
