#!/usr/bin/env python3
#-*-coding:utf-8-*-
import RPi.GPIO as GPIO
import time
import bluetooth
import platform
from time import sleep
from datetime import datetime
from weasyprint import HTML, CSS

def conectar():

        while True:
                
                print ("Tentando conectar...")
                
                try:
                        
                        bd_addr  = "B4:E6:2D:99:76:AB"
                        port     = 2
                        sock     = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                        sock.connect((bd_addr,port))

                        print ("Conectado!")
                        return sock
                except:
                        continue

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
	iden = getIdentificacao()
	relatorio += 'Relatorio_' + str(date['dia']) + '-' + str(date['mes']) + '-' + str(date['ano']) + '_'
	relatorio += str(date['hora']) + '-' + str(date['minuto']) + '-' + str(date['segundo']) + '_'
	relatorio += iden
	
	return relatorio
	
def getDate():
	date = datetime.now()
	dateTime = {
		'dia'     : date.strftime("%d"),
		'mes'     : date.strftime("%m"),
		'ano'     : date.strftime("%Y"),
		'hora'    : date.strftime("%H"),
		'minuto'  : date.strftime("%M"),
        'segundo' : date.strftime("%S"),
		'dt'      : date.strftime("%d/%m/%Y"),
        'ht'      : date.strftime("%H:%M:%S")
	}
	
	return dateTime

def geraRelatorio(html,name):
        pdf = HTML(string=html.encode('utf-8'))
        relatorio = 'Relatorios/' + name + '.pdf'
        result = pdf.write_pdf(relatorio, stylesheets=[CSS(string='''
        @page{
                size: A4;
                margin: 1cm;
        } 
        *{
                font-family:Verdana;       
        }
        #tabela{
                width:100%;
                border:solid 1px;
                text-align: center;
                border-collapse:collapse;
        }     
        #tabela tr{
                height:20px;
        }
        #tabela tr td:first-child, #tabela tr td:last-child{
                width:150px;
        }
        #tabela tbody tr:nth-child(odd){
                background: #d6d8d8;
        }
        #tabela .cabecalho1{
                text-align: left;
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
        }
        #tabela .cabecalho2{
                text-align: center;
                font-weight: bold;
                background:#747777;
                color: #ffffff;
                height:30px; 
                width: 33%;
        } 
        '''
        )])

        return result

def numeracao():
        arquivo = open("numeracao.txt","r")
        lista_aux  = arquivo.readlines()
        arquivo.close()
        lista = lista_aux[0].split()
        
        numero = int(lista[0])
        data_old = lista[1]
        data_atual = getDate()

        numero += 1

        if data_atual['dt'] != data_old:
                numero = 1
                
        if len(str(numero)) == 1:
                novo_numero = '0' + str(numero)
        else:
                novo_numero = str(numero)

        novo_valor_arquivo = novo_numero + ' ' + data_atual['dt'] + ' *'
        arquivo_escrita = open("numeracao.txt","w")
        arquivo_escrita.write(novo_valor_arquivo)
        arquivo_escrita.close()

        return novo_numero

def getIdentificacao():
        nome = platform.node()
        return nome

flag = 0

#-------------------------------------------------------------------------------#


def main():
        
	servo = configServo()

	pwm = configPinoGpio(servo['pino'],servo['frequencia'], 1)
	pwm.start(0)

	pulso = calcularPulso(servo['frequencia'], servo['pulso_0'], servo['pulso_180'])
	
	dados = ""

	html = '''
        <table id="tabela">
            <tbody>
                <tr class="cabecalho1" style="background: #f46242;height:40px;width: 100%">
                    <td colspan="2">Identificação:&nbsp;
        '''
	dadosDin = ""
	
	flag = 0

	qtd_registros = 0

	sock = conectar()

	while 1:

		try:
			dados += sock.recv(1024).decode()
			data_end = dados.find('\n')

			if (data_end != -1):
                                                
				temp        = dados.split()
				temperatura = float(temp[2])
				
				print (dados)

				dt = getDate()
				
				flag += 1
                                
				if flag == 1:
					relatorio = headerRelatorio()

				dadosDin += '<tr><td>' + str(dt['dt']) + '</td>'
				dadosDin += '<td>' + str(dt['ht']) + '</td>'
				dadosDin += '<td>' + str(temp[2]) + '</td>'
				dadosDin += '<td>' + str(temp[6]) + '</td>'
				dadosDin += '<td>' + str(temp[10]) + '</td></tr>'

				qtd_registros += 1                                              
                                        
				if qtd_registros == 30:

					identificacao = getIdentificacao()
					n_relatorio = numeracao()

					html += identificacao
					html += '</td><td colspan="2">Relatório: nº'
					html += n_relatorio
					html += '</td><td>Data:'
					html += str(dt['dt'])
					html += '''
					</td>     
					</tr><tr class="cabecalho2">
							<td>Data</td>
							<td>Horário</td>
							<td>°C</td>
							<td>Máx. °C</td>
							<td>Min. °C</td>
					</tr>
					'''
					html += dadosDin
					html += '''
								</tbody>
						</table>
						<div class="row" style="text-align: right;font-size: 11px; ">
								<p><i><u>ReportTemperature version:1.0.1</u></i></p>
						</div>
					'''

					if geraRelatorio(html,relatorio):
							print ('Falhou')
					else:
							print ('Sucesso')
					

					html = ""
					dadosDin = ""

					html = '''
					<table id="tabela">
							<tbody>
							<tr class="cabecalho1" style="background: #f46242;height:40px;width: 100%">
									<td colspan="2">Identificação:&nbsp;
					'''
					
					relatorio = headerRelatorio()
					qtd_registros = 0
                                
				if temperatura > 26:
						
					set_angulo(pwm, 15, pulso['taxa_0'], pulso['taxa_range'])
					#while dec_angulo > 15:
						#     set_angulo(pwm, 15, pulso['taxa_0'], pulso['taxa_range'])
						#    dec_angulo = dec_angulo-15
						#   sleep(1.5)
				
				else:
					set_angulo(pwm, 90, pulso['taxa_0'], pulso['taxa_range'])
                                        
			dados = dados[data_end+1:]
                                
		except KeyboardInterrupt:
                        
			print("Encerrando...")
			pwm.stop()
			configPinoGpio(servo['pino'], servo['frequencia'], 0)
			sock.close()
			sleep(5)
			
			break
	
if __name__== "__main__":
    main()
