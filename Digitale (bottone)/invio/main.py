# main.py -- put your code here!
from network import LoRa
import socket
import machine
import pycom
import time

# BOTTONE - INVIO

# Setup del socket
lora = LoRa(mode=LoRa.LORA, frequency=868000000) # 868 MHz
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)


# Ferma la pulsazione del led e lo spegne
pycom.heartbeat(False)
pycom.rgbled(0x000000)

# Configurazione PIN
adc = machine.ADC()
apin = adc.channel(pin='P16') # Pin fisico G3 (vedi pinout su slack)


while True:
	time.sleep(0.05) # Attesa per evitare errore "EAGAIN" -> Velocità di trasmissione troppo elevata
	if apin() > 500: # Conversione A/D, se il valore letto (mV) è maggiore di 500 allora accende led ed inizia invio dati
		s.send('1')
		pycom.rgbled(0xffffff) # Led acceso bianco
	else:
		s.send('0')
		pycom.rgbled(0x000000) # Led spento
