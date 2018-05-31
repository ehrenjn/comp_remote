import serial
import win32api as win
#import time


mappings = {
    'd': 174,
    'u': 175,
    'l': 32
}

def tap(key):
    win.keybd_event(key, 0, 0, 0)
    win.keybd_event(key, 0, 2, 0)

times = {l: 0 for l in 'udlr'} 
def increment_times():
    for t in times:
        times[t] += 1

port = serial.Serial('COM4', 9600, timeout = 0.01)
while 1:
    button = port.readline()
    increment_times()
    if button in mappings:
        if times[button] > 10:
            tap(mappings[button])
        times[button] = 0
    if abs(win.GetKeyState(67)) > 1:
        break

port.close()
print "port closed"
