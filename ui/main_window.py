"""
Main Window - Class Quiz Maker
Tabs: Question & Answers | Design & Preview | Export
"""

from pathlib import Path
import json

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QStatusBar,
    QMessageBox, QTabWidget, QFileDialog, QTextBrowser, QDialog,
    QVBoxLayout as QVBox, QPushButton
)
from PyQt6.QtCore import QSettings, Qt, QTimer
from PyQt6.QtGui import QAction

from ui.content_panel import ContentPanel
from ui.design_workspace import DesignWorkspace
from ui.export_panel import ExportPanel
from ui.theme_manager import ThemeManager
from core.design_config import DesignConfig
from core.mcq_parser import MCQ

APP_NAME = "Class Quiz Maker"
ORG_NAME = "EduTools"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 840)
        self.setMinimumSize(1024, 680)

        self.settings = QSettings(ORG_NAME, "ClassQuizMaker")
        self.theme_manager = ThemeManager(self)
        self.design_config = DesignConfig()
        self.project_path: Path | None = None
        self._dirty = False

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._apply_initial_theme()
        self._connect_signals()
        self._setup_autosave()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.content_panel = ContentPanel()
        # && escapes Qt mnemonic so "&" is shown and no letter is underlined
        self.tabs.addTab(self.content_panel, "  Question && Answers  ")

        self.design_workspace = DesignWorkspace()
        self.tabs.addTab(self.design_workspace, "  Design && Preview  ")

        self.export_panel = ExportPanel()
        self.export_panel.config_provider = self.design_workspace.get_config
        if hasattr(self.export_panel, "btn_cover"):
            self.export_panel.btn_cover.clicked.connect(self.create_youtube_cover)
        self.tabs.addTab(self.export_panel, "  Export  ")

        layout.addWidget(self.tabs)

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        act = QAction("Select File...", self)
        act.setShortcut("Ctrl+O")
        act.triggered.connect(self.content_panel.load_file)
        file_menu.addAction(act)

        act = QAction("Add Q&A", self)
        act.setShortcut("Ctrl+A")
        act.triggered.connect(self.content_panel.add_question)
        file_menu.addAction(act)

        act = QAction("Load Sample", self)
        act.triggered.connect(self.content_panel.load_sample)
        file_menu.addAction(act)

        file_menu.addSeparator()

        act = QAction("Save Project...", self)
        act.setShortcut("Ctrl+S")
        act.triggered.connect(self.save_project)
        file_menu.addAction(act)

        act = QAction("Load Project...", self)
        act.setShortcut("Ctrl+Shift+O")
        act.triggered.connect(self.load_project)
        file_menu.addAction(act)

        file_menu.addSeparator()
        act = QAction("Create YouTube Cover...", self)
        act.triggered.connect(self.create_youtube_cover)
        file_menu.addAction(act)

        file_menu.addSeparator()
        act = QAction("Clear All Questions", self)
        act.triggered.connect(self.content_panel.clear_all)
        file_menu.addAction(act)

        file_menu.addSeparator()
        act = QAction("Exit", self)
        act.setShortcut("Ctrl+Q")
        act.triggered.connect(self.close)
        file_menu.addAction(act)

        view_menu = menubar.addMenu("&View")
        act = QAction("Toggle Dark/Light Theme", self)
        act.setShortcut("Ctrl+T")
        act.triggered.connect(self.toggle_theme)
        view_menu.addAction(act)

        help_menu = menubar.addMenu("&Help")
        act = QAction("Q&A Formats", self)
        act.triggered.connect(self.show_qa_formats)
        help_menu.addAction(act)
        act = QAction("About", self)
        act.triggered.connect(self.show_about)
        help_menu.addAction(act)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.lang_label = QLabel("Language: —")
        self.count_label = QLabel("Questions: 0")
        self.format_label = QLabel("Format: YouTube 16:9")
        self.autosave_label = QLabel("")
        self.theme_label = QLabel("Theme: Light")
        self.statusbar.addWidget(self.lang_label, 1)
        self.statusbar.addWidget(self.count_label, 1)
        self.statusbar.addWidget(self.format_label, 1)
        self.statusbar.addWidget(self.autosave_label, 1)
        self.statusbar.addPermanentWidget(self.theme_label)

    def _setup_autosave(self):
        """Autosave every 2 minutes when there is content."""
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(120_000)  # 2 minutes
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()

    def _autosave_path(self) -> Path:
        if self.project_path:
            return self.project_path
        autosave_dir = Path.home() / ".classquiz_maker"
        autosave_dir.mkdir(parents=True, exist_ok=True)
        return autosave_dir / "autosave.vquiz"

    def _project_payload(self) -> dict:
        cfg = self.design_workspace.get_config()
        cfg.quality = self.export_panel.quality.currentData() or cfg.quality
        if hasattr(self.export_panel, "codec"):
            cfg.codec = self.export_panel.codec.currentData() or cfg.codec
        return {
            "version": 1,
            "app": APP_NAME,
            "questions": [
                {"question": m.question, "options": m.options, "correct": m.correct}
                for m in self.content_panel.mcqs
            ],
            "design": cfg.to_dict(),
        }

    def _write_project(self, path: Path, quiet: bool = False) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(self._project_payload(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self._dirty = False
            if quiet:
                from datetime import datetime
                self.autosave_label.setText(
                    f"Autosaved {datetime.now().strftime('%H:%M')}"
                )
            return True
        except Exception as e:
            if not quiet:
                QMessageBox.critical(self, "Save Error", str(e))
            return False

    def _autosave(self):
        if not self.content_panel.mcqs and not self._dirty:
            return
        if not self.content_panel.mcqs:
            return
        path = self._autosave_path()
        self._write_project(path, quiet=True)

    def _mark_dirty(self, *_args):
        self._dirty = True

    def _connect_signals(self):
        self.content_panel.language_changed.connect(self._on_language)
        self.content_panel.question_count_changed.connect(self._on_count)
        self.content_panel.question_count_changed.connect(self._sync_all)
        self.content_panel.question_count_changed.connect(self._mark_dirty)
        self.design_workspace.config_changed.connect(self._on_design)
        self.design_workspace.config_changed.connect(self._mark_dirty)
        self.design_workspace.format_changed.connect(self._on_format)
        self.tabs.currentChanged.connect(self._on_tab)

    def _on_language(self, lang: str):
        self.lang_label.setText(f"Language: {lang}")
        self.design_workspace.apply_content_language(lang)

    def _on_count(self, n: int):
        self.count_label.setText(f"Questions: {n}")

    def _on_format(self, fmt: str):
        self.format_label.setText(
            "Format: YouTube 16:9" if fmt == "youtube" else "Format: Reel 9:16"
        )
        self.design_config.format = fmt

    def _on_design(self, config: DesignConfig):
        self.design_config = config
        self.export_panel.set_config(config)

    def _sync_all(self, _n=None):
        mcqs = self.content_panel.mcqs
        cfg = self.design_config
        self.design_workspace.set_mcqs(mcqs)
        self.design_workspace.set_config(cfg)
        self.export_panel.set_mcqs(mcqs)
        self.export_panel.set_config(cfg)

    def _on_tab(self, index: int):
        text = self.tabs.tabText(index).strip()
        if text in ("Design & Preview", "Export"):
            self._sync_all()

    def _apply_initial_theme(self):
        if self.settings.value("theme", "light") == "dark":
            self.theme_manager.apply_dark()
            self.theme_label.setText("Theme: Dark")
        else:
            self.theme_manager.apply_light()
            self.theme_label.setText("Theme: Light")

    def toggle_theme(self):
        if self.settings.value("theme", "light") == "light":
            self.theme_manager.apply_dark()
            self.settings.setValue("theme", "dark")
            self.theme_label.setText("Theme: Dark")
        else:
            self.theme_manager.apply_light()
            self.settings.setValue("theme", "light")
            self.theme_label.setText("Theme: Light")

    def save_project(self):
        default = str(self.project_path) if self.project_path else str(
            Path.home() / "classquiz_project.vquiz"
        )
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", default,
            "Class Quiz Project (*.vquiz);;JSON (*.json)"
        )
        if not path:
            return
        if not path.lower().endswith((".vquiz", ".json")):
            path += ".vquiz"
        self.project_path = Path(path)
        if self._write_project(self.project_path, quiet=False):
            self.setWindowTitle(f"{APP_NAME} — {self.project_path.name}")
            QMessageBox.information(self, "Saved", f"Saved:\n{path}")

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Project", str(Path.home()),
            "Class Quiz Project (*.vquiz);;JSON (*.json);;All (*)"
        )
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            mcqs = [
                MCQ(q["question"], q["options"], q["correct"])
                for q in data.get("questions", [])
            ]
            self.content_panel.mcqs = mcqs
            self.content_panel._refresh_cards()
            self.content_panel._emit_updates()
            if "design" in data:
                cfg = DesignConfig.from_dict(data["design"])
                self.design_config = cfg
                self.design_workspace.set_config(cfg)
                self.export_panel.set_config(cfg)
            self.project_path = Path(path)
            self.setWindowTitle(f"{APP_NAME} — {self.project_path.name}")
            self._sync_all()
            self._dirty = False
            QMessageBox.information(self, "Loaded", f"{len(mcqs)} questions + design.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def create_youtube_cover(self):
        """Open Design → YouTube Cover for full editor (preview + styles)."""
        # Switch to Design tab
        for i in range(self.tabs.count()):
            if "Design" in self.tabs.tabText(i):
                self.tabs.setCurrentIndex(i)
                break
        if hasattr(self.design_workspace, "open_cover_section"):
            self.design_workspace.open_cover_section()
        # Seed cover colors from theme if still defaults
        try:
            cfg = self.design_workspace.get_config()
            cov = getattr(cfg, "cover", None)
            if cov and (not cov.subject and not cov.lesson):
                if hasattr(self.design_workspace, "_cover_from_theme"):
                    self.design_workspace._cover_from_theme()
        except Exception:
            pass

    def show_qa_formats(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Supported Q&A Formats")
        dlg.resize(560, 480)
        layout = QVBox(dlg)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml("""
        <h2>Supported Q&A Formats</h2>
        <p>Paste or load a <b>.txt</b> file. Separate questions with a blank line.</p>

        <h3>1. Standard (recommended)</h3>
        <pre>
What is the capital of France?
A) London
B) Berlin
C) Paris
D) Madrid
Answer: C
        </pre>

        <h3>2. Dot or colon after letter</h3>
        <pre>
What is 2 + 2?
A. 3
B. 4
C. 5
D. 6
Correct: B
        </pre>

        <h3>3. Numbered question + Tamil answer label</h3>
        <pre>
Q1. இந்தியாவின் தலைநகரம் எது?
A) மும்பை
B) கொல்கத்தா
C) புது தில்லி
D) சென்னை
சரியான பதில்: C
        </pre>

        <h3>4. Minimal (letter only on last line)</h3>
        <pre>
Largest planet in the solar system?
A) Earth
B) Mars
C) Jupiter
D) Venus
C
        </pre>

        <h3>Tips</h3>
        <ul>
          <li>Exactly <b>4 options</b> (A–D) per question.</li>
          <li>Blank line between questions.</li>
          <li>Answer keywords: <code>Answer:</code>, <code>Correct:</code>,
              <code>சரியான பதில்:</code>, or a lone letter on the last line.</li>
          <li>English and Tamil are auto-detected from the text.</li>
        </ul>
        """)
        layout.addWidget(browser)
        btn = QPushButton("Close")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()

    def show_about(self):
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<h3>{APP_NAME}</h3>"
            "<p>Create classroom quiz videos for YouTube and Reels/Shorts.</p>"
            "<p>Built for school teachers — English &amp; Tamil.</p>"
            "<p>Version 1.0.0</p>"
        )

    def closeEvent(self, event):
        # Final quiet autosave on exit if there are questions
        if self.content_panel.mcqs:
            self._write_project(self._autosave_path(), quiet=True)
        super().closeEvent(event)
