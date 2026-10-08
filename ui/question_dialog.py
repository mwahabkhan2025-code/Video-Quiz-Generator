"""
Add / Edit Question Dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QMessageBox,
    QFormLayout, QFrame
)
from PyQt6.QtCore import Qt

from core.mcq_parser import MCQ


class QuestionDialog(QDialog):
    """Dialog to add or edit a single MCQ."""

    def __init__(self, parent=None, mcq: MCQ | None = None, index: int | None = None):
        super().__init__(parent)
        self.mcq = mcq
        self.index = index
        self.is_edit = mcq is not None

        self.setWindowTitle("Edit Question" if self.is_edit else "Add Question")
        self.setMinimumWidth(520)
        self.setModal(True)

        self._setup_ui()
        if self.is_edit:
            self._populate()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Question
        layout.addWidget(QLabel("Question"))
        self.question_edit = QLineEdit()
        self.question_edit.setPlaceholderText("Enter the question text...")
        self.question_edit.setMinimumHeight(36)
        layout.addWidget(self.question_edit)

        # Options
        layout.addWidget(QLabel("Options"))
        self.option_edits = []
        self.correct_group = QButtonGroup(self)

        for i in range(4):
            row = QHBoxLayout()
            letter = chr(65 + i)

            radio = QRadioButton(letter)
            radio.setFixedWidth(40)
            self.correct_group.addButton(radio, i)
            row.addWidget(radio)

            edit = QLineEdit()
            edit.setPlaceholderText(f"Option {letter}")
            edit.setMinimumHeight(34)
            self.option_edits.append(edit)
            row.addWidget(edit, 1)

            layout.addLayout(row)

        # Default select A
        self.correct_group.button(0).setChecked(True)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Question")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _populate(self):
        if not self.mcq:
            return
        self.question_edit.setText(self.mcq.question)
        for i, opt in enumerate(self.mcq.options):
            self.option_edits[i].setText(opt)
        idx = ord(self.mcq.correct) - 65
        if 0 <= idx <= 3:
            self.correct_group.button(idx).setChecked(True)

    def _on_save(self):
        question = self.question_edit.text().strip()
        if not question:
            QMessageBox.warning(self, "Validation", "Question text cannot be empty.")
            return

        options = []
        for edit in self.option_edits:
            text = edit.text().strip()
            if not text:
                QMessageBox.warning(self, "Validation", "All four options are required.")
                return
            options.append(text)

        correct_idx = self.correct_group.checkedId()
        if correct_idx < 0:
            QMessageBox.warning(self, "Validation", "Please select the correct answer.")
            return

        self.result_mcq = MCQ(
            question=question,
            options=options,
            correct=chr(65 + correct_idx)
        )
        self.accept()

    def get_mcq(self) -> MCQ | None:
        return getattr(self, "result_mcq", None)
