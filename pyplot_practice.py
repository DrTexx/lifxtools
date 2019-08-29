import math
import matplotlib.pyplot as plt

# let's say we want 5Hz
# we want x to reach 1
# and we want y to have done 5 cycles

seconds = 1 # the total number of seconds
samplerate = 48000 # the number of data points per second
freq = 1 # the frequency of the signal we're producing

time_between_samples = seconds / samplerate
total_samples = seconds * samplerate

time = []
data = []

for n in range(total_samples):
    seconds = n / samplerate
    time.append(seconds)
    data.append(math.cos(seconds*freq*(2*math.pi)))

# y1 = []
# y2 = []
# y3 = []
#
# for n in x:
#     y1.append( 1 + math.sin(n) )
#     y2.append( 1 - math.cos(n) )
#     y3.append( math.tan(n) )

# print(x)
# print(y1)
# print(y2)
# print(y3)

# plt.figure()
# plt.plot(time,data)
# plt.ylabel('more numbers')
# plt.show()

# ------------------------------------------------------------------------------

# Python example - Fourier transform using numpy.fft method
import numpy as np
import matplotlib.pyplot as plotter

# How many time points are needed i,e., Sampling Frequency
samplingFrequency   = 48000 # was 100

# At what intervals time points are sampled
samplingInterval       = 1 / samplingFrequency;

# Begin time period of the signals
beginTime           = 0

# End time period of the signals
endTime             = 10

# Frequency of the signals
signal1Frequency     = 20
signal2Frequency     = 60

# Time points
time        = np.arange(beginTime, endTime, samplingInterval)

# Create two sine waves
amplitude1 = np.sin(2*np.pi*signal1Frequency*time)
amplitude2 = np.sin(2*np.pi*signal2Frequency*time)

# Add the sine waves
amplitude = amplitude1 + amplitude2

# for frame in amplitude:
#     print(frame)

# Frequency domain representation
def return_FFT(amplitude=amplitude,samplingFrequency=samplingFrequency):
    fourierTransform = np.fft.fft(amplitude)/len(amplitude)           # Normalize amplitude
    fourierTransform = fourierTransform[range(int(len(amplitude)/2))] # Exclude sampling frequency

    tpCount     = len(amplitude)
    values      = np.arange(int(tpCount/2))
    timePeriod  = tpCount/samplingFrequency
    frequencies = values/timePeriod

    return(frequencies,abs(fourierTransform))

fft = return_FFT(amplitude=amplitude,samplingFrequency=samplingFrequency)

# for i in range(len(frequencies)):
#     print(frequencies[i],fourierTransform[i])

# only give amplitues for specified frequencies
# for i in range(len(frequencies)):
#     if (frequencies[i] > 30 and frequencies[i] < 70):
#         print(frequencies[i],abs(fourierTransform[i]))

# Create subplot
figure, axis = plotter.subplots(4, 1)
plotter.subplots_adjust(hspace=1)

axis[2].plot(time,amplitude)

# Frequency domain representation
axis[3].set_title('Fourier transform depicting the frequency components')
# axis[3].plot(frequencies, abs(fourierTransform))
axis[3].plot(fft[0], fft[1])
axis[3].set_xlabel('Frequency')
axis[3].set_ylabel('Amplitude')

plotter.show()
