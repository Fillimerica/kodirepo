# This module implements the custom settings interfaces for the selenium library.
# Functions are provided for callers to access the Kodi selenium configuration
# and to trigger selenium to open its configuration module.
# Written by Thomas Filliman
# Version 1.0 - October 2026

import xbmcaddon
import xbmc

# Need a pointer to the selenium addon.
seleniumAddon=xbmcaddon.Addon('script.module.selenium')

def openSettings():
    # Trigger selenium to open its configuration dialog.
    seleniumAddon.openSettings()
    xbmc.sleep(1000)
    # Wait for setup to finish.
    while xbmc.getCondVisibility('Window.IsActive(addonsettings)'):
        xbmc.sleep(1000)  # Sleep to prevent heavy CPU throttling

def getSetting(settingName):
    # Get the specified setting from the selenium configuration.
    return seleniumAddon.getSetting(settingName)

