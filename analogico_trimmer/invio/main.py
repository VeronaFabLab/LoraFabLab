"""
Invio di un valore letto da trimmer in frequenza "locale"
e ricezione su una altra board LoPy con regolazione dinamica
del led
--INVIO
"""

from network import LoRa
import socket
import machine
import pycom
import time

lora = LoRa(mode=LoRa.LORA, frequency=868000000) # 868 MHz
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

pycom.heartbeat(False) # Disattiva la pulsazione del led e...
pycom.rgbled(0x000000) # ...lo spegne

adc = machine.ADC()
apin = adc.channel(pin='P16') # Pin G3 Expansion Board

def map_voltage(voltage):
	return ((voltage // 64) * 0x111111)

while True:
	time.sleep(0.5) # Attesa per evitare errore EAGAIN -> Velocità di trasmissione troppo elevata
	rgb_value = map_voltage(apin())
	pycom.rgbled(rgb_value) # Imposta colore led
	s.send(str(rgb_value)) # Invia il valore
	print(apin())
