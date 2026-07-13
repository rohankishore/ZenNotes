# Just a wrapper file for Notepad== encodings stuff
# Import encodings, defines file i/o with multiple encodings, etc
# Ironically originally written for ZenNotes, which depends on Notepad==
import os
import sys
from tkinter import messagebox
import traceback

import notepadequalequal.common as common
from notepadequalequal.common import encodings
from notepadequalequal.exceptions import UnsupportedEncodingError

sys.path.append(os.path.join(os.path.dirname(__file__), 'notepadequalequal'))

def retrieve_file(input):
    for enc in common.encodings[:]:
        try:
            with open(input, 'r', encoding=enc) as file:
                fileContent = file.read()
            return fileContent
        except UnicodeDecodeError:
            print("UnicodeDecodeError caught!")
            print("File is not " + str(enc) + ", trying next encoding...")
        except LookupError:
            print("LookupError caught!")
            print("Encoding not supported in this copy of Python, removing from list to avoid future clashes...")
            common.encodings.remove(enc)
    messagebox.showinfo("The program crashed due to an error", "The program has crashed due to an error. Please relaunch the program; any unsaved work will be recovered automatically on relaunch.")
    try:
        raise UnsupportedEncodingError("The file at " + str(input) + " could not be opened due to its encoding not being supported. The program has crashed itself to avoid further problems.")
    except UnsupportedEncodingError:
        traceback.print_exc()
        sys.exit(1)

def write_file(content, filepath, encoding='utf-8'):
    with open(filepath, "w", encoding=encoding) as f:
        f.write(content)

def retrieve_file_with_encoding(filepath):
    for enc in encodings[:]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError:
            continue
        except LookupError:
            encodings.remove(enc)
    content = retrieve_file(filepath)
    return content, 'utf-8'
