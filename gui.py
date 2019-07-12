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
default_brightness = True
default_color = (58275, 0, 33968, 3500)
bedtime_color = (58275, 3, 18010, 2000)
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

def toggle_light(_light,brightness):
    light_power = _light.get_power()
    if (light_power == 0):
        _light.set_power(brightness)
        if (debug==True): print("{} power set to {}".format(_light.get_label(), brightness))
    elif (light_power > 0):
        _light.set_power(False)
        if (debug==True): print("{} turned off".format(_light.get_label()))
    else:
        print("WIP: power other than True or False not currently supported, using 65535 range is not yet implemented")

def set_light_color(_light,color):
    _light.set_color(color)
    if (debug==True): print("{} color set to {}".format(_light.get_label(),color))

# main function
def main():
    lifx = return_interface()
    devices = lifx.get_lights()
    num_lights = return_num_lights(devices)
    list_devices(devices)
    #blink_devices(devices)

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

            test_text = Label(test_frame,text="Lights discovered")
            test_text.pack()

            light0_frame = Frame(test_frame)
            light0_frame.config(padding=5,relief=SUNKEN)
            light0_frame.pack()

            light0_name = Label(light0_frame, text=str(devices[0].get_label()))
            light0_name.pack(side=LEFT)

            light0_toggle = Button(light0_frame, text="toggle power", command=self.toggle_light_0)
            light0_toggle.pack(side=LEFT)

            light0_reset_color = Button(light0_frame, text="reset color", command=self.reset_color_light_0)
            light0_reset_color.pack(side=LEFT)

            light0_bedtime_color = Button(light0_frame, text="bedtime color", command=self.bedtime_color_light_0)
            light0_bedtime_color.pack(side=LEFT)

            light0_set_white = Button(light0_frame, text="set white", command=self.set_white_light_0)
            light0_set_white.pack(side=LEFT)

            light0_set_red = Button(light0_frame, text="set red", command=self.set_red_light_0)
            light0_set_red.pack(side=LEFT)

        def toggle_light_0(self): toggle_light(devices[0],default_brightness)
        def reset_color_light_0(self): set_light_color(devices[0],default_color)
        def bedtime_color_light_0(self): set_light_color(devices[0],bedtime_color)
        def set_white_light_0(self): set_light_color(devices[0],WHITE)
        def set_red_light_0(self): set_light_color(devices[0],RED)

        def _exit_app(self,event):
            exit()

    app = Window(root)
    root.mainloop()

if __name__=="__main__":
    main()
