from __future__ import absolute_import, division, print_function, unicode_literals
import serial
import time
import numpy as np
import math
from geopy import distance
import pi3d
# From https://github.com/henriberisha/gps_location/blob/main/gps.py
"""
def get_longitude(in_long, hemisphere):
	if in_long == '':
		print("LONGITUDE: no GPS lock")
	else:
		index_decimal = (-1) * (len(in_long) - in_long.index(".")) #getting the negative index of '.' decimal point
  
   		#splitting the entry using the negative index found earlier
		minute = int(in_long[index_decimal - 2 : index_decimal])
		degree = int(in_long[: index_decimal -2 ])
		seconds = round(float(in_long[index_decimal:])*60)
		print("LONGITUDE: {}°{}'{}{}  {}".format(degree, minute, seconds, '"', hemisphere))

def get_latitude(in_lat, hemisphere):
	if in_lat == '':
		print("LATITUDE: no GPS lock")	
	else:
		index_decimal = (-1) * (len(in_lat) - in_lat.index("."))

		minute = int(in_lat[index_decimal - 2 : index_decimal])
		degree = int(in_lat[: index_decimal -2 ])
		seconds = round(float(in_lat[index_decimal:])*60)
		print("LATITUDE: {}°{}'{}{}  {}".format(degree, minute, seconds, '"', hemisphere))


try:  #raises exception if device is not found
except:
	print("USB_GPS device not found at /'dev/ttyUSB0'\n"
	      "Device may not be plugged, or mapped at different file under '/dev' directory")
	exit()

while 1:
   
   try: x = ser.readline() #device may disconnect and no read will be possible
   except: 
   	print("USB_GPS device disconnected")
   	exit()
   
   try: data = x.decode('utf-8')  #if byte input cannot be decoded
   except: continue
   
   #if we have a successful read, only $GPGAA NMEA_sentence is of interest in this script
   sentence = data.split(',')
   
   if sentence[0] == '$GPGGA':
   	if sentence[1] == '':
   		print("GPS device connected but no satellite lock acquired")
   	else:
   		#printing local time from the device
   		local = time.strftime("%H:%M:%S", time.localtime())
	   	print("LOCAL/THIS DEVICE TIME:", local)
	   	
	   	#reading and calculating time from the gps
   		gps_time = int(sentence[1][:6])
	   	hours = int(gps_time / 10000)
   		gps_time = gps_time % 10000
	   	minutes = int(gps_time / 100)
	   	seconds = gps_time % 100
   	
	   	if hours < 10: hours = '0'+str(hours)
	   	if minutes < 10: minutes = '0'+str(minutes)
	   	if seconds < 10: seconds = '0'+str(seconds)
	   	print("GPS TIME: {}:{}:{} UTC".format(hours, minutes, seconds))
	   	
	   	#printing latitude and longitude
   		get_latitude(sentence[2], sentence[3])
   		get_longitude(sentence[4], sentence[5])
   		print("\n")
   ser.flush()
"""

import board
import busio

from adafruit_bno08x import (
	BNO_REPORT_ACCELEROMETER,
	BNO_REPORT_GYROSCOPE,
	BNO_REPORT_MAGNETOMETER,
	BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
bno = BNO08X_I2C(i2c)

bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

def quatToEuler(quaternion):
	mag = np.linalg.norm(quaternion)
	unit = quaternion/mag
	a = 2*math.acos(unit[3]) # Simple angle
	alpha = math.sin(a/2)
	return np.degrees(np.acos(unit/alpha)[:3])


DISPLAY = pi3d.Display.create(w=800, h=500, frames_per_second=50, background=(0.1, 0.1, 0.0, 0.0),
	display_config=pi3d.DISPLAY_CONFIG_HIDE_CURSOR | pi3d.DISPLAY_CONFIG_MAXIMIZED, use_glx=True)
cam = pi3d.Camera()
font = pi3d.Font("fonts/FreeSans.ttf", color="#FF8010")
string2 = pi3d.String(camera=CAMERA2D, is_3d=False, font=font, string=fps, 
	x=-DISPLAY.width / 2 + 200, y=DISPLAY.height / 2 - 75, z=1.0)

cam2D = pi3d.Camera(is_3d=False)
cube = pi3d.Cuboid(w = 10, h = 5, l = 20, x = 30)
mykeys = pi3d.Keyboard()
rot = [0,0,0]
last_tm = 0
while DISPLAY.loop_running():
	try:
		rot = quatToEuler(bno.quaternion)
		print(rot)
		# Implementation taken from
		# https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Quaternion_to_angles_(in_ZYX_sequence)_conversion
	except Exception:
		rot = last
	cube.rotate(*rot)
	cube.draw()

	# From https://github.com/paddywwoof/pi3d_book/blob/master/programs/strings01.py
	tm = time.time()
	fps = "{:6.2f}FPS".format(i / (tm - last_tm))
	string2.quick_change(fps)
	last_tm = tm
	string2.draw()

	k = mykeys.read()
	if k == 27:
		mykeys.close()
		DISPLAY.destroy()
		break
	last = rot

mykeys.close()
DISPLAY.destroy()

"""
import helpers

cameraControl = serial.Serial(
    port = "/dev/serial0", 
    baudrate = 115200, 
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE, 
    timeout=1
)

helpers.UARTController.sendCommand(cameraControl, "Mode", "Outline")
helpers.UARTController.sendCommand(cameraControl, "Save", "Parameter Save")
helpers.UARTController.sendCommand(cameraControl, "Pallet", "Aurora")
helpers.UARTController.sendCommand(cameraControl, "Save", "Parameter Save")
print("Done!")
"""