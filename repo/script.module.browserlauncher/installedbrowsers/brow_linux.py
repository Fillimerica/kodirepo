# Moved to a flatpak compliant semi-universal browser discovery method.
# uses an external bash script to discover and pass back.
# The external script holds the possible browser names installed on the system.

import os
import subprocess
from .browsers import instBrowType

# Determine the path to the shell script and make sure it is executable.
modulePath=os.path.dirname(os.path.abspath(__file__))
scriptFQFN=os.path.join(modulePath,"flatpak_browsers.sh")
os.chmod(scriptFQFN, 0o755)

# Determine the proper command line to run based upon flatpak sandbox status.
if os.path.isfile("/.flatpak-info"):
    cmd=["flatpak-spawn","--host", scriptFQFN]
else:
    cmd=[scriptFQFN]

def getBrowsers():
    browserList=[]
    # Run the external command and return the result.
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        for line in result.stdout.strip().split("\n"):
            brow=line.split(":")
            browserList.append(instBrowType(*brow))
    except Exception as e:
        pass
    return browserList

