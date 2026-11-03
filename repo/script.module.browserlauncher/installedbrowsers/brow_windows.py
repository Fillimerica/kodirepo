import os
import pathlib
import platform
from .browsers import instBrowType
try:
    # noinspection PyUnresolvedReferences
    import winreg
except ImportError:     # pragma: no cover
    import_error = "Operating system is not Windows, winreg is not imported."

# dictionary of possible browsers
POSSIBLE_BROWSERS = {
    "Google Chrome": "chrome",
    "Google Chrome Canary": "chrome-canary",
    "Chromium": "chromium",
    "Mozilla Firefox": "firefox",
    "Firefox Developer Edition": "firefox-developer",
    "Firefox Nightly": "firefox-nightly",
    "Opera Stable": "opera-stable",
    "Opera beta": "opera-beta",
    "Opera developer": "opera-developer",
    "Microsoft Edge": "msedge",
    "Microsoft Edge Beta": "msedge-beta",
    "Microsoft Edge Dev": "msedge-dev",
    "Microsoft Edge Canary": "msedge-canary",
    "Brave": "brave",
    "Brave Beta": "brave-beta",
    "Brave Nightly": "brave-nightly",
    "Vivaldi": "vivaldi",
    "Min": "min",
}

# dictionary of possible browser names
POSSIBLE_BROWSER_NAMES = dict(
    (value, key) for key, value in POSSIBLE_BROWSERS.items()
)

# get all installed browsers
def getbrowsers():
    match platform.architecture()[0]:
        case OS.WIN32:    # pragma: no cover
            return _get_unique_browsers(winreg.KEY_WOW64_32KEY)
        case OS.WIN64:
            return _get_unique_browsers(winreg.KEY_WOW64_64KEY)
    return None

# get browsers from registry
def _get_browsers_from_registry(tree: int, access: int):
    instBrowList=[]
    try:
        with winreg.OpenKey(tree, r"Software\Clients\StartMenuInternet", access=access) as hkey:
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(hkey, i)
                    i += 1
                except OSError:
                    break
                try:
                    description = winreg.QueryValue(hkey, subkey)
                    if not description or not isinstance(description, str):  # pragma: no cover
                        description = subkey
                except OSError:  # pragma: no cover
                    description = subkey
                try:
                    cmd = winreg.QueryValue(hkey, rf"{subkey}\shell\open\command")
                    cmd = cmd.strip('"')
                    os.stat(cmd)
                except (OSError, AttributeError, TypeError, ValueError):  # pragma: no cover
                    continue
                instBrowList.append(instBrowType(
                    name=POSSIBLE_BROWSERS.get(description, "unknown"),
                    location=cmd)
                )
    except FileNotFoundError:  # pragma: no cover
        pass
    return instBrowList

# get only unique browsers
def _get_unique_browsers(winreg_key):
    # get browsers from local machine
    browsers_local_machine = _get_browsers_from_registry(winreg.HKEY_LOCAL_MACHINE,
                                                         winreg.KEY_READ | winreg_key)

    # get browsers from current user
    browsers_current_user = _get_browsers_from_registry(winreg.HKEY_CURRENT_USER, winreg.KEY_READ)

    # get browsers available in both places
    instBrowList=[]
    seen=set()
    for brow in (browsers_local_machine + browsers_current_user):
        identical=(brow.name,brow.loc)
        if identical not in seen:
            seen.add(identical)
            instBrowList.append(brow)
    return instBrowList

