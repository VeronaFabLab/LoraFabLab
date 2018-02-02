""" LoPy Board OTAA - LoPy Nano Gateway """

from network import LoRa
import socket
import binascii
import struct
import pycom
from machine import Pin
from onewire import OneWire, DS18X20 # https://github.com/pycom/pycom-libraries/blob/master/examples/DS18X20/
import time
import custom_var # Per nascondere chiavi da GitHub

# Inizializza LoRa in modalità LORAWAN.
lora = LoRa(mode=LoRa.LORAWAN)

# Parametri per autenticazione OTAA
# Chiavi fornite da console TTN
dev_eui = binascii.unhexlify(custom_var.dev_eui_code.replace(' ', '')) # Non necessaria con OTAA (?)
app_eui = binascii.unhexlify(custom_var.app_eui_code.replace(' ', ''))
app_key = binascii.unhexlify(custom_var.app_key_code.replace(' ', ''))

# Imposta i 3 canali di default alla stessa frequenza (must be before sending the OTAA join request)
# Non servirebbe con l'attivazione OTAA, inoltre su firmware 1.0.0.b1 getta l'errore "Missing argument(s) value"
lora.add_channel(index=0, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(index=1, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(index=2, frequency=868100000, dr_min=0, dr_max=5)

# Connessione alla rete utilizzando OTAA
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# Disattivo la pulsazione del led per poterlo fissare durante la connessione al gateway
pycom.heartbeat(False)
# Aspetto finché non trovo un gateway
while not lora.has_joined():
	time.sleep(2.5)
	print('Gateway... dove sei?')
	pycom.rgbled(0x7f7f00) # Giallo

# Connessione avvenuta, riattivo la normale pulsazione blu
pycom.heartbeat(True)

# Rimuovo tutti i canali non-predefiniti
for i in range(3, 16):
    lora.remove_channel(i)

# Creo un socket LoRa
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 4) # 5

# make the socket non-blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
#s.setblocking(True)

# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

time.sleep(2)

#DS18B20 data line connected to pin P10
ow = OneWire(Pin('P10'))
temp = DS18X20(ow)

while True:
	temp.start_conversion() # Bisogna attendere almeno un secondo dopo questa istruzione
	time.sleep(1)
	data = temp.read_temp_async() # Leggo la temperatura
	print("{} --> {:.1f}".format(round(data,2), data)) # Arrotondo a due cifre decimali massime dopo la virgola
	net = ("{:.1f}".format(str(data))).encode('utf-8') # Preparo la stringa da inviare
	s.send(net)
	time.sleep(4)
	rx, port = s.recvfrom(256) # Dovrebbe riconoscere una risposta dal gateway (?)
	if rx:
		print('Received: {}, on port: {}'.format(rx, port))
	time.sleep(295)

"""
for i in range(100):
    pkt = ('PKT #' + str(i)).encode('utf-8')
    print('Sending:', pkt)
    s.send(pkt)
    time.sleep(4)
    rx, port = s.recvfrom(256)
    if rx:
        print('Received: {}, on port: {}'.format(rx, port))
    time.sleep(6)
"""

# https://github.com/pycom/pycom-libraries/blob/master/examples/loraNanoGateway/node/main.py
# https://www.thethingsnetwork.org/docs/devices/lopy/usage.html#register-your-device-eui
# https://docs.pycom.io/chapter/tutorials/lopy/lorawan-nano-gateway.html
# https://www.thethingsnetwork.org/docs/devices/bytes.html
# https://www.thethingsnetwork.org/wiki/LoRaWAN/Duty-Cycle#duty-cycle_maximum-duty-cycle
