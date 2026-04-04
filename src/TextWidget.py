# coding:utf-8
import base64
import wikipedia
from PySide6.QtGui import QFont, QAction, QIcon, Qt
from PySide6.QtWidgets import *
from PySide6.QtCore import QCoreApplication
from googletrans import Translator
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, MessageBox
import platform
import os

translator = Translator()

class TWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        if platform.system() == "Windows":
            local_app_data = os.getenv('LOCALAPPDATA')
        elif platform.system() == "Linux":
            local_app_data = os.path.expanduser("~/.config")
        elif platform.system() == "Darwin":
            local_app_data = os.path.expanduser("~/Library/Application Support")
        else:
            print("Unsupported operating system")
            sys.exit(1)
        self.local_app_data = local_app_data
        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        self.configSrcPath = os.path.join(self.scriptDir, "resource", "data", "config.json")
        self.configSrcDirPath = os.path.join(self.scriptDir, "resource")
        self.configPath = os.path.join(self.local_app_data, "ZenNotes", "data", "config.json")
        self.configDirPath = os.path.join(self.local_app_data, "ZenNotes")

        from qfluentwidgets.common.config import qconfig
        from qfluentwidgets import isDarkTheme
        self.isDarkTheme = isDarkTheme

        # Create the main container layout
        container = QWidget(self)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add the text editor
        self.text_editor = QTextEdit(self)
        self.text_editor.setFont(get_font_for_platform(14))
        self.text_editor.setAcceptRichText(False)
        self.text_editor.textChanged.connect(self.update_word_stats)
        main_layout.addWidget(self.text_editor)

        # Add the stats label at the bottom-right
        stats_layout = QHBoxLayout()
        stats_layout.addStretch()  # Push the label to the right
        self.word_stats_label = QLabel("Words: 0 | Characters: 0", self)
        stats_layout.addWidget(self.word_stats_label)
        main_layout.addLayout(stats_layout)

        # Set the container layout
        container.setLayout(main_layout)
        self.setLayout(main_layout)

        self.textChanged.connect(self.update_word_stats)

        self.setFont(get_font_for_platform(14))
        self.setAcceptRichText(False)
        self.filepath = None
        
        qconfig.themeChanged.connect(self.update_theme)
        self.update_theme()

    def update_theme(self):
        if self.isDarkTheme():
            stylesheet = "QTextEdit{background-color : #272727; color : white; border: 0;}"
            label_style = "color: white;"
        else:
            stylesheet = "QTextEdit{background-color : #FAF9F8; color : black; border: 0;}"
            label_style = "color: black;"
        self.text_editor.setStyleSheet(stylesheet)
        self.word_stats_label.setStyleSheet(label_style)
        self.setStyleSheet(stylesheet)

    def update_word_stats(self):
        text = self.toPlainText()
        words = len(text.split())
        characters = len(text)
        self.word_stats_label.setText(f"Words: {words} | Characters: {characters}")

    def contextMenuEvent(self, e):
        menu = RoundMenu(parent=self)
        # menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)

        # NOTE: hide the shortcut key
        # menu.view.setItemDelegate(MenuItemDelegate())

        copy_action = Action(FIF.COPY, 'Copy')
        copy_action.triggered.connect(lambda: self.copy())

        # Create an action for cut
        cut_action = Action(FIF.CUT, 'Cut')
        cut_action.triggered.connect(lambda: self.cut())

        # Create an action for copy
        copy_action = Action(FIF.COPY, 'Copy')
        copy_action.triggered.connect(lambda: self.copy())

        # Create an action for paste
        paste_action = Action(FIF.PASTE, 'Paste')
        paste_action.triggered.connect(lambda: self.paste())

        # Create an action for undo
        undo_action = Action(FIF.CANCEL, 'Undo')
        undo_action.triggered.connect(lambda: self.undo())

        # Create an action for redo
        redo_action = Action(FIF.EMBED, 'Redo')
        redo_action.triggered.connect(lambda: self.redo())

        # Create an action for select all
        select_all_action = QAction('Select All')
        select_all_action.triggered.connect(lambda: self.selectAll())

        # add actions
        menu.addAction(copy_action)
        menu.addAction(cut_action)

        # add sub menu for translate
        translation_submenu = RoundMenu("Translate", self)
        translation_submenu.setIcon(QIcon(os.path.join(self.configDirPath, "translate.png")))

        translate_selection_action = Action(FIF.CLEAR_SELECTION, 'Selection')
        translate_selection_action.triggered.connect(lambda: self.translate_selection())

        translate_full_action = Action(FIF.DOCUMENT, 'Full Document')
        translate_full_action.triggered.connect(lambda: self.translate_document())

        translation_submenu.addAction(translate_selection_action)
        translation_submenu.addAction(translate_full_action)

        encrypt_submenu = RoundMenu("Encryption", self)
        encrypt_submenu.setIcon(QIcon(os.path.join(self.configDirPath, "encrypt.png")))

        encrypt = RoundMenu('Encrypt', self)
        encrypt.setIcon(QIcon(os.path.join(self.configDirPath, "encrypt.png")))

        e_selection = Action(FIF.CLEAR_SELECTION, 'Selection')
        e_selection.triggered.connect(lambda: self.encrypt_selection())
        e_fd = Action(FIF.DOCUMENT, 'Full Document')
        e_fd.triggered.connect(lambda: self.encrypt_document())
        encrypt.addAction(e_selection)
        encrypt.addAction(e_fd)

        decrypt = RoundMenu('Decrypt', self)
        decrypt.setIcon(QIcon(os.path.join(self.configDirPath, "decrypt.png")))
        d_selection = Action(FIF.CLEAR_SELECTION, 'Selection')
        d_selection.triggered.connect(lambda: self.decode_selection())
        d_fd = Action(FIF.DOCUMENT, 'Full Document')
        d_fd.triggered.connect(lambda: self.decode_document())
        decrypt.addAction(d_selection)
        decrypt.addAction(d_fd)

        encrypt_submenu.addMenu(encrypt)
        encrypt_submenu.addMenu(decrypt)

        # submenu.addActions([
        #    QAction('Video'),
        #    Action(FIF.MUSIC, 'Music'),
        # ])

        # add actions
        menu.addActions([
            paste_action,
            select_all_action,
            undo_action
        ])

        # add separator
        menu.addSeparator()

        menu.addMenu(translation_submenu)
        menu.addMenu(encrypt_submenu)

        menu.addSeparator()

        wiki_action = Action(QIcon(os.path.join(os.path.join(self.configDirPath, "wikipedia.png"))), "Get Summary from Wikipedia")
        wiki_action.triggered.connect(self.wiki_get)
        menu.addAction(wiki_action)

        menu.exec(e.globalPos(), aniType=MenuAnimationType.FADE_IN_PULL_UP)

    def wiki_get(self):
        cursor = self.textCursor()
        query = cursor.selectedText()
        try:
            result = wikipedia.summary(query, sentences=4, auto_suggest=False)
            w = MessageBox(
                'Is this good?',
                ("'" + result + "'" + "\n" + "\n" + "\n" + "Should I insert this to the editor?"
                 ),
                self
            )
            w.yesButton.setText('Yeah')
            w.cancelButton.setText('Nah Nevermind')

            if w.exec():
                self.append(result)
        except Exception as e:
            w = MessageBox(
                'ERROR',
                "Unexpected Error Occured. Can't access Wikipedia right now!",
                self
            )
            w.yesButton.setText('Hmmm OK!')
            w.cancelButton.setText('Try again')

            if w.exec():
                pass

    def translate_selection(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        text = cursor.selectedText()

        a = translator.translate(text, dest="en")
        a = a.text
        w = MessageBox(
            'Is this good?',
            ("'" + a + "'" + "\n" + "\n" + "\n" + "Should I insert this to the editor?"
             ),
            self
        )
        w.yesButton.setText('Yeah')
        w.cancelButton.setText('Nah Nevermind')

        if w.exec():
            self.textCursor().insertText(a)

    def translate_document(self):
        text = self.toPlainText()

        a = translator.translate(text, dest="en")
        a = a.text

        w = MessageBox(
            'Is this good?',
            ("'" + a + "'" + "\n" + "\n" + "\n" + "Should I insert this to the editor?"
             ),
            self
        )
        w.yesButton.setText('Yeah')
        w.cancelButton.setText('Nah Nevermind')

        if w.exec():
            self.setPlainText(a)

    def encrypt_selection(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        sample_string = cursor.selectedText()
        if sample_string != "":
            sample_string_bytes = sample_string.encode("ascii")
            base64_bytes = base64.b64encode(sample_string_bytes)
            base64_encoded = base64_bytes.decode("ascii") + "   "
            self.textCursor().insertText(base64_encoded)

    def encrypt_document(self):
        text = self.toPlainText()
        if text != "":
            sample_string_bytes = text.encode("ascii")
            base64_bytes = base64.b64encode(sample_string_bytes)
            base64_encoded = base64_bytes.decode("ascii") + "   "
            self.setPlainText(base64_encoded)

    def decode_selection(self):
        cursor = self.textCursor()
        base64_string = cursor.selectedText()
        if base64_string != "":
            base64_bytes = base64_string.encode("ascii")
            sample_string_bytes = base64.b64decode(base64_bytes)
            sample_string = sample_string_bytes.decode("ascii") + "   "
            self.textCursor().insertText(sample_string)

    def decode_document(self):
        text = self.toPlainText()
        if text != "":
            base64_bytes = text.encode("ascii")
            sample_string_bytes = base64.b64decode(base64_bytes)
            sample_string = sample_string_bytes.decode("ascii") + "   "
            self.setPlainText(sample_string)
    
    def toPlainText(self):
        return self.text_editor.toPlainText()

    def setPlainText(self, text: str):
        self.text_editor.setPlainText(text)
        # Update stats and force a repaint so text becomes visible immediately
        try:
            self.update_word_stats()
        except Exception:
            pass
        self.text_editor.repaint()
        QCoreApplication.processEvents()
        self.text_editor.setFocus()

    def append(self, text: str):
        self.text_editor.append(text)

    def textCursor(self):
        return self.text_editor.textCursor()

    def setTextCursor(self, cursor):
        self.text_editor.setTextCursor(cursor)

    def ensureCursorVisible(self):
        self.text_editor.ensureCursorVisible()

def get_font_for_platform(size=12, plain=True):
    system_name = platform.system()
    if system_name == "Windows":
        if plain == True:
            return QFont("Consolas", size)
        else:
            return QFont("Arial", size)
    elif system_name == "Darwin":
        if plain == True:
            return QFont("Menlo", size)
        else:
            return QFont("Helvetica", size)
    else:
        print("WARNING: No non-plain font is available on your platform.")
        return QFont("DejaVu Sans Mono", size)