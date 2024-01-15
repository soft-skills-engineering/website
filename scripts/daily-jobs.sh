#!/bin/bash

cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

source venv/bin/activate
pip3 --quiet install -r requirements.txt

# Daily tasks to run:
./trello-setup-next-episode