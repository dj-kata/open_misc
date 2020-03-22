#!/usr/bin/env python
# coding: utf-8

import pygame.midi
import picamera
import time

hold_pre = 0
def send_sysex(out, address, data): # address[4]
    wdt = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x77, 0x12]
    for a in address:
        wdt.append(a)
    wdt.append(data)
    tmp = (sum(address) + data) % 128
    chksum = 128 - tmp
    wdt.append(chksum)
    wdt.append(0xF7)
    #print ("sysex wdt:%s" % str(wdt))
    out.write_sys_ex(pygame.midi.time(), wdt)
def part_on(out, p): # p:1-16
    addr = 0x3F + p
    send_sysex(out, [0x18, 0x00, addr, 0x02], 0x01)
def part_off(out, p): # p:1-16
    addr = 0x3F + p
    send_sysex(out, [0x18, 0x00, addr, 0x02], 0x00)
def is_hold(ev):
    ret = False
    global hold_pre
    if len(ev)>0 and ev[0][1] - hold_pre > 50: # チャタリング対策
        if ev[0][0][1] == 64 and ev[0][0][2] == 127 and ev[0][0][0] in range(174,185): # ダンパーの値がコロコロ変わる対策
            ret = True
    hold_pre = ev[0][1]
    return ret
def switch_core(out, parts): # [1,2,3]を入力すると、1,2,3chがオン、それ以外offになる
    for i in range(2,17):
        if i in parts:
            part_on(out, i)
        else:
            part_off(out, i)
def trans_core(out, tr, val): # tr:track number,  val: -48...48
    wval = val + 64
    addr = 0x1F + tr
    send_sysex(out, [0x18, 0x00, addr, 0x0B], wval)
def oct_core(out, tr, val): # tr:track number,  val: -3 ... 3
    wval = val + 64
    addr = 0x1F + tr
    send_sysex(out, [0x18, 0x00, addr, 0x1B], wval)

class part_switch(object):
    def __init__(self):
        pygame.midi.init()
        self.port_out = 2
        self.port_in = 3
        self.hold_pre = 0 # 前回holdされた時刻
        self.mout = pygame.midi.Output(self.port_out)
        self.min  = pygame.midi.Input(self.port_in)
        self.mout.set_instrument(0)
    def switch(self, parts):
        switch_core(self.mout, parts)
    def trans(self, tr, val):
        trans_core(self.mout, tr, val)
    def oct(self, tr, val):
        oct_core(self.mout, tr, val)
    def exe(self):
        # ペダルを踏んだときに実行するメソッド。
        # ここをオーバーライドすればよい。
        pass
    def run(self):
        try:
            while True:
                if self.min.poll():
                    ev = self.min.read(10)
                    #if len(ev)>0:
                    #    print(str(ev[0][0]))
                    if is_hold(ev):
                        print "%d, dumper pedal!" % ev[0][1]
                        self.exe()
        except KeyboardInterrupt:
            self.min.close()
            out.close()
            pygame.midi.quit()
            print( "quit!")
