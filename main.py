import serial
from helpers import *
import numpy as np 
import cv2
import pygame
from picamera2 import Picamera2
import sys
from RPi_GPIO_Rotary import rotary
import time
from threading import Thread
import cython
import traceback

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8')
logger.setLevel(logging.WARNING)
logger.debug("Item isn't selected")

if not cython.compiled:
    print("Main is not cythonized. Re-run the build script to speed things up.")


# Variable definitions --------------------------------------------------
cameraControl = serial.Serial(port = "/dev/serial0", baudrate = 115200)
pygame.init()

usbCam = False
mainLoop = True

thermalCameraResX = 640
thermalCameraResY = 480

# Get these from the cameras spec sheet
camFovX = 17.6
camFovY = 13.2

# Computed value based off of the camera FoV and the screen FoV.
coveredX = 1000
coveredY = int(coveredX * (thermalCameraResY/thermalCameraResX))
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


pallets = {"White Hot": [0, 0, 0, 1, 1, 1],
           "Black Hot": [-255, -255, -255, 1, 1, 1],
           "Ironbow": [0, 0, -255, 1, 0, 1],
           "Red Hot": [0, 0, 0, 1, 0, 0],
           "Orange": [0, 0, 0, 1, 0.41, 0.12]
           }
# Each pallet is defined as an offset for each channel and a multiplier.
# To get a "positive" color, leave it as 

rotaryEncoder = rotary.Rotary(23, 24, 25, 2)
rotaryEncoder.register(increment = incrementFlagCallback,
                       decrement = decrementFlagCallback,
                       pressed = buttonFlagCallback
                       )
rotaryEncoder.start()


mainMenu = {
    "pallet": MenuItem("Colour Pallet", "pallet", "text", *pallets.keys()),
    "display": MenuItem("Display mode", "display", "text", *[
        "Full image", "Cutoff", "Edges", "Raw output"
    ]),

    "cutoff": MenuItem("Cutoff temperature", "cutoff", "int",  50, 0, 100,
        dependsOn = ("display", "Cutoff")
    ),

    "edgeDetectionMode" : MenuItem("Edge detect mode", "edgeDetectionMode",
        "text", *["Auto", "Manual"], dependsOn = ("display", "Edges")
    ), 

    "edgeSensitivityLower": MenuItem("Edge sensitivity lower", 
        "edgeSensitivityLower", "int", 100, 0, 200, 
        dependsOn = ("edgeDetectionMode", "Manual")
    ),

    "edgeSensitivityUpper": MenuItem("Edge sensitivity upper", 
        "edgeSensitivityUpper", "int", 250, 0, 255, 
        dependsOn = ("edgeDetectionMode", "Manual")
    ),

    "digitalZoom": MenuItem("Digital zoom", "digitalZoom", "float", 1, 1, 2.5, 
        numSteps = 4),

    "contrast": MenuItem("Image Enhancement", "imageEnhancement", "int", 50,
        0, 100
    ),

    "staticDenoise": MenuItem("Static Denoising", "staticDenoise", "int", 50,
        0, 100
    ),

    "dynamicDenoise": MenuItem("Dynamic Denoising", "dynaicDenoise", "int",
        50,  0, 100
    ),

    "exit": MenuItem("Exit menu", "exit", "exit", None)
}


associatedCommands = {
    #"pallet": {
    #    "command": "SETPallet",
    #    "White Hot": b"\x00",
    #    "Black Hot": b"\x01",
    #    "Red Hot": b"\x02"
    #    },
    "staticDenoise": {
        "command": "SETStaticDenoise"
    },
    "dynamicDenoise": {
        "command": "SETDynamicDenoise"
    },
    "imageEnhancement": {
        "command": "SETStaticDenoise"
    },
    "contrast": {
        "command": "SETContrast"
    }
    }

curMenuIndex = 0

if usbCam:
    cam = cv2.VideoCapture(0)
else:
    pass


curDisplayMode = mainMenu["display"].getCurrentVal()

class CameraHandler:
    # Taking implementation from https://pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
    def __init__(self):
        self.cam = Picamera2()
        self.cam.set_controls({'AeEnable': False})
        self.cam.start()
        self.stopped = False

        f = self.cam.capture_array()
        f = np.rot90(f)
        frame = cv2.flip(f, 1)

        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.fps = 0

    def startThread(self):
        Thread(target=self.updateThread, args=()).start()
        return self

    def updateThread(self):
        prevTime = 0
        while not self.stopped:
            f = self.cam.capture_array()
            f = np.rot90(f)
            frame = cv2.flip(f, 1)

            displayMode = mainMenu["display"].getCurrentVal()
            edgeDetectMode = mainMenu["edgeDetectionMode"].getCurrentVal()
            curPallet = pallets[mainMenu["pallet"].getCurrentVal()]


            if displayMode =="Edges":
                # Converts an image to grayscale and computes the threshold values
                # for the cv2.Canny function. Then applies canny edge detection 
                # before converting the image into RGB.
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if edgeDetectMode == "Auto":
                    median = np.median(frame)
                    lowerThreshold = int(max(0, 0.66 * median))
                    upperThreshold = int(min(255, 1.33 * median))
                else:
                    lowerThreshold = mainMenu["edgeSensitivityLower"].getCurrentVal()
                    upperThreshold = mainMenu["edgeSensitivityUpper"].getCurrentVal()

                edges = cv2.Canny(frame, lowerThreshold, upperThreshold)
                img = recolorImage(edges, curPallet)

            elif displayMode == "Cutoff":
                # Converts the image into grayscale, computes the threshold for the
                # bottom percentage of pixels then sets them to 0.
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                threshold = np.max(frame) * (mainMenu["cutoff"].getCurrentVal()/100)
                for i in range(len(frame)):
                    frame[i][frame[i] < threshold] = 0

                img = recolorImage(frame, curPallet)

            elif displayMode == "Full image":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                img = recolorImage(frame, curPallet)

            elif displayMode == "Raw output":
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.frame = img
            curTime = time.time()
            self.fps = 1/(curTime - prevTime)
            prevTime = curTime

        if self.stopped:
            self.cam.stop()
            return

    def read(self) -> np.typing.NDArray:
        return self.frame

    def stop(self):
        self.stopped = True

    def getFPS(self):
        return self.fps

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

        curPallet = pallets[mainMenu["pallet"].getCurrentVal()]
        zoomLvl = mainMenu["digitalZoom"].getCurrentVal()

        img = cv2.resize(img, (int(coveredY * zoomLvl), int(coveredX * zoomLvl)), interpolation = interpolationMode)

        xBuffer = int(screenResX/2 - int(coveredX * zoomLvl)/2)
        yBuffer = int(screenResY/2 - int(coveredY * zoomLvl)/2)

        surf = pygame.surfarray.make_surface(img)
        display.blit(surf, (int(xBuffer/(zoomLvl**2)), int(yBuffer/(zoomLvl**2))))
        logger.debug("Wrote to display surface fine!")
        # Handle pygame & keypress inputs
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

            else:
                curMenuKey = list(mainMenu.keys())[curMenuIndex]
                mainMenu[curMenuKey].updateDisplayText(mainMenu[curMenuKey].getCurrentVal())

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
                    cmdName = associatedCommands[curMenuKey]["command"]
                    #if cmdName == "SETPallet":
                     #   data = associatedCommands[curMenuKey][mainMenu[curMenuKey].getCurrentVal()]
                    #else: Leaving this here in case I want to set the pallet
                    # on the camera later
                    data = bytes([mainMenu[curMenuKey].getCurrentVal()])
                    UARTController.sendCommand(
                        cameraControl,
                        cmdName,
                        data
                    )
                    logger.debug("Command sent fine.")
                
            # Render the menu
            mainItem = list(mainMenu.items())[curMenuIndex][1].getDisplayText()
            displayX, displayY = display.get_width(), display.get_height()
            textBoxSurf = textBox(mainItem, itemSelected)
            textBoxX, textBoxY = textBoxSurf.get_width(), textBoxSurf.get_height()
            display.blit(textBoxSurf, (displayX/2 - textBoxX/2, displayY/2 - textBoxY/2))

            logger.debug("Rendering went fine!")
            # Handle what to do with those inputs
            if list(mainMenu.items())[curMenuIndex][1].getName() == "exit" and itemSelected:
                showMenu = False
                itemSelected = False

        tNew = time.time()
        fps = 1/(tNew - tPrev)
        tPrev = tNew
        txt = font.render(str(round(fps)), 1, (255,255, 255), (0,0,0))
        txt2 = font.render(str(round(cam.getFPS())), 1, (255, 255, 255), (0,0,0))
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