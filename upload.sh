#!/usr/bin/env bash

set -x
set -e

function usage() {
  echo "usage: ./upload.sh [audio-file] [markdown-file]"
}

if [[ $# != 2 ]]; then
  usage
  exit 1
fi

username=$(whoami)
if [ $username == "dasmithm" -o $username == "dsmith" ]; then # Dave's accounts
  username="dave"
fi

mp3_file=$1
byte_size=`ls -nl "$mp3_file" | awk '{print $5}'`
duration=`mp3info -p "%m:%02s" "$mp3_file"`
episode_number=`echo "$mp3_file" | perl -ne'/-(\d+)\.mp3/ && print $1'`
uuid=`uuidgen | perl -ne 'print lc'`
prefixed_episode_number="$(printf '%03d' $episode_number)"
new_filename="sse-${prefixed_episode_number}.mp3"
post_date=`date "+%Y-%m-%d 12:00:00 -0700"`


# edit file to set file name, byte size, guid,
perl -pi -e"s/guid: .*/guid: ${uuid}/" $2
perl -pi -e"s/date: .*/date: ${post_date}/" $2
perl -pi -e"s/duration: .*/duration: \"${duration}\"/" $2
perl -pi -e"s/length: .*/length: ${byte_size}/" $2
perl -pi -e"s/sse-(\d+)\.mp3/sse-${prefixed_episode_number}\.mp3/" $2

scp "$mp3_file" "$username@thesmithfam.org:~/podcasts/${new_filename}"
