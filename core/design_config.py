"""
Design configuration model - holds all visual & timing settings.
Serializable to/from JSON for project save/load.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json
from pathlib import Path


@dataclass
class ColorStyle:
    color: str = "#ffffff"
    font_size: int = 28
    font_family: str = "Segoe UI"
    bold: bool = False


@dataclass
class BorderStyle:
    enabled: bool = True
    thickness: int = 4
    color: str = "#0d9488"
    radius: int = 16


@dataclass
class BackgroundStyle:
    type: str = "solid"          # solid | gradient | image
    color: str = "#0f172a"
    color2: str = "#1e293b"      # for gradient
    image_path: str = ""


@dataclass
class IntervalSettings:
    after_question: float = 1.5   # seconds after question is announced
    between_options: float = 1.0  # seconds after each option is spoken
    before_answer: float = 10.0   # wait after all options (countdown clock shown)
    answer_duration: float = 2.0  # how long correct answer stays on screen
    before_intro: float = 2.0     # silence at video start before intro speech
    after_intro: float = 3.0      # pause after intro before first question
    after_answer: float = 3.0     # pause after correct answer before next question


@dataclass
class IntroSettings:
    enabled: bool = True
    title: str = "Quiz Time!"
    subtitle: str = "Test your knowledge"
    duration: float = 3.0
    background_color: str = "#0f172a"
    title_color: str = "#ffffff"
    subtitle_color: str = "#94a3b8"
    title_size: int = 48
    subtitle_size: int = 24
    show_logo: bool = False
    logo_path: str = ""


@dataclass
class OutroSettings:
    enabled: bool = True
    title: str = "Thanks for watching!"
    subtitle: str = "Subscribe for more quizzes"
    duration: float = 3.0
    background_color: str = "#0f172a"
    title_color: str = "#ffffff"
    subtitle_color: str = "#94a3b8"
    title_size: int = 40
    subtitle_size: int = 22


@dataclass
class CoverSettings:
    """YouTube cover (1280x720) text and style."""
    title: str = "Class Quiz"
    subject: str = ""
    class_name: str = ""
    lesson: str = ""
    school: str = ""
    show_question_count: bool = True
    background_color: str = "#0f172a"
    background_color2: str = "#1e293b"
    accent_color: str = "#0d9488"
    title_color: str = "#ffffff"
    subtitle_color: str = "#94a3b8"
    meta_color: str = "#e2e8f0"
    title_size: int = 42
    lesson_size: int = 22
    meta_size: int = 18
    font_family: str = "Segoe UI"
    text_align: str = "center"  # left | center | right
    show_logo: bool = False
    logo_path: str = ""


@dataclass
class VoiceSettings:
    language: str = "en"          # en | ta
    voice_name: str = "en-IN-NeerjaNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    background_music: bool = False
    music_path: str = ""
    music_volume: float = 0.3


@dataclass
class DesignConfig:
    """Complete design configuration for a project."""
    border: BorderStyle = field(default_factory=BorderStyle)
    background: BackgroundStyle = field(default_factory=BackgroundStyle)
    title: ColorStyle = field(default_factory=lambda: ColorStyle("#f1f5f9", 32, "Segoe UI", True))
    question: ColorStyle = field(default_factory=lambda: ColorStyle("#f1f5f9", 26, "Segoe UI", True))
    answers: ColorStyle = field(default_factory=lambda: ColorStyle("#e2e8f0", 22, "Segoe UI", False))
    correct_answer: ColorStyle = field(default_factory=lambda: ColorStyle("#ffffff", 22, "Segoe UI", True))
    correct_bg: str = "#10b981"
    option_bg: str = "#334155"
    card_bg: str = "#1e293b"  # question card panel (supports light themes)
    intervals: IntervalSettings = field(default_factory=IntervalSettings)
    intro: IntroSettings = field(default_factory=IntroSettings)
    outro: OutroSettings = field(default_factory=OutroSettings)
    voice: VoiceSettings = field(default_factory=VoiceSettings)
    cover: CoverSettings = field(default_factory=CoverSettings)
    format: str = "youtube"       # youtube | reel
    quality: str = "standard"     # basic | standard | high | excellent
    codec: str = "auto"           # auto | libx264 | h264_nvenc | h264_qsv | h264_amf | libx265

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DesignConfig":
        cfg = cls()
        if "border" in data:
            cfg.border = BorderStyle(**data["border"])
        if "background" in data:
            cfg.background = BackgroundStyle(**data["background"])
        if "title" in data:
            cfg.title = ColorStyle(**data["title"])
        if "question" in data:
            cfg.question = ColorStyle(**data["question"])
        if "answers" in data:
            cfg.answers = ColorStyle(**data["answers"])
        if "correct_answer" in data:
            cfg.correct_answer = ColorStyle(**data["correct_answer"])
        if "correct_bg" in data:
            cfg.correct_bg = data["correct_bg"]
        if "option_bg" in data:
            cfg.option_bg = data["option_bg"]
        if "card_bg" in data:
            cfg.card_bg = data["card_bg"]
        if "intervals" in data:
            cfg.intervals = IntervalSettings(**data["intervals"])
        if "intro" in data:
            cfg.intro = IntroSettings(**data["intro"])
        if "outro" in data:
            cfg.outro = OutroSettings(**data["outro"])
        if "voice" in data:
            cfg.voice = VoiceSettings(**data["voice"])
        if "cover" in data and isinstance(data["cover"], dict):
            cfg.cover = CoverSettings(**{
                k: v for k, v in data["cover"].items()
                if k in CoverSettings.__dataclass_fields__
            })
        if "format" in data:
            cfg.format = data["format"]
        if "quality" in data:
            cfg.quality = data["quality"]
        if "codec" in data:
            cfg.codec = data["codec"]
        return cfg

    def save(self, path: str):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str) -> "DesignConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)
