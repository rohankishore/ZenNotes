import platform
import sys

class platformError(Exception):
    pass

if platform.system() == "Windows":
    raise platformError("We have detected that you are using Windows. Please use the Inno Setup script instead.")
elif platform.system() == "Linux":
    import installers.linux
else:
    raise platformError("Unsupported platform detected. There is no installer for this platform.")
