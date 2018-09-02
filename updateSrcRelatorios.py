#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyudev
from time import sleep
import os, usb
import re
import shutil

# função para encontrar os arquivos
def find_files(pattern, path):
    for path, dirs, files in os.walk(path):
        for filename in files:
            full_file_name = os.path.join(path, filename)
            match = re.match(pattern, full_file_name)
            if match:
                yield full_file_name

# função para copiar os arquivos encontrados 
def copy_files(pattern, src_path, dest_path):
    for full_file_name in find_files(pattern, src_path):
        print(full_file_name)

        try:
            shutil.copy(full_file_name, dest_path)
        except IOError:
            pass
    return

def detectaUSB(context):

    jaCopiou = False
    dif = 0

    while 1:
        dif += 1
        try:
            device = pyudev.Device.from_path(context, '/sys/block/sda/sda1')
            print("Dispositivo conectado " + str(dif))
            if jaCopiou == False:
                copy_files('.', '/home/pi/Desktop/workspace/Relatorios', '/media/pi/CARLOS/tmp/Relatorios/')
                jaCopiou = True
            sleep(5)
        except:
            print("Dispositivo não conectado" + str(dif))
            jaCopiou = False
            sleep(5)
    return

if __name__ == '__main__':

    context = pyudev.Context()
    detectaUSB(context)


# monitor = pyudev.Monitor.from_netlink(context)
# monitor.filter_by('block')
# def log_event(action, device):
#     if 'ID_FS_TYPE' in device:
#         with open('filesystems.log', 'a+') as stream:
#             print('{0} - {1}'.format(action, device.get('ID_FS_LABEL')), file=stream)

# observer = pyudev.MonitorObserver(monitor, log_event)
# observer.start()
