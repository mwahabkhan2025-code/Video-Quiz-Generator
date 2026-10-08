# Contributing to Class Quiz Maker

Thanks for helping improve this open-source classroom tool.

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/class-quiz-maker.git
cd class-quiz-maker
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**System dependency:** [ffmpeg](https://ffmpeg.org/) must be on your `PATH`.

## Tests

```bash
pytest tests/ -v
```

Please run tests before opening a pull request.

## Guidelines

1. **Keep the app teacher-friendly** — clear labels, sensible defaults, no jargon in the UI when possible.
2. **English and Tamil** — if you change text parsing, TTS, or fonts, test both languages when you can.
3. **Small, focused PRs** — one feature or fix per pull request is easier to review.
4. **No secrets** — never commit API keys, tokens, or personal paths.
5. **Match existing style** — PyQt6 UI patterns and `core/` vs `ui/` layout already in the repo.

## Reporting issues

Include:

- OS and Python version  
- Steps to reproduce  
- Expected vs actual behavior  
- Log snippet from the Export tab if video generation fails  

## License

By contributing, you agree that your contributions are licensed under the MIT License (see [LICENSE](LICENSE)).
