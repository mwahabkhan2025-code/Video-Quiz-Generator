"""
MCQ Parser - Supports English and Tamil question formats.
Handles common variants: A)/A./A:, Answer:/Correct:/சரியான பதில்:, lone letter.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import re


@dataclass
class MCQ:
    question: str
    options: List[str]          # exactly 4 items, without the letter prefix
    correct: str                # "A", "B", "C" or "D"

    def to_text(self) -> str:
        lines = [self.question]
        for i, opt in enumerate(self.options):
            lines.append(f"{chr(65 + i)}) {opt}")
        lines.append(f"Answer: {self.correct}")
        return "\n".join(lines)


def detect_language(text: str) -> str:
    """Simple heuristic: if Tamil characters present → Tamil, else English."""
    tamil_range = re.compile(r'[\u0B80-\u0BFF]')
    if tamil_range.search(text):
        return "Tamil"
    return "English"


_OPTION_RE = re.compile(r'^([A-Da-d])[\s\)\.\:\-]+\s*(.+)$')
_ANSWER_RE = re.compile(
    r'(?:Answer|Correct|Ans|சரியான\s*பதில்)\s*[:\-]?\s*([A-Da-d])\b',
    re.IGNORECASE,
)
_LONE_LETTER_RE = re.compile(r'^([A-Da-d])[\.\)\:]?\s*$')
_Q_PREFIX_RE = re.compile(
    r'^(?:Question\s*\d*[:\.]?\s*|Q\.?\s*\d+[\.\)\:]?\s*|\d+[\.\)\:]\s*)',
    re.IGNORECASE,
)


def _clean_option(raw: str) -> str:
    """Remove leading 'A)', 'A.', 'A:', 'A -', etc."""
    m = _OPTION_RE.match(raw.strip())
    if m:
        return m.group(2).strip()
    return re.sub(r'^[A-Da-d][\)\.\:\-]\s*', '', raw).strip()


def _extract_correct(line: str) -> Optional[str]:
    """Extract correct answer letter from various formats. Returns None if not found."""
    line = line.strip()
    if not line:
        return None
    match = _ANSWER_RE.search(line)
    if match:
        return match.group(1).upper()
    match = _LONE_LETTER_RE.match(line)
    if match:
        return match.group(1).upper()
    # Last standalone A-D in the line
    found = re.findall(r'\b([A-Da-d])\b', line)
    if found:
        return found[-1].upper()
    return None


def _parse_block(lines: List[str]) -> Optional[MCQ]:
    """Parse a single question block into an MCQ, or None if invalid."""
    if len(lines) < 5:
        return None

    # Find option lines (A–D)
    option_indices = []
    options_by_letter = {}
    for i, ln in enumerate(lines):
        m = _OPTION_RE.match(ln)
        if m:
            letter = m.group(1).upper()
            if letter in "ABCD" and letter not in options_by_letter:
                options_by_letter[letter] = m.group(2).strip()
                option_indices.append(i)

    if len(options_by_letter) < 4:
        # Fallback: assume lines 1–4 are options after question
        if len(lines) >= 6:
            question = _Q_PREFIX_RE.sub('', lines[0]).strip()
            options = [_clean_option(o) for o in lines[1:5]]
            correct = _extract_correct(lines[5])
            if correct and len(options) == 4 and all(options):
                return MCQ(question=question, options=options, correct=correct)
        return None

    # Question = everything before first option line
    first_opt = min(option_indices)
    q_lines = lines[:first_opt]
    question = " ".join(q_lines).strip() if q_lines else lines[0]
    question = _Q_PREFIX_RE.sub('', question).strip()

    options = [options_by_letter.get(L, "") for L in "ABCD"]
    if not all(options):
        return None

    # Correct answer: search lines after last option
    last_opt = max(option_indices)
    correct = None
    for ln in lines[last_opt + 1:]:
        correct = _extract_correct(ln)
        if correct:
            break
    # Also allow answer embedded in last option line region
    if not correct and last_opt + 1 < len(lines):
        correct = _extract_correct(lines[-1])

    if not correct:
        return None

    return MCQ(question=question, options=options, correct=correct)


def parse_mcq_text(text: str) -> List[MCQ]:
    """
    Parse a block of text containing one or more MCQs.
    Supports blank-line separated blocks and continuous streams of A–D options.
    """
    text = text.strip()
    if not text:
        raise ValueError("No valid MCQs found in the text. Please check the format.")

    # Primary: split on double newlines
    blocks = re.split(r'\n\s*\n', text)
    mcqs: List[MCQ] = []

    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        mcq = _parse_block(lines)
        if mcq:
            mcqs.append(mcq)

    # Fallback: if nothing parsed, try treating whole text as stream
    # and splitting whenever we see a new question after a complete A–D set
    if not mcqs:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        i = 0
        while i < len(lines):
            # Look ahead for a window that might be a question
            window = lines[i:i + 12]
            mcq = _parse_block(window)
            if mcq:
                mcqs.append(mcq)
                # Advance past the lines we consumed (roughly)
                i += 6
            else:
                i += 1

    if not mcqs:
        raise ValueError(
            "No valid MCQs found. Expected format:\n\n"
            "Question text?\nA) option\nB) option\nC) option\nD) option\nAnswer: C\n\n"
            "See Help → Q&A Formats for more examples."
        )

    return mcqs


def parse_mcq_file(filepath: str) -> List[MCQ]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    text = path.read_text(encoding="utf-8")
    return parse_mcq_text(text)
