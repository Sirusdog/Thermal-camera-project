#import pySerial as ser
from helpers import *
import numpy as np 
import cv2
import pygame
import Picamera
import sys
import asyncio


# Variable definitions --------------------------------------------------
#cameraControl = ser.serial.Serial(port = "/dev/ttyS0", baudrate = 115200)

usbCam = False
mainLoop = True


screenResX = 1500
screenResY = 1500

thermalCameraResX = 3280
thermalCameraResY = 2464

# Computed value based off of the camera FoV and the screen FoV.
coveredX = 1000
coveredY = int(coveredX * (thermalCameraResY/thermalCameraResX))
# Maintains aspect ratio. Will work with a predefined value but 
# the image may become stretched.

xBuffer = int((screenResX - coveredX)/2)
YBuffer = int((screenResY - coveredY)/2)

interpolationMode = cv2.INTER_AREA if coveredX < thermalCameraRexX else cv2.INTER_NEAREST

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

buttonFlag = False
incrementFlag = False
decrementFlag = False
showMenu = False
itemSelected = False

async def buttonFlagCallback():
    global buttonFlag
    buttonFlag = True

async def incrementFlagCallback():
    global incrementFlag
    incrementFlag = True

async def decrementFlagCallback():
    global decrementFlag
    decrementFlag = True

async def showMenuCallback():
    global showMenu
    showMenu = True

async def itemSelectedCallback():
    global itemSelected
    itemSelected = True


mainMenu = {
    "pallet": MenuItem("Colour Pallet", "pallet", "text", [
        "White Hot", "Black Hot", "Red Hot" # TODO DOUBLE CHECK THIS
    ]),
    "display": MenuItem("Display mode", "display", "text", [
        "Full image", "Cutoff", "Edges"
    ]),

    "cutoff": MenuItem("Cutoff temperature", "cutoff", "toggle", None,
        dependsOn = ("display", "Cutoff")
    ),

    "edgeDetectionMode" : MenuItem("Edge detect mode", "edgeDetectionMode",
        "text", ["Auto", "Manual"], dependsOn = ("display", "Edges")
    ), 

    "edgeSensitivityLower": MenuItem("Edge sensitivity lower", 
        "edgeSensitivityLower", "int", 0, 200, 
        dependsOn = ("edgeDectionMode", "Manual")
    ),

    "edgeSensitivityUpper": MenuItem("Edge sensitivity upper", 
        "edgeSensitivityUpper", "int", 0, 255, 
        dependsOn = ("edgeDectionMode", "Manual")
    ),

    "digitalZoom": MenuItem("Digital zoom", "digitalZoom", "float", 1, 4),

    "contrast": MenuItem("Image Enhancement", "imageEnhancement", "int", 0, 100
    ),

    "staticDenoise": MenuItem("Static Denoising", "staticDenoise", "int", 
        0, 100
    ),

    "dynamicDenoise": MenuItem("Dynamic Denoising", "dynaicDenoise", "int",
        0, 100
    ),

    "exit": MenuItem("Exit menu", "exit", "exit", None)
}

if usbCam:
    cam = cv2.VideoCapture(0)
else:
    cam = Picamera2()
    cam.start

# Main --------------------------------------------------------------------
while mainLoop:
    if usbCam:
        ret, frame = cam.read()
    else:
        frame = cam.capture_array()
        frame = np.rot90(frame)
        frame = cv2.flip(frame, 1)
    
    match mainMenu["display"].getCurrentVal():
        case "Edges":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if mainMenu["edgeDetectionMode"].getCurrentVal() == "Auto":
                np.median(frame)
                lowerThreshold = int(max(0, 0.66 * median))
                upperThreshold = int(min(255, 1.33 * median))
            else:
                lowerThreshold = mainMenu["edgeSensitivityLower"].getCurrentVal()
                upperThreshold = mainMenu["edgeSensitivityUpper"].getCurrentVal()

            edges = cv2.Canny(frame, lowerThreshold, upperThreshold)
            img = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        case "Cutoff":
        
            # TODO: Deterimine how to get the cuttoff temperature for each pixel.
            # Once that's done then just truncate the value to 0.
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        case "Full Image":
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    img = cv2.resize(img, (coveredX, coveredY), interpolation = interpolationMode)
    img = cv2.copyMakeBorder(img, yBuffer, yBuffer, xBuffer, xBuffer,
                            cv2.BORDER_CONSTANT, value = (0,0,0))
    surf = pygame.surfarray.make_surface(img)
    displaysurf.blit(surf, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainLoop = False 
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                mainLoop = False

    pygame.display.update()

pygame.quit()
sys.exit()