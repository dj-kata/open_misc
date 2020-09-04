#!/usr/bin/python3
# usage: ./cut.py input [opt]
import re,sys,os,subprocess,math
from docopt import docopt

#### parameters
# FFMPEG_CMD = 'ffmpeg'
FFMPEG_CMD = './ffmpeg.exe' # WSL上でWindows用ffmpegを叩く場合(GPU使いたい人等)
FFPROBE_CMD = '/usr/bin/ffprobe'
FADE_DURATION = 2 # フェード時間
DEFAULT_VBITRATE = 10 # デフォルト: 10Mbps

#### for 音ゲー動画
MAX_DURATION_TWITTER = 140  # 動画の最大長(s)、twitterだと140
RESULT_DURATION = 6 # リザルト画面(厳密には、最初のsc点直後)を何秒間残すか
SC_IDX = 0          # 何番目のシーンチェンジ時刻をベースにするか。デフォルトは0。
SC_THRESHOLD = 0.8  # シーンチェンジ判定のしきい値

otoge_duration = 0  # 音ゲーモード時の動画長

__doc__ = """{f}

Usage:
    {f} <input> [<output>] [-r | --rm] [--fadein] [--fadeout] [--h264] 
        [--vbitrate <val>] [--acopy] [-s <start_ts>] [-e <end_ts>]
        [--otoge]
    {f} -h | --help

Options:
    <OUTPUT_FILE>              use specific output-file-name
    --fadein                   enable fadein
    --fadeout                  enable fadeout
    -r --rm                    remove inputfile after encoding
    --h264                     use h264_nvenc (default:hevc_nvenc)
    --vbitrate <val>           set video bitrate(Mbps) (default:10)
    --acopy                    use the same audio codec settings as input
    -s <START_TS>              set start-point for trimming
    -e <END_TS>                set end-point for trimming
    --otoge                    use setting for oto-game(2pass)
    -h --help                  show this screen and exit.

""".format(f=__file__)

if __name__ == '__main__':
    args = docopt(__doc__)

    f_in = args['<input>']
    print(f_in)
    f_out = f_in+'.mp4'

    if args['<output>']:
        f_out = args['<output>']
    st = 0
    if args['-s']:
        dat = list(map(int,args['-s'].split(':')))
        st = dat[-1]
        if len(dat) >= 2: st += dat[-2]*60
        if len(dat) >= 3: st += dat[-3]*3600
    ed = 0
    if args['-e']:
        dat = list(map(int,args['-e'].split(':')))
        ed = dat[-1]
        if len(dat) >= 2: ed += dat[-2]*60
        if len(dat) >= 3: ed += dat[-3]*3600
    opt_ss = ''
    opt = f'-i {f_in} -hide_banner'
    if st > 0:
        opt_ss = f' -ss {st}'
    if ed > 0 and ed > st:
        opt += f' -t {ed - st}'
    if args['--otoge']:
        args['--h264'] = True
        args['--fadeout'] = True
        args['--fadein'] = True
        cmd = f'{FFMPEG_CMD} {opt_ss} {opt} -c:v h264_nvenc -t {MAX_DURATION_TWITTER} -filter:v "select=\'gt(scene,{SC_THRESHOLD})\',showinfo" -f null /dev/null'
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ###### シーンチェンジ情報を分析
        dat = [l.decode() for l in proc.stderr.readlines() if 'pts_time' in l.decode()]
        sc = [math.ceil(float(re.sub(' .*', '', re.sub('.*pts_time:', '', d)))) for d in dat]
        otoge_duration = min(MAX_DURATION_TWITTER, sc[SC_IDX] + RESULT_DURATION)

    vb = DEFAULT_VBITRATE # default
    if args['--vbitrate']:
        vb = int(args['--vbitrate'])
    if args['--acopy']:
        opt += f" -c:a copy -b:v {vb}M -deinterlace"
    else:
        opt += f" -b:a 256k -b:v {vb}M -deinterlace"

    if args['--h264']:
        opt += " -c:v h264_nvenc"
    else:
        opt += " -c:v hevc_nvenc -tag:v hvc1"
    if args['--fadein']:
        duration = ed - st
        opt += f' -filter:v "fade=in:st=0:d=1"'
        opt += f' -filter:a "afade=t=in:st=0:d=1"'
    if args['--fadeout']:
        if ed == 0:
            a = subprocess.check_output([FFPROBE_CMD, f_in, '-show_entries', 'format=duration'], stderr=open('/dev/null', 'w')).decode().split('\n')[1]
            ed = float(re.sub('.*=', '', a))
        duration = ed - st
        if args['--otoge']:
            duration = otoge_duration # 1pass目の結果をここで伝える
            opt += f' -t {duration}'
            
        opt += f' -filter:v "fade=out:st={duration-FADE_DURATION}:d={FADE_DURATION}"'
        opt += f' -filter:a "afade=t=out:st={duration-FADE_DURATION}:d={FADE_DURATION}"'

    cmd = f'{FFMPEG_CMD} {opt_ss} {opt} {f_out}'
    print(f'encode command = {cmd}')
    print (cmd)
    os.system(cmd)

    if args['--rm']:
        os.system(f'rm -rf {f_in}')
