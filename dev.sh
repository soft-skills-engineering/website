#!/bin/bash

set -e

cd "$(dirname "$0")"

if ! which bundle >/dev/null; then
  echo "Can't find a bundle executable. Please install it. You may need to run 'rvm use 2.6.5'"
  exit 1
fi

bundle install
rm -rf _site
bundle exec jekyll serve --watch --incremental --future --host 0.0.0.0
