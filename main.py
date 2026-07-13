import serial # For communicating with the camera.
from helpers import *
import numpy as np # Array handling.
import cv2 # Image capture and processing.
import pygame # Actually displaying things.
from picamera2 import Picamera2 # Now deprecated.
import sys # Properly exiting the program once shutdown.
from RPi_GPIO_Rotary import rotary # For handling the rotary encoder.
import time # FPS displays.
from threading import Thread # Speeding up camera input.
import cython
import traceback # Properly prints errors.
import signal

from trapdoor import Trapdoor # Handles settings file

settings = Trapdoor("main", ".\\configs", "mainConfig.toml")

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='main.log', encoding='utf-8')
logger.setLevel(logging.WARNING)

def handler(signum, frame):
    pass
try:
    signal.signal(signal.SIGHUP, handler)
except AttributeError:
    pass

if not cython.compiled:
    print("Main is not cythonized. Re-run the build script to speed things up.")


# Definitions and initialisations --------------------------------------------
cameraControl = serial.Serial(
    port = "/dev/serial0", 
    baudrate = 115200, 
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE, 
    timeout=1
    )

pygame.init()

usbCam = True
mainLoop = True

thermalCameraResX = 256
thermalCameraResY = 192

# Get these from the cameras spec sheet
camFovX = float(settings.get("camSettings.camFovX"))
camFovY = float(settings.get("camSettings.camFovY"))

# Computed value based off of the camera FoV and the screen FoV.
coveredX = int(settings.get("displaySettings.coveredX"))
coveredY = int(settings.get("displaySettings.coveredY"))

# Maintains aspect ratio. Will work with a predefined value but 
# the image may become stretched.

interpolationMode = cv2.INTER_AREA if coveredX < thermalCameraResX else cv2.INTER_NEAREST

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
font = pygame.font.SysFont(None, 30)

screenResX = display.get_width()
screenResY = display.get_height()

xBuffer = int(screenResX/2 - coveredX/2)
yBuffer = int(screenResY/2 - coveredY/2)

print("Using display of dimensions:", display.get_width(), display.get_height())

buttonFlag = False
incrementFlag = False
decrementFlag = False
showMenu = False
itemSelected = False

def buttonFlagCallback():
    global buttonFlag
    buttonFlag = True

def incrementFlagCallback():
    global incrementFlag
    incrementFlag = True

def decrementFlagCallback():
    global decrementFlag
    decrementFlag = True

def textBox(textIn: str, selected: bool) -> pygame.Surface:
    # Dynamically draws a border around some given text.
    text = font.render(textIn, 1, (255,255, 255))
    width, height = font.size(textIn)

    boxSurf = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
    color = (255, 0, 0) if selected else (255, 255, 255)
    coords = pygame.Rect(0, 0, width + 20, height + 20)

    pygame.draw.rect(boxSurf, color, coords, width = 5)
    boxSurf.blit(text, (10, 10))

    return boxSurf


rotaryEncoder = rotary.Rotary(23, 24, 25, 2)
rotaryEncoder.register(increment = incrementFlagCallback,
                       decrement = decrementFlagCallback,
                       pressed = buttonFlagCallback
                       )
rotaryEncoder.start()

enabledModules = settings.get("enabledModules")

mainMenu = {
    "pallet": MenuItem("Colour Pallet", "pallet", "text", 
        settings.get("current.pallet"), 
        settings.get("camSettings.enabledPallets").split(", ")
    ),

    "display": MenuItem("Display mode", "display", "text", 
        settings.get("current.display"), 
        settings.get("camSettings.enabledModes").split(", ")
    ),

    "record": MenuItem("Record", "record", "toggle", False, None),

    #"digitalZoom": MenuItem("Digital zoom", "digitalZoom", "float", 1, 1, 2.5, 
    #    numSteps = 4),

    "contrast": MenuItem("Image Enhancement", "imageEnhancement", "int", 
        [int(settings.get("current.contrast")), 0, 100]
    ),

    "spatialNR": MenuItem("Spatial NR", "spatialNR", "int", 
        [int(settings.get("current.spatialNR")),  0, 100]
    ),

    "temporalNR": MenuItem("Temporal NR", "temporalNR", "int",
        [int(settings.get("current.temporalNR")),  0, 100]
    ),

    "xShift": MenuItem("Alignment shift X", "xShift", "int", [0, -400, 400], 
        numSteps = 800),

    "yShift": MenuItem("Alignment shift Y", "yShift", "int", [0, -400, 400], 
        numSteps = 800),

    "exit": MenuItem("Exit menu", "exit", "exit", None, None)
}
# TODO: Take in default x and y shifts.
if "map" in enabledModules and not "3dMap" in enabledModules:
    mainMenu["map"] = MenuItem("Show Map", "map", "toggle", False)
if "compass" in enabledModules:
    mainMenu["compass"] = MenuItem("Show Compass", "compass", "toggle", False)
if "waypoints" in enabledmodules and not "3dWaypoints" in enabledModules:
    mainMenu["waypoints"] = MenuItem("Show waypoints", "waypoints", "toggle", False)


associatedCommands = {
    "pallet": "Pallet",
    "display": "Mode",
    "spatialNR": "Spatial Noise Reduction",
    "temporalNR": "Temporal Noise Reduction",
    "imageEnhancement": "Detail Enhancement",
    "contrast": "Contrast"
}

toStore = [
    "pallet", "display", "contrast", "spatialNR", "temporalNR", "xShift", 
    "yShift", "map", "waypoints", "compass"
] # Values that are stored/kept the same on reboot.

curMenuIndex = 0

curDisplayMode = mainMenu["display"].getCurrentVal()



print("Initialisations complete, running main body.")
# Main --------------------------------------------------------------------
tPrev = 0
tNew = 0

cam = CameraHandler()
cam.startThread()
time.sleep(0.5)

try:
    while mainLoop:
        img = cam.read()
        logger.debug("Image read fine!")

        zoomLvl = 1 #mainMenu["digitalZoom"].getCurrentVal()

        img = cv2.resize(
            img, (int(coveredY * zoomLvl), int(coveredX * zoomLvl)), 
            interpolation = interpolationMode
        )

        xBuffer = int(screenResX/2 - int(coveredX * zoomLvl)/2) + (
            mainMenu["xShift"].getCurrentVal()
        )
        
        yBuffer = int(screenResY/2 - int(coveredY * zoomLvl)/2) + (
            mainMenu["yShift"].getCurrentVal()
        )

        surf = pygame.surfarray.make_surface(img)
        display.blit(surf, (int(xBuffer/(zoomLvl**2)), int(yBuffer/(zoomLvl**2))))
        logger.debug("Wrote to display surface fine!")

        # Handle pygame & keypress inputs. These are for debugging.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainLoop = False 
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    mainLoop = False

                # For debug inputs.
                if pygame.key.get_pressed()[pygame.K_DOWN]:
                    incrementFlagCallback()
                if pygame.key.get_pressed()[pygame.K_UP]:
                    decrementFlagCallback()
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    buttonFlagCallback()
        logger.debug("Events handled fine!")

        # Logic for showing the menu when the button is pressed and the menu isn't 
        # shown and for when it's pressed and something needs to be selected/
        if buttonFlag and showMenu == False:
            showMenu = True
            buttonFlag = False
        elif buttonFlag and itemSelected:
            itemSelected = False 
            buttonFlag = False
        elif buttonFlag:
            itemSelected = True
            buttonFlag = False
        
        logger.debug("Flags handled fine!")

        if showMenu:
            valid = False
            count = 0
            if not itemSelected:
                logger.debug("Item isn't selected")
                # Handles the actual rendering of each menu item.
                # As we don't want to display items with dependencies when
                # Those conditions aren't met, it loops through ever item
                # Until it finds the next one to display.

                if incrementFlag == True:
                    curMenuIndex += 1
                    incrementFlag = False
                    if curMenuIndex >= len(mainMenu):
                        curMenuIndex = 0
                    logger.debug("Inrementing")
                    while not valid:
                        curMenuItem = list(mainMenu.items())[curMenuIndex][1]
                        dependencies = curMenuItem.dependency

                        if dependencies == None:
                            valid = True
                        elif mainMenu[dependencies[0]].getCurrentVal() == dependencies[1]:
                            valid = True
                        else:
                            curMenuIndex += 1
                            count += 1
                            if curMenuIndex == len(mainMenu):
                                curMenuIndex = 0
                        logger.debug("Increment handled fine!")
                elif decrementFlag == True:
                    curMenuIndex -= 1
                    decrementFlag = False
                    if curMenuIndex < 0:
                        curMenuIndex = len(mainMenu) - 1
                    while not valid:
                        curMenuItem = list(mainMenu.items())[curMenuIndex][1]
                        dependencies = curMenuItem.dependency

                        if dependencies == None:
                            valid = True
                        elif mainMenu[dependencies[0]].getCurrentVal() == dependencies[1]:
                            valid = True
                        else:
                            curMenuIndex -= 1
                            count += 1
                            if curMenuIndex < 0:
                                curMenuIndex = len(mainMenu) - 1
                    logger.debug("Decrement handled fine!")
                mainMenu[list(mainMenu.keys())[curMenuIndex]].reset()

            else: # If the item is selected and the menu is shown:
                curMenuKey = list(mainMenu.keys())[curMenuIndex]
                mainMenu[curMenuKey].updateDisplayText(mainMenu[curMenuKey].getCurrentVal())

                # If a increment/decrement was triggered:
                doChange = False
                if incrementFlag:
                    mainMenu[curMenuKey].incrementCurrentVal()
                    incrementFlag = False
                    doChange = True
                    logger.debug("Sub-item increment handled fine!")
                elif decrementFlag:
                    mainMenu[curMenuKey].decrementCurrentVal()
                    decrementFlag = False
                    doChange = True
                    logger.debug("Sub-item decrement handled fine!")

                if doChange and curMenuKey in associatedCommands.keys():
                    # If we need to send some command to the camera.
                    cmdName = str(associatedCommands[curMenuKey]["command"])
                    subCommand = mainMenu[curMenuKey].getCurrentVal()
                    UARTController.sendCommand(
                        cameraControl,
                        cmdName,
                        subCommand
                    )
                    logger.debug("Command sent fine.")

                if curMenuKey in toStore: 
                    # If we want to store a value for later.
                    settings.set(
                        "current." + curMenuKey, 
                        mainMenu[curMenuKey].getCurrentVal()
                    )
                
            # Render the menu
            mainItem = list(mainMenu.items())[curMenuIndex][1].getDisplayText()
            displayX, displayY = display.get_width(), display.get_height()
            textBoxSurf = textBox(mainItem, itemSelected)
            textBoxX, textBoxY = textBoxSurf.get_width(), textBoxSurf.get_height()
            display.blit(textBoxSurf, (displayX/2 - textBoxX/2, displayY/2 - textBoxY/2))

            logger.debug("Rendering went fine!")

            # Handle what to do with certain inputs
            if list(mainMenu.items())[curMenuIndex][1].getName() == "exit" and itemSelected:
                showMenu = False
                itemSelected = False
            elif list(mainMenu.items())[curMenuIndex][1].getName() == "record" and itemSelected:
                itemSelected = False
                if mainMenu["record"].getCurrentVal():
                    cam.startRecording()
                else:
                    cam.stopRecording()


        tNew = time.time()
        fps = 1/(tNew - tPrev)
        tPrev = tNew
        txt = font.render(str(round(fps)), 1, (255,255, 255), (0,0,0))
        txt2 = font.render(f"{str(round(cam.getFPS())):2}", 1, (255, 255, 255), (0,0,0))
        display.blit(txt, (0,0))
        display.blit(txt2, (0, 35))
        pygame.display.update()

except Exception as e:
    print(e)
    traceback.print_exc()
finally:
    cam.stop()
    pygame.quit()
    sys.exit()