#-*-coding:utf-8-*-
import RPi.GPIO as GPIO
import time
import bluetooth
import Adafruit_CharLCD as LCD
import json
from time import sleep
from datetime import datetime

#________________________________________________________________________________________#
#________________________Configuração da conexão bluetooth_______________________________#

bd_addr = "98:D3:31:40:14:9F" 
port    = 1
sock    = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))
data1    = ""

#________________________________________________________________________________________#
#________________________Configuração do servo motor (GPIO)______________________________#

servo_pin = 19

#Ajuste estes valores para obter o intervalo completo do movimento do servo
deg_0_pulse   = 0.5 
deg_180_pulse = 2.5
f             = 50.0

def set_angle(angle):
	duty = deg_0_duty + (angle/180.0)* duty_range
	pwm.ChangeDutyCycle(duty)

# Faca alguns calculos dos parametros da largura do pulso
period      = 1000/f
k           = 100/period
deg_0_duty  = deg_0_pulse*k
pulse_range = deg_180_pulse - deg_0_pulse
duty_range  = pulse_range * k

#Iniciar o pino gpio
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin,GPIO.OUT)
pwm = GPIO.PWM(servo_pin,f)
pwm.start(0)

arquivoDados = open("backup2.txt","a")
while 1:
	#data1 = ""
	try:
		#Recebe os dados do sensor de temperatura
		
		data1 += sock.recv(1024)
		
		#data = json.loads(data1)
		data_end = data1.find('\n')
		mensagem = ""
		mensagemBackup = ""
		

		if (data_end != -1):
			
			print str(len(data1))
			
			if (int(len(data1)) != 43):
				data1 = data1[data_end+1:]
				continue
			
			print str(len(data1))
			temp        = data1.split()
			temperatura = int(temp[2])
			
			print data1

			date = datetime.now()
			dt   = date.strftime("%d/%m/%Y %H:%M")

			mensagemBackup += (dt + ' - ' + data1)
			arquivoDados.write(mensagemBackup)
			print mensagemBackup
			
			
			if temperatura > 26:
				
				set_angle(0)
			
			else:
				
				set_angle(80)
				
			
			data1 = data1[data_end+1:]
			
	except KeyboardInterrupt:
		pwm.stop() 
		GPIO.cleanup()
		arquivoDados.close()
		sock.close()
		break

