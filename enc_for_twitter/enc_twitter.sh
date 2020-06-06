#!/bin/bash
# usage: ./enc_twitter.sh input.mp4 [input.mp4,...]
# twitterに投稿可能なビットレートにする & 140秒トリムする。
opt="-b:v 8M -b:a 256k -c:v h264_nvenc -t 140"
for f in "$@";do
        ./ffmpeg.exe -i $f ${opt} ${f}_twitter.mp4
done
