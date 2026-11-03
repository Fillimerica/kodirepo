# This module allows lauching an external web browser with a url from within Kodi.
# The installed list of abailable browsers is dynamically aquired from the operating
# system, and the settings dialog handles configuring a default browser along with
# browser specific options, and an optional isolated profile.
# Operating system support: Windows (32 & 64 bit), Linux (non-flatpak only due to sandbox restrictions)

# C 2026 Thomas Filliman


import sys
import os
import urllib.parse
import xbmc
import xbmcaddon
import xbmcgui
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
profileFolder=addon.getAddonInfo('profile')
addonsettings= addon.getSettings()

# Define defaults for the browser parameters
url=''
stopPlayback='yes'
useKiosk='yes'
userAgent=''

platformID=browserList.getPlatformID()
platformBrowList=browserList.getBrowserList(platformID)

# Define support function shortcuts. (translation is a function, even though it looks like a variable)
translation=addon.getLocalizedString

# Define settings globals used in browser launch function
browserProfile=''

def readSettings():
    global browserProfile
    
    # Read in the settings from Settings.xml
    browIndex=addonsettings.getInt('BrowserIndex') ## Index into master browser configuration for the selected browser.
    if (browIndex > -1) and (browIndex < len(platformBrowList)):
        selBrowser=platformBrowList[browIndex]
    else:
        selBrowser=None

    useIsolatedProfile=addonsettings.getBool('useIsolatedProfile') ## Whether to use the default browser profile or a custome one.
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
    sFieldIndexID=sFieldID+"Index"
    sFieldProfilePath=sFieldID+"Profile"
    
    # Retrieve the current browser index, in case there is already a configured browser for this addon.
    isValid, curBrowIndexStr=guiSettings.getGuiSetting(sFieldIndexID)
    if not isValid:
        xbmc.log(f"{translation(30028)}{sFieldIndexID}",xbmc.LOGERROR)
        return
    curBrowIndex=int(curBrowIndexStr)
    if curBrowIndex < 0:
        curProfile=""
    else:
        isValid, curProfile=guiSettings.getGuiSetting(sFieldProfilePath)
        if not isValid:
            xbmc.log(f"{translation(30028)}{sFieldProfilePath}",xbmc.LOGERROR)
            return

    # Build a list of just the browser names for the Kodi select dialog.
    browListNames=[brow.description for brow in platformBrowList]
    
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
                        case "firefox":
                            # Call the Firefox specific initialization code.
                            createProfileFirefox(curProfile,selValue)
                        case "chrome":
                            # Call the Chrome specific initialization code.
                            createProfileChrome(curProfile,selValue)
                        case "msedge":
                            # Call the Edge specific initialization code.
                            createProfileEdge(curProfile,selValue)
                        case _:
                            xbmcgui.Dialog().ok(addon_name,f"{translation(30031)}{platformBrowList[selValue].name}")
                            return
                else:
                    # Use the default browser profile.
                    curProfile=""
                # Final validation check prior to saving
                if (selValue != -1):
                    # Save the selected browser information into the settings.
                    addon.setSetting(id=sFieldID,value=platformBrowList[selValue].name)
                    addon.setSettingInt(id=sFieldIndexID,value=selValue)
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

def browserCommandLine(selBrowser):
    # This functon forms and returns the command line options for the
    # selected browser.
    profile = ""
    if (browserProfile):
        profile = selBrowser.profile+browserProfile
    if (useKiosk=="yes") and (selBrowser.kiosk):
        kiosk =selBrowser.kiosk
    else:
        kiosk=""
    if (userAgent) and (selBrowser.agent):
        agent = selBrowser.agent+'"'+userAgent+'" '
    else:
        agent=""
    return profile+agent+selBrowser.extra+kiosk

def browserLaunch(url,stopPlayback):
    # This function formats an execution string to the target browser
    # and passes the parameters to display the desired website.
    
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
    if platformID in ['system.platform.windows','system.platform.linux']:
        # Verify that the selBrowser.FQFN exists.
        while not os.path.isfile(selBrowser.FQFN):
            tMsg=translation(30017)+"\n"
            tMsg=tMsg+"Browser Name: "+selBrowser.name+"\n"
            tMsg=tMsg+"EXE: "+selBrowser.FQFN+"\n\n"
            tMsg=tMsg+translation(30016)
            tDlgRC=xbmcgui.Dialog().yesno(addon_name,tMsg,translation(30001),translation(30002),0,xbmcgui.DLG_YESNO_YES_BTN)
            # If user chooses to cancel exit the addon completely
            if not tDlgRC:
                return
            # Open the settings for the addon to allow the user to adjust the configuration.
            addon.openSettings()
            selBrowser=readSettings()
        # Append the launcher options
        browRun=[selBrowser.FQFN,browserCommandLine(selBrowser),url]
        # DEBUGGING # xbmcgui.Dialog().ok(addon_name,browRun)
        xbmcgui.Dialog().notification("Browser Launcher",f"Starting the {selBrowser.name} web browser..",xbmcgui.NOTIFICATION_INFO)
        subprocess.Popen(browRun)
        
    elif platformID=='system.platform.android':
        # See if we can launch the android browser.
        xbmc.executebuiltin('StartAndroidActivity("'+selBrowser.FQFN+'","android.intent.action.VIEW","","'+url+'")')
    else:
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
