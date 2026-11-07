#!/bin/sh

# List of common Linux web browser binaries to check on the host
# Format of each entry is filename : browser type code : Description (used in dialogs)
BROWSERS="
google-chrome:chrome:Chrome
google-chrome-stable:chrome:Chrome Stable
firefox:firefox:Firefox
firefox-esr:firefox:Firefox ESR
chromium:chrome:Chromium
chromium-browser:chrome:Chromium
msedge:edge:Edge
brave-browser:brave:Brave
opera:opera:Opera
vivaldi-stable:vivaldi:Vivaldi
librewolf:librewolf:Librewolf
epiphany:epiphany:Epiphany
midori:midori:Midori
"

FOUND_ANY=0
old_Ifs=$IFS

while IFS= read -r browser; do
    # Skip blank lines
    [ -z "$browser" ] && continue

    # Parse the line into elements using a colon IFS
    IFS=":"
    read -r filename name description <<EOF
$browser
EOF
    # Restore IFS immediately for safety
    IFS=$old_ifs

    # Using 'command -v' ensures it checks the host's actual environment PATH
    EXEC_PATH=$(command -v "$filename" 2>/dev/null)
    
    if [ -n "$EXEC_PATH" ]; then
        # Output clean text that Kodi's Python layer can easily parse
        printf "%s:%s:%s\n" "$name" "$EXEC_PATH" "$description"
        FOUND_ANY=1
    fi
done <<EOF
$BROWSERS
EOF

if [ "$FOUND_ANY" -eq 0 ]; then
    exit 1
fi

