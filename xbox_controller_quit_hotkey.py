#!/usr/bin/python3
# Originally released by rdb under the Unlicense (unlicense.org)
# Modified by Rhythm Lunatic
# TODO: No need for an array since we're only checking two buttons
# Also it should open all devices instead of js0 in case p2, p3, or p4 wants to quit the game
import os, struct, array
import subprocess
import sys
import time
from fcntl import ioctl

def processExists(process, isPID = False):
	if isPID:
		return subprocess.run(["kill","-0",process], stderr=subprocess.DEVNULL).returncode == 0
	else:
		return subprocess.run(["pgrep", process], stdout=subprocess.DEVNULL).returncode == 0

# "But what if my process is named --pid?"
# Don't do that. Or substitute junk for the first argument.
givenPIDToKill = (sys.argv[1] == "--pid")

PROGRAM_TO_KILL = sys.argv[-1]
print("Will kill "+PROGRAM_TO_KILL)

#Since moltengamepad hides existing controllers we need to enumerate until we find a working controller.
infile_path = None
for i in range(0,9):
	toTry = "/dev/input/js"+str(i)
	if os.path.exists(toTry):
		try:
			with open(toTry) as test:
				print("Found available controller at "+toTry)
				infile_path = toTry
				break
		except IOError:
			pass
		
if not infile_path:
	print("No controllers found, giving up.")
	os._exit(0)

#Uncomment if you need to test it in foreground
pid = os.fork()
if pid:
	print("Spawned background process with PID "+str(pid))
	os._exit(0)


	
EVENT_SIZE = struct.calcsize("LhBB")

jsdev = open(infile_path, "rb")

# We'll store the states here.
button_states = {}

axis_map = []
button_map = []

buf = array.array('B', [0] * 64)
ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
print('Device name: %s' % js_name)

# Get number of axes and buttons.
buf = array.array('B', [0])
ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
num_axes = buf[0]

buf = array.array('B', [0])
ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
num_buttons = buf[0]

# Get the axis map.
#buf = array.array('B', [0] * 0x40)
#ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

#for axis in buf[:num_axes]:
#	axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
#	axis_map.append(axis_name)
#	axis_states[axis_name] = 0.0

# Get the button map.
buf = array.array('H', [0] * 200)
ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

for btn in buf[:num_buttons]:
	#btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
	button_map.append(btn)
	button_states[btn] = 0

#print('%d axes found: %s' % (num_axes, ', '.join(axis_map)))
print('%d buttons found' % (num_buttons))

# Wait for process to spawn
initTime = time.time()
while not processExists(PROGRAM_TO_KILL,givenPIDToKill):
	if time.time() - initTime > 10:
		print("Process hasn't spawned in 10 seconds. Giving up and exiting.")
		os._exit(0)

print("Process spawned, continuing")

while processExists(PROGRAM_TO_KILL,givenPIDToKill):
	evbuf = jsdev.read(8)
	if evbuf:
		time, value, type, number = struct.unpack('IhBB', evbuf)

		#if type & 0x80:
		#	 print("(initial)", end="")

		if type & 0x01:
			#print(str(number))
			#button = button_map[number]
			button = number
			if button and number == 7 or number == 8:
				button_states[button] = value
				if value:
					print("%s pressed" % (button))
					if button_states[7] and button_states[8]:
						print("Quit controller hotkey pressed...")
						if givenPIDToKill:
							subprocess.run(["kill","-s","SIGTERM", PROGRAM_TO_KILL])
						else:
							subprocess.run(["pkill", "-SIGTERM", PROGRAM_TO_KILL])
						print("Good bye.")
						os._exit(0)
				#else:
				#	print("%s released" % (button))

		#if type & 0x02:
		#	axis = axis_map[number]
		#	if axis:
		#		fvalue = value / 32767.0
		#		axis_states[axis] = fvalue
		#		print("%s: %.3f" % (axis, fvalue))

print("The process has exited. This program will exit.")
