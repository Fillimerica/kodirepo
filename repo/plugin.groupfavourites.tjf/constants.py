# Constants and globals file for the GroupFavorites Plugin
# V1.0 - October 2025

import sys
import xbmc
from xbmcaddon import Addon
from xbmcvfs import translatePath

# Get the addon base path. Here we use pathlib module for convenient path handling
ADDON_PATH = translatePath(Addon().getAddonInfo('path'))
ICONS_DIR = ADDON_PATH +"/resources/images/icons"
FANART_DIR = ADDON_PATH +"/resources/images/fanart"
DATA_DIR = translatePath("special://profile/addon_data/"+Addon().getAddonInfo('id'))

# Main title for the plugin.
ADDON_NAME=Addon().getAddonInfo('name')

# String localization shortcut.
localize = Addon().getLocalizedString

# Check to see if the debugger is installed as an optional dependency.
IsWebPDB=xbmc.getCondVisibility('System.HasAddon("script.module.web-pdb")')