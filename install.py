import platform
import sys

class platformError(Exception):
    pass

class linux:
    def install():
        import os

        if os.path.isdir("dist") and not os.path.exists("dist/main/main.exe"):
            print("Found existing build, proceeding to install it...")
        else:
            print("ERROR: No build found")
            print("Building first...")
            import build
            build.run_pyinstaller()
            print("Build complete, installing build...")
        
        installdirDefault = "/opt/rohankishore/zennotes"
        installdir = input(f"Select installation directory (default {installdirDefault}, just press enter):")
        if not installdir:
            installdir = installdirDefault
        else:
            installdir = os.path.expanduser(installdir)
        username = os.getenv("USER")
        if username == "root":
            lnDir = "/usr/local/bin"
            deskDir = "/usr/share/applications"
            os.makedirs(lnDir, exist_ok=True)
            os.makedirs(deskDir, exist_ok=True)
        else:
            lnDir = f"/home/{username}/.local/bin"
            deskDir = f"/home/{username}/.local/share/applications"
            os.makedirs(lnDir, exist_ok=True)
            os.makedirs(deskDir, exist_ok=True)

        print(f"Installing to {installdir}...")
        os.makedirs(installdir, exist_ok=True)
        os.system(f"cp -r dist/main/* {installdir}/")
        
        print("Creating symlinks...")
        os.system(f"ln -sf {installdir}/main {lnDir}/zennotes")

        print("Creating desktop shortcuts...")
        os.system(f"cp zennotes.desktop {deskDir}/zennotes.desktop")
        os.system(f"sed -i 's#@INSTALLDIR@#{installdir}#g' {deskDir}/zennotes.desktop")

if platform.system() == "Windows":
    raise platformError("We have detected that you are using Windows. Please use the Inno Setup script instead.")
elif platform.system() == "Linux":
    linux.install()
else:
    raise platformError("Unsupported platform detected. There is no installer for this platform.")
