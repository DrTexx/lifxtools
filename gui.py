#!/usr/bin/env python3
# coding=utf-8

# imports
import sys # used for processing CLI arguments
import tkinter as Tk
from time import sleep # used for delays
from lifxlan import LifxLAN # used for controlling lights
# settings
num_lights = None

# configuration
num_lights = 1 # makes discovery much faster when specified

# main function
def main():
    print("Discovering lights...")
    lifx = LifxLAN(num_lights)
    devices = lifx.get_lights()
    i = 0
    for device in devices:
        print("devices[{}] = [label='{}', power={}, color={}])".format(i,device.get_label(),device.get_power(),device.get_color()))
        device.set_power(False,0,True)
        sleep(1)
        device.set_power(True,0,True)
        i+=1

if __name__=="__main__":
    main()
