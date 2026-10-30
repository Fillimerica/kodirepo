# This support module implements the somewhat kludgey direct access to settings dialog GUI
# objects so that support modules can read the current settings values while the settings 
# dialog is currently being displayed.

# IMPORTANT! The SettingsMap structure defined below must be configured to match the actual settings
# that are defined in settings.xml (at least the ones that need to be read from within any RunScript
# calls). The best way to expose the offset values is to enable debug logging and then use the mouse
# to hover over the elements displayed in the running DialogAddonSettings.xml dialog.
# The offset is the relative offset from the TopControlMarker setting, which is always at offset 0.

import xbmc
import xbmcgui
import xbmcaddon
import web_pdb

# Define support function shortcuts.
translate=xbmcaddon.Addon().getLocalizedString

# This is the SettingsMap, which identifies where and how to access each setting.
# Format is Name,Offset from Anchor,ControlType,SanityCheck
# ControlTypes: bool,label2,text
class settingsMapType:
    def __init__(self, name: str, offset: int, ctrlType:str, sCheck:str=""):
        self.name=name
        self.offset=offset
        self.ctrlType=ctrlType
        self.sCheck=sCheck

SettingsMap: list[settingsMapType] = [
    settingsMapType(name="TopControlMarker",offset=0,ctrlType="label2",sCheck="TopControlSanityCheck"),
    settingsMapType(name="ProfilePathOverride",offset=1,ctrlType="bool"),
    settingsMapType(name="ProfilePathCustom",offset=2,ctrlType="label2",sCheck=translate(30041)),
    settingsMapType(name="ProfileSuffix",offset=3,ctrlType="text"),
    settingsMapType(name="Browser",offset=6,ctrlType="label2",sCheck=translate(30013)),
    settingsMapType(name="BrowserIndex",offset=7,ctrlType="text"),
    settingsMapType(name="BrowserProfileButton",offset=8,ctrlType="label2",sCheck=translate(30050)),
    settingsMapType(name="BrowserProfile",offset=9,ctrlType="text")
    ]

# Addon global constants
addon_name="GUI Settings Manager"

# define a global pointer to the currently active dialog.
dlgWindow=0

# ControlAnchor holds the numeric ID of the TopControlMarker setting in the GUI. It serves to anchor
# the relative position of all the other settings.
# The default 1st Setting Object is defined in Kodi in file GUIDialogSettingsBase.h 
# as CONTROL_SETTINGS_START_CONTROL = -180.
# Since the 1st control is typically the group header (which isn't identifiable)
# the TopControlMarker will therefore be +1 or at -179.
# As of 10/2026 this has been confirmed in Kodi Omega & Piers.
ExpectedAnchor=-179
ControlAnchor=0

msg3000="Anchor was Not Found at Expected Location. Trying a Range..."

def getAnchor():
    # This function sets the anchor point of the TopControlMarker setting
    # within the current dialog window's controls.
    # Updates global variable ControlAnchor if sucessful.
    global ControlAnchor
    
    # Retrieve the TopControlMarker from the settingsMap (should be the only one at offest=0
    curSettingMap=next((item for item in SettingsMap if item.offset == 0),None)
    if curSettingMap==None:
        msg= f"TopControlMarker with offset=0 can not be found in the settingsMap. Check the settingsMap configuration."
        xbmc.log(msg,xbmc.LOGERROR)
        xbmcgui.Dialog().ok(addon_name+" Error",msg)
        return
    # 1st try to get the anchor at the ExpectedAnchor ID
    try:
        markerText=dlgWindow.getControl(ExpectedAnchor).getLabel()
    except:
        markerText=""
    if markerText == curSettingMap.name:
        # Marker was found at the expected position, set and return.
        ControlAnchor=ExpectedAnchor
        return
    
    # Anchor was not found at the ExpectedAnchor ID, try a numeric range to see if it moved
    # but is still discoverable.
    xbmcgui.Dialog().notification(addon_name,msg3000,xbmcgui.NOTIFICATION_WARNING)
    for i in range(-180,0,1):
        try:
            markerText=dlgWindow.getControl(ExpectedAnchor).getLabel()
        except:
            markerText=""
        if markerText == curSettingMap.name:
            # Marker was found at an alternate position, set and return.
            ControlAnchor=i
            msg= f"Anchor was found at ID={i}\nPleqase notify the addon developer."
            xbmc.log(msg,xbmc.LOGWARNING)
            xbmcgui.Dialog().ok(addon_name+" Warning",msg)
            return
    # Achor point still not found even after a range search. This is fatal.
    msg= f"Anchor marker can not be located. Unable to determine settings value. Pleqase notify the addon developer."
    xbmc.log(msg,xbmc.LOGERROR)

def displayErrorMessage(errorCode,settingName="",dispType=1):
    # This function writes a coded error message to the Kodi log file 
    # or displays a dialog box to the user on-screen, or both.
    # Designed to be called either internally or by the parent.
    # dispType: 1=Log only, 2=display only, 3=both log and display error code message.
    match errorCode:
        case "ERR_NOANCHOR":
            msg= f"Anchor marker can not be located. Unable to determine settings value."
        case "ERR_SETTINGNOTFOUND":
            msg= f"Setting \"{settingName}\" can not be located wihtin the SettingsMap.\nCheck the SettingsMap definition in the source code."
        case "ERR_GETCONTROL":
            msg= f"Unable to query getControl for setting \"{settingName}\" .\nCheck the SettingsMap definition in the source code."
        case "ERR_SETTINGFAILEDSANITY":
            msg= f"Setting \"{settingName}\" failed the sanity check wihtin the SettingsMap.\nCheck the SettingsMap definition in the source code."
        case "ERR_UNKNOWNCTRLTYPE":
            msg= f"The control type defined in the SettingsMap for setting \"{settingName}\" is unknown.\nCheck the SettingsMap definition in the source code."
        case _:
            msg=f"Unknown error code passed to displayErrorMessage. Code={errorCode}."
    if (dispType==1) or (dispType==3):
        # Log to Kodi log file.
        xbmc.log(msg,xbmc.LOGINFO)
    if (dispType==2) or (dispType==3):
        # Display a messagebox to the user.
        xbmcgui.Dialog().ok(addon_name+" Error",msg)

def getSetting(settingName):
    # In: settingName = Setting name of the setting to get the current value.
    # Returns: ErrorCode (str) "" if no error, otherwise string error code.
    # Returns: value of settingName if there was no error.

    # Assign the current window ID to a global variable.
    
    global dlgWindow
    if dlgWindow == 0:
        dlgWindow=xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
    
    # Check to make sure tha the ControlAnchor was found.
    if ControlAnchor==0:
        getAnchor()
        if ControlAnchor==0:
            return "ERR_NOANCHOR",""

    # ControlAnchor is valid, process settingName
    curSettingMap=next((item for item in SettingsMap if item.name == settingName),None)
    if curSettingMap==None:
        return "ERR_SETTINGNOTFOUND",""
    
    # SettingsMap for the passed setting has been located. Process the mode and ctrlType.
    tValid=True
    tErrorCode=""
    retVal=""
    match curSettingMap.ctrlType:
        case "bool":
            # no sanity check, .isSelected() returns the state.
            try:
                retVal=dlgWindow.getControl(ControlAnchor+curSettingMap.offset).isSelected()
            except:
                tValid=False
                tErrorCode="ERR_GETCONTROL"
        case "text":
            # no sanity check, .getText() hopefully returns the value.
            try:
                retVal=dlgWindow.getControl(ControlAnchor+curSettingMap.offset).getText()
            except:
                tValid=False
                tErrorCode="ERR_GETCONTROL"
        case "label2":
            # sanity check, .getLabel2() hopefully returns the value.
            try:
                if not dlgWindow.getControl(ControlAnchor+curSettingMap.offset).getLabel()==curSettingMap.sCheck:
                    tValid=False
                    tErrorCode="ERR_SETTINGFAILEDSANITY"
            except:
                tValid=False
                tErrorCode="ERR_GETCONTROL"
            # Did the sanity check pass?
            if tValid:
                try:
                    retVal=dlgWindow.getControl(ControlAnchor+curSettingMap.offset).getLabel2()
                except:
                    tValid=False
                    tErrorCode="ERR_GETCONTROL"
        case _:
            # This is the fall-through for a non-matching ctrlType
            tValid=False
            tErrorCode="ERR_UNKNOWNCTRLTYPE"
            msg= f"Unknown SettingsMap.ctrlType value={curSettingMap.ctrlType}for setting \"{settingName}\". Check the SettingsMap definition in the source code."
            xbmc.log(msg,xbmc.LOGERROR)

    # Send the return code and the data back to the caller.
    return tErrorCode, retVal
