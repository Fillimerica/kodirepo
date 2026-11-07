# This module implements the custom "callback" from the Kodi Settings.xml
# configuration process.
# This allows the script setup to handle highly customized setup steps while
# still presenting the user with a standard Kodi setup diulog.
# Written by Thomas Filliman
# Operating system support: Windows (32 & 64 bit), Linux 

# Version 1.1 - November 2026

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

from browserList import platformID,platformBrowList,IsFlatpak

# Define support function shortcuts. (translation is a function, even though it looks like a variable)
translation=addon.getLocalizedString

def setBrowser(sFieldID):
    # This specialized function reads the list of browsers for the current platform and allows the user to select one.
    
    if IsWebPDB:
        pass # needed to complete if statement when debugging is disabled.
        #web_pdb.set_trace()
    
    # Define the related settings fields in settings.xml
    sFieldFQFN=sFieldID+"FQFN"
    sFieldProfilePath=sFieldID+"Profile"
    sFieldBrowType=sFieldID+"Type"
    
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

    # Selenium only supports specific browsers, so need to filter out all the other
    # installed browsers. However, still need to retain the correct index into the
    # master platformBrowList so that the browser type and options can be saved.
    browListNames=[]
    browListIndex=[]
    curBrowIndex=-1
    for idx,brow in enumerate(platformBrowList):
        if brow.name.lower() in ["chrome","firefox","msedge"]:
            browListNames.append(brow.description)
            browListIndex.append(idx)
            # See if there is a current selection by matching FQFN values.
            if (brow.FQFN==curBrowFQFN) and (curBrowIndex==-1):
                curBrowIndex=len(browListIndex)-1 # Relative index into sub-list for kodi select.

    # If some installed browsers were excluded, advise the user.
    if (len(browListNames) != len(platformBrowList)):
        xbmcgui.Dialog().ok(addon_name,translation(30036))

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
                # Re-assign selValue to the actual index of the selected browser in platformBrowList
                selValue=browListIndex[selValue]
                
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

                # Final validation check prior to saving
                if (curProfile) and (selValue != -1):
                    # Save the selected browser information into the settings.
                    addon.setSetting(id=sFieldID,value=platformBrowList[selValue].description)
                    addon.setSetting(id=sFieldFQFN,value=platformBrowList[selValue].FQFN)
                    addon.setSetting(id=sFieldProfilePath,value=curProfile)
                    addon.setSetting(id=sFieldBrowType,value=platformBrowList[selValue].name)
                    if curProfile:
                        addon.setSetting(id="BrowserProfileButton",value="Select to Show")
                    else:
                        addon.setSetting(id="BrowserProfileButton",value="-browser default-")
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
                    isValid, browserProfile=guiSettings.getGuiSetting("BrowserProfile")
                    if isValid:
                        xbmcgui.Dialog().ok("Profile Path",browserProfile)
            case _:
                # This is the fall-through error condition. Advise user that and invalid script request was made.
                xbmc.log(f"{translation(30029)}{param[0]}",xbmc.LOGERROR)

else:
    xbmcgui.Dialog().ok(addon_name,translation(30025))
