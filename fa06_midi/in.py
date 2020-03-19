#!/usr/bin/python
import pygame
import pygame.midi
import picamera
import time

pygame.init()
pygame.midi.init()

port_in  = 3

for id in range(pygame.midi.get_count()):
    print id
    print pygame.midi.get_device_info(id)

m_in  = pygame.midi.Input(port_in)

try:
    while True:
        if m_in.poll():
            ev = m_in.read(10)
            if len(ev) > 0:
                print str(ev)
except KeyboardInterrupt:
    m_in.close()
    pygame.midi.quit()
    print( "quit!")
