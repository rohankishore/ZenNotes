# Just a wrapper file for Notepad== contents
# Import encodings, defines file i/o with multiple encodings, etc
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'notepadequalequal'))

from notepadequalequal.common import encodings
from notepadequalequal.fileio import retrieve_file

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
