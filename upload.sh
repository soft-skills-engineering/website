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


byte_size=`ls -nl "$1" | awk '{print $5}'`
duration=`mp3info -p "%m:%02s" $1`
episode_number=`echo "$1" | perl -ne'/episode-(\d+)\.mp3/ && print $1'`
uuid=`uuidgen | perl -ne 'print lc'`
new_filename="sse-${episode_number}.mp3"
post_date=`date "+%Y-%m-%d 12:00:00 -0700"`


# edit file to set file name, byte size, guid,
perl -pi -e"s/guid: .*/guid: ${uuid}/" $2
perl -pi -e"s/date: .*/date: ${post_date}/" $2
perl -pi -e"s/duration: .*/duration: \"${duration}\"/" $2
perl -pi -e"s/length: .*/length: ${byte_size}/" $2
perl -pi -e"s/sse-(\d+)\.mp3/sse-${episode_number}\.mp3/" $2

scp $1 ssh.thesmithfam.org:~/podcasts/${new_filename}

