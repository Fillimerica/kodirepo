import sys
import urllib.parse
import xbmcaddon
import xbmcgui
import os
import subprocess

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
profileFolder=addon.getAddonInfo('profile')
addonsettings= addon.getSettings()

# Define defaults for the browser parameters
url=''
stopPlayback='yes'
useKiosk='yes'
userAgent='fred'

# Windows default browser types enumeration (0=Chrome, 1=Firefox) 
# define default paths to the exe.
# For each enumeration, define the parameters that go with the corresponding browser.
bPath = ['C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
         'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe']
bKiosk = ['--kiosk ', '-kiosk ']
bProfile = ['--user-data-dir=', '-profile ']
bAgent = ['--user-agent=', '']
bExtra = ['--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run ',
          '']

# Read in the settings from Settings.xml
winBrowser=addonsettings.getInt('winBrowser') ## Windows - browser type (non-custom 0=Chrome, 1=Firefox)

useCustomPath=addonsettings.getBool('useCustomPath') ## Windows - use a custom path instead of the winBrowser defaults
customPath=addonsettings.getString('CustomPath') ## Windows - custom browser FQFN if useCustomPath=true

useOwnProfile=addonsettings.getBool('useOwnProfile') ## Whether to use the logged in browser profile or a temporary one

androidBrowserID=addonsettings.getString('androidBrowser') ## Android (TV) - the Android Browser ID
# End of Settings

def browserCommandLine(selBrowser):
    # This functon forms and returns the command line options for the
    # selected browser.
    profile = ""
    if (useOwnProfile) and (bProfile[selBrowser]):
        profile = bProfile[selBrowser]+'"'+os.path.join(profileFolder,str(winBrowser))+'" '
    if (useKiosk=="yes") and (bKiosk[selBrowser]):
        kiosk = bKiosk[selBrowser]
    else:
        kiosk=""
    if (userAgent) and (bAgent[selBrowser]):
        agent = bAgent[selBrowser]+'"'+userAgent+'" '
    else:
        agent=""
    return profile+agent+bExtra[selBrowser]+kiosk

# Internal functions
def browserLaunch(url,stopPlayback):
    # This function formats an execution string to the target browser
    # and passes the parameters to display the desired website.
    
## TF 02/2026 Enhance launcher to support android TV devices.

    if stopPlayback == "yes": xbmc.Player().stop() 
    
    # Determine which operating system
    if xbmc.getCondVisibility('system.platform.windows'):
        # Select the FQFN for the desired browser
        if useCustomPath:
            browserFQFN=customPath
        else:
            browserFQFN=bPath[winBrowser]

        # Append the launcher options
        browRun='"'+browserFQFN+'" '+browserCommandLine(winBrowser)+'"'+url+'"'
        # DEBUGGING # xbmcgui.Dialog().ok(addon_name,browRun)
        subprocess.Popen(browRun)
    elif xbmc.getCondVisibility('system.platform.android'):
        # See if we can launch the android browser.
        selBrowser = addon.getSetting("androidBrowser")
        xbmc.executebuiltin('StartAndroidActivity("'+selBrowser+'","android.intent.action.VIEW","","'+url+'")')
    else:
        xbmcgui.Dialog().Ok(addon_name,str(translation(30026))+'!')

# Main execution block starts here

# sys.argv[0] is always the script name/path. 
# sys.argv[1-n] contains the query string if passed from a skin or menu.
if len(sys.argv) > 1:
    # Example 1: If passed as a comma delimited query string 
    for param in sys.argv:
        param1=param.split("=",1)
        match param1[0].lower():
            case "url":
                url=param1[1].lower()
            case "stopplayback":
                stopPlayback=param1[1].lower()
            case "usekiosk":
                useKiosk=param1[1].lower()
            case "useragent":
                userAgent=param1[1].lower()

    browserLaunch(url,stopPlayback)
else:
    xbmcgui.Dialog().ok(addon_name,'No parameter passed, must pass at least 1 value to be valid.')