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
MyList Favorites Support Module
This module contains the methods and functions to support the creation
and maintenance of the MyList favorites list.
V 1.0 - October 2025
"""
import pickle
import os
from urllib.parse import urlencode, parse_qsl

import xbmc
import xbmcgui
import xbmcplugin

# Import the project constants and globals for use within the module.
from constants import *

# Import the debugger if supported on the system
if IsWebPDB:
    import web_pdb

# Class to hold MyList favorites, which is persisted on disk by the addon
class MyListClass:
    def __init__(self,title='',poster='',isfolder='F',url=''):
        self.title=title
        self.poster=poster
        self.isfolder=isfolder
        self.url=url

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return f'{URL}?{urlencode(kwargs)}'

def list_mylist():
    # Create the list of favorites/mylist items
    # from the MyList.pkl file.

    # Debugging control if supported on the system
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    # Load current list data from the disk cache.
    MyListData=[]
    if os.path.exists(MYLISTFQFN):
        with open(MYLISTFQFN, 'rb') as f:
            MyListData=pickle.load(f)

    ListItemList=[]

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(HANDLE, ADDON_NAME)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(HANDLE, 'movies')

    # Iterate through each entry.
    for row in MyListData:
        t_title=row.title
        SeriesArt=row.poster
        # Create a list item with a text label
        list_item = xbmcgui.ListItem(label=t_title)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        list_item.setArt({'poster': SeriesArt, 'fanart': SeriesArt})
        # Set additional info for the list item via InfoTag.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        info_tag = list_item.getVideoInfoTag()
        info_tag.setMediaType('movie')
        info_tag.setTitle(t_title)
        # Create a URL for a plugin recursive call. **comes from saved data
        # is_folder = True means that this item opens a sub-list of lower level items.
        if row.isfolder=="T":       # decode from saved data.
            is_folder=True
            list_item.setProperty('IsPlayable','false')
        else:
            is_folder=False
            list_item.setProperty('IsPlayable','true')
        list_item.setIsFolder(is_folder)

        # Build a context menu link for this item so it can be added to My List
        cMenuURL=get_url(
            action='delmylist',
            url=row.url
            )
        list_item.addContextMenuItems([ ("Remove from MyList","RunPlugin({})".format(cMenuURL))])

        # ListItemList is for Kodi, SeriesInfoList is for caching of series data.
        ListItemList.append([row.url,list_item,is_folder])

    # Add the items to the Kodi virtual folder listing.
    if len(ListItemList)>0:
        xbmcplugin.addDirectoryItems(HANDLE,ListItemList,len(ListItemList))
        # Add sort methods for the virtual folder items
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)

def addto_mylist(pTitle,pArtwork,pIsFolder,pURL):
    # This routine is called by the context menu invoker and
    # writes a new entry to the MyList.pkl file.

    # Load current list data from the disk cache.
    MyListData=[]
    if os.path.exists(MYLISTFQFN):
        with open(MYLISTFQFN, 'rb') as f:
            MyListData=pickle.load(f)

    # Create a new list item from the data passed to the function.
    MyListItem=MyListClass(pTitle,pArtwork,pIsFolder,pURL)
    MyListData.append(MyListItem)

    # Write out the new list to disk.
    with open(MYLISTFQFN, 'wb') as f:
        pickle.dump(MyListData, f)
    xbmc.executebuiltin('Notification('+ADDON_NAME+', Added Selected Item to My List, 5000)')

def deletefrom_mylist(pURL):
    # This routine is called by the context menu invoker and
    # removes an existing entry from the MyList.pkl file.

    # Load current list data from the disk cache.
    MyListData=[]
    if os.path.exists(MYLISTFQFN):
        with open(MYLISTFQFN, 'rb') as f:
            MyListData=pickle.load(f)

    # Scan through the rows and find the matching entry to delete.
    for row in MyListData:
        if row.url==pURL:
            MyListData.remove(row)
            break

    # Write out the new list to disk.
    with open(MYLISTFQFN, 'wb') as f:
        pickle.dump(MyListData, f)

    # Call list_mylist to refresh the on-screen listing.
    xbmc.executebuiltin("Container.Refresh()")

    xbmc.executebuiltin('Notification('+ADDON_NAME+', Removed Selected Item from My List, 5000)')



