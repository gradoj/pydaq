"""

"""
try:
    import sys
    import daq
    import numpy
    import math
    import threading
except:
    raise


import pyaudio

global_data = 0
new_data = False

class pysounddaq(daq.daq):
    """ interface for sound using pyAudio
    
    """
    def __init__(self,handle=0):
        """

        """
        daq.daq.__init__(self)
        class_name = self.__class__.__name__
        #print "class", class_name, "created"
        self.sound = pyaudio.PyAudio()
        self.handle = handle
        

        
        self.host_api = self.sound.get_host_api_info_by_index(self.handle)
        self.inputs = self.sound.get_default_input_device_info()
        self.outputs = self.sound.get_default_output_device_info()

        self.__fillhwinfo(handle=handle)
        
        self.bus = self.host_api['name']
        self.dll = 'sound'
        self.numai = self.inputs['maxInputChannels']
        self.ainame = self.inputs['name']
        self.numao = self.outputs['maxOutputChannels']
        self.aoname = self.outputs['name']
        self.numdi = 0
        self.numdo = 0
        self.numci = 0
        self.numco = 0
        self.model = self.inputs['name']
        self.handle = self.host_api['index']        

    def __fillhwinfo(self,
                handle=0):
        FORMAT = pyaudio.paInt16
        looper = True
        i = 44100

        self.defaultai = self.host_api['defaultInputDevice']
        self.defaultao = self.host_api['defaultOutputDevice']
        while (looper == True):
            try:
                looper = self.sound.is_format_supported(i,self.defaultai,1,FORMAT,None,None,FORMAT)
                i = i + 100
            except:    
                self.maxSchRate = i
                looper = False

        looper = True
        i = 44100
        while (looper == True):
            try:
                looper = self.sound.is_format_supported(i,None,None,FORMAT,self.defaultao,1,FORMAT)
                i = i + 100
            except:    
                #print i
                self.maxaoSchRate = i
                looper = False                

        self.aichannels = range(1,self.inputs['maxInputChannels']+1,1)
        self.aochannels = range(1,self.outputs['maxOutputChannels']+1,1)
    class analog_output(daq.daq.analog_output):
        def __init__(self,
                     daqclass,
                     handle=0,
                     channel=(0,),
                     contfin='cont',
                     samplerate=44100,
                     clock='OnboardClock'):
            class_name = self.__class__.__name__
            #print "class", class_name, "created"

            if contfin == 'cont':
                self.finite = False
            else:
                self.finite = True
            self.handle = handle
            self.channel = channel
            self.samplerate = int(samplerate)
            self.num_of_threads = 0
            self.aot=[]
            
        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed" 


        def output_sin(self,freq=1000):
            A1=2000
            freq=float(freq) # frequency of sine in Hertz

            fs = 44100.     # sampling frequency
            chunk = 1024
            T = 1/freq  # period of sine
            StepSize = 1 / fs
            tt = numpy.arange(0,T,StepSize)
            x1 = A1*numpy.sin( (2*math.pi*freq) * (tt) )
            x1 = x1.astype('h')
            
            '''samplespercycle = (1/freq)*fs
            
            chunk = int(samplespercycle)
            data = numpy.zeros(chunk*2,dtype=numpy.int16)
            y = numpy.zeros(chunk,dtype=numpy.int16)
            yy = numpy.zeros(chunk,dtype=numpy.int16)


            #the port audio stream is interleaved
            for i in numpy.arange(chunk):
                yy[i] = 2000*math.sin(2*math.pi*freq*(i/fs))
                #y=yy

            if(len(self.channel) > 1):
                #i = 0
                #for items in zip(yy,y):
                #    for item in items:
                #        data[i] = item
                #        i = i + 1
                data = numpy.ravel(numpy.vstack((y, yy)), order='F')
        
#This can be used to de-interleave data
#return data.reshape(2, len(data)/2, order='FORTRAN')

            else:
                print 'not-interleaving'
                data = yy
            '''
            
            #from matplotlib.pyplot import plot, show
            #plot(tt)
            #show()
            self.aot.append(ao_thread(self.channel,x1,chunk,int(fs)))
        def start(self):
            self.aot[-1].start()
        def stop(self):
        
            for x in self.aot:
                x.join()

        def output_waveform(self, waveform):

            d_len = len(waveform)
            chunk = 1024
            data = numpy.zeros(d_len,dtype=numpy.int16)
                
            if(len(self.channel) > 1):
                y = numpy.zeros(d_len/2,dtype=numpy.uint16)
                yy = numpy.zeros(d_len/2,dtype=numpy.uint16)

                y = waveform[:d_len/2]
                yy = waveform[d_len/2:]                
                print 'interleaving'
                i = 0
                for items in zip(y,yy):
                    for item in items:
                        data[i] = item
                        i = i + 1
            else:
                data = waveform

            
            
            self.aot.append(ao_thread(self.channel,
                                      data,
                                      chunk,
                                      self.samplerate,
                                      self.finite))

            self.aot[-1].start()            

    def __del__(self):
        class_name = self.__class__.__name__
        #print "class", class_name, "destroyed"


    class analog_input(daq.daq.analog_output):
        def __init__(self,
                     daqclass,
                     handle=0,
                     channel=(0,),
                     rsediff='rse',
                     contfin='fin',
                     samplerate=44100):
            class_name = self.__class__.__name__
            #print "class", class_name, "created"
            if contfin == 'cont':
                self.finite = False
            else:
                self.finite = True
            self.handle = handle
            self.channel = channel
            self.samplerate = samplerate
            self.num_of_threads = 0
            self.chunk = 1024
            self.ait=[]
            self.ait.append(ai_thread(self.channel,
                                      self.chunk,
                                      self.samplerate,
                                      self.finite))
            
        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed" 
        def stop(self):
        
            for x in self.ait:
                x.join()
        def start(self):
            self.ait[-1].start()
        def acquire(self,num_samples):
            global global_data
            global new_data
            CHANNELS = 1
            RATE = 44100
            RECORD_SECONDS = 5
            
            self._stopevent = threading.Event()
            self._sleepperiod = 1.0

            self.chunk = num_samples

            #self.p = pyaudio.PyAudio()

            #FORMAT = pyaudio.paInt16
            '''self.stream = self.p.open(format = FORMAT,
                            channels = len(self.channel), 
                            rate = self.samplerate, 
                            input = True,
                            output = False,
                            frames_per_buffer = self.chunk)
            '''
 
            '''self.ait.append(ai_thread(self.channel,
                                      self.chunk,
                                      self.samplerate,
                                      self.finite))
            '''

            

            # if the user doesn't call start() we'll just call it for him
            #if self.finite == True:
                #data = self.stream.read(self.chunk)
                #self.ait[-1].start()
            #else:
                #self.ait[-1].start()
            
            while(new_data == False):
                pass
            new_data = False

            data = numpy.fromstring(global_data, dtype=numpy.int16)
            return data


        def AcquireAndGraph(self,num_samples):
            try:
                import scipy
                import matplotlib.pyplot as plt
                #import scipy.signal.waveforms as waveforms
            except:
                print 'AcquireAndGraph function requires Matplotlib and Scipy.'
                raise
            CHANNELS = 1
            RATE = 44100
            RECORD_SECONDS = 5
            num_samples = float(num_samples)

            self.chunk = int(num_samples)

            self.p = pyaudio.PyAudio()

            FORMAT = pyaudio.paInt16
            self.stream = self.p.open(format = FORMAT,
                            channels = 1, 
                            rate = RATE, 
                            input = True,
                            output = True,
                            frames_per_buffer = self.chunk)
            data = self.stream.read(self.chunk)
            data = numpy.fromstring(data, dtype=numpy.int16)
            
            acqTime = (num_samples/RATE) # turn into ms

            t = scipy.linspace(0,acqTime,num_samples)

            plt.plot(t,data)
            plt.grid(True)
            plt.xlabel('Time(s)')
            plt.ylabel('Volts')
            plt.title('Voltage Versus Time')
            plt.show()

def sound(waveform, samplerate=44100):
    ''' outputs waveform over speakers
    '''
    finite = True
    d_len = len(waveform)
    chunk = 1024
    channel = 1 # just mono for now
    #data = numpy.zeros(d_len,dtype=numpy.int16)
        
    p = pyaudio.PyAudio()
    if waveform.dtype == 'float32':
        FORMAT = pyaudio.paFloat32
    elif waveform.dtype == 'float64':
        waveform = waveform.astype('f') # go from 64 down to 32 bits
        FORMAT = pyaudio.paFloat32
    elif waveform.dtype == 'int8':
        FORMAT = pyaudio.paInt8
    elif waveform.dtype == 'int16':
        FORMAT = pyaudio.paInt16
    elif waveform.dtype == 'int24':
        FORMAT = pyaudio.paInt24
    elif waveform.dtype == 'int32':
        FORMAT = pyaudio.paInt32
    else:
        print 'Unsupported format.'
        FORMAT = pyaudio.paFloat32
        
    stream = p.open(format = FORMAT,
                    channels = channel, #number of channels
                    rate = int(samplerate), 
                    input = False,
                    output = True,
                    frames_per_buffer = chunk)
    stream.write(waveform,len(waveform))
    
def daqfind():
    """ Used to find what daqs are installed on your system

     Returns dictionary looking like
        {mfg='ni'   manufacturer of daq(currently only ni)ni,sound,
                    advantech,labjack,mcc
         bus='usb'  bus
         id='dev1'
         ai=8
         ao=2
         di=32
         do=32
         cnto=2
         cnti=2
            }
     """

    """for i in range(0,128):
        daq = 'Dev' + str(i)

                sys.stdout.write('Dev')
                print i, '-', cat[str(category[0])], 'found(sw)'
                  if (serialnumber == 0):
                    sys.stdout.write('Dev')
                    print i, '-', cat[str(category[0])], 'found(hw) - Disconnected'
                else:
                    sys.stdout.write('Dev')
                    print i, '-', cat[str(category[0])], 'found(hw)'
                    """
    sound = pyaudio.PyAudio()
    host_api = sound.get_default_host_api_info()
    inputs = sound.get_default_input_device_info()
    outputs = sound.get_default_output_device_info()
    
    #print host_api
    #print inputs
    #print outputs


    
    dev_info = []
    handles = []

    for i in range(0,sound.get_host_api_count()):
        handles.append(i)

    #print '%(id)-8s%(ai)-8s%(ao)-8s%(di)-8s%(do)-8s%(ci)-8s%(co)-8s'% dev_info[nd]
    return handles
        #print sound.get_default_input_device_info()
        #print sound.get_device_count()
        #print sound.get_device_info_by_index(7)
        #sound.get_host_api_count()
        #sound.get_host_api_info_by_index(0)
        #sound.get_default_host_api_info()
        #sound.get_default_input_device_info()
        #sound.get_default_output_device_info()
        

def daqhwinfo(self,
                  handle='0'):
        pass
    
class ao_thread(threading.Thread):
    def __init__ ( self, channel, y, chunk, samplerate, finite=False):
        
        # channel is really number of channels
        self.channel = len(channel)
        print 'self.channel: ', self.channel
        self.samplerate = samplerate
        self._stopevent = threading.Event()
        self._sleepperiod = 4.5
        self.finite = finite
        self.y = y
        self.chunk = 1024#chunk

        self.p = pyaudio.PyAudio()

        FORMAT = pyaudio.paInt16
        #FORMAT = pyaudio.paFloat32
        

        self.stream = self.p.open(format = FORMAT,
                        channels = self.channel, #number of channels
                        rate = self.samplerate, 
                        input = False,
                        output = True,
                        frames_per_buffer = chunk)


        threading.Thread.__init__(self)

       
    def run(self):
        while not self._stopevent.isSet():
            #self.stream.write(self.y,self.chunk)
            
            
            #for i in range(0,len(self.y),1024):
                #self.stream.write(self.y[i:i+1023],1024)
            self.stream.write(self.y,len(self.y))
            if (self.finite == True):
                self._stopevent.set()

            #self._stopevent.wait(self._sleepperiod)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)    


class ai_thread(threading.Thread):
    def __init__ ( self, channel, chunk, samplerate, finite=False):
        
        # channel is really number of channels
        self.channel = len(channel)
        #print 'self.channel: ', self.channel
        self.samplerate = samplerate
        self._stopevent = threading.Event()
        self._sleepperiod = 4.5
        self.finite = finite
        
        self.chunk = 1024#chunk

        self.p = pyaudio.PyAudio()

        FORMAT = pyaudio.paInt16
        #FORMAT = pyaudio.paFloat32
        

        '''self.stream = self.p.open(format = FORMAT,
                        channels = self.channel, #number of channels
                        rate = samplerate, 
                        input = False,
                        output = True,
                        frames_per_buffer = chunk)
        '''
        self.stream = self.p.open(format = FORMAT,
                        channels = self.channel, 
                        rate = self.samplerate, 
                        input = True,
                        output = False,
                        frames_per_buffer = self.chunk)

        threading.Thread.__init__(self)

       
    def run(self):
        while not self._stopevent.isSet():
            #self.stream.write(self.y,self.chunk)
            
            
            #for i in range(0,len(self.y),1024):
                #self.stream.write(self.y[i:i+1023],1024)
            #self.stream.write(self.y,len(self.y))
            global global_data
            global new_data
            global_data = self.stream.read(self.chunk)
            new_data = True
            if (self.finite == True):
                self._stopevent.set()

            #self._stopevent.wait(self._sleepperiod)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)    

