""" LoPy Board OTAA
Lettura e invio temperatura da sensore DS18B20 a server TTN
"""

from network import LoRa
import socket
import binascii
import struct
import pycom
import time
from machine import Pin
from onewire import DS18X20, OneWire # https://github.com/pycom/pycom-libraries/blob/master/examples/DS18X20/
import custom_var # Soluzione momentanea per mantenere private le chiavi da GitHub

# Inizializza LoRa in modalità LORAWAN
lora = LoRa(mode=LoRa.LORAWAN)

# Parametri per autenticazione OTAA
# Chiavi fornite da console TTN
dev_eui = binascii.unhexlify(custom_var.dev_eui_code2) #0123456789ABCDEF
app_eui = binascii.unhexlify(custom_var.app_eui_code2) #0123456789ABCDEF
app_key = binascii.unhexlify(custom_var.app_key_code2) #0123456789ABCDEF0123456789ABCDEF

# Imposta i 3 canali di default alla stessa frequenza (must be before sending the OTAA join request)
# Non servirebbe con l'attivazione OTAA, inoltre su firmware 1.0.0.b1 getta l'errore "Missing argument(s) value"
lora.add_channel(index=0, frequency=868100000, dr_min=0, dr_max=5) # 868.1 MHz
lora.add_channel(index=1, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(index=2, frequency=868100000, dr_min=0, dr_max=5)

# Connessione alla rete utilizzando OTAA
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# Disattivo la pulsazione del led per poterlo fissare durante la connessione al gateway
pycom.heartbeat(False)

while not lora.has_joined(): # Riprovo finché non trovo un gateway
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
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 4)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
# s.setblocking(True)

# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

time.sleep(1)

# DS18B20 cavo dati connesso al pin P10,
ow = OneWire(Pin('P10')) # G17 dell'Expansion Board
sens = DS18X20(ow) # Inizializza sensore

while True:
	sens.start_conversion() # Bisogna attendere almeno un secondo dopo questa istruzione
	time.sleep(1)
	data = sens.read_temp_async() # Leggo la temperatura
	try: # Errore su format di un valore None se non è collegato un sensore
		print("{} --> {:.1f}".format(round(data, 2), data)) # Arrotonda a due cifre decimali massime dopo la virgola
		net = (str("{:.1f}".format(data))).encode('utf-8') # Codifica la stringa da inviare in bytes
		s.send(net) # Finalmente invia
		pycom.heartbeat(True)
		time.sleep(1)
		rx, port = s.recvfrom(256) # Dovrebbe riconoscere una risposta -> solo se socket.setblocking(True)
		if rx: print('Received: {}, on port: {}'.format(rx, port))
	except:
		# Non è riuscito a leggere la temperatura
		print("Sensore non collegato!")
		pycom.heartbeat(False) # Necessario per impostare un colore led custom
		pycom.rgbled(0xff0000) # Imposto led rosso per informazione visiva
	time.sleep(298) # 5 minutis
