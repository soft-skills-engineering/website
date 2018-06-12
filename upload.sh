#!/usr/bin/env bash

# Usage:
if [[ $# != 3 ]]; then
  echo "This script does the following after the audio file is edited:"
  echo "  1. Create the episode markdown file (with metadata)"
  echo "  2. Upload the mp3 to the server"
  echo
  echo "After you run it, you must poopulate the TODOs in the mark down file"
  echo
  echo "usage: ./upload.sh <audio-file> <episode-date> <url-title>"
  echo
  echo "example: ./upload.sh /tmp/sse-112.mp3 2018-06-12 dogma-rehab-and-firing-a-coworker"
  echo
  exit 1
fi

set -e

# Hack for Dave's Macs:
username=$(whoami)
if [ $username == "dasmithm" -o $username == "dsmith" ]; then # Dave's accounts
  username="dave"
fi

# Command line args:
mp3_file=$1
episode_date=$2
episode_url_title=$3

website_dir="$(realpath "$(dirname "$0")")"
byte_size=`ls -nl "$mp3_file" | awk '{print $5}'`
duration=`mp3info -p "%m:%02s" "$mp3_file"`
episode_number=`echo "$mp3_file" | perl -ne'/-(\d+)\.mp3/ && print $1'`
uuid=`uuidgen | perl -ne 'print lc'`
prefixed_episode_number="$(printf '%03d' $episode_number)"
new_filename="sse-${prefixed_episode_number}.mp3"
episode_timestamp="$episode_date 12:00:00 -0700"
episode_markdown_file="$website_dir/_posts/$episode_date-episode-$episode_number-$episode_url_title.md"

# Markdown file template:
cat << EOM > "$episode_markdown_file"
---
layout: post
title: "Episode $episode_number: TODO WRITE TITLE HERE"
date: $episode_timestamp
guid: $uuid
duration: "$duration"
length: $byte_size
file: "https://dts.podtrac.com/redirect.mp3/download.softskills.audio/sse-$episode_number.mp3"
categories: episode
enable_comments: true
---

In this episode, Dave and Jamison answer these questions:

1. TODO

TODO

2. TODO

TODO
EOM

echo "Episode markdown has been created here:"
echo
echo $episode_markdown_file
echo
read -p "Open vim to edit it? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
  vi "$episode_markdown_file"
fi
echo
echo

read -p "Add it to git now? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
  git add "$episode_markdown_file"
  git commit -v
fi
echo
echo


read -p "Upload to server now? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
  scp "$mp3_file" "$username@thesmithfam.org:~/podcasts/${new_filename}"
fi
echo
echo
