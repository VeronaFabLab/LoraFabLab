from network import LoRa
import socket
import time
import pycom

# BOTTONE - RICEZIONE

# Setup del socket
lora = LoRa(mode=LoRa.LORA, frequency=868000000) # 868 MHz
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

# Ferma la pulsazione del led e lo spegne
pycom.heartbeat(False)
pycom.rgbled(0x000000)

while True:
    if s.recv(64) == b'1':
        pycom.rgbled(0xffffff) # Led acceso bianco
    elif s.recv(64) == b'0':
        pycom.rgbled(0x000000) # Led spento
