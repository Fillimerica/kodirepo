# Favourites Group Addon for Kodi

### Purpose:

This addon allows saving of Kodi elements (addons,folders,media, and endpoints) to a group similar to the built-in favourites feature. The main enhancement is that multiple independent named groups of elements can be created each having a different combination of elements.

### Implementation:

A new global context menu item is added to Kodi, called "Add to FavouriteGroup" which should be present in most of the locations that the "Add to favourites" context menu item is also available.

In many of the customizable skins, new menu options can be added that invoke a specific Favourite Group, or the Group of Groups master list.

New named Favourite Groups can be added or deleted at any time.

Kodi elements can be added to one or more Favourite Group in one operation.

### Installation:

See the installation instructions document: [kodirepo/README.md at master · Fillimerica/kodirepo](https://github.com/Fillimerica/kodirepo/blob/master/README.md)

### Usage:

A new context menu item will be present called "Add to FavouriteGroup" in most areas of Kodi. Navigate to the desired addon, folder, media, or endpoint, bring up the context menu, and select "Add to FavouriteGroup"

![](./assets/2025-11-09-17-16-35-image.png)

The Desired Item Name diolog will be shown with the current item name displayed. Optionally edit the name to reflect the specific content being linked, and choose "Done" to continue. Selecting a completely blank Item Name will cancel the Add to FavouriteGroup operation.

![](./assets/2025-11-09-17-17-01-image.png)

The Group Selection dialog will be displayed. If named Favourites Groups exist, they will be listed along with the special "<NEW GROUP>" group. Select one or more groups to add the item into. Select "<NEW GROUP>" to create a new named Favourites Group. Then Press OK to continue. Selecting CANCEL will will cancel the Add to FavouriteGroup operation.

![](./assets/2025-11-09-17-22-30-image.png)

If "<NEW GROUP>" was chosen, you will be prompted for a group name. Please use characters that are valid for filenames in your operating system. (Limited checks are done to determine if the entered name is valid.)

![](./assets/2025-11-09-17-26-21-image.png)

If the Add to Favourite Group was sucessful, a notification will appear in the upper corner:

![](./assets/2025-11-09-17-29-19-image.png)

### Usage Part 2

Once one or more Favourite Groups have been created, you may access them from either the addon directly or via the url of a specific group.

The most likely place to implement this is in the menu customization feature of a skin.

When run from the Addon menu directly (as can be done with the Estuary Skin), initially all of the Favourite Groups will be listed. Once a specific group is selected, the group items will be displayed. The specific group can be added to the global favorites which will provide direct access. This allows sub-dividing the global favourites into sub-categories.

When working with a skin that allows direct menu customization, a specific Favourite Group can be added directly to the menu or sub-menu.
