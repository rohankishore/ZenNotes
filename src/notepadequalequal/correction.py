from spellchecker import SpellChecker
import re
import tkinter as tk
from tkinter import messagebox

root = None

# Spelling stuff
class Spelling:
    def __init__(self, text_widget=None):
        self.text_area = text_widget
        self.languages = {
            "english": "en",
            "russian": "ru",
            "spanish": "es",
            "portuguese": "pt",
            "italian": "it",
            "french": "fr",
            "german": "de",
            "arabic": "ar",
            "persian": "fa",
            "dutch": "nl",
            "latvian": "lv",
            "basque": "eu",
        }

        self.spellcheckers = {
            name: SpellChecker(language=code)
            for name, code in self.languages.items()
        }

    def tokenize(self, text):
        TOKEN_PATTERN = re.compile(r"\w+|\W+")
        return TOKEN_PATTERN.findall(text)
    
    def preserve_case(self, original, corrected):
        if original.isupper():
            return corrected.upper()
        if original[0].isupper():
            return corrected.capitalize()
        return corrected

    def check_spelling(self, lang='none', text=""):
        if lang == 'none':
            return text
        checker = self.spellcheckers.get(lang)
        if not checker:
            return text
        tokens = self.tokenize(text)
        corrected_tokens = []
        for token in tokens:
            if token.isalpha():
                corrected = checker.correction(token)
                corrected = self.preserve_case(token, corrected)
                corrected_tokens.append(corrected)
            else:
                corrected_tokens.append(token)
        return ''.join(corrected_tokens)
    
    def spellcheck_selected(self, language_mode=None):
        try:
            selected_text = self.text_area.get("sel.first", "sel.last")
            start = self.text_area.index("sel.first")
            end = self.text_area.index("sel.last")
            corrected_text = self.check_spelling(language_mode, selected_text)
            approved_text = approval_dialog("Spellcheck", "Is this text okay to insert into the editor?", corrected_text)
            if approved_text is None:
                messagebox.showinfo("Cancelled", "Spellcheck cancelled")
                return
            approved_len = len(approved_text)
            insert_end = self.text_area.index(f"{start} + {approved_len} chars")
            self.text_area.delete(start, end)
            self.text_area.insert(start, approved_text)
            self.text_area.tag_add("sel", start, insert_end)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during spellcheck: {str(e)}")

# Utilities
def approval_dialog(title, message, text):
    global returnText
    returnText = ""

    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("512x342")
    popup.resizable(True, True)

    label = tk.Label(popup, text=message)
    label.pack()
    text_widget = tk.Text(popup, width=50, height=10)
    text_widget.insert(tk.END, text)
    text_widget.pack()

    def confirm(event=None):
        global returnText
        returnText = text_widget.get("1.0", tk.END).rstrip("\n")
        popup.destroy()
    
    def cancel(event=None):
        global returnText
        returnText = None
        popup.destroy()
    
    confirm_button = tk.Button(popup, text="Confirm", command=confirm)
    confirm_button.pack(side=tk.RIGHT, padx=10, pady=10)
    cancel_button = tk.Button(popup, text="Cancel", command=cancel)
    cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)
    popup.protocol('WM_DELETE_WINDOW', cancel)
    
    popup.wait_window()
    return returnText