#!/bin/bash

# Create output directories if necessary
mkdir -p logs
mkdir -p outputs/Sat_A outputs/Sat_B outputs/Sat_C

# Start a new tmux session
tmux new-session -d -s swarmpal_tasks

# Split the tmux window into three panes
tmux split-window -t swarmpal_tasks:0.0 -h
tmux split-window -t swarmpal_tasks:0.1 -h
tmux select-layout -t swarmpal_tasks even-horizontal

# Run Python scripts in each pane
tmux send-keys -t swarmpal_tasks:0.0 'python fac-fast-processor.py A outputs/Sat_A FAC/TMS/Sat_A' C-m
tmux send-keys -t swarmpal_tasks:0.1 'python fac-fast-processor.py B outputs/Sat_B FAC/TMS/Sat_B' C-m
tmux send-keys -t swarmpal_tasks:0.2 'python fac-fast-processor.py C outputs/Sat_C FAC/TMS/Sat_C' C-m

# Attach to the tmux session to view the windows
tmux attach-session -t swarmpal_tasks
