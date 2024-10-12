#!/bin/bash

source /path/to/your/clone/.venv/bin/activate

restore_padding() {
  if [[ -n "$KITTY_PID_" ]]; then
    kitty @ set-spacing padding=default
  fi
}

if [[ -n "$KITTY_PID" ]]; then
  kitty @ set-spacing padding=0
fi

trap restore_padding EXIT

python3 /path/to/your/clone/main.py

restore_padding
