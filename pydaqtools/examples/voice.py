import pydaqtools as pdt
import time
import random
import numpy
pdt.daqfind()

sample_rate = 44100
sample_time = 5 # record voice for sample_time seconds
daqid = 2
num_voices = 1 # number of voices to add to conversation
num_samples = sample_rate * sample_time # samples/second * seconds

speakers = pdt.analog_output(daqid=daqid,channel=(0),samplerate=sample_rate)
mic = pdt.analog_input(daqid=daqid, samplerate=sample_rate)
print 'recording...'
a = mic.acquire(num_samples)
print 'done.'
speakers.output_waveform(a)
temp_a = []
crowd = []
crowd_right = a
crowd_left = []


# loop through the number of voices to add to the crowd
for i in range(num_voices):
    quiet = numpy.zeros(num_samples)
    # get a random value anywhere in the recorded samples as a starting point
    seed = random.randint(0, num_samples)
    # make a copy of the recorded array shifted by seed samples
    temp_a = a[seed:]
    temp_a = numpy.concatenate((temp_a,a[0:seed]))
    
    # add the most recent voice to the rest of the crowd
    for j in range(len(a)):
        crowd_right[j] = crowd_right[j] + temp_a[j]

# make one more copy of the recording - one for left speaker and one for right 
crowd_left = crowd_right[num_samples/10:] # just start at any place in the array
crowd_left = numpy.concatenate((crowd_left,crowd_right[0:num_samples/10]))

#crowd = numpy.concatenate((crowd_left,crowd_right))
crowd = numpy.concatenate((a,quiet))
#speakers.output_waveform(a)
#time.sleep(15)
raw_input('Press enter to stop')
speakers.stop()


