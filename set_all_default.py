#!/home/denver/venvs/lifxtools/bin/python3 -E

from lifxtools import return_interface, default_color

lifx = return_interface(None)
lights = lifx.get_lights()

for light in lights:
    light.set_color(default_color)
