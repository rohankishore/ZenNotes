"""
The main python file. Run this file to use the app. Also, for googletrans, use the command:
` pip install googletrans==4.0.0rc1 ` since the newer versions doesnt work well with PyCharm.

"""
import base64
import datetime
import os
import threading
from tkinter import filedialog, messagebox

import pyttsx3
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import *

from TextWidget import TWidget
from TitleBar import CustomTitleBar

class NoEditorSpecified(Exception):
    pass

class MarkdownPreview(QWidget):
    def __init__(self, objectName):
        super().__init__(parent=None)

        self.setObjectName(objectName)

        # Create a vertical splitter
        splitter = QSplitter(self)
        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        stylesheet = "QTextEdit{background-color : #272727; color : white; border : 0; font-size: 16}"

        # Left half: Markdown editor
        markdown_editor = QWidget(self)
        markdown_layout = QVBoxLayout(markdown_editor)
        self.txt = QTextEdit(self)
        self.txt.textChanged.connect(self.updateMarkdownPreview)
        self.txt.setStyleSheet(stylesheet)
        markdown_layout.addWidget(self.txt)
        splitter.addWidget(markdown_editor)

        # Right half: Preview
        preview = QWidget(self)
        preview_layout = QVBoxLayout(preview)
        self.preview_txt = QTextEdit(self)
        self.preview_txt.setReadOnly(True)
        self.preview_txt.setStyleSheet(stylesheet)
        preview_layout.addWidget(self.preview_txt)
        splitter.addWidget(preview)

        # Set the splitter size policy to distribute the space evenly
        splitter.setSizes([self.width() // 2, self.width() // 2])

        # Set the splitter handle width (optional)
        splitter.setHandleWidth(1)

    def updateMarkdownPreview(self):
        txt = self.txt.toPlainText()
        self.preview_txt.setMarkdown(txt)


class TabInterface(QFrame):
    """ Tab interface. Contains the base class to add/remove tabs """

    def __init__(self, text: str, icon, objectName, parent=None):
        super().__init__(parent=parent)
        self.iconWidget = IconWidget(icon, self)
        self.iconWidget.setFixedSize(120, 120)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setSpacing(30)

        self.setObjectName(objectName)


class Window(MSFluentWindow):
    """ Main window class. Uses MSFLuentWindow to imitate the Windows 11 FLuent Design windows. """

    def __init__(self):
        # self.isMicaEnabled = False
        super().__init__()

        self.scriptDir = os.path.dirname(os.path.abspath(__file__))

        self.setTitleBar(CustomTitleBar(self))
        self.tabBar = self.titleBar.tabBar  # type: TabBar

        setTheme(Theme.DARK)

        # Create shortcuts for Save and Open
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.open_shortcut = QShortcut(QKeySequence.StandardKey.Open, self)

        # Connect the shortcuts to functions
        self.save_shortcut.activated.connect(self.save_document)
        self.open_shortcut.activated.connect(self.open_document)

        # create sub interface
        self.homeInterface = QStackedWidget(self, objectName='homeInterface')
        self.markdownInterface = MarkdownPreview(objectName="markdownInterface")
        self.stackedWidget.addWidget(self.homeInterface)
        self.stackedWidget.addWidget(self.markdownInterface)
        # self.settingInterface = Settings()
        # self.settingInterface.setObjectName("markdownInterface")

        self.tabBar.addTab(text="Untitled 1", routeKey="Untitled 1")
        self.tabBar.setCurrentTab('Untitled 1')

        self.mode = "plaintext" # default a mode

        self.initNavigation()
        self.initWindow()

        # Select default 'Write' mode
        self.navigationInterface.setCurrentItem('Write')
        self.setModeToWrite()

    def initNavigation(self):
        self.navigationInterface.addItem(
            routeKey='Write',
            icon=FIF.EDIT,
            text='Write',
            onClick=self.setModeToWrite,
            position=NavigationItemPosition.TOP
        )
        self.navigationInterface.addItem(
            routeKey='Markdown',
            icon=QIcon(os.path.join(self.scriptDir, "resource", "markdown.svg")),
            text='Markdown',
            onClick=self.setModeToMarkdown,
            position=NavigationItemPosition.TOP
        )

        # self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', FIF.SETTING,  NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem(
            routeKey='Help',
            icon=FIF.INFO,
            text='About',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM)

        self.navigationInterface.setCurrentItem(
            self.homeInterface.objectName())

        self.text_widgets = {}  # Create a dictionary to store TWidget instances for each tab
        for i in range(self.tabBar.count()):  # Iterate through the tabs using count
            routeKey = self.tabBar.tabText(i)  # Get the routeKey from tabText

            # Create a new instance of TWidget for each tab
            t_widget = TWidget(self)
            self.text_widgets[routeKey] = t_widget  # Store the TWidget instance in the dictionary

            self.current_editor = t_widget

            # Add the TWidget to the corresponding TabInterface
            tab_interface = TabInterface(self.tabBar.tabText(i), 'icon', routeKey, self)
            tab_interface.vBoxLayout.addWidget(t_widget)
            self.homeInterface.addWidget(tab_interface)
        
        self.text_widgets['Markdown'] = self.markdownInterface.txt # Store markdown editor instance in dictionary
        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)

    def initWindow(self):
        self.resize(1100, 750)
        self.setWindowIcon(QIcon('src/resource/icon.ico'))
        self.setWindowTitle('ZenNotes')

        w, h = 1200, 800
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def dateTime(self):
        cdate = str(datetime.datetime.now())
        self.current_editor.append(cdate)


    def showMessageBox(self):
        w = MessageBox(
            'ZenNotes 📝',
            (
                    "Version : 1.4.0"
                    + "\n" + "\n" + "\n" + "💝  I hope you'll enjoy using ZenNotes as much as I did while coding it  💝" + "\n" + "\n" + "\n" +
                    "Made with 💖 By Rohan Kishore"
            ),
            self
        )
        w.yesButton.setText('GitHub')
        w.cancelButton.setText('Return')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/rohankishore/"))

    def onTabChanged(self, index: int):
        self.text_widgets['Markdown'] = self.markdownInterface.txt # Store markdown editor instance in dictionary
        routeKey = self.tabBar.currentTab().routeKey()
        mode = self.mode
        print("Current routeKey:", routeKey)
        print("Current mode:", mode)
        if mode == "markdown":
            self.stackedWidget.setCurrentWidget(self.markdownInterface)
        else:
            tab_widget = self.findChild(TabInterface, routeKey)
            if tab_widget:
                self.homeInterface.setCurrentWidget(tab_widget)
                self.stackedWidget.setCurrentWidget(self.homeInterface)
        if mode == "markdown":
            self.current_editor = self.markdownInterface.txt
        else:
            self.current_editor = self.text_widgets.get(routeKey)
        print(f"Switched to tab: {routeKey}")
        print(f"Current editor set to: {self.current_editor}")

    def onSideTabChanged(self, modeToSet):
        if modeToSet == "Markdown":
            self.mode = "markdown"
        else:
            self.mode = "plaintext"
        self.onTabChanged(self.tabBar.currentIndex())
        print("Mode changed to:", self.mode)

    def setModeToMarkdown(self):
        self.onSideTabChanged("Markdown")
    
    def setModeToWrite(self):
        self.onSideTabChanged("Write")

    def onTabAddRequested(self):
        base_name = "Untitled"
        idx = 1
        # Generate a routeKey not already used
        while True:
            routeKey = f"{base_name} {idx}"
            if routeKey not in self.text_widgets:
                break
            idx += 1
        self.addTab(routeKey, routeKey, '')

        # Set the current_editor to the newly added TWidget
        self.current_editor = self.text_widgets[routeKey]

    def open_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;Markdown Files (*.md)"
        )
        if file_path:
            self.open_file(file_path)

    def open_file(self, file_path):
        filename = os.path.basename(file_path).split('/')[-1]
        _, ext = os.path.splitext(filename)
        if ext.lower() == '.md':
            self.setModeToMarkdown()
        else:
            self.setModeToWrite()

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    filedata = f.read()
                    print(f"filedata: {filedata}")

                if self.mode == "markdown":
                    self.stackedWidget.setCurrentWidget(self.markdownInterface)
                    QCoreApplication.processEvents()
                    self.current_editor = self.markdownInterface.txt
                    editor = self.current_editor
                    editor.setPlainText(filedata)
                    try:
                        self.markdownInterface.updateMarkdownPreview()
                    except Exception:
                        pass
                    try:
                        self.markdownInterface.preview_txt.setMarkdown(filedata)
                    except Exception:
                        pass
                    try:
                        self.markdownInterface.preview_txt.repaint()
                        self.markdownInterface.preview_txt.viewport().update()
                        self.markdownInterface.preview_txt.updateGeometry()
                    except Exception:
                        pass
                    QCoreApplication.processEvents()
                    try:
                        editor.setFocus()
                    except Exception:
                        pass
                    self.navigationInterface.blockSignals(True)
                    self.navigationInterface.setCurrentItem('Markdown')
                    self.navigationInterface.blockSignals(False)
                else:
                    editor = self.addTab(filename, filename, '')
                    self.current_editor = editor
                    editor.setPlainText(filedata)
                    tab_widget = self.findChild(TabInterface, filename)
                    if tab_widget:
                        self.homeInterface.setCurrentWidget(tab_widget)
                    self.stackedWidget.setCurrentWidget(self.homeInterface)
                    QCoreApplication.processEvents()
                    try:
                        editor.setFocus()
                    except Exception:
                        pass
                    self.navigationInterface.blockSignals(True)
                    self.navigationInterface.setCurrentItem('Write')
                    self.navigationInterface.blockSignals(False)


                # Check the first line of the text
                first_line = filedata.split('\n')[0].strip()
                if first_line == ".LOG":
                    editor.append(str(datetime.datetime.now()))
                print("Editor text length:", len(editor.toPlainText()))
            except UnicodeDecodeError:
                MessageBox(
                    'Wrong Filetype! 📝',
                    (
                        "Make sure you've selected a valid file type. Also note that PDF, DOCX, Image Files, are NOT supported in ZenNotes as of now."
                    ),
                    self
                )

    def closeEvent(self, event):
        a = self.current_editor.toPlainText()

        if a != "":

            w = MessageBox(
                'Confirm Exit',
                (
                        "Do you want to save your 'magnum opus' before exiting? " +
                        "Or would you like to bid adieu to your unsaved masterpiece?"
                ),
                self
            )
            w.yesButton.setText('Yeah')
            w.cancelButton.setText('Nah')

            if w.exec():
                self.save_document()
        else:
            event.accept()  # Close the application

    def find_first(self):
        def find_word(word):
            cursor = self.current_editor.document().find(word)

            if not cursor.isNull():
                self.current_editor.setTextCursor(cursor)
                self.current_editor.ensureCursorVisible()

        word_to_find, ok = QInputDialog.getText(
            self,
            "Find Word",
            "Enter the word you want to find:"
        )

        if ok and word_to_find:
            find_word(word_to_find)

    def findWord(self):
        def find_word(word):
            if not self.current_editor:
                return

            text_cursor = QTextCursor(self.current_editor.document())
            format = QTextCharFormat()
            format.setBackground(QColor("yellow"))

            while text_cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor):
                if text_cursor.selectedText() == word:
                    text_cursor.mergeCharFormat(format)

        word_to_find, ok = QInputDialog.getText(
            self,
            "Find Word",
            "Enter the word you want to find:"
        )

        if ok and word_to_find:
            find_word(word_to_find)

    def checkExt(self, name):
        root, ext = os.path.splitext(name)
        if ext:
            return ext
        else:
            return False
    
    def getEditorType(self):
        self.onTabChanged(self.tabBar.currentIndex())
        if self.mode == "markdown":
            self.current_editor = self.markdownInterface.txt
        else:
            routeKey = self.tabBar.tabText(self.tabBar.currentIndex())
            self.current_editor = self.text_widgets.get(routeKey)

    def save_document(self):
        try:
        #     if not self.current_editor:
        #         print("No active TWidget found.")
        #         return  # Check if there is an active TWidget
            self.getEditorType()
            editor = self.current_editor
            if not editor:
                raise NoEditorSpecified("No editor specified to save from.")

            text_to_save = editor.toPlainText()
            print("Text to save:", text_to_save)  # Debug print

            if self.mode == "markdown":
                name, fileExt = QFileDialog.getSaveFileName(
                    self,
                    "Save File",
                    "",
                    "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)"
                )
            else:
                name, fileExt = QFileDialog.getSaveFileName(
                    self,
                    "Save File",
                    "",
                    "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
                )
            print("File path without extension to save:", name)  # Debug print
            if fileExt:
                if fileExt == "Text Files (*.txt)" and not self.checkExt(name):
                    name += '.txt'
                elif fileExt == "Markdown Files (*.md)" and not self.checkExt(name):
                    name += '.md'
            print("File path to save:", name)  # Debug print

            if name:
                with open(name, 'w', encoding='utf-8') as file:
                    file.write(text_to_save)
                    title = os.path.basename(name) + " ~ ZenNotes"
                    active_tab_index = self.tabBar.currentIndex()
                    self.tabBar.setTabText(active_tab_index, os.path.basename(name))
                    self.setWindowTitle(title)
                    print("File saved successfully.")  # Debug print
        except Exception as e:
            print(f"An error occurred while saving the document: {e}")

    def tts(self):
        cursor = self.current_editor.textCursor()
        text = cursor.selectedText()

        def thread_tts():
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()

        thread1 = threading.Thread(target=thread_tts)
        thread1.start()

    def go_to_line(self):

        line_number, ok = QInputDialog.getInt(
            self,
            "Go to Line",
            "Enter line number:",
            value=1,
        )

        cursor = self.current_editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number - 1)

        # Set the cursor as the new cursor for the QTextEdit
        self.current_editor.setTextCursor(cursor)

        # Ensure the target line is visible
        self.current_editor.ensureCursorVisible()

    def addTab(self, routeKey, text, icon):
        self.tabBar.addTab(routeKey, text, icon)
        # Create a new TWidget instance for the new tab
        t_widget = TWidget(self)
        self.text_widgets[routeKey] = t_widget  # Store the TWidget instance in the dictionary
        tab_interface = TabInterface(text, icon, routeKey, self)
        tab_interface.vBoxLayout.addWidget(t_widget)
        self.homeInterface.addWidget(tab_interface)
        self.current_editor = t_widget  # Add TWidget to the corresponding TabInterface
        self.tabBar.setCurrentTab(routeKey)  # Switch to the newly added tab
        return t_widget

if __name__ == '__main__':
    app = QApplication()
    w = Window()
    w.show()
    app.exec()
