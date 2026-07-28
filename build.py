import subprocess
import sys
import os
import shutil
import platform
import site
import install_deps

def copy_icon():
    shutil.copy('icon.ico', 'dist/main/icon.ico')

def get_spellchecker_data():
    site_packages_dir = site.getsitepackages()[0]
    site_packages_dir = os.path.join(site_packages_dir, 'Lib', 'site-packages') if platform.system() == "Windows" and "venv" in site_packages_dir else site_packages_dir
    return os.path.join(site_packages_dir, 'spellchecker', 'resources')

def run_pyinstaller():
    try:
        main_script = os.path.join('src', 'main.py')

        # PyInstaller command to build the executable
        spellchecker_data_path = get_spellchecker_data()
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
                '--hidden-import=spellchecker',
                '--add-data', 'src/resource:resource',
                '--add-data', 'src/notepadequalequal:notepadequalequal',
                '--add-data', f'{spellchecker_data_path}:spellchecker/resources'
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



