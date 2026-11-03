# This module implements the custom "callback" from the Kodi Settings.xml
# configuration process.
# This allows the script setup to handle highly customized setup steps while
# still presenting the user with a standard Kodi setup diulog.
# Written by Thomas Filliman
# Version 1.0 - October 2026

import sys
import os
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
addon_path=xbmcvfs.translatePath(addon.getAddonInfo('path'))
addon_data_path=xbmcvfs.translatePath(f"special://profile/addon_data/{addon_id}")

platformID=browserList.getPlatformID()
platformBrowList=browserList.getBrowserList(platformID)

# Define support function shortcuts. (translation is a function, even though it looks like a variable)
translation=addon.getLocalizedString

def setBrowser(sFieldID):
    # This specialized function reads the list of browsers for the current platform and allows the user to select one.
    # Interaction with the settings.xml file uses hard-coded field ID suffix of "Index"
    # Get the current value of sFieldID (str)
    if IsWebPDB:
        pass # needed to complete if statement when debugging is disabled.
        #web_pdb.set_trace()
    
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
            # User selected a browser. If it has changed or a profile does not exist, create the profile path.
            if (not curProfile) or (selValue != curBrowIndex):
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

                # Final validation check prior to saving
                if (curProfile) and (selValue != -1):
                    # Save the selected browser information into the settings.
                    addon.setSetting(id=sFieldID,value=platformBrowList[selValue].name)
                    addon.setSettingInt(id=sFieldIndexID,value=selValue)
                    addon.setSetting(id=sFieldProfilePath,value=curProfile)
                    addon.setSetting(id="BrowserProfileButton",value="Select to Show")
                else:
                    xbmcgui.Dialog().ok(addon_name,translation(30027))
            # Exit the while loop after the profile was created or left unchanged     
            break
    # End of while loop

def setLinuxPermissions():
    # This function makes sure that the selenium-manager on Linux
    # has the correct permissions to be executed.
    selMgrLinux=xbmcvfs.validatePath(addon_path+"/lib/selenium/webdriver/common/linux-x86_64/selenium-manager")
    if os.path.isfile(selMgrLinux):
        os.chmod(selMgrLinux, 0o755)

# Main called code starts here.    
if len(sys.argv) > 1:
    # Example 1: If passed as a comma delimited query string 
    for param in sys.argv:
        param1=param.split("=",1)
        match param1[0].lower():
            case "setting":
                if param1[1]=="Browser":
                    # This call processes the selected browser and establishes the profile path.
                    setBrowser(param1[1])
                    # Need to set file permission on the linux selenium-manager so it can be executed.
                    if platformID=="system.platform.linux":
                        setLinuxPermissions()
                elif param1[1]=="BrowserProfile":
                    # This call displays the full BrowserProfile path in a dialog box 
                    # large enough to show the entire value.
                    #web_pdb.set_trace()
                    isValid, browserProfile=getGuiSetting("BrowserProfile")
                    if isValid:
                        xbmcgui.Dialog().ok("Profile Path",browserProfile)
            case _:
                # This is the fall-through error condition. Advise user that and invalid script request was made.
                xbmc.log(f"{translation(30029)}{param[0]}",xbmc.LOGERROR)

else:
    xbmcgui.Dialog().ok(addon_name,translation(30025))
