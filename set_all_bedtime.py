#!/home/denver/Applications/lifxtools/bin/python3 -E

from lifxtools import return_interface, bedtime_color

lifx = return_interface(None)
lights = lifx.get_lights()

for light in lights:
    light.set_color(bedtime_color)
