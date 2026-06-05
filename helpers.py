from collections.abc import Callable
from picamera2 import Picamera2
from threading import Thread
import cv2
import numpy as np

#import pySerial as ser

"""
Notes:


TODO:
"""

class MenuItem:
    """
    Class for each individual menu item.
    """
    def __init__(self, displayText: str, name: str,
                itemType: str, *data: list, numSteps = 20, dependsOn = None):
        
        self.displayText = displayText
        self.defaultDisplayText = displayText
        self.name = name
        self.itemType = itemType
        self.currentVal = data[0]
        self.dependency = dependsOn


        if itemType == "text":
            self.possibleValues = data 
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


    def getDisplayText(self): 
        return str(self.displayText)
    # Setter covered by self.updateDisplayText
    
    def getName(self):
        return self.name
    
    def getCurrentVal(self):
        if self.itemType == "text":
            return self.possibleValues[self.currentVal]
        else:
            return self.currentVal
    def setCurrentVal(self, val):
        self.currentVal = val

    def getType(self):
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
#SERIAL COMMUNICATION

class Command():
    """
    Class to represent a single command.
    
    Attributes:
    classAddress : byte
        Class address for a command in the docs.
    subclassAddress : byte
        Subclass address for a command in the docs.
    flag : byte
        Read/write flag for a given command.
    data : list[byte]
    """
    deviceAddress = b"\x36"

    def __init__(self, classAddress, subclassAddress, flag, *data):
        self.classAddress = classAddress
        self.subclassAddress = subclassAddress
        self.flag = flag
        self.data = data

        self.size = (len(data) + 4).to_bytes(1, byteorder="big")
        chkInt = int.from_bytes(classAddress, byteorder="big") \
                                + int.from_bytes(subclassAddress, byteorder="big") \
                                + int.from_bytes(flag, byteorder = "big")
        for i in data:
            chkInt += int.from_bytes(i, byteorder = "big")
        self.chk = bytes([int((bin(chkInt)[2:])[-8:], 2)])
        
    
    def changeData(self, *data):
        self.size = (len(data) + 4).to_bytes(1, byteorder="big")
        chkInt = int.from_bytes(self.classAddress, byteorder="big") \
                                + int.from_bytes(self.subclassAddress, byteorder="big") \
                                + int.from_bytes(self.flag, byteorder = "big")
        for i in data:
            chkInt += int.from_bytes(i, byteorder = "big")
        self.chk = bytes([int((bin(chkInt)[2:])[-8:], 2)])
        
    def buildPayload(self):
        dataString = b""
        for i in self.data:
            dataString += i
        return b"\xF0" + self.size + b"\x36" \
               + self.classAddress + self.subclassAddress \
               + self.flag + dataString\
               + self.chk + b"\xFF"


class UARTController:
    """
    Helper class for handling the sending and interpretation? of commands.
    """
    
    def sendCommand(serialOBJ, commandName, *modifyData):
        commands = {
        "READModel": Command(b"\x74", b"\x02", b"\x01", b"\x00"),
        "SETBrightness": Command(b"\x78", b"\x02", b"\x00", b"\x00"),
        "SETContrast": Command(b"\x78", b"\x03", b"\x00", b"\x00"),
        "SETImageEnhancement": Command(b"\x78", b"\x10", b"\x00", b"\x00"),
        "SETStaticDenoise": Command(b"\x78", b"\x15", b"\x00", b"\x00"),
        "SETDynamicDenoise": Command(b"\x78", b"\x16", b"\x00", b"\x00"),
        "SETPallet": Command(b"\x78", b"\x20", b"\x00", b"\x00")
        }

        curCommand = commands[commandName]
        if len(modifyData) != 0:
            curCommand.changeData(*modifyData)
        payload = curCommand.buildPayload()
        print(payload)
        serialOBJ.write(payload)

#Checksum = Add device, class, subclass, retirn flag and data, take lower 8 bits

print("Helpers loaded.")