import serial
import time
import numpy as np
import math
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


try: ser = serial.Serial(port='/dev/ttyAMC0', baudrate = 4800) #raises exception if device is not found
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

while True:
    try:
        # Implementation taken from
        # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Quaternion_to_angles_(in_ZYX_sequence)_conversion
        quat = np.array([*bno.quaternion])
        print(quat, end=" : ")
        mag = np.linalg.norm(quat)
        unit = quat/mag
        a = 2*math.acos(unit[3]) # Simple angle
        alpha = math.sin(a/2)
        rot = np.degrees(np.acos(unit/alpha)[:3])
        print(rot)

        time.sleep(0.5)
    except Exception as e:
        print(e, " has occured.")
    