# Constants and globals file for the TJF Network Plugin
# V1.1 - October 2026

import sys
from pathlib import Path
from xbmcaddon import Addon
import xbmcvfs

# Get the plugin url in plugin:// notation.
URL = sys.argv[0]
# Get a plugin handle as an integer number.
HANDLE = int(sys.argv[1])
# Get the addon base path. Here we use pathlib module for convenient path handling
ADDON_PATH = Path(xbmcvfs.translatePath(Addon().getAddonInfo('path')))
ICONS_DIR = ADDON_PATH / 'resources' / 'images' / 'icons'
FANART_DIR = ADDON_PATH / 'resources' / 'images' / 'fanart'
DATA_DIR = Path(xbmcvfs.translatePath("special://profile/addon_data/"+Addon().getAddonInfo('id'))) / 'data'

# Make sure the DATA_DIR path exists, create it if needed. 
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Used to hold items persisting in the My List special favorites group.
MYLISTFQFN=DATA_DIR / 'MyList.pkl'

# Main title for the plugin.
ADDON_NAME=Addon().getAddonInfo('name')


# Shortcuts (behave like a function but reduce typing in the source)
translate=Addon().getLocalizedString

# Check to see if the debugger is installed as an optional dependency.
try:
    import web_pdb
    IsWebPDB = True
except:
    IsWebPDB = False
