"""
Export Panel - Quality presets, generate preview / full video / individual Shorts (Phase 4–5)
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QComboBox, QLineEdit, QFileDialog,
    QProgressBar, QMessageBox, QTextEdit, QFrame, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings

from core.design_config import DesignConfig
from core.mcq_parser import MCQ
from core.video_engine import (
    VideoEngine, detect_encoder, list_available_encoders, QUALITY_PRESETS,
)
from typing import List
import subprocess
import sys


class GenerateWorker(QThread):
    progress = pyqtSignal(int, str)
    finished_ok = pyqtSignal(str, str)
    finished_err = pyqtSignal(str)

    def __init__(self, mcqs, config, output_path, mode: str, parent=None):
        """
        mode: "preview" | "full" | "shorts"
        """
        super().__init__(parent)
        self.mcqs = mcqs
        self.config = config
        self.output_path = output_path
        self.mode = mode
        self.engine = VideoEngine()

    def run(self):
        def cb(pct, msg):
            self.progress.emit(pct, msg)

        try:
            if self.mode == "shorts":
                self._run_shorts(cb)
            else:
                preview_only = self.mode == "preview"
                result = self.engine.generate(
                    self.mcqs, self.config, self.output_path,
                    preview_only=preview_only,
                    progress_cb=cb,
                )
                if result.success:
                    self.finished_ok.emit(result.output_path or "", result.message)
                else:
                    self.finished_err.emit(result.message)
        except Exception as e:
            self.finished_err.emit(str(e))

    def _run_shorts(self, cb):
        out_base = Path(self.output_path)
        if out_base.suffix.lower() == ".mp4":
            out_dir = out_base.parent / (out_base.stem + "_shorts")
        else:
            out_dir = out_base
        out_dir.mkdir(parents=True, exist_ok=True)

        # Force reel format for shorts
        cfg = self.config
        original_fmt = cfg.format
        cfg.format = "reel"

        n = len(self.mcqs)
        paths = []
        for i, mcq in enumerate(self.mcqs):
            if self.engine._cancel:
                self.finished_err.emit("Cancelled by user.")
                cfg.format = original_fmt
                return
            pct = int(100 * i / max(n, 1))
            cb(pct, f"Short {i + 1}/{n}...")
            out = out_dir / f"short_{i + 1:02d}.mp4"
            result = self.engine.generate(
                [mcq], cfg, str(out),
                preview_only=True,
                progress_cb=None,
            )
            if not result.success:
                cfg.format = original_fmt
                self.finished_err.emit(f"Failed on short {i + 1}: {result.message}")
                return
            paths.append(str(out))

        cfg.format = original_fmt
        cb(100, "All Shorts done!")
        self.finished_ok.emit(
            str(out_dir),
            f"Created {len(paths)} Shorts in {out_dir}"
        )

    def cancel(self):
        self.engine.cancel()


class ExportPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mcqs: List[MCQ] = []
        self.config = DesignConfig()
        self.config_provider = None  # optional: () -> DesignConfig
        self.worker: GenerateWorker | None = None
        self._last_output: str = ""
        self._settings = QSettings("EduTools", "ClassQuizMaker")
        self._setup_ui()
        self._restore_last_path()
        self._detect_gpu()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(14)

        # Codec + quality (no page-level title)
        q_group = QGroupBox("Video Quality && Codec")
        q_group.setStyleSheet(
            "QGroupBox{"
            "  margin-top:16px; padding-top:28px; padding-bottom:10px;"
            "  border:1px solid #e2e8f0; border-radius:10px; background:#ffffff;"
            "}"
            "QGroupBox::title{"
            "  subcontrol-origin:margin; subcontrol-position:top left;"
            "  left:6px; top:0px; padding:2px 6px 8px 6px;"
            "  color:#0f766e; background:transparent;"
            "}"
            "QGroupBox QLabel{background:transparent;}"
        )
        q_form = QFormLayout(q_group)
        q_form.setContentsMargins(12, 8, 12, 10)
        q_form.setSpacing(8)

        self.quality = QComboBox()
        self.quality.setMaximumWidth(320)
        self.quality.setAccessibleName("Quality preset")
        for key, meta in QUALITY_PRESETS.items():
            self.quality.addItem(meta["label"], key)
        self.quality.setCurrentIndex(1)
        self.quality.currentIndexChanged.connect(self._on_quality_changed)
        quality_row = QHBoxLayout()
        quality_row.setSpacing(10)
        quality_row.addWidget(self.quality)
        self.quality_hint = QLabel(
            "Classroom — good for projectors · Best — sharpest for YouTube uploads"
        )
        self.quality_hint.setObjectName("mutedLabel")
        self.quality_hint.setWordWrap(True)
        quality_row.addWidget(self.quality_hint, 1)
        q_form.addRow("Quality preset", quality_row)

        self.codec = QComboBox()
        self.codec.setMaximumWidth(320)
        for cid, label in list_available_encoders():
            self.codec.addItem(label, cid)
        codec_row = QHBoxLayout()
        codec_row.setSpacing(10)
        codec_row.addWidget(self.codec)
        self.lbl_encoder = QLabel("")
        self.lbl_encoder.setStyleSheet("color: #64748b; font-size: 11px; background: transparent;")
        codec_row.addWidget(self.lbl_encoder)
        codec_row.addStretch()
        q_form.addRow("Codec", codec_row)
        layout.addWidget(q_group)

        # Output mode
        mode_group = QGroupBox("Output Mode")
        mode_group.setStyleSheet(
            "QGroupBox{"
            "  margin-top:16px; padding-top:28px; padding-bottom:10px;"
            "  border:1px solid #e2e8f0; border-radius:10px; background:#ffffff;"
            "}"
            "QGroupBox::title{"
            "  subcontrol-origin:margin; subcontrol-position:top left;"
            "  left:6px; top:0px; padding:2px 6px 8px 6px;"
            "  color:#0f766e; background:transparent;"
            "}"
            "QGroupBox QLabel{background:transparent;}"
            "QRadioButton{background:transparent; spacing:8px;}"
            "QRadioButton::indicator{width:16px;height:16px;}"
        )
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setContentsMargins(12, 4, 12, 8)
        mode_layout.setSpacing(6)
        self.mode_full = QRadioButton("One long video (all questions)")
        self.mode_full.setChecked(True)
        self.mode_shorts = QRadioButton("Individual Shorts (one file per question, 9:16)")
        self.mode_preview = QRadioButton("Preview only (first question)")
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.mode_full)
        self.mode_group.addButton(self.mode_shorts)
        self.mode_group.addButton(self.mode_preview)
        mode_layout.addWidget(self.mode_full)
        mode_layout.addWidget(self.mode_shorts)
        mode_layout.addWidget(self.mode_preview)
        layout.addWidget(mode_group)

        # Output path + actions on one line
        out_group = QGroupBox("Output")
        out_group.setStyleSheet(
            "QGroupBox{"
            "  margin-top:16px; padding-top:28px; padding-bottom:10px;"
            "  border:1px solid #e2e8f0; border-radius:10px; background:#ffffff;"
            "}"
            "QGroupBox::title{"
            "  subcontrol-origin:margin; subcontrol-position:top left;"
            "  left:6px; top:0px; padding:2px 6px 8px 6px;"
            "  color:#0f766e; background:transparent;"
            "}"
            "QGroupBox QLabel{background:transparent;}"
        )
        out_layout = QVBoxLayout(out_group)
        out_layout.setContentsMargins(12, 8, 12, 10)
        out_layout.setSpacing(10)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        path_lbl = QLabel("File / Folder")
        path_lbl.setStyleSheet("background: transparent;")
        path_row.addWidget(path_lbl)
        self.out_path = QLineEdit(str(Path.home() / "quiz_video.mp4"))
        path_row.addWidget(self.out_path, 1)
        btn_browse = QPushButton("Browse...")
        btn_browse.setObjectName("secondaryButton")
        btn_browse.clicked.connect(self._browse)
        path_row.addWidget(btn_browse)

        self.btn_generate = QPushButton("Generate Video")
        self.btn_generate.setMinimumHeight(36)
        self.btn_generate.setEnabled(False)
        self.btn_generate.setToolTip("Add questions in the Question & Answers tab first")
        self.btn_generate.clicked.connect(self._start)
        path_row.addWidget(self.btn_generate)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.setMinimumHeight(36)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel)
        path_row.addWidget(self.btn_cancel)

        out_layout.addLayout(path_row)

        # Post-export actions (shown after success)
        post_row = QHBoxLayout()
        post_row.setSpacing(8)
        self.btn_open_folder = QPushButton("Open Folder")
        self.btn_open_folder.setObjectName("secondaryButton")
        self.btn_open_folder.setEnabled(False)
        self.btn_open_folder.setAccessibleName("Open output folder")
        self.btn_open_folder.clicked.connect(self._open_folder)
        post_row.addWidget(self.btn_open_folder)
        self.btn_play = QPushButton("Play Video")
        self.btn_play.setObjectName("secondaryButton")
        self.btn_play.setEnabled(False)
        self.btn_play.setAccessibleName("Play output video")
        self.btn_play.clicked.connect(self._play_output)
        post_row.addWidget(self.btn_play)
        self.btn_cover = QPushButton("YouTube Cover…")
        self.btn_cover.setObjectName("secondaryButton")
        self.btn_cover.setAccessibleName("Create YouTube cover image")
        self.btn_cover.setToolTip("Create a 1280×720 cover PNG from the current theme")
        # Wired from MainWindow after panels exist
        post_row.addWidget(self.btn_cover)
        post_row.addStretch()
        out_layout.addLayout(post_row)

        layout.addWidget(out_group)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setAccessibleName("Export progress")
        layout.addWidget(self.progress)

        self.lbl_status = QLabel("Add questions in Question & Answers, then generate here.")
        self.lbl_status.setObjectName("mutedLabel")
        layout.addWidget(self.lbl_status)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(140)
        self.log.setPlaceholderText("Generation log...")
        self.log.setAccessibleName("Generation log")
        layout.addWidget(self.log)

        layout.addStretch()

    def _detect_gpu(self):
        enc, label = detect_encoder()
        self.lbl_encoder.setText(f"Auto detects: {label}")
        self._log(f"Best available encoder: {label}")

    def set_mcqs(self, mcqs: List[MCQ]):
        self.mcqs = mcqs or []
        self._update_generate_enabled()

    def set_config(self, config: DesignConfig):
        self.config = config
        idx = self.quality.findData(config.quality)
        if idx >= 0:
            self.quality.setCurrentIndex(idx)
        codec = getattr(config, "codec", "auto") or "auto"
        cidx = self.codec.findData(codec)
        if cidx >= 0:
            self.codec.setCurrentIndex(cidx)

    def _update_generate_enabled(self):
        busy = self.worker is not None and self.worker.isRunning()
        has_q = bool(self.mcqs)
        self.btn_generate.setEnabled(has_q and not busy)
        if not has_q:
            self.btn_generate.setToolTip("Add questions in the Question & Answers tab first")
        else:
            self.btn_generate.setToolTip("")

    def _browse(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Output Video", self.out_path.text(),
            "MP4 Video (*.mp4);;All Files (*)"
        )
        if path:
            if not path.lower().endswith(".mp4"):
                path += ".mp4"
            self.out_path.setText(path)

    def _log(self, msg: str):
        self.log.append(msg)

    def _current_mode(self) -> str:
        if self.mode_preview.isChecked():
            return "preview"
        if self.mode_shorts.isChecked():
            return "shorts"
        return "full"

    def _start(self):
        if not self.mcqs:
            QMessageBox.warning(self, "No Questions", "Load questions in the Question & Answers tab first.")
            return

        out = self.out_path.text().strip()
        if not out:
            QMessageBox.warning(self, "Output", "Choose an output file path.")
            return

        # Always prefer the latest Design & Preview settings (voice, intervals, theme)
        if callable(getattr(self, "config_provider", None)):
            try:
                fresh = self.config_provider()
                if fresh is not None:
                    self.config = fresh
            except Exception:
                pass
        self.config.quality = self.quality.currentData()
        self.config.codec = self.codec.currentData() or "auto"
        mode = self._current_mode()

        self.btn_generate.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress.setValue(0)
        self.lbl_status.setText("Starting...")
        self._log(f"Starting mode={mode} → {out}")

        self.worker = GenerateWorker(
            self.mcqs, self.config, out, mode=mode, parent=self
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_ok)
        self.worker.finished_err.connect(self._on_err)
        self.worker.start()

    def _cancel(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.lbl_status.setText("Cancelling...")
            self._log("Cancel requested...")

    def _on_progress(self, pct: int, msg: str):
        self.progress.setValue(pct)
        self.lbl_status.setText(msg)
        self._log(msg)

    def _on_ok(self, path: str, message: str):
        self.progress.setValue(100)
        self.lbl_status.setText(message)
        self._log(f"Success: {path}")
        self._last_output = path or ""
        self._settings.setValue("last_output_path", self.out_path.text().strip())
        self._reset_buttons()
        self.btn_open_folder.setEnabled(bool(path))
        # Play only for single video files
        p = Path(path) if path else None
        self.btn_play.setEnabled(bool(p and p.is_file() and p.suffix.lower() == ".mp4"))

    def _on_err(self, message: str):
        self.lbl_status.setText(f"Error: {message}")
        self._log(f"Error: {message}")
        self._reset_buttons()
        QMessageBox.critical(self, "Generation Failed", message)

    def _reset_buttons(self):
        self.btn_cancel.setEnabled(False)
        self.worker = None
        self._update_generate_enabled()

    def _restore_last_path(self):
        last = self._settings.value("last_output_path", "")
        if last:
            self.out_path.setText(str(last))

    def _on_quality_changed(self, _idx=None):
        key = self.quality.currentData()
        tips = {
            "basic": "Fast — smaller file, quicker export (drafts & checks)",
            "standard": "Classroom — recommended for most lessons and projectors",
            "high": "High quality — sharper text, larger file",
            "excellent": "Best quality — slowest export, ideal for YouTube",
        }
        # QUALITY_PRESETS keys may differ; fall back to generic tip
        tip = tips.get(key) or "Classroom is best for most lessons · Best for YouTube uploads"
        if hasattr(self, "quality_hint"):
            self.quality_hint.setText(tip)

    def _open_path(self, path: str):
        try:
            p = Path(path)
            target = str(p if p.is_dir() else p)
            if sys.platform == "darwin":
                subprocess.Popen(["open", target])
            elif sys.platform == "win32":
                if p.is_dir():
                    subprocess.Popen(["explorer", target])
                else:
                    subprocess.Popen(["explorer", "/select,", target])
            else:
                subprocess.Popen(["xdg-open", target])
        except Exception as e:
            self._log(f"Could not open: {e}")

    def _open_folder(self):
        path = self._last_output or self.out_path.text().strip()
        if not path:
            return
        p = Path(path)
        folder = p if p.is_dir() else p.parent
        self._open_path(str(folder))

    def _play_output(self):
        path = self._last_output
        if path and Path(path).is_file():
            self._open_path(path)
