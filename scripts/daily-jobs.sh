#!/bin/bash
set -e

cd "$(dirname "$0")"

echo Running daily jobs from directory $(pwd)

if [ $(git branch --show-current) != "gh-pages" ]; then
  git checkout gh-pages > /dev/null
fi

git pull > /dev/null

if [ ! -d "./venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

source venv/bin/activate
pip3 --quiet install -r requirements.txt

# Daily tasks to run:
./trello-setup-next-episode

