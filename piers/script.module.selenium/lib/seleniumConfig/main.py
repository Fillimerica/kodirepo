# This module implements the custom "callback" from the Kodi Settings.xml
# configuration process.
# This allows the script setup to handle highly customized setup steps while
# still presenting the user with a standard Kodi setup diulog.
# Written by Thomas Filliman
# Version 1.0 - October 2026

import sys
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

# Helper function to handle interface calls with guiSettings module.
def getGuiSetting(settingName,errReport=3):
    # This function is a shortcut helper that handles calling the guiSettings module
    # and handling the default error reporting.
    # In: settingName = Setting name of the setting to get the current value.
    # In: [optional] errReport = how to handle error reporting. Integer code:
    #   0=No error reporting, return error code as 2nd variable.
    #   1=Log to the Kodi log file, return error code as the 2nd variable.
    #   2=Display an error dialog to the user, return error code as the 2nd variable.
    #   3=[default] Both Log and Display, return error code as the 2nd variable.
    errorCode, retVal=guiSettings.getSetting(settingName)
    if errorCode != "":
        guiSettings.displayErrorMessage(errorCode,settingName,errReport)
        return False,errorCode
    return True,retVal

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

    # Pass the profile creationn command to the browser.
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

    # Pass the profile creationn command to the browser.
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

    # Pass the profile creationn command to the browser.
    process = subprocess.run(cmd)
   
    # All finished, remove the processing message
    p_dialog.close()


def setBrowser(sFieldID):
    # This specialized function reads the list of browsers for the current platform and allows the user to select one.
    # Interaction with the settings.xml file uses hard-coded field ID suffix of "Index"
    # Get the current value of sFieldID (str)
    #web_pdb.set_trace()
    
    sFieldIndexID=sFieldID+"Index"
    sFieldProfilePath=sFieldID+"Profile"
    
    # Retrieve the current browser index, in case there is already a configured browser for this addon.
    isValid, curBrowIndexStr=getGuiSetting(sFieldIndexID)
    if not isValid:
        return
    curBrowIndex=int(curBrowIndexStr)
    # Translate the unique index into the real index for the Kodi select dialog.
    if curBrowIndex < 0:
        curAbsIndex=-1
        curProfile=""
    else:
        curAbsIndex = next((i for i, brow in enumerate(platformBrowList) if brow.index == curBrowIndex), -1)
        isValid, curProfile=getGuiSetting(sFieldProfilePath)
        if not isValid:
            return

    # Build a list of just the browser names for the Kodi select dialog.
    browListNames=[brow.name for brow in platformBrowList]
    
    selValue=-1
    while selValue == -1:
        # Obtain the desired browser selection from the Kodi GUI 
        selValue=xbmcgui.Dialog().select(translation(30014),browListNames,0,curAbsIndex)
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
            if (not curProfile) or (selValue != curAbsIndex):
                # Need to create the profile path for the selected browser.
                # See if a custom path override has been selected.
                isValid, proPathOverride=getGuiSetting("ProfilePathOverride")
                if not isValid:
                    return
                if proPathOverride:
                    isValid, curProfile=getGuiSetting("ProfilePathCustom")
                    if not isValid:
                        return
                    if not xbmcvfs.exists(curProfile):
                        xbmcgui.Dialog().ok(addon_name,translation(30043))
                        return
                else:
                    isValid, profileSuffix=getGuiSetting("ProfileSuffix")
                    if not isValid:
                        return
                    curProfile=xbmcvfs.validatePath(addon_data_path+"/"+platformBrowList[selValue].name+"/"+profileSuffix+"/")

                # Call the browser specific profile creation function.
                if platformBrowList[selValue].name.lower() == "firefox":
                    # Call the Firefox specific initialization code.
                    createProfileFirefox(curProfile,selValue)
                elif platformBrowList[selValue].name.lower() == "chrome":
                    # Call the Chrome specific initialization code.
                    createProfileChrome(curProfile,selValue)
                elif platformBrowList[selValue].name.lower() == "edge":
                    # Call the Edge specific initialization code.
                    createProfileEdge(curProfile,selValue)
                else:
                    xbmcgui.Dialog().ok(addon_name,translation(30026))
                    return

                # Final validation check prior to saving
                if (curProfile) and (selValue != -1):
                    # Save the selected browser information into the settings.
                    addon.setSetting(id=sFieldID,value=platformBrowList[selValue].name)
                    addon.setSettingInt(id=sFieldIndexID,value=platformBrowList[selValue].index)
                    addon.setSetting(id=sFieldProfilePath,value=curProfile)
                    addon.setSetting(id="BrowserProfileButton",value="Select to Show")
                else:
                    xbmcgui.Dialog().ok(addon_name,translation(30027))
            # Exit the while loop after the profile was created or left unchanged     
            break
    # End of while loop

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
