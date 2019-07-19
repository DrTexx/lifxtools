'''
lifxtools package
'''
print("lifxtools/__init__.py")

# imports
from tkinter import * # for UI
from tkinter.ttk import * # for not ugly UI
from time import sleep # used for delays
from lifxlan import LifxLAN, RED, WHITE # used for controlling lights

# settings
num_lights = None # makes discovery much faster when specified instead of none
default_color = (58275, 0, 33968, 3500) # roughly 50% brightness at 3500k
bedtime_color = (58275, 0, 18010, 2000) # roughly 25% brightness at 2000k
live_data = True
debug = True

# functions
def return_interface(num_lights,debug=False):

    try:
        if (debug == True): print("[ light discovery ] starting...")
        if (num_lights != None): print("WARNING: num_lights is not None. Make sure it is set to your actual number of devices or you will likely have issues!")
        lifx = LifxLAN(num_lights)
        return(lifx)

    except:
        raise Error("[ light discovery ] ERROR!")

    finally:
        if (debug == True): print("[ light discovery ] finished!")

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

def list_lights(_lights,debug=False):
    try:
        if (debug == True): print("[ list lights ] started...")
        for light in _lights: print("[{}] power:{} color:{} infrared:{}".format(light.get_label(), light.get_power(), light.get_color(), light.get_infrared()))
    except:
        if (debug == True): print("[ list lights ] ERROR!")
    finally:
        if (debug == True): print("[ list lights ] finished!")

def get_light_color(_light): return(_light.get_color())
def get_light_brightness(_light): return(get_light_color(_light)[2])
def blink_light(_light,delay=1):
    _light.set_power(False,rapid=True)
    sleep(delay)
    _light.set_power(True,rapid=True)

def get_lights(_interface,debug=False):

    try:
        if (debug == True): print("[ get lights ] started...")
        return(_interface.get_lights())

    except:
        if (debug == True): print("[ get lights ] ERROR!")

    finally:
        if (debug == True): print("[ get lights ] finished!")

class managedLight:

    def __init__(self,_light,debug=False):
        if (debug == True): print("creating a new managedLight...")
        self.light = _light
        self.power = None
        self.color = None
        self.infrared = None

    def ssave(self):
        '''save light state inside of class'''
        self.power = self.light.get_power()
        self.color = self.light.get_color()
        #self.infrared = self.light.get_infrared()

    def sload(self):
        '''load light state last saved inside of class'''
        self.light.set_color(self.color)
        self.light.set_power(self.power)
        #self.light.set_infrared(self.infrared)

    def sexport(self):
        '''export light state to outside class'''
        pass

    def simport(self):
        '''import light state from outside class'''
        pass

    def print_saved_state(self):
        '''print the saved state of the light'''
        print("[{} (saved)] power:{} color:{} infrared:{}".format(self.light.get_label(), self.power, self.color, self.infrared))
