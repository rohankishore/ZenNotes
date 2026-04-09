import sys
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy
from PySide6.QtCore import *
from PySide6.QtGui import QWheelEvent, QShortcut, QKeySequence
#from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import *
from TextWidget import TWidget


class CustomTabBar(TabBar):
    def wheelEvent(self, e: QWheelEvent):
        delta = e.pixelDelta().x() if not e.pixelDelta().isNull() else e.angleDelta().x()
        if delta != 0:
            scroll_bar = self.horizontalScrollBar()
            scroll_bar.setValue(scroll_bar.value() - delta)
            e.accept()
            return

        super().wheelEvent(e)
from zencodings import encodings

class CustomTitleBar(MSFluentTitleBar):

    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)

        # add buttons
        self.toolButtonLayout = QHBoxLayout()
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        self.menuButton = TransparentToolButton(FIF.MENU, self)
        #self.forwardButton = TransparentToolButton(FIF.RIGHT_ARROW.icon(color=color), self)
        #self.backButton = TransparentToolButton(FIF.LEFT_ARROW.icon(color=color), self)

        #self.forwardButton.setDisabled(True)
        self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)
        self.toolButtonLayout.setSpacing(15)
        self.toolButtonLayout.addWidget(self.menuButton)
        #self.toolButtonLayout.addWidget(self.backButton)
        #self.toolButtonLayout.addWidget(self.forwardButton)

        self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        self.tabBar = CustomTabBar(self)

        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(220)
        self.tabBar.setTabShadowEnabled(False)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))
        self.tabBar.setScrollable(True)
        self.tabBar.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tabBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

        self.tabBar.tabCloseRequested.connect(self.removeTabHandler)
        # self.tabBar.currentChanged.connect(lambda i: print(self.tabBar.tabText(i)))

        self.hBoxLayout.insertWidget(5, self.tabBar, 1)
        self.hBoxLayout.setStretch(6, 0)

        # self.hBoxLayout.insertWidget(7, self.saveButton, 0, Qt.AlignmentFlag.AlignLeft)
        # self.hBoxLayout.insertWidget(7, self.openButton, 0, Qt.AlignmentFlag.AlignLeft)
        # self.hBoxLayout.insertWidget(7, self.newButton, 0, Qt.AlignmentFlag.AlignLeft)
        # self.hBoxLayout.insertSpacing(8, 20)

        self.menu = RoundMenu("Menu")
        self.menu.setStyleSheet("QMenu{color : red;}")

        file_menu = RoundMenu("File", self)
        new_action = Action(text="New", icon=FIF.ADD.icon(QColor("white")))
        new_action.setShortcut("Ctrl+N")
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_action.triggered.connect(parent.onTabAddRequested)
        new_shortcut.activated.connect(parent.onTabAddRequested)
        file_menu.addAction(new_action)
        open_action = Action(text="Open", icon=FIF.SEND_FILL)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(parent.open_document)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        save_action = Action(text="Save", icon=FIF.SAVE)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(parent.save_document)
        file_menu.addAction(save_action)
        saveas_action = Action(text="Save As", icon=FIF.SAVE_AS)
        saveas_action.setShortcut("Ctrl+Shift+S")
        saveas_action.triggered.connect(parent.save_document_as)
        file_menu.addAction(saveas_action)
        self.menu.addMenu(file_menu)

        edit_menu = RoundMenu("Edit", self)
        cut_action = Action(text="Cut", icon=FIF.CUT.icon(QColor("white")))
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(lambda : TWidget.cut(parent.current_editor))
        edit_menu.addAction(cut_action)
        copy_action = Action(text="Copy", icon=FIF.COPY)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda : TWidget.copy(parent.current_editor))
        edit_menu.addAction(copy_action)
        paste_action = Action(text="Paste", icon=FIF.PASTE)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda : TWidget.paste(parent.current_editor))
        edit_menu.addAction(paste_action)
        edit_menu.addSeparator()
        find_action = Action(text="Find", icon=FIF.SEARCH)
        find_action.setShortcut("Ctrl+F")
        find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        find_action.triggered.connect(lambda: parent.findText())
        find_shortcut.activated.connect(lambda: parent.findText())
        edit_menu.addAction(find_action)
        replace_action = Action(text="Replace", icon=FIF.REMOVE_FROM)
        replace_action.setShortcut("Shift+Ctrl+R")
        replace_shortcut = QShortcut(QKeySequence("Shift+Ctrl+R"), self)
        replace_action.triggered.connect(lambda: parent.replaceText())
        replace_shortcut.activated.connect(lambda: parent.replaceText())
        edit_menu.addAction(replace_action)
        goto_action = Action(text="Go to Line", icon=FIF.UP)
        goto_action.setShortcut("Shift+Ctrl+G")
        goto_shortcut = QShortcut(QKeySequence("Shift+Ctrl+G"), self)
        goto_action.triggered.connect(lambda: parent.go_to_line())
        goto_shortcut.activated.connect(lambda: parent.go_to_line())
        edit_menu.addAction(goto_action)
        edit_menu.addSeparator()
        dateTime_action = Action(text="Time/Date", icon=FIF.DATE_TIME)
        dateTime_action.triggered.connect(lambda: parent.dateTime())
        edit_menu.addAction(dateTime_action)
        self.menu.addMenu(edit_menu)

        selection_menu = RoundMenu("Selection", self)
        tts_action = Action(text="TTS", icon=FIF.SPEAKERS.icon(QColor("white")))
        tts_action.triggered.connect(lambda: parent.tts())
        selection_menu.addAction(tts_action)
        self.menu.addMenu(selection_menu)

        view_menu = RoundMenu("View", self)
        dark_mode_action = Action(text="Dark Mode")
        dark_mode_action.triggered.connect(parent.set_theme_dark)
        light_mode_action = Action(text="Light Mode")
        light_mode_action.triggered.connect(parent.set_theme_light)
        view_menu.addAction(dark_mode_action)
        view_menu.addAction(light_mode_action)
        self.menu.addMenu(view_menu)

        encoding_menu = RoundMenu("Encoding", self)
        for encoding in encodings:
            encoding_action = Action(text=encoding.upper())
            encoding_action.triggered.connect(lambda checked, enc=encoding: parent.set_twidget_encoding(enc))
            encoding_menu.addAction(encoding_action)
        self.menu.addMenu(encoding_menu)

        # Create the menuButton
        # self.menuButton = TransparentToolButton(FIF.MENU, self)
        self.menuButton.clicked.connect(self.showMenu)

    def showMenu(self):
        # Show the menu at the position of the menuButton
        self.menu.exec(self.menuButton.mapToGlobal(self.menuButton.rect().bottomLeft()))

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False

        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)
    
    def removeTabHandler(self, index: int):
        self.tabBar.removeTab(index)
        self.parent().onTabChanged(self.tabBar.currentIndex())

    def test(self):
        print("hello")