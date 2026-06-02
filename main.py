import pySerial as ser

cameraControl = ser.serial.Serial(port = "/dev/ttyS0", baudrate = 115200)