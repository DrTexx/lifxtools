# based on code by the brilliant Scott Harden
# original post code is adapted from:
# https://www.swharden.com/wp/2016-07-19-realtime-audio-visualization-in-python/

# note:
# this code is sensitive to the volume of applications on your desktop.
# Although your actual output audio to speakers shouldn't affect math,
# the volume you're outputting from applications will.
# it is recommended to max out the volume in applications such as spotify
# and then adjust your actual desktop output level to a desirable volume

# protip:
# if you're a spotify user, enable normalization and set your volume level to 'Loud'
# this let's you get the most out of your volume and better maintains audio quality.

import pyaudio
import numpy as np
import lifxtools
import math

from colorama import init
init()
from colorama import Fore, Back, Style

from hsv2ansi import hsv2ansi

# settings
fade = 5 # in milliseconds
vol_multiplier = 8 # 6 - Loud HQ music, 8 - Normal HQ Music or Spotify normalized to 'loud' enviroment, 10 - spotify normalize to 'normal'

# thanks to the commenter "Dima Tisnek" for this elegant solution to clamping:
# https://stackoverflow.com/q/4092528
clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

lifx = lifxtools.return_interface(None)
lights = lifx.get_lights()
managedLights = lifxtools.create_managed_lights(lights)

for ml in managedLights:
    ml.ssave()
    ml.light.set_power(True)

try:
    maxValue = 2**16
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=2,rate=44100,
                  input=True, frames_per_buffer=1024)

    hue = 0 # float: 0 .. 1
    while True:
        data = np.frombuffer(stream.read(1024),dtype=np.int16)
        # print(data)

        # dataL = data[0::2]
        # dataR = data[1::2]
        # peakL = np.abs(np.max(dataL)-np.min(dataL))/maxValue
        # peakR = np.abs(np.max(dataR)-np.min(dataR))/maxValue
        # peakLR = (peakL + peakR) / 2
        # print(peakLR*100)

        volume_norm = np.linalg.norm(data)*vol_multiplier
        normLR = clamp((volume_norm / maxValue) / 100, 0, 1)
        # print(normLR)

        bar_total = 100
        bar_activated = "■"
        bar_inactived = "□"

        bars_active = int(normLR*bar_total)

        active_style = hsv2ansi(hue,0,0)

        # Histogram mode
        active_blocks = active_style[0] + active_style[1] + bar_activated * bars_active
        # Bar Mode
        # active_blocks = active_style[0] + Back.BLACK + bar_activated * bars_active

        inactive_blocks = Back.BLACK + bar_inactived * (bar_total - bars_active)

        lrString = '{}{}'.format(active_blocks,inactive_blocks)

        print("normLR=[{}] ({})".format(lrString + Style.RESET_ALL,int(normLR*100)))
        # print("---hue=[{}] ({})".format(hueString,hue))

        h = 65535*hue
        s = 65535*normLR
        v = 65535
        k = 6500

        for light in lights:
            light.set_color((h, s, v, k),fade,rapid=True)

        if (hue < 1):
            hue += 0.001
        else:
            hue = 0

        # print("L:%00.02f R:%00.02f"%(peakL*100, peakR*100))
finally:
    for ml in managedLights:
        ml.sload()
        Style.RESET_ALL