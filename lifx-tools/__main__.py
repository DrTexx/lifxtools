#!/usr/bin/env python3
# coding=utf-8

# imports
import sys # used for processing CLI arguments
from tkinter import * # for UI
from tkinter.ttk import * # for not ugly UI
from time import sleep # used for delays
from lifxlan import LifxLAN, RED, WHITE # used for controlling lights
# settings
num_lights = None
default_color = (58275, 0, 33968, 3500) # roughly 50% brightness at 3500k
bedtime_color = (58275, 0, 18010, 2000) # roughly 25% brightness at 2000k
live_data = True
debug = True

# configuration
#num_lights = 1 # makes discovery much faster when specified

# functions
def return_interface():
    print("Discovering lights...")
    if (num_lights != None): print("WARNING: num_lights is not None. Make sure it is set to your actual number of devices or you will likely have issues!")
    return(LifxLAN(num_lights))

def return_num_lights(devices):
    if (num_lights != None):
        return(num_lights)
    else:
        return(len(devices))

def list_devices(devices):
    i = 0
    for device in devices:
        if (debug==True): print("devices[{}] = [label='{}', power={}, color={}])".format(i,device.get_label(),device.get_power(),device.get_color()))
        i += 1

def blink_devices(devices):
    """ blink all devices found one-by-one """
    for device in devices:
        original_power = device.get_power()

        device.set_power(False,0.1)
        sleep(0.5)
        device.set_power(True,0.1)
        sleep(0.5)

        device.set_power(original_power)

def toggle_light(_light):
    light_power = _light.get_power()
    if (light_power == 0):
        _light.set_power(True)
        if (debug==True): print("{} turned on".format(_light.get_label()))
    elif (light_power > 0):
        _light.set_power(False)
        if (debug==True): print("{} turned off".format(_light.get_label()))
    else:
        print("WIP: power other than True or False not currently supported, using 65535 range is not yet implemented")

def set_light_color(_light,color):
    _light.set_color(color)
    if (debug==True): print("{} color set to {}".format(_light.get_label(),color))

def get_light_color(_light): return(_light.get_color())
def get_light_brightness(_light): return(get_light_color(_light)[2])

# main function
def main():
    lifx = return_interface()
    devices = lifx.get_lights()
    num_lights = return_num_lights(devices)
    list_devices(devices)
    # blink_devices(devices)

    root = Tk()

    class Window(Frame):

        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.master = master
            self._init_window()

        def _init_window(self):
            m = self.master
            m.title = "Lifx Tk Controller"

            test_frame = Frame(m)
            test_frame.pack()

            live_data_frame = Frame(test_frame)
            live_data_frame.pack()

            live_data_checkbox = Checkbutton(live_data_frame, text="Enable live data", var=live_data)
            live_data_checkbox.var = live_data
            live_data_checkbox.pack()

            test_text = Label(test_frame,text="Lights discovered")
            test_text.pack()

            self.light_settings = []
            i = 0
            for device in devices:
                self.light_settings.append({'device': device, 'frame': Frame(test_frame)}) # add frames and all relevant things here
                # configure frames and relevant items here
                self.light_settings[i]['frame'].config(padding=5,relief=SUNKEN)
                self.light_settings[i]['frame'].pack()

                _light_device = self.light_settings[i]['device']
                _light_frame = self.light_settings[i]['frame']

                light_label = Label(_light_frame, text=str(_light_device.get_label()))
                light_label.pack(side=LEFT)

                light_toggle = Button(_light_frame, text="toggle power", command=lambda: toggle_light(_light_device))
                light_toggle.pack(side=LEFT)

                # light_brightness = Scale(_light_frame, from_=0, to=65535, orient=HORIZONTAL) # this needs to be accessible outside of for loop, right now it is not
                # light_brightness.pack(side=LEFT)

                light_profile_default = Button(_light_frame, text="default color", command=lambda: set_light_color(_light_device,default_color))
                light_profile_default.pack(side=LEFT)

                light_profile_bedtime = Button(_light_frame, text="bedtime color", command=lambda: set_light_color(_light_device,bedtime_color))
                light_profile_bedtime.pack(side=LEFT)

                light_profile_white = Button(_light_frame, text="white color", command=lambda: set_light_color(_light_device, WHITE))
                light_profile_white.pack(side=LEFT)

                light_profile_red = Button(_light_frame, text="red color", command=lambda: set_light_color(_light_device, RED))
                light_profile_red.pack(side=LEFT)

            if (debug == True): print(self.light_settings)
            light0_frame = self.light_settings[0]['frame'] # TEMPORARY UNTIL CODE BELOW MIGRATED TO ITERABLE FORMAT

            self.light0_brightness = Scale(light0_frame, from_=0, to=65535,orient=HORIZONTAL)
            self.light0_brightness.pack(side=LEFT)

        def _update_brightness(self): self.light0_brightness.set(get_light_brightness(devices[0]))

        def _update_loop(self,ms_per_loop=1000):
            if (live_data == True):
                self._update_brightness()
            self.after(ms_per_loop,self._update_loop) # repeat _update_loop()

        def _exit_app(self,event):
            exit()

    app = Window(root)
    app._update_loop() # must be before main loop
    root.mainloop()

if __name__=="__main__":
    main()
