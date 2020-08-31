#!/usr/bin/python3
# usage: ./cut.py input [opt]
import re,sys,os,subprocess
from docopt import docopt

#### parameters
# FFMPEG_CMD = 'ffmpeg'
FFMPEG_CMD = './ffmpeg.exe' # WSL上でWindows用ffmpegを叩く場合(GPU使いたい人等)
FFPROBE_CMD = '/usr/bin/ffprobe'
FADE_DURATION = 2 # フェード時間

__doc__ = """{f}

Usage:
    {f} <input> [<output>] [-r | --rm] [--fadein] [--fadeout] [--h264] 
        [--vbitrate <val>] [--acopy] [-s <start_ts>] [-e <end_ts>]
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
    vb = 10 # default
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
        opt += f' -filter:v "fade=out:st={duration-FADE_DURATION}:d={FADE_DURATION}"'
        opt += f' -filter:a "afade=t=out:st={duration-FADE_DURATION}:d={FADE_DURATION}"'

    cmd = f'{FFMPEG_CMD} {opt_ss} {opt} {f_out}'
    print(f'encode command = {cmd}')
    print (cmd)
    os.system(cmd)

    if args['--rm']:
        os.system(f'rm -rf {f_in}')
