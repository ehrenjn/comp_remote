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





















'''
#in this example I'm reading serial data from an arduino on port COM4 @ 9600 baud (you can find out what port it's on in the arduino ide)
#remember that you can't upload anything to the port while a port is open
#also remember that an 'access denied' windows error just means that another program is reading from the port

import serial

port = serial.Serial('COM4', 38400, timeout = 0.01) #port name and baud
data = ''
line = ''
while line == '':
    line = port.readline()
    data += line
    #print line
while line != '':
    line = port.readline() #ASSUMES THERES A NEWLINE BETWEEN EVERY MESSAGE FROM THE ARDUINO
    data += line
    #print line
    
port.close() #gotta close those badboys or else nothing will be able to read from the port

print data.split('\n')
data = [int(d) for d in data.split('\n') if d != '']
print len(data)
print '\n'*5
for i, _ in enumerate(data):
    if (i+1 < len(data)):
        print data[i+1] - data[i]
'''
