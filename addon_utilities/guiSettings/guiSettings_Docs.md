### Instructions for using the guiSettings Python module.

###### Purpose: the guiSettings module exposes settings that are defined in settings.xml and are displayed to the user via the DialogAddonSettings.xml, inside scripts called from RunScript within a format="action". This allows the script to evaluate and act upon the current values that the user has chosen, selected, or entered in the dialog.

##### Configuration

In the settings.xml file:

1. The first setting in each "category" must be of type="button" and format="action". If that type is not appropriate for the first setting, then one must still be created and can be set with `<visible>false</visible>`. Assign the label an id# that is unique and the `<default>` tag should be a unique text string that will be matched at run-time for a sanity check. For example:

   ```
   <setting id="TopControlMarker" type="string" label="30000" help="">
       <level>0</level>
       <visible>false</visible>
       <default>TopControlSanityCheck</default>
       <control type="button" format="action">
       </control>
   </setting>
   ```

2. Construct the remainder of the settings.xml file according to the Kodi documentation.

3. For this code module to be utilized, at least one of the settings needs to be `<control type="button" format="action">`, with a `<data>` tag that calls a RunScript(script-name,parameteres). It is within this script call that the guiSettings module will be used. For example:

```
<setting id="ProfileButton" type="string" label="30050" help="">
	<level>0</level>
	<default>Select to Show</default>
	<control type="button" format="action">
		<data>RunScript(script.module.testme,setting=ProfileButton)</data>
	</control>
</setting>
```

In the guiSettings.py module:

1. Open the guiSettings.py module in an editor (python-aware is recommended).
2. Scroll down to the section that defines the settingsMap. There will be one entry for a typical 1st setting entry that was defined in Step #1 of the settings.xml configuration. Edit this entry as follows:
   1. For the name, change it to match the exact translated label value used as specified in the addon's strings.po file.
   2. For the offset, leave it at 0 as this is the 1st entry in the category.
   3. For ctrlType, leave it as "label2".
   4. For sCheck, change it to match the value that was specified in the `<default>`tag.
3. Append additional settingsMapType rows, one for each setting in the settings.xml file. Technically, only settings that need to have their values read by the script need to be added, but it won't matter if all the settings are listed either. For each setting assign the parameters as follows:
   1. For the name, specify the setting's id string (not its translated label).

   2. For the offset, calculate the ***relative*** offset of this setting from the 1st group setting that was configured in step #2. Generally speaking, each setting in sequence will have an offset that increments by 1. However, when crossing group boundaries the visible group displayed counts as a skip of 2 (one for the separator and 1 for the group text line). So offsets are not always sequential. Another method to calculate the offset is to turn on debugging in Kodi and then bring up the settings for the Addon. The on-screen display will show an internal ID# next to the Focused keyword starting at -179 and progressing upwards for most settings.

   3. For the ctrlType, there are three possible strings that correspond to recognized settings types:

      1. "bool" for toggles (control type="toggle")
      2. "text" for edit fields (control type="edit")
      3. "label2" for buttons and selectors (control type="button" or "list")
      4. Unfortunately, at this time spinners and sliders (control type="spinner" and "slider") are not supported and can't be accessed by python.

   4. For the sCheck, only if ctrlType is "label2" specify the translated Kodi string assigned to the setting's label. The shortcut of translate(nnnnn) where nnnnn is the Kodi string ID as specified in the addon's strings.po file can be used instead. For ctrlType="bool" or "text" this attribute is unused and can be left blank or unspecified.

      For example, for a path selector with a strings.po ID of 30041, this would be the settingsMapType entry to create:

      ```
      <setting id="ProfilePathCustom" type="path" label="30041" help="30002">
          <level>0</level>
          <default>n/a</default>
          <constraints>
              <allowempty>true</allowempty>
          </constraints>
          <control type="button" format="path">
              <heading>30041</heading>
          </control>
      </setting>
      ```

      ```
      settingsMapType(name="ProfilePathCustom",offset=2,ctrlType="label2",sCheck=translate(30041)),
      ```

   5. Save the modified python module **in the addon's code folder** (typically where <extension point="xbmc.python.script" library= is pointing). Then close this editing window.

##### Usage

In the the script file called by RunScript from within settings.xml:

1. Add to imports section prior to 1st use of functions:
     **import guiSettings**
2. Read a reference to a setting:
    **errorCode, settingValue = guiSettings.getSetting("SettingName")**
    where "SettingName" is the setting ID name (not the label) that was specified in the name= parameter of the settingsMapType for the setting of interest.
    Two strings are returned:
   1. The 1st is a result code that indicates the type of error returned if any.
   2. The 2nd is the actual value of the setting if there was no error.
   * If errorCode is blank =="" the settingValue holds the value from SettingName.
   * If errorCode is not blank, then an error was thrown and settingValue is undefined. errorCode will contain the reason for the error. If desired a subsequent call to **guiSettings.displayErrorMessage(errorCode,"SettingName", dispType)** can be made.
3. The displayErrorMessage() function decodes the error code into a descriptive string, then either displays it to the user, writes it to the Kodi log file, or both. Parameters:
   1. errorCode = the coded error string from the output of a prior guiSettings.getSetting call.
   2. "SettingName" = the name of the setting that was used in the prior guiSettings.getSetting call.
   3. dispType = the type of output to generate (integer number) as follows:
      * 1= Write a descriptive error string to the Kodi log file.

      * 2=Display a dialog message to the user containing a description of the error.

      * 3=Both Log and Display the descriptive error message.

##### Example

The script.module.selenium addon illustrates the typical usage of this module.
That addon can be found in the TJF Repository here: https://github.com/Fillimerica/kodirepo
and the source code can be found here: https://github.com/Fillimerica/kodiaddon-script.module.selenium
