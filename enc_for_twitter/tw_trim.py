#!/usr/bin/python3
# usage: ./enc_twitter.sh input.mp4 [h:]m:s output_name [sc_idx]
# 指定位置から140秒切り出す。ただし、シーンチェンジが早い場合はそちらを優先。
# 1pass目で指定位置から140秒の間にあるシーンチェンジを検出
# 2pass目で検出された位置+αまでをエンコード
import subprocess, sys, re, math, os

RESULT_DURATION = 5 # リザルト画面(厳密には、最初のsc点直後)を何秒間残すか
SC_IDX = 0  # 何番目のシーンチェンジ時刻をベースにするか。デフォルトは0。
SC_THRESHOLD = 0.8 # シーンチェンジ判定のしきい値
if len(sys.argv) < 4:
    print ('usage: %s input.mp4 [h:]m:s output_name' % sys.argv[0])
    sys.exit(1)
if len(sys.argv) == 5:
    SC_IDX = int(sys.argv[4])

opt = "-b:v 10M -b:a 256k -c:v h264_nvenc"
f_in  = sys.argv[1]
f_out = sys.argv[3]
st    = list(map(int, sys.argv[2].split(':')))
st_sec = st[-1] + st[-2] * 60
if len(st) == 3:
    st_sec += st[0] * 3600

cmd_base = f'./ffmpeg.exe -ss {st_sec} -i {f_in} -c:v h264_nvenc'

### 1pass目
cmd = f'{cmd_base} -t 140 -filter:v "select=\'gt(scene,{SC_THRESHOLD})\',showinfo" -f null /dev/null'
###### encode実行
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

###### シーンチェンジ情報を分析
dat = [l.decode() for l in proc.stderr.readlines() if 'pts_time' in l.decode()]
sc = [math.ceil(float(re.sub(' .*', '', re.sub('.*pts_time:', '', d)))) for d in dat]
duration = min(140, sc[SC_IDX] + RESULT_DURATION)

### 2pass目
fadeout  = f'-filter:v "fade=out:st={duration-0.5}:d=0.5" '
fadeout += f'-filter:a "afade=t=out:st={duration-0.5}:d=0.5"'
print(fadeout)
cmd = f'{cmd_base} -t {duration} {fadeout} {f_out}'
os.system(cmd)

