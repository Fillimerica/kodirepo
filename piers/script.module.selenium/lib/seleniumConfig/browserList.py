# This module creates a list of browser types and options for the current
# operating system.

# C 2026 Thomas Filliman

import xbmc
import xbmcaddon
import xbmcvfs
from installedbrowsers.browsers import getInstalledBrowsers
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
platformBrowList=[]

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_id = addon.getAddonInfo('id')
addon_path=xbmcvfs.translatePath(addon.getAddonInfo('path'))
addon_data_path=xbmcvfs.translatePath(f"special://profile/addon_data/{addon_id}")

def getBrowserList(platformID):
    # This function accepts a platform ID string and returns a list of
    # all browsers that work on the specified platform.
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
    if curPlatformID in ["system.platform.linux","system.platform.windows"]:
        # Iterate over each of the installed browsers.
        for brow in getInstalledBrowsers(curPlatformID):
            match brow.name.lower():
                case "chrome":
                    newBrow=browType()
                    newBrow.name=brow.name
                    newBrow.description='Chrome'
                    newBrow.platform=curPlatformID
                    newBrow.FQFN=brow.location
                    # Define the browser specific configuration options.
                    newBrow.kiosk='--kiosk '
                    newBrow.profile='--user-data-dir='
                    newBrow.agent='--user-agent='
                    newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
                    browList.append(newBrow)
                case "msedge":
                    newBrow=browType()
                    newBrow.name=brow.name
                    newBrow.description='Edge'
                    newBrow.platform=curPlatformID
                    newBrow.FQFN=brow.location
                    # Define the browser specific configuration options.
                    newBrow.kiosk='--kiosk '
                    newBrow.profile='--user-data-dir='
                    newBrow.agent='--user-agent='
                    newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
                    browList.append(newBrow)
                case "firefox":
                    newBrow=browType()
                    newBrow.name=brow.name
                    newBrow.description='Firefox'
                    newBrow.platform=curPlatformID
                    newBrow.FQFN=brow.location
                    # Define the browser specific configuration options.
                    newBrow.kiosk='-kiosk '
                    newBrow.profile='-profile '
                    newBrow.agent=''
                    newBrow.extra=''
                    browList.append(newBrow)
                case "unknown":
                    # ok to skip these without reporting an error, just if debugging.
                    xbmc.log(f"Unknown installed browser detected. Skipping. Browser={brow.name}. Location={brow.location}",xbmc.LOGDEBUG)
                case _:
                    # Unsupported browser was installed, okay to log and skip over.
                    xbmc.log(f"Unsupported installed browser detected. Skipping. Browser={brow.name}.Location={brow.location}",xbmc.LOGWARNING)
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

def createProfileFirefox(profile_path: str, browIndex: int):
    # Display a status message to the user as this process may taker some time.
    p_dialog = xbmcgui.DialogProgressBG()
    p_dialog.create(addon_name,translation(30030))
    
    # Prep the target profile folder to make sure it exists.
    xbmcvfs.mkdirs(profile_path)
    
    # For firefox, copy the user.js file into the empty profile to control Firefox startup behavior
    user_jsFQFN=xbmcvfs.validatePath(addon_path+"/resources/firefox/user.js")
    user_jsDest=xbmcvfs.validatePath(profile_path+"/user.js")
    xbmcvfs.copy(user_jsFQFN,user_jsDest)    
    
    # Build the command-line string to execute
    htmlFile=xbmcvfs.validatePath(addon_path+"/resources/firefox/FirefoxIndex.html")
    cmd = [ platformBrowList[browIndex].FQFN, "-no-remote", "-wait-for-browser", "-CreateProfile","Selenium",
    "-profile", f"{profile_path}", htmlFile ]

    # Pass the profile creation command to the browser.
    process = subprocess.run(cmd)
   
    # All finished, remove the processing message
    p_dialog.close()

def createProfileEdge(profile_path: str, browIndex: int):
    # Display a status message to the user as this process may taker some time.
    p_dialog = xbmcgui.DialogProgressBG()
    p_dialog.create(addon_name,translation(30030))
    
    # Prep the target profile folder to make sure it exists.
    xbmcvfs.mkdirs(profile_path)
    
    # Build the command-line string to execute
    htmlFile=xbmcvfs.validatePath(addon_path+"/resources/chrome/EdgeIndex.html")
    cmd = [ platformBrowList[browIndex].FQFN, f"--user-data-dir={profile_path}", "--no-first-run", htmlFile ]

    # Pass the profile creation command to the browser.
    process = subprocess.run(cmd)
   
    # All finished, remove the processing message
    p_dialog.close()

def createProfileChrome(profile_path: str, browIndex: int):
    # Display a status message to the user as this process may taker some time.
    p_dialog = xbmcgui.DialogProgressBG()
    p_dialog.create(addon_name,translation(30030))
    
    # Prep the target profile folder to make sure it exists.
    xbmcvfs.mkdirs(profile_path)
    
    # Build the command-line string to execute
    htmlFile=xbmcvfs.validatePath(addon_path+"/resources/chrome/EdgeIndex.html")
    cmd = [ platformBrowList[browIndex].FQFN, f"--user-data-dir={profile_path}", "--no-first-run", htmlFile ]

    # Pass the profile creation command to the browser.
    process = subprocess.run(cmd)
   
    # All finished, remove the processing message
    p_dialog.close()

# Main module initialization code
buildBrowserList()
# Define the platform-filtered browser list for use in the createProfile fiunctions:
platformBrowList=getBrowserList(getPlatformID())

