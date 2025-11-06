# Context menu handler for the SubFavourites Plugin
# V1.0 - October 2025

import sys
import xbmcgui
import xbmcvfs
import xml.etree.ElementTree as ET
import re

# Remote debugging module.
#import web_pdb

# Import the project constants and globals for use within the module.
from constants import *

# Base XML string for new group
XML_BASE="""
<favourites>
</favourites>
"""

def CreateElement():
    """
    This function builds the complete xml entry for the current listitem.
    Called once even if multiple xml files will be updated.
    """

    # Define the new element to add
    NewElement=ET.Element('favourite')
    NewElement.tail="\n"    # Inject xml newline formatting for pre-3.9 python
    NewElement.set('name',sys.listitem.getLabel())

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
        
    # Determine the media type and the correct endpoint if not a folder.
    if sys.listitem.isFolder():
        NewElement.text=sys.listitem.getPath()
        NewElement.set('mediatype','folder')
    else:
        # Endpoint. Determine type and get absolute playback path.
        # IsVideo?
        mType=sys.listitem.getVideoInfoTag().getMediaType()
        mPath=sys.listitem.getPath()
        if not mType=="":
            NewElement.text=sys.listitem.getVideoInfoTag().getFilenameAndPath()
            NewElement.set('mediatype',mType)
        elif not sys.listitem.getPictureInfoTag().getResolution()=="":
            # IsPicture?
            mType='picture'
            NewElement.text=':ShowPicture("'+mPath+'")'
            NewElement.set('mediatype',mType)
        elif mPath[0:9]=="addons://":
            # IsAddon?
            mType='addon'
            NewElement.text=':RunAddon("'+mPath.rsplit('/')[-1]+'")'
            NewElement.set('mediatype',mType)
        else:
            # Unknown Type
            mType='unknown'
            NewElement.text=sys.listitem.getPath()
            NewElement.set('mediatype',mType)
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
    
    while True:
        fnameraw=xbmcgui.Dialog().input(localize(30104),defaultt=fnameraw)
        if fnameraw=="":
            msg=localize(30106)
            if xbmcgui.Dialog().yesno(localize(30105),msg,defaultbutton=xbmcgui.DLG_YESNO_NO_BTN):
                return ""
            else:
                continue
        else:
            # User typed something, verify that it is a valid groupname.
            if re.search(lvalidregex,fnameraw):
                msg=localize(30108)+"[CR][CR]"
                msg=msg+localize(30109)+"="+fnameraw+"[CR][CR]"+localize(30110)
                if xbmcgui.Dialog().yesno(localize(30107),msg,defaultbutton=xbmcgui.DLG_YESNO_YES_BTN):
                    continue
                else:
                    return ""
            break
    # Group name specified and is valid.
    # Create the base XML file from the group name
    GroupFQFN=xbmcvfs.translatePath(DATA_DIR)+'/'+fnameraw+'.xml'
    xmltree=ET.ElementTree(ET.fromstring(XML_BASE))
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

    if paramstring == 'add':
        #web_pdb.set_trace()
        # Perform the add context menu action.
        i_label=sys.listitem.getLabel()
        folders,files=xbmcvfs.listdir(DATA_DIR)
        tgroup=[localize(30102)]+[item.rsplit(".",1)[0] for item in files if item.endswith(".xml")]
        fnames=xbmcgui.Dialog().multiselect(localize(30103)+" "+i_label,tgroup)
        # Check if the user clicked ok and process the selections
        if fnames is not None:
            NewElement=CreateElement()
            for sel in fnames:
                if tgroup[sel]==localize(30102):
                    # Adding a new named group.
                    GroupName=CreateNewGroup()
                    if not GroupName=="":
                        SaveItem(GroupName,NewElement)
                else:
                    SaveItem(tgroup[sel],NewElement)
    else:
        # If the provided paramstring does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError(f'Invalid paramstring: {paramstring}!')

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[1])