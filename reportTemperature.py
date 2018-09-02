#-*-coding:utf-8-*-
import RPi.GPIO as GPIO
import time
import bluetooth
import Adafruit_CharLCD as LCD
import json
from time import sleep
from datetime import datetime

bd_addr = "98:D3:31:40:14:9F" 
port    = 1
sock    = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))

def configPinoGpio(pino_servo, frequencia, status):
	
	if status:
	
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pino_servo,GPIO.OUT)
		pwm = GPIO.PWM(pino_servo,frequencia)
	
		return pwm
	
	else:	
		
		GPIO.cleanup()
		return
	

def configServo():
	
	listaConfigServo = {
		'pino'      : 19,
		'pulso_0'   : 0.5,
		'pulso_180' : 2.5,
		'frequencia': 50.0
	}
		
	return listaConfigServo
	

def calcularPulso(frequencia, pulso_0, pulso_180):
	
	periodo     = 1000/frequencia
	k           = 100/periodo
	taxa_0      = pulso_0 * k
	pulso_range = pulso_180 - pulso_0
	taxa_range  = pulso_range * k
	
	result = {
		'taxa_0'     : taxa_0,
		'taxa_range' : taxa_range
	}
	
	return result

def set_angulo(pwm, angulo, taxa_0, taxa_range):
	taxa = taxa_0 + (angulo/180.0)* taxa_range
	pwm.ChangeDutyCycle(taxa)
	

def headerRelatorio():
	
	relatorio = ""
	date = getDate()
	relatorio += 'Relatorio_' + str(date['dia']) + '-' + str(date['mes']) + '-' + str(date['ano']) + '_'
	relatorio += str(date['hora']) + '-' + str(date['minuto']) + '\n'
	
	return relatorio
	
def getDate():
	date = datetime.now()
	dateTime = {
		'dia'    : date.strftime("%d"),
		'mes'    : date.strftime("%m"),
		'ano'    : date.strftime("%Y"),
		'hora'   : date.strftime("%H"),
		'minuto' : date.strftime("%M"),
		'dt'     : date.strftime("%d/%m/%Y %H:%M")
	}
	
	return dateTime

flag = 0

#-------------------------------------------------------------------------------#
servo = configServo()

pwm = configPinoGpio(servo['pino'],servo['frequencia'], 1)
pwm.start(0)

pulso = calcularPulso(servo['frequencia'], servo['pulso_0'], servo['pulso_180'])

dados = ""

flag = 0

while 1:

	try:
		#Recebe os dados do sensor de temperatura
		
		dados += sock.recv(1024)
		data_end = dados.find('\n')
		
		mensagem = ""
		mensagemBackup = ""
		

		if (data_end != -1):
					
			if (int(len(dados)) != 43):
				
				dados = dados[data_end+1:]
				continue
			
			temp        = dados.split()
			temperatura = int(temp[2])
			
			print dados

			dt = getDate()
			
			flag += 1
			
			if flag == 1:
				
				tempoAnterior = dt['minuto']
				
				relatorio = headerRelatorio()
				rel_arq   = relatorio + 'txt'
				
				arquivoDados = open(rel_arq,"a")
				
				arquivoDados.write(relatorio)
				
			
			tempoAtual = dt['minuto']
			
			if tempoAtual != tempoAnterior:
				
				arquivoDados.close()
				
				relatorio = headerRelatorio()
				rel_arq   = relatorio + '.txt'
				
				arquivoDados = open(rel_arq,"a")
				
				arquivoDados.write(relatorio)
				
				tempoAnterior = tempoAtual

			mensagemBackup += (dt['dt'] + ' - ' + dados)
			arquivoDados.write(mensagemBackup)
			
			if temperatura > 26:
				
				set_angulo(pwm, 0, pulso['taxa_0'], pulso['taxa_range'])
			
			else:
				
				set_angulo(pwm, 80, pulso['taxa_0'], pulso['taxa_range'])
				
			
			dados = dados[data_end+1:]
			
	except KeyboardInterrupt:
		
		pwm.stop()
		configPinoGpio(servo['pino'], servo['frequencia'], 0)
		arquivoDados.close()
		sock.close()
		
		break

