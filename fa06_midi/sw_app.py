from part_switch import *
import re
from ipywidgets import Button
from IPython.display import display
import functools
class hoge(part_switch):
    def __init__(self):
        super(hoge, self).__init__()
        self.cnt = 0
        self.cmd = []
    def read_param(self, filename):
        r = open(filename)
        self.cmd = []
        while True:
            line = r.readline().rstrip()
            if not line:
                break
            l = re.sub(',', '', line)
            self.cmd.append(map(int, l))
        print self.cmd
    def exe(self):
        self.switch(self.cmd[self.cnt])
        self.cnt = (self.cnt + 1) % len(self.cmd)
       
dir = "./live_patch"

params = !ls $dir/*
buttons = []
def btn_evt(btn, filename):
    a=hoge()
    a.read_param(filename)
    a.run()
for f in params:
    name = re.sub('.*/', '', re.sub('.txt', '', f))
    btn = Button(description=name)
    btn.on_click(functools.partial(btn_evt, filename=f))
display(btn)
