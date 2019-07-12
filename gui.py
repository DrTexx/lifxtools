#!/usr/bin/env python3
# coding=utf-8

# imports
import sys # used for processing CLI arguments
from tkinter import * # for UI
from tkinter.ttk import * # for not ugly UI
from time import sleep # used for delays
from lifxlan import LifxLAN # used for controlling lights
# settings
num_lights = None
default_brightness = True

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
        print("devices[{}] = [label='{}', power={}, color={}])".format(i,device.get_label(),device.get_power(),device.get_color()))
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

def gen_device_list(_devices,_listbox):
    for device in _devices:
        _listbox.insert(END, device.get_label())

def toggle_light(_light,brightness):
    light_power = _light.get_power()
    if (light_power == 0):
        _light.set_power(brightness)
    elif (light_power > 0):
        _light.set_power(False)
    else:
        print("WIP: power other than 0 or 65535 not currently supported")


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

            test_listbox = Listbox(test_frame)
            test_listbox.pack()
            gen_device_list(devices,test_listbox)

            test_button = Button(test_frame, text="toggle light 0", command=self.toggle_light_0)
            test_button.pack()

        def toggle_light_0(self): toggle_light(devices[0],default_brightness)

        def _exit_app(self,event):
            exit()

    app = Window(root)
    root.mainloop()

if __name__=="__main__":
    main()
