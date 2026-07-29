"""
The main python file. Run this file to use the app.
"""
import base64
import datetime
import json
import os
import threading
import sys
import platform
import shutil

import pyttsx3
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
try:
    import mistune
except ImportError:
    mistune = None
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import *

from TextWidget import TWidget, get_font_for_platform
from TitleBar import CustomTitleBar
from zencodings import write_file, retrieve_file_with_encoding
from Finder import Finder, FindAndReplace
from zspellcheck import SpellChecker

class NoEditorSpecified(Exception):
    pass

class MarkdownPreview(QWidget):
    def __init__(self, objectName):
        super().__init__(parent=None)

        self.setObjectName(objectName)

        from qfluentwidgets.common.config import qconfig
        from qfluentwidgets import isDarkTheme
        self.isDarkTheme = isDarkTheme
        self.markdown_renderer = self._build_markdown_renderer()

        # Create a vertical splitter
        splitter = QSplitter(self)
        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        # Left half: Markdown editor
        markdown_editor = QWidget(self)
        markdown_layout = QVBoxLayout(markdown_editor)
        self.txt = TWidget(self)
        self.txt.setFont(get_font_for_platform(16))
        markdown_layout.addWidget(self.txt)
        splitter.addWidget(markdown_editor)
        self.txt.text_editor.textChanged.disconnect()
        self.txt.text_editor.textChanged.connect(self.updateMarkdownPreview)
        self.update_word_stats = self.txt.update_word_stats

        # Right half: Preview
        preview = QWidget(self)
        preview_layout = QVBoxLayout(preview)
        self.preview_txt = QTextBrowser(self)
        self.preview_txt.setReadOnly(True)
        self.preview_txt.setOpenExternalLinks(True)
        self.preview_txt.setFont(get_font_for_platform(16))
        preview_layout.addWidget(self.preview_txt)
        splitter.addWidget(preview)
        preview_bar = self.preview_txt.verticalScrollBar()
        preview_bar.valueChanged.connect(self.save_preview_scrollRatio)

        # Set the splitter size policy to distribute the space evenly
        splitter.setSizes([self.width() // 2, self.width() // 2])
        # Set the splitter handle width (optional)
        splitter.setHandleWidth(1)
        # Initialize saved scroll ratio
        self.scroll_ratio = 0.0
        self.saving_scroll = True  # Flag to control saving scroll ratio

        qconfig.themeChanged.connect(self.update_theme)
        self.update_theme()
        self.updateMarkdownPreview()

    def _build_markdown_renderer(self):
        if mistune is None:
            return None

        plugins = [
            "table",
            "task_lists",
            "strikethrough",
            "def_list",
            "footnotes",
            "url",
        ]

        try:
            return mistune.create_markdown(
                escape=False,
                hard_wrap=False,
                renderer="html",
                plugins=plugins,
            )
        except Exception:
            try:
                return mistune.create_markdown(
                    escape=False,
                    hard_wrap=False,
                    renderer="html",
                    plugins=["table", "task_lists", "strikethrough"],
                )
            except Exception:
                return None

    def _wrap_preview_html(self, body_html):
        if self.isDarkTheme():
            background = "#272727"
            text_color = "#F5F5F5"
            muted_color = "#BDBDBD"
            border_color = "#444444"
            code_bg = "#1E1E1E"
            table_header_bg = "#333333"
            link_color = "#7AB7FF"
        else:
            background = "#FAF9F8"
            text_color = "#111111"
            muted_color = "#555555"
            border_color = "#D8D8D8"
            code_bg = "#F2F2F2"
            table_header_bg = "#EAEAEA"
            link_color = "#005BBB"

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    html, body {{
      background: {background};
      color: {text_color};
      margin: 0;
      padding: 0;
      font-family: Segoe UI, Arial, sans-serif;
      font-size: 16px;
      line-height: 1.55;
    }}
    body {{
      padding: 16px 18px;
    }}
    a {{
      color: {link_color};
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    pre, code {{
      font-family: Consolas, Monaco, monospace;
    }}
    pre {{
      background: {code_bg};
      border: 1px solid {border_color};
      border-radius: 8px;
      padding: 12px;
      overflow-x: auto;
    }}
    code {{
      background: {code_bg};
      border-radius: 4px;
      padding: 0.15em 0.35em;
    }}
    pre code {{
      background: transparent;
      padding: 0;
    }}
    blockquote {{
      margin: 12px 0;
      padding: 0 0 0 12px;
      border-left: 4px solid {border_color};
      color: {muted_color};
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 14px 0;
    }}
    th, td {{
      border: 1px solid {border_color};
      padding: 6px 10px;
      vertical-align: top;
    }}
    th {{
      background: {table_header_bg};
    }}
    hr {{
      border: 0;
      border-top: 1px solid {border_color};
      margin: 18px 0;
    }}
    img {{
      max-width: 100%;
      height: auto;
    }}
    li.task-list-item {{
      list-style: none;
      margin-left: -1.4em;
    }}
    input.task-list-item-checkbox {{
      margin-right: 0.5em;
    }}
  </style>
</head>
<body>
{body_html}
</body>
</html>"""

    def render_markdown(self, markdown_text):
        if self.markdown_renderer is None:
            return None

        rendered = self.markdown_renderer(markdown_text)
        return self._wrap_preview_html(rendered or "<p></p>")

    def update_theme(self):
        if self.isDarkTheme():
            stylesheet = "QTextEdit, QTextBrowser{background-color : #272727; color : white; border : 0; font-size: 16}"
        else:
            stylesheet = "QTextEdit, QTextBrowser{background-color : #FAF9F8; color : black; border : 0; font-size: 16}"

        self.txt.setStyleSheet(stylesheet)
        self.preview_txt.setStyleSheet(stylesheet)
        self.updateMarkdownPreview()

    def updateMarkdownPreview(self):
        self.txt.update_word_stats()
        txt = self.txt.toPlainText()
        rendered = self.render_markdown(txt)
        self.saving_scroll = False
        if rendered is None:
            self.preview_txt.setMarkdown(txt)
        else:
            self.preview_txt.setHtml(rendered)
        self.saving_scroll = True
        self.restore_preview_scrollRatio()
        QTimer.singleShot(0, self.restore_preview_scrollRatio)

    def save_preview_scrollRatio(self):
        if not self.saving_scroll:
            return
        try:
            self.scroll_ratio = self.preview_txt.verticalScrollBar().value() / max(1, self.preview_txt.verticalScrollBar().maximum())
        except Exception:
            self.scroll_ratio = 0.0

    def restore_preview_scrollRatio(self):
        self.preview_txt.verticalScrollBar().setValue(int(self.scroll_ratio * self.preview_txt.verticalScrollBar().maximum()))

class TabInterface(QFrame):
    """ Tab interface. Contains the base class to add/remove tabs """

    def __init__(self, text: str, icon, objectName, parent=None):
        super().__init__(parent=parent)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        self.setObjectName(objectName)

class Window(MSFluentWindow):
    """ Main window class. Uses MSFLuentWindow to imitate the Windows 11 FLuent Design windows. """

    def __init__(self):
        # self.isMicaEnabled = False
        super().__init__()

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
        if not os.path.exists(self.configDirPath):
            shutil.copytree(self.configSrcDirPath, self.configDirPath, dirs_exist_ok=True)

        self.apply_saved_theme()
        self.encoding = 'utf-8' # default encoding

        self.setTitleBar(CustomTitleBar(self))
        self.tabBar = self.titleBar.tabBar  # type: TabBar

        # Create shortcuts for Save and Open
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.open_shortcut = QShortcut(QKeySequence.StandardKey.Open, self)
        self.saveas_shortcut = QShortcut(QKeySequence.StandardKey.SaveAs, self)

        # Connect the shortcuts to functions
        self.save_shortcut.activated.connect(self.save_document)
        self.open_shortcut.activated.connect(self.open_document)
        self.saveas_shortcut.activated.connect(self.save_document_as)

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
        self.usedRouteKeys = []
        self.usedRouteKeys.append("Untitled 1")  # Add the initial tab to the list of used keys

        self.initNavigation()
        self.initWindow()

        # Select default 'Write' mode
        self.navigationInterface.setCurrentItem('Write')
        self.setModeToWrite()

        # Check for no tabs every 100 ms
        self.tabCheckTimer = QTimer(self)
        self.tabCheckTimer.timeout.connect(self.checkForNoTabs)
        self.tabCheckTimer.start(100)

        self.onTabChanged(self.tabBar.currentIndex())  # Initialize current_editor reference
        self.apply_saved_theme() # Re-set the theme after initializing UI

    def load_config(self):
        default_config = {"theme": "dark"}

        try:
            if not os.path.exists(self.configPath):
                return default_config

            with open(self.configPath, "r", encoding="utf-8") as f:
                raw = f.read().strip()

            if not raw:
                return default_config

            config = json.loads(raw)
            if not isinstance(config, dict):
                return default_config

            theme = str(config.get("theme", "dark")).lower()
            if theme not in {"dark", "light"}:
                theme = "dark"
            return {"theme": theme}
        except Exception:
            return default_config

    def save_config(self, config):
        os.makedirs(os.path.dirname(self.configPath), exist_ok=True)
        with open(self.configPath, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def apply_saved_theme(self):
        config = self.load_config()
        theme_name = config.get("theme", "dark")
        self.set_theme(theme_name)

    def set_theme(self, theme_name):
        normalized_theme = str(theme_name).lower()
        if normalized_theme == "light":
            setTheme(Theme.LIGHT)
            self.save_config({"theme": "light"})
        else:
            setTheme(Theme.DARK)
            self.save_config({"theme": "dark"})

    def set_theme_dark(self):
        self.set_theme("dark")

    def set_theme_light(self):
        self.set_theme("light")

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
            icon=QIcon(os.path.join(self.configDirPath, "markdown.svg")),
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
            self.usedRouteKeys.append(routeKey)
        
        self.text_widgets['Markdown'] = self.markdownInterface.txt # Store markdown editor instance in dictionary
        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)

    def initWindow(self):
        self.resize(1100, 750)
        self.setWindowIcon(QIcon(os.path.join(self.configDirPath, "icon.ico")))
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
                    "Version : 1.5.1"
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
        # Use displayed tab text as key, not TabItem.routeKey() which doesn't update on rename
        tabDisplayName = self.tabBar.tabText(index)
        mode = self.mode
        print("Current tab name:", tabDisplayName)
        print("Current mode:", mode)
        if mode == "markdown":
            self.stackedWidget.setCurrentWidget(self.markdownInterface)
        else:
            # Find the TabInterface using the displayed tab name as objectName
            tab_widget = self.findChild(TabInterface, tabDisplayName)
            if tab_widget:
                self.homeInterface.setCurrentWidget(tab_widget)
                self.stackedWidget.setCurrentWidget(self.homeInterface)
        if mode == "markdown":
            self.current_editor = self.markdownInterface.txt
        else:
            self.current_editor = self.text_widgets.get(tabDisplayName)
        print(f"Switched to tab: {tabDisplayName}")
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
            if routeKey not in self.usedRouteKeys:
                break
            idx += 1
        self.addTab(routeKey, routeKey, '')

        # Set the current_editor to the newly added TWidget
        self.current_editor = self.text_widgets[routeKey]
        self.usedRouteKeys.append(routeKey)  # Add the new routeKey to the list of used keys

    def checkForNoTabs(self):
        if self.tabBar.count() == 0:
            sys.exit()

    def open_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;Markdown Files (*.md)"
        )
        if file_path:
            self.open_file(file_path)
            self.current_editor.filepath = file_path

    def open_file(self, file_path):
        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        if ext.lower() == '.md':
            self.setModeToMarkdown()
        else:
            self.setModeToWrite()
        if filename in self.usedRouteKeys:
            base_name = filename
            idx = 2
            # Generate a routeKey not already used
            while True:
                routeKey = f"{base_name} {idx}"
                if routeKey not in self.usedRouteKeys:
                    break
                idx += 1
            filename = routeKey

        if file_path:
            try:
                filedata, encoding = retrieve_file_with_encoding(file_path)
                # print(f"filedata: {filedata}")

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
                self.current_editor.encoding = encoding
                self.current_editor.update_word_stats()
                self.usedRouteKeys.append(filename)
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
        # Ensure we have a valid editor
        if not self.current_editor:
            self.getEditorType()
        
        a = ""
        for _, text_widget in self.text_widgets:
            a += text_widget.toPlainText()

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
                self.save_all_documents()
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

    def findText(self):
        finder = Finder(parent=self, textWidget=self.current_editor)
        finder.exec()

    def replaceText(self):
        replacer = FindAndReplace(parent=self, textWidget=self.current_editor)
        replacer.exec()

    def checkExt(self, name):
        root, ext = os.path.splitext(name)
        if ext:
            return ext
        else:
            return False
    
    def getExtensionFromFilter(self, filter_string):
        """Extract file extension from QFileDialog filter string."""
        if not filter_string:
            return ''
        # Extract from patterns like "Text Files (*.txt)" -> ".txt"
        if '*.' in filter_string:
            start = filter_string.index('*.')
            end = filter_string.index(')', start)
            return filter_string[start+1:end]  # Returns ".txt"
        return ''
    
    def getEditorType(self):
        self.onTabChanged(self.tabBar.currentIndex())
        if self.mode == "markdown":
            self.current_editor = self.markdownInterface.txt
        else:
            # Use displayed tab text as key, not TabItem.routeKey()
            tabDisplayName = self.tabBar.tabText(self.tabBar.currentIndex())
            self.current_editor = self.text_widgets.get(tabDisplayName)

    def save_document(self, dlgName = ""):
        try:
            self.getEditorType()
            editor = self.current_editor
            if not editor:
                raise NoEditorSpecified("No editor specified to save from.")

            text_to_save = editor.toPlainText()
            name = ""
            if dlgName:
                dlgTitle = "Save " + dlgName
            else:
                dlgTitle = "Save File"

            if not editor.filepath:
                # No filepath set, show save dialog
                if self.mode == "markdown":
                    name, fileExt = QFileDialog.getSaveFileName(
                        self,
                        dlgTitle,
                        "",
                        "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)"
                    )
                else:
                    name, fileExt = QFileDialog.getSaveFileName(
                        self,
                        dlgTitle,
                        "",
                        "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
                    )
                
                # User canceled dialog
                if not name:
                    return
                
                # Add extension if not present
                if not self.checkExt(name):
                    ext = self.getExtensionFromFilter(fileExt)
                    if ext:
                        name += ext
                    else:
                        name += '.txt'  # Default to .txt
            else:
                # Use existing filepath
                name = editor.filepath

            # Get encoding from current editor
            encoding = self.current_editor.encoding

            # Write file
            write_file(text_to_save, name, encoding=encoding)
            
            # Prepare UI update values
            title = os.path.basename(name) + " ~ ZenNotes"
            active_tab_index = self.tabBar.currentIndex()
            old_displayed_name = self.tabBar.tabText(active_tab_index)
            new_displayed_name = os.path.basename(name)
            
            # Update internal state BEFORE triggering any UI signals
            # This ensures onTabChanged will find the editor in text_widgets
            editor.filepath = name
            
            # Update text_widgets dictionary if filename changed (before setTabText triggers signal)
            if old_displayed_name != new_displayed_name:
                if old_displayed_name in self.text_widgets:
                    self.text_widgets[new_displayed_name] = self.text_widgets.pop(old_displayed_name)
                # Update TabInterface's objectName
                tab_interface = self.findChild(TabInterface, old_displayed_name)
                if tab_interface:
                    tab_interface.setObjectName(new_displayed_name)
            for routekey in self.usedRouteKeys:
                if routekey == old_displayed_name:
                    self.usedRouteKeys.remove(old_displayed_name)
                    self.usedRouteKeys.append(new_displayed_name)
            
            # NOW update UI (this may trigger signals)
            self.tabBar.setTabText(active_tab_index, new_displayed_name)
            self.setWindowTitle(title)
            
            print(f"File saved successfully to: {name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred while saving the document: {e}")

    def save_document_as(self):
        try:
            self.getEditorType()
            editor = self.current_editor
            if not editor:
                raise NoEditorSpecified("No editor specified to save from.")

            text_to_save = editor.toPlainText()

            # Always show save dialog for "Save As"
            if self.mode == "markdown":
                name, fileExt = QFileDialog.getSaveFileName(
                    self,
                    "Save File As",
                    "",
                    "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)"
                )
            else:
                name, fileExt = QFileDialog.getSaveFileName(
                    self,
                    "Save File As",
                    "",
                    "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
                )
            
            # User canceled dialog
            if not name:
                return
            
            # Add extension if not present
            if not self.checkExt(name):
                ext = self.getExtensionFromFilter(fileExt)
                if ext:
                    name += ext
                else:
                    name += '.txt'  # Default to .txt
            
            # Get encoding from current editor
            encoding = self.current_editor.encoding

            # Write file
            write_file(text_to_save, name, encoding=encoding)
            
            # Prepare UI update values
            title = os.path.basename(name) + " ~ ZenNotes"
            active_tab_index = self.tabBar.currentIndex()
            old_displayed_name = self.tabBar.tabText(active_tab_index)
            new_displayed_name = os.path.basename(name)
            
            # Update internal state BEFORE triggering any UI signals
            # This ensures onTabChanged will find the editor in text_widgets
            editor.filepath = name
            
            # Update text_widgets dictionary if filename changed (before setTabText triggers signal)
            if old_displayed_name != new_displayed_name:
                if old_displayed_name in self.text_widgets:
                    self.text_widgets[new_displayed_name] = self.text_widgets.pop(old_displayed_name)
                # Update TabInterface's objectName
                tab_interface = self.findChild(TabInterface, old_displayed_name)
                if tab_interface:
                    tab_interface.setObjectName(new_displayed_name)
            for routekey in self.usedRouteKeys:
                if routekey == old_displayed_name:
                    self.usedRouteKeys.remove(old_displayed_name)
                    self.usedRouteKeys.append(new_displayed_name)
            
            # NOW update UI (this may trigger signals)
            self.tabBar.setTabText(active_tab_index, new_displayed_name)
            self.setWindowTitle(title)
            
            print(f"File saved as: {name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred while saving the document: {e}")
    
    def save_all_documents(self):
        for i in range(self.tabBar.count()):
            self.tabBar.setCurrentIndex(i)
            self.onTabChanged(i)
            self.save_document(dlgName=self.tabBar.tabText(i))

    def tts(self):
        cursor = self.current_editor.textCursor()
        text = cursor.selectedText()

        def thread_tts():
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()

        thread1 = threading.Thread(target=thread_tts)
        thread1.start()

    def spellcheck_handler(self):
        spell_checker = SpellChecker(text_widget=self.current_editor)
        spell_checker.z_spellcheck_selected(language_mode='en')

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
        self.onTabChanged(self.tabBar.currentIndex())  # Update the current_editor reference
        return t_widget
    
    def set_twidget_encoding(self, encoding):
        self.current_editor.set_encoding(encoding)

def main():
    if platform.system() == "Linux":
        from quirks import get_linux_productname, crosvm_quirks
        if "crosvm" in get_linux_productname():
            crosvm_quirks()
    
    app = QApplication()
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    splash_pixmap = QPixmap(os.path.join(scriptDir, "resource", "splash.png"))
    splash_label = QSplashScreen(splash_pixmap)
    splash_label.show()
    font = get_font_for_platform()
    nonPlainFont = get_font_for_platform(plain=False)
    app.setFont(nonPlainFont)
    
    if platform.system() == "Darwin":
        def openEventHandler(event):
            file_to_open = event.file()
            QTimer.singleShot(0, lambda: w.open_file(file_to_open))
            return True
        oldEvent = QApplication.event
        def newEvent(self, event):
            if event.type() == QEvent.FileOpen:
                return openEventHandler(event)
            return oldEvent(self, event)
        QApplication.event = newEvent
        w = Window()
        w.show()
    else:
        w = Window()
        w.show()
        if len(sys.argv) > 1:
            file_to_open = sys.argv[1]
            QTimer.singleShot(0, lambda: w.open_file(file_to_open))

    splash_label.hide()
    app.exec()

if __name__ == '__main__':
    main()
