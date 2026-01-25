# Copyright (C) 2025, Thomas Filliman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Hard-coded start of a custom favorites plugin.
Initial version reads from a fixed file name called streaming.xml

Future plans are to make this configurable if the proof of concept 
works out.
"""
import sys
import os
from pathlib import Path
from urllib.parse import urlencode, parse_qsl
import xml.etree.ElementTree as ET

import xbmcgui
import xbmcvfs
import xbmcplugin

# Import the project constants and globals for use within the module.
from constants import *

# These "constants" must be defined in this module rather than 
# within constants because the arguments passed will be different
# depending on whether the call is for the plugin, script, or context menu.
# Get the plugin url in plugin:// notation.
URL = sys.argv[0]
# Get a plugin handle as an integer number.
HANDLE = int(sys.argv[1])

def validfilename(genstring):
    return "".join(x for x in genstring if x.isalnum())

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return f'{URL}?{urlencode(kwargs)}'

def list_root():
    """
    Called when setting up the plugin (typically from a skin menu)
    Returns a virtual directory that lists the available Group xml files 
    from the addon data folder.
    """
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    folders,files=xbmcvfs.listdir(DATA_DIR)
    tgroup=[item.rsplit(".",1)[0] for item in files if item.endswith(".xml")]
    if len(tgroup)>0:
        # Set plugin category. It is displayed in some skins as the name
        # of the current section.
        xbmcplugin.setPluginCategory(HANDLE, ADDON_NAME)
        xbmcplugin.setProperty(HANDLE,'FolderName','Root')
        xbmcplugin.setContent(HANDLE, 'video')
        for row in tgroup:
            # Create a list item with a text label
            list_item = xbmcgui.ListItem(label=row,offscreen=True)

            # Open and read the group root tag.
            GroupFQFN=DATA_DIR+'/'+row+'.xml'
            xmltree=ET.parse(GroupFQFN)
            xmlroot=xmltree.getroot()
            # Verify the root tag is valid.
            if not xmlroot.tag=='favourites':
                raise ValueError(localize(30111)+f' {xmlroot.tag}!')
                return -1
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            t_Art=xmlroot.get('thumb')
            if not t_Art=="":
                list_item.setArt({'thumb': t_Art, 'icon': t_Art})
            t_Art=xmlroot.get('poster')
            if not t_Art=="":
                list_item.setArt({'poster': t_Art, 'fanart': t_Art})

            url = get_url(action='groupsel', data=row)
            is_folder=True

            # Build a context menu link for this group.
            # Allow removal of the entire group.
            cMenuURLDel=get_url(
                action='groupdel', 
                data=row
                )
            # Build a context menu link for this group.
            # Allow rename of the group.
            cMenuURLRen=get_url(
                action='groupren', 
                data=row
                )
            # Allow setting/changing the image associated with this group.
            cMenuURLImage=get_url(
                action='groupimage', 
                data=row
                )
            list_item.addContextMenuItems([
            (localize(30208),"RunPlugin({})".format(cMenuURLImage)),
            (localize(30304),"RunPlugin({})".format(cMenuURLRen)),
            (localize(30201),"RunPlugin({})".format(cMenuURLDel))
            ])

            list_item.setProperty('IsPlayable','false')
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)
    else:
        xbmcgui.Dialog().ok('GroupFavorites Error',localize(30200))
        return

    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)

def groupsel(groupname):
    """
    Load the selected group and build the virtual folder.
    """
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(HANDLE, "Favorites Group: "+groupname)
    #xbmcplugin.setProperty(HANDLE,'FolderName','Root')
    xbmcplugin.setContent(HANDLE, 'favorites')
 
    # Open and read the desired list of media/plugin objects.
    GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
    xmltree=ET.parse(GroupFQFN)
    xmlroot=xmltree.getroot()
    # Verify the root tag is valid.
    if not xmlroot.tag=='favourites':
        raise ValueError(localize(30111)+f' {xmlroot.tag}!')
        return -1

    # Read each child node and build the Kodi Directory from it.
    NumItems=len(xmlroot)
    for index,row in enumerate(xmlroot):
        t_title=row.get('name')
        # Create a list item with a text label
        list_item = xbmcgui.ListItem(label=t_title,offscreen=True)

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        art = {}
        t_Art=row.get('thumb')
        if not t_Art=="":
            art['thumb'] = t_Art
            art['icon'] = t_Art
            art['fanart'] = t_Art
           # list_item.setArt({'thumb': t_Art, 'icon': t_Art})
        t_Art=row.get('poster')
        if not t_Art=="":
            art['poster'] = t_Art
            art['fanart'] = t_Art
            #list_item.setArt({'poster': t_Art, 'fanart': t_Art})
        list_item.setArt(art)
        list_item.setProperty('IsPlayable', 'true')
        # Set additional info for the list item via InfoTag.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        # info_tag = list_item.getVideoInfoTag()
        # info_tag.setMediaType('video')
        # info_tag.setTitle(t_title)
        # is_folder = True means that this item opens a sub-list of lower level items.
        # In this implementation, all entries are endpoints and the url command handles the item.
        # so all entries are set to isFolder=False right now.
        #if row.get('isFolder')=='False':
        if True:
            is_folder=False
            list_item.setProperty('IsPlayable','true')
        else:
            is_folder=True
            list_item.setProperty('IsPlayable','false')

        # Create the URL for the item. If the 1st character is a colon, must use a Kodi
        # builtin function to "play" the media item.
        if row.text[0:1]==':':
            url = get_url(action='invoke', data=row.text[1:])
            list_item.setProperty('IsPlayable','false')
        else:
            url=row.text
            
        # Build the context menu for items in the group.
        cMenuItems=[]
        # Section 1: Move Up, Move Down (if >1 total elements are in the list)
        if NumItems>1:
            # Build a context menu link for this item so it can be Moved Up in the group.
            if index>0: # Only if not already at the top
                cMenuURL=get_url(
                    action='itemmoveup', 
                    itemname=row.text,
                    itemindex=index,
                    groupname=groupname
                    )
                cMenuItems.append((localize(30125),"RunPlugin({})".format(cMenuURL)))

            # Build a context menu link for this item so it can be Moved Down in the group.
            if index<(NumItems-1):
                cMenuURL=get_url(
                    action='itemmovedown', 
                    itemname=row.text,
                    itemindex=index,
                    groupname=groupname
                    )
                cMenuItems.append((localize(30126),"RunPlugin({})".format(cMenuURL)))

        # Build a context menu link for this item so it's thumnail/image can be changed in the group.
        cMenuURL=get_url(
            action='itemthumb', 
            itemname=row.text,
            itemindex=index,
            groupname=groupname
            )
        cMenuItems.append((localize(30127),"RunPlugin({})".format(cMenuURL)))

        # Build a context menu link for this item so it can be renamed in the group.
        cMenuURL=get_url(
            action='itemrename', 
            itemname=row.text,
            itemindex=index,
            groupname=groupname
            )
        cMenuItems.append((localize(30112),"RunPlugin({})".format(cMenuURL)))

        # Build a context menu link for this item so it can be removed from the group.
        cMenuURL=get_url(
            action='itemdel', 
            itemname=row.text,
            itemindex=index,
            groupname=groupname
            )
        cMenuItems.append((localize(30101),"RunPlugin({})".format(cMenuURL)))

        list_item.addContextMenuItems(cMenuItems)

        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)

def GroupImage(groupname):
    """
    This function allows setting or changing the image associated with the group.
    A confirmation dialog is shown prior to a change being saved.
    """
    # Check setting to see if operation is permitted
    if not AddonSettings.getBool('allow_imagegroup'):
        xbmcgui.Dialog().ok(localize(30208),localize(30231))
        return False
    GroupThumb=xbmcgui.Dialog().browse(2,localize(30124),"",useThumbs=True,defaultt=":Cancel")
    if GroupThumb==":Cancel":   # User selected cancel from the dialog.
        # User canceled, display notification and exit.
        xbmcgui.Dialog().notification(localize(30209),localize(30210))
        return False
    # Update the thumb key in the group xml file.
    GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
    xmltree=ET.parse(GroupFQFN)
    xmlroot=xmltree.getroot()
    # Verify the root tag is valid.
    if not xmlroot.tag=='favourites':
        raise ValueError(localize(30111)+f' {xmlroot.tag}!')
        return -1
    xmlroot.set("thumb",GroupThumb)
    xmltree.write(GroupFQFN)

    # Call group load function to rebuild the kodi listing.
    list_root()

    # Tell Kodi to refresh the virtual directory container after it has been rebuilt.
    xbmc.executebuiltin('Container.Refresh')
    return True

def DeleteGroup(groupname):
    """
    This function deletes an entire group including the xml file.
    A confirmation dialog is shown prior to deletion.
    """
    # Check setting to see if operation is permitted
    if not AddonSettings.getBool('allow_deletegroup'):
        xbmcgui.Dialog().ok(localize(30202),localize(30230))
        return False
    msg=localize(30109)+"="+groupname+"[CR][CR]"+localize(30203)
    if xbmcgui.Dialog().yesno(localize(30202),msg,defaultbutton=xbmcgui.DLG_YESNO_NO_BTN):
        # Erase the entire group.
        # Create the base XML file from the group name
        GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
        os.remove(GroupFQFN)
        # Call group load function to rebuild the kodi listing.
        list_root()

        # Tell Kodi to refresh the virtual directory container after it has been rebuilt.
        xbmc.executebuiltin('Container.Refresh')
        return True
    return False

def RenameGroup(groupname):
    """
    This function renames the group.
    The user is prompted for a new item name to use.
    """

    # Prompt the user for the new group name.
    i_label=xbmcgui.Dialog().input(localize(30113),groupname)
    if i_label=="":
        # User canceled, display notification and exit without renaming.
        xbmcgui.Dialog().notification(localize(30116),localize(30117))
        return -2
    else:
        newname = i_label

    GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
    NewFQFN=DATA_DIR+'/'+newname+'.xml'
    os.rename(GroupFQFN, NewFQFN)
    # Call group load function to rebuild the kodi listing.
    list_root()

    # Tell Kodi to refresh the virtual directory container after it has been rebuilt.
    xbmc.executebuiltin('Container.Refresh')
    return True
    
def ItemImage(groupname,itemname,itemindex):
    """
    This function allows setting or changing the image associated with selected item..
    A confirmation dialog is shown prior to a change being saved.
    """

    # Check setting to see if operation is permitted
    if not AddonSettings.getBool('allow_imageitem'):
        xbmcgui.Dialog().ok(localize(30127),localize(30136))
        return False
    ItemThumb=xbmcgui.Dialog().browse(2,localize(30128),"",useThumbs=True,defaultt=":Cancel")
    if ItemThumb==":Cancel":   # User selected cancel from the dialog.
        # User canceled, display notification and exit.
        xbmcgui.Dialog().notification(localize(30212),localize(30210))
        return False
    # Update the thumb key in the group xml file.
    GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
    xmltree=ET.parse(GroupFQFN)
    xmlroot=xmltree.getroot()
    # Verify the root tag is valid.
    if not xmlroot.tag=='favourites':
        raise ValueError(localize(30111)+f' {xmlroot.tag}!')
        return -1
    for index,row in enumerate(xmlroot.findall('favourite')):
        if (row.text==itemname) and (index==int(itemindex)):
            # Matching item located, update the item thumbnail.
            row.set("thumb",ItemThumb)
            break
    else:
        raise ValueError(localize(30213))
        return -1

    # Item sucessfully removed from the tree, write out the modified group xml.
    xmltree.write(GroupFQFN)
    
    # Call group load function to rebuild the kodi listing.
    groupsel(groupname)
    
    # Tell Kodi to refresh the virtual directory container after it has been rebuilt.
    xbmc.executebuiltin('Container.Refresh')
    return True

def RenameItem(groupname,itemname,itemindex):
    """
    This function renames the listitem from in the current group.
    The user is prompted for a new item name to use.
    """
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    # Check setting to see if operation is permitted
    if not AddonSettings.getBool('allow_renameitem'):
        xbmcgui.Dialog().ok(localize(30112),localize(30133))
        return False
    # Open and read the current group.
    GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
    xmltree=ET.parse(GroupFQFN)
    xmlroot=xmltree.getroot()
    # Verify the root tag is valid.
    if not xmlroot.tag=='favourites':
        raise ValueError(localize(30111)+f' {xmlroot.tag}!')
        return -1
    for index,row in enumerate(xmlroot.findall('favourite')):
        if (row.text==itemname) and (index==int(itemindex)):
            # Matching item located, prompt the user for the new item name.
            i_label=xbmcgui.Dialog().input(localize(30113),row.get('name'))
            if i_label=="":
                # User canceled, display notification and exit without renaming.
                xbmcgui.Dialog().notification(localize(30116),localize(30117))
                return -2
            else:
                # Update the name key in the current row.
                row.set('name',i_label)
                break
    else:
        raise ValueError(localize(30213))
        return -1

    # Item sucessfully removed from the tree, write out the modified group xml.
    xmltree.write(GroupFQFN)
    
    # Call group load function to rebuild the kodi listing.
    groupsel(groupname)
    
    # Tell Kodi to refresh the virtual directory container after it has been rebuilt.
    xbmc.executebuiltin('Container.Refresh')
            
    return True

def DeleteItem(groupname,itemname,itemindex):
    """
    This function deletes the selected listitem from the current group.
    A confirmation dialog is shown prior to deletion.
    """
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    # Check setting to see if operation is permitted
    if not AddonSettings.getBool('allow_deleteitem'):
        xbmcgui.Dialog().ok(localize(30204),localize(30232))
        return False
    # Open and read the current group.
    GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
    xmltree=ET.parse(GroupFQFN)
    xmlroot=xmltree.getroot()
    # Verify the root tag is valid.
    if not xmlroot.tag=='favourites':
        raise ValueError(localize(30111)+f' {xmlroot.tag}!')
        return -1
    for index,row in enumerate(xmlroot.findall('favourite')):
        if (row.text==itemname) and (index==int(itemindex)):
            # Matching item located, confirm with user that this item should be deleted.
            msg=localize(30109)+"="+groupname+"[CR]"+localize(30205)+"="+row.get('name')+"[CR][CR]"
            msg=msg+localize(30206)
            if xbmcgui.Dialog().yesno(localize(30204),msg,defaultbutton=xbmcgui.DLG_YESNO_NO_BTN):
                xmlroot.remove(row)
            break
    else:
        raise ValueError(localize(30207))
        return -1

    # Item sucessfully removed from the tree, write out the modified group xml.
    xmltree.write(GroupFQFN)
    
    # Call group load function to rebuild the kodi listing.
    groupsel(groupname)
    
    # Tell Kodi to refresh the virtual directory container after it has been rebuilt.
    xbmc.executebuiltin('Container.Refresh')
            
    return True

def MoveItem(groupname,itemname,itemindex,direction):
    """
    This function deletes the selected listitem from the current group.
    A confirmation dialog is shown prior to deletion.
    """
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    # Check setting to see if operation is permitted
    if not AddonSettings.getBool('allow_moveitem'):
        xbmcgui.Dialog().ok(localize(30134),localize(30135))
        return False
    # Open and read the current group.
    GroupFQFN=DATA_DIR+'/'+groupname+'.xml'
    xmltree=ET.parse(GroupFQFN)
    xmlroot=xmltree.getroot()
    # Verify the root tag is valid.
    if not xmlroot.tag=='favourites':
        raise ValueError(localize(30111)+f' {xmlroot.tag}!')
        return -1
    for index,row in enumerate(xmlroot.findall('favourite')):
        if (row.text==itemname) and (index==int(itemindex)):
            xmlroot.remove(row)
            xmlroot.insert((index+direction),row)
            break
    else:
        raise ValueError(localize(30213))
        return -1

    # Item sucessfully removed from the tree, write out the modified group xml.
    xmltree.write(GroupFQFN)
    
    # Call group load function to rebuild the kodi listing.
    groupsel(groupname)
    
    # Tell Kodi to refresh the virtual directory container after it has been rebuilt.
    xbmc.executebuiltin('Container.Refresh')
            
    return True

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """

    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if not params:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of Groups
        list_root()
    elif params.get('action') == 'invoke':
        # Try to run the embedded command.
        xbmc.executebuiltin(params['data'])

    elif params.get('action') == 'groupsel':
        # Open the selected group and populate the virtual directory.
        groupsel(params['data'])

    elif params.get('action') == 'groupimage':
        # Change the image associated with the group.
        GroupImage(params['data'])

    elif params.get('action') == 'groupdel':
        # Delete the entire group.
        DeleteGroup(params['data'])

    elif params.get('action') == 'groupren':
        # Delete the entire group.
        RenameGroup(params['data'])

    elif params.get('action') == 'itemmoveup':
        # Move the selected item up in the group.
        MoveItem(params['groupname'],params['itemname'],params['itemindex'],-1)

    elif params.get('action') == 'itemmovedown':
        # Move the selected item up in the group.
        MoveItem(params['groupname'],params['itemname'],params['itemindex'],1)

    elif params.get('action') == 'itemthumb':
        # Rename the selected item in the group.
        ItemImage(params['groupname'],params['itemname'],params['itemindex'])

    elif params.get('action') == 'itemrename':
        # Rename the selected item in the group.
        RenameItem(params['groupname'],params['itemname'],params['itemindex'])

    elif params.get('action') == 'itemdel':
        # Remove the selected item from the group it is in.
        DeleteItem(params['groupname'],params['itemname'],params['itemindex'])

    elif not (params.get('content_type') == None):
        # Default in some skins when called from a content screen.
        list_root()

    else:
        # If the provided paramstring does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError(f'Invalid paramstring: {paramstring}!')

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
