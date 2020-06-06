#!/usr/bin/python3
# usage: ./enc_twitter.sh input.mp4 [h:]m:s output_name
# 指定した位置から140秒切り出す。
import os, sys
if len(sys.argv) < 4:
    print ('usage: %s input.mp4 [h:]m:s output_name' % sys.argv[0])
    sys.exit(1)

opt = "-b:v 10M -b:a 256k -c:v h264_nvenc -t 140"

f_in  = sys.argv[1]
f_out = sys.argv[3]
st    = list(map(int, sys.argv[2].split(':')))
st_sec = st[-1] + st[-2]*60

if len(st) == 3:
    st_sec += st[0] * 3600
os.system(f'./ffmpeg.exe -i {f_in} {opt} -ss {st_sec} {f_out}')
