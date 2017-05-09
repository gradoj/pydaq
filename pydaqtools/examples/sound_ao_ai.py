import pydaqtools as pdt
import matplotlib.pyplot as plt
import numpy
import time

daqid=2

sample_rate = 44100
num_samples = sample_rate/10 # 100ms of data

# let pydaqtools find daqs installed on system
pdt.daqfind()

# get an analog output from the sound card
speakers = pdt.analog_output(daqid=daqid,
                             channel=(0))
# output a 1kHz sin wave
speakers.output_sin(freq=1000)

# give it a second to start outputting on the speakers
time.sleep(1)

# grab the default microphone
microphone = pdt.analog_input(daqid=daqid,
                              channel=0,
                              samplerate=sample_rate)

# acquire a seconds worth of samples
samples = microphone.acquire(num_samples)

# stop the sound card from outputting
speakers.stop()

# calculate estimated acquisition time in milliseconds
acqTime = (float(num_samples) / sample_rate)*1000

# linspace(start, stop, number of steps)
time = numpy.linspace(0, acqTime, num_samples)

# plot all the data
plt.subplot(2,1,1)
plt.ylabel('ADCs')
plt.xlabel('Time(ms)')
plt.grid(True)
plt.plot(time, samples)

# zoom in and plot 10ms worth of data
plt.subplot(2,1,2)
plt.ylabel('ADCs')
plt.xlabel('Time(ms)')
plt.grid(True)
plt.plot(time[44:485], samples[44:485])

# save the plot
plt.savefig('sound_ao_ai.png',dpi=72)
# and then pop it up on screen
plt.show()

