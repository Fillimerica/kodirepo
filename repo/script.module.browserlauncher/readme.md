### Kodi Script Addon to Display Websites in a Browser

This addon supports the launching of a web-url in the local system browser. Currently works on Windows and Android TV Boxes.

Tested with Kodi Omega and Piers

#### Installation in Kodi:

<u>Method 1: From the TJF Repository</u>

Repository link:  https://fillimerica.github.io/kodirepo/

1. Enable "Unknown Sources" in Kodi Settings > System > Add-ons
2. Add the TJF Repository to the Kodi Sources in the Kodi File Manager
   1. Go to Settings > File manager
   2. Select "Add source" in either pane.
   3. Copy and paste (or type) the repository link listed above into the larger "Enter path..." edit box.
   4. In the smaller edit box under "Enter a name for this media source.", give the repository link a meanigful name such as "TJF Repository"
   5. Select OK to save this source.
3. Install the Repository as an add-on:
   1. Go to Settings > Add-ons
   2. Select "Install from zip file" (NOT install from repository at this point)
   3. In the "install from zip file" dialog, select the source that was added in step #2 above.
   4. A single zip file should appear in the list, select it to install the TJF Repository.
4. Install the BrowserLauncher add-on from the TJF Repository
   1. Go to Settings > Add-ons (if not already there)
   2. This time choose "Install from repository", and select the "TJF Repository" from the list.
   3. Choose "Program add-ons" from the category list.
   4. Choose "Browser Launcher" from the list. The Browser Launcher add-on will be installed.

<u>Method 2: From the Github Code Source</u>

1. From the github project repository, click on the green Code button and choose the "Download ZIP" option.
2. Depending on your browser configuration you may be prompted to choose a download location and/or a file name. In some configurations this is bypassed in favor of automatic downloading into a designated Downloads folder. In either case make sure the zip file that is downloded is copied or moved into a location that Kodi can access in the Kodi File Manager.
3. Enable "Unknown Sources" in Kodi Settings > System > Add-ons
4. Install the Browser Launcher add-on:
   1. Go to Settings > Add-ons
   2. Select "Install from zip file"
   3. In the "install from zip file" dialog, select the zip file that was downloaded in step #2 above. The Browser Launcher add-on will be installed.

### Configuration

To configure the local browser that will be used, go to Settings > Add-ons > My Add-ons > Program add-ons, and select "Browser Launcher" from the list. Then Choose the Configure Option Button.

#### Usage

This add-on is meant to be invoked via the RunScript function typically from a custom skin menu or by a favourites shortcut such as can be generated with the FavouritesGroup add-on. The Kodi RunScript function takes the addon ID as the first parameter followed by one or more comma separated parameters to be passed to the Browser Launcher. 

##### Parameters:

* url=[web url] provide the complete url the browser should display. commas are prohibited but all other characters that are typically part of a standard url are allowed. Quoting and escaping are not required.

* stopPlayback=[yes or no] , whether to instruct Kodi to stop any media playback that is in progress, default if omitted is StopPlayback=yes.

* useKiosk=[yes or no] , whether to start the browser in "kiosk" mode (full-screen) if supported, default if omitted is useKiosk=yes.

* userAgent=[user agent value] for browsers that support setting the userAgent on the command line, this parameter specifies that the user agent should be set and the value to use. Ignored on browsers that do not support user agent overrides.

##### Example:

RunScript(script.module.browserlauncher,url=https://weather.imagemaster.org,useKiosk=no)
