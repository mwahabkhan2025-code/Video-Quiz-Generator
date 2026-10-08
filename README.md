# Class Quiz Maker

**Open-source desktop app** for teachers to create classroom quiz videos for **YouTube (16:9)** and **Reels / Shorts (9:16)**.

Paste questions (English or Tamil), pick a visual theme, preview, and export a ready-to-share video with optional voice narration.

[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

---

## Features

- **MCQ import** — plain text files, multiple formats, English & Tamil
- **Live design workspace** — themes gallery, colors, intervals, intro/outro, voice
- **YouTube cover editor** — title, colors, fonts, left/center/right text, PNG export (1280×720)
- **Export** — full video, preview clip, or individual Shorts; quality presets
- **Light / dark UI** — autosave, project files (`.vquiz`)

---

## Requirements

| Requirement | Notes |
|-------------|--------|
| **Python 3.10+** | [python.org](https://www.python.org/downloads/) — on Windows, enable **Add Python to PATH** |
| **ffmpeg** (+ ffprobe) | Must be on your system `PATH` |
| **Internet** | First TTS run downloads neural voices (then cached) |

### Install ffmpeg

- **Windows:** `winget install ffmpeg` or [ffmpeg.org](https://ffmpeg.org/download.html)
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg` (or your distro equivalent)

```bash
python --version
ffmpeg -version
```

---

## Install & run

```bash
git clone https://github.com/YOUR_USERNAME/class-quiz-maker.git
cd class-quiz-maker

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

Replace `YOUR_USERNAME/class-quiz-maker` with your GitHub path after you create the repository.

---

## Quick first run

1. **Question & Answers** — **File → Load Sample**, or open a `.txt` / **Add Q&A**
2. **Design & Preview** — choose a theme from the gallery; tune Intro / Question / Outro
3. **YouTube Cover** (optional) — Design styles → **YouTube Cover** → generate PNG
4. **Export** — set output path → **Generate Video**

---

## Question format

Paste or load a `.txt` file. Separate questions with a blank line. Exactly four options (A–D).

```text
What is the capital of France?
A) London
B) Berlin
C) Paris
D) Madrid
Answer: C
```

Tamil example:

```text
இந்தியாவின் தலைநகரம் எது?
A) மும்பை
B) கொல்கத்தா
C) புது தில்லி
D) சென்னை
சரியான பதில்: C
```

Answer labels: `Answer:`, `Correct:`, `சரியான பதில்:`, or a lone letter on the last line.

---

## Tests

```bash
pytest tests/ -v
```

---

## Project layout

```text
class-quiz-maker/
  main.py              # Entry point
  requirements.txt
  LICENSE              # MIT
  core/                # Parser, design, renderer, video engine, cover art
  ui/                  # PyQt6 windows and panels
  samples/             # English & Tamil examples
  resources/           # App icon, Tamil fonts (Noto Sans Tamil)
  tests/
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE).

Bundled **Noto Sans Tamil** fonts are from Google Noto and subject to the
[SIL Open Font License](https://scripts.sil.org/OFL).

Neural voices are provided at runtime via [edge-tts](https://github.com/rany2/edge-tts) / optional gTTS; their use is subject to the respective service terms.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not found | Try `python3` or `py` (Windows) |
| `No module named PyQt6` | `pip install -r requirements.txt` in the same environment |
| `ffmpeg` / `ffprobe` not found | Install ffmpeg and **restart the terminal** |
| Voice / TTS fails | Check internet on first run; app can fall back to gTTS |
| Garbled Tamil audio | Select a **Tamil** voice (or reload questions so auto-detect runs) |
| Blank window | Run on a normal desktop session (not headless) |

---

## Roadmap (ideas)

- More question types (True/False, short answer, fill-up)
- Lesson PDF import
- Optional image search for questions

Contributions welcome.
