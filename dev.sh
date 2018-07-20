#!/bin/bash

set -e

cd "$(dirname "$0")"

which bundle >/dev/null || sudo gem install bundler

bundle install
rm -rf _site
bundle exec jekyll serve --watch --incremental --future
