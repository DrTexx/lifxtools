import threading
import numpy as np
import pyaudio
from time import sleep, process_time

from colorama import init

init()
from colorama import Fore, Back, Style

# ---- class-specific functions ----
# thanks to the commenter "Dima Tisnek" for this elegant solution to clamping:
# https://stackoverflow.com/q/4092528
clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

# ---- functions ----


def print_bar(
    LightShow_Object, _name, _val, _seg_active, _seg_inactive, _total_segments=100
):

    # check inputed data
    if not (type(_seg_active) == BarSegment or type(_seg_inactive) == BarSegment):
        raise TypeError(
            "active_segment and inactive_segment must be BarSegment objects"
        )
    elif not (0 <= _val <= 1):  # ensure _val is between 0 and 1
        raise ValueError("val must be between 0 and 1, value was", _val)
    else:
        segments_activated = int(_val * _total_segments)

        active_string = _seg_active.gen_segments(segments_activated)
        inactive_string = _seg_inactive.gen_segments(
            _total_segments - segments_activated
        )

        if LightShow_Object.loop_time != None:
            target_Hz = LightShow_Object.packetHz
            actual_Hz = 1 / LightShow_Object.loop_time
            delta_Hz = int(actual_Hz - target_Hz)

            lrString = "({}Hz) ({:>3}Hz Δ) {}=[{}{}{}] ({})".format(
                target_Hz,
                delta_Hz,
                _name,
                active_string,
                inactive_string,
                Style.RESET_ALL,
                int(_val * 100),
            )
            print(lrString)

        # Frequency domain representation


# adapted code from https://pythontic.com/visualization/signals/fouriertransform_fft
def return_FFT(amplitude, samplingFrequency):
    fourierTransform = np.fft.fft(amplitude) / len(amplitude)  # Normalize amplitude
    fourierTransform = fourierTransform[
        range(int(len(amplitude) / 2))
    ]  # Exclude sampling frequency

    tpCount = len(amplitude)
    values = np.arange(int(tpCount / 2))
    timePeriod = tpCount / samplingFrequency
    frequencies = values / timePeriod

    return (frequencies, abs(fourierTransform))


# ---- classes ----


class BarSegment:
    def __init__(self, symbol, fore="", back=""):
        self.symbol = symbol
        self.fore = fore
        self.back = back

    def gen_segments(self, amount):
        return self.fore + self.back + self.symbol * amount + Style.RESET_ALL


class LightShow:
    def __init__(
        self,
        mlifx,
        pyaudio,
        packetHz,
        fade,
        colorCycleHz=0.5,
        color_temp=6500,
        min_brightness=1,
        max_brightness=65535,
        min_saturation=0,
        max_saturation=65535,
        amp_sensitivity=9,
        initial_hue=0,
        hue_cycle_duration=5,
    ):

        self.mlifx = mlifx
        self.pyaudio = pyaudio
        self.packetHz = packetHz
        self.fade = fade
        self.color_temp = color_temp
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_saturation = min_saturation
        self.max_saturation = max_saturation

        self.amp_sensitivity = amp_sensitivity

        self.pa = self.pyaudio.PyAudio()

        self.running = False
        self.threads = self._create_threads()
        self.stream = self._create_stream()
        self.audio_data = np.array([])
        self.audio_norm = 0
        self.audio_proportion = 0
        self.audio_hue_impact = 0.5  # float from 0 .. 1

        self.hue = initial_hue

        self.hue_rel = (
            0
        )  # relative hue (modified by external factors, isolated from normal hue)

        self.hue_min = 0
        self.hue_max = 65535
        self.hue_cycle_duration = hue_cycle_duration  # in seconds

        self.hue_increment = (self.hue_max / self.packetHz) / self.hue_cycle_duration

        self.needs_update = (
            False
        )  # make sure we don't run loops until data needed for those loops is ready

        self.loop_time = None

    def start(self):

        self.running = True  # enable threads
        self.mlifx.prepare()  # save state of all managed lights and power them on
        self._start_threads()
        self.stream.start_stream()

    def stop(self):

        self.running = False  # stop all threads
        self.mlifx.restore()  # restore original state of all managed lights
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        print(Style.RESET_ALL)  # reset ansi escapes

    def _create_threads(self):

        threads = {
            "set_loop": threading.Thread(target=self._set_loop),
            "hue_loop": threading.Thread(target=self._hue_loop),
        }

        return threads

    def _start_threads(self):

        for t in self.threads:
            self.threads[t].start()

    def _set_loop(self):

        while self.running == True:

            if self.needs_update == True:

                t1 = process_time()

                self.audio_norm = np.linalg.norm(self.audio_data) / len(self.audio_data)
                self.audio_proportion = clamp(
                    self.audio_norm / 2 ** self.amp_sensitivity, 0, 1
                )  # normalized audio returning a value between 0 to 1

                # ---- SCRIPT PUT IN HACK-Y ----
                # data_frames = len(self.audio_data)
                # fft_frequencies, fourierTransform = return_FFT(self.audio_data, data_frames)
                # freq_count = 0
                # total_amp = 0
                # for i in range(len(fft_frequencies)):
                #     if (fft_frequencies[i] >= 0 and fft_frequencies[i] <= 60):
                #         freq_count += 1
                #         total_amp += fourierTransform[i]
                #     if (freq_count > 0):
                #         average_amp = total_amp / freq_count
                #     else:
                #         average_amp = 0
                # self.audio_proportion = average_amp/data_frames # todo: look into RMS (Root Mean
                #                                                 # Squared) to potentially fix spikes
                #                                                 # in bass while loud treble
                # self.audio_proportion = clamp(self.audio_proportion*self.amp_sensitivity,0,1)
                # ---- SCRIPT PUT IN HACK-Y ----

                self.hue_rel = self.hue + self.hue * np.sin(
                    self.audio_proportion * self.audio_hue_impact
                )
                # self.hue_rel = self.hue

                self.hue_rel = (
                    self.hue_rel % self.hue_max
                )  # MAGIC PART THAT MAKES THE VALUE WRAP AROUND PERFECTLY

                h, s, v, k = self._intense_HSVK()

                pixel_color = (h, s, v, k)
                # pixel_color = (self.hue, 65535*1, max_brightness*self.audio_proportion, color_temp)
                pixel_empty = (0, 0, 0, k)

                for light in self.mlifx.lights:
                    light.set_color(pixel_color, self.fade, rapid=True)

                for m_tc in self.mlifx.managed_tilechains:
                    m_tc.canvas = np.roll(
                        m_tc.canvas, 1, axis=1
                    )  # shift canvas on axis
                    m_tc.canvas = np.roll(
                        m_tc.canvas, 1, axis=0
                    )  # shift canvas on axis
                    m_tc.paint_line(pixel_color, "y", 0)  # paint line on side of canvas
                    m_tc.paint_line(pixel_color, "x", 0)  # paint line on side of canvas
                    m_tc.paint_line(pixel_color, "y", 7)  # paint line on side of canvas
                    m_tc.paint_line(pixel_color, "x", 7)  # paint line on side of canvas

                    m_tc.update_tilechain()

                self.needs_update = False

                t2 = process_time()

                while (
                    t2 - t1 < 1 / self.packetHz
                ):  # loop until we've waited as long as the packetHz specifies
                    t2 = process_time()

                self.loop_time = t2 - t1

    def _hue_loop(self):

        while self.running == True:

            self.hue = self.hue + self.hue_increment  # add increment

            if self.hue > self.hue_max:
                self.hue = self.hue - self.hue_max
            elif self.hue < self.hue_min:
                self.hue = self.hue + self.hue_max

            sleep(1 / self.packetHz)

    def _stream_callback(self, in_data, frame_count, time_info, flag):

        audio_data = np.frombuffer(in_data, dtype=np.int16)

        self.audio_data = audio_data
        self.needs_update = True

        return (audio_data, pyaudio.paContinue)

    def _create_stream(self):

        stream = self.pa.open(
            format=self.pyaudio.paInt16,
            channels=2,  # todo: this shouldn't be hardcoded
            rate=44100,  # todo: this shouldn't be hardcoded
            input=True,
            stream_callback=self._stream_callback,
        )
        return stream

    def _intense_HSVK(self):

        h = self.hue_rel
        s = (
            self.min_saturation
            + (self.max_saturation - self.min_saturation) * self.audio_proportion
        )  # regular saturation - higher levels = higher saturation
        v = (
            self.min_brightness
            + (self.max_brightness - self.min_brightness) * self.audio_proportion
        )
        k = self.color_temp

        return (h, s, v, k)

    def _whiteout_HSVK(self):

        h = self.hue_rel
        s = self.max_saturation * np.cos(
            self.min_saturation - self.audio_proportion
        )  # inverse saturation - higher levels = lower saturation
        v = (
            self.min_brightness
            + (self.max_brightness - self.min_brightness) * self.audio_proportion
        )
        k = self.color_temp

        return (h, s, v, k)

    def _blackout_HSVK(self):

        h = self.hue_rel
        s = (
            self.min_saturation
            + (self.max_saturation - self.min_saturation) * self.audio_proportion
        )  # regular saturation - higher levels = higher saturation
        v = (
            self.max_brightness
            - (self.max_brightness - self.min_brightness) * self.audio_proportion
        )
        k = self.color_temp

        return (h, s, v, k)

    def _just_red_HSVK(self):

        h = 0
        s = (
            self.min_saturation
            + (self.max_saturation - self.min_saturation) * self.audio_proportion
        )  # regular saturation - higher levels = higher saturation
        v = (
            self.min_brightness
            + (self.max_brightness - self.min_brightness) * self.audio_proportion
        )
        k = self.color_temp

        return (h, s, v, k)
