# LEGACY: unused by MainWindow (DesignWorkspace is the active design UI).
"""
Design Panel - Professional compact form (PyQt-realistic).
Two-column groups, no empty stretch, scrollable.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFormLayout, QSpinBox, QDoubleSpinBox,
    QLineEdit, QCheckBox, QComboBox, QColorDialog, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.design_config import DesignConfig
from core.templates import TEMPLATES


class ColorButton(QPushButton):
    """Color swatch — objectName ColorSwatch so theme does not override fill."""
    color_changed = pyqtSignal(str)

    def __init__(self, color="#ffffff", parent=None):
        super().__init__(parent)
        self._color = color
        self.setObjectName("ColorSwatch")
        self.setFixedSize(40, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to choose color")
        self.clicked.connect(self._pick)
        self._style()

    def _style(self):
        # Explicit fill + border; do not inherit QPushButton teal
        self.setStyleSheet(
            f"""
            QPushButton#ColorSwatch {{
                background-color: {self._color};
                border: 2px solid #94a3b8;
                border-radius: 6px;
                min-width: 40px;
                max-width: 40px;
                min-height: 28px;
                max-height: 28px;
                padding: 0px;
            }}
            QPushButton#ColorSwatch:hover {{
                border: 2px solid #0d9488;
            }}
            """
        )

    def _pick(self):
        # Clear app stylesheet while the dialog is open so labels/buttons stay readable
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        old_ss = app.styleSheet() if app else ""
        if app:
            app.setStyleSheet("")
        try:
            c = QColorDialog.getColor(
                QColor(self._color), self, "Select Color",
                QColorDialog.ColorDialogOption.DontUseNativeDialog,
            )
        finally:
            if app:
                app.setStyleSheet(old_ss)
        if c.isValid():
            self._color = c.name()
            self._style()
            self.color_changed.emit(self._color)

    def color(self):
        return self._color

    def set_color(self, c):
        self._color = c or "#000000"
        self._style()


class DesignPanel(QWidget):
    config_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = DesignConfig()
        self._build()
        self._load()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 12)
        outer.setSpacing(8)

        head = QHBoxLayout()
        t = QLabel("Design Styles")
        t.setObjectName("sectionTitle")
        head.addWidget(t)
        head.addStretch()
        head.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(180)
        for n in TEMPLATES:  # Default + A–Z
            self.template_combo.addItem(n)
        self.template_combo.currentTextChanged.connect(self._apply_template)
        head.addWidget(self.template_combo)
        outer.addLayout(head)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        grid = QGridLayout(body)
        grid.setSpacing(10)
        grid.setContentsMargins(0, 4, 4, 4)

        # Row 0: Background | Border
        grid.addWidget(self._bg_group(), 0, 0)
        grid.addWidget(self._border_group(), 0, 1)

        # Row 1: Question | Answers
        grid.addWidget(self._question_group(), 1, 0)
        grid.addWidget(self._answers_group(), 1, 1)

        # Row 2: Intervals | Intro
        grid.addWidget(self._intervals_group(), 2, 0)
        grid.addWidget(self._intro_group(), 2, 1)

        # Row 3: Outro | Voice
        grid.addWidget(self._outro_group(), 3, 0)
        grid.addWidget(self._voice_group(), 3, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        row = QHBoxLayout()
        btn = QPushButton("Reset Defaults")
        btn.setObjectName("secondaryButton")
        btn.clicked.connect(self._reset)
        row.addWidget(btn)
        row.addStretch()
        outer.addLayout(row)

    def _fg(self):
        f = QFormLayout()
        f.setHorizontalSpacing(10)
        f.setVerticalSpacing(6)
        f.setContentsMargins(10, 8, 10, 10)
        f.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        return f

    def _bg_group(self):
        g = QGroupBox("Background")
        f = self._fg()
        self.bg_type = QComboBox()
        self.bg_type.addItems(["solid", "gradient"])
        self.bg_type.setFixedWidth(120)
        self.bg_type.currentTextChanged.connect(self._emit)
        f.addRow("Type", self.bg_type)
        self.bg_color = ColorButton("#0f172a")
        self.bg_color.color_changed.connect(self._emit)
        f.addRow("Background color", self.bg_color)
        self.bg_color2 = ColorButton("#1e293b")
        self.bg_color2.color_changed.connect(self._emit)
        f.addRow("Gradient 2nd color", self.bg_color2)
        g.setLayout(f)
        return g

    def _border_group(self):
        g = QGroupBox("Border")
        f = self._fg()
        self.border_enabled = QCheckBox("Show border")
        self.border_enabled.setChecked(True)
        self.border_enabled.toggled.connect(self._emit)
        f.addRow(self.border_enabled)
        self.border_thickness = QSpinBox()
        self.border_thickness.setRange(0, 20)
        self.border_thickness.setValue(4)
        self.border_thickness.setFixedWidth(70)
        self.border_thickness.valueChanged.connect(self._emit)
        f.addRow("Thickness", self.border_thickness)
        self.border_color = ColorButton("#0d9488")
        self.border_color.color_changed.connect(self._emit)
        f.addRow("Border color", self.border_color)
        self.border_radius = QSpinBox()
        self.border_radius.setRange(0, 40)
        self.border_radius.setValue(16)
        self.border_radius.setFixedWidth(70)
        self.border_radius.valueChanged.connect(self._emit)
        f.addRow("Radius", self.border_radius)
        g.setLayout(f)
        return g

    def _question_group(self):
        g = QGroupBox("Question Style")
        f = self._fg()
        self.q_color = ColorButton("#f1f5f9")
        self.q_color.color_changed.connect(self._emit)
        f.addRow("Question text color", self.q_color)
        self.q_size = QSpinBox()
        self.q_size.setRange(12, 72)
        self.q_size.setValue(26)
        self.q_size.setFixedWidth(70)
        self.q_size.valueChanged.connect(self._emit)
        f.addRow("Font size", self.q_size)
        self.q_bold = QCheckBox("Bold")
        self.q_bold.setChecked(True)
        self.q_bold.toggled.connect(self._emit)
        f.addRow(self.q_bold)
        g.setLayout(f)
        return g

    def _answers_group(self):
        g = QGroupBox("Answers Style")
        f = self._fg()
        self.a_color = ColorButton("#e2e8f0")
        self.a_color.color_changed.connect(self._emit)
        f.addRow("Text color", self.a_color)
        self.a_size = QSpinBox()
        self.a_size.setRange(12, 48)
        self.a_size.setValue(22)
        self.a_size.setFixedWidth(70)
        self.a_size.valueChanged.connect(self._emit)
        f.addRow("Font size", self.a_size)
        self.option_bg = ColorButton("#334155")
        self.option_bg.color_changed.connect(self._emit)
        f.addRow("Option bg", self.option_bg)
        self.correct_bg = ColorButton("#10b981")
        self.correct_bg.color_changed.connect(self._emit)
        f.addRow("Correct bg", self.correct_bg)
        g.setLayout(f)
        return g

    def _intervals_group(self):
        g = QGroupBox("Intervals (seconds)")
        f = self._fg()
        self.int_after_q = QDoubleSpinBox()
        self.int_after_q.setRange(0, 30)
        self.int_after_q.setSingleStep(0.5)
        self.int_after_q.setDecimals(1)
        self.int_after_q.setValue(1.5)
        self.int_after_q.setFixedWidth(80)
        self.int_after_q.valueChanged.connect(self._emit)
        f.addRow("After question", self.int_after_q)
        self.int_between = QDoubleSpinBox()
        self.int_between.setRange(0, 10)
        self.int_between.setSingleStep(0.5)
        self.int_between.setDecimals(1)
        self.int_between.setValue(1.0)
        self.int_between.setFixedWidth(80)
        self.int_between.valueChanged.connect(self._emit)
        f.addRow("After each option", self.int_between)
        self.int_before_ans = QDoubleSpinBox()
        self.int_before_ans.setRange(0, 60)
        self.int_before_ans.setSingleStep(0.5)
        self.int_before_ans.setDecimals(1)
        self.int_before_ans.setValue(10.0)
        self.int_before_ans.setFixedWidth(80)
        self.int_before_ans.valueChanged.connect(self._emit)
        f.addRow("After all options (countdown)", self.int_before_ans)
        self.int_ans_dur = QDoubleSpinBox()
        self.int_ans_dur.setRange(0.5, 15)
        self.int_ans_dur.setSingleStep(0.5)
        self.int_ans_dur.setDecimals(1)
        self.int_ans_dur.setValue(2.0)
        self.int_ans_dur.setFixedWidth(80)
        self.int_ans_dur.valueChanged.connect(self._emit)
        f.addRow("Answer duration", self.int_ans_dur)
        g.setLayout(f)
        return g

    def _intro_group(self):
        g = QGroupBox("Flash / Intro")
        f = self._fg()
        self.intro_enabled = QCheckBox("Enable intro")
        self.intro_enabled.setChecked(True)
        self.intro_enabled.toggled.connect(self._emit)
        f.addRow(self.intro_enabled)
        self.intro_title = QLineEdit("Quiz Time!")
        self.intro_title.setMaximumWidth(200)
        self.intro_title.textChanged.connect(self._emit)
        f.addRow("Title", self.intro_title)
        self.intro_subtitle = QLineEdit("Test your knowledge")
        self.intro_subtitle.setMaximumWidth(200)
        self.intro_subtitle.textChanged.connect(self._emit)
        f.addRow("Subtitle", self.intro_subtitle)
        self.intro_duration = QDoubleSpinBox()
        self.intro_duration.setRange(1, 15)
        self.intro_duration.setValue(3.0)
        self.intro_duration.setFixedWidth(80)
        self.intro_duration.valueChanged.connect(self._emit)
        f.addRow("Duration", self.intro_duration)
        self.intro_title_color = ColorButton("#ffffff")
        self.intro_title_color.color_changed.connect(self._emit)
        f.addRow("Title color", self.intro_title_color)
        g.setLayout(f)
        return g

    def _outro_group(self):
        g = QGroupBox("Outro")
        f = self._fg()
        self.outro_enabled = QCheckBox("Enable outro")
        self.outro_enabled.setChecked(True)
        self.outro_enabled.toggled.connect(self._emit)
        f.addRow(self.outro_enabled)
        self.outro_title = QLineEdit("Thanks for watching!")
        self.outro_title.setMaximumWidth(200)
        self.outro_title.textChanged.connect(self._emit)
        f.addRow("Title", self.outro_title)
        self.outro_subtitle = QLineEdit("Subscribe for more")
        self.outro_subtitle.setMaximumWidth(200)
        self.outro_subtitle.textChanged.connect(self._emit)
        f.addRow("Subtitle", self.outro_subtitle)
        self.outro_duration = QDoubleSpinBox()
        self.outro_duration.setRange(1, 15)
        self.outro_duration.setValue(3.0)
        self.outro_duration.setFixedWidth(80)
        self.outro_duration.valueChanged.connect(self._emit)
        f.addRow("Duration", self.outro_duration)
        g.setLayout(f)
        return g

    def _voice_group(self):
        g = QGroupBox("Voice & Audio")
        f = self._fg()
        self.voice_lang = QComboBox()
        self.voice_lang.addItems(["English", "Tamil"])
        self.voice_lang.setFixedWidth(120)
        self.voice_lang.currentTextChanged.connect(self._on_voice_lang)
        f.addRow("Language", self.voice_lang)
        self.voice_name = QComboBox()
        self.voice_name.setMinimumWidth(180)
        self._fill_voices("English")
        self.voice_name.currentTextChanged.connect(self._emit)
        f.addRow("Voice", self.voice_name)
        self.voice_rate = QComboBox()
        self.voice_rate.addItems(["-20%", "-10%", "+0%", "+10%", "+20%"])
        self.voice_rate.setCurrentText("+0%")
        self.voice_rate.setFixedWidth(90)
        self.voice_rate.currentTextChanged.connect(self._emit)
        f.addRow("Speed", self.voice_rate)
        self.bg_music = QCheckBox("Background music")
        self.bg_music.toggled.connect(self._emit)
        f.addRow(self.bg_music)
        g.setLayout(f)
        return g

    def _fill_voices(self, lang):
        self.voice_name.clear()
        if lang == "Tamil":
            self.voice_name.addItems(["ta-IN-PallaviNeural", "ta-IN-ValluvarNeural"])
        else:
            self.voice_name.addItems([
                "en-IN-NeerjaNeural", "en-IN-PrabhatNeural",
                "en-US-JennyNeural", "en-US-GuyNeural",
            ])

    def _on_voice_lang(self, lang):
        self._fill_voices(lang)
        self._emit()

    def _emit(self, *a):
        self._save()
        self.config_changed.emit(self.config)

    def _save(self):
        c = self.config
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
        c.intro.enabled = self.intro_enabled.isChecked()
        c.intro.title = self.intro_title.text()
        c.intro.subtitle = self.intro_subtitle.text()
        c.intro.duration = self.intro_duration.value()
        c.intro.title_color = self.intro_title_color.color()
        c.outro.enabled = self.outro_enabled.isChecked()
        c.outro.title = self.outro_title.text()
        c.outro.subtitle = self.outro_subtitle.text()
        c.outro.duration = self.outro_duration.value()
        c.voice.language = "ta" if self.voice_lang.currentText() == "Tamil" else "en"
        c.voice.voice_name = self.voice_name.currentText()
        c.voice.rate = self.voice_rate.currentText()
        c.voice.background_music = self.bg_music.isChecked()

    def _load(self):
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
        self.intro_enabled.setChecked(c.intro.enabled)
        self.intro_title.setText(c.intro.title)
        self.intro_subtitle.setText(c.intro.subtitle)
        self.intro_duration.setValue(c.intro.duration)
        self.intro_title_color.set_color(c.intro.title_color)
        self.outro_enabled.setChecked(c.outro.enabled)
        self.outro_title.setText(c.outro.title)
        self.outro_subtitle.setText(c.outro.subtitle)
        self.outro_duration.setValue(c.outro.duration)
        self.voice_lang.setCurrentText("Tamil" if c.voice.language == "ta" else "English")
        self._fill_voices(self.voice_lang.currentText())
        i = self.voice_name.findText(c.voice.voice_name)
        if i >= 0:
            self.voice_name.setCurrentIndex(i)
        self.voice_rate.setCurrentText(c.voice.rate)
        self.bg_music.setChecked(c.voice.background_music)

    def _apply_template(self, name):
        fac = TEMPLATES.get(name)
        if not fac:
            return
        self.config = fac() if name != "Default" else DesignConfig()
        self.template_combo.blockSignals(True)
        self._load()
        self.template_combo.blockSignals(False)
        self.config_changed.emit(self.config)

    def _reset(self):
        self.config = DesignConfig()
        self._load()
        self.config_changed.emit(self.config)


    def apply_content_language(self, lang: str):
        """Sync voice language when Content detects Tamil/English."""
        if not lang or lang == "—":
            return
        target = "Tamil" if "tamil" in lang.lower() or lang.lower() == "ta" else "English"
        if self.voice_lang.currentText() == target:
            return
        self.voice_lang.blockSignals(True)
        self.voice_lang.setCurrentText(target)
        self.voice_lang.blockSignals(False)
        self._fill_voices(target)
        # pick a sensible default voice for that language
        if target == "Tamil":
            idx = self.voice_name.findText("ta-IN-PallaviNeural")
            if idx >= 0:
                self.voice_name.setCurrentIndex(idx)
        else:
            idx = self.voice_name.findText("en-IN-NeerjaNeural")
            if idx >= 0:
                self.voice_name.setCurrentIndex(idx)
        self._emit()

    def get_config(self):
        self._save()
        return self.config

    def set_config(self, config):
        self.config = config
        self._load()
