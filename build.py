import subprocess
import sys
import os
import shutil
import platform

def copy_icon():
    shutil.copy('icon.ico', 'dist/main/icon.ico')

def run_pyinstaller():
    try:
        main_script = os.path.join('src', 'main.py')

        # PyInstaller command to build the executable
        if platform.system() == 'Darwin':
            cmd = [
            'pyinstaller',
            main_script,
            '-w',  # Makes it windowed
            '--name "ZenNotes"',
            '--icon=icon.ico'
        ]
        else:
            cmd = [
                'pyinstaller',
                main_script,
                '--onedir',  # Create a single folder
                '-w',  # Makes it windowed
                '--icon=icon.ico'
            ]

        # Run PyInstaller
        subprocess.check_call(cmd)

        print("Build successful.")
    except Exception as e:
        print(f"Build failed: {e}")
    
    copy_icon()


if __name__ == '__main__':
    run_pyinstaller()

