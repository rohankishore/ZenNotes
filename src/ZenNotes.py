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
        # self.settingInterface = Settings()
        # self.settingInterface.setObjectName("markdownInterface")

        self.tabBar.addTab(text="Untitled 1", routeKey="Untitled 1")
        self.tabBar.setCurrentTab('Untitled 1')

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.EDIT, 'Write', FIF.EDIT, NavigationItemPosition.TOP)
        self.addSubInterface(self.markdownInterface, QIcon("src/resource/markdown.svg"), 'Markdown',
                             QIcon("src/resource/markdown.svg"))
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
        objectName = self.tabBar.currentTab().routeKey()
        self.homeInterface.setCurrentWidget(self.findChild(TabInterface, objectName))
        self.stackedWidget.setCurrentWidget(self.homeInterface)

        # Get the currently active tab
        current_tab = self.homeInterface.widget(index)

        if current_tab and isinstance(current_tab, TabInterface):
            # Update the current TWidget
            self.current_editor = self.text_widgets[current_tab.objectName()]

    def onTabAddRequested(self):
        text = f'Untitled {self.tabBar.count() + 1}'
        self.addTab(text, text, '')

        # Set the current_editor to the newly added TWidget
        self.current_editor = self.text_widgets[text]

    def open_document(self):
        file_dir = filedialog.askopenfilename(
            title="Select file",
        )
        filename = os.path.basename(file_dir).split('/')[-1]

        if file_dir:
            try:
                with open(file_dir, "r") as f:
                    filedata = f.read()
                    self.addTab(filename, filename, '')
                    self.current_editor.setPlainText(filedata)

                    # Check the first line of the text
                    first_line = filedata.split('\n')[0].strip()
                    if first_line == ".LOG":
                        self.current_editor.append(str(datetime.datetime.now()))

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

    def save_document(self):
        try:
            if not self.current_editor:
                print("No active TWidget found.")
                return  # Check if there is an active TWidget

            text_to_save = self.current_editor.toPlainText()
            print("Text to save:", text_to_save)  # Debug print

            name, fileExt = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "",
                "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
            )

            print("File path to save:", name)  # Debug print

            if name:
                with open(name, 'w') as file:
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
        self.homeInterface.addWidget(TabInterface(text, icon, routeKey, self))
        # Create a new TWidget instance for the new tab
        t_widget = TWidget(self)
        self.text_widgets[routeKey] = t_widget  # Store the TWidget instance in the dictionary
        tab_interface = self.findChild(TabInterface, routeKey)
        tab_interface.vBoxLayout.addWidget(t_widget)
        self.current_editor = t_widget  # Add TWidget to the corresponding TabInterface


if __name__ == '__main__':
    app = QApplication()
    w = Window()
    w.show()
    app.exec()
