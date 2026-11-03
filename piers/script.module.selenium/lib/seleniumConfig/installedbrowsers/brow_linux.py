import os
import shutil
import configparser
from .browsers import instBrowType

# tuple of possible browsers
# desktop entry name may be different for different architectures:
# for example "chromium_chromium.desktop" or "chromium-browser.desktop"
POSSIBLE_BROWSERS = (
    ("chrome", ("google-chrome",)),
    ("chromium", ("chromium", "chromium_chromium", "chromium-browser")),
    ("firefox", ("firefox", "firefox_firefox")),
    ("opera", ("opera",)),
    ("opera-beta", ("opera-beta",)),
    ("opera-developer", ("opera-developer",)),
    ("msedge", ("microsoft-edge",)),
    ("msedge-beta", ("microsoft-edge-beta",)),
    ("msedge-dev", ("microsoft-edge-dev",)),
    ("brave", ("brave-browser", "brave_brave")),
    ("brave-beta", ("brave-browser-beta",)),
    ("brave-nightly", ("brave-browser-nightly",)),
    ("vivaldi-stable", ("vivaldi-stable",)),
    ("vivaldi-snapshot", ("vivaldi-snapshot",)),
    ("min", ("min",))
)

# tuple of browser locations
# $XDG_DATA_HOME and $XDG_DATA_DIRS are not always set
BROWSER_LOCATIONS = (
    "~/.local/share/applications",
    "/usr/share/applications",
    "/var/lib/snapd/desktop/applications",
)

# get all installed browsers
def getBrowsers():
    INIRead=configparser.ConfigParser(interpolation=None)
    browserList=[]
    unique_browsers=set()
    for browser_name, desktop_entries in POSSIBLE_BROWSERS:
        for application_dir in BROWSER_LOCATIONS:
            for desktop_entry in desktop_entries:
                path = os.path.join(application_dir, f"{desktop_entry}.desktop")
                if not os.path.isfile(path):
                    continue
                if browser_name in unique_browsers:
                    continue
                # Found a .desktop entry for an installed browser not already in the list.
                INIRead.read(path)
                executable_path = INIRead['Desktop Entry']['Exec']
                if executable_path.lower().endswith(" %u"):
                    executable_path = executable_path[:-3].strip()
                # Some desktop entries omit the path if they are searchable in the PATH. 
                if not os.path.isfile(executable_path):
                    executable_path = shutil.which(executable_path)
                if os.path.isfile(executable_path):
                    browserList.append(instBrowType(name=browser_name,location=executable_path))
                    unique_browsers.add(browser_name)
    return browserList

