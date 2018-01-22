""" LoPy Board OTAA esempio compatibile con LoPy Nano Gateway """

from network import LoRa
import socket
import binascii
import struct
import time
import custom_var

# Inizializza LoRa in modalità LORAWAN.
lora = LoRa(mode=LoRa.LORAWAN)

# Parametri per autenticazione OTAA
dev_eui = binascii.unhexlify(custom_var.dev_eui_code.replace(' ','')) # these settings can be found from TTN
app_eui = binascii.unhexlify(custom_var.app_eui.replace(' ','')) # these settings can be found from TTN
app_key = binascii.unhexlify(custom_var.app_key_code.replace(' ','')) # these settings can be found from TTN

# set the 3 default channels to the same frequency (must be before sending the OTAA join request)
# Non serve con OTAA
#lora.add_channel(index=0, frequency=868100000, dr_min=0, dr_max=5)
#lora.add_channel(index=1, frequency=868100000, dr_min=0, dr_max=5)
#lora.add_channel(index=2, frequency=868100000, dr_min=0, dr_max=5)

# join a network using OTAA
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# Aspetto finché non trovo un gateway
while not lora.has_joined():
    time.sleep(2.5)
    print('Gateway... dove sei?')

# remove all the non-default channels
#for i in range(3, 16):
#    lora.remove_channel(i)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket non-blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)

# send some data
#s.send(bytes([0x01, 0x02, 0x03]))

# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

for i in range(50):
	s.send(b'PKT #' + bytes([i]))
	time.sleep(4)
	rx = s.recv(64)
	if rx:
		print(rx)
		time.sleep(6)

#https://github.com/pycom/pycom-libraries/blob/master/examples/loraNanoGateway/node/main.py
