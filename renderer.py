import serial
import time
# From https://github.com/henriberisha/gps_location/blob/main/gps.py
try: ser = serial.Serial(port='/dev/ttyACM0', baudrate = 4800) #raises exception if device is not found
except:
	print("USB_GPS device not found at /'dev/ttyACM0'\n"
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
   		print(sentence[2], sentence[3])
   		print(sentence[4], sentence[5])
   		print("\n")
   ser.flush()