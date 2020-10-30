#!/bin/bash
# It runs Linux or Windows games with some additional compatibility settings

# Example config file:
# program=/mmt/Windows/Games/MBAACC/MBAA.exe
# args=
# win=true
# dinput=false (Not implemented)
# killbyname=

# Parameters can be in any order.
# program: Location of the game
# args: Launch arguments of the game
# win: If true, runs using WINE, otherwise executes the program normally
# dinput: If true, controllers will switch to DInput mode so the DPad functions correctly.
# killbyname: The name of the application to kill instead of killing what launched. This is mostly only for launchers like Steam since if you killed by PID you'd kill steam. Keep it blank if you're not running your game through Steam.

declare -A CONFIG
while IFS= read -r line; do
    CONFIG[${line%%=*}]=${line#*=}
done < "$1"

#mapfile -t < "$1"
#readarray -t lines < "$1"


#Make sure to change directories...
cd "${CONFIG[program]%/*}"
echo $PWD

# If a wine program gets killed (Even with SIGINT) the resolution won't switch back
# Perhaps this is only needed for wine?
currentRes=$(xrandr | grep \* | awk '{print $1}')

# ,, means make it lowercase
if [ "${CONFIG[win],,}" = "true" ]; then
    if [[ ! -z "${CONFIG[args]// }" ]]; then
        wine "${CONFIG[program]}" "${CONFIG[args]}" &
    else
        wine "${CONFIG[program]}" &
    fi
else
    #This is how you get steam games working without steam://rungameid
    #If steam is installed somewhere else... Good luck.
    export LD_LIBRARY_PATH=~/.steam/debian-installation/ubuntu12_32/steam-runtime/lib/x86_64-linux-gnu
    if [[ ! -z "${CONFIG[args]// }" ]]; then
        "${CONFIG[program]}" "${CONFIG[args]}" &
    else
        "${CONFIG[program]}" &
    fi
fi

#echo "${CONFIG[killbyname]}"
if [[ ! -z "${CONFIG[killbyname]// }" ]]; then
    echo "Will kill a process by the name of ${CONFIG[killbyname]}"
    ~/xbox_controller_quit_hotkey.py ${CONFIG[killbyname]}
else
    echo "PID of new process is $!"
    ~/xbox_controller_quit_hotkey.py --pid $!
fi

while [ -n "$(ps -p $! -o pid=)" ]
do
    # This does nothing.
	true
done
xrandr -s $currentRes


