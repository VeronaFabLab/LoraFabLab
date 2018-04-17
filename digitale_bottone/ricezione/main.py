"""
Ricezione lettura pressione di un bottone (0|1) in frequenza "locale" 
inviata da un'altra board LoPy con accensione di led e buzzer
--RICEZIONE
"""

from network import LoRa
import socket
import time
import pycom
from machine import PWM

# PWM per output buzzer
pwm= PWM(0, frequency= 3000)
buzzer= pwm.channel(0, pin='G9', duty_cycle=0)

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
		buzzer.duty_cycle(0.5)
	elif s.recv(64) == b'0':
		pycom.rgbled(0x000000) # Led spento
		buzzer.duty_cycle(0)
