# coding:utf-8
from PySide6.QtGui import QFont, QAction, QIcon
from PySide6.QtWidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, MessageBox
from googletrans import Translator

translator = Translator()




class TWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFont(QFont("Consolas", 14))
        self.setAcceptRichText(False)
        self.setStyleSheet("QTextEdit{background-color : #272727; color : white; border: 0;}")

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


        # add sub menu
        translation_submenu = RoundMenu("Translate", self)
        translation_submenu.setIcon(QIcon("resource/translate.png"))

        translate_selection_action = Action(FIF.CLEAR_SELECTION, 'Selection')
        translate_selection_action.triggered.connect(lambda: self.translate_selection())

        translate_full_action = Action(FIF.DOCUMENT, 'Full Document')
        translate_full_action.triggered.connect(lambda: self.translate_document())

        translation_submenu.addAction(translate_selection_action)
        translation_submenu.addAction(translate_full_action)

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

        # show menu
        menu.exec(e.globalPos(), aniType=MenuAnimationType.FADE_IN_PULL_UP)


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


