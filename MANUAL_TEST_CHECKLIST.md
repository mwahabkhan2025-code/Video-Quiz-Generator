# Manual Test Checklist — ClassQuiz Maker

## Phase 1 – Question & Answers
- [ ] App launches as **ClassQuiz Maker** with icon
- [ ] Empty state shows guided steps when no questions
- [ ] Light / Dark theme toggles (Ctrl+T) and persists after restart
- [ ] Load Sample loads English or Tamil questions
- [ ] Select File works with `.txt` MCQ files (no success dialog)
- [ ] Add Q&A dialog validates empty fields
- [ ] Edit / Delete / Move Up / Down work
- [ ] Raw Text Mode apply parses correctly
- [ ] Clear All asks for confirmation
- [ ] Status bar shows Language + Question count

## Phase 2 – Design & Preview
- [ ] Question / Intro / Outro buttons switch preview **and** right settings panel
- [ ] YouTube 16:9 / Reel 9:16 toggle works
- [ ] Changing background color updates preview
- [ ] Intro: BG color, title/subtitle colors, logo picker work
- [ ] Outro: BG color, title/subtitle colors work
- [ ] Interval steps are 0.5 s
- [ ] Templates apply Science / GK / Tamil / Minimal
- [ ] Save Project (.vquiz) and Load Project restores questions + design
- [ ] Autosave status appears after ~2 minutes

## Phase 3 – Export
- [ ] Quality labels are plain language (Classroom recommended)
- [ ] Codec dropdown lists available encoders
- [ ] Output row: path + Browse + Generate + Cancel on one line
- [ ] Generate disabled when no questions
- [ ] Generate Full Video creates multi-question MP4
- [ ] Progress bar advances; Cancel stops generation
- [ ] On success, output folder opens (no confirmation dialog)
- [ ] Countdown clock appears during think-time in video

## Cross-cutting
- [ ] Tamil questions render with Noto Sans Tamil
- [ ] No crash when switching tabs rapidly
- [ ] App usable at 1100×700 minimum window size
- [ ] Color picker text is readable
