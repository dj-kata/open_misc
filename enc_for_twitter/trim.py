#!/usr/bin/python3
# usage: ./trim.py in.mp4 out.mp4 st(hh:mm:ss) ed(hh:mm:ss) [-fadeout]
import sys, os
FADE_DURATION = 0.5 # フェードの長さ(s)

if len(sys.argv) < 5:
    print (f'usage: {sys.argv[0]} in.mp4 out.mp4 st((hh:)mm:ss) ed((hh:)mm:ss) [-fadeout]')
    sys.exit()

f_in  = sys.argv[1]
f_out = sys.argv[2]

st    = list(map(int, sys.argv[3].split(':')))
st_sec = st[-1] + st[-2] * 60
if len(st) == 3:
    st_sec += st[0] * 3600

ed    = list(map(int, sys.argv[4].split(':')))
ed_sec = ed[-1] + ed[-2] * 60
if len(ed) == 3:
    ed_sec += ed[0] * 3600

isFadeout = ('-fadeout' in sys.argv)

duration = ed_sec - st_sec

print (f'duration = {duration}')

opt      = "-b:v 10M -c:v hevc_nvenc -tag:v hvc1 -ab 192k -deinterlace"
cmd_base = f'./ffmpeg.exe -ss {st_sec} -i {f_in} {opt}'

if isFadeout:
    fadeout  = f'-filter:v "fade=out:st={duration-FADE_DURATION}:d={FADE_DURATION}" '
    fadeout += f'-filter:a "afade=t=out:st={duration-FADE_DURATION}:d={FADE_DURATION}"'
else:
    fadeout = ''
cmd = f'{cmd_base} -t {duration} {fadeout} {f_out}'
os.system(cmd)
