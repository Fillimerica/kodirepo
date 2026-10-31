# This module creates a list of browser types and options for the current
# operating system.
# A browserList.pkl cache file is created to store and retrieve the configuration
# across sessions without having to rebuild the list dynamically every time the
# module is run.
# C 2026 Thomas Filliman

import xbmc
import xbmcaddon
import xbmcvfs
import pickle
import installed_browsers
# Check to see if the debugger is installed as an optional dependency.
try:
    import web_pdb
    IsWebPDB = True
except:
    IsWebPDB = False

class browType:
    name: str
    description: str
    FQFN: str
    kiosk: str
    profile: str
    agent: str
    extra: str
browList=[]

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_id = addon.getAddonInfo('id')
addon_path=xbmcvfs.translatePath(addon.getAddonInfo('path'))
addon_data_path=xbmcvfs.translatePath(f"special://profile/addon_data/{addon_id}")

def getBrowserList(platformID, rebuildList=False):
    # This function accepts a platform ID string and returns a list of
    # all browsers that work on the specified platform.
    # Also accepts an optional parameter to force the rebuilding of the list
    # in cases where the user installs an additional browser after the initialization
    # configuration has been completed.
    if rebuildList:
        buildBrowserList()
    if platformID:
        selBrowsers=[brow for brow in browList if brow.platform==platformID]
    else:
        selBrowsers=browList
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

def buildBrowserList():
    # This function scans the current operating environment for installed
    # supported web browsers, and adds any found to the browList module list array.
    global browList
    if IsWebPDB:
        pass # needed to complete if statement when debugging is disabled.
        #web_pdb.set_trace()
    browList=[]
    # The installed_browsers module supports Linux, MacOS, & Windows.
    # For Android TV Boxes, return a static list defined in the code. (Best effort)
    curPlatformID=getPlatformID()
    if curPlatformID in ["system.platform.linux","system.platform.osx","system.platform.windows"]:
        # Iterate over each of the installed browsers.
        for brow in installed_browsers.browsers():
            match brow["name"].lower():
                case "chrome":
                    newBrow=browType()
                    newBrow.name=brow["name"]
                    newBrow.description=brow["description"]
                    newBrow.platform=curPlatformID
                    newBrow.FQFN=brow["location"]
                    # Define the browser specific configuration options.
                    newBrow.kiosk='--kiosk '
                    newBrow.profile='--user-data-dir='
                    newBrow.agent='--user-agent='
                    newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
                    browList.append(newBrow)
                case "msedge":
                    newBrow=browType()
                    newBrow.name=brow["name"]
                    newBrow.description=brow["description"]
                    newBrow.platform=curPlatformID
                    newBrow.FQFN=brow["location"]
                    # Define the browser specific configuration options.
                    newBrow.kiosk='--kiosk '
                    newBrow.profile='--user-data-dir='
                    newBrow.agent='--user-agent='
                    newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
                    browList.append(newBrow)
                case "firefox":
                    newBrow=browType()
                    newBrow.name=brow["name"]
                    newBrow.description=brow["description"]
                    newBrow.platform=curPlatformID
                    newBrow.FQFN=brow["location"]
                    # Define the browser specific configuration options.
                    newBrow.kiosk='--kiosk '
                    newBrow.profile='--user-data-dir='
                    newBrow.agent='--user-agent='
                    newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
                    browList.append(newBrow)
                case "unknown":
                    # ok to skip these without reporting an error, just if debugging.
                    xbmc.log(f"Unknown installed browser detected. Skipping. Browser={brow['name']}. Description={brow['description']}",xbmc.LOGDEBUG)
                case _:
                    # Unsupported browser was installed, okay to log and skip over.
                    xbmc.log(f"Unsupported installed browser detected. Skipping. Browser={brow['name']}. Description={brow['description']}",xbmc.LOGWARNING)
    else:
        # OS isn't supported by iterator, configure a static list for other platforms.
        # Android TV Box
        newBrow=browType()
        newBrow.name='Fully Kiosk'
        newBrow.description='Fully Kiosk'
        newBrow.platform='system.platform.android'
        newBrow.FQFN='de.ozerov.fully'
        newBrow.kiosk=''
        newBrow.profile=''
        newBrow.agent=''
        newBrow.extra=''
        browList.append(newBrow)

        newBrow=browType()
        newBrow.name='Browser'
        newBrow.description='Browser'
        newBrow.platform='system.platform.android'
        newBrow.FQFN='com.internet.tvbrowser'
        newBrow.kiosk=''
        newBrow.profile=''
        newBrow.agent=''
        newBrow.extra=''
        browList.append(newBrow)
    # The new browList has been built. Save a copy to a pickler file for future access.
    with open(browListFQFN,"wb") as f:
        pickle.dump(browList,f)


# Main module initialization code
browListFQFN=xbmcvfs.makeLegalFilename(addon_data_path+"/browserList.pkl")
# Check to see if the browserList.pkl file already exists, if it does then import it.
# If it does not then create the list of browsers currently installed.
if xbmcvfs.exists(browListFQFN):
    with open(browListFQFN,"rb") as f:
        browList = pickle.load(f)
else:
    buildBrowserList()

