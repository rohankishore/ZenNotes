import platform
import sys

class platformError(Exception):
    pass

class linux:
    def install():
        import os

        if os.path.isdir("dist"):
            print("Found existing build, proceeding to install it...")
        else:
            print("ERROR: No build found")
            print("Building first...")
            import build
            build.run_pyinstaller()
            print("Build complete, installing build...")
        
        

if platform.system() == "Windows":
    raise platformError("We have detected that you are using Windows. Please use the Inno Setup script instead.")
elif platform.system() == "Linux":
    linux.install()
else:
    raise platformError("Unsupported platform detected. There is no installer for this platform.")
