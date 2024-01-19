#!/bin/bash
set -e

cd "$(dirname "$0")"

git checkout gh-pages
git pull

if [ ! -d "./venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

source venv/bin/activate
pip3 --quiet install -r requirements.txt

# Daily tasks to run:
./trello-setup-next-episode

