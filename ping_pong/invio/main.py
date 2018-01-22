from network import LoRa
import socket
import time
import pycom

''' PING - INVIO '''

# Setup del socket
lora = LoRa(mode=LoRa.LORA, frequency=868000000) # 868 MHz
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

a = 0
while True:
	time.sleep(5)
	o = 'Ping-{}'.format(a)
	s.send(o)
	print(o)
	a += 1
