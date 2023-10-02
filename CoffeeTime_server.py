"""
Server script for ESP32
---
Project : Coffee Time
File : CoffeeTime_server.py
Author : BALDERIOTTI Julien
Create : 26/09/2023
MàJ : 26/09/2023
"""

import socket
import _thread

from machine import Pin, Timer
import network

DEBUG = True
if(DEBUG):
    def dprint(*args, **kwargs):
        print(*args, **kwargs)
    def Button_test():
        global BUTTON_isPressed
        BUTTON_isPressed = True
else:
    def dprint(*args, **kwargs):
        pass
    def Button_test(socket):
        pass

HOST = ""
PORT = 5169  # Port to listen on (non-privileged ports are > 1023)

SSID = "Maison_ALDO" 
KEY = "#Y2s&O-K,\"=qx7DL"

### GPIO ###
BUTTON_PIN = 10

### Timer ###
timer1 = Timer(1)

### GLOBAL VARIABLE ###
Timer_UpdateEvent = False
SocketClient_Connected = []

def Timer1_IRQHandler(timer):
    global Timer_UpdateEvent
    Timer_UpdateEvent = True

# Function thread client.
def worker(*arg):
    global SocketClient_Connected
    
    Socket_client = arg[0]
    
    dprint("[SERVER] > Worker <", _thread.get_ident(), "> is up.")
    
    while(True):
        try:
            data = Socket_client.recv(254).decode()
        except OSError:
            break
        if data == "end":
            break
    
    Socket_client.close()
    SocketClient_Connected.remove(Socket_client)
    dprint("[SERVER] > Worker <", _thread.get_ident(), "> is close.")
    _thread.exit()

def WLAN_Init():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        dprint("[WLAN] > Connecting to network...")
        wlan.connect(SSID, KEY)
        while not wlan.isconnected():
            pass
    dprint("[WLAN] > Network config : ", wlan.ifconfig())
    return wlan.ifconfig()[0]

def EXT_IRQHandler(pin):
    global Timer_UpdateEvent, SocketClient_Connected
    timer1.init(period=250, callback=Timer1_IRQHandler)
    if Timer_UpdateEvent:
        timer1.deinit()
        Timer_UpdateEvent = False
        
        # Send a toat notification for all client connected
        for socketclient in SocketClient_Connected:
            socketclient.send("coffee-time".encode())
        dprint("[SERVER] > Send toast notification.")

def GPIO_Init():
    button = Pin(BUTTON_PIN, Pin.IN)
    button.irq(trigger=Pin.IRQ_RISING, handler=EXT_IRQHandler)

if __name__ == "__main__":    
    GPIO_Init() # Init GPIOs
    HOST = WLAN_Init() # Conexion to network

    # Create server socket
    Socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dprint("[SERVER] > Server socket create.")

    # Bind server socket
    Socket_server.bind((HOST, PORT))
    dprint("[SERVER] > Server socket binded.")

    # Listen connection at server socket
    Socket_server.listen(20)
    dprint("[SERVER] > Server socket listenning...")

    # Infinit loop
    while True:
        # Accept client socket
        Socket_Client, Socket_ClientAddr = Socket_server.accept()
        dprint("[SERVER] > Client join server : ", end="")
        dprint("ADDR : ", Socket_ClientAddr[0], "; PORT : ", Socket_ClientAddr[1])
        
        # Add socket client on list of connected
        SocketClient_Connected.append(Socket_Client)
        
        # Creat worker for client socket
        _thread.start_new_thread(worker, (Socket_Client,))
        