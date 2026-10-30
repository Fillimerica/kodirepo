# Constants and globals file for the TJF Network Plugin
# V1.0 - October 2025

import sys
from pathlib import Path
from xbmcaddon import Addon
from xbmcvfs import translatePath

# Get the plugin url in plugin:// notation.
URL = sys.argv[0]
# Get a plugin handle as an integer number.
HANDLE = int(sys.argv[1])
# Get the addon base path. Here we use pathlib module for convenient path handling
ADDON_PATH = Path(translatePath(Addon().getAddonInfo('path')))
ICONS_DIR = ADDON_PATH / 'resources' / 'images' / 'icons'
FANART_DIR = ADDON_PATH / 'resources' / 'images' / 'fanart'
DATA_DIR = ADDON_PATH / 'data'

# Used to hold items persisting in the My List special favorites group.
MYLISTFQFN=DATA_DIR / 'MyList.pkl'

# Main title for the plugin.
ADDON_NAME=Addon().getAddonInfo('name')

# Check to see if the debugger is installed as an optional dependency.
try:
    import web_pdb
    IsWebPDB = True
except:
    IsWebPDB = False
