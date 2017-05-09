import numpy
import pydaqtools as pdt
import matplotlib.pyplot as plt

num_samples = 10000
pwm_freq = 10000
sample_rate = 1000000

# let pydaqtools find daqs installed on system
pdt.daqfind()

# create analog input using first daq installed on system
ai = pdt.analog_input(samplerate=sample_rate)

# create a counter output to generate a pwm signal
co = pdt.counter_output(frequency=pwm_freq)
# start the pwm signal
co.start()

samples = ai.acquire(num_samples)

#optional command to create figure 1(default=1)
plt.figure(1)

#optional command to create a subplot(default=111)
plt.subplot(211)

# calculate estimated acquisition time in milliseconds
acqTime = (float(num_samples) / sample_rate)*1000

# linspace(start, stop, number of steps)
time = numpy.linspace(0, acqTime, num_samples)

plt.ylabel('Voltage')
plt.xlabel('Time(ms)')
plt.grid(True)
plt.plot(time[0:500], samples[0:500])

# select the psd subplot
plt.subplot(2,1,2)

# ignoring plt.psd's return tuple - (pxx, freqs) 
plt.psd( samples, NFFT=len(time), Fs=sample_rate, scale_by_freq=False)
plt.savefig('ai_co_psd.png',dpi=72)
plt.show()

