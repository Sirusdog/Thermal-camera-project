import serial
import helpers

ser = serial.Serial(
    port = "/dev/serial0", baudrate = 115200, parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE, timeout=1)
from time import sleep
from binascii import hexlify


#ser.send(b"\x55\x43\x49\x12\x00\x10\x10\x46\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x58\x4d")

def cycle(data):
    ser.write(data)
    ret = ser.read(23)
    print(ret)
    sleep(1)
    return ret

analogOutputModes = {b"\xBE\xAA\x03\x00\x00\x00\x00\x04\x49\xEB\xAA": "Analog off",
b"\xBE\xAA\x03\x00\x00\x01\x00\x35\x7a\xEB\xAA": "NTSC On",
b"\xBE\xAA\x03\x00\x00\x01\x01\x14\x6a\xEB\xAA": "Pal on",
b"": "Returned thing empty"
}
"""
print("Sending/recieving serial data.")
vidDisabled = cycle(b"\x55\x43\x49\x12\x00\x10\x10\x4a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x96\x5b") # Disable video
videoToNTSC = cycle(b"\x55\x43\x49\x12\x00\x10\x10\x4a\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xaa\x80") # Change video to NTSC?
displayMode = cycle(b"\x55\x43\x49\x12\x00\x10\x10\x8a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x3f\xca") # Get display mode
print("Serial code written")
print(analogOutputModes[displayMode])
"""
UARTController.sendCommand(ser, "Mode", index = 1)
UARTController.sendCommand(ser, "Mode", subCommand = "Get")