from collections.abc import Callable

#import pySerial as ser

"""
Notes:


TODO:
Handle changing text box sizes
Handle submenues
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

        match itemType:
            case "text":
                self.possibleValues = data 
                self.currentVal = 0

            case "int":
                self.maximum = data[1]
                self.minimum = data[2]
                self.stepSize = round((self.maximum - self.minimum) / numSteps)

            case "float":
                self.maximum = data[1]
                self.minimum = data[2]
                self.stepSize = (self.maximum - self.minimum) / numSteps

            case "toggle":
                pass

            case "exit":
                pass

            case _:
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
        match self.itemType:
            case "text":
                self.currentVal += 1
                if self.currentVal == len(self.possibleValues):
                    self.currentVal = 0
                self.updateDisplayText(self.possibleValues[self.currentVal])
            case "int":
                if self.currentVal != self.maximum:
                    self.currentVal += self.stepSize
                self.updateDisplayText(self.currentVal)
            case "float":
                if self.currentVal != self.maximum:
                    self.currentVal += self.stepSize
                self.updateDisplayText(self.currentVal)
            case "toggle":
                self.currentVal = not self.currentVal
                self.updateDisplayText(self.currentVal)                    
            case "exit":
                pass

    def decrementCurrentVal(self):
        match self.itemType:
            case "text":
                self.currentVal -= 1
                if self.currentVal < 0:
                    self.currentVal = len(self.possibleValues) - 1
                self.updateDisplayText(self.possibleValues[self.currentVal])
            case "int":
                if self.currentVal != self.minimum:
                    self.currentVal -= self.stepSize
                self.updateDisplayText(self.currentVal)
            case "float":
                if self.currentVal != self.minimum:
                    self.currentVal -= self.stepSize
                self.updateDisplayText(self.currentVal)
            case "toggle":
                self.currentVal = not self.currentVal
                self.updateDisplayText(self.currentVal)
            case "exit":
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
        return b"\xF0" + self.size + b"\x36" \
               + self.classAddress + self.subclassAddress \
               + self.flag + self.data\
               + self.chk + b"\xFF"

class UARTController:
    """
    Helper class for handling the sending and interpretation? of commands.
    """
    uartStart = b"\xF0"
    uartEnd = b"\xFF"
    deviceAddress = b"\x36"
    
    commands = {
        "READModel": Command(b"\x74", b"\x02", b"\x01", b"\x00"),
        "SETBrightness": Command(b"\x78", b"\x02", b"\x00", b"\x00"),
        "SETContrast": Command(b"\x78", b"\x03", b"\x00", b"\x00"),
        "SETImageEnhancement": Command(b"\x78", b"\x10", b"\x00", b"\x00"),
        "SETStaticDenoise": Command(b"\x78", b"\x15", b"\x00", b"\x00"),
        "SETDynamicDenoise": Command(b"\x78", b"\x16", b"\x00", b"\x00"),
        "SETPallette": Command(b"\x78", b"\x20", b"\x00", b"\x00")
    }

    def sendCommand(self, signalOBJ, commandName, *modifyData):
        curCommand = self.commands[commandName]
        if len(modifyData) != 0:
            curCommand.changeData(*modifyData)
        payload = curCommand.buildPayload() 

#Checksum = Add device, class, subclass, retirn flag and data, take lower 8 bits

print("Helpers loaded.")