import pygame.midi
import picamera
import time

pygame.init()
pygame.midi.init()

port_out = 2
port_in  = 3

out = pygame.midi.Output(port_out)
m_in  = pygame.midi.Input(port_in)
out.set_instrument(0)

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

def part_on(p): # p:1-16
    addr = 0x3F + p
    send_sysex([0x18, 0x00, addr, 0x02], 0x01)
def part_off(p): # p:1-16
    addr = 0x3F + p
    send_sysex([0x18, 0x00, addr, 0x02], 0x00)

def is_hold(ev):
    ret = False
    if len(ev)>0:
        if ev[0][0] == [176,64,127,0]:
            ret = True
    return ret

def part_switch(parts):
    for i in range(1,17):
        if i in parts:
            part_on(i)
        else:
            part_off(i)

try:
    while True:
        if m_in.poll():
            ev = m_in.read(10)
            if is_hold(ev):
                part_switch([1,2,3,4,5,6])

except KeyboardInterrupt:
    m_in.close()
    out.close()
    pygame.midi.quit()
    print( "quit!")
