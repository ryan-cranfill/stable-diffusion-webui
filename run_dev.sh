#!/bin/bash

SESSION="run"
SESSIONEXISTS=$(tmux list-sessions | grep -w "$SESSION")

if [ "$SESSIONEXISTS" = "" ]
then

  tmux new-session -d -s "$SESSION" -d -x "$(tput cols)" -y "$(tput lines)"

  tmux rename-window -t 0 'window 0'
  tmux send-keys -t 'window 0' '# API server' C-m
  tmux send-keys -t 'window 0' '# Wait for parcel to be ready' C-m
  tmux send-keys -t 'window 0' 'until pids=$(pgrep -f parcel)' C-m
  tmux send-keys -t 'window 0' 'do   ' C-m
  tmux send-keys -t 'window 0' '    sleep 1' C-m
  tmux send-keys -t 'window 0' 'done' C-m
  tmux send-keys -t 'window 0' 'source venv/bin/activate' C-m
  tmux send-keys -t 'window 0' 'python -m src.server' C-m
  tmux splitw -h

  tmux send-keys -t 'window 0' '# Display thread' C-m
  tmux send-keys -t 'window 0' '# Wait for server to be ready' C-m
  tmux send-keys -t 'window 0' 'export DISPLAY=:0' C-m
  tmux send-keys -t 'window 0' 'until pids=$(pgrep -f "python -m src.server")' C-m
  tmux send-keys -t 'window 0' 'do   ' C-m
  tmux send-keys -t 'window 0' '    sleep 1' C-m
  tmux send-keys -t 'window 0' 'done' C-m
  tmux send-keys -t 'window 0' 'source venv/bin/activate' C-m
  tmux send-keys -t 'window 0' 'source ./webui-user.sh' C-m
  tmux send-keys -t 'window 0' 'nodemon --watch src -e py --exec python -m src.display' C-m
  tmux splitw -v

  tmux send-keys -t 'window 0' '# Parcel bundler' C-m
  tmux send-keys -t 'window 0' 'cd src/windows-vistas-client' C-m
  tmux send-keys -t 'window 0' 'rm -rf .parcel-cache dist' C-m
  tmux send-keys -t 'window 0' 'npm start' C-m
  tmux select-pane -t 0
  tmux splitw -v

  tmux send-keys -t 'window 0' '# Generator thread' C-m
  tmux send-keys -t 'window 0' '# Wait for server to be ready' C-m
  tmux send-keys -t 'window 0' 'until pids=$(pgrep -f "python -m src.server")' C-m
  tmux send-keys -t 'window 0' 'do   ' C-m
  tmux send-keys -t 'window 0' '    sleep 1' C-m
  tmux send-keys -t 'window 0' 'done' C-m
  tmux send-keys -t 'window 0' 'source venv/bin/activate' C-m
  tmux send-keys -t 'window 0' 'source ./webui-user.sh' C-m
  tmux send-keys -t 'window 0' 'python -m src.sd_generator' C-m

  tmux select-pane -t 0

fi

tmux attach-session -t "$SESSION":0


#source venv/bin/activate
#source webui-user.sh
#python -m src.server
#python -m src.sd_generator
#nodemon --watch src -e py --exec python -m src.display