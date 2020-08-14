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
def switch_core(out, parts): # [1,2,3]を入力すると、1,2,3chがオン、それ以外offになる
    for i in range(1,17):
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
        self.detect_midi_device()
        self.hold_pre = 0 # 前回holdされた時刻
        print ("MIDI port : ", self.port_in, self.port_out)
        self.mout = pygame.midi.Output(self.port_out)
        self.min  = pygame.midi.Input(self.port_in, 256)
        self.mout.set_instrument(0)
    def detect_midi_device(self):
        for id in range(pygame.midi.get_count()):
            info = pygame.midi.get_device_info(id)
            if "ZOOM MS Series MIDI" in info[1]:
                if info[2] == 0:
                    # MS-50GをEditor Modeに切り替え
                    tmp_out = pygame.midi.Output(id)
                    tmp_out.write_sys_ex(pygame.midi.time(), [0xF0, 0x52, 0x00, 0x58, 0x50, 0xF7])
                elif info[2] == 1:
                    self.port_in = id
            if "FA-06" in info[1]:
                if info[2] == 0:
                    self.port_out = id
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
        last = pygame.midi.time()
        while True:
            if self.min.poll():
                ev = self.min.read(10)
                if len(ev)>0:
                    if pygame.midi.time() - last > 200:
                        #print "%d, dumper pedal!" % ev[0][1]
                        last = pygame.midi.time()
                        self.exe()
