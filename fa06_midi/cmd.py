### note01
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
            line = r.readline()
            if not line:
                break
            l = re.sub(' ','',re.sub('#.*', '', line.rstrip())).split(";")
            if len(l)>0 and l[0] != '':
                self.cmd.append(l)
        print self.cmd
    def exe(self):
        c = self.cmd[self.cnt]
        #print (c)
        for cmd in c:
            val = map(int, re.findall("\d+", cmd))
            if cmd[:2] == 'sw':
                self.switch(val)
            elif cmd[:3] == 'oct':
                self.oct(val[0], val[1])
            elif cmd[:5] == 'trans':
                self.trans(val[0], val[1])
        self.cnt = (self.cnt + 1) % len(self.cmd)
target_dir = "./live_patch"

### note02
params = !find $target_dir|grep txt
for i in range(len(params)):
    print "%d: %s" % (i, params[i])
    
### note03
target=0
params = !find $target_dir|grep txt
for i in range(len(params)):
    print "%d: %s" % (i, params[i])
