import serial
import win32api as win
import time

#MAKE SURE THE IRR IS ALWAYS FACING THE REMOTE, WHEN YOU PUT IT ON THE REAL BOARD MAKE SURE YOU HAVE THAT PART FACING FORWARD

def make_tap(key):
    def tap():
        win.keybd_event(key, 0, 0, 0)
        win.keybd_event(key, 0, 2, 0)
    return tap

def mode_switch():
    global buttons
    if buttons == keyboard_mapping:
        buttons = mouse_mapping
    else:
        buttons = keyboard_mapping

def get_port():
    for p in xrange(256):
        try:
            port = serial.Serial('COM{}'.format(p), 9600, timeout = 0.01)
            if raw_input("use port {}? y/n ".format(p)) != 'n':
                return port
            port.close()
        except:
            pass
    raise Exception("Couldn't find port")
    

class Action(object):
    
    triggered_actions = set()
    
    def __init__(self, on_trigger, repeat = True, on_hold = None, hold_time = 1):
        self._on_trigger = on_trigger
        self._on_hold = on_hold
        self._hold_time = hold_time
        self._first_triggered_at = -1
        self._triggered = False
        self._repeat = repeat
        
    def trigger(self):
        if not self._triggered:
            self._first_triggered_at = time.time()
            Action.triggered_actions.add(self)
        if self._repeat or not self._triggered:
            self._on_trigger()
            self._triggered = True
            
    @staticmethod
    def reset_all():
        if len(Action.triggered_actions) == 1: #if theres only one triggered action
            for a in Action.triggered_actions: #loops over the one action
                time_held = time.time() - a._first_triggered_at
                if a._on_hold is not None and time_held > a._hold_time:
                    a._on_hold()
        for a in Action.triggered_actions:
            a._triggered = False
        Action.triggered_actions = set()


class Mouse(object):
    def left_click():
        win.mouse_event(2, 0, 0, 0)
        win.mouse_event(4, 0, 0, 0)
    clicker = Action(left_click, repeat = False)

    @staticmethod
    def make_action(dirs, clicky = False, **action_params):
        amts = map(lambda x: x*10, dirs)
        def move():
            if clicky and len(Action.triggered_actions) == 1: #if this click is the only action triggered
                Mouse.clicker.trigger()
            elif not clicky or not Mouse.clicker._triggered: #only move the mouse if the clicker isn't down
                win.mouse_event(1, amts[0], amts[1], 0)
        return Action(move, **action_params)
    

keyboard_mapping = {
    'd': Action(make_tap(174)),
    'u': Action(make_tap(175)),
    'l': Action(make_tap(32), False),
    'r': Action(mode_switch),
    '^': Action(Action.reset_all)
}

mouse_mapping = {
    'd': Mouse.make_action((0, 1)),
    'u': Mouse.make_action((0, -1)),
    'l': Mouse.make_action((-1, 0), on_hold = mode_switch),
    'r': Mouse.make_action((1, 0), clicky = True),
    '^': Action(Action.reset_all)
}

buttons = mouse_mapping #keyboard_mapping


port = get_port()
print port
while 1:
    data = port.readline()
    for char in data:
        if char in buttons:
            buttons[char].trigger()
    if abs(win.GetKeyState(67)) > 1:
        break

port.close()
print "port closed"
