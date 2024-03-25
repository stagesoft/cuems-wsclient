from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

import os


import asyncio
import subprocess

import time
import os

INPORT = 6007
OUTPORT = 6006
IP = "0.0.0.0"
#IP = "192.168.1.12"
SERVER_IP = "192.168.1.1"

project_1 = "a56bd00e-d71b-11ee-b5f5-111111111111"

project_2 = "a56bd00e-d71b-11ee-b5f5-222222222222"

project_3 = "a56bd00e-d71b-11ee-b5f5-333333333333"




project_id_file = '/etc/cuems/project_id'

def shutdown_handler(addr, *args):
    
    print("received shutdown")
    subprocess.Popen('/usr/local/bin/shutdown.sh', shell=True)
    

def program_change_handler(addr, *args):

    print(f"received program id: {args[0]}")

    if args[0] != None:
        project_num = args[0]


    if project_num == 1:
            project_id = project_1
    elif project_num == 2:
            project_id = project_2
    elif project_num == 2:
            project_id = project_3


    try:

        with open(project_id_file, "w") as my_file:
            my_file.write(project_id)
    except FileNotFoundError as e:
        print(f"Something else went wrong {e}")

    time.sleep(1)
    print("received program change")
    subprocess.Popen('/usr/local/bin/shutdown.sh', shell=True)

def default_osc_handler(addr, *args):
    print(f'Recibido mensaje OSC no reconocido : direccion -> {addr} | datos -> {args}')


 # creamos nuestro dispatcher de mensajes OSC
dispatcher = Dispatcher()

  # asignamos manejadores en rutas de formato "/game_#" para los juegos
dispatcher.map(f"/afrucat/shutdown", shutdown_handler)

  # asignamos manejador para los mensajes de taquilla
dispatcher.map(f"/afrucat/program", program_change_handler)

 # asignamos manejador por defecto
dispatcher.set_default_handler(default_osc_handler)




server = osc_server.ThreadingOSCUDPServer(
        (IP, INPORT), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()