# Just a wrapper file for Notepad== spellcheck stuff
# Import spellcheck
import os
import sys

from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLabel, QMessageBox, QTextEdit, QVBoxLayout
from PySide6.QtGui import QTextCursor

from Finder import resolveTextWidget

sys.path.append(os.path.join(os.path.dirname(__file__), 'notepadequalequal'))

from notepadequalequal.correction import *

class SpellChecker(Spelling):
    def __init__(self, text_widget=None):
        super().__init__(text_widget)

    def _normalize_language_mode(self, language_mode):
        if not language_mode or language_mode == "none":
            return "none"

        if language_mode in self.languages:
            return language_mode

        reverse_languages = {code: name for name, code in self.languages.items()}
        return reverse_languages.get(language_mode, language_mode)

    def z_spellcheck_selected(self, language_mode=None):
        try:
            resolved_widget = resolveTextWidget(self.text_area)
            if not resolved_widget:
                return

            cursor = resolved_widget.textCursor()
            if not cursor.hasSelection():
                return

            selected_text = cursor.selectedText()
            corrected_text = self.check_spelling(self._normalize_language_mode(language_mode), selected_text)
            approved_text = approval_dialog("Spellcheck", "Is this text okay to insert into the editor?", corrected_text)
            if approved_text is None:
                QMessageBox.information(resolved_widget, "Cancelled", "Spellcheck cancelled")
                return
            cursor.insertText(approved_text)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred during spellcheck: {str(e)}")

# Utilities
def approval_dialog(title, message, text):
    popup = QDialog(QApplication.activeWindow())
    popup.setWindowTitle(title)
    popup.resize(512, 342)

    layout = QVBoxLayout(popup)
    layout.addWidget(QLabel(message))

    text_widget = QTextEdit(popup)
    text_widget.setPlainText(text)
    layout.addWidget(text_widget)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=popup)
    button_box.button(QDialogButtonBox.Ok).setText("Confirm")
    layout.addWidget(button_box)

    accepted_text = None

    def confirm():
        nonlocal accepted_text
        accepted_text = text_widget.toPlainText().rstrip("\n")
        popup.accept()

    button_box.accepted.connect(confirm)
    button_box.rejected.connect(popup.reject)

    if popup.exec() == QDialog.Accepted:
        return accepted_text
    return None
