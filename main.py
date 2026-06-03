import serial
from helpers import *
import numpy as np 
import cv2
import pygame
from picamera2 import Picamera2
import sys
from RPi_GPIO_Rotary import rotary

pygame.init()

# Variable definitions --------------------------------------------------
cameraControl = serial.Serial(port = "/dev/serial0", baudrate = 115200)

usbCam = False
mainLoop = True

screenResX = 1920
screenResY = 1080

thermalCameraResX = 640
thermalCameraResY = 480

# Computed value based off of the camera FoV and the screen FoV.
coveredX = 500
coveredY = int(coveredX * (thermalCameraResY/thermalCameraResX))
# Maintains aspect ratio. Will work with a predefined value but 
# the image may become stretched.

xBuffer = int((screenResX - coveredX)/2 - coveredX/2)
yBuffer = int((screenResY - coveredY)/2 - coveredY/2)

interpolationMode = cv2.INTER_AREA if coveredX < thermalCameraResX else cv2.INTER_NEAREST

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
font = pygame.font.SysFont(None, 30)

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

def textBox(textIn, selected):
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


mainMenu = {
    "pallet": MenuItem("Colour Pallet", "pallet", "text", *[
        "White Hot", "Black Hot", "Red Hot" # TODO DOUBLE CHECK THIS
    ]),
    "display": MenuItem("Display mode", "display", "text", *[
        "Full image", "Cutoff", "Edges"
    ]),

    "cutoff": MenuItem("Cutoff temperature", "cutoff", "toggle", None,
        dependsOn = ("display", "Cutoff")
    ),

    "edgeDetectionMode" : MenuItem("Edge detect mode", "edgeDetectionMode",
        "text", *["Auto", "Manual"], dependsOn = ("display", "Edges")
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

curMenuIndex = 0

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

    mainMenu["display"].setCurrentVal(2)

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

        case _:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    img = cv2.resize(img, (coveredX, coveredY), interpolation = interpolationMode)
    #img = cv2.copyMakeBorder(img, yBuffer, yBuffer, xBuffer, 
    #xBuffer, cv2.BORDER_CONSTANT, value = (0,0,0))

    surf = pygame.surfarray.make_surface(img)
    display.blit(surf, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainLoop = False 
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                mainLoop = False

            if pygame.key.get_pressed()[pygame.K_UP]:
                incrementFlagCallback()
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                decrementFlagCallback()
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                buttonFlagCallback()

    if buttonFlag and showMenu == False:
        showMenu = True
        buttonFlag = False
    elif buttonFlag and itemSelected:
        itemSelected = False 
        buttonFlag = False
    elif buttonFlag:
        itemSelected = True
        buttonFlag = False

    if showMenu:
        if incrementFlag == True:
            curMenuIndex += 1
            incrementFlag = False
        elif decrementFlag == True:
            curMenuIndex -= 1
            decrementFlag = False
            
        if curMenuIndex < 0:
            curMenuIndex = len(mainMenu)
        elif curMenuIndex > len(mainMenu):
            curMenuIndex = 0
        valid = False
        count = 0
        while not valid and not count > len(mainMenu):
            curMenuItem = list(mainMenu.items())[curMenuIndex][1]
            dependencies = curMenuItem.dependency
            if dependencies == None:
                valid = True
            elif mainMenu[dependencies[0]].getCurrentVal() == dependencies[1]:
                valid = True
            else:
                curMenuItem += 1
                count += 1
                if curMenuItem > len(mainMenu):
                    curMenuIndex = 0

        curMenuKey = list(mainMenu.keys())[curMenuIndex][1]

        mainItem = list(mainMenu.items())[curMenuIndex][1].getDisplayText()
        displayX, displayY = surf.get_width(), surf.get_height()
        textBoxSurf = textBox(mainItem, False)
        textBoxX, textBoxY = textBoxSurf.size()
        display.blit(textBoxSurf, (displayX/2 - textBoxX/2, displayY/2 - textBoxY/2))

    pygame.display.update()

pygame.quit()
sys.exit()