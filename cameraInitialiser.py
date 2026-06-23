import serial
ser = serial.Serial(
    port = "/dev/serial0", baudrate = 115200, parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE, timeout=1)
from time import sleep
from binascii import hexlify


def pbyte(data):
    # check if there are multiple bytes
    if len(str(data)) > 1:
        # make list all bytes given
        msg = list(data)
        # mark which item is being converted
        s = 0
        for u in msg:
            # convert byte to ascii, then encode ascii to get byte number
            u = hexlify(u)
            # make byte printable by canceling \x
            u = "\\x"+u
            # apply coverted byte to byte list
            msg[s] = u
            s = s + 1
        msg = "".join(msg)
    else:
        msg = data
        # convert byte to ascii, then encode ascii to get byte number
        msg = hexlify(u)
        # make byte printable by canceling \x
        msg = "\\x"+msg
    # return printable byte
    return msg
#ser.send(b"\x55\x43\x49\x12\x00\x10\x10\x46\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x58\x4d")

def cycle(data):
    ser.write(data)
    ret = ser.read(23)
    pbyte(ret)
    sleep(1)
    return ret

analogOutputModes = {b"\xBE\xAA\x03\x00\x00\x00\x00\x04\x49\xEB\xAA": "Analog off",
b"\xBE\xAA\x03\x00\x00\x01\x00\x35\x7a\xEB\xAA": "NTSC On",
b"\xBE\xAA\x03\x00\x00\x01\x01\x14\x6a\xEB\xAA": "Pal on",
b"": "Returned thing empty"
}

print("Sending/recieving serial data.")
vidDisabled = cycle(b"\x55\x43\x49\x12\x00\x10\x10\x4a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x96\x5b") # Disable video
videoToNTSC = cycle(b"\x55\x43\x49\x12\x00\x10\x10\x4a\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe3\x58") # Change video to NTSC?
displayMode = cycle(b"\x55\x43\x49\x12\x00\x10\x10\x8a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x3f\xca") # Get display mode
print("Serial code written")
print(analogOutputModes[displayMode])