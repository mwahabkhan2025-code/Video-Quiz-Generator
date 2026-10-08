"""
Built-in design themes for Class Quiz Maker.
- QUESTION_THEMES: 20 full look-and-feel presets for question screens
- INTRO_THEMES: 10 intro card presets
- OUTRO_THEMES: 10 outro card presets
Legacy TEMPLATES dict kept for overall template combo.
"""

from core.design_config import (
    DesignConfig, BorderStyle, BackgroundStyle, ColorStyle,
    IntervalSettings, IntroSettings, OutroSettings, VoiceSettings
)


def _cfg(
    bg1, bg2, border, q_color, a_color, correct_bg, option_bg,
    intro_title="Quiz Time!", intro_sub="Test your knowledge",
    outro_title="Thanks for watching!", outro_sub="Subscribe for more quizzes",
    accent="#0d9488", gradient=True, card_bg=None,
) -> DesignConfig:
    cfg = DesignConfig()
    cfg.background = BackgroundStyle(
        type="gradient" if gradient else "solid",
        color=bg1, color2=bg2 or bg1,
    )
    cfg.border = BorderStyle(enabled=True, thickness=3, color=border, radius=16)
    cfg.question = ColorStyle(color=q_color, font_size=28, bold=True)
    cfg.answers = ColorStyle(color=a_color, font_size=22)
    cfg.correct_answer = ColorStyle(color="#ffffff", font_size=22, bold=True)
    cfg.correct_bg = correct_bg
    cfg.option_bg = option_bg
    cfg.card_bg = card_bg or "#1e293b"
    cfg.intro = IntroSettings(
        enabled=True, title=intro_title, subtitle=intro_sub, duration=3.0,
        background_color=bg1, title_color=accent, subtitle_color=a_color, title_size=48,
    )
    cfg.outro = OutroSettings(
        enabled=True, title=outro_title, subtitle=outro_sub, duration=3.0,
        background_color=bg1, title_color=accent, subtitle_color=a_color, title_size=40,
    )
    return cfg


QUESTION_THEMES = {
    "Teal Classroom": lambda: _cfg(
        "#0f172a", "#134e4a", "#14b8a6", "#f0fdfa", "#ccfbf1",
        "#0d9488", "#1e293b", accent="#2dd4bf",
    ),
    "Ocean Blue": lambda: _cfg(
        "#0c1929", "#132f4c", "#38bdf8", "#e0f2fe", "#bae6fd",
        "#0ea5e9", "#1e3a5f", accent="#38bdf8",
        intro_title="Science Quiz", intro_sub="Explore · Learn · Discover",
    ),
    "Royal Purple": lambda: _cfg(
        "#1a1025", "#2e1065", "#a78bfa", "#f3e8ff", "#e9d5ff",
        "#8b5cf6", "#3b0764", accent="#c4b5fd",
        intro_title="General Knowledge", intro_sub="How much do you know?",
    ),
    "Amber Gold": lambda: _cfg(
        "#1c1917", "#292524", "#fbbf24", "#fef3c7", "#fde68a",
        "#d97706", "#44403c", accent="#fbbf24",
        intro_title="பொது அறிவு வினாடி வினா", intro_sub="அறிவை சோதிப்போம்!",
        outro_title="நன்றி!", outro_sub="மேலும் வினாடி வினாக்களுக்கு காத்திருங்கள்",
    ),
    "Minimal Dark": lambda: _cfg(
        "#111827", "#111827", "#6b7280", "#f9fafb", "#e5e7eb",
        "#10b981", "#374151", accent="#ffffff", gradient=False,
        intro_title="Quiz", intro_sub="", outro_title="The End", outro_sub="",
    ),
    "Rose Pink": lambda: _cfg(
        "#1f0a14", "#4a044e", "#f472b6", "#fce7f3", "#fbcfe8",
        "#db2777", "#3b0a2a", accent="#f9a8d4",
    ),
    "Forest Green": lambda: _cfg(
        "#052e16", "#14532d", "#4ade80", "#dcfce7", "#bbf7d0",
        "#16a34a", "#166534", accent="#86efac",
    ),
    "Sunset Orange": lambda: _cfg(
        "#1c0a00", "#7c2d12", "#fb923c", "#ffedd5", "#fed7aa",
        "#ea580c", "#431407", accent="#fdba74",
    ),
    "Sky Soft": lambda: _cfg(
        "#0c4a6e", "#075985", "#7dd3fc", "#e0f2fe", "#bae6fd",
        "#0284c7", "#0c4a6e", accent="#38bdf8",
    ),
    "Indigo Night": lambda: _cfg(
        "#1e1b4b", "#312e81", "#818cf8", "#e0e7ff", "#c7d2fe",
        "#4f46e5", "#1e1b4b", accent="#a5b4fc",
    ),
    "Coral Reef": lambda: _cfg(
        "#1a0a0a", "#7f1d1d", "#fb7185", "#ffe4e6", "#fecdd3",
        "#e11d48", "#450a0a", accent="#fda4af",
    ),
    "Mint Fresh": lambda: _cfg(
        "#022c22", "#064e3b", "#6ee7b7", "#d1fae5", "#a7f3d0",
        "#059669", "#064e3b", accent="#34d399",
    ),
    "Slate Pro": lambda: _cfg(
        "#0f172a", "#1e293b", "#94a3b8", "#f1f5f9", "#e2e8f0",
        "#64748b", "#334155", accent="#cbd5e1",
    ),
    "Crimson Classic": lambda: _cfg(
        "#1a0505", "#450a0a", "#f87171", "#fee2e2", "#fecaca",
        "#dc2626", "#3f0a0a", accent="#fca5a5",
    ),
    "Lavender Dream": lambda: _cfg(
        "#1e1033", "#4c1d95", "#c4b5fd", "#ede9fe", "#ddd6fe",
        "#7c3aed", "#2e1065", accent="#ddd6fe",
    ),
    "Cyan Tech": lambda: _cfg(
        "#083344", "#164e63", "#22d3ee", "#cffafe", "#a5f3fc",
        "#06b6d4", "#155e75", accent="#67e8f9",
    ),
    "Warm Sand": lambda: _cfg(
        "#1c1410", "#44403c", "#d6d3d1", "#fafaf9", "#e7e5e4",
        "#a8a29e", "#292524", accent="#f5f5f4",
    ),
    "Emerald Board": lambda: _cfg(
        "#022c22", "#0f3d2e", "#34d399", "#ecfdf5", "#d1fae5",
        "#10b981", "#064e3b", accent="#6ee7b7",
        intro_title="Class Quiz", intro_sub="Think · Answer · Learn",
    ),
    "Midnight Neon": lambda: _cfg(
        "#09090b", "#18181b", "#a3e635", "#fafafa", "#d4d4d8",
        "#84cc16", "#27272a", accent="#bef264",
    ),
    "Peach Cream": lambda: _cfg(
        "#1c1010", "#4a1c1c", "#fdba74", "#fff7ed", "#ffedd5",
        "#f97316", "#3b1212", accent="#fdba74",
    ),
    # —— Light themes ——
    "Clean White": lambda: _cfg(
        "#f8fafc", "#e2e8f0", "#0d9488", "#0f172a", "#334155",
        "#0d9488", "#e2e8f0", accent="#0f766e", gradient=True,
        card_bg="#ffffff",
        intro_title="Quiz Time!", intro_sub="Test your knowledge",
    ),
    "Soft Sky": lambda: _cfg(
        "#e0f2fe", "#bae6fd", "#0284c7", "#0c4a6e", "#075985",
        "#0284c7", "#7dd3fc", accent="#0369a1", gradient=True,
        card_bg="#f0f9ff",
    ),
    "Paper Mint": lambda: _cfg(
        "#ecfdf5", "#d1fae5", "#059669", "#064e3b", "#065f46",
        "#059669", "#a7f3d0", accent="#047857", gradient=True,
        card_bg="#f0fdf4",
    ),
    "Warm Cream": lambda: _cfg(
        "#fffbeb", "#fef3c7", "#d97706", "#78350f", "#92400e",
        "#d97706", "#fde68a", accent="#b45309", gradient=True,
        card_bg="#fffbeb",
    ),
    "Lavender Light": lambda: _cfg(
        "#f5f3ff", "#ede9fe", "#7c3aed", "#4c1d95", "#5b21b6",
        "#7c3aed", "#ddd6fe", accent="#6d28d9", gradient=True,
        card_bg="#faf5ff",
    ),
    "Rose Light": lambda: _cfg(
        "#fff1f2", "#ffe4e6", "#e11d48", "#9f1239", "#be123c",
        "#e11d48", "#fecdd3", accent="#be123c", gradient=True,
        card_bg="#fff1f2",
    ),
}



INTRO_THEMES = {
    "Classic Teal": {
        "title": "Quiz Time!", "subtitle": "Test your knowledge",
        "background_color": "#0f172a", "title_color": "#2dd4bf",
        "subtitle_color": "#94a3b8", "title_size": 48,
    },
    "Bright Start": {
        "title": "Let's Begin!", "subtitle": "Get ready to answer",
        "background_color": "#0c4a6e", "title_color": "#38bdf8",
        "subtitle_color": "#bae6fd", "title_size": 50,
    },
    "Tamil Warm": {
        "title": "வினாடி வினா நேரம்!", "subtitle": "அறிவை சோதிப்போம்",
        "background_color": "#1c1917", "title_color": "#fbbf24",
        "subtitle_color": "#fde68a", "title_size": 42,
    },
    "Minimal White": {
        "title": "Quiz", "subtitle": "",
        "background_color": "#111827", "title_color": "#ffffff",
        "subtitle_color": "#9ca3af", "title_size": 56,
    },
    "Purple Spark": {
        "title": "Brain Boost", "subtitle": "How much do you know?",
        "background_color": "#1a1025", "title_color": "#c4b5fd",
        "subtitle_color": "#e9d5ff", "title_size": 48,
    },
    "Green Board": {
        "title": "Class Quiz", "subtitle": "Think · Answer · Learn",
        "background_color": "#052e16", "title_color": "#86efac",
        "subtitle_color": "#bbf7d0", "title_size": 46,
    },
    "Sunrise": {
        "title": "Good Morning Quiz!", "subtitle": "Warm up your mind",
        "background_color": "#1c0a00", "title_color": "#fdba74",
        "subtitle_color": "#fed7aa", "title_size": 44,
    },
    "Exam Mode": {
        "title": "Practice Test", "subtitle": "Answer carefully",
        "background_color": "#0f172a", "title_color": "#f1f5f9",
        "subtitle_color": "#94a3b8", "title_size": 48,
    },
    "Kids Fun": {
        "title": "Fun Quiz!", "subtitle": "Can you get them all?",
        "background_color": "#4a044e", "title_color": "#f9a8d4",
        "subtitle_color": "#fbcfe8", "title_size": 50,
    },
    "Contest": {
        "title": "Challenge Round", "subtitle": "May the best mind win",
        "background_color": "#1e1b4b", "title_color": "#a5b4fc",
        "subtitle_color": "#c7d2fe", "title_size": 46,
    },
}


OUTRO_THEMES = {
    "Thanks Classic": {
        "title": "Thanks for watching!", "subtitle": "Subscribe for more quizzes",
        "background_color": "#0f172a", "title_color": "#2dd4bf",
        "subtitle_color": "#94a3b8", "title_size": 40,
    },
    "Great Job": {
        "title": "Great job!", "subtitle": "See you in the next lesson",
        "background_color": "#0c1929", "title_color": "#38bdf8",
        "subtitle_color": "#bae6fd", "title_size": 42,
    },
    "Tamil Thanks": {
        "title": "நன்றி!", "subtitle": "மேலும் வினாடி வினாக்களுக்கு காத்திருங்கள்",
        "background_color": "#1c1917", "title_color": "#fbbf24",
        "subtitle_color": "#fde68a", "title_size": 38,
    },
    "Keep Learning": {
        "title": "Keep learning!", "subtitle": "Practice makes perfect",
        "background_color": "#052e16", "title_color": "#86efac",
        "subtitle_color": "#bbf7d0", "title_size": 40,
    },
    "Share & Learn": {
        "title": "Thanks for playing!", "subtitle": "Share with your class",
        "background_color": "#1a1025", "title_color": "#c4b5fd",
        "subtitle_color": "#e9d5ff", "title_size": 40,
    },
    "The End": {
        "title": "The End", "subtitle": "",
        "background_color": "#111827", "title_color": "#ffffff",
        "subtitle_color": "#9ca3af", "title_size": 48,
    },
    "Next Lesson": {
        "title": "See you next time!", "subtitle": "New quiz every week",
        "background_color": "#0c4a6e", "title_color": "#7dd3fc",
        "subtitle_color": "#bae6fd", "title_size": 40,
    },
    "Score Cheer": {
        "title": "Well done!", "subtitle": "You finished the quiz",
        "background_color": "#1c0a00", "title_color": "#fdba74",
        "subtitle_color": "#fed7aa", "title_size": 42,
    },
    "Classroom Close": {
        "title": "Class dismissed!", "subtitle": "Review and revise",
        "background_color": "#0f172a", "title_color": "#f1f5f9",
        "subtitle_color": "#94a3b8", "title_size": 40,
    },
    "Subscribe CTA": {
        "title": "Like & Subscribe", "subtitle": "More quizzes coming soon",
        "background_color": "#450a0a", "title_color": "#fda4af",
        "subtitle_color": "#fecdd3", "title_size": 40,
    },
}


# Overall template combo: Default first, then A–Z
TEMPLATES = {
    "Default": DesignConfig,
    **{name: QUESTION_THEMES[name] for name in sorted(QUESTION_THEMES.keys())},
}

# Sorted name lists for UI dropdowns
QUESTION_THEME_NAMES = sorted(QUESTION_THEMES.keys())
INTRO_THEME_NAMES = sorted(INTRO_THEMES.keys())
OUTRO_THEME_NAMES = sorted(OUTRO_THEMES.keys())
