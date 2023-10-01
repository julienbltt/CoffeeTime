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

from machine import Pin
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

### GLOBAL VARIABLE ###
BUTTON_isPressed = False # FLAG
BUTTON_mutex = _thread.allocate_lock() # Mutex of button state global variable.

# Function thread client.
def worker(*arg):
    global BUTTON_isPressed, BUTTON_mutex

    Socket_client = arg[0]
    isConnect = True

    while(isConnect):
        if BUTTON_isPressed:
            BUTTON_mutex.acquire()
            BUTTON_isPressed = False
            BUTTON_mutex.release()
            Socket_client.send("coffee-time".encode())
    
    Socket_client.close()
    
    _thread.exit(0)

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
    global BUTTON_isPressed, BUTTON_mutex
    BUTTON_mutex.acquire()
    BUTTON_isPressed = True
    BUTTON_mutex.release()

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
        
        # Creat worker for client socket
        Worker_threadId = _thread.start_new_thread(worker, (Socket_Client,))
        dprint("[SERVER] > Worker ", Worker_threadId, " : is up.")
        