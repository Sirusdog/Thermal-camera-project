# Responsible for initialising/re-initialising the settings file.
# Set your default values here rather then in the config file itself to avoid
# problems if it accidentally corrupts.

from trapdoor import Trapdoor

t = Trapdoor("main", "./configs", "mainConfig.toml")
t.set("camSettings.enabledPallets", """White Hot, Black Hot, Ironbow, Rainbow, Night, Aurora, Red Hot, Jungle, Medical, Golden Red""") 
# Series of values seperated by a comma and a space 
# UARTControllers command variable for pallets then it *will* crash.

t.set("camSettings.enabledModes", """General, Outline, Low Temperature Highlight, Linear Stretch, High Contrast, Low Contrast""") 
# Series of values seperated by a comma and a space
# UARTControllers command variable for modes then it *will* crash.

t.set("camSettings.camFovX", "17.6") # Float, get from camera datasheet
t.set("camSettings.camFovY", "13.2") # Float, get from camera datasheet

t.set("displaySettings.coveredX", "256") # Int, from 0 to the screen size.
t.set("displaySettings.coveredY", "198") # Int, from 0 to the screen size.
# Reccommend you compute coveredY based off of your camera's aspect ratio.
# You are able to force this to be square, though it's not recomended.

t.set("current.xShift", "0") # Int
t.set("current.yShift", "0") # Int


t.set("enabledModules", '') # Series of values seperated by a comma and a space
# i.e "compass, waypoints"
# possible options are "compass, waypoints, 3dWaypoints, map, 3dMap"
# The 3D versino takes priority, so if you set both map and 3dMap it'll render
# the map in 3D.


t.set("current.display", "General")
t.set("current.pallet", "White Hot")
t.set("current.contrast", "50") # Int, in increments of ten from 0-100
t.set("current.temporalNR", "50") # Int, in increments of ten from 0-100
t.set("current.spatialNR", "50") # Int, in increments of ten from 0-100

t.set("current.compass", "False")
t.set("current.map", "False")
t.set("current.waypoints", "False")

import setup.py