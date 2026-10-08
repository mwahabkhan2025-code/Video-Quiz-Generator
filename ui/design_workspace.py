"""
Design Workspace - 3-column layout matching the mockup:
  Left: section nav | Center: live preview | Right: settings for selected section
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QFormLayout,
    QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QComboBox,
    QColorDialog, QFrame, QSizePolicy, QAbstractItemView, QFileDialog,
    QSlider,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from pathlib import Path
from typing import List, Optional

from core.design_config import DesignConfig, CoverSettings
from core.templates import (
    TEMPLATES, INTRO_THEMES, OUTRO_THEMES,
    QUESTION_THEME_NAMES, INTRO_THEME_NAMES, OUTRO_THEME_NAMES,
)
from ui.preview_panel import PreviewCanvas
from ui.widgets import ColorButton
from ui.theme_gallery import ThemeGallery
from core.mcq_parser import MCQ


def form() -> QFormLayout:
    f = QFormLayout()
    f.setHorizontalSpacing(10)
    f.setVerticalSpacing(8)
    f.setContentsMargins(8, 8, 8, 8)
    f.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
    return f


class DesignWorkspace(QWidget):
    """Mockup-style Design page: nav | preview | settings."""

    config_changed = pyqtSignal(object)
    format_changed = pyqtSignal(str)

    SECTIONS = [
        "Overall / Template",
        "Background",
        "Border",
        "Question Style",
        "Answers Style",
        "Intervals",
        "Flash / Intro",
        "Outro",
        "Voice & Audio",
        "Layout (YouTube / Reel)",
        "YouTube Cover",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = DesignConfig()
        self.mcqs: List[MCQ] = []
        self._setup_ui()
        self._load_all()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ===== LEFT NAV =====
        left = QFrame()
        left.setFixedWidth(200)
        left.setObjectName("card")
        left.setStyleSheet(
            "QFrame#card{background:#ffffff;border-right:1px solid #e2e8f0;border-radius:0;}"
        )
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 12, 8, 12)
        ll.setSpacing(4)

        nav_title = QLabel("DESIGN STYLES")
        nav_title.setStyleSheet("font-size:11px;font-weight:700;color:#64748b;letter-spacing:0.5px;")
        ll.addWidget(nav_title)

        self.nav = QListWidget()
        self.nav.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.nav.setStyleSheet("""
            QListWidget{border:none;background:transparent;font-size:13px;}
            QListWidget::item{padding:10px 12px;border-radius:8px;margin:2px 0;}
            QListWidget::item:selected{background:#e0f2f1;color:#0f766e;font-weight:600;}
            QListWidget::item:hover:!selected{background:#f1f5f9;}
        """)
        for s in self.SECTIONS:
            self.nav.addItem(QListWidgetItem(s))
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self._on_nav)
        ll.addWidget(self.nav, 1)
        root.addWidget(left)

        # ===== CENTER PREVIEW =====
        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(12, 12, 12, 12)
        cl.setSpacing(8)

        top = QHBoxLayout()
        prev_lbl = QLabel("Live Preview")
        prev_lbl.setObjectName("sectionTitle")
        top.addWidget(prev_lbl)
        top.addStretch()

        self.btn_yt = QPushButton("YouTube 16:9")
        self.btn_yt.setCheckable(True)
        self.btn_yt.setChecked(True)
        self.btn_yt.clicked.connect(lambda: self._set_fmt("youtube"))
        top.addWidget(self.btn_yt)

        self.btn_reel = QPushButton("Reel 9:16")
        self.btn_reel.setCheckable(True)
        self.btn_reel.setObjectName("secondaryButton")
        self.btn_reel.clicked.connect(lambda: self._set_fmt("reel"))
        top.addWidget(self.btn_reel)

        self.btn_mode_q = QPushButton("Question")
        self.btn_mode_q.setCheckable(True)
        self.btn_mode_q.setChecked(True)
        self.btn_mode_q.setObjectName("secondaryButton")
        self.btn_mode_q.clicked.connect(lambda: self._set_preview_mode("question"))
        top.addWidget(self.btn_mode_q)

        self.btn_mode_intro = QPushButton("Intro")
        self.btn_mode_intro.setCheckable(True)
        self.btn_mode_intro.setObjectName("secondaryButton")
        self.btn_mode_intro.clicked.connect(lambda: self._set_preview_mode("intro"))
        top.addWidget(self.btn_mode_intro)

        self.btn_mode_outro = QPushButton("Outro")
        self.btn_mode_outro.setCheckable(True)
        self.btn_mode_outro.setObjectName("secondaryButton")
        self.btn_mode_outro.clicked.connect(lambda: self._set_preview_mode("outro"))
        top.addWidget(self.btn_mode_outro)
        cl.addLayout(top)

        self.canvas_frame = QFrame()
        self.canvas_frame.setObjectName("card")
        cfl = QVBoxLayout(self.canvas_frame)
        cfl.setContentsMargins(8, 8, 8, 8)
        self.canvas = PreviewCanvas()
        self.canvas.setMinimumHeight(360)
        cfl.addWidget(self.canvas, 1)
        cl.addWidget(self.canvas_frame, 1)

        # Cover preview — same outer card + letterbox chrome as question Live Preview
        self.cover_preview_frame = QFrame()
        self.cover_preview_frame.setObjectName("card")
        self.cover_preview_frame.setVisible(False)
        cpl = QVBoxLayout(self.cover_preview_frame)
        cpl.setContentsMargins(8, 8, 8, 8)
        self.cover_preview_label = QLabel("Cover preview")
        self.cover_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_preview_label.setMinimumHeight(360)
        self.cover_preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # Match PreviewCanvas letterbox background
        self.cover_preview_label.setStyleSheet(
            "background:#e2e8f0;border-radius:8px;"
        )
        cpl.addWidget(self.cover_preview_label, 1)
        cl.addWidget(self.cover_preview_frame, 1)

        self.timing_legend = QLabel(
            "Flow: Intro → Question → Options → Think time → Correct answer → Next"
        )
        self.timing_legend.setObjectName("mutedLabel")
        self.timing_legend.setWordWrap(True)
        self.timing_legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.timing_legend)

        root.addWidget(center, 1)

        # ===== RIGHT SETTINGS =====
        right = QFrame()
        right.setFixedWidth(360)
        right.setObjectName("card")
        right.setStyleSheet(
            "QFrame#card{background:#ffffff;border-left:1px solid #e2e8f0;border-radius:0;}"
        )
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 12, 12, 12)
        rl.setSpacing(8)

        self.settings_title = QLabel("Settings")
        self.settings_title.setStyleSheet("font-size:15px;font-weight:700;color:#0f172a;")
        rl.addWidget(self.settings_title)

        self.stack = QStackedWidget()
        self._build_pages()
        rl.addWidget(self.stack, 1)
        root.addWidget(right)

    def _build_pages(self):
        # 0 Overall / Template — visual gallery + optional name dropdown
        p0 = QWidget()
        p0_lay = QVBoxLayout(p0)
        p0_lay.setContentsMargins(0, 0, 0, 0)
        p0_lay.setSpacing(8)

        self.theme_gallery = ThemeGallery()
        self.theme_gallery.theme_selected.connect(self._apply_template)
        p0_lay.addWidget(self.theme_gallery, 1)

        row = QHBoxLayout()
        row.addWidget(QLabel("Or pick by name"))
        self.template_combo = QComboBox()
        for n in TEMPLATES:  # Default + A–Z
            self.template_combo.addItem(n)
        self.template_combo.currentTextChanged.connect(self._apply_template)
        row.addWidget(self.template_combo, 1)
        p0_lay.addLayout(row)
        self.stack.addWidget(p0)

        # 1 Background
        p1 = QWidget()
        f1 = form()
        self.bg_type = QComboBox()
        self.bg_type.addItems(["solid", "gradient"])
        self.bg_type.currentTextChanged.connect(self._changed)
        f1.addRow("Type", self.bg_type)
        self.bg_color = ColorButton("#0f172a")
        self.bg_color.color_changed.connect(self._changed)
        f1.addRow("Color", self.bg_color)
        self.bg_color2 = ColorButton("#1e293b")
        self.bg_color2.color_changed.connect(self._changed)
        f1.addRow("Gradient 2nd", self.bg_color2)
        p1.setLayout(f1)
        self.stack.addWidget(p1)

        # 2 Border
        p2 = QWidget()
        f2 = form()
        self.border_enabled = QCheckBox("Show border")
        self.border_enabled.setChecked(True)
        self.border_enabled.toggled.connect(self._changed)
        f2.addRow(self.border_enabled)
        self.border_thickness = QSpinBox()
        self.border_thickness.setRange(0, 20)
        self.border_thickness.setValue(4)
        self.border_thickness.valueChanged.connect(self._changed)
        f2.addRow("Thickness", self.border_thickness)
        self.border_color = ColorButton("#0d9488")
        self.border_color.color_changed.connect(self._changed)
        f2.addRow("Color", self.border_color)
        self.border_radius = QSpinBox()
        self.border_radius.setRange(0, 40)
        self.border_radius.setValue(16)
        self.border_radius.valueChanged.connect(self._changed)
        f2.addRow("Radius", self.border_radius)
        p2.setLayout(f2)
        self.stack.addWidget(p2)

        # 3 Question
        p3 = QWidget()
        f3 = form()
        self.q_color = ColorButton("#f1f5f9")
        self.q_color.color_changed.connect(self._changed)
        f3.addRow("Color", self.q_color)
        self.q_size = QSpinBox()
        self.q_size.setRange(12, 72)
        self.q_size.setValue(26)
        self.q_size.valueChanged.connect(self._changed)
        f3.addRow("Font size", self.q_size)
        self.q_bold = QCheckBox("Bold")
        self.q_bold.setChecked(True)
        self.q_bold.toggled.connect(self._changed)
        f3.addRow(self.q_bold)
        p3.setLayout(f3)
        self.stack.addWidget(p3)

        # 4 Answers
        p4 = QWidget()
        f4 = form()
        self.a_color = ColorButton("#e2e8f0")
        self.a_color.color_changed.connect(self._changed)
        f4.addRow("Text color", self.a_color)
        self.a_size = QSpinBox()
        self.a_size.setRange(12, 48)
        self.a_size.setValue(22)
        self.a_size.valueChanged.connect(self._changed)
        f4.addRow("Font size", self.a_size)
        self.option_bg = ColorButton("#334155")
        self.option_bg.color_changed.connect(self._changed)
        f4.addRow("Option bg", self.option_bg)
        self.correct_bg = ColorButton("#10b981")
        self.correct_bg.color_changed.connect(self._changed)
        f4.addRow("Correct bg", self.correct_bg)
        p4.setLayout(f4)
        self.stack.addWidget(p4)

        # 5 Intervals
        p5 = QWidget()
        f5 = form()
        self.int_after_q = QDoubleSpinBox()
        self.int_after_q.setRange(0, 30)
        self.int_after_q.setSingleStep(0.5)
        self.int_after_q.setDecimals(1)
        self.int_after_q.setValue(1.5)
        self.int_after_q.valueChanged.connect(self._changed)
        f5.addRow("After question", self.int_after_q)
        self.int_between = QDoubleSpinBox()
        self.int_between.setRange(0, 10)
        self.int_between.setSingleStep(0.5)
        self.int_between.setDecimals(1)
        self.int_between.setValue(1.0)
        self.int_between.valueChanged.connect(self._changed)
        f5.addRow("After each option", self.int_between)
        self.int_before_ans = QDoubleSpinBox()
        self.int_before_ans.setRange(0, 60)
        self.int_before_ans.setSingleStep(0.5)
        self.int_before_ans.setDecimals(1)
        self.int_before_ans.setValue(10.0)
        self.int_before_ans.valueChanged.connect(self._changed)
        f5.addRow("After all options (countdown)", self.int_before_ans)
        self.int_ans_dur = QDoubleSpinBox()
        self.int_ans_dur.setRange(0.5, 15)
        self.int_ans_dur.setSingleStep(0.5)
        self.int_ans_dur.setDecimals(1)
        self.int_ans_dur.setValue(2.0)
        self.int_ans_dur.valueChanged.connect(self._changed)
        f5.addRow("Answer duration", self.int_ans_dur)
        self.int_before_intro = QDoubleSpinBox()
        self.int_before_intro.setRange(0, 15)
        self.int_before_intro.setSingleStep(0.5)
        self.int_before_intro.setDecimals(1)
        self.int_before_intro.setValue(2.0)
        self.int_before_intro.valueChanged.connect(self._changed)
        f5.addRow("Before intro speech", self.int_before_intro)
        self.int_after_intro = QDoubleSpinBox()
        self.int_after_intro.setRange(0, 15)
        self.int_after_intro.setSingleStep(0.5)
        self.int_after_intro.setDecimals(1)
        self.int_after_intro.setValue(3.0)
        self.int_after_intro.valueChanged.connect(self._changed)
        f5.addRow("After intro", self.int_after_intro)
        self.int_after_ans = QDoubleSpinBox()
        self.int_after_ans.setRange(0, 15)
        self.int_after_ans.setSingleStep(0.5)
        self.int_after_ans.setDecimals(1)
        self.int_after_ans.setValue(3.0)
        self.int_after_ans.valueChanged.connect(self._changed)
        f5.addRow("After answer (next Q)", self.int_after_ans)
        p5.setLayout(f5)
        self.stack.addWidget(p5)

        # 6 Intro
        p6 = QWidget()
        f6 = form()
        self.intro_enabled = QCheckBox("Enable intro")
        self.intro_enabled.setChecked(True)
        self.intro_enabled.toggled.connect(self._changed)
        f6.addRow(self.intro_enabled)
        self.intro_theme = QComboBox()
        self.intro_theme.addItem("— Custom —")
        for name in INTRO_THEME_NAMES:
            self.intro_theme.addItem(name)
        self.intro_theme.currentTextChanged.connect(self._apply_intro_theme)
        f6.addRow("Intro theme", self.intro_theme)
        self.intro_title = QLineEdit("Quiz Time!")
        self.intro_title.textChanged.connect(self._changed)
        f6.addRow("Title", self.intro_title)
        self.intro_subtitle = QLineEdit("Test your knowledge")
        self.intro_subtitle.textChanged.connect(self._changed)
        f6.addRow("Subtitle", self.intro_subtitle)
        self.intro_duration = QDoubleSpinBox()
        self.intro_duration.setRange(1, 15)
        self.intro_duration.setSingleStep(0.5)
        self.intro_duration.setValue(3.0)
        self.intro_duration.valueChanged.connect(self._changed)
        f6.addRow("Duration (s)", self.intro_duration)
        self.intro_bg_color = ColorButton("#0f172a")
        self.intro_bg_color.color_changed.connect(self._changed)
        f6.addRow("Background", self.intro_bg_color)
        self.intro_title_color = ColorButton("#ffffff")
        self.intro_title_color.color_changed.connect(self._changed)
        f6.addRow("Title color", self.intro_title_color)
        self.intro_subtitle_color = ColorButton("#94a3b8")
        self.intro_subtitle_color.color_changed.connect(self._changed)
        f6.addRow("Subtitle color", self.intro_subtitle_color)
        self.intro_title_size = QSpinBox()
        self.intro_title_size.setRange(16, 120)
        self.intro_title_size.setValue(48)
        self.intro_title_size.valueChanged.connect(self._changed)
        f6.addRow("Title size", self.intro_title_size)
        self.intro_subtitle_size = QSpinBox()
        self.intro_subtitle_size.setRange(12, 80)
        self.intro_subtitle_size.setValue(24)
        self.intro_subtitle_size.valueChanged.connect(self._changed)
        f6.addRow("Subtitle size", self.intro_subtitle_size)
        self.intro_show_logo = QCheckBox("Show school / channel logo")
        self.intro_show_logo.toggled.connect(self._on_intro_logo_toggled)
        f6.addRow(self.intro_show_logo)
        logo_row = QHBoxLayout()
        self.intro_logo_path = QLineEdit()
        self.intro_logo_path.setPlaceholderText("PNG or JPG…")
        self.intro_logo_path.setEnabled(False)
        self.intro_logo_path.textChanged.connect(self._changed)
        logo_row.addWidget(self.intro_logo_path)
        self.btn_intro_logo = QPushButton("Browse…")
        self.btn_intro_logo.setObjectName("secondaryButton")
        self.btn_intro_logo.setEnabled(False)
        self.btn_intro_logo.clicked.connect(self._browse_intro_logo)
        logo_row.addWidget(self.btn_intro_logo)
        f6.addRow("Logo file", logo_row)
        p6.setLayout(f6)
        self.stack.addWidget(p6)

        # 7 Outro
        p7 = QWidget()
        f7 = form()
        self.outro_enabled = QCheckBox("Enable outro")
        self.outro_enabled.setChecked(True)
        self.outro_enabled.toggled.connect(self._changed)
        f7.addRow(self.outro_enabled)
        self.outro_theme = QComboBox()
        self.outro_theme.addItem("— Custom —")
        for name in OUTRO_THEME_NAMES:
            self.outro_theme.addItem(name)
        self.outro_theme.currentTextChanged.connect(self._apply_outro_theme)
        f7.addRow("Outro theme", self.outro_theme)
        self.outro_title = QLineEdit("Thanks for watching!")
        self.outro_title.textChanged.connect(self._changed)
        f7.addRow("Title", self.outro_title)
        self.outro_subtitle = QLineEdit("Subscribe for more")
        self.outro_subtitle.textChanged.connect(self._changed)
        f7.addRow("Subtitle", self.outro_subtitle)
        self.outro_duration = QDoubleSpinBox()
        self.outro_duration.setRange(1, 15)
        self.outro_duration.setSingleStep(0.5)
        self.outro_duration.setValue(3.0)
        self.outro_duration.valueChanged.connect(self._changed)
        f7.addRow("Duration (s)", self.outro_duration)
        self.outro_bg_color = ColorButton("#0f172a")
        self.outro_bg_color.color_changed.connect(self._changed)
        f7.addRow("Background", self.outro_bg_color)
        self.outro_title_color = ColorButton("#ffffff")
        self.outro_title_color.color_changed.connect(self._changed)
        f7.addRow("Title color", self.outro_title_color)
        self.outro_subtitle_color = ColorButton("#94a3b8")
        self.outro_subtitle_color.color_changed.connect(self._changed)
        f7.addRow("Subtitle color", self.outro_subtitle_color)
        self.outro_title_size = QSpinBox()
        self.outro_title_size.setRange(16, 120)
        self.outro_title_size.setValue(40)
        self.outro_title_size.valueChanged.connect(self._changed)
        f7.addRow("Title size", self.outro_title_size)
        self.outro_subtitle_size = QSpinBox()
        self.outro_subtitle_size.setRange(12, 80)
        self.outro_subtitle_size.setValue(22)
        self.outro_subtitle_size.valueChanged.connect(self._changed)
        f7.addRow("Subtitle size", self.outro_subtitle_size)
        p7.setLayout(f7)
        self.stack.addWidget(p7)

        # 8 Voice
        p8 = QWidget()
        f8 = form()
        self.voice_lang = QComboBox()
        self.voice_lang.addItems(["English", "Tamil"])
        self.voice_lang.currentTextChanged.connect(self._on_voice_lang)
        f8.addRow("Language", self.voice_lang)
        self.voice_name = QComboBox()
        self._populate_voices("English")
        self.voice_name.currentTextChanged.connect(self._changed)
        f8.addRow("Voice", self.voice_name)
        self.voice_rate = QComboBox()
        self.voice_rate.addItems(["-20%", "-10%", "+0%", "+10%", "+20%"])
        self.voice_rate.setCurrentText("+0%")
        self.voice_rate.currentTextChanged.connect(self._changed)
        f8.addRow("Speed", self.voice_rate)

        self.bg_music = QCheckBox("Enable background music")
        self.bg_music.toggled.connect(self._on_bg_music_toggled)
        f8.addRow(self.bg_music)

        music_row = QHBoxLayout()
        self.music_path = QLineEdit()
        self.music_path.setPlaceholderText("Select an audio file…")
        self.music_path.setEnabled(False)
        self.music_path.textChanged.connect(self._changed)
        music_row.addWidget(self.music_path)
        self.btn_music_browse = QPushButton("Browse…")
        self.btn_music_browse.setObjectName("secondaryButton")
        self.btn_music_browse.setEnabled(False)
        self.btn_music_browse.clicked.connect(self._browse_music)
        music_row.addWidget(self.btn_music_browse)
        f8.addRow("Music file", music_row)

        self.music_volume = QSlider(Qt.Orientation.Horizontal)
        self.music_volume.setRange(5, 100)
        self.music_volume.setValue(30)
        self.music_volume.setEnabled(False)
        self.music_volume.valueChanged.connect(self._changed)
        self.lbl_music_vol = QLabel("30%")
        vol_row = QHBoxLayout()
        vol_row.addWidget(self.music_volume)
        vol_row.addWidget(self.lbl_music_vol)
        self.music_volume.valueChanged.connect(
            lambda v: self.lbl_music_vol.setText(f"{v}%")
        )
        f8.addRow("Volume", vol_row)

        p8.setLayout(f8)
        self.stack.addWidget(p8)

        # 9 Layout
        p9 = QWidget()
        f9 = form()
        hint = QLabel("Use the YouTube / Reel buttons\nabove the preview.")
        hint.setStyleSheet("color:#64748b;font-size:12px;")
        f9.addRow(hint)
        p9.setLayout(f9)
        self.stack.addWidget(p9)

        # 10 YouTube Cover
        p10 = QWidget()
        f10 = form()
        self.cover_title = QLineEdit("Class Quiz")
        self.cover_title.textChanged.connect(self._cover_changed)
        f10.addRow("Title", self.cover_title)
        self.cover_subject = QLineEdit()
        self.cover_subject.setPlaceholderText("e.g. Science")
        self.cover_subject.textChanged.connect(self._cover_changed)
        f10.addRow("Subject", self.cover_subject)
        self.cover_class = QLineEdit()
        self.cover_class.setPlaceholderText("e.g. Class 10")
        self.cover_class.textChanged.connect(self._cover_changed)
        f10.addRow("Class", self.cover_class)
        self.cover_lesson = QLineEdit()
        self.cover_lesson.setPlaceholderText("e.g. Chapter 3")
        self.cover_lesson.textChanged.connect(self._cover_changed)
        f10.addRow("Lesson", self.cover_lesson)
        self.cover_school = QLineEdit()
        self.cover_school.setPlaceholderText("School / channel (optional)")
        self.cover_school.textChanged.connect(self._cover_changed)
        f10.addRow("School", self.cover_school)
        self.cover_show_count = QCheckBox("Show question count")
        self.cover_show_count.setChecked(True)
        self.cover_show_count.toggled.connect(self._cover_changed)
        f10.addRow(self.cover_show_count)

        self.cover_bg1 = ColorButton("#0f172a")
        self.cover_bg1.color_changed.connect(self._cover_changed)
        f10.addRow("Background", self.cover_bg1)
        self.cover_bg2 = ColorButton("#1e293b")
        self.cover_bg2.color_changed.connect(self._cover_changed)
        f10.addRow("Background 2", self.cover_bg2)
        self.cover_accent = ColorButton("#0d9488")
        self.cover_accent.color_changed.connect(self._cover_changed)
        f10.addRow("Accent", self.cover_accent)
        self.cover_title_color = ColorButton("#ffffff")
        self.cover_title_color.color_changed.connect(self._cover_changed)
        f10.addRow("Title color", self.cover_title_color)
        self.cover_sub_color = ColorButton("#94a3b8")
        self.cover_sub_color.color_changed.connect(self._cover_changed)
        f10.addRow("Lesson color", self.cover_sub_color)
        self.cover_meta_color = ColorButton("#e2e8f0")
        self.cover_meta_color.color_changed.connect(self._cover_changed)
        f10.addRow("Meta color", self.cover_meta_color)

        self.cover_title_size = QSpinBox()
        self.cover_title_size.setRange(18, 72)
        self.cover_title_size.setValue(42)
        self.cover_title_size.valueChanged.connect(self._cover_changed)
        f10.addRow("Title size", self.cover_title_size)
        self.cover_lesson_size = QSpinBox()
        self.cover_lesson_size.setRange(12, 40)
        self.cover_lesson_size.setValue(22)
        self.cover_lesson_size.valueChanged.connect(self._cover_changed)
        f10.addRow("Lesson size", self.cover_lesson_size)
        self.cover_meta_size = QSpinBox()
        self.cover_meta_size.setRange(12, 32)
        self.cover_meta_size.setValue(18)
        self.cover_meta_size.valueChanged.connect(self._cover_changed)
        f10.addRow("Meta size", self.cover_meta_size)

        self.cover_font = QComboBox()
        self.cover_font.addItems(["Segoe UI", "Arial", "Noto Sans", "Georgia", "Tahoma"])
        self.cover_font.currentTextChanged.connect(self._cover_changed)
        f10.addRow("Font", self.cover_font)

        self.cover_align = QComboBox()
        self.cover_align.addItem("Left", "left")
        self.cover_align.addItem("Center", "center")
        self.cover_align.addItem("Right", "right")
        self.cover_align.setCurrentIndex(1)  # Center default
        self.cover_align.currentIndexChanged.connect(self._cover_changed)
        f10.addRow("Text position", self.cover_align)

        self.cover_show_logo = QCheckBox("Show logo")
        self.cover_show_logo.toggled.connect(self._on_cover_logo_toggled)
        f10.addRow(self.cover_show_logo)
        logo_row = QHBoxLayout()
        self.cover_logo_path = QLineEdit()
        self.cover_logo_path.setPlaceholderText("PNG or JPG…")
        self.cover_logo_path.setEnabled(False)
        self.cover_logo_path.textChanged.connect(self._cover_changed)
        logo_row.addWidget(self.cover_logo_path)
        self.btn_cover_logo = QPushButton("Browse…")
        self.btn_cover_logo.setObjectName("secondaryButton")
        self.btn_cover_logo.setEnabled(False)
        self.btn_cover_logo.clicked.connect(self._browse_cover_logo)
        logo_row.addWidget(self.btn_cover_logo)
        f10.addRow("Logo file", logo_row)

        self.btn_cover_from_theme = QPushButton("Match current theme colors")
        self.btn_cover_from_theme.setObjectName("secondaryButton")
        self.btn_cover_from_theme.clicked.connect(self._cover_from_theme)
        f10.addRow(self.btn_cover_from_theme)

        self.btn_cover_export = QPushButton("Generate cover PNG…")
        self.btn_cover_export.clicked.connect(self._export_cover_png)
        f10.addRow(self.btn_cover_export)

        p10.setLayout(f10)
        # wrap in scroll for long form
        cover_scroll = QScrollArea()
        cover_scroll.setWidgetResizable(True)
        cover_scroll.setFrameShape(QFrame.Shape.NoFrame)
        cover_scroll.setWidget(p10)
        self.stack.addWidget(cover_scroll)

    def _on_nav(self, row: int):
        if row < 0:
            return
        self.stack.setCurrentIndex(row)
        self.settings_title.setText(self.SECTIONS[row])
        cover_mode = row == 10  # YouTube Cover
        if hasattr(self, "cover_preview_frame"):
            self.cover_preview_frame.setVisible(cover_mode)
        # Hide question canvas / mode toggles in cover mode
        for w in (getattr(self, "canvas_frame", None), self.btn_mode_q, self.btn_mode_intro,
                  self.btn_mode_outro, self.btn_yt, self.btn_reel):
            if w is not None:
                try:
                    w.setVisible(not cover_mode)
                except Exception:
                    pass
        if hasattr(self, "timing_legend"):
            self.timing_legend.setVisible(not cover_mode)
        if cover_mode:
            self._refresh_cover_preview()
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, self._refresh_cover_preview)
            return
        # Auto-switch preview mode for intro/outro/question styles
        if row == 6:
            self._set_preview_mode("intro", sync_nav=False)
        elif row == 7:
            self._set_preview_mode("outro", sync_nav=False)
        elif row in (3, 4, 5):
            self._set_preview_mode("question", sync_nav=False)

    def _set_preview_mode(self, mode: str, sync_nav: bool = True):
        """Switch live preview mode and (optionally) open matching settings panel."""
        self.canvas.set_show_mode(mode)
        # Exclusive button state
        self.btn_mode_q.setChecked(mode == "question")
        self.btn_mode_intro.setChecked(mode == "intro")
        self.btn_mode_outro.setChecked(mode == "outro")
        self.btn_mode_q.setObjectName("" if mode == "question" else "secondaryButton")
        self.btn_mode_intro.setObjectName("" if mode == "intro" else "secondaryButton")
        self.btn_mode_outro.setObjectName("" if mode == "outro" else "secondaryButton")
        for b in (self.btn_mode_q, self.btn_mode_intro, self.btn_mode_outro):
            b.style().unpolish(b)
            b.style().polish(b)
        if sync_nav:
            # Map mode → left-nav / right settings section
            target = {"intro": 6, "outro": 7, "question": 3}.get(mode)
            if target is not None and self.nav.currentRow() != target:
                self.nav.blockSignals(True)
                self.nav.setCurrentRow(target)
                self.nav.blockSignals(False)
                self.stack.setCurrentIndex(target)
                self.settings_title.setText(self.SECTIONS[target])

    def _set_fmt(self, fmt: str):
        self.canvas.set_format(fmt)
        self.config.format = fmt
        self.btn_yt.setChecked(fmt == "youtube")
        self.btn_reel.setChecked(fmt == "reel")
        self.btn_yt.setObjectName("" if fmt == "youtube" else "secondaryButton")
        self.btn_reel.setObjectName("" if fmt == "reel" else "secondaryButton")
        for b in (self.btn_yt, self.btn_reel):
            b.style().unpolish(b)
            b.style().polish(b)
        self.format_changed.emit(fmt)
        self._changed()

    def _populate_voices(self, lang: str):
        self.voice_name.clear()
        if lang == "Tamil":
            self.voice_name.addItems(["ta-IN-PallaviNeural", "ta-IN-ValluvarNeural"])
        else:
            self.voice_name.addItems([
                "en-IN-NeerjaNeural", "en-IN-PrabhatNeural",
                "en-US-JennyNeural", "en-US-GuyNeural",
            ])

    def _on_voice_lang(self, lang: str):
        self._populate_voices(lang)
        self._changed()

    def _on_bg_music_toggled(self, checked: bool):
        self.music_path.setEnabled(checked)
        self.btn_music_browse.setEnabled(checked)
        self.music_volume.setEnabled(checked)
        self._changed()

    def _browse_music(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Music",
            self.music_path.text() or str(Path.home()),
            "Audio (*.mp3 *.wav *.m4a *.ogg *.flac);;All (*)",
        )
        if path:
            self.music_path.setText(path)
            self._changed()

    def _on_intro_logo_toggled(self, checked: bool):
        self.intro_logo_path.setEnabled(checked)
        self.btn_intro_logo.setEnabled(checked)
        self._changed()

    def _browse_intro_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo Image",
            self.intro_logo_path.text() or str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All (*)",
        )
        if path:
            self.intro_logo_path.setText(path)
            self._changed()

    def _changed(self, *a):
        if getattr(self, "_loading", False):
            return
        self._save()
        self.canvas.set_config(self.config)
        self.config_changed.emit(self.config)

    def _save(self):
        c = self.config
        if hasattr(self, "cover_title"):
            self._save_cover_to_config()
        c.background.type = self.bg_type.currentText()
        c.background.color = self.bg_color.color()
        c.background.color2 = self.bg_color2.color()
        c.border.enabled = self.border_enabled.isChecked()
        c.border.thickness = self.border_thickness.value()
        c.border.color = self.border_color.color()
        c.border.radius = self.border_radius.value()
        c.question.color = self.q_color.color()
        c.question.font_size = self.q_size.value()
        c.question.bold = self.q_bold.isChecked()
        c.answers.color = self.a_color.color()
        c.answers.font_size = self.a_size.value()
        c.option_bg = self.option_bg.color()
        c.correct_bg = self.correct_bg.color()
        c.intervals.after_question = self.int_after_q.value()
        c.intervals.between_options = self.int_between.value()
        c.intervals.before_answer = self.int_before_ans.value()
        c.intervals.answer_duration = self.int_ans_dur.value()
        c.intervals.before_intro = self.int_before_intro.value()
        c.intervals.after_intro = self.int_after_intro.value()
        c.intervals.after_answer = self.int_after_ans.value()
        c.intro.enabled = self.intro_enabled.isChecked()
        c.intro.title = self.intro_title.text()
        c.intro.subtitle = self.intro_subtitle.text()
        c.intro.duration = self.intro_duration.value()
        c.intro.background_color = self.intro_bg_color.color()
        c.intro.title_color = self.intro_title_color.color()
        c.intro.subtitle_color = self.intro_subtitle_color.color()
        c.intro.title_size = self.intro_title_size.value()
        c.intro.subtitle_size = self.intro_subtitle_size.value()
        c.intro.show_logo = self.intro_show_logo.isChecked()
        c.intro.logo_path = self.intro_logo_path.text().strip()
        c.outro.enabled = self.outro_enabled.isChecked()
        c.outro.title = self.outro_title.text()
        c.outro.subtitle = self.outro_subtitle.text()
        c.outro.duration = self.outro_duration.value()
        c.outro.background_color = self.outro_bg_color.color()
        c.outro.title_color = self.outro_title_color.color()
        c.outro.subtitle_color = self.outro_subtitle_color.color()
        c.outro.title_size = self.outro_title_size.value()
        c.outro.subtitle_size = self.outro_subtitle_size.value()
        c.voice.language = "ta" if self.voice_lang.currentText() == "Tamil" else "en"
        c.voice.voice_name = self.voice_name.currentText()
        c.voice.rate = self.voice_rate.currentText()
        c.voice.background_music = self.bg_music.isChecked()
        c.voice.music_path = self.music_path.text().strip()
        c.voice.music_volume = self.music_volume.value() / 100.0

    def _load_all(self):
        """Push config → widgets without firing _changed mid-load."""
        self._loading = True
        c = self.config
        self.bg_type.setCurrentText(c.background.type)
        self.bg_color.set_color(c.background.color)
        self.bg_color2.set_color(c.background.color2)
        self.border_enabled.setChecked(c.border.enabled)
        self.border_thickness.setValue(c.border.thickness)
        self.border_color.set_color(c.border.color)
        self.border_radius.setValue(c.border.radius)
        self.q_color.set_color(c.question.color)
        self.q_size.setValue(c.question.font_size)
        self.q_bold.setChecked(c.question.bold)
        self.a_color.set_color(c.answers.color)
        self.a_size.setValue(c.answers.font_size)
        self.option_bg.set_color(c.option_bg)
        self.correct_bg.set_color(c.correct_bg)
        self.int_after_q.setValue(c.intervals.after_question)
        self.int_between.setValue(c.intervals.between_options)
        self.int_before_ans.setValue(c.intervals.before_answer)
        self.int_ans_dur.setValue(c.intervals.answer_duration)
        self.int_before_intro.setValue(getattr(c.intervals, "before_intro", 2.0))
        self.int_after_intro.setValue(getattr(c.intervals, "after_intro", 3.0))
        self.int_after_ans.setValue(getattr(c.intervals, "after_answer", 3.0))
        self.intro_enabled.setChecked(c.intro.enabled)
        self.intro_title.setText(c.intro.title)
        self.intro_subtitle.setText(c.intro.subtitle)
        self.intro_duration.setValue(c.intro.duration)
        self.intro_bg_color.set_color(c.intro.background_color)
        self.intro_title_color.set_color(c.intro.title_color)
        self.intro_subtitle_color.set_color(getattr(c.intro, "subtitle_color", "#94a3b8"))
        self.intro_title_size.setValue(c.intro.title_size)
        self.intro_subtitle_size.setValue(getattr(c.intro, "subtitle_size", 24))
        self.intro_show_logo.setChecked(bool(c.intro.show_logo))
        self.intro_logo_path.setText(c.intro.logo_path or "")
        self.intro_logo_path.setEnabled(bool(c.intro.show_logo))
        self.btn_intro_logo.setEnabled(bool(c.intro.show_logo))
        self.outro_enabled.setChecked(c.outro.enabled)
        self.outro_title.setText(c.outro.title)
        self.outro_subtitle.setText(c.outro.subtitle)
        self.outro_duration.setValue(c.outro.duration)
        self.outro_bg_color.set_color(c.outro.background_color)
        self.outro_title_color.set_color(c.outro.title_color)
        self.outro_subtitle_color.set_color(getattr(c.outro, "subtitle_color", "#94a3b8"))
        self.outro_title_size.setValue(c.outro.title_size)
        self.outro_subtitle_size.setValue(getattr(c.outro, "subtitle_size", 22))
        self.voice_lang.setCurrentText("Tamil" if c.voice.language == "ta" else "English")
        self._populate_voices(self.voice_lang.currentText())
        idx = self.voice_name.findText(c.voice.voice_name)
        if idx >= 0:
            self.voice_name.setCurrentIndex(idx)
        self.voice_rate.setCurrentText(c.voice.rate)
        self.bg_music.setChecked(c.voice.background_music)
        self.music_path.setText(c.voice.music_path or "")
        vol = int(round((c.voice.music_volume or 0.3) * 100))
        self.music_volume.setValue(max(5, min(100, vol)))
        self.lbl_music_vol.setText(f"{self.music_volume.value()}%")
        self.music_path.setEnabled(c.voice.background_music)
        self.btn_music_browse.setEnabled(c.voice.background_music)
        self.music_volume.setEnabled(c.voice.background_music)
        if hasattr(self, "cover_title"):
            self._load_cover_fields()
        self._loading = False
        # Force preview to the freshly loaded config (including correct_bg / card_bg)
        self.canvas.set_config(c)
        self.canvas.update()


    def _cover_changed(self, *a):
        if getattr(self, "_loading", False):
            return
        self._save_cover_to_config()
        self._refresh_cover_preview()
        self.config_changed.emit(self.config)

    def _save_cover_to_config(self):
        if not hasattr(self.config, "cover") or self.config.cover is None:
            self.config.cover = CoverSettings()
        c = self.config.cover
        c.title = self.cover_title.text().strip() or "Class Quiz"
        c.subject = self.cover_subject.text().strip()
        c.class_name = self.cover_class.text().strip()
        c.lesson = self.cover_lesson.text().strip()
        c.school = self.cover_school.text().strip()
        c.show_question_count = self.cover_show_count.isChecked()
        c.background_color = self.cover_bg1.color()
        c.background_color2 = self.cover_bg2.color()
        c.accent_color = self.cover_accent.color()
        c.title_color = self.cover_title_color.color()
        c.subtitle_color = self.cover_sub_color.color()
        c.meta_color = self.cover_meta_color.color()
        c.title_size = self.cover_title_size.value()
        c.lesson_size = self.cover_lesson_size.value()
        c.meta_size = self.cover_meta_size.value()
        c.font_family = self.cover_font.currentText()
        c.text_align = self.cover_align.currentData() or "center"
        c.show_logo = self.cover_show_logo.isChecked()
        c.logo_path = self.cover_logo_path.text().strip()

    def _load_cover_fields(self):
        c = getattr(self.config, "cover", None) or CoverSettings()
        self.cover_title.setText(c.title or "Class Quiz")
        self.cover_subject.setText(c.subject or "")
        self.cover_class.setText(c.class_name or "")
        self.cover_lesson.setText(c.lesson or "")
        self.cover_school.setText(c.school or "")
        self.cover_show_count.setChecked(bool(getattr(c, "show_question_count", True)))
        self.cover_bg1.set_color(getattr(c, "background_color", "#0f172a"))
        self.cover_bg2.set_color(getattr(c, "background_color2", "#1e293b"))
        self.cover_accent.set_color(getattr(c, "accent_color", "#0d9488"))
        self.cover_title_color.set_color(getattr(c, "title_color", "#ffffff"))
        self.cover_sub_color.set_color(getattr(c, "subtitle_color", "#94a3b8"))
        self.cover_meta_color.set_color(getattr(c, "meta_color", "#e2e8f0"))
        self.cover_title_size.setValue(int(getattr(c, "title_size", 42)))
        self.cover_lesson_size.setValue(int(getattr(c, "lesson_size", 22)))
        self.cover_meta_size.setValue(int(getattr(c, "meta_size", 18)))
        font = getattr(c, "font_family", "Segoe UI") or "Segoe UI"
        idx = self.cover_font.findText(font)
        if idx >= 0:
            self.cover_font.setCurrentIndex(idx)
        align = getattr(c, "text_align", "center") or "center"
        aidx = self.cover_align.findData(align)
        if aidx < 0:
            aidx = self.cover_align.findText(align.capitalize())
        if aidx >= 0:
            self.cover_align.setCurrentIndex(aidx)
        self.cover_show_logo.setChecked(bool(getattr(c, "show_logo", False)))
        self.cover_logo_path.setText(getattr(c, "logo_path", "") or "")
        self.cover_logo_path.setEnabled(self.cover_show_logo.isChecked())
        self.btn_cover_logo.setEnabled(self.cover_show_logo.isChecked())

    def _refresh_cover_preview(self):
        if not hasattr(self, "cover_preview_label"):
            return
        from core.cover_art import cover_preview_pixmap
        self._save_cover_to_config()
        n = len(getattr(self, "mcqs", None) or [])
        # Match Live Preview canvas area (~16:9 inside the same card)
        lbl = self.cover_preview_label
        mw = max(480, lbl.width() - 16) if lbl.width() > 40 else 720
        mh = max(270, lbl.height() - 16) if lbl.height() > 40 else 405
        pm = cover_preview_pixmap(
            self.config.cover, question_count=n, max_width=mw, max_height=mh
        )
        lbl.setPixmap(pm)

    def _cover_from_theme(self):
        c = self.config
        self.cover_bg1.set_color(c.background.color)
        self.cover_bg2.set_color(c.background.color2 or c.background.color)
        self.cover_accent.set_color(c.border.color)
        self.cover_title_color.set_color(c.question.color if c.question.color else "#ffffff")
        self._cover_changed()

    def _on_cover_logo_toggled(self, checked: bool):
        self.cover_logo_path.setEnabled(checked)
        self.btn_cover_logo.setEnabled(checked)
        self._cover_changed()

    def _browse_cover_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo Image",
            self.cover_logo_path.text() or str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All (*)",
        )
        if path:
            self.cover_logo_path.setText(path)
            self._cover_changed()

    def _export_cover_png(self):
        from core.cover_art import render_youtube_cover
        self._save_cover_to_config()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save YouTube Cover",
            str(Path.home() / "quiz_cover.png"),
            "PNG Image (*.png)",
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        n = len(getattr(self, "mcqs", None) or [])
        try:
            out = render_youtube_cover(path, cover=self.config.cover, question_count=n)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Cover saved", f"Saved:\n{out}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Cover art", str(e))

    def open_cover_section(self):
        """Jump to YouTube Cover settings (from menu / Export)."""
        idx = 10
        if idx < len(self.SECTIONS):
            self.nav.setCurrentRow(idx)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, self._refresh_cover_preview)

    def _apply_template(self, name: str):
        factory = TEMPLATES.get(name)
        if not factory:
            return
        # Preserve voice/audio — themes are visual only; never reset language mid-project
        prev_voice = self.config.voice
        prev_intervals = self.config.intervals
        prev_format = self.config.format
        prev_quality = self.config.quality
        prev_codec = getattr(self.config, "codec", "auto")
        prev_cover = getattr(self.config, "cover", None)
        self.config = factory() if name != "Default" else DesignConfig()
        self.config.voice = prev_voice
        self.config.intervals = prev_intervals
        self.config.format = prev_format
        self.config.quality = prev_quality
        self.config.codec = prev_codec
        if prev_cover is not None:
            self.config.cover = prev_cover
        self.template_combo.blockSignals(True)
        idx = self.template_combo.findText(name)
        if idx >= 0:
            self.template_combo.setCurrentIndex(idx)
        self._load_all()
        self.template_combo.blockSignals(False)
        self.canvas.set_config(self.config)
        self.canvas.update()
        self.config_changed.emit(self.config)
        if hasattr(self, "theme_gallery"):
            self.theme_gallery.set_current(name)

    def _apply_intro_theme(self, name: str):
        data = INTRO_THEMES.get(name)
        if not data:
            return
        self.intro_title.blockSignals(True)
        self.intro_subtitle.blockSignals(True)
        self.intro_title.setText(data.get("title", ""))
        self.intro_subtitle.setText(data.get("subtitle", ""))
        self.intro_bg_color.set_color(data.get("background_color", "#0f172a"))
        self.intro_title_color.set_color(data.get("title_color", "#ffffff"))
        self.intro_subtitle_color.set_color(data.get("subtitle_color", "#94a3b8"))
        self.intro_title_size.setValue(int(data.get("title_size", 48)))
        if hasattr(self, "intro_subtitle_size"):
            self.intro_subtitle_size.setValue(int(data.get("subtitle_size", 24)))
        self.intro_title.blockSignals(False)
        self.intro_subtitle.blockSignals(False)
        self._changed()

    def _apply_outro_theme(self, name: str):
        data = OUTRO_THEMES.get(name)
        if not data:
            return
        self.outro_title.blockSignals(True)
        self.outro_subtitle.blockSignals(True)
        self.outro_title.setText(data.get("title", ""))
        self.outro_subtitle.setText(data.get("subtitle", ""))
        self.outro_bg_color.set_color(data.get("background_color", "#0f172a"))
        self.outro_title_color.set_color(data.get("title_color", "#ffffff"))
        self.outro_subtitle_color.set_color(data.get("subtitle_color", "#94a3b8"))
        self.outro_title_size.setValue(int(data.get("title_size", 40)))
        if hasattr(self, "outro_subtitle_size"):
            self.outro_subtitle_size.setValue(int(data.get("subtitle_size", 22)))
        self.outro_title.blockSignals(False)
        self.outro_subtitle.blockSignals(False)
        self._changed()

    def set_mcqs(self, mcqs: List[MCQ]):
        self.mcqs = mcqs or []
        if self.mcqs:
            self.canvas.set_mcq(self.mcqs[0], 0, len(self.mcqs))
        else:
            self.canvas.set_mcq(None)
        self.canvas.set_config(self.config)

    def set_config(self, config: DesignConfig):
        self.config = config
        self._load_all()

    def get_config(self) -> DesignConfig:
        self._save()
        return self.config

    def apply_content_language(self, lang: str):
        """Auto-select TTS voice language when content language is detected."""
        target = "Tamil" if lang and (
            lang.lower().startswith("ta") or lang.lower() == "tamil"
        ) else "English"
        changed = self.voice_lang.currentText() != target
        if changed:
            self.voice_lang.setCurrentText(target)  # triggers _on_voice_lang → voices + _changed
        else:
            # Still ensure a valid voice id for that language is selected
            self._populate_voices(target)
            if target == "Tamil" and not (self.voice_name.currentText() or "").startswith("ta"):
                idx = self.voice_name.findText("ta-IN-PallaviNeural")
                if idx >= 0:
                    self.voice_name.setCurrentIndex(idx)
                self._changed()
