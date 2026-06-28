import serial
from helpers import UARTController

ser = serial.Serial(
    port = "/dev/serial0", baudrate = 115200, parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE, timeout=1)
from time import sleep
from binascii import hexlify


analogOutputModes = {b"\xBE\xAA\x03\x00\x00\x00\x00\x04\x49\xEB\xAA": "Analog off",
b"\xBE\xAA\x03\x00\x00\x01\x00\x35\x7a\xEB\xAA": "NTSC On",
b"\xBE\xAA\x03\x00\x00\x01\x01\x14\x6a\xEB\xAA": "Pal on",
b"": "Returned thing empty"
}

UARTController.sendCommand(ser, "Zoom", 2)
UARTController.sendCommand(ser, "Zoom", "Get")
