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

# songs for testing:
# Flux Pavilion feat. Steve Aoki - Steve French [looks alright, but beats aren't very solitary]
# Gold Top - Uh Oh (Stand Tall Fists Up Remix) [looks amazing, however the bass is SO INTENSE that multiplier needs to be reduced]
# Yeah Yeah Yeahs - Heads Will Roll (A-Trak Version) (JVH-C Remix) [totally awesome]
# TOP $HELF - Run That $hit [god-tier bass-wobbles and juicy hits]
# Jack U x Ekali x Gravez - Mind (Karol Tip Edit) [insane unique bass that demands attention, inspires me to work on bass isolation so I can replicate the frequency of subs in light saturation]
# SAINT WKND x SAINT MOTEL - MY TYPE [good for testing future bass isolation]
# Jake Hill - Snowflake [my good the audio is the bass in this song, no isolation needed, really clear graph]

import pyaudio
import numpy as np
import lifxtools
import math

from colorama import init
init()
from colorama import Fore, Back, Style

from hsv2ansi import hsv2ansi

# ---- settings ----

fade = 100 # in milliseconds
slow_hue = True
vol_multiplier = 6 # 6 - Loud HQ music, 8 - Normal HQ Music or Spotify normalized to 'loud' enviroment, 10 - spotify normalize to 'normal'

# ---- functions ----

# thanks to the commenter "Dima Tisnek" for this elegant solution to clamping:
# https://stackoverflow.com/q/4092528
clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

def set_lights(h,s,v,k,fade,rapid):
    for light in lights:
        light.set_color((h, s, v, k),fade,rapid=rapid)

# ---- script ----

lifx = lifxtools.return_interface(None)
lights = lifx.get_lights()
managedLights = lifxtools.create_managed_lights(lights)

lifxtools.prepare_managedLights(managedLights)

try:
    maxValue = 2**16
    pa=pyaudio.PyAudio()
    stream=pa.open(format=pyaudio.paInt16,channels=2,rate=44100,
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

        volume_cycle_impact = 1 # number is the amount of time to skip into the future when the volume is loud
        hue_y = abs(math.sin(hue + hue*volume_cycle_impact*normLR))

        active_style = hsv2ansi(hue_y,0,0)

        # Histogram mode
        active_blocks = active_style[0] + active_style[1] + bar_activated * bars_active
        # Bar Mode
        # active_blocks = active_style[0] + Back.BLACK + bar_activated * bars_active

        inactive_blocks = Back.BLACK + bar_inactived * (bar_total - bars_active)

        lrString = '{}{}'.format(active_blocks,inactive_blocks)

        print("normLR=[{}] ({})".format(lrString + Style.RESET_ALL,int(normLR*100)))
        # print("---hue=[{}] ({})".format(hueString,hue))

        # flash mode! (loud means bright!)
        h = 65535*(1-hue_y)
        s = 65535*math.cos(1-normLR) # inverse saturation - higher levels = lower saturation
        v = 1 + ((65535-1)*normLR) # regular brightness
        k = 6500

        # blackout mode! (bass seems to feel more natural)
        # h = 65535*hue
        # s = 65535*math.sin(normLR) # regular saturation - higher levels = higher saturation
        # v = 65535*(1-normLR) # inverse brightness - higher levels = lower brightness
        # k = 6500

        set_lights(h,s,v,k,fade,True)

        if (hue < 1):
            if (slow_hue == True): hue += 0.001
            elif (slow_hue == False): hue += 0.01
            else: raise TypeError("slow_hue must be a bool!")
        else:
            hue = 0

        # print("L:%00.02f R:%00.02f"%(peakL*100, peakR*100))
finally:
    lifxtools.restore_managedLights(managedLights)
    Style.RESET_ALL
