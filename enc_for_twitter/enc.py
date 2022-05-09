#!/usr/bin/python3
# usage: ./cut.py input [opt]
import re,os,subprocess,math
from absl import app,flags
FLAGS = flags.FLAGS

#### parameters
FFMPEG_CMD = './ffmpeg.exe' # WSL上でWindows用ffmpegを叩く場合(GPU使いたい人等)
FFPROBE_CMD = '/usr/bin/ffprobe'

#### for 音ゲー動画
MAX_DURATION_TWITTER = 140  # 動画の最大長(s)、twitterだと140
RESULT_DURATION = 6 # リザルト画面(厳密には、最初のsc点直後)を何秒間残すか
SC_IDX = 0          # 何番目のシーンチェンジ時刻をベースにするか。デフォルトは0。
SC_THRESHOLD = 0.8  # シーンチェンジ判定のしきい値

otoge_duration = 0  # 音ゲーモード時の動画長


def parse_ts(ts):
    dat = ts.split(':')
    ss=0.0;mm=0;hh=0
    ss = float(dat[-1])
    if len(dat) > 1:
        mm = int(dat[-2])*60
    if len(dat) > 2:
        hh = int(dat[0])*3600
    return hh+mm+ss

def main(argv):
    f_in = argv[1]
    f_out = f_in+'.mp4'
    if len(argv) > 2:
        f_out = argv[2]
    print(f'input:{f_in} output:{f_out}')

    st = 0;ed=-1
    if FLAGS.trim:
        tmp_s,tmp_e = FLAGS.trim.split('-')
        st = parse_ts(tmp_s)
        ed = parse_ts(tmp_e)
    elif FLAGS.st:
        st = parse_ts(FLAGS.st)
    elif FLAGS.ed:
        ed = parse_ts(FLAGS.ed)
    opt = f'-i {f_in} -hide_banner'
    opt_vf = '-vf yadif=0:-1'
    opt_af = f' -af volume={FLAGS.gain}dB'
    if ed > 0 and ed > st:
        opt += f' -t {ed-st}'
    opt = f'-ss {st} {opt}'
    if FLAGS.otoge:
        cmd = f'{FFMPEG_CMD} {opt} -c:v h264_nvenc -t {MAX_DURATION_TWITTER} -filter:v "select=\'gt(scene,{SC_THRESHOLD})\',showinfo" -f null /dev/null'
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ###### シーンチェンジ情報を分析
        dat = [l.decode() for l in proc.stderr.readlines() if 'pts_time' in l.decode()]
        sc = [math.ceil(float(re.sub(' .*', '', re.sub('.*pts_time:', '', d)))) for d in dat]
        otoge_duration = min(MAX_DURATION_TWITTER, sc[SC_IDX] + RESULT_DURATION)
        print (f'otoge mode> detected duration: {otoge_duration}[s]')

    vb = FLAGS.vbitrate
    if FLAGS.acopy:
        opt += f' -c:a copy -b:v {vb}M'
    else:
        opt += f' -ab 256k -b:v {vb}M'
    if FLAGS.h264 or FLAGS.otoge:
        opt += " -c:v h264_nvenc"
    else:
        opt += " -c:v hevc_nvenc -tag:v hvc1"
    # フェード関係
    val_fadein = FLAGS.fadein
    val_fadeout = FLAGS.fadeout
    if FLAGS.fadein > 0 or FLAGS.otoge:
        if FLAGS.otoge and FLAGS.fadein == 0:
            val_fadein = 2
    if FLAGS.fadeout > 0 or FLAGS.otoge:
        if FLAGS.otoge and FLAGS.fadeout == 0:
            val_fadeout = 2
    if val_fadein > 0:
        opt_vf += f',fade=t=in:st=0:d={val_fadein}'
        opt_af += f',afade=t=in:st=0:d={val_fadein}'
    if val_fadeout > 0:
        opt_vf += f',fade=t=out:st={ed-st-val_fadeout}:d={val_fadeout}'
        opt_af += f',afade=t=out:st={ed-st-val_fadeout}:d={val_fadeout}'
    if FLAGS.acopy: # acopyと-afは共存できないため、コピー時は切っておく
        opt_af = ''
    cmd = f'{FFMPEG_CMD} {opt} {opt_af} {opt_vf} {f_out}'
    print(f'encode command = {cmd}')
    os.system(cmd)

    if FLAGS.rm:
        os.system(f'rm -rf {f_in}')

if __name__ == '__main__':
    flags.DEFINE_integer('fadein', 0, 'set a duration for fadein', short_name='i')
    flags.DEFINE_integer('fadeout', 0, 'set a duration for fadeout', short_name='o')
    flags.DEFINE_bool('rm', False, 'remove inputfile after encoding', short_name='r')
    flags.DEFINE_bool('h264', False, 'use h264_nvenc (default:nvenc_hevc)')
    flags.DEFINE_integer('vbitrate', 10, 'set a bitrate for video(Mbps)')
    flags.DEFINE_float('gain', 0, 'set a value for gaining audio volume', short_name='g')
    flags.DEFINE_bool('acopy', False, 'use the same audio codes settings as input')
    flags.DEFINE_string('st', None, 'set start-point for trimming (hh:mm:ss.ms)', short_name='s')
    flags.DEFINE_string('ed', None, 'set end-point for trimming (hh:mm:ss.ms)', short_name='e')
    flags.DEFINE_string('trim', None, 'set start and end point for trimming (hh:mm:ss.ms-hh:mm:ss.ms)', short_name='t')
    flags.DEFINE_bool('otoge', False, 'use the settings for otogame (2pass)')
    app.run(main)
