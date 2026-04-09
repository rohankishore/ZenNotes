from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton, QMessageBox, QTextEdit
from PySide6.QtGui import QTextCursor, QKeySequence, QShortcut

# Misc functions
def resolveTextWidget(textWidget):
    if textWidget is None:
        return None
    if hasattr(textWidget, 'text_editor') and isinstance(getattr(textWidget, 'text_editor'), QTextEdit):
        return textWidget.text_editor
    return textWidget

# Exceptions
class QTextEditNotProvidedError(Exception):
    pass


# Main classes
class Finder(QDialog):
    def __init__(self, parent=None, textWidget=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.text_widget = textWidget

        self.setWindowTitle("Find")

        layout = QVBoxLayout(self)

        self.label = QLabel("Enter the text you want to find:")
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

        self.find_shortcut = QShortcut(QKeySequence("Enter"), self)
        self.find_shortcut.activated.connect(lambda: self.findAndSelect(textWidget=self.text_widget))

        self.line_edit.setFocus()

    def getText(self):
        return self.line_edit.text()

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
        resolved_widget = resolveTextWidget(textWidget)
        if not resolved_widget:
            raise QTextEditNotProvidedError("No text widget provided")

        found = self.findNext(resolved_widget, textToFind)
        if not found:
            QMessageBox.information(self, "Not Found", f"'{textToFind}' not found in the document.")

class FindAndReplace(Finder):
    def __init__(self, parent=None, textWidget=None):
        super().__init__(parent=parent, textWidget=textWidget)
        self.setWindowTitle("Find and Replace")

        self.replace_label = QLabel("Enter the text you want to replace it with:")
        self.replace_line_edit = QLineEdit()

        self.button_box.removeButton(self.close_button)

        self.replace_button = QPushButton("Replace")
        self.replaceNext_button = QPushButton("Replace Next")
        self.close_button = QPushButton("Close")

        self.button_box.addButton(self.replace_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.replaceNext_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.close_button, QDialogButtonBox.DestructiveRole)

        self.layout().insertWidget(2, self.replace_label)
        self.layout().insertWidget(3, self.replace_line_edit)

        self.replace_button.clicked.connect(lambda: self.replaceText(textWidget=self.text_widget))
        self.replaceNext_button.clicked.connect(lambda: self.replaceNext(textWidget=self.text_widget))
        self.close_button.clicked.connect(self.reject)

        self.replace_shortcut = QShortcut(QKeySequence("Shift+Enter"), self)
        self.replaceNext_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Enter"), self)
        self.replace_shortcut.activated.connect(lambda: self.replaceText(textWidget=self.text_widget))
        self.replaceNext_shortcut.activated.connect(lambda: self.replaceNext(textWidget=self.text_widget))

        self.line_edit.setFocus()

    def replaceText(self, textWidget=None, number=-1):
        text_to_find = self.getText()
        text_to_replace = self.replace_line_edit.text()
        resolved_widget = resolveTextWidget(textWidget)
        if not resolved_widget:
            raise QTextEditNotProvidedError("No text widget provided")

        found = self.findNext(resolved_widget, text_to_find)
        if not found:
            QMessageBox.information(self, "Not Found", f"'{text_to_find}' not found in the document.")
            return
        
        text = resolved_widget.toPlainText()
        modifiedText = text.replace(text_to_find, text_to_replace, number)
        resolved_widget.setPlainText(modifiedText)

    def replaceNext(self, textWidget=None):
        self.replaceText(textWidget=textWidget, number=1)
