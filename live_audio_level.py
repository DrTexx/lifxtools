# based on code by the brilliant Scott Harden
# original post code is adapted from:
# https://www.swharden.com/wp/2016-07-19-realtime-audio-visualization-in-python/

import pyaudio
import numpy as np
import lifxtools
import math

clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

# settings
fade = 0 # in milliseconds

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

    while True:
        data = np.frombuffer(stream.read(1024),dtype=np.int16)
        print(data)

        # dataL = data[0::2]
        # dataR = data[1::2]
        # peakL = np.abs(np.max(dataL)-np.min(dataL))/maxValue
        # peakR = np.abs(np.max(dataR)-np.min(dataR))/maxValue
        # peakLR = (peakL + peakR) / 2
        # print(peakLR*100)

        volume_norm = np.linalg.norm(data)*10
        normLR = clamp((volume_norm / maxValue) / 100, 0, 1)
        print(normLR)

        for light in lights:
            light.set_color((65535*normLR, 65535*0.5, (65535*normLR)/2, 6500),fade,rapid=True)

        # print("L:%00.02f R:%00.02f"%(peakL*100, peakR*100))
finally:
    for ml in managedLights:
        ml.sload()
