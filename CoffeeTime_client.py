"""
Client script for windows user.
---
Project : Coffee Time
File : CoffeeTime_client.py
Author : BALDERIOTTI Julien
Create : 26/09/2023
MàJ : 26/09/2023
"""
import os
from win11toast import toast
import socket
import sys
import ipaddress
import threading
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import darkdetect

DEBUG = True
if(DEBUG):
    def dprint(*args, **kwargs):
        print(*args, **kwargs)

### Global variables
IP = ""
PORT = 5169
if darkdetect.isDark():
    ICO = "coffee_time_white.ico"
else:
    ICO = "coffee_time_black.ico"

###Exit Handler ###
def Exit_IRQHandle(icon, item):
    socket_client.send("end".encode())
    socket_client.close()
    icon.stop()
    sys.exit(0)

### Network scanner ###
# WORKER
def NetworkScanner_Worker(ip):
    global IP
    try:
        host = socket.gethostbyaddr(str(ip))
        dprint(f"[WORKER] > IP: {ip} - Répond - Nom d'appareil: {host[0]}")
        if host[0] == "mpy-esp32s2":
            IP = str(ip)
    except (socket.herror, socket.gaierror):
        pass

# Main scanner function
def NetworkScanner_FindServerIP():
    network = socket.gethostbyname(socket.gethostname())[:-2] + "0/24" # Réseau de la passerelle.
    ip_network = ipaddress.IPv4Network(network, strict=False)

    threads = []

    for ip in ip_network.hosts():
        thread = threading.Thread(target=NetworkScanner_Worker, args=(ip,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def ColorTheme_IRQHandler(color):
    global ICO
    dprint("[CLIENT] > Windows swap to", color, "theme.")
    if color == "Dark":
        dprint("[CLIENT] > Is dark!")
        ICO = "coffee_time_white.ico"
    elif color == "Light":
        dprint("[CLIENT] > Is light!")
        ICO = "coffee_time_black.ico"

def Toast_Display():
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    PATH_ICO = os.path.join(ROOT_PATH, ICO)

    toast('COFFEE TIME !', '', image=PATH_ICO )



if __name__ == "__main__":
    global socket_client

    # Create client socket.
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dprint("[CLIENT] > Client socket created.")

    # Scan network for find server IP
    dprint("[CLIENT] > Network scanning...")
    NetworkScanner_FindServerIP() # Init IP value with server ip address. (ESP32 module)
    dprint("[CLIENT] > Server ip find (", IP, ")")

    # Connect to server socket.
    try:
        socket_client.connect((IP, PORT))
    except socket.error as msg:
        dprint("[CLIENT] ERROR : ", msg)
        dprint("[CLIENT] > Shutdown")
        sys.exit(1)
    dprint("[CLIENT] > Client socket connected.")

    # Start listenning of systheme color theme switching
    Thread_ColorTheme = threading.Thread(target=darkdetect.listener, args=(ColorTheme_IRQHandler,))
    Thread_ColorTheme.daemon = True
    Thread_ColorTheme.start()

    IconTaskBar = icon('coffeetime', Image.open("./coffee.ico"), title="CoffeeTime", menu=menu(item('Exit', Exit_IRQHandle)))
    IconTaskBar.run_detached()
    dprint("[CLIENT] > Icon in notification task bar is launched.")

    dprint("[CLIENT] > Start main loop.")
    while True:
        # Receive data from server socket.
        data = socket_client.recv(254).decode()          
        dprint("[CLIENT] > RECV : ", data)
        if data == "coffee-time":
            Toast_Display()
            dprint("[CLIENT] > Toast displayed.")