# This module creates a list of browser types and options for various
# operating systems. This allows browserlauncher to maintain a central
# list of all browser types on all supported operating systems.
# C 2026 Thomas Filliman

import xbmc

class browType:
    index: int
    name: str
    FQFN: str
    platform: str
    kiosk: str
    profile: str
    agent: str
    extra: str

allBrowsers=[]    
# Definition Section of Supported Browsers 
# Note that the index property should be a unique integer that stays with the definition
# regardless of position. Index values do not need to be consecutive or ordered.

# Windows
newBrow=browType()
newBrow.index=1
newBrow.name='Chrome'
newBrow.platform='system.platform.windows'
newBrow.FQFN='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
newBrow.kiosk='--kiosk '
newBrow.profile='--user-data-dir='
newBrow.agent='--user-agent='
newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
allBrowsers.append(newBrow)

newBrow=browType()
newBrow.index=2
newBrow.name='Firefox'
newBrow.platform='system.platform.windows'
newBrow.FQFN='C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'
newBrow.kiosk='-kiosk '
newBrow.profile='-profile '
newBrow.agent=''
newBrow.extra=''
allBrowsers.append(newBrow)

newBrow=browType()
newBrow.index=3
newBrow.name='Edge'
newBrow.platform='system.platform.windows'
newBrow.FQFN='C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
newBrow.kiosk='--edge-kiosk-type=fullscreen --kiosk '
newBrow.profile='--user-data-dir='
newBrow.agent='--user-agent='
newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
allBrowsers.append(newBrow)

# Android TV Box
newBrow=browType()
newBrow.index=20
newBrow.name='Fully Kiosk'
newBrow.platform='system.platform.android'
newBrow.FQFN='de.ozerov.fully'
newBrow.kiosk=''
newBrow.profile=''
newBrow.agent=''
newBrow.extra=''
allBrowsers.append(newBrow)

newBrow=browType()
newBrow.index=21
newBrow.name='Browser'
newBrow.platform='system.platform.android'
newBrow.FQFN='com.internet.tvbrowser'
newBrow.kiosk=''
newBrow.profile=''
newBrow.agent=''
newBrow.extra=''
allBrowsers.append(newBrow)

def getBrowserList(platformID):
    # This function accepts a platform ID string and returns a list of
    # all browsers that work on the specified platform.
    if platformID:
        selBrowsers=[brow for brow in allBrowsers if brow.platform==platformID]
    else:
        selBrowsers=allBrowsers
    return selBrowsers

def getPlatformID():
    # This function returns the platform ID string of the platform on which
    # Kodi is currently running.
    if xbmc.getCondVisibility("system.platform.windows"):
        platform = "system.platform.windows"
    elif xbmc.getCondVisibility("system.platform.android"):
        platform = "system.platform.android"
    elif xbmc.getCondVisibility("system.platform.ios"):
        platform = "system.platform.ios"
    elif xbmc.getCondVisibility("system.platform.osx"):
        platform = "system.platform.osx"
    elif xbmc.getCondVisibility("system.platform.linux"):
        # Note: Android also evaluates to Linux in some contexts,
        # so check Android first if needed.
        platform = "system.platform.linux"
    elif xbmc.getCondVisibility("system.platform.xbox"):
        platform = "system.platform.xbox"
    else:
        platform = "unknown"
    return platform