import sys
import os
import urllib.parse
import xbmcaddon
import xbmcgui
import subprocess
import browserList
#import web_pdb

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
profileFolder=addon.getAddonInfo('profile')
addonsettings= addon.getSettings()

# Define defaults for the browser parameters
url=''
stopPlayback='yes'
useKiosk='yes'
userAgent='fred'

platformID=browserList.getPlatformID()
platformBrowList=browserList.getBrowserList(platformID)

def translation(kodiStringID):
    # This function wraps the Kodi getLocalizedString function for shorthand use.
    return addon.getLocalizedString(kodiStringID)

def readSettings():
    global selBrowser,useCustomPath,customPath,useOwnProfile
    
    # Read in the settings from Settings.xml
    browIndex=addonsettings.getInt('BrowserIndex') ## Index into master browser configuration for the selected browser.
    selBrowser=next((brow for brow in platformBrowList if brow.index == browIndex), None)

    useCustomPath=addonsettings.getBool('useCustomPath') ## Windows - use a custom path instead of the winBrowser defaults
    customPath=addonsettings.getString('CustomPath') ## Windows - custom browser FQFN if useCustomPath=true

    useOwnProfile=addonsettings.getBool('useOwnProfile') ## Whether to use the logged in browser profile or a temporary one
    # End of Settings

def setBrowser(sFieldID):
    # This specialized function reads the list of browsers for the current platform and allows the user to select one.
    # Interaction with the settings.xml file uses hard-coded field ID suffix of "Index"
    # Get the current value of sFieldID (str)
    #web_pdb.set_trace()
    
    sFieldIndexID=sFieldID+"Index"
    curBrowIndex=addon.getSettingInt(id=sFieldIndexID)
    # Translate the unique index into the real index for the Kodi select dialog.
    if curBrowIndex < 0:
        curAbsIndex=0
    else:
        curAbsIndex = next((i for i, brow in enumerate(platformBrowList) if brow.index == curBrowIndex), -1)
    # Build a list of just the browser names for the Kodi select dialog.
    browListNames=[brow.name for brow in platformBrowList]
    # Obtain the desired browser selection from the Kodi GUI 
    selValue=xbmcgui.Dialog().select(translation(30014),browListNames,0,curAbsIndex)
    
    # Save the selected browser information into the settings.
    addon.setSetting(id=sFieldID,value=platformBrowList[selValue].name)
    addon.setSettingInt(id=sFieldIndexID,value=platformBrowList[selValue].index)
    
def browserCommandLine():
    # This functon forms and returns the command line options for the
    # selected browser.
    profile = ""
    if (useOwnProfile) and (selBrowser.profile):
        profile = selBrowser.profile+'"'+os.path.join(profileFolder,selBrowser.name)+'" '
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
    readSettings()
    if selBrowser is None:
        while selBrowser is None:
            tMsg=translation(30015)+"\n"+translation(30016)
            tDlgRC=xbmcgui.Dialog().yesno(addon_name,tMsg,translation(30001),translation(30002),0,xbmcgui.DLG_YESNO_YES_BTN)
            # If user chooses to cancel exit the addon completely
            if not tDlgRC:
                return
            # Open the settings for the addon to allow the user to adjust the configuration.
            addon.openSettings()
            readSettings()

    # Launch the selected browser based on the operating system in use.
    if platformID=='system.platform.windows':
        # Select the FQFN for the desired browser
        if useCustomPath:
            browserFQFN=customPath
        else:
            browserFQFN=selBrowser.FQFN
        # Verify that the browserFQFN exists.
        while not os.path.isfile(browserFQFN):
            tMsg=translation(30017)+"\n"
            tMsg=tMsg+"Browser Name: "+selBrowser.name+"\n"
            tMsg=tMsg+"EXE: "+browserFQFN+"\n\n"
            tMsg=tMsg+translation(30016)
            tDlgRC=xbmcgui.Dialog().yesno(addon_name,tMsg,translation(30001),translation(30002),0,xbmcgui.DLG_YESNO_YES_BTN)
            # If user chooses to cancel exit the addon completely
            if not tDlgRC:
                return
            # Open the settings for the addon to allow the user to adjust the configuration.
            addon.openSettings()
            readSettings()
            # Select the FQFN for the desired browser
            if useCustomPath:
                browserFQFN=customPath
            else:
                browserFQFN=selBrowser.FQFN

        # Append the launcher options
        browRun='"'+browserFQFN+'" '+browserCommandLine()+'"'+url+'"'
        # DEBUGGING # xbmcgui.Dialog().ok(addon_name,browRun)
        subprocess.Popen(browRun)
        
    elif platformID=='system.platform.android':
        # See if we can launch the android browser.
        xbmc.executebuiltin('StartAndroidActivity("'+selBrowser.FQFN+'","android.intent.action.VIEW","","'+url+'")')
    else:
        xbmcgui.Dialog().Ok(addon_name,translation(30026)+'!')

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
