# This is a simplified local files system browser search routine.
# currently supports Windows and Linux.

class instBrowType:
    def __init__(self,name,location):
        self.name=name
        self.location=location

def getInstalledBrowsers(platformID):
    match platformID:
        case "system.platform.windows":
            from .brow_windows import getBrowsers
            return getBrowsers()
        case "system.platform.linux":
            from .brow_linux import getBrowsers
            return getBrowsers()
        case _:
            xbmc.log(f"Unsupported platform requested in instaslledbrowser module. Platform={platformID}",xbmc.LOGWARNING)
            return None
