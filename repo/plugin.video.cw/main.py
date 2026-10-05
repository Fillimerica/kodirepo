# Copyright (C) 2025-2026, Thomas Filliman
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
CW Network video plugin that is compatible with Kodi 20.x "Nexus" and above
"""
# Import the project constants and globals for use within the module.
from constants import *

import sys
from pathlib import Path
from urllib.parse import urlencode, parse_qsl
import pickle
import time
import os
import datetime as dt
import configparser

# Import the debugger if supported on the system
if IsWebPDB:
    import web_pdb

import subprocess

import xbmcgui
import xbmcplugin
import xbmc

# Import the Selenium Webdriver Subsystem
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

# Import the Mylist support module
import mylist

# Helper function to extract the numeric value from a string after a passed prefix.
import re
def getPrefixValue(prefix,tString):
    # matches digits immediately following a prefix string.
    strNum = re.search(prefix+"(\\d+)",tString)
    if strNum:
        return int(strNum.group(1))
    return -1

# Read the browser settings from the settings.ini file.
def readsettings(section,key):
    Result=None
    SFile=configparser.ConfigParser()
    try:
        SFile.read(ADDON_PATH / 'settings.ini')
        Result=SFile[section][key]
    except configparser.Error as e:
        print(f"Error parsing config file: {e}")
    except FileNotFoundError:
        print("Error: 'settings.ini' not found.")
    except Exception as e:
        print(f"A readsettings error occurred: {e}")
    return Result

BROWSER_TYPE='Firefox'
BROWSER_PROFILE=readsettings('Browser','profile')

# This is the static configuration section for the CW Network
class HomeCat:
    def __init__(self,name='',url='',filename=''):
        self.name=name
        self.url=url
        self.filename=filename

CWTVBase="https://www.cwtv.com"
HomeCategory=[
    HomeCat('Series',CWTVBase+"/series/",'SeriesData.pkl'),
    HomeCat('Movies',CWTVBase+"/movies/",'MoviesData.pkl')]

# Class to hold series data that is cached to disk.
class SeriesInfo:
    def __init__(self,href='',poster='',title='',url=''):
        self.href=href
        self.poster=poster
        self.title=title
        self.url=url

# Class to hold episode data for a series, which is persisted on disk by the addon
class EpList:
    def __init__(self,href='',title='',series='',season='',poster='',info='',plot=''):
        self.href=href
        self.title=title
        self.series=series
        self.season=season
        self.poster=poster
        self.info=info
        self.plot=plot

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


def list_categories():
    """
    Create the list of content categories.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(HANDLE, 'CW Network')
    xbmcplugin.setProperty(HANDLE,'FolderName','CWBase')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(HANDLE, 'videos')
    # This is starting out as a static text list for Series and Movies

    # Debugging control if supported on the system
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    """
    # Testing category to see how content tags are reflected in the UI.
    # Create a list item with a text label.
    list_item = xbmcgui.ListItem(label='Primary Label', label2='Label2', path='Listitem Path')
    # Set images for the list item.
    # Convert Path objects to str because Kodi API accepts only str.
    list_item.setArt({
        'icon': str(ICONS_DIR / 'cwicon2.png'),
        'fanart': str(FANART_DIR / 'comedy.jpg'),
        'thumb': str(FANART_DIR / 'tp1-thumb.png'),
        'banner': str(FANART_DIR / 'tp1-banner.png'),
        'clearart': str(FANART_DIR / 'tp1-clearart.png'),
        'landscape': str(FANART_DIR / 'tp1-landscape.png'),
        'poster': str(FANART_DIR / 'tp1-poster.png'),
        'clearlogo': str(FANART_DIR / 'tp1-clearlogo.png'),
    })
    # Set additional info for the list item using its InfoTag.
    # InfoTag allows to set various information for an item.
    # For available properties and methods see the following link:
    # https://codedocs.xyz/xbmc/xbmc/classXBMCAddon_1_1xbmc_1_1InfoTagVideo.html
    # 'mediatype' is needed for a skin to display info for this ListItem correctly.
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('tvshow')
    info_tag.setTitle('Title InfoTag')
    info_tag.setYear(2000)
    info_tag.setEpisode(18)
    info_tag.setSeason(9)
    info_tag.setEpisodeGuide('EpisodeGuideTag')
    info_tag.setPlot('Plot InfoTag')
    info_tag.setPlotOutline('PlotOutline InfoTag')
    info_tag.setTagLine('TagLine InfoTag')
    info_tag.setTvShowTitle('TvShow InfoTag')
    info_tag.setTvShowStatus('TvShowStatus InfoTag')
    info_tag.setGenres(['Genre1','Genre2 InfoTag'])
    info_tag.setDuration(601)
    info_tag.setTrailer('Trailer InfoTag')
    info_tag.addSeason(6,'Season InfoTag')
    info_tag.setDirectors(['Directors InfoTag'])
    #info_tag.setGenres([genre_info['genre']])
    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=listing&genre_index=0
    url = get_url(action='listing', genre_index=0)
    # is_folder = True means that this item opens a sub-list of lower level items.
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)
    """
    for index in range(len(HomeCategory)):
        # Create a list item with a text label.
        list_item = xbmcgui.ListItem(label=HomeCategory[index].name, offscreen=True)
        # Set images for the list item.
        # Convert Path objects to str because Kodi API accepts only str.
        list_item.setArt({
            'icon': str(ICONS_DIR / 'cwicon2.png'),
            'fanart': str(FANART_DIR / 'comedy.jpg'),
        })
        # Set additional info for the list item using its InfoTag.
        # InfoTag allows to set various information for an item.
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        info_tag = list_item.getVideoInfoTag()
        info_tag.setMediaType('video')
        info_tag.setTitle(HomeCategory[index].name)
        # Example: plugin://plugin.video.example/?action=listing&genre_index=0
        url = get_url(action='listing', cat_index=index)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        list_item.setIsFolder(is_folder)
        list_item.setProperty('IsPlayable','false')
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

    # Add the fixed data entry for the MyList category.
    t_title="My List"
    list_item = xbmcgui.ListItem(label=t_title,offscreen=True)
    # Set images for the list item.
    # Convert Path objects to str because Kodi API accepts only str.
    list_item.setArt({
        'icon': str(ICONS_DIR / 'cwicon2.png'),
        'fanart': str(FANART_DIR / 'comedy.jpg'),
    })
    # Set additional info for the list item using its InfoTag.
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('video')
    info_tag.setTitle(t_title)
    # Example: plugin://plugin.video.example/?action=listing&genre_index=0
    url = get_url(action='listmylist')
    # is_folder = True means that this item opens a sub-list of lower level items.
    is_folder = True
    list_item.setIsFolder(is_folder)
    list_item.setProperty('IsPlayable','false')
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)


def list_series(cat_index):
    """
    Create the list of playable videos in the Kodi interface.

    :param genre_index: the index of genre in the list of show types
    :type genre_index: int
    """
    # Debugging control if supported on the system
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(HANDLE, ADDON_NAME)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(HANDLE, 'movies')

    # See if a recent (today) series cache file exists, and if so use it
    # for the series data rather than quering the website.
    EPFileName=HomeCategory[cat_index].filename
    EPFileFQFN=DATA_DIR / EPFileName
    SeriesInfoCache=False
    if os.path.exists(EPFileFQFN):
        today=dt.datetime.now().date()
        filetime=dt.datetime.fromtimestamp(os.path.getmtime(EPFileFQFN))
        if filetime.date()==today:
            with open(EPFileFQFN, 'rb') as f:
                SeriesInfoList=pickle.load(f)
            SeriesInfoCache=True

    # SeriesInfoCache controls whether SeriesInfoList has been loaded from disk.
    if SeriesInfoCache:
        xbmc.executebuiltin('Notification('+ADDON_NAME+', List Building from Cache, 5000)')
        ListItemList=[]
        # Iterate through each Series.
        for row in SeriesInfoList:
            t_title=row.title
            SeriesArt=row.poster
            # Create a list item with a text label
            list_item = xbmcgui.ListItem(label=t_title,offscreen=True)
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            list_item.setArt({'poster': SeriesArt, 'fanart': SeriesArt})
            # Set additional info for the list item via InfoTag.
            # 'mediatype' is needed for skin to display info for this ListItem correctly.
            info_tag = list_item.getVideoInfoTag()
            info_tag.setMediaType('video')
            info_tag.setTitle(t_title)
            # Create a URL for a plugin recursive call.
            url = get_url(action='season', series=row.href, cat_index=cat_index)
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = True
            list_item.setIsFolder(is_folder)
            list_item.setProperty('IsPlayable','false')

            # Build a context menu link for this item so it can be added to My List
            cMenuURL=get_url(
                action='addmylist',
                title=list_item.getLabel(),
                artwork=list_item.getArt('poster'),
                isfolder="T" if is_folder else "F",
                url=row.url
                )
            list_item.addContextMenuItems([ ("Add to MyList","RunPlugin({})".format(cMenuURL))])
            # ListItemList is for Kodi, SeriesInfoList is for caching of series data.
            ListItemList.append([row.url,list_item,is_folder])
    else:
        xbmc.executebuiltin('Notification('+ADDON_NAME+', Retrieving Series List from Website, 5000)')
        # Fire up Selenium and load the headless website for information scraping.
        gdpath=ADDON_PATH / 'geckodriver.exe'
        gdlogpath=ADDON_PATH / 'geckodriver.log'
        options=Options()
        options.add_argument("--headless")
        options.add_argument("-profile")
        options.add_argument(BROWSER_PROFILE)
        FFService=Service(executable_path=gdpath, log_path=gdlogpath)
        driver = webdriver.Firefox(service=FFService,options=options)
        driver.implicitly_wait(10)
        driver.get(HomeCategory[cat_index].url)

        # Testing using a hard pause to allow time for the website to load.
        time.sleep(2)

        # Get the full list of potential show objects.
        xbmc.executebuiltin('Notification('+ADDON_NAME+', Web Data Processing, 5000)')
        SHOWListRaw= driver.find_elements(By.CLASS_NAME, "swimlane-content")
        xbmc.executebuiltin('Notification('+ADDON_NAME+', Web Data Filtering, 5000)')
        SeriesListDup=[item for item in SHOWListRaw if item.get_property('href').startswith(HomeCategory[cat_index].url)]
        xbmc.executebuiltin('Notification('+ADDON_NAME+', Dupe Removal, 5000)')
        SeriesListIndex=[]
        for index in range(len(SeriesListDup)):
            thref=SeriesListDup[index].get_property('href')
            if not any(thref in row for row in SeriesListIndex):
                SeriesListIndex.append([thref,index])

        xbmc.executebuiltin('Notification('+ADDON_NAME+', List Building, 5000)')
        ListItemList=[]
        SeriesInfoList=[]
        # Iterate through each Series.
        for row in SeriesListIndex:
            t_title=SeriesListDup[row[1]].get_property('title')
            SeriesArt=SeriesListDup[row[1]].find_element(By.CSS_SELECTOR,"img").get_dom_attribute("data-src")
            # Create a list item with a text label
            list_item = xbmcgui.ListItem(label=t_title,offscreen=True)
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            list_item.setArt({'poster': SeriesArt, 'fanart': SeriesArt})
            # Set additional info for the list item via InfoTag.
            # 'mediatype' is needed for skin to display info for this ListItem correctly.
            info_tag = list_item.getVideoInfoTag()
            info_tag.setMediaType('video')
            info_tag.setTitle(t_title)
            # Create a URL for a plugin recursive call.
            url = get_url(action='season', series=row[0], cat_index=cat_index)
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = True
            list_item.setIsFolder(is_folder)
            list_item.setProperty('IsPlayable','false')

            # Build a context menu link for this item so it can be added to My List
            cMenuURL=get_url(
                action='addmylist',
                title=list_item.getLabel(),
                artwork=list_item.getArt('poster'),
                isfolder="T" if is_folder else "F",
                url=url
                )
            list_item.addContextMenuItems([ ("Add to MyList","RunPlugin({})".format(cMenuURL))])
            # ListItemList is for Kodi, SeriesInfoList is for caching of series data.
            ListItemList.append([url,list_item,is_folder])
            SeriesInfoList.append(SeriesInfo(href=row[0],poster=SeriesArt,title=t_title,url=url))

        # Shut down the headless browser instance.
        driver.quit()

        # Save the ListItemList for future re-use.
        with open(EPFileFQFN, 'wb') as f:
            pickle.dump(SeriesInfoList, f)

    #xbmc.executebuiltin('Notification('+ADDON_NAME+', List Building Part 2, 5000)')
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItems(HANDLE,ListItemList,len(ListItemList))
    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    #xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)

def list_seasons(series_url,cat_index):
    """
    Create the list of playable videos and store on disk.
    Calculate if the series is broken up by season and create a category
    for each season the series has.

    If the series has only a few episodes or only has one season,
    forward the request to the list episodes routine directly.

    :param series_url: url of the main series page on the website.
    """
    # Debugging control if supported on the system
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    xbmc.executebuiltin('Notification('+ADDON_NAME+', Retrieving Series Data from Website, 5000)')
    # Fire up Selenium and load the headless website for information scraping.
    gdpath=ADDON_PATH / 'geckodriver.exe'
    gdlogpath=ADDON_PATH / 'geckodriver.log'
    options=Options()
    options.add_argument("--headless")
    options.add_argument("-profile")
    options.add_argument(BROWSER_PROFILE)
    FFService=Service(executable_path=gdpath, log_path=gdlogpath)
    driver = webdriver.Firefox(service=FFService,options=options)
    driver.implicitly_wait(10)
    driver.get(series_url)

    # Get the full list of episodes within the series.
    Season_Max=0
    episodelist=[]
    episodes=driver.find_elements(By.CLASS_NAME,"videoLink")
    xbmc.executebuiltin('Notification('+ADDON_NAME+', Extracting Episode Info., 5000)')
    for episode in episodes:
        # TF 04/2026 Added filter on data-type and a sanity check on data-season to prevent clip
        # and promotional links from being added to the full episode list.
        if episode.get_dom_attribute('data-type')=='full':
            EpListItem=EpList() # Create a new instance of the object for each item to be stored in the list.
            EpListItem.href=episode.get_property('href')
            EpListItem.series=episode.get_dom_attribute('data-seriestitle')
            EpListItem.title=episode.get_dom_attribute('data-eptitle')
            EpListItem.season=episode.get_dom_attribute('data-season')
            EpListItem.poster=episode.find_element(By.CSS_SELECTOR,"img").get_dom_attribute("data-src")
            EpListItem.info=episode.find_element(By.CLASS_NAME,"videoinfo").get_property("textContent")
            EpListItem.plot=episode.find_element(By.CLASS_NAME,"vdesc").get_property("textContent")
            # Add the completed object to the episodes list.
            episodelist.append(EpListItem)
            # Keep track of seasons recorded.
            # Added sanity-check for empty season value
            if EpListItem.season:
                if Season_Max<int(EpListItem.season):
                    Season_Max=int(EpListItem.season)
            else:
                 xbmc.executebuiltin('Notification('+ADDON_NAME+', WARNING SEASON DATA MISSING, 5000)')


    # Make sure at least 1 episode was found. (failsafe)
    if Season_Max>0:
        # Retain series name for use with season markers
        SeriesTitle=EpListItem.series

        # Write the episode list to disk, using the series name as the filename.
        EPFileName=validfilename(SeriesTitle)+'.pkl'
        EPFileFQFN=DATA_DIR / EPFileName
        with open(EPFileFQFN, 'wb') as f:
            pickle.dump(episodelist, f)

        # Done with selenium for now, close the session.
        driver.quit()

        # If series is only 1 season, transfer to list_episodes,
        # otherwise build a semi-static Season ## list.
        if Season_Max==1:
            list_episodes('1',EPFileName)
        else:
            # Retrieve the master series or movies list and locate the List_item Art tag.
            # Note this will fail for the movie category right now. TODO
            SRFileName=HomeCategory[cat_index].filename
            SRFileFQFN=DATA_DIR / SRFileName
            with open(SRFileFQFN, 'rb') as f:
                SeriesInfoList=pickle.load(f)
            ArtPoster=''
            for index in range(len(SeriesInfoList)):
                if SeriesInfoList[index].href==series_url:
                    ArtPoster=SeriesInfoList[index].poster
                    break

            # Set plugin category. It is displayed in some skins as the name
            # of the current section.
            xbmcplugin.setPluginCategory(HANDLE, ('Series: '+SeriesTitle))
            # Set plugin content. It allows Kodi to select appropriate views
            # for this type of content.
            xbmcplugin.setContent(HANDLE, 'seasons')
            # Iterate through each Season.
            for index in range(Season_Max):
                SeasonText= f"{SeriesTitle} - Season {(index+1)}"
                # Create a list item with a text label
                list_item = xbmcgui.ListItem(label=SeasonText,offscreen=True)
                # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
                list_item.setArt({'poster': ArtPoster, 'fanart': ArtPoster})
                # Set additional info for the list item via InfoTag.
                # 'mediatype' is needed for skin to display info for this ListItem correctly.
                info_tag = list_item.getVideoInfoTag()
                info_tag.setMediaType('season')
                info_tag.setTitle(SeasonText)
                # Create a URL for a plugin recursive call.
                url = get_url(action='episodes', season=str(index+1), EPFile=EPFileName)
                # is_folder = True means that this item opens a sub-list of lower level items.
                is_folder = True
                list_item.setIsFolder(is_folder)
                list_item.setProperty('IsPlayable','false')

                # Build a context menu link for this item so it can be added to My List
                cMenuURL=get_url(
                    action='addmylist',
                    title=list_item.getLabel(),
                    artwork=list_item.getArt('poster'),
                    isfolder="T" if is_folder else "F",
                    url=url
                    )
                list_item.addContextMenuItems([ ("Add to MyList","RunPlugin({})".format(cMenuURL))])

                # Add our item to the Kodi virtual folder listing.
                xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)
            # Add sort methods for the virtual folder items
            xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)

            # Finish creating a virtual folder.
            xbmcplugin.endOfDirectory(HANDLE)
    else:
        xbmc.executebuiltin('Notification('+ADDON_NAME+', No Episodes Found for Series, 15000,DefaultIconError.png)')

def list_episodes(pseason,EPFileName):
    """
    Create the list of playable videos in the Kodi interface.

    :param
    pseason, season # (text),
    epfilename is episode file name from list_seasons
    """
    # Debugging control if supported on the system
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    EpList=[]

    # Restore the episode list from the disk
    EPFileFQFN=DATA_DIR / EPFileName
    with open(EPFileFQFN, 'rb') as f:
        EpList=pickle.load(f)

    # Derive a title from the 1st episode data.
    SeasonTitle=EpList[0].series+ f" Season: {pseason}"

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(HANDLE, SeasonTitle)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(HANDLE, 'episodes')
    # Iterate through each Series.
    for episode in EpList:
        # Only include episode if season matches
        if episode.season==pseason:
            # Series have their episode # encoded within episode.info, decode it if possible
            # otherwise use a default of 0.
            EpisodeNum=0
            InfoSeason=getPrefixValue("S",episode.info)
            if InfoSeason>0:
                InfoEpisode=getPrefixValue("E",episode.info)
                if InfoEpisode>0:
                    EpisodeNum=InfoEpisode
            # Create a list item with a text label
            list_item = xbmcgui.ListItem(label=episode.title,offscreen=True)
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            list_item.setArt({
                'icon': str(ICONS_DIR / 'cwicon2.png'),
                'fanart': str(FANART_DIR / 'comedy.jpg'),
                'thumb': episode.poster,
                'banner': str(FANART_DIR / 'tp1-banner.png'),
                'poster': episode.poster,
            })
            # Set additional info for the list item via InfoTag.
            # 'mediatype' is needed for skin to display info for this ListItem correctly.
            info_tag = list_item.getVideoInfoTag()
            info_tag.setMediaType('episode')
            info_tag.setTitle(episode.title)
            info_tag.setSeason(int(episode.season))
            info_tag.setPlot(episode.plot)
            info_tag.setGenres([episode.info])
            info_tag.setDirectors([episode.info])
            info_tag.setEpisode(EpisodeNum)
            # Set 'IsPlayable' property to 'true'.
            # Create a URL for a plugin recursive call.
            url = get_url(action='play', video=episode.href)
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = False
            list_item.setIsFolder(is_folder)
            list_item.setProperty('IsPlayable','true')

            # Build a context menu link for this item so it can be added to My List
            cMenuURL=get_url(
                action='addmylist',
                title=list_item.getLabel(),
                artwork=list_item.getArt('poster'),
                isfolder="T" if is_folder else "F",
                url=url
                )
            list_item.addContextMenuItems([ ("Add to MyList","RunPlugin({})".format(cMenuURL))])

            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

    # Add sort methods for the virtual folder items
    #xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)


def play_video(video_url):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    Issue: For Kodi, https:// resolves to an internet protocol type and doesn't allow
    matching oin the suffix. Solution is to strip the https:// prefix off if it is present
    and allow the webplayer to preped it if it is missing.
    """
    # Debugging control if supported on the system
    if IsWebPDB:
        pass # needed in case the trace line is commented out
        #web_pdb.set_trace()

    play_item = xbmcgui.ListItem(offscreen=True)
    # The .CW suffix causes Kodi to invoke the custom webplayer to play the content.
    if video_url.startswith('https://'):
        custom_url=video_url[8:]+".CW"
    else:
        custom_url=video_url+".CW"
    play_item.setPath(custom_url)
    xbmcplugin.setResolvedUrl(HANDLE, True , listitem=play_item)

    #playitem='System.ExecWait('+path+')'
    #xbmc.executebuiltin(playitem)
    # # Create a playable item with a path to play.
    # # offscreen=True means that the list item is not meant for displaying,
    # # only to pass info to the Kodi player
    # play_item = xbmcgui.ListItem(offscreen=True)
    # play_item.setPath(path)
    # # Pass the item to the Kodi player.
    #xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)
    #xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=False)

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """

    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if not params:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()
    elif params['action'] == 'listing':
        # Display the list of videos in a provided category.
        list_series(int(params['cat_index']))
    elif params['action'] == 'season':
        # Generate a list of seasons in the series.
        list_seasons(params['series'],int(params['cat_index']))
    elif params['action'] == 'episodes':
        # Generate a list of seasons in the series.
        list_episodes(params['season'],params['EPFile'])
    elif params['action'] == 'play':
        # Play a video from a provided URL.
        play_video(params['video'])

# These actions support the MyList favorites feature.
    elif params['action'] == 'addmylist':
        # Add a new entry to MyList favorites.
        mylist.addto_mylist(params['title'],params['artwork'],params['isfolder'],params['url'])
    elif params['action'] == 'delmylist':
        # Add a new entry to MyList favorites.
        mylist.deletefrom_mylist(params['url'])
    elif params['action'] == 'listmylist':
        # Add a new entry to MyList favorites.
        mylist.list_mylist()

    else:
        # If the provided paramstring does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError(f'Invalid paramstring: {paramstring}!')

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
