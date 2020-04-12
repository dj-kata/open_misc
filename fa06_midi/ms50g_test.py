#!/usr/bin/python
import pygame
import pygame.midi
import picamera
import time

pygame.init()
pygame.midi.init()

port_out  = 2
port_in  = 3

for id in range(pygame.midi.get_count()):
    print id
    print pygame.midi.get_device_info(id)

m_out  = pygame.midi.Output(port_out)
m_in  = pygame.midi.Input(port_in)

# to Editor mode
m_out.write_sys_ex(pygame.midi.time(), [0xF0, 0x52, 0x00, 0x58, 0x50, 0xF7])

last = pygame.midi.time()

try:
    while True:
        if m_in.poll():
            ev = m_in.read(10)
            if len(ev) > 0:
                if pygame.midi.time() - last > 200:
                    print "pedal!"
                    last= pygame.midi.time()
except KeyboardInterrupt:
    m_in.close()
    pygame.midi.quit()
    print( "quit!")
