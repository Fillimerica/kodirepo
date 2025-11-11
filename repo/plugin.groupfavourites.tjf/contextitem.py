# Context menu handler for the SubFavourites Plugin
# V1.0 - October 2025

import sys
import xbmcgui
import xbmcvfs
import xml.etree.ElementTree as ET
import re
import urllib.parse as urlparse

# Import the project constants and globals for use within the module.
from constants import *

# Remote debugging module. IsWebPDB determines if it is installed on the system.
if IsWebPDB:
    import web_pdb

# Base XML string for new group
XML_BASE="""
<favourites>
</favourites>
"""

def CreateElement(pItemName):
    """
    This function builds the complete xml entry for the current listitem.
    Called once even if multiple xml files will be updated.
    """

    # Define the new element to add
    NewElement=ET.Element('favourite')
    NewElement.tail="\n"    # Inject xml newline formatting for pre-3.9 python
    NewElement.set('name',pItemName)

    if sys.listitem.isFolder():
        NewElement.set('isFolder','True')
    else:
        NewElement.set('isFolder','False')
        
    iArt=sys.listitem.getArt('thumb')
    if not iArt=='':
        NewElement.set('thumb',iArt)
    else:
        iArt=sys.listitem.getArt('poster')
        #NewElement.set('thumb',iArt)
        NewElement.set('poster',iArt)
        
    # Determine the media type and the correct endpoint.
    l_Path=sys.listitem.getPath()
    l_folder=sys.listitem.isFolder()
    nWindowID=xbmcgui.getCurrentWindowId()
    
    if l_Path[0:9]=="addons://":
        # IsAddon?
        mType='addon'
        mPath=':RunAddon("'+l_Path.rsplit('/')[-1]+'")'
    elif l_Path[0:13]=="favourites://":
        # IsFavourites link?
        mType='favourites'
        # Discovered that some times the path comes through as quoted 
        # and that messes up the kodi function call formatting.
        mPath=':'+urlparse.unquote(l_Path[13:])
    elif l_folder:
        # Media group or playlist folder.
        mType='folder_media'
        mPath=f':ActivateWindow({nWindowID},"{l_Path}",return)'
    elif not sys.listitem.getPictureInfoTag().getResolution()=="":
        # IsPicture?
        mType='picture'
        mPath=f':ShowPicture("{l_Path}")'
    else:
        # Regular Media Endpoint Song/Video
        mType='mediaendpoint'
        mPath=f':PlayMedia("{l_Path}")'

    # Add the item details to the current element.
    NewElement.set('mediatype',mType)
    NewElement.text=mPath
    return NewElement
    

# Save the current listitem into the selected GroupFavorites xml file.
def SaveItem(GroupName,Element):
    GroupFQFN=xbmcvfs.translatePath(DATA_DIR)+'/'+GroupName+'.xml'
    # Open and read the existing values
    xmltree=ET.parse(GroupFQFN)
    xmlroot=xmltree.getroot()
    # Verify the root tag is valid.
    if not xmlroot.tag=='favourites':
        raise ValueError(localize(30111)+f' {xmlroot.tag}!')
        return -1

    # Append the new element into the xml tree.
    if len(xmlroot)>0:
        xmlroot[-1].tail="\n\t"     # Inject xml newline formatting for pre-3.9 python
    else:
        xmlroot.text="\n\t"         # If first entry, make room at the root for the new entry.
    xmlroot.append(Element)
    xmltree.write(GroupFQFN)
    
def CreateNewGroup():
    """
    This function prompts the user for a new group name.
    If one is provided that does not already exist then a basic xml
    shell is created and the name is returned.
    """
    lvalidregex=r'[\\/:\*\?"<>|]'
    fnameraw=""

    # Make sure the addon data folder exists, create it if it does not.
    if not xbmcvfs.exists(DATA_DIR+"/"):
        xbmcvfs.mkdirs(DATA_DIR)
    
    while True:
        fnameraw=xbmcgui.Dialog().input(localize(30104),defaultt=fnameraw)
        if fnameraw=="":
            # User chose to cancel new group creation. Display a confirmation dialog.
            msg=localize(30106)
            if xbmcgui.Dialog().yesno(localize(30105),msg,defaultbutton=xbmcgui.DLG_YESNO_NO_BTN):
                return ""
            else:
                continue
        else:
            # User typed something, verify that it is a valid groupname.
            if re.search(lvalidregex,fnameraw):
                msg=localize(30108)+"[CR]"
                msg=msg+localize(30109)+"="+fnameraw+"[CR][CR]"+localize(30110)
                if xbmcgui.Dialog().yesno(localize(30107),msg,defaultbutton=xbmcgui.DLG_YESNO_YES_BTN):
                    continue
                else:
                    return ""
            # Create the base XML file from the group name
            GroupFQFN=xbmcvfs.translatePath(DATA_DIR)+'/'+fnameraw+'.xml'
            # Verify that the group name entered does not already exist.
            if xbmcvfs.exists(GroupFQFN):
                msg=localize(30122)+"[CR]"
                msg=msg+localize(30109)+"="+fnameraw+"[CR][CR]"+localize(30110)
                if xbmcgui.Dialog().yesno(localize(30121),msg,defaultbutton=xbmcgui.DLG_YESNO_YES_BTN):
                    continue
                else:
                    return ""
            break
    # Group name specified and is valid.
    # Ask ther user if they would like to associate an image with the group.
    GroupThumb=""
    if xbmcgui.Dialog().yesno(localize(30109)+": "+fnameraw,localize(30123),defaultbutton=xbmcgui.DLG_YESNO_YES_BTN):
        # Yes, prompt for an image file to use.
        GroupThumb=xbmcgui.Dialog().browse(2,localize(30124),"",useThumbs=True,defaultt="")

    xmltree=ET.ElementTree(ET.fromstring(XML_BASE))
    xmltree.getroot().set("thumb",GroupThumb)
    xmltree.write(GroupFQFN)
    return fnameraw

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: action to be taken
    "add" - add the selected entry into a SubFavourite group.
    :type paramstring: str
    """
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    if paramstring == 'add':
        # Perform the add context menu action.
        i_label=xbmcgui.Dialog().input(localize(30113),sys.listitem.getLabel())
        if i_label=="":
            # User canceled, display notification and exit without adding.
            xbmcgui.Dialog().notification(localize(30114),localize(30115))
            return False
        folders,files=xbmcvfs.listdir(DATA_DIR)
        tgroup=[localize(30102)]+[item.rsplit(".",1)[0] for item in files if item.endswith(".xml")]
        # Loop requesting to select a group name until the user either selects one or presses cancel.
        while True:
            fnames=xbmcgui.Dialog().multiselect(localize(30103)+" "+i_label,tgroup)
            # Check if the user clicked ok and process the selections
            if fnames is None:
                # User canceled, display notification and exit without adding.
                xbmcgui.Dialog().notification(localize(30114),localize(30115))
                return False
            if len(fnames)==0:
                # User pressed ok without selecting a group. Prompt for a re-selection.
                if xbmcgui.Dialog().yesno(localize(30119),localize(30120),defaultbutton=xbmcgui.DLG_YESNO_YES_BTN):
                    continue
                else:
                    # User canceled, display notification and exit without adding.
                    xbmcgui.Dialog().notification(localize(30114),localize(30115))
                    return False
            # User selected at least one group (or new group).    
            NewElement=CreateElement(i_label)
            for sel in fnames:
                if tgroup[sel]==localize(30102):
                    # Adding a new named group.
                    GroupName=CreateNewGroup()
                    if not GroupName=="":
                        SaveItem(GroupName,NewElement)
                else:
                    SaveItem(tgroup[sel],NewElement)
            # Provide feeback to user once item has been sucessfully added to the group(s)
            xbmcgui.Dialog().notification(localize(30114),i_label+" "+localize(30118))
            break

    else:
        # If the provided paramstring does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError(f'Invalid paramstring: {paramstring}!')

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[1])