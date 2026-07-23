from picamera2 import Picamera2 # Deprecated.
from threading import Thread
import cv2
import numpy as np
import cython
import numpy.typing as npt
from concurrent.futures import ThreadPoolExecutor as tpe
import logging
import serial
from crc import Calculator, Crc16
import os
import time
logger = logging.getLogger(__name__)

if not cython.compiled:
    print("Helpers is not cythonized. Re-run the build script to speed things up.")

class MenuItem:
    """
    Class for each individual menu item.
    """
    def __init__(self, displayText: str, name: str, itemType: str,  data: list,
                numSteps = 20, dependsOn = None):
        
        self.displayText = displayText
        self.defaultDisplayText = displayText
        self.name = name
        self.itemType = itemType
        self.currentVal = data[0]
        self.dependency = dependsOn


        if itemType == "text":
            self.possibleValues = data[1:]
            self.currentVal = 0

        elif itemType == "int":
            self.maximum = data[1]
            self.minimum = data[2]
            self.stepSize = round((self.maximum - self.minimum) / numSteps)

        elif itemType == "float":
            self.maximum = data[1]
            self.minimum = data[2]
            self.stepSize = (self.maximum - self.minimum) / numSteps

        elif itemType == "toggle":
            pass

        elif itemType == "exit":
            self.currentVal = ""

        else:
            raise ValueError("Invalid menu type specified.")
    
    def updateDisplayText(self, val):
        """Updates the displayed text to the given value. Mostly internal."""
        self.displayText = val

    def reset(self):
        """Resets displayText to it's default."""
        self.displayText = self.defaultDisplayText


    def getDisplayText(self) -> str: 
        return str(self.displayText)
    # Setter covered by self.updateDisplayText
    
    def getName(self) -> str:
        return self.name
    
    def getCurrentVal(self):
        if self.itemType == "text":
            return self.possibleValues[self.currentVal]
        else:
            return self.currentVal

    def setCurrentVal(self, val):
        self.currentVal = val

    def getType(self) -> str:
        return self.type

    def incrementCurrentVal(self):
        if self.itemType =="text":
            self.currentVal += 1
            if self.currentVal == len(self.possibleValues):
                self.currentVal = 0
            self.updateDisplayText(self.possibleValues[self.currentVal])

        elif self.itemType == "int":
            if self.currentVal != self.maximum:
                self.currentVal += self.stepSize
            self.updateDisplayText(self.currentVal)

        elif self.itemType == "float":
            if self.currentVal != self.maximum:
                self.currentVal += self.stepSize
                self.currentVal = round(self.currentVal, 2)
            self.updateDisplayText(self.currentVal)

        elif self.itemType == "toggle":
            self.currentVal = not self.currentVal
            self.updateDisplayText(self.currentVal)

        elif self.itemType == "exit":
            pass

    def decrementCurrentVal(self):
        if self.itemType ==  "text":
            self.currentVal -= 1
            if self.currentVal < 0:
                self.currentVal = len(self.possibleValues) - 1
            self.updateDisplayText(self.possibleValues[self.currentVal])

        elif self.itemType == "int":
            if self.currentVal != self.minimum:
                self.currentVal -= self.stepSize
            self.updateDisplayText(self.currentVal)

        elif self.itemType == "float":
            if self.currentVal != self.minimum:
                self.currentVal -= self.stepSize
            self.updateDisplayText(self.currentVal)

        elif self.itemType == "toggle":
            self.currentVal = not self.currentVal
            self.updateDisplayText(self.currentVal)

        elif self.itemType == "exit":
            pass


#---------------------------------------------------------------------------
#VIDEO HANDLING

class CameraHandler:
    # Taking implementation from https://pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/

    fourcc = cv2.VideoWriter_fourcc(*"DIVX")

    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        #self.cam.set_controls({'AeEnable': False})
        #config = self.cam.create_still_configuration(
        #    buffer_count = 2,
        #    controls={"Framerate": 50}
        #)
        #self.cam.start()
        #self.stopped = False

        ret, frame = self.cam.read()
        #f = np.rot90(f)
        #frame = cv2.flip(f, 1)

        self.frame = frame # cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.fps = 0
        self.record = False
        self.recorder = None
        self.stopped = False

    def startThread(self):
        Thread(target=self.updateThread, args=()).start()
        return self

    def updateThread(self):
        prevTime = 0
        while not self.stopped:
            ret, frame = self.cam.read()
            frame = np.rot90(frame)
            frame = cv2.flip(frame, 1)
            self.frame = frame

            # Gets the FPS.
            curTime = time.time()
            self.fps = 1/(curTime - prevTime)
            prevTime = curTime

        if self.stopped:
            return

    def read(self) -> np.typing.NDArray:
        return self.frame

    def stop(self):
        self.stopped = True

    def getFPS(self):
        return self.fps


    def startRecording(self):
        count = str(len(os.listdir("./Videos")))
        self.recorder = cv2.VideoWriter(
            "ThermalCamVideo " + count, fourcc, 50, (256, 192)
            )
        self.record = True
        Thread(target = self.recordThread, args = ()).start()

    def recordThread(self):
        while self.record and not self.stopped:
            self.recorder.write(self.frame)
        return

    def stopRecording(self):
        self.record = False

#---------------------------------------------------------------------------
#SERIAL COMMUNICATION



class UARTController:
    """
    Helper class for handling the sending and interpretation of UART commands.
    """
    commands = {
        'Pallet': {
            'White Hot': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x54\x6D',
            'Reserved': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1D\xB5',
            'Sepia': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xE7\xCD',
            'Ironbow': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xAE\x15',
            'Rainbow': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x3C',
            'Night': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5A\xE4',
            'Aurora': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xA0\x9C',
            'Red Hot': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xE9\x44',
            'Jungle': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xDA\xCF',
            'Medical': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x93\x17',
            'Black Hot': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x69\x6F',
            'Golden Red': rb'\x55\x43\x49\x12\x00\x10\x03\x45\x00\x00\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\xB7',
            'Get': rb'\x55\x43\x49\x12\x00\x10\x03\x85\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x21\x67',
        },
        
        'Mode': {
            'Low Temperature Highlight': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xC5\x65',
            'Linear Stretch': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xB0\x66',
            'Low Contrast': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x63',
            'General': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5A\x60',
            'High Contrast': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\x68',
            'Highlight': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x64\x6B',
            'Reserved 1': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFB\x6E',
            'Reserved 2': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8E\x6D',
            'Reserved 3': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x6D\x7E',
            'Outline': rb'\x55\x43\x49\x12\x00\x10\x04\x42\x00\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x7D',
            'Get': rb'\x55\x43\x49\x12\x00\x10\x04\x89\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x0D\x0A'
            },

        'Detail Enhancement': {
            '0': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xC3\x15',
            '10': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x81\x08',
            '20': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x47\x2F',
            '30': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x1E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x32',
            '40': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xCB\x60',
            '50': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x32\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xD9\x4A',
            '60': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x3C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4F\x5A',
            '70': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x46\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xBD\xC3',
            '80': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xD3\xFF',
            '90': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x5A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x91\xE2',
            '100': rb'\x55\x43\x49\x12\x00\x10\x04\x45\x00\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xF7\xAB',
            'Get': rb'\x55\x43\x49\x12\x00\x10\x04\x85\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xC3\x1C'
        },

        'Contrast': {
            '0': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xAE\x8E',
            '10': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xEC\x93',
            '20': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2A\xB4',
            '30': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x1E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x68\xA9',
            '40': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xA6\xFB',
            '50': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x32\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xB4\xD1',
            '60': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x3C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x22\xC1',
            '70': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x46\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xD0\x58',
            '80': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xBE\x64',
            '90': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x5A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFC\x79',
            '100': rb'\x55\x43\x49\x12\x00\x10\x04\x4A\x00\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9A\x30',
            'Get': rb'\x55\x43\x49\x12\x00\x10\x04\x8A\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xAE\x87',
        },

        'Spatial Noise Reduction': {
            '0': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xCF\xF5',
            '10': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8D\xE8',
            '20': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4B\xCF',
            '30': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x1E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09\xD2',
            '40': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xC7\x80',
            '50': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x32\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xD5\xAA',
            '60': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x3C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x43\xBA',
            '70': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x46\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xB1\x23',
            '80': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xDF\x1F',
            '90': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x5A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9D\x02',
            '100': rb'\x55\x43\x49\x12\x00\x10\x04\x4B\x00\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFB\x4B',
            'Get': rb'\x55\x43\x49\x12\x00\x10\x04\x8B\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xCF\xFC'
        },
        'Temporal Noise Reduction': {
            '0': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xC9\x85',
            '10': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8B\x98',
            '20': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4D\xBF',
            '30': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x1E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\xA2',
            '40': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xC1\xF0',
            '50': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x32\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xD3\xDA',
            '60': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x3C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x45\xCA',
            '70': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x46\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xB7\x53',
            '80': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xD9\x6F',
            '90': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x5A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9B\x72',
            '100': rb'\x55\x43\x49\x12\x00\x10\x04\x4C\x00\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFD\x3B',
            'Get': rb'\x55\x43\x49\x12\x00\x10\x04\x8C\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xC9\x8C'
        },
        'Module Temperature': {
            'Get': rb'\x55\x43\x49\x12\x00\x10\x10\x91\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x6A'
        },
        'Max Temperature': {
            'Get': rb'\x55\x43\x49\x12\x00\x10\x10\x92\x00\x00\x00\x00\x00\x00\x01\xC0\x00\x0e\x00\x00\x00\xce\xa0'
        },
        'Zoom': {
            '1': rb'\x55\x43\x49\x12\x00\x01\x31\x42\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x0A',
            '2': rb'\x55\x43\x49\x12\x00\x01\x31\x42\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x41\x0C',
            '3': rb'\x55\x43\x49\x12\x00\x01\x31\x42\x00\x00\x1E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7C\x0E',
            '4': rb'\x55\x43\x49\x12\x00\x01\x31\x42\x00\x00\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xCF\x00',
            '8': rb'\x55\x43\x49\x12\x00\x01\x31\x42\x00\x00\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xD3\x19',
            'Get': rb'\x55\x43\x49\x12\x00\x01\x31\x82\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x4E\x02'
        },
        'Save': {
            'Parameter Save': rb'\x55\x43\x49\x12\x00\x10\x10\x51\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xA9\xFB',
            'Parameter Restore': rb'\x55\x43\x49\x12\x00\x10\x10\x52\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x76'
        }
    }
    responsesGeneral = {}
    responses = {}
    for cmdSet, cmds in commands.items():
        for k, v in cmds.items():
            responsesGeneral[v] = [cmdSet, v]
    # Turns commands inside out

    numericResponses = ["Module Temperature", "Max Temperature"]

    crcCalculator = Calculator(Crc16.XMODEM)

    def sendCommand(
        serialOBJ: serial.Serial, commandClass: str, subCommand
        ):

        curCommand = UARTController.commands[commandClass]
        byteString = list(curCommand[subCommand])
        serialOBJ.write(byteString)
        responseHeader = serialOBJ.read(5)
        successFlag = responseHeader[4]

        response = serialOBJ.read(int.from_bytes(responseHeader[2:-1], "big"))
        ret = {}
        
        expectedCRC = response[-4:-2]
        data = response[:-4]
        recievedCRC = UARTController.crcCalculator.checksum(data)

        if response == b"":
            logger.warning("No response recieved. Cable is likely disconnected.")
            print("No response, cable likely disconnected.")
            ret["success"] = False
        if expectedCRC != recievedCRC:
            logger.warning("Command " + commandClass + ": CRC check failed.")
            print(("Command " + commandClass + ": CRC check failed. "))
        if successFlag != b"\x00":
            logger.warning("Command " + commandClass + ": Status abnormal.")
            logger.warning(str(response))

        if commandClass not in UARTController.numericResponses:
            try:
                responseClass, name = responses[data]
                logger.debug("Command " + commandClass + ": Returned " + responseClass + name)
                ret["success"] = True
                ret["responseClass"] = responseClass
                ret["name"] = name
            except KeyError:
                logger.warning("Command " + commandClass + ": Returned an invalid value.")
                ret["success"] = False




#---------------------------------------------------------------------------
#GPS HANDLING
class GPSReciever:
    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyAMC0', baudrate = 115200)
        self.time = 0
        self.longitude = 0
        self.latitude = 0
        self.latHemisphere = "N"
        self.longHemisphere = "W"

    def getLongitude(self):
        return self.longitude
    def getLatitude(self):
        return self.latitude

    def startGPS(self):
        Thread(target = self.gpsThread, args = ()).start()

    def gpsThread(self):
        try:
            data = self.ser.readline()
        except Exception as e:
            logger.warn("The following error occured when reading the GPS data")
            logger.warn(e)
        

#---------------------------------------------------------------------------
#IMU HANDLING
class IMUHandler:
    def __init__(self):
        #self.
        pass

print("Helpers loaded.")