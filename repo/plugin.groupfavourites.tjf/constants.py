# Constants and globals file for the GroupFavorites Plugin
# V1.0 - October 2025

import sys
import xbmc
import xbmcvfs
from xbmcaddon import Addon

# Get the addon base path. Here we use pathlib module for convenient path handling
ADDON_PATH = xbmcvfs.translatePath(Addon().getAddonInfo('path'))
ICONS_DIR = ADDON_PATH +"/resources/images/icons"
FANART_DIR = ADDON_PATH +"/resources/images/fanart"
BASE_DATA_DIR = xbmcvfs.translatePath("special://profile/addon_data/"+Addon().getAddonInfo('id'))
DATA_DIR=BASE_DATA_DIR+"/groups"

# Main title for the plugin.
ADDON_NAME=Addon().getAddonInfo('name')

# String localization shortcut.
localize = Addon().getLocalizedString

# Define Addon Settings Class for the Addon.
AddonSettings=Addon().getSettings()

# Version 0.2.0 Need to move the group xml files into a sub-folder of data because
# the Kodi settings.xml file gets stored there.
# Kodi in Linux has issues with the xbmcvfs.exists and mkdirs functions, need to work
# around the issues.
if not xbmcvfs.exists(DATA_DIR+"/"):
    xbmcvfs.mkdirs(DATA_DIR)
    if xbmcvfs.exists(DATA_DIR+"/"):
        folders,files=xbmcvfs.listdir(BASE_DATA_DIR)
        for item in files:
            if item.endswith(".xml") and (not item=="settings.xml"):
                if xbmcvfs.copy(BASE_DATA_DIR+"/"+item,DATA_DIR+"/"+item):
                    xbmcvfs.delete(BASE_DATA_DIR+"/"+item)
                else:
                    raise ValueError(localize(30215)+f' {BASE_DATA_DIR+"/"+item}')
    else:
        raise ValueError(localize(30214)+f' {DATA_DIR}')
        
# Check to see if the debugger is installed as an optional dependency.
IsWebPDB=xbmc.getCondVisibility('System.HasAddon("script.module.web-pdb")')