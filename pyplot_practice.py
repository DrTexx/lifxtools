import math
import matplotlib.pyplot as plt

# let's say we want 5Hz
# we want x to reach 1
# and we want y to have done 5 cycles

seconds = 1 # the total number of seconds
samplerate = 48000 # the number of data points per second
freq = 20 # the frequency of the signal we're producing

time_between_samples = seconds / samplerate
total_samples = seconds * samplerate

data = []

for n in range(total_samples):
    data.append(math.cos(n))

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

plt.figure()
# plt.plot(x,x)
plt.plot(data)
# plt.plot(x,y2)
# plt.plot(x,y3)
plt.ylabel('more numbers')

plt.show()
