"""
Content Panel - Question cards with theme-aware chips, drag-reorder, and undo delete.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QFileDialog, QMessageBox, QSizePolicy,
    QTextEdit, QCheckBox, QListWidget, QListWidgetItem, QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QMimeData, QByteArray
from PyQt6.QtGui import QDrag

from core.mcq_parser import MCQ, parse_mcq_file, parse_mcq_text, detect_language
from ui.question_dialog import QuestionDialog


class QuestionCard(QFrame):
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    move_up_requested = pyqtSignal(int)
    move_down_requested = pyqtSignal(int)

    def __init__(self, index: int, mcq: MCQ, parent=None):
        super().__init__(parent)
        self.index = index
        self.mcq = mcq
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAcceptDrops(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 12, 12)
        layout.setSpacing(8)

        # Row 1: number + question + actions
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        num = QLabel(str(index + 1))
        num.setObjectName("questionBadge")
        num.setFixedSize(28, 28)
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setAccessibleName(f"Question {index + 1}")
        row1.addWidget(num)

        q = QLabel(mcq.question)
        q.setWordWrap(True)
        q.setObjectName("questionText")
        row1.addWidget(q, 1)

        for symbol, tip, name, slot in [
            ("✎", "Edit", "Edit question", lambda: self.edit_requested.emit(self.index)),
            ("✕", "Delete", "Delete question", lambda: self.delete_requested.emit(self.index)),
            ("↑", "Move up", "Move question up", lambda: self.move_up_requested.emit(self.index)),
            ("↓", "Move down", "Move question down", lambda: self.move_down_requested.emit(self.index)),
        ]:
            btn = QPushButton(symbol)
            btn.setObjectName("iconButton")
            btn.setToolTip(tip)
            btn.setAccessibleName(name)
            btn.setMinimumSize(32, 32)
            btn.clicked.connect(slot)
            row1.addWidget(btn)

        layout.addLayout(row1)

        # Row 2: option chips (theme via objectName)
        chips = QHBoxLayout()
        chips.setSpacing(6)
        for i, opt in enumerate(mcq.options):
            letter = chr(65 + i)
            is_ok = letter == mcq.correct
            chip = QLabel(f"{letter}) {opt}")
            chip.setWordWrap(True)
            chip.setObjectName("optionChipCorrect" if is_ok else "optionChip")
            chip.setAccessibleName(
                f"Option {letter}, correct answer" if is_ok else f"Option {letter}"
            )
            chips.addWidget(chip)
        chips.addStretch()
        layout.addLayout(chips)


class QuestionList(QListWidget):
    """List widget supporting internal drag-and-drop reorder of question cards."""

    order_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSpacing(6)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setObjectName("questionList")

    def dropEvent(self, event):
        super().dropEvent(event)
        self.order_changed.emit()


class ContentPanel(QWidget):
    language_changed = pyqtSignal(str)
    question_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mcqs: List[MCQ] = []
        self._undo_stack: List[Tuple[int, MCQ]] = []  # (index, mcq) for last deletes
        self._undo_timer: Optional[QTimer] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 12)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        self.hint_drag = QLabel("Drag cards to reorder · Delete supports Undo")
        self.hint_drag.setObjectName("mutedLabel")
        header.addWidget(self.hint_drag)
        header.addStretch()
        self.raw_checkbox = QCheckBox("Raw Text Mode")
        self.raw_checkbox.setAccessibleName("Raw text mode")
        self.raw_checkbox.toggled.connect(self._toggle_raw_mode)
        header.addWidget(self.raw_checkbox)
        layout.addLayout(header)

        # Empty state
        self.empty_state = QFrame()
        self.empty_state.setObjectName("emptyState")
        el = QVBoxLayout(self.empty_state)
        el.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.setSpacing(14)
        el.setContentsMargins(32, 48, 32, 48)

        empty_title = QLabel("No questions yet")
        empty_title.setObjectName("sectionTitle")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(empty_title)

        empty_hint = QLabel(
            "Start with a sample, open a text file, or add questions one by one.\n"
            "Then open Design & Preview to style, and Export to create your video."
        )
        empty_hint.setObjectName("mutedLabel")
        empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_hint.setWordWrap(True)
        el.addWidget(empty_hint)

        empty_btns = QHBoxLayout()
        empty_btns.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_btns.setSpacing(10)

        b_sample = QPushButton("Load Sample")
        b_sample.setMinimumHeight(36)
        b_sample.setAccessibleName("Load sample questions")
        b_sample.clicked.connect(self.load_sample)
        empty_btns.addWidget(b_sample)

        b_file = QPushButton("Select File")
        b_file.setObjectName("secondaryButton")
        b_file.setMinimumHeight(36)
        b_file.setAccessibleName("Select questions file")
        b_file.clicked.connect(self.load_file)
        empty_btns.addWidget(b_file)

        b_add = QPushButton("Add Q&A")
        b_add.setObjectName("secondaryButton")
        b_add.setMinimumHeight(36)
        b_add.setAccessibleName("Add question")
        b_add.clicked.connect(self.add_question)
        empty_btns.addWidget(b_add)

        el.addLayout(empty_btns)
        layout.addWidget(self.empty_state, 1)

        # Scrollable card list with drag-reorder
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVisible(False)

        self.list_widget = QuestionList()
        self.list_widget.order_changed.connect(self._on_list_reordered)
        self.scroll.setWidget(self.list_widget)
        layout.addWidget(self.scroll, 1)

        # Undo toast bar (hidden by default)
        self.undo_bar = QFrame()
        self.undo_bar.setObjectName("undoBar")
        self.undo_bar.setVisible(False)
        ub = QHBoxLayout(self.undo_bar)
        ub.setContentsMargins(12, 8, 12, 8)
        self.undo_label = QLabel("Question deleted")
        self.undo_label.setObjectName("mutedLabel")
        ub.addWidget(self.undo_label, 1)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.setObjectName("secondaryButton")
        self.btn_undo.setAccessibleName("Undo delete")
        self.btn_undo.clicked.connect(self._undo_delete)
        ub.addWidget(self.btn_undo)
        layout.addWidget(self.undo_bar)

        # Raw editor
        self.raw_editor = QTextEdit()
        self.raw_editor.setPlaceholderText(
            "Paste questions:\n\nQuestion?\nA) ...\nB) ...\nC) ...\nD) ...\nAnswer: C\n"
        )
        self.raw_editor.setVisible(False)
        self.raw_editor.setMinimumHeight(180)
        self.raw_editor.setAccessibleName("Raw questions text")
        layout.addWidget(self.raw_editor)

        self.btn_apply_raw = QPushButton("Apply Raw Text")
        self.btn_apply_raw.setVisible(False)
        self.btn_apply_raw.setAccessibleName("Apply raw text")
        self.btn_apply_raw.clicked.connect(self._apply_raw_text)
        layout.addWidget(self.btn_apply_raw)

    def _toggle_raw_mode(self, checked: bool):
        self.empty_state.setVisible(False)
        self.scroll.setVisible(not checked and bool(self.mcqs))
        self.raw_editor.setVisible(checked)
        self.btn_apply_raw.setVisible(checked)
        self.hint_drag.setVisible(not checked)
        if checked and self.mcqs:
            self.raw_editor.setPlainText("\n\n".join(m.to_text() for m in self.mcqs))
        if not checked:
            self._refresh_cards()

    def _apply_raw_text(self):
        try:
            self.mcqs = parse_mcq_text(self.raw_editor.toPlainText())
            self._refresh_cards()
            self._emit_updates()
            QMessageBox.information(self, "Success", f"Loaded {len(self.mcqs)} questions.")
        except Exception as e:
            QMessageBox.warning(self, "Parse Error", str(e))

    def _refresh_cards(self):
        self.list_widget.clear()
        for i, mcq in enumerate(self.mcqs):
            card = QuestionCard(i, mcq)
            card.edit_requested.connect(self.edit_question)
            card.delete_requested.connect(self._delete_question)
            card.move_up_requested.connect(self._move_up)
            card.move_down_requested.connect(self._move_down)
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(card.sizeHint().expandedTo(card.minimumSizeHint()))
            # Force a reasonable height so the card lays out
            card.adjustSize()
            item.setSizeHint(card.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)
            # Re-adjust after embed
            card.adjustSize()
            item.setSizeHint(card.sizeHint())

        has = bool(self.mcqs)
        raw = self.raw_checkbox.isChecked()
        self.empty_state.setVisible(not has and not raw)
        self.scroll.setVisible(has and not raw)
        self.hint_drag.setVisible(has and not raw)

    def _on_list_reordered(self):
        """Rebuild mcqs list from current list widget order."""
        new_order: List[MCQ] = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            w = self.list_widget.itemWidget(item)
            if isinstance(w, QuestionCard):
                new_order.append(w.mcq)
        if len(new_order) == len(self.mcqs):
            self.mcqs = new_order
            # Refresh indices on cards without full rebuild if possible
            self._refresh_cards()
            self._emit_updates()

    def _emit_updates(self):
        self.question_count_changed.emit(len(self.mcqs))
        if self.mcqs:
            self.language_changed.emit(detect_language(self.mcqs[0].question))
        else:
            self.language_changed.emit("—")

    def add_question(self):
        dlg = QuestionDialog(self)
        if dlg.exec():
            mcq = dlg.get_mcq()
            if mcq:
                self.mcqs.append(mcq)
                self._refresh_cards()
                self._emit_updates()

    def edit_question(self, index: int):
        if not (0 <= index < len(self.mcqs)):
            return
        dlg = QuestionDialog(self, mcq=self.mcqs[index], index=index)
        if dlg.exec():
            mcq = dlg.get_mcq()
            if mcq:
                self.mcqs[index] = mcq
                self._refresh_cards()
                self._emit_updates()

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select File", str(Path.home()), "Text (*.txt);;All (*)"
        )
        if not path:
            return
        try:
            self.mcqs = parse_mcq_file(path)
            self._refresh_cards()
            self._emit_updates()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_sample(self):
        root = Path(__file__).resolve().parent.parent
        candidates = [
            root / "samples" / "tamil_gk_sample.txt",
            root / "samples" / "english_gk_sample.txt",
        ]
        for sample in candidates:
            if sample.exists():
                try:
                    self.mcqs = parse_mcq_file(str(sample))
                    self._refresh_cards()
                    self._emit_updates()
                    return
                except Exception:
                    continue
        QMessageBox.warning(
            self, "No Sample",
            "Sample files not found.\nExpected samples/tamil_gk_sample.txt next to the app.",
        )

    def clear_all(self):
        if not self.mcqs:
            return
        if QMessageBox.question(
            self, "Clear All", f"Delete all {len(self.mcqs)} questions?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.mcqs.clear()
            self._undo_stack.clear()
            self.undo_bar.setVisible(False)
            self._refresh_cards()
            self._emit_updates()

    def _delete_question(self, index: int):
        if not (0 <= index < len(self.mcqs)):
            return
        removed = self.mcqs.pop(index)
        self._undo_stack.append((index, removed))
        self._refresh_cards()
        self._emit_updates()
        self._show_undo_toast(f"Question {index + 1} deleted")

    def _show_undo_toast(self, message: str):
        self.undo_label.setText(message)
        self.undo_bar.setVisible(True)
        if self._undo_timer is not None:
            self._undo_timer.stop()
        self._undo_timer = QTimer(self)
        self._undo_timer.setSingleShot(True)
        self._undo_timer.timeout.connect(self._dismiss_undo)
        self._undo_timer.start(8000)

    def _dismiss_undo(self):
        self.undo_bar.setVisible(False)
        # Keep only the last undo entry window; clear stack after timeout
        self._undo_stack.clear()

    def _undo_delete(self):
        if not self._undo_stack:
            self.undo_bar.setVisible(False)
            return
        index, mcq = self._undo_stack.pop()
        index = max(0, min(index, len(self.mcqs)))
        self.mcqs.insert(index, mcq)
        self._refresh_cards()
        self._emit_updates()
        self.undo_bar.setVisible(False)
        if self._undo_timer is not None:
            self._undo_timer.stop()

    def _move_up(self, index: int):
        if index > 0:
            self.mcqs[index], self.mcqs[index - 1] = self.mcqs[index - 1], self.mcqs[index]
            self._refresh_cards()
            self._emit_updates()

    def _move_down(self, index: int):
        if index < len(self.mcqs) - 1:
            self.mcqs[index], self.mcqs[index + 1] = self.mcqs[index + 1], self.mcqs[index]
            self._refresh_cards()
            self._emit_updates()
