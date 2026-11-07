# This module creates a list of browser types and options for the current
# operating system.

# C 2026 Thomas Filliman

import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import subprocess
import urllib.parse
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

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_id = addon.getAddonInfo('id')
addon_path=xbmcvfs.translatePath(addon.getAddonInfo('path'))
addon_data_path=xbmcvfs.translatePath(f"special://profile/addon_data/{addon_id}")

# Define support function shortcuts. (translation is a function, even though it looks like a variable)
translation=addon.getLocalizedString

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

def buildBrowserList(platformID):
    # This function scans the current operating environment for installed
    # supported web browsers, and adds any found to the browList module list array.
    # On Linux, running in a sandboxed Flatpak requires special handling of file paths and access.
    if IsWebPDB:
        pass # needed to complete if statement when debugging is disabled.
        #web_pdb.set_trace()
    browList=[]
    # The installed_browsers module supports Linux, MacOS, & Windows.
    # For Android TV Boxes, return a static list defined in the code. (Best effort)
    if platformID in ["system.platform.linux","system.platform.windows"]:
        # Iterate over each of the installed browsers.
        for brow in getInstalledBrowsers(platformID):
            match brow.name.lower():
                case "chrome" | "msedge" | "brave" |"opera" | "vivaldi" | "midori":
                    newBrow=browType()
                    newBrow.name=brow.name
                    newBrow.description=brow.description
                    newBrow.platform=platformID
                    newBrow.FQFN=brow.location
                    # Define the browser specific configuration options.
                    newBrow.kiosk='--kiosk'
                    newBrow.profile='--user-data-dir='
                    newBrow.agent='--user-agent='
                    newBrow.extra='--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '
                    browList.append(newBrow)
                case "firefox" | "librewolf":
                    newBrow=browType()
                    newBrow.name=brow.name
                    newBrow.description=brow.description
                    newBrow.platform=platformID
                    newBrow.FQFN=brow.location
                    # Define the browser specific configuration options.
                    newBrow.kiosk='-kiosk'
                    newBrow.profile='-profile'
                    newBrow.agent=''
                    newBrow.extra=''
                    browList.append(newBrow)
                case "epiphany":
                    newBrow=browType()
                    newBrow.name=brow.name
                    newBrow.description=brow.description
                    newBrow.platform=platformID
                    newBrow.FQFN=brow.location
                    # Define the browser specific configuration options.
                    newBrow.kiosk=''
                    newBrow.profile='--profile'
                    newBrow.agent=''
                    newBrow.extra=''
                    browList.append(newBrow)
                case "unknown":
                    # ok to skip these without reporting an error, just if debugging.
                    xbmc.log(f"{translation(30032)}{brow.name}. Location={brow.location}",xbmc.LOGDEBUG)
                case _:
                    # Unsupported browser was installed, okay to log and skip over.
                    xbmc.log(f"{translation(30033)}{brow.name}.Location={brow.location}",xbmc.LOGWARNING)
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
    return browList

def createDefaultIndexPage(browIndex:int):
    # This function combines the ProfileTemplate.html file with the selected
    # browser's name and the addon_name to create a new ProfileIndex.html
    # file that can be instantiated by the selected browser.
    templateFile=xbmcvfs.validatePath(addon_path+"/resources/ProfileTemplate.html")
    indexFile=xbmcvfs.validatePath(addon_data_path+"/ProfileIndex.html")
    
    # Read in the template file
    with open(templateFile, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Replace the template placeholders with actual data.
    html_content=html_content.replace("{browser_name}",platformBrowList[browIndex].description)
    html_content=html_content.replace("{addon_name}",addon_name)

    # Write out the completed html file
    with open(indexFile, "w", encoding="utf-8") as f:
        f.write(html_content)

    return indexFile

def createProfileFirefox(profile_path: str, browIndex: int):
    # Display a status message to the user as this process may take some time.
    xbmcgui.Dialog().notification(addon_name,translation(30030),xbmcgui.NOTIFICATION_INFO,10000,False)
    
    # Prep the target profile folder to make sure it exists.
    xbmcvfs.mkdirs(profile_path)
    
    # For firefox, copy the user.js file into the empty profile to control Firefox startup behavior
    user_jsFQFN=xbmcvfs.validatePath(addon_path+"/resources/firefox/user.js")
    user_jsDest=xbmcvfs.validatePath(profile_path+"/user.js")
    xbmcvfs.copy(user_jsFQFN,user_jsDest)    
    
    # Build the command-line string to execute
    htmlFile=createDefaultIndexPage(browIndex)
    cmd = [ platformBrowList[browIndex].FQFN, "-no-remote", "-wait-for-browser", "-CreateProfile",addon_id,
    "-profile", f"{profile_path}", htmlFile ]
    if IsFlatpak:
        # Need to prefix the run command with the flatpak spawn elements
        cmd = ["flatpak-spawn","--host", *cmd]

    # Pass the profile creation command to the browser.
    process = subprocess.run(cmd)
   
    # All finished, show a short processing completed message
    xbmcgui.Dialog().notification(addon_name,translation(30035),xbmcgui.NOTIFICATION_INFO,5000,False)


def createProfileChrome(profile_path: str, browIndex: int):
    # Display a status message to the user as this process may take some time.
    xbmcgui.Dialog().notification(addon_name,translation(30030),xbmcgui.NOTIFICATION_INFO,10000,False)
    
    # Prep the target profile folder to make sure it exists.
    xbmcvfs.mkdirs(profile_path)
    
    # Build the command-line string to execute
    htmlFile=createDefaultIndexPage(browIndex)
    cmd = [ platformBrowList[browIndex].FQFN, f"--user-data-dir={profile_path}", "--no-first-run", htmlFile ]
    if IsFlatpak:
        # Need to prefix the run command with the flatpak spawn elements
        cmd = ["flatpak-spawn","--host", *cmd]

    # Pass the profile creation command to the browser.
    process = subprocess.run(cmd)
   
    # All finished, remove the processing message
    xbmcgui.Dialog().notification(addon_name,translation(30035),xbmcgui.NOTIFICATION_INFO,5000,False)

def createProfileWebkit(profile_path: str, browIndex: int):
    # Display a status message to the user as this process may take some time.
    xbmcgui.Dialog().notification(addon_name,translation(30030),xbmcgui.NOTIFICATION_INFO,10000,False)
    
    # Prep the target profile folder to make sure it exists.
    xbmcvfs.mkdirs(profile_path)
    
    # Build the command-line string to execute
    htmlFile=createDefaultIndexPage(browIndex)
    cmd = [ platformBrowList[browIndex].FQFN, "--profile", f"{profile_path}", htmlFile ]
    if IsFlatpak:
        # Need to prefix the run command with the flatpak spawn elements
        cmd = ["flatpak-spawn","--host", *cmd]

    # Pass the profile creation command to the browser.
    process = subprocess.run(cmd)
   
    # All finished, remove the processing message
    xbmcgui.Dialog().notification(addon_name,translation(30035),xbmcgui.NOTIFICATION_INFO,5000,False)

# Main module initialization code

# Determine the current running environment
platformID=getPlatformID()
# See if running in a Linux Flatpak sandbox.
IsFlatpak=False
if platformID=="system.platform.linux":
    if xbmcvfs.exists("/.flatpak-info"):
        IsFlatpak=True

# Build the installed browser list (this list is exported to other modules for use globally)
platformBrowList=buildBrowserList(platformID)


