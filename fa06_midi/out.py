#!/usr/bin/python
import pygame
import pygame.midi
import picamera
import time

pygame.init()
pygame.midi.init()

port_out = 2

out = pygame.midi.Output(port_out)
out.set_instrument(0)

def on(key,vel):
    out.note_on(key,vel)
def off(key,vel):
    out.note_off(key,vel)
def send_sysex(address, data): # address[4]
    wdt = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x77, 0x12]
    for a in address:
        wdt.append(a)
    wdt.append(data)
    tmp = (sum(address) + data) % 128
    chksum = 128 - tmp
    wdt.append(chksum)
    wdt.append(0xF7)
    out.write_sys_ex(pygame.midi.time(), wdt)
def wobble(val):
    send_sysex([0x19,0x01,0x20,0x1f], val)
    send_sysex([0x19,0x01,0x21,0x1f], val)
#out.close()
