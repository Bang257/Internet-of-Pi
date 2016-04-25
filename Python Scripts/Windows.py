#!/usr/bin/python

#https://code.google.com/p/python-weather-api/
#https://code.google.com/archive/p/python-weather-api/wikis/Examples.wiki#Weather.com

#https://medium.com/@edwardbenson/how-i-hacked-amazon-s-5-wifi-button-to-track-baby-data-794214b0bdd8
#http://raspberrypi.stackexchange.com/questions/7088/playing-audio-files-with-python

from scapy.all import *
import smtplib
import pywapi
import requests
import time
import winsound

MAGIC_FORM_URL = 'http://api.cloudstitch.io/' #change magic form URL to your account

timing = 0
start_Time = ""
curmin = -1
curhour = -1

def record_time():
	global timing
	global start_Time
	if timing==0:
		start_Time = time.strftime("%H:%M")
		data = {
		"Date": time.strftime("%Y/%m/%d"),
		"Start_Time": start_Time,
		"End_Time": 'X'
		}
		timing=1
		print ("Starting clock")
	elif timing==1:
		data = {
			"Date": time.strftime("%Y/%m/%d"),
			"Start_Time": start_Time,
			"End_Time": time.strftime("%H:%M")
		}
		timing=0
		print ("Stopping clock")
	requests.post(MAGIC_FORM_URL, data)
	print ("Time logged")
		
def weather():
	weather_com_result = pywapi.get_weather_from_weather_com('58072', units='imperial')
	weather_String = "Valley City - " + weather_com_result['current_conditions']['text']
	weather_String += " high=" + weather_com_result['forecasts'][0]['high']
	weather_String += " low=" + weather_com_result['forecasts'][0]['low']
	weather_String += " curr=" + weather_com_result['current_conditions']['temperature']
	weather_String += " feels like=" + weather_com_result['current_conditions']['feels_like']
	weather_String += " wind=" + weather_com_result['current_conditions']['wind']['text']
	weather_String += " at " + weather_com_result['current_conditions']['wind']['speed'] + "mph" 
	weather_String += " Precip=" + weather_com_result['forecasts'][0]['day']['chance_precip'] + "%"
	weather_String += " -Weather.com"
	print (weather_String)
	send_Mail(weather_String)
	
def send_Mail(msg):
	fromaddr = 'myemail@gmail.com' #Your from address
	toaddrs  = '12345678910@srtwireless.com' #your to address
	
	# Credentials
	username = 'myemail@gmail.com' #your gmail username
	password = 'password' #your gmail password

	# The actual mail send
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg)
	server.quit()
	print ("Mail sent")
	
def alarm():
	tme = time.strftime("%H")
	winsound.PlaySound("C:\\Users\\dallas.d.petersen\\Desktop\\SOAR Presentation\\Siren.wav", winsound.SND_FILENAME) #siren.wav path
	send_Mail('Help! I\'ve fallen and I can\'t get up')
		
def morningWeather():
#This block will send a weather text at 9:00 every morning automatically
	global curmin
	global curhour
  
	hour = int(time.strftime("%H"))
	min = int(time.strftime("%M"))
  
	if curmin != min: #prevent spamming messages multiple times per minute
		print("{}:{}".format(hour-12, min))
		curmin = min
		if hour == 9 and min >= 00 and curhour!=hour:
			weather()
			curhour = hour
		if hour>=10: #reset current hour after the hour ends..fixes a bug where it would not work two days in a row
			curhour = -1
		
def arp_display(pkt):
	morningWeather()

	if pkt[ARP].op == 1: #who-has (request)
		if pkt[ARP].psrc == '0.0.0.0': # ARP Probe
			if pkt[ARP].hwsrc == '74:75:48:e4:bb:da': # Hefty
				print ("Pushed Hefty - Sending weather message")
				weather()
			elif pkt[ARP].hwsrc == 'a0:02:dc:e7:35:7c': # Gatorade
				print ("Pushed Gatorade - Timelog")
				record_time()
			elif pkt[ARP].hwsrc == '74:75:48:e7:00:ae': # ON
				print ("Pushed ON - Running panic button")
				alarm()
			elif pkt[ARP].hwsrc == '74:c2:46:b4:29:b7': # G2
				print ("Pushed G2 - Running panic button")
				alarm()
			else:
				print ("ARP Probe from unknown device: " + pkt[ARP].hwsrc)

#print sniff(prn=arp_display, filter="arp", store=0, count=20) #program stops after 20 seconds
print (sniff(prn=arp_display, filter="arp", store=0))
