# Responsible for initialising/re-initialising the settings file.
# Set your default values here rather then in the config file itself to avoid
# problems if it accidentally corrupts.

from trapdoor import Trapdoor

t = Trapdoor("main", ".\\configs", "mainConfig.toml")
t.set("camSettings.enabledPallets", ["White Hot", "Black Hot", "Ironbow", 
"Rainbow", "Night", "Aurora", "Red Hot", "Jungle", "Medical", "Golden Red"]) 
# List of strings. Note that if you put in a value here that isn't in the 
# UARTControllers command variable for pallets then it *will* crash.

t.set("camSettings.enabledModes", ["General", "Outline", 
"Low Temperature Highlight", "Linear Stretch", "High Contrast", "Low Contrast"]) 
# List of strings. Note that if you put in a value here that isn't in the 
# UARTControllers command variable for modes then it *will* crash.

t.set("camSettings.camFovX", 17.6) # Float
t.set("camSettings.camFovY", 13.2) # Float

t.set("camSettings.contrast", 50) # Int, in increments of ten from 0-199
t.set("camSettings.temporalNR", 50) # Int, in increments of ten from 0-199
t.set("camSettings.spatialNR", 50) # Int, in increments of ten from 0-199

t.set("displaySettings.coveredX", 1000) # Int, from 0 to the screen size.
t.set("displaySettings.coveredY", 1500) # Int, from 0 to the screen size.
# Reccommend you compute coveredY based off of your camera's aspect ratio.
# You are able to force this to be square, though it's not recomended.

t.set("enabledModules", []) # List of strings

import setup.py