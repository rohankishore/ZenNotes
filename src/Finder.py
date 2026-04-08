from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton
from PySide6.QtGui import QTextCursor

class QTextEditNotProvidedError(Exception):
    pass
class Finder(QDialog):
