#!/usr/bin/python
# midipiano.py
# turn your PiPiano into a MIDI input device
# Author : Phil Howard @gadgetoid

# You need Python Midi to run this script
# Start here: https://github.com/vishnubob/python-midi
# Make sure you: sudo apt-get install swig libasound2-dev
# Then sudo python setup.py install
#
# Download, unzip and run sunvox-lofi from here: http://www.warmplace.ru/soft/sunvox/sunvox-1.7.5.zip
# You need to run mididumphw to learn the client name and port
# Then fire up this script, and cross your fingers!

# to run:
# sudo python midipiano.py

import RPi.GPIO as GPIO
import time
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import *
import thread
import os
import midi
import midi.sequencer

from socket import socket, AF_INET, SOCK_STREAM

MIDI_CLIENT = 128
MIDI_PORT = 0

class Piano():
    def __init__(self):
        self.seq = midi.sequencer.SequencerWrite()
        self.seq.subscribe_port(MIDI_CLIENT, MIDI_PORT)
        self.seq.start_sequencer()

    def note_on(self, note):
        self.seq.event_write(midi.NoteOnEvent(velocity=100, pitch=note, tick=0), False, False, True)
    def note_off(self, note):
        self.seq.event_write(midi.NoteOffEvent(velocity=100, pitch=note, tick=0), False, False, True)

    def on(self):
        return False

    def off(self):
        return False


piano = Piano()

buzzer_pin=26

GPIO.setmode(GPIO.BOARD)

GPIO.setup(buzzer_pin, GPIO.OUT)
myPWM=GPIO.PWM(buzzer_pin, 10)
myPWM.start(0)


scale=[
	midi.C_4, #262
	midi.D_4, #294
	midi.E_4, #330
	midi.F_4, #349
	midi.G_4, #392
	midi.A_4, #440
	midi.B_4, #494
	midi.C_5, #524
	midi.Cs_4,#277
	midi.Ds_4,#311
	midi.Fs_4,#370
	midi.Gs_4,#415
	midi.As_4 #466
]

myBus=""
if GPIO.RPI_REVISION == 1:
    myBus=0
else:
    myBus=1

mcp = Adafruit_MCP230XX(busnum = myBus, address = 0x20, num_gpios = 16)

i=0
while i<13:
    mcp.pullup(i,1)
    i=i+1
i=13
while i<16:
    mcp.config(i,0)
    i=i+1

def light(a,b,c):
    mcp.output(13,a)
    mcp.output(14,b)
    mcp.output(15,c)

def metronome():
    while True:
        light(1,0,0)
        time.sleep(0.5)
        light(0,1,0)
        time.sleep(0.5)
        light(0,0,1)
        time.sleep(0.5)

thread.start_new_thread(metronome, ())

last=[0,0,0,0,0,0,0,0,0,0,0,0,0]

while True:
    i=0
    while i<13:
        if mcp.input(i)!=last[i]:
            if mcp.input(i):
                piano.note_off(scale[i])
                print str(i) + ' off'
            else:
                piano.note_on(scale[i])
                print str(i) + ' on'
        last[i]=mcp.input(i)
        i=i+1
