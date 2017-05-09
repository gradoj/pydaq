#!/usr/bin/python
"""
Labjack
"""
#from pkg_resources import resource_filename, resource_string, resource_stream
try:
    import os
    import ctypes
    import numpy
    import math
    import sys
    import pickle
    import time
    import daq
except:
    raise

if os.name == 'nt':
    #ctypes.windll.LoadLibrary("labjackud")
    ljud = ctypes.cdll.labjackud
    #nidaq = ctypes.windll.nicaiu # load the nidaqmx dll for windows
    #nidaq = ctypes.cdll.nidaqmxbase # load the nidaqmx base dll for windows
elif os.name == 'posix':
    pass
    # linux nidaqmx
    #nidaq = ctypes.cdll.LoadLibrary("/usr/local/natinst/nidaqmx/lib/libnidaqmx.so.1.6.0")
    # mac osx nidaqmx base module
    #nidaq = ctypes.cdll.LoadLibrary('/Library/Frameworks/nidaqmxbase.framework/nidaqmxbase')

class pylabjack(daq.daq):
    """
    Labjack daq
    """
    
    def __init__(self, handle='0'):
        """
        DAQ Device ID in the form Dev1, Dev2, etc.
        """
        daq.daq.__init__(self)
        class_name = self.__class__.__name__
        #print "class", class_name, "created"
        '''self.__fillhwinfo(handle=handle)

        

        self.bus = getproductbus(handle)
        self.dll = 'ni'
        self.numai = getnumai(handle)
        self.numao = getnumao(handle)
        self.numdi = getnumdi(handle)
        self.numdo = getnumdo(handle)
        self.numco = getnumco(handle)
        self.numci = getnumci(handle)
        self.model = getdevicenumber(handle)
        self.handle = handle

        #self.dotask = nidotask()
        #self.aitask = niaitask()
        #self.aotask = niaotask()
        self.cotask = nicotask()
        self.citask = nicitask()
        #self.ditask = niditask()
        
        #self.dosactive = []
        '''
    def __del__(self):
        class_name = self.__class__.__name__
             
    def __fillhwinfo(self,
                handle='0'):
        deviceunplugged = 0

        self.simulated = numpy.zeros(1,dtype=numpy.uint32)
        CHK(nidaq.DAQmxGetDevIsSimulated(handle, self.simulated.ctypes.data))
        if(self.simulated):
            #print 'Simulated daq detected.\n'
            #logger.info('Simulated daq detected')
            pass
            
        else:
            #print 'Hardware daq detected.\n'
            #logger.info('Hardware daq detected.')
            pass

        self.serialnumber = numpy.zeros(1,dtype=numpy.uint32)
        nidaq.DAQmxGetDevSerialNum(handle, self.serialnumber.ctypes.data)
        self.serial_number = hex(self.serialnumber)

        if (self.serialnumber == 0):
            #print 'Device Not Connected.\n'
            deviceunplugged = 1

                    
        if os.name == 'nt':
            self.category = getproductcategory(handle=handle)
        else:
            self.category = 0
        
        #print 'Product Category:', ni_cat # returns 14643 or M Series DAQ for the USB6218
        #print ''

        #documentation missing for this
        #producttype = numpy.zeros(10,dtype=numpy.uint32)
        #CHK(nidaq.DAQmxGetDevProductType('Dev2', producttype.ctypes.data, uInt32(10)))
        #print producttype




        if os.name == 'nt':
            self.cserialnumber = numpy.zeros(1,dtype=numpy.uint32)
            #don't run this through CHK just fail and move on
            if(nidaq.DAQmxGetCarrierSerialNum(handle, self.cserialnumber.ctypes.data) == 0):
                pass
            #print 'Carrier Serial Number:', hex(cserialnumber)         
            #print ""   

            #not sure what this is just returns nothing
            #print 'Chassis Modules:'
            #modules = numpy.zeros(1000,dtype=numpy.str_)
            #CHK(nidaq.DAQmxGetDevChassisModuleDevNames(daq, modules.ctypes.data, uInt32(1000)))
            #modules = ''.join(list(modules))
            #print modules + '\n'        
     
        if (deviceunplugged):
            return

        if os.name == 'nt':
            self.atrigger = numpy.zeros(1,dtype=numpy.uint32)
            nidaq.DAQmxGetDevAnlgTrigSupported(handle, self.atrigger.ctypes.data)
            if(self.atrigger):
                pass
            #print 'Analog trigger supported.\n'


        if os.name == 'nt':    
            self.dtrigger = numpy.zeros(1,dtype=numpy.uint32)
            nidaq.DAQmxGetDevDigTrigSupported(handle, self.dtrigger.ctypes.data)
            if(self.dtrigger):
                pass
                #print 'Digital trigger supported.\n' 

                 

        #print 'Analog In Channels:'
        self.aichannels = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevAIPhysicalChans(handle, self.aichannels.ctypes.data, uInt32(1000)))
        self.aichannels = ''.join(list(self.aichannels)).split(', ')
        #print aichannels + '\n'

        if os.name == 'nt':
            self.maxSchRate = numpy.zeros(1,dtype=numpy.float64)
            if(nidaq.DAQmxGetDevAIMaxSingleChanRate(handle, self.maxSchRate.ctypes.data)):
                pass
            else:
                pass
                #print 'Max Single Channel Sample Rate:', maxSchRate
                #print ""

        if os.name == 'nt':
            self.maxMchRate = numpy.zeros(1,dtype=numpy.float64)
            if(nidaq.DAQmxGetDevAIMaxMultiChanRate(handle, self.maxMchRate.ctypes.data)):
                pass
            else:
                pass
                #print 'Max Multi Channel Sample Rate:', maxMchRate
                #print ""

        if os.name == 'nt':
            self.minSamplingRate = numpy.zeros(1,dtype=numpy.float64)
            if(nidaq.DAQmxGetDevAIMinRate(handle, self.minSamplingRate.ctypes.data)):
                pass
            else:
                pass
                #print 'Minimum Sample Rate:', minSamplingRate
                #print ""

        if os.name == 'nt':
            self.simSampling = numpy.zeros(1,dtype=numpy.uint32)
            if(nidaq.DAQmxGetDevAISimultaneousSamplingSupported(handle, self.simSampling.ctypes.data)):
                pass
            else:
                if(self.simSampling):
                    pass
                #print 'Simultaneous sampling supported\n'

        #print 'Analog Out Channels:'
        self.aochannels = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevAOPhysicalChans(handle, self.aochannels.ctypes.data, uInt32(1000)))
        self.aochannels = ''.join(list(self.aochannels)).split(', ')

      

        #print aochannels, '\n'

        #print 'Digital In Lines:'
        self.dils = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevDILines(handle, self.dils.ctypes.data, uInt32(1000)))
        self.dils = ''.join(list(self.dils)).split(', ')
        #print dils, '\n'

        #print 'Digital In Ports:'
        self.dips = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevDIPorts(handle, self.dips.ctypes.data, uInt32(1000)))
        self.dips = ''.join(list(self.dips)).split(', ')
        #print dips, '\n'

        #print 'Digital Out Lines:'
        self.dols = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevDOLines(handle, self.dols.ctypes.data, uInt32(1000)))
        self.dols = ''.join(list(self.dols)).split(', ')
        #print dols, '\n'

        #print 'Digital Out Ports:'
        self.dops = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevDOPorts(handle, self.dops.ctypes.data, uInt32(1000)))
        self.dops = ''.join(list(self.dops)).split(', ')
        #print dops, '\n'


        #print 'Counter Input Channels:'
        self.cichannels = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevCIPhysicalChans(handle, self.cichannels.ctypes.data, uInt32(1000)))
        self.cichannels = ''.join(list(self.cichannels)).split(', ')
        #print cichannels, '\n'


        #print 'Counter Output Channels:'
        self.cochannels = numpy.zeros(1000,dtype=numpy.str_)
        CHK(nidaq.DAQmxGetDevCOPhysicalChans(handle, self.cochannels.ctypes.data, uInt32(1000)))
        self.cochannels = ''.join(list(self.cochannels)).split(', ')
        
        #print cochannels, '\n'





    class analog_output(daq.daq.analog_output):
        def __init__(self,
                     daqclass,
                     channel=('Dev1/ao0',),
                     contfin='fin',
                     minimum=-10.0,
                     maximum=10.0,
                     timeout=10.0,
                     samplerate=10000.0,
                     samplesPerChan=2000,
                     clock='OnboardClock'):
            
            class_name = self.__class__.__name__
            self.channel = channel
            #print "class", class_name, "created"

            if (contfin == 'fin'):
                self.contfin = c.DAQmx_Val_FiniteSamps
            elif(contfin == 'cont'):
                self.contfin = c.DAQmx_Val_ContSamps
            else:
                raise            
            
            self.minimum = float64(minimum)
            self.maximum = float64(maximum)
            self.timeout = float64(timeout)
            #self.bufferSize = uInt32(10)
            #self.pointsToRead = self.bufferSize
            #self.pointsRead = uInt32()
            self.sampleRate = float64(samplerate)
            self.samplesPerChan = uInt64(samplesPerChan)
            
            self.clockSource = ctypes.create_string_buffer(clock)          
            
            self.aotask = niaotask()
            self.aotask.create_channel(self.channel,
                                       self.contfin,
                                       self.minimum, 
                                       self.maximum,
                                       self.sampleRate,
                                       self.samplesPerChan,
                                       self.clockSource)
            
        def __del__(self):
            class_name = self.__class__.__name__
            print "class", class_name, "destroyed" 


        def output_dc(self,voltage):
            self.aotask.write_data(self.channel, voltage)
            
            #tstart = time.time()
            #if self.taskHandle.value != 0:
            #    nidaq.DAQmxStopTask(self.taskHandle)
            #return data
        def output_waveform(self, waveform):
            self.aotask.write_data(self.channel, waveform)



    def __del__(self):
        class_name = self.__class__.__name__
        #print "class", class_name, "destroyed"


    class analog_input(daq.daq.analog_input):
        def __init__(self,
                     daqclass,
                     channel=('Dev1/ai0',),
                     rsediff='rse',
                     contfin='fin',
                     minimum=-10.0,
                     maximum=10.0,
                     timeout=10.0,
                     samplerate=10000.0,
                     samplesperchan=2000,
                     clock='OnboardClock'):
            class_name = self.__class__.__name__
            #print "class", class_name, "created"

            self.chan = channel

            if (rsediff == 'diff'):
                self.rsediff = c.DAQmx_Val_Diff
            elif(rsediff == 'rse'):
                self.rsediff = c.DAQmx_Val_RSE
            else:
                raise

            if (contfin == 'fin'):
                self.contfin = c.DAQmx_Val_FiniteSamps
            elif(contfin == 'cont'):
                self.contfin = c.DAQmx_Val_ContSamps
            else:
                raise
            
            #self.parentdaq = daqclass
            self.minimum = float64(minimum)
            self.maximum = float64(maximum)
            self.timeout = float64(timeout)
            #self.bufferSize = uInt32(10)
            #self.pointsToRead = self.bufferSize
            #self.pointsRead = uInt32()
            self.sampleRate = float64(samplerate)
            self.samplesPerChan = uInt64(samplesperchan)


            self.clockSource = ctypes.create_string_buffer(clock)
            #self.data = numpy.zeros((1000,),dtype=numpy.float64)

            self.aitask = niaitask()

            self.aitask.create_channel(self.chan,
                                                 self.rsediff,
                                                 self.contfin,
                                                 self.minimum,
                                                 self.maximum,
                                                 self.sampleRate,
                                                 self.samplesPerChan,
                                                 self.clockSource)            

        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"


        def acquire(self,num_samples):


            #tstart = time.time()
            #data = self.parentdaq.aitask.get_data(self.chan, num_samples)
            data = self.aitask.get_data(self.chan, num_samples)
            #tstop = time.time()
            #print tstart
            #print tstop
            #acquiretime = tstop - tstart
            #print 'Total Acquisition Time:', acquiretime, 'sec'
            #print num_samples/acquiretime, 'samples/sec'

            return data
        
        def start(self):
            self.aitask.start()
        def stop(self):
            self.aitask.stop()
        def AcquireAndGraph(self,num_samples):
            try:
                import matplotlib.pyplot as plt
                #import scipy.signal.waveforms as waveforms
                import scipy    
            except:
                print 'AcquireAndGraph function requires Matplotlib and Scipy.'
                raise
            y = self.acquire(num_samples)
            #arange(start,stop,step)

            acqTime = (num_samples/self.sampleRate.value)*1000 # turn into ms
            t = scipy.linspace(0,acqTime,num_samples)

            plt.plot(t,y)
            plt.grid(True)
            plt.xlabel('Time(ms)')
            plt.ylabel('Volts')
            plt.title('Voltage Versus Time')
            plt.show()


            """Acquirefig = plt.figure()
            Acquireplt = Acquirefig.add_subplot(111)
            Acquireplt.plot(t,y)

            Acquireplt.grid(True)

            Acquireplt.set_xlabel('Time(ms)')
            Acquireplt.set_ylabel('Volts')
            Acquireplt.set_title('Voltage Versus Time')
            
            plt.savefig('VvsT')
            
            plt.show()   """
            
            return y


    class counter_output(daq.daq.counter_output):
        def __init__(self,
                     daqclass,
                     channel='Dev1/actr0',
                     frequency=100,
                     dutycycle=0.5,
                     delay=0,
                     idlestate='Low'):
            class_name = self.__class__.__name__
            #print "class", class_name, "created"


            
            
            self.pwmchan = channel
            print self.pwmchan
            self.pwmchan = ctypes.create_string_buffer(self.pwmchan)
            self.parentdaq = daqclass
            self.parentdaq.cotask.create_channel(self.pwmchan,
                                                 frequency=frequency,
                                                 dutycycle=dutycycle,
                                                 delay=delay,
                                                 idlestate=idlestate)

            

        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"


            
        def start(self):
            self.parentdaq.cotask.start_channel(self.pwmchan)
            
        def stop(self):
            self.parentdaq.cotask.stop_channel(self.pwmchan)


        def update_pwm(self,frequency,dutycycle):
            self.parentdaq.cotask.update_pwm(self.pwmchan, frequency, dutycycle)              

    class counter_input(daq.daq.counter_input):
        def __init__(self,
                     daqclass,
                     channel='Dev1/actr0',
                     min_val=1.0,
                     max_val=10000.0,
                     edge='rising',
                     meas_method='low_freq_1_ctr',
                     meas_time=1.0,
                     divisor=1):
            
            class_name = self.__class__.__name__
            #print "class", class_name, "created"

            if (edge == 'rising'):
                ni_edge = c.DAQmx_Val_Rising
            elif (edge == 'falling'):
                ni_edge = c.DAQmx_Val_Falling
            else:
                raise

            if (meas_method == 'low_freq_1_ctr'):
                ni_meas_method = c.DAQmx_Val_LowFreq1Ctr
            elif (meas_method == 'high_freq_2_ctr'):
                ni_meas_method = c.DAQmx_Val_HighFreq2Ctr
            elif (meas_method == 'divide_2_ctr'):
                ni_meas_method = c.DAQmx_Val_LargeRng2Ctr
            else:
                raise
            
            self.cichan = channel
            print self.cichan
            self.cichan = ctypes.create_string_buffer(self.cichan)
            self.parentdaq = daqclass
            #create_channel(self, channel, min_val, max_val, edge, meas_method, meas_time, divisor)
            self.parentdaq.citask.create_channel(self.cichan,
                                                 min_val,
                                                 max_val,
                                                 ni_edge,
                                                 ni_meas_method,
                                                 meas_time,
                                                 divisor)

            

        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"


            
        def start(self):
            self.parentdaq.citask.start_channel(self.cichan)
            
        def stop(self):
            self.parentdaq.citask.stop_channel(self.cichan)

        def get_frequency(self, num_samples):
            freq = self.parentdaq.citask.get_frequency(num_samples=num_samples)
            return freq

  

    class digital_output(daq.daq.digital_output):
        def __init__(self,
                     daqclass,
                     channel=('Dev1/port0/line0',),
                     group='ChannelPerLine',
                     samplerate=1.0,
                     samplesPerChan=1):

            class_name = self.__class__.__name__
            #print "class", class_name, "created"
            self.sampleRate = float64(samplerate)
            self.samplesPerChan = uInt64(samplesPerChan)
            #self.clockSource = ctypes.create_string_buffer(clock)

            self.value = 0

            
            #self.parentdaq.dosactive.append(self.value)            
            self.dochan = channel#self.handle + '/' + port + '/' + channel + ':' + '0' 

            self.dotask = nidotask()
            self.dotask.create_channel(self.dochan)

            #CHK(nidaq.DAQmxCreateDOChan(self.parentdaq.doTaskHandle,
            #                            self.dochan,
            #                            "",
            #                            c.DAQmx_Val_ChanForAllLines))

            #CHK(nidaq.DAQmxCfgSampClkTiming(self.PWMtaskHandle,self.clockSource,self.sampleRate,
            #                                c.DAQmx_Val_Rising,c.DAQmx_Val_FiniteSamps,self.samplesPerChan))


            
        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"

            if self.dotask.doTaskHandle.value != 0:
                nidaq.DAQmxStopTask(self.dotask.doTaskHandle)
                nidaq.DAQmxClearTask(self.dotask.doTaskHandle)
            

        def output(self,
                   pinstate=0):
        
            if(isinstance(pinstate,int)):
                self.dotask.set_vals(self.dochan, (pinstate,))
            else:
                self.dotask.set_vals(self.dochan, pinstate)

                  
            """CHK(nidaq.DAQmxWriteDigitalScalarU32(self.PWMtaskHandle,
                                                 uInt32(1),
                                                 float64(1.0),
                                                 uInt32(pinstate),
                                                 #dataout.ctypes.data,
                                                 None))"""


    class digital_input(daq.daq.digital_input):
        def __init__(self,
                     daqclass,
                     channel='Dev1/port0/line0',
                     group='c.DAQmx_Val_ChanPerLine',
                     samplerate=1.0,
                     samplesPerChan=1):

            class_name = self.__class__.__name__
            #print "class", class_name, "created"
            self.sampleRate = float64(samplerate)
            self.samplesPerChan = uInt64(samplesPerChan)
            #self.clockSource = ctypes.create_string_buffer(clock)

            self.value = 0

            
            #self.parentdaq.dosactive.append(self.value)            
            self.dichan = channel 

            self.ditask = niditask()
            self.ditask.create_channel(self.dichan)

            #CHK(nidaq.DAQmxCreateDOChan(self.parentdaq.doTaskHandle,
            #                            self.dochan,
            #                            "",
            #                            c.DAQmx_Val_ChanForAllLines))

            #CHK(nidaq.DAQmxCfgSampClkTiming(self.PWMtaskHandle,self.clockSource,self.sampleRate,
            #                                c.DAQmx_Val_Rising,c.DAQmx_Val_FiniteSamps,self.samplesPerChan))


            
        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"

            if self.ditask.diTaskHandle.value != 0:
                nidaq.DAQmxStopTask(self.ditask.diTaskHandle)
                nidaq.DAQmxClearTask(self.ditask.diTaskHandle)
            

        def get(self,num_points=1):
                   
            
            return self.ditask.get(self.dichan,
                                   points=num_points)
   
                
                  



def daqfind():
    """ Searches for NI Daqs Dev(0-127), cDAQN(0-127), Mod(0-7) 

    Returns a list of valid handles for devices currently
    found on system.
    """
    handles = []
    try:
        import u12
        daq = u12.U12()
    except:
        return handles

    daqs = daq.listAll()

    for i in daqs['localIDList']:
        if i < 9999:
            handles.append(i)
    #print handles
    return handles

def getdevicesimulated(handle='Dev1'):
    simulated = numpy.zeros(1,dtype=numpy.uint32)
    answer = nidaq.DAQmxGetDevIsSimulated(handle, simulated.ctypes.data)
    if (answer == 0): # check for a valid reply
        return simulated

def getproductcategory(handle='Dev1'):
    #ni_cat = resource_filename(__name__, 'data/ni_cat.dat')    
    file = open(ni_cat, 'rb')
    ni_cat = pickle.load(file)
    file.close()

    category = numpy.zeros(1,dtype=numpy.uint32)
    if os.name == 'nt':
        nidaq.DAQmxGetDevProductCategory(handle, category.ctypes.data)
    return ni_cat[str(category[0])]


def getproductbus(handle='Dev1'):
    #ni_bus = resource_filename(__name__, 'data/ni_bus.dat')    
    file = open(ni_bus, 'rb')
    ni_bus = pickle.load(file)
    file.close()

    bus = numpy.zeros(1,dtype=numpy.uint32)
    nidaq.DAQmxGetDevBusType(handle, bus.ctypes.data)
    return ni_bus[str(bus[0])]

def getdevicenumber(handle='Dev1'):
    #ni_dev = resource_filename(__name__, 'data/ni_dev.dat')    
    file = open(ni_dev, 'rb')
    ni_dev = pickle.load(file)
    file.close()

    device = numpy.zeros(1,dtype=numpy.uint32)
    nidaq.DAQmxGetDevProductNum(handle, device.ctypes.data)
    return ni_dev[str(device[0])]

def getnumai(handle='Dev1'):
    aichannels = numpy.zeros(1000,dtype=numpy.str_)
    CHK(nidaq.DAQmxGetDevAIPhysicalChans(handle, aichannels.ctypes.data, uInt32(1000)))          # not supported for this device
        #return int(0)
    aichannels = ''.join(list(aichannels))
    if (len(aichannels) == 0):
        return 0
    aichannels = aichannels.rsplit(', ')
    return len(aichannels)

def getnumao(handle='Dev1'):
    aochannels = numpy.zeros(1000,dtype=numpy.str_)
    CHK(nidaq.DAQmxGetDevAOPhysicalChans(handle, aochannels.ctypes.data, uInt32(1000)))
        # not supported for this device          
        #return int(0)
    
    aochannels = ''.join(list(aochannels))
    if (len(aochannels) == 0):
        return 0
    aochannels = aochannels.rsplit(', ')
    return len(aochannels)

def getnumdi(handle='Dev1'):
    dichannels = numpy.zeros(1000,dtype=numpy.str_)
    if(nidaq.DAQmxGetDevDILines(handle, dichannels.ctypes.data, uInt32(1000))):
        # not supported for this device
        return int(0)
    dichannels = ''.join(list(dichannels))
    if (len(dichannels) == 0):
        return 0        
    dichannels = dichannels.rsplit(', ')
    return len(dichannels)

def getnumdo(handle='Dev1'):
    dochannels = numpy.zeros(1000,dtype=numpy.str_)
    if(nidaq.DAQmxGetDevDOLines(handle, dochannels.ctypes.data, uInt32(1000))):
        # not supported for this device          
        return int(0)
    dochannels = ''.join(list(dochannels))
    if (len(dochannels) == 0):
        return 0        
    dochannels = dochannels.rsplit(', ')
    return len(dochannels)

def getnumco(handle='Dev1'):
    cochannels = numpy.zeros(1000,dtype=numpy.str_)
    if(nidaq.DAQmxGetDevCOPhysicalChans(handle, cochannels.ctypes.data, uInt32(1000))):
        # not supported for this device          
        return int(0)
    cochannels = ''.join(list(cochannels))
    if (len(cochannels) == 0):
        return 0        
    cochannels = cochannels.rsplit(', ')
    return len(cochannels)

def getnumci(handle='Dev1'):
    cichannels = numpy.zeros(1000,dtype=numpy.str_)
    if(nidaq.DAQmxGetDevCIPhysicalChans(handle, cichannels.ctypes.data, uInt32(1000))):
        # not supported for this device          
        return int(0)
    cichannels = ''.join(list(cichannels))
    if (len(cichannels) == 0):
        return 0        
    cichannels = cichannels.rsplit(', ')
    return len(cichannels)     

    


    


