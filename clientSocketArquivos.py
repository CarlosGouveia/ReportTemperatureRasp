#!/usr/bin/env python3

import socket
import sys
import os, usb
import re

def buscaArquivos(path):

    for _, _, arquivo in os.walk(path):
        pass
    
    return arquivo

def enviaArquivos(caminho_pasta):
    
    lista_arquivos = buscaArquivos(caminho_pasta)
    print(lista_arquivos)

    for arquivo in lista_arquivos:

        try:
            s = socket.socket()
            s.connect(("192.168.42.232",8001))

            s.send((arquivo).encode())
            
            f = open (caminho_pasta + '/' + str(arquivo), "rb")
            l = f.read(4096)

            while (l):
                s.send(l)
                l = f.read(4096)

            f.close()
            s.close()
        except:

            s.close()
            continue
    
    return

def main():

    caminho_pasta = '/home/pi/Desktop/workspace/Relatorios'
    enviaArquivos(caminho_pasta)

if __name__ == '__main__':
    main()