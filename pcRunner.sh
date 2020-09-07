#!/bin/bash
# It runs Linux or Windows games with some additional compatibility settings

# Example config file:
# /mmt/Windows/Games/MBAACC/MBAA.exe
# win=true
# dinput=false (Not implemented)

# Meaning of parameters:
# 1st line: Location of the game
# 2nd line: If true, runs using WINE, otherwise executes the program normally
# 3rd line: If true, controllers will switch to DInput mode so the DPad functions correctly.

mapfile -t < "$1"

#Make sure to change directories...
cd "${MAPFILE[0]%/*}"
echo $PWD

# If a wine program gets killed (Even with SIGINT) the resolution won't switch back
# Perhaps this is only needed for wine?
currentRes=$(xrandr | grep \* | awk '{print $1}')

# ,, means make it lowercase
if [ "${MAPFILE[1],,}" = "win=true" ]; then
    wine "${MAPFILE[0]}" &
else
    "${MAPFILE[0]}" &
fi
echo "PID of new process is $!"

~/xbox_controller_quit_hotkey.py --pid $!

while [ -n "$(ps -p $! -o pid=)" ]
do
    # This does nothing.
	true
done
xrandr -s $currentRes


