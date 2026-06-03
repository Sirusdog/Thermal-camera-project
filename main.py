import serial
from helpers import *
import numpy as np 
import cv2
import pygame
from picamera2 import Picamera2
import sys
import asyncio
from RPi_GPIO_Rotary import rotary

# Variable definitions --------------------------------------------------
cameraControl = serial.Serial(port = "/dev/serial0", baudrate = 115200)

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
yBuffer = int((screenResY - coveredY)/2)

interpolationMode = cv2.INTER_AREA if coveredX < thermalCameraResX else cv2.INTER_NEAREST

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

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

def textBox():
    pass

rotaryEncoder = rotary.Rotary(23, 24, 25, 2)
rotaryEncoder.register(increment = incrementFlagCallback,
                       decrement = decrementFlagCallback,
                       pressed = buttonFlagCallback
                       )
rotaryEncoder.start()


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
        "edgeSensitivityLower", "int", 100, 0, 200, 
        dependsOn = ("edgeDectionMode", "Manual")
    ),

    "edgeSensitivityUpper": MenuItem("Edge sensitivity upper", 
        "edgeSensitivityUpper", "int", 250, 0, 255, 
        dependsOn = ("edgeDectionMode", "Manual")
    ),

    "digitalZoom": MenuItem("Digital zoom", "digitalZoom", "float", 1, 1, 4),

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

curMenuItem = 0

if usbCam:
    cam = cv2.VideoCapture(0)
else:
    cam = Picamera2()
    cam.start()

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
                median = np.median(frame)
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
    display.blit(surf, (0, 0))



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainLoop = False 
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                mainLoop = False

    pygame.display.update()

pygame.quit()
sys.exit()