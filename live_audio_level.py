#!/home/denver/venvs/lifxtools/bin/python3 -E

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

import numpy as np
import lifxtools
from time import sleep
from ManagedTilechain import ManagedTilechain
import math

from colorama import init
init()
from colorama import Fore, Back, Style

from hsv2ansi import hsv2ansi

# ---- settings ----

fade = 0 # in milliseconds
slow_hue = True
min_brightness = 1 # default value - 1 (if this is 0 responsiveness might be impacted negatively)
max_brightness = 65535*0.25   # default value - 65535
vol_multiplier = 6 # 6 - Loud HQ music, 8 - Normal HQ Music or Spotify normalized to 'loud' enviroment, 10 - spotify normalize to 'normal'
update_Hz = 60 # 120 is default, low-spec PC's need lower Hz, light can't handle Hz too high and crash intermitently
                # note: tilechains take a lot more processing power to do realtime music-vis

# ---- functions ----

# thanks to the commenter "Dima Tisnek" for this elegant solution to clamping:
# https://stackoverflow.com/q/4092528
clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

def set_lights(h,s,v,k,fade,rapid):
    for light in lights:
        light.set_color((h, s, v, k),fade,rapid=rapid)

def print_bar(_name,_val,_seg_active,_seg_inactive,_total_segments=100):

    # check inputed data
    if not (type(_seg_active) == BarSegment or type(_seg_inactive) == BarSegment):
        raise TypeError("active_segment and inactive_segment must be BarSegment objects")
    elif not (0 <= _val <= 1): # ensure _val is between 0 and 1
        raise ValueError("val must be between 0 and 1")
    else:
        segments_activated = int(_val*_total_segments)

        active_string = _seg_active.gen_segments(segments_activated)
        inactive_string = _seg_inactive.gen_segments(_total_segments - segments_activated)

        lrString = "{}=[{}{}{}] ({})".format(_name,active_string, inactive_string, Style.RESET_ALL, int(_val*100))

        print(lrString)

        # Frequency domain representation
# adapted code from https://pythontic.com/visualization/signals/fouriertransform_fft
def return_FFT(amplitude,samplingFrequency):
    fourierTransform = np.fft.fft(amplitude)/len(amplitude)           # Normalize amplitude
    fourierTransform = fourierTransform[range(int(len(amplitude)/2))] # Exclude sampling frequency

    tpCount     = len(amplitude)
    values      = np.arange(int(tpCount/2))
    timePeriod  = tpCount/samplingFrequency
    frequencies = values/timePeriod

    return(frequencies,abs(fourierTransform))

# def callback(in_data, frame_count, time_info, status):
#     data = np.frombuffer(audio.stream.read(1024),dtype=np.int16)
#     return (data, pyaudio.paContinue)

fulldata = np.array([])

def callback(in_data, frame_count, time_info, flag):
    global b,a,fulldata #global variables for filter coefficients and array
    data = np.frombuffer(in_data, dtype=np.float32)

    #do whatever with data, in my case I want to hear my data filtered in realtime
    print("reading!")
    # data = signal.filtfilt(b,a,data,padlen=200).astype(np.float32).tostring()

    fulldata = np.append(fulldata,data) #saves filtered data in an array
    return (data, pyaudio.paContinue)

# def callback(in_data, frame_count, time_info, flag):
#     global b,a,fulldata #global variables for filter coefficients and array
#     audio_data = np.fromstring(in_data, dtype=np.float32)
#     #do whatever with data, in my case I want to hear my data filtered in realtime
#     audio_data = signal.filtfilt(b,a,audio_data,padlen=200).astype(np.float32).tostring()
#     fulldata = np.append(fulldata,audio_data) #saves filtered data in an array
#     return (audio_data, pyaudio.paContinue)

# ---- classes ----

class BarSegment:

    def __init__(self,symbol,fore="",back=""):
        self.symbol = symbol
        self.fore = fore
        self.back = back

    def gen_segments(self,amount):
        return(self.fore + self.back + self.symbol * amount + Style.RESET_ALL)

# ---- script ----

lifx = lifxtools.return_interface(None)
lights = lifx.get_devices()
lifxtools.list_lights(lights)
# lights = lifx.get_devices_by_group("Office").get_device_list()
# lights = [lifx.get_device_by_name("Proto Tile")]
tilechains = lifx.get_tilechain_lights()

# remove tilechains from normal light list
for light_n in range(len(lights)):
    if (lights[light_n] in tilechains):
        lights.remove(lights[light_n])

# create and prepare (save state of) managed lights
managedLights = lifxtools.create_managed_lights(lights)
lifxtools.prepare_managedLights(managedLights)

# set flag true if there are any tilechains found
tilechains_present = len(tilechains) > 0

if (tilechains_present == True):
    tilechain = tilechains[0]
    m_tc = ManagedTilechain(tilechain)

g_data = np.array([])

def callback(in_data, frame_count, time_info, flag):
    global g_data #global variables for filter coefficients and array
    # data = np.frombuffer(stream.read(1024),dtype=np.int16,exception_on_overflow=False)
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    #do whatever with data, in my case I want to hear my data filtered in realtime
    # audio_data = signal.filtfilt(b,a,audio_data,padlen=200).astype(np.float32).tostring()
    g_data = audio_data #saves filtered data in an array
    return (audio_data, pyaudio.paContinue)

import pyaudio
pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=2,
    rate=44100,
    input=True,
    stream_callback=callback
)
stream.start_stream()

try:
    maxValue = 2**16

    active_segment = BarSegment("■") # todo: this is a bit wasteful, revise this later
    inactive_segment = BarSegment("□")


    hue = 0 # float: 0 .. 1

    i = 0
    y = 0
    x = 0
    if (tilechains_present == True):
        y_max = len(m_tc.canvas) - 1
        x_max = len(m_tc.canvas[0]) - 1

    while stream.is_active():
        # data = np.frombuffer(stream.read(1024),dtype=np.int16,exception_on_overflow=False)
        data = g_data
        # amplitude = np.frombuffer(audio.stream.read(1024),dtype=np.array)

        # dataL = data[0::2]
        # dataR = data[1::2]
        # peakL = np.abs(np.max(dataL)-np.min(dataL))/maxValue
        # peakR = np.abs(np.max(dataR)-np.min(dataR))/maxValue

        # def redraw_figure():
        #     plt.draw()
        #     plt.pause(0.00001)
        #
        # print(data)
        # import matplotlib.pyplot as plt
        data_frames = len(data) # the number of frames in the captured audio data
        time = np.arange(0,data_frames) # an array from 0 to the total number of frames captured for this loop
        # figure, axis = plt.subplots(4, 1)
        # print(type(time))
        # print(type(data))
        # axis[0].plot(time, data)
        # # redraw_figure()
        # i = i + 1
        # if i > 2:
        #     input()


        volume_norm = np.linalg.norm(data) # normalize audio level
        volume_norm_multiplied = volume_norm*vol_multiplier
        normLR = clamp((volume_norm_multiplied / maxValue) / 100, 0, 1) # clamp audio level

        volume_cycle_impact = 1 # number is the amount of time to skip into the future of the hue cycle when the volume is loud

        hue_y = abs(math.sin(hue + hue*volume_cycle_impact*normLR))

        hue_y_ansi = hsv2ansi(hue_y,0,0)

        # active_segment.styles[0] = hue_y_ansi[0] # restyle segment to new hue
        # active_segment.styles[1] = hue_y_ansi[1] # restyle segment to new hue
        # inactive_segment.styles[0] = hue_y_ansi[0] # restyle segment to new hue
        # inactive_segment.styles[1] = Back.BLACK

        active_segment.fore, active_segment.back = (hue_y_ansi)
        inactive_segment.fore, inactive_segment.back = (hue_y_ansi[0], Back.BLACK)
        # print_bar("normLR",normLR,active_segment,inactive_segment)
        # print_bar("peakL",peakL,active_segment,inactive_segment)
        # print_bar("peakR",peakR,active_segment,inactive_segment)

        active_bass = BarSegment("■") # todo: this is a bit wasteful, revise this later
        inactive_bass = BarSegment("□")
        active_bass.fore, active_segment.back = (Fore.BLACK, Back.WHITE)
        inactive_bass.fore, inactive_segment.back = (Fore.WHITE, Back.BLACK)

        # fft_frequencies, fourierTransform = return_FFT(data, data_frames)
        #
        # freq_count = 0
        # total_amp = 0
        #
        # for i in range(len(fft_frequencies)):
        #     if (fft_frequencies[i] >= 0 and fft_frequencies[i] <= 150):
        #         freq_count += 1
        #         total_amp += fourierTransform[i]
        #
        #     if (freq_count > 0):
        #         average_amp = total_amp / freq_count
        #     else:
        #         average_amp = 0

        # normLR = average_amp/data_frames # todo: look into RMS (Root Mean
                                         # Squared) to potentially fix spikes
                                         # in bass while loud treble
        # print_bar("0-60Hz",normLR,active_bass,inactive_bass)
        # print_bar("0-60Hz",normLR,active_segment,inactive_segment)

        print_bar("normLR",normLR,active_segment,inactive_segment)

        # print(average_amp,freq_count) # print reported average amplitude

        # flash mode! (loud means bright!)
        h = 65535*hue_y
        s = 65535*math.cos(1-normLR) # inverse saturation - higher levels = lower saturation
        v = min_brightness + ((max_brightness-min_brightness)*normLR) # regular brightness
        # v = 65535*0.5
        k = 6500

        # whiteout mode!
        # h = 65535*(1-hue_y)
        # s = 65535*math.cos(1-normLR) # inverse saturation - higher levels = lower saturation
        # v = 1 + ((65535-1)*normLR) # regular brightness
        # k = 6500

        # blackout mode! (bass seems to feel more natural)
        # h = 65535*hue
        # s = 65535*math.sin(normLR) # regular saturation - higher levels = higher saturation
        # v = 65535*(1-normLR) # inverse brightness - higher levels = lower brightness
        # k = 6500

        for light in lights:
            light.set_color((h,s,v,k),fade,True)

        # paint by pixel index - do for each music sample taken
        # pixel_color = (0, 0, 0, 6500)

        # paint pixel at x,y
        # pixel_color = (65535*hue, 65535*1, 65535*normLR, 6500)
        # m_tc.paint_pixel(pixel_color, x, y)
        # if (y < y_max): # if x is not maxed
        #     if (x < x_max):
        #         x += 1 # add 1 to y
        #     else:
        #         y += 1
        #         x = 0
        # else:
        #     y = 0

        # scan amplitude along x
        # pixel_color = (65535*hue_y, 65535*normLR, (65535*0.1)+(65535*0.9)*normLR, 6500)
        # pixel_white = (0, 0, (65535*0.1)+(65535*0.9)*normLR, 6500)
        # m_tc.paint_line(pixel_color,'x',y-1)
        # m_tc.paint_line(pixel_white,'x',y)
        # if (y < y_max):
        #     y += 1
        # else:
        #     y = 0

        if (tilechains_present == True):
            pixel_color = (65535*hue, 65535*1, max_brightness*normLR, 6500)
            pixel_empty = (0, 0, 0, 6500)
            # m_tc.canvas = np.roll(m_tc.canvas, 1, axis=1) # shift canvas on axis
            # m_tc.canvas = m_tc._gen_empty_frame()
            m_tc.paint_line(pixel_color,'y',0) # paint line on side of canvas
            m_tc.paint_line(pixel_color,'x',0) # paint line on side of canvas
            m_tc.paint_line(pixel_color,'y',7) # paint line on side of canvas
            m_tc.paint_line(pixel_color,'x',7) # paint line on side of canvas
            # m_tc.paint_line(pixel_color,'y',7) # paint line on side of canvas
            # # m_tc.paint_line(pixel_empty,'y',1)
            # # m_tc.paint_line(pixel_empty,'x',2)
            # # m_tc.paint_line(pixel_empty,'x',3)
            # # m_tc.paint_line(pixel_empty,'x',4)
            # # m_tc.paint_line(pixel_empty,'x',5)

            m_tc.update_tilechain()

        sleep(1/update_Hz)

        # increment or reset hue
        if (hue < 1):
            if (slow_hue == True): hue += 0.001
            elif (slow_hue == False): hue += 0.01
            else: raise TypeError("slow_hue must be a bool!")
        else:
            hue = 0

        # print("L:%00.02f R:%00.02f"%(peakL*100, peakR*100))
finally:
    lifxtools.restore_managedLights(managedLights)
    stream.stop_stream()
    stream.close()
    pa.terminate()
    Style.RESET_ALL
