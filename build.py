import subprocess
import sys
import os
import shutil
import platform
import install_deps

def copy_icon():
    shutil.copy('icon.ico', 'dist/main/icon.ico')

def run_pyinstaller():
    try:
        main_script = os.path.join('src', 'main.py')

        # PyInstaller command to build the executable
        if platform.system() == 'Darwin':
            cmd = [
            'pyinstaller',
            'darwinBuild.spec'
            # main_script,
            # '-w',  # Makes it windowed
            # '--name', 'ZenNotes',
            # '--icon=icon.ico'
        ]
        else:
            cmd = [
                'pyinstaller',
                main_script,
                '--onedir',  # Create a single folder
                '-w',  # Makes it windowed
                '--icon=icon.ico', 
                '--add-data', 'src/resource:resource',
                '--add-data', 'src/notepadequalequal:notepadequalequal'
            ]

        # Run PyInstaller
        subprocess.check_call(cmd)

        print("Build successful.")
    except Exception as e:
        print(f"Build failed: {e}")

    if platform.system() != 'Darwin':
        copy_icon()


if __name__ == '__main__':
    install_deps.main()
    run_pyinstaller()



