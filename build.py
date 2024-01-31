import subprocess
import sys
import os


def run_pyinstaller():
    try:
        # Replace 'your_script.py' with the name of your main Python script
        main_script = 'ZenNotes.py'

        # PyInstaller command to build the executable
        cmd = [
            'pyinstaller',
            main_script,
            '--onedir',  # Create a single executable file
            '-w',  # Makes it windowed
            '--icon="icon.ico"'
        ]

        # Run PyInstaller
        subprocess.check_call(cmd)

        print("Build successful.")
    except Exception as e:
        print(f"Build failed: {e}")


if __name__ == '__main__':
    run_pyinstaller()
