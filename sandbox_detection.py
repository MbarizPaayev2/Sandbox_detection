#!/usr/bin/python3
import ctypes  #Allows access to low-level Windows API func
import random  #Used to generate random limits
import time    #For time measurements and delay calculations
import sys     #Provides system-specific functions

user32 = ctypes.windll.user32  #Load user32.dll
kernel32 = ctypes.windll.kernel32 #Load kernel32.dll

#This structure stores information about the last input event on the system
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
         #cbSize: size of the structure in bytes, must be initialized before API call
        ("cbSize", ctypes.c_uint),
        #dwTime: timestamp (in milliseconds) of the last user input event
        ("dwTime", ctypes.c_ulong)
    ]


def get_last_input():
    
    #Create an instance of the LASTINPUTINFO
    struct_lastinputinfo = LASTINPUTINFO()
    
    #Set the structure size
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    
    #Call GetLastInputInfo to fill the structure with the last input timestamp
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))
    
    #Get the total time (in milliseconds) that the system has been running
    run_time = kernel32.GetTickCount()
    
    #Calculate the elapsed time since the last user input
    elapsed = run_time - struct_lastinputinfo.dwTime

    print(f"[*] It's been {elapsed} milliseconds since the last input event.")
    
    # Return the elapsed time
    return elapsed

#variable for using counting process
keystrokes = 0
mouse_clicks = 0
double_clicks = 0


def get_key_press():
    """Class document"""
    #Access global counters for mouse clicks and keystrokes
    global mouse_clicks
    global keystrokes

    #Iterate through all possible virtual key codes (0x00–0xFF)
    for i in range(0, 0xFF):
       #Check if the key was pressed since the last call
       #-32767 indicates a fresh key press (transition from up → down)
        if user32.GetAsyncKeyState(i) == -32767:

            # Left mouse button
            if i == 0x1:
                mouse_clicks += 1
                return time.time()

            # ASCII keys
            if 1 < i < 127:
                keystrokes += 1
    #If no key or mouse input detected, return None
    return None

def detect_sandbox():
    """class docstring"""
    global mouse_clicks
    global keystrokes
    global double_clicks

    #Assign random thresholds for keystrokes and mouse clicks
    max_keystrokes = random.randint(10, 25)
    max_mouse_clicks = random.randint(5, 25)

     #Maximum allowed time (in seconds) between two clicks to consider them as a double-click
    double_clicks = 0
    max_double_clicks = 0
    double_clicks_threshold = 0.250

    first_double_click = None

    #Maximum idle time (in milliseconds) since last user input
    #If exceeded, it strongly suggests an automated sandbox environment
    max_input_threshold = 30000  # ms

    previous_timestamp = None
    detection_complete = False

    last_input = get_last_input()
    if last_input >= max_input_threshold:
        sys.exit(0)
   #Continuous monitoring loop until sandbox detection criteria are met
    while not detection_complete:
        #Check for new keyboard or mouse input
        keypress_time = get_key_press()
        #If a key or mouse click was detected
        if keypress_time is not None and previous_timestamp is not None:
            #Calculate time elapsed since last input to detect double-clicks
            elapsed = keypress_time - previous_timestamp
 
            #Increment double-click counter if the interval is below threshold
            if elapsed <= double_clicks_threshold:
                double_clicks += 1
            
            #Track the timestamp of the first double-click
            if first_double_click is None:
                first_double_click = time.time()
            else:
                #If too many double-clicks happen too quickly, exit (possible sandbox)
                if double_clicks == max_double_clicks:
                    if keypress_time - first_double_click <= (max_double_clicks *
                                                              double_clicks_threshold):
                        sys.exit(0)
        #If maximum input thresholds are reached, consider sandbox detection complete
        if (keystrokes >= max_keystrokes and
                double_clicks >= max_double_clicks and
                mouse_clicks >= max_mouse_clicks):
            return
         
        #Update previous timestamp for next iteration
        previous_timestamp = keypress_time or previous_timestamp


detect_sandbox()
print("we are ok!")
