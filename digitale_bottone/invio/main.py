"""
Invio lettura pressione di un bottone (0|1) in frequenza "locale" e
ricezione su un'altra board LoPy con accensione di led e buzzer
--INVIO
"""

from network import LoRa
import socket
import pycom
import time
from machine import Pin

# Setup del socket
lora = LoRa(mode=LoRa.LORA, frequency=868000000) # 868 MHz
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

pycom.heartbeat(False) # Ferma la pulsazione del led e lo spegne
pycom.rgbled(0x000000)

# Configurazione PIN
#adc = machine.ADC()
#apin = adc.channel(pin='P16') # Pin fisico G3 (vedi pinout su slack)
p_in = Pin("P10", mode=Pin.IN, pull=Pin.PULL_UP) # Pin G17 Expansion Board

while True:
	time.sleep(0.05) # Attesa per evitare errore "EAGAIN" -> Velocità di trasmissione troppo elevata
	if (p_in() == 0): # Conversione A/D, se il valore letto (mV) è maggiore di 500 allora accende led ed inizia invio dati
		s.send('1')
		pycom.rgbled(0xffffff) # Led acceso bianco
	else:
		s.send('0')
		pycom.rgbled(0x000000) # Led spento
