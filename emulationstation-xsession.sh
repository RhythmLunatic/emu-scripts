#!/bin/bash

# Place in ~/
# set your xsession to this like "xterm -e ~/emulationstation-xsession.sh"
# Or create an autostart.sh in ~/.config/openbox/ that says "gnome-terminal --full-screen --hide-menubar -e ~/emulationstation-xsession.sh"
# Dolphin (And probably a lot more) doesn't work without a window manager so you probably want Openbox

xsetroot -solid black
unclutter -root &
#./hhpc &
#./moltengamepad --mimic-xpad --rumble &
#sleep 1s && emulationstation; pkill -SIGINT moltengamepad
tmux new-session \; send-keys 'sleep 1s && emulationstation; pkill -SIGINT moltengamepad; exit' C-m \; split-window -v \; send-keys './moltengamepad --mimic-xpad --rumble; exit' C-m \;
