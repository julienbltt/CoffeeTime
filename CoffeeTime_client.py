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

DEBUG = True
if(DEBUG):
    def dprint(*args, **kwargs):
        print(*args, **kwargs)

HOST = "192.168.1.66"
PORT = 5169

def Toast_Display():
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    PATH_ICO = os.path.join(ROOT_PATH, "coffee_time.ico")

    toast('COFFEE TIME !', '', image=PATH_ICO )


if __name__ == "__main__":
    # Create client socket.
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dprint("[CLIENT] > Client socket created.")

    # Connect to server socket.
    try:
        socket_client.connect((HOST, PORT))
    except socket.error as msg:
        dprint("[CLIENT] ERROR : ", msg)
        dprint("[CLIENT] > Shutdown")
        sys.exit(1)

    dprint("[CLIENT] > Client socket connected.")

    while True:
        # Receive data from server socket.
        data = socket_client.recv(254).decode()
        dprint(data)
        if not data:
            dprint("[CLIENT] > Server down.")
            break
        else:
            dprint("[CLIENT] > RECV : ", data)

        if data == "coffee-time":
            Toast_Display()
            dprint("[CLIENT] > Toast displayed.")