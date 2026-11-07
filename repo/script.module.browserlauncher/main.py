# This module allows lauching an external web browser with a url from within Kodi.
# The installed list of abailable browsers is dynamically aquired from the operating
# system, and the settings dialog handles configuring a default browser along with
# browser specific options, and an optional isolated profile.
# Operating system support: Windows (32 & 64 bit), Linux (non-flatpak only due to sandbox restrictions)

# C 2026 Thomas Filliman


import sys
import os
import urllib.parse
import shlex
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import subprocess
import browserList
import guiSettings

# Check to see if the debugger is installed as an optional dependency.
try:
    import web_pdb
    IsWebPDB = True
except:
    IsWebPDB = False

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_id = addon.getAddonInfo('id')
addon_data_path=xbmcvfs.translatePath(f"special://profile/addon_data/{addon_id}")
addonsettings= addon.getSettings()

# Define defaults for the browser parameters
url=''
stopPlayback='yes'
useKiosk='yes'
userAgent=''

#platformID=browserList.getPlatformID()
#platformBrowList=browserList.getBrowserList(platformID)
from browserList import platformID,platformBrowList,IsFlatpak

# Define support function shortcuts. (translation is a function, even though it looks like a variable)
translation=addon.getLocalizedString

# Define settings globals used in browser launch function
browserProfile=''

def readSettings():
    global browserProfile
    
    # Read in the settings from Settings.xml
    # Uses the FQFN for the browser as a key, since the list is dynamically generated.
    browFQFN=addonsettings.getString('BrowserFQFN')
    selBrowser=next((brow for brow in platformBrowList if brow.FQFN==browFQFN), None)

    useIsolatedProfile=addonsettings.getBool('useIsolatedProfile') ## Whether to use the default browser profile or a custom one.
    if useIsolatedProfile:
        browserProfile=addonsettings.getString('BrowserProfile')
    else:
        browserProfile=''
    return selBrowser
    # End of Settings

def setBrowser(sFieldID):
    # This specialized function reads the list of browsers for the current platform and allows the user to select one.
    # Interaction with the settings.xml file uses hard-coded field ID suffix of "Index"
    
    if IsWebPDB:
        pass # needed to complete if statement when debugging is disabled.
        #web_pdb.set_trace()
    
    # Get the current value of sFieldID (str)
    sFieldFQFN=sFieldID+"FQFN"
    sFieldProfilePath=sFieldID+"Profile"
    
    # Retrieve the current browser index, in case there is already a configured browser for this addon.
    isValid, curBrowFQFN=guiSettings.getGuiSetting(sFieldFQFN)
    if not isValid:
        xbmc.log(f"{translation(30028)}{sFieldFQFN}",xbmc.LOGERROR)
        return
    if curBrowFQFN=="-not configured-":
        curProfile=""
    else:
        isValid, curProfile=guiSettings.getGuiSetting(sFieldProfilePath)
        if not isValid:
            xbmc.log(f"{translation(30028)}{sFieldProfilePath}",xbmc.LOGERROR)
            return
    # platformBrowList is initialized upon module load. If it is empty and IsFlatpak is true, then 
    # perhaps the override has not been configured. Log and advise the user.
    if not platformBrowList:
        if IsFlatpak:
            xbmc.log(f"{translation(30034)}{sFieldProfilePath}",xbmc.LOGERROR)
            xbmcgui.Dialog().ok(addon_name,translation(30034))
    
    # Build a list of just the browser names for the Kodi select dialog.
    browListNames=[brow.description for brow in platformBrowList]
    # Calculate the list index if a selection was previously made.
    curBrowIndex=next((idx for idx,brow in enumerate(platformBrowList) if brow.FQFN==curBrowFQFN),-1)
    
    selValue=-1
    while selValue == -1:
        # Obtain the desired browser selection from the Kodi GUI 
        selValue=xbmcgui.Dialog().select(translation(30014),browListNames,0,curBrowIndex)
        # selValue will be -1 if the user cancelled out of the dialog.
        if selValue == -1:
            if not curProfile:
                rc=xbmcgui.Dialog().yesno(addon_name,translation(30015),translation(30003),translation(30004),0,xbmcgui.DLG_YESNO_YES_BTN)
                if rc:
                    continue
            # Re-use existing configuration already saved.
            return
        else:
            # User selected a browser. See if a new/different browser was selected.
            if (selValue != curBrowIndex):
                # See if a non-default (isolated) browser profile should be created.
                isValid, useIsolatedProfile=guiSettings.getGuiSetting("useIsolatedProfile")
                if not isValid:
                    xbmc.log(f"{translation(30028)}useIsolatedProfile",xbmc.LOGERROR)
                    return
                if useIsolatedProfile:
                    # Need to create the profile path for the selected browser.
                    # See if a custom path override has been selected.
                    isValid, proPathOverride=guiSettings.getGuiSetting("ProfilePathOverride")
                    if not isValid:
                        xbmc.log(f"{translation(30028)}ProfilePathOverride",xbmc.LOGERROR)
                        return
                    if proPathOverride:
                        isValid, curProfile=guiSettings.getGuiSetting("ProfilePathCustom")
                        if not isValid:
                            xbmc.log(f"{translation(30028)}ProfilePathCustom",xbmc.LOGERROR)
                            return
                        if not xbmcvfs.exists(curProfile):
                            xbmcgui.Dialog().ok(addon_name,translation(30043))
                            return
                    else:
                        curProfile=xbmcvfs.validatePath(addon_data_path+"/"+platformBrowList[selValue].name+"/")
                    # curProfile now set to the desired isolated profile. Create it.
                    # Call the browser specific profile creation function.
                    match platformBrowList[selValue].name.lower():
                        case "firefox" | "librewolf":
                            # Call the Firefox specific initialization code.
                            browserList.createProfileFirefox(curProfile,selValue)
                        case "chrome" | "msedge" | "brave" |"opera" | "vivaldi" | "midori":
                            # Call the Chrome specific initialization code.
                            browserList.createProfileChrome(curProfile,selValue)
                        case "epiphany":
                            # Call the WebKit specific initialization code.
                            browserList.createProfileWebkit(curProfile,selValue)
                        case _:
                            xbmcgui.Dialog().ok(addon_name,f"{translation(30031)}{platformBrowList[selValue].name}")
                            return
                else:
                    # Use the default browser profile.
                    curProfile=""
                # Final validation check prior to saving
                if (selValue != -1):
                    # Save the selected browser information into the settings.
                    addon.setSetting(id=sFieldID,value=platformBrowList[selValue].description)
                    addon.setSetting(id=sFieldFQFN,value=platformBrowList[selValue].FQFN)
                    addon.setSetting(id=sFieldProfilePath,value=curProfile)
                    if curProfile:
                        addon.setSetting(id="BrowserProfileButton",value="Select to Show")
                    else:
                        addon.setSetting(id="BrowserProfileButton",value="-browser default-")
                else:
                    xbmcgui.Dialog().ok(addon_name,translation(30027))
            # Exit the while loop after the profile was created or left unchanged     
            break
    # End of while loop

def browserOptions(selBrowser):
    # This functon returns a list with the selected options for the browser.
    browOpts=[]
    if (browserProfile) and (selBrowser.profile):
        if selBrowser.profile[-1]=="=":
            browOpts.append(selBrowser.profile+browserProfile)
        else:
            browOpts.append(selBrowser.profile)
            browOpts.append(browserProfile)
    if (useKiosk=="yes") and (selBrowser.kiosk):
        browOpts.append(selBrowser.kiosk)
    if (userAgent) and (selBrowser.agent):
        if selBrowser.agent[-1]=="=":
            browOpts.append(selBrowser.agent+userAgent)
        else:
            browOpts.append(selBrowser.agent)
            browOpts.append(userAgent)
    if (selBrowser.extra):
        # Unpack the grouped options.
        browOpts.extend(shlex.split(selBrowser.extra))
    return browOpts

def browserLaunch(url,stopPlayback):
    # This function formats an execution string to the target browser
    # and passes the parameters to display the desired website.
    if IsWebPDB:
        pass # needed to complete if statement when debugging is disabled.
        #web_pdb.set_trace()

## TF 02/2026 Enhance launcher to support android TV devices.

    if stopPlayback == "yes":
        xbmc.Player().stop()
    
    # Read the settings for the addon and confirm that a valid browser is selected.
    selBrowser=readSettings()
    while selBrowser is None:
        tMsg=translation(30015)+"\n"+translation(30016)
        tDlgRC=xbmcgui.Dialog().yesno(addon_name,tMsg,translation(30001),translation(30002),0,xbmcgui.DLG_YESNO_YES_BTN)
        # If user chooses to cancel exit the addon completely
        if not tDlgRC:
            return
        # Open the settings for the addon to allow the user to adjust the configuration.
        addon.openSettings()
        selBrowser=readSettings()

    # Launch the selected browser based on the operating system in use.
    match platformID:
        case 'system.platform.windows':
            # Append the launcher options
            browOpts=browserOptions(selBrowser)
            browRun=[selBrowser.FQFN, *browOpts, url]
            # DEBUGGING # xbmcgui.Dialog().ok(addon_name,browRun)
            xbmcgui.Dialog().notification("Browser Launcher",f"Starting the {selBrowser.name} web browser..",xbmcgui.NOTIFICATION_INFO)
            subprocess.Popen(browRun)

        case 'system.platform.linux':
            # For linux, need to determine if Kodi is running in a Flatpak sandbox and adjust 
            # execution calls accordingly.

            # Append the launcher options
            browOpts=browserOptions(selBrowser)
            browRun=[selBrowser.FQFN, *browOpts, url]
            # See if running in a Linux Flatpak sandbox.
            if xbmcvfs.exists("/.flatpak-info"):
                browRun = ["flatpak-spawn","--host", *browRun]
            # DEBUGGING # xbmcgui.Dialog().ok(addon_name,browRun)
            xbmcgui.Dialog().notification("Browser Launcher",f"Starting the {selBrowser.name} web browser..",xbmcgui.NOTIFICATION_INFO)
            subprocess.Popen(browRun)
        
        case 'system.platform.android':
            # See if we can launch the android browser.
            xbmc.executebuiltin('StartAndroidActivity("'+selBrowser.FQFN+'","android.intent.action.VIEW","","'+url+'")')
        case _:
            xbmcgui.Dialog().ok(addon_name,translation(30026)+'!')

# Main execution block starts here

# sys.argv[0] is always the script name/path. 
# sys.argv[1-n] contains the query string if passed from a skin or menu.
if len(sys.argv) > 1:
    # Example 1: If passed as a comma delimited query string 
    exitNow=False
    for param in sys.argv:
        param1=param.split("=",1)
        match param1[0].lower():
            case "setting":
                if param1[1]=="Browser":
                    setBrowser(param1[1])
                elif param1[1]=="BrowserProfile":
                    # This call displays the full BrowserProfile path in a dialog box 
                    # large enough to show the entire value.
                    isValid, browserProfile=guiSettings.getGuiSetting("BrowserProfile")
                    if isValid:
                        xbmcgui.Dialog().ok("Profile Path",browserProfile)
                exitNow=True
                break
            case "url":
                url=param1[1]
            case "stopplayback":
                stopPlayback=param1[1].lower()
            case "usekiosk":
                useKiosk=param1[1].lower()
            case "useragent":
                userAgent=param1[1]
    if not exitNow:
        browserLaunch(url,stopPlayback)
else:
    xbmcgui.Dialog().ok(addon_name,translation(30025))
