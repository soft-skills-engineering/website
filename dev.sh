#!/bin/bash

sudo gem install bundler \
  && bundle install \
  && bundle exec jekyll serve --watch --incremental --future
