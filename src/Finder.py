from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton, QMessageBox, QTextEdit
from PySide6.QtGui import QTextCursor

class QTextEditNotProvidedError(Exception):
    pass

class Finder(QDialog):
    def __init__(self, parent=None, textWidget=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.text_widget = textWidget

        self.setWindowTitle("Find")

        layout = QVBoxLayout(self)

        self.label = QLabel("Enter the text that you want to find:")
        layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)

        self.find_button = QPushButton("Find")
        self.close_button = QPushButton("Close")

        self.button_box = QDialogButtonBox()
        self.button_box.addButton(self.find_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.close_button, QDialogButtonBox.DestructiveRole)

        layout.addWidget(self.button_box)

        self.find_button.clicked.connect(lambda: self.findAndSelect(textWidget=self.text_widget))
        self.close_button.clicked.connect(self.reject)

    def getText(self):
        return self.line_edit.text()

    def resolveTextWidget(self, textWidget):
        if textWidget is None:
            return None
        if hasattr(textWidget, 'text_editor') and isinstance(getattr(textWidget, 'text_editor'), QTextEdit):
            return textWidget.text_editor
        return textWidget

    def findNext(self, text_edit, text):
        if not text_edit:
            raise QTextEditNotProvidedError("No text widget provided")
        if not text:
            return False

        cursor = text_edit.textCursor()

        found_cursor = text_edit.document().find(text, cursor)
        if found_cursor.isNull():
            start_cursor = QTextCursor(text_edit.document())
            found_cursor = text_edit.document().find(text, start_cursor)
            if found_cursor.isNull():
                return False

        text_edit.setTextCursor(found_cursor)
        text_edit.ensureCursorVisible()

        return True
    
    def findAndSelect(self, textToFind="", textWidget=None):
        if not textToFind:
            textToFind = self.getText()
        resolved_widget = self.resolveTextWidget(textWidget)
        if not resolved_widget:
            raise QTextEditNotProvidedError("No text widget provided")

        found = self.findNext(resolved_widget, textToFind)
        if not found:
            QMessageBox.information(self, "Not Found", f"'{textToFind}' not found in the document.")