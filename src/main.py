"""
The main python file. Run this file to use the app. Also, for googletrans, use the command:
` pip install googletrans==4.0.0rc1 ` since the newer versions doesnt work well with PyCharm.

"""


import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import os
from PySide6.QtGui import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import *
from qframelesswindow import *
from tkinter import filedialog, messagebox
from TextWidget import TWidget
from TitleBar import CustomTitleBar

class Widget(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

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
        self.isMicaEnabled = True
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.tabBar = self.titleBar.tabBar  # type: TabBar


        setTheme(Theme.DARK)
        #setThemeColor(QColor("red")) #sets the red accents

        # create sub interface
        self.homeInterface = QStackedWidget(self, objectName='homeInterface')

        self.tabBar.addTab(text="Untitled 1", routeKey="Untitled 1")
        self.tabBar.setCurrentTab('Untitled 1')

        #self.current_editor = self.text_widgets["Scratch 1"]

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.EDIT, 'Write', FIF.EDIT)
        self.navigationInterface.addItem(
            routeKey='Help',
            icon=FIF.INFO,
            text='About',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

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
        self.setWindowIcon(QIcon('resource/icon.ico'))
        self.setWindowTitle('ZenNotes')

        w, h = 1200, 800
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def showMessageBox(self):
        w = MessageBox(
            'ZenNotes 📝',
            (
                    "Version : 1.0"
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
                f = open(file_dir, "r")
                filedata = f.read()
                self.addTab(filename, filename, '')
                self.current_editor.setPlainText(filedata)
                f.close()
            except UnicodeDecodeError:
                messagebox.showerror("Wrong Filetype!", "This file type is not supported!")

    def save_document(self):
        try:
            if not self.current_editor:
                print("No active TWidget found.")
                return  # Check if there is an active TWidget

            text_to_save = self.current_editor.toPlainText()
            print("Text to save:", text_to_save)  # Debug print

            name = filedialog.asksaveasfilename(
                title="Select file",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
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


    def addTab(self, routeKey, text, icon):
        self.tabBar.addTab(routeKey, text, icon)
        self.homeInterface.addWidget(TabInterface(text, icon, routeKey, self))
        # Create a new TWidget instance for the new tab
        t_widget = TWidget(self)
        self.text_widgets[routeKey] = t_widget  # Store the TWidget instance in the dictionary
        tab_interface = self.findChild(TabInterface, routeKey)
        tab_interface.vBoxLayout.addWidget(t_widget)
        self.current_editor = t_widget# Add TWidget to the corresponding TabInterface

if __name__ == '__main__':
    app = QApplication()
    w = Window()
    w.show()
    app.exec()
