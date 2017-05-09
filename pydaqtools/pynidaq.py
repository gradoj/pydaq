#!/usr/bin/python
"""
National Instruments USB-6218 32-Input, 16-bit DAQ
"""
#from pkg_resources import resource_filename
try:
    import pkgutil
    import os
    import ctypes
    import numpy
    import math
    import sys
    import pickle
    import time
    import ni_consts as c
    import daq
except:
    raise

#import logging
#import logging.config
#logging.config.fileConfig("logging.conf")
#logger = logging.getLogger("daqLog")



#>>> find_library('nidaqmxbase')
#'/Library/Frameworks/nidaqmxbase.framework/nidaqmxbase'
if os.name == 'nt':
    nidaq = ctypes.windll.nicaiu # load the nidaqmx dll for windows
    #nidaq = ctypes.cdll.nidaqmxbase # load the nidaqmx base dll for windows
elif os.name == 'posix':
    # linux nidaqmx
    nidaq = ctypes.cdll.LoadLibrary("/usr/local/natinst/nidaqmx/lib/libnidaqmx.so.1.6.0")
    # mac osx nidaqmx base module
    #nidaq = ctypes.cdll.LoadLibrary('/Library/Frameworks/nidaqmxbase.framework/nidaqmxbase')
##############################

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
written = int32()
pointsRead = uInt32()

    
def CHK(err):
    #a simple error checking routine
    if err < 0:
        buf_size = 1000
        buf = ctypes.create_string_buffer('\000' * buf_size)
        buf = ctypes.create_string_buffer(buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
        


class pynidaq(daq.daq):
    """
    Tested with National Instruments USB-6218 32-Input, 16-bit DAQ
    """
    
    def __init__(self, handle='Dev1'):
        """
        DAQ Device ID in the form Dev1, Dev2, etc.
        """
        daq.daq.__init__(self)
        class_name = self.__class__.__name__
        #print "class", class_name, "created"
        self.__fillhwinfo(handle=handle)

        

        self.bus = getproductbus(handle)
        self.dll = 'nidaqmx'
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
        #self.cotask = nicotask()
        #self.citask = nicitask()
        #self.ditask = niditask()
        
        #self.dosactive = []
    def __del__(self):
        class_name = self.__class__.__name__
             
    def __fillhwinfo(self,
                handle='Dev1'):
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
    def connect_terms(self, source_ch,destination,modifier=c.DAQmx_Val_DoNotInvertPolarity):
    #DAQmx_Val_DoNotInvertPolarity
    #DAQmx_Val_InvertPolarity 
    #int32 DAQmxConnectTerms (const char sourceTerminal[], const char destinationTerminal[], int32 signalModifiers);
        print ('source:', source_ch)
        print ('destination:', destination)
        src = ctypes.create_string_buffer(source_ch)
        dst = ctypes.create_string_buffer(destination)

        CHK(nidaq.DAQmxConnectTerms(src, dst, modifier))




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
            print ("class", class_name, "destroyed")


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
                print ('AcquireAndGraph function requires Matplotlib and Scipy.')
                return
    
            
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
                     idlestate=c.DAQmx_Val_Low):
            class_name = self.__class__.__name__
            #print "class", class_name, "created"


            
            
            self.pwmchan = channel
            print (self.pwmchan)
            self.pwmchan = ctypes.create_string_buffer(self.pwmchan)
            #self.parentdaq = daqclass
            self.cotask = nicotask()
        
            self.cotask.create_channel(self.pwmchan,
                                                 frequency=frequency,
                                                 dutycycle=dutycycle,
                                                 delay=delay,
                                                 idlestate=idlestate)

            

        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"


            
        def start(self):
            self.cotask.start_channel(self.pwmchan)
            
        def stop(self):
            self.cotask.stop_channel(self.pwmchan)


        def update_pwm(self,frequency,dutycycle):
            self.cotask.update_pwm(self.pwmchan, frequency, dutycycle)              

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
            print (self.cichan)
            self.cichan = ctypes.create_string_buffer(self.cichan)
            #self.parentdaq = daqclass
            self.citask = nicitask()
            #create_channel(self, channel, min_val, max_val, edge, meas_method, meas_time, divisor)
            self.citask.create_channel(self.cichan,
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
            self.citask.start_channel(self.cichan)
            
        def stop(self):
            self.citask.stop_channel(self.cichan)

        def get_frequency(self, num_samples):
            freq = self.citask.get_frequency(num_samples=num_samples)
            return freq

  

    class digital_output(daq.daq.digital_output):
        def __init__(self,
                     daqclass,
                     channel=('Dev1/port0/line0',),
                     group=c.DAQmx_Val_ChanPerLine,
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
                     group=c.DAQmx_Val_ChanPerLine,
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
    nd = 0 # number of daqs

    # load the ni device category dictionary file(translate device
    # category number to human readable words)
    #file = open(ni_cat, 'rb')
    #ni_cat = resource_filename(__name__, 'data/ni_cat.dat')
    
    
    ni_cat = pkgutil.get_data('pydaqtools', 'data/ni_cat.dat')
    #file = open('ni_cat.dat', 'rb')
    cat = pickle.loads(ni_cat)
    #file.close()

    category = numpy.zeros(1,dtype=numpy.uint32)
    #simulated = numpy.zeros(1,dtype=numpy.uint32)
    handles = []

    for i in range(0,127):
        
        # first look for ni instruments with Dev1 or Dev2 etc. Brute force but
        # I don't see any documentation to help.         
        handle = 'Dev' + str(i)
        simulated = getdevicesimulated(handle)
        # if we received a valid answer not an error
        if(simulated < 0):
            #error returned just check next daq
            pass
        elif(simulated == 1):
            # the device is just a software simulated device
            handles.append(handle)
            nd = nd + 1 # inc the number of valid daqs counter
        else:
            # we've found a valid hardware ni daq(just maybe not plugged in)
            serialnumber = numpy.zeros(1,dtype=numpy.uint32)
            nidaq.DAQmxGetDevSerialNum(handle, serialnumber.data[0])

            # this seems to be ni's recommended method. If serial number is
            # zero then device was installed on the system at one time but
            # it is not currently. I'm just going to ignore it.
            if (serialnumber == 0):
                pass
            # finally, a valid, installed ni hardware daq 
            else:
                # add the newly found valid handle to the list
                handles.append(handle)
                nd = nd + 1 # inc the number of valid daqs counter

        # next look for compact chassis'
        handle = 'cDAQ' + str(i)
        simulated = getdevicesimulated(handle)
        if(simulated < 0):
            #error returned just check next daq
            pass
        elif(simulated == 1):
            # the device is just a software simulated device
            pass
        else:
            # we've found a valid hardware ni daq(just maybe not plugged in)
            serialnumber = numpy.zeros(1,dtype=numpy.uint32)
            nidaq.DAQmxGetDevSerialNum(handle, serialnumber.data[0])

            # this seems to be ni's recommended method. If serial number is
            # zero then device was installed on the system at one time byt
            # it is not currently. I'm just going to ignore it.
            if (serialnumber == 0):
                pass
            # finally, a valid, installed ni hardware daq 
            else:
                # add the newly found valid handle to the list it's just a
                # chassis but add it anyways
                handles.append(handle)
                nd = nd + 1

                # found the chassis so search for modules installed              
                for j in range(0,7):
                    handle = 'cDAQ' + str(i) + 'Mod' + str(j)
                    simulated = getdevicesimulated(handle)
                    if(simulated < 0):
                        #error returned just check next daq
                        pass
                    elif(simulated == 1):
                        # the device is just a software simulated device
                        pass
                    else:
                        # we've found a valid hardware module
                        handles.append(handle)
                        
                        nd = nd + 1
    return handles

def getdevicesimulated(handle='Dev1'):
    simulated = numpy.zeros(1,dtype=numpy.uint32)
    simulated = ctypes.c_bool()    
    
    answer = nidaq.DAQmxGetDevIsSimulated(handle, ctypes.byref(simulated))
    if (int(answer) == 0): # check for a valid reply
        return simulated
    return 0

def getproductcategory(handle='Dev1'):
    #ni_cat = resource_filename(__name__, 'data/ni_cat.dat')
    ni_cat = pkgutil.get_data('pydaqtools', 'data/ni_cat.dat')
    #file = open('data/ni_cat.dat', 'rb')
    ni_cat = pickle.loads(ni_cat)
    #file.close()

    category = numpy.zeros(1,dtype=numpy.uint32)
    if os.name == 'nt':
        nidaq.DAQmxGetDevProductCategory(handle, category.ctypes.data)
    return ni_cat[str(category[0])]


def getproductbus(handle='Dev1'):
    #ni_bus = resource_filename(__name__, 'data/ni_bus.dat')
    ni_bus = pkgutil.get_data('pydaqtools', 'data/ni_bus.dat')
    #file = open('data/ni_bus.dat', 'rb')
    ni_bus = pickle.loads(ni_bus)
    #file.close()

    bus = numpy.zeros(1,dtype=numpy.uint32)
    nidaq.DAQmxGetDevBusType(handle, bus.ctypes.data)
    return ni_bus[str(bus[0])]

def getdevicenumber(handle='Dev1'):
    #ni_dev = resource_filename(__name__, 'data/ni_dev.dat')
    ni_dev = pkgutil.get_data('pydaqtools', 'data/ni_dev.dat')
    #file = open('data/ni_dev.dat', 'rb')
    ni_dev = pickle.loads(ni_dev)
    #file.close()

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

    


    
class niditask:
    def __init__(self):
        self.diTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.diTaskHandle)))
        self.numch = 0
        self.ch = {}
        self.datain = []
        
      
        
    def create_channel(self, channel):
        
        for ch in channel:
            chan = ctypes.create_string_buffer(ch)
            print (chan.value)        

            CHK(nidaq.DAQmxCreateDIChan(self.diTaskHandle,
                                        chan,
                                        "",
                                        c.DAQmx_Val_GroupByChannel))
        
    def get(self, channel, points):
        
        self.start()
        bufferSize=uInt32(points*len(channel))

        samps_read = uInt32()
        bytes_per_sample = uInt32()
        self.data = numpy.zeros((points*len(channel),),dtype=numpy.uint8)

        CHK(nidaq.DAQmxReadDigitalLines(self.diTaskHandle,
                                        uInt32(points), #c.DAQmx_Val_Auto,  # samples per channel
                                        float64(10.0),     # timeout
                                        c.DAQmx_Val_GroupByChannel,    # fill mode
                                        self.data.ctypes.data,    # read array
                                        uInt32(bufferSize.value), # size of read array
                                        ctypes.byref(samps_read),    # actual num of samples read
                                        ctypes.byref(bytes_per_sample),     # actual number of bytes per sample
                                        None))
                                        
        self.stop()
        #print 'Samples read: ', samps_read
        #print 'Bytes per Sample: ', bytes_per_sample
        return self.data

    def start(self):
        CHK(nidaq.DAQmxStartTask(self.diTaskHandle))
    def stop(self):
        if self.diTaskHandle.value != 0:
            nidaq.DAQmxStopTask(self.diTaskHandle)
            

class nidotask:
    def __init__(self):
        self.doTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.doTaskHandle)))
        self.numch = 0
        self.ch = {}
        self.dataout = []
    def create_channel(self, channel):

        for ch in channel:
            chan = ctypes.create_string_buffer(ch)
            print (chan.value)        
        
            CHK(nidaq.DAQmxCreateDOChan(self.doTaskHandle,
                                        chan,
                                        "",
                                        c.DAQmx_Val_ChanForAllLines))

    def set_vals(self, channel, output):
        
        self.data = numpy.array(output,dtype=numpy.uint8)
        
        self.sampleswritten = uInt32()        

        CHK(nidaq.DAQmxWriteDigitalLines(self.doTaskHandle,
                                         uInt32(len(output)/len(channel)),            # samples per channel
                                         uInt32(1),            # auto start
                                         float64(10.0),        # timeout
                                         c.DAQmx_Val_GroupByChannel,
                                         self.data.ctypes.data,
                                         ctypes.byref(self.sampleswritten),
                                         None))
        #print 'Samples Written per Channel:', self.sampleswritten
    def start(self):
        CHK(nidaq.DAQmxStartTask(self.doTaskHandle))
    def stop(self):
        if self.doTaskHandle.value != 0:
            nidaq.DAQmxStopTask(self.doTaskHandle)        

class niaitask:
    def __init__(self):
        self.aiTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.aiTaskHandle)))

        
    def create_channel(self, 
                       channel, 
                       rsediff, 
                       contfin, 
                       minimum, 
                       maximum, 
                       samplerate, 
                       samplesperchannel, 
                       clocksource):


        
        for ch in channel:
            chan = ctypes.create_string_buffer(ch)
            print (chan.value)

            CHK(nidaq.DAQmxCreateAIVoltageChan(self.aiTaskHandle,chan,"",rsediff,minimum,maximum,
                c.DAQmx_Val_Volts,None))

        self.pointsToRead = samplesperchannel
        CHK(nidaq.DAQmxCfgSampClkTiming(self.aiTaskHandle,
                                        clocksource,
                                        samplerate,
                                        c.DAQmx_Val_Rising,
                                        contfin,
                                        self.pointsToRead))

        #CHK(nidaq.DAQmxCfgInputBuffer(self.aiTaskHandle,200000))

        

        self.minimum = minimum
        self.maximum = maximum
        self.samplerate = samplerate
        self.samplesperchannel = samplesperchannel
        self.clocksource = clocksource
        self.rsediff = rsediff
        self.contfin = contfin

    def start(self):
        CHK(nidaq.DAQmxStartTask(self.aiTaskHandle))
    def stop(self):
        if self.aiTaskHandle.value != 0:
            nidaq.DAQmxStopTask(self.aiTaskHandle)
            #nidaq.DAQmxClearTask(self.aiTaskHandle)       
        
    def get_data(self, channel, points):        
        # with multiple channels in the task the buffer needs to
        # be increased (bufferSize = pointsToRead * numchannelsInTask)
        self.bufferSize = uInt32(int(points*len(channel)))

        

        #this data array as well needs to be scaled by the number of channels in task
        self.data = numpy.zeros((points*len(channel),),dtype=numpy.float64)
        self.pointsRead = uInt32()
        
        
        CHK(nidaq.DAQmxReadAnalogF64(self.aiTaskHandle,
                                     uInt32(int(points)),#c.DAQmx_Val_Auto (Auto means read all available)
                                     float64(10.0),       # timeout
                                     c.DAQmx_Val_GroupByChannel,
                                     self.data.ctypes.data,
                                     uInt32(self.bufferSize.value),
                                     ctypes.byref(self.pointsRead),None))

        #print "Acquired %d point(s)"%(self.pointsRead.value)
        self.data = self.data.reshape(len(channel),points)

        if self.contfin == c.DAQmx_Val_FiniteSamps:
            self.stop()

        return self.data




class niaotask:
    def __init__(self):
        self.aoTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.aoTaskHandle)))
        self.ch = {}
        self.dataout = []


    def create_channel(self, 
                       channel,
                       contfin,
                       minimum, 
                       maximum,
                       samplerate,
                       samplesperchannel,
                       clocksource):

        for ch in channel:
            chan = ctypes.create_string_buffer(ch)
            print (chan.value)

            
            
            CHK(nidaq.DAQmxCreateAOVoltageChan(self.aoTaskHandle,
                                               chan,
                                               "",
                                               minimum,
                                               maximum,
                                               c.DAQmx_Val_Volts,None))
               
        self.pointsToWrite = samplesperchannel
        CHK(nidaq.DAQmxCfgSampClkTiming(self.aoTaskHandle,
                                        clocksource,#clock source default to internal
                                        samplerate,
                                        c.DAQmx_Val_Rising,
                                        contfin,
                                        self.pointsToWrite))            
        
        self.minimum = minimum
        self.maximum = maximum
        self.samplerate = samplerate
        self.samplesperchannel = samplesperchannel
        self.clocksource = clocksource
        self.contfin = contfin        

    def write_data(self, channel, waveform):



        # The minimum samples per channel is 2 this gives a
        # bit of a problem for output_dc



        try:
            # the data needs to be in the right format here
            # need to do a reshape
            waveform.reshape(len(waveform)*len(waveform[0]) )            
            samplesperchannel = uInt32(len(waveform))
            data = numpy.array(waveform, dtype=numpy.float64)
        except:
            # this is a little dangerous but if the above fails just load
            # a 2 datapoint array
            data = numpy.array([waveform,waveform], dtype=numpy.float64)

        

        #y = numpy.zeros(1000,dtype=numpy.float64)

        # create 1000 evenly spaced values from time=0 to x
        #t = scipy.linspace(0,0.01,1000)
        #f = 1000
        #A = 3

        #y = A*waveforms.square(2*math.pi*f*t,duty=0.5)
        #y = A*waveforms.sawtooth(2*math.pi*f*t,width=0.5)

        
        #for i in numpy.arange(1000):
        #    y[i] = 9.95*math.sin(i*2.0*math.pi*1000.0/16000.0)
        #print len(data)
        #print data


        CHK(nidaq.DAQmxWriteAnalogF64(self.aoTaskHandle,
                                      uInt32(len(data)),  #number of samples per channel
                                      uInt32(1),  #autostart task
                                      float64(10.0), #timeout
                                      c.DAQmx_Val_GroupByChannel,
                                      data.ctypes.data,
                                      None,None))

    def start(self):
        CHK(nidaq.DAQmxStartTask(self.aoTaskHandle))
    def stop(self):
        if self.aoTaskHandle.value != 0:
            nidaq.DAQmxStopTask(self.aoTaskHandle)
            
            
class nicotask:
    def __init__(self):
        self.coTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.coTaskHandle)))
        
        self.numch = 0
        self.ch = {}
        self.dataout = []
       
    def create_channel(self, channel, frequency, dutycycle, delay, idlestate):


        nidaq.DAQmxStopTask(self.coTaskHandle)
        CHK(nidaq.DAQmxCreateCOPulseChanFreq(self.coTaskHandle,channel,"",
                                              c.DAQmx_Val_Hz,
                                              idlestate,
                                              float64(delay), # delay
                                              float64(frequency), # frequency
                                              float64(dutycycle))) # duty cycle
        CHK(nidaq.DAQmxCfgImplicitTiming(self.coTaskHandle,c.DAQmx_Val_ContSamps,uInt64(1000)))        
        #CHK(nidaq.DAQmxStartTask(self.coTaskHandle))

        freq = numpy.zeros(1,dtype=numpy.float64)
        duty = numpy.zeros(1,dtype=numpy.float64)
        freq = frequency
        duty = dutycycle
        self.ch[str(channel)] = self.numch
        self.dataout.append((freq,duty))
        self.numch = self.numch + 1

    def update_pwm(self, channel, frequency, dutycycle):
        index = self.ch[str(channel)]
        self.dataout[index] = (frequency, dutycycle)

        frequency = self.get_task_frequency()
        print (frequency)
        dutycycle = self.get_task_dutycycle()
        print (dutycycle)
        self.sampsWritten = uInt32()
        
        CHK(nidaq.DAQmxWriteCtrFreq(self.coTaskHandle,
                                          uInt32(1), #numSampsPerChan
                                          uInt32(1), #autostart task
                                          c.DAQmx_Val_WaitInfinitely,
                                          c.DAQmx_Val_GroupByChannel,
                                          frequency.ctypes.data,
                                          dutycycle.ctypes.data,
                                          ctypes.byref(self.sampsWritten),
                                          None))
        
    def stop_channel(self, channel):
        CHK(nidaq.DAQmxStopTask(self.coTaskHandle))


    def start_channel(self, channel):
        CHK(nidaq.DAQmxStartTask(self.coTaskHandle))
        
    def get_task_frequency(self):
        
        dataout = numpy.zeros(self.numch,dtype=numpy.float64)
        for i in range(self.numch):
            dataout[i]=self.dataout[i][0]
        return dataout
    def get_task_dutycycle(self):
        
        dataout = numpy.zeros(self.numch,dtype=numpy.float64)
        for i in range(self.numch):
            dataout[i]=self.dataout[i][1]
        return dataout      


class nicitask:
    def __init__(self):
        self.ciTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.ciTaskHandle)))
        
        self.numch = 0
        self.ch = {}
        self.dataout = []
       
    def create_channel(self, channel, min_val, max_val, edge, meas_method, meas_time, divisor):


        #nidaq.DAQmxStopTask(self.ciTaskHandle)
        """int32 DAQmxCreateCIFreqChan (TaskHandle taskHandle,
                                      const char counter[],
                                      const char nameToAssignToChannel[],
                                      float64 minVal,
                                      float64 maxVal,
                                      int32 units,
                                      int32 edge,
                                      int32 measMethod,
                                      float64 measTime,
                                      uInt32 divisor,
                                      const char customScaleName[]);
        """
        CHK(nidaq.DAQmxCreateCIFreqChan(self.ciTaskHandle,
                                        channel,
                                        '', # name to assign to virtual channel
                                        float64(min_val),
                                        float64(max_val),
                                        c.DAQmx_Val_Hz,
                                        edge,
                                        meas_method,
                                        float64(meas_time),
                                        uInt32(divisor),
                                        ''))
                                        

                                        
        CHK(nidaq.DAQmxCfgImplicitTiming(self.ciTaskHandle,c.DAQmx_Val_FiniteSamps,uInt64(1000)))       
        #CHK(nidaq.DAQmxStartTask(self.ciTaskHandle))
        
    def stop_channel(self):
        CHK(nidaq.DAQmxStopTask(self.ciTaskHandle))


    def start_channel(self):
        CHK(nidaq.DAQmxStartTask(self.ciTaskHandle))

    def get_frequency(self, num_samples):
        """int32 DAQmxReadCounterF64 (TaskHandle taskHandle,
                                    int32 numSampsPerChan,
                                    float64 timeout,
                                    float64 readArray[],
                                    uInt32 arraySizeInSamps,
                                    int32 *sampsPerChanRead,
                                    bool32 *reserved);
        """


        self.data = numpy.zeros((num_samples,),dtype=numpy.float64)
        self.pointsRead = uInt32()
        CHK(nidaq.DAQmxReadCounterF64(self.ciTaskHandle,
                                      num_samples,
                                      float64(10.0), #self.timeout,
                                      self.data.ctypes.data,
                                      uInt32(num_samples),
                                      ctypes.byref(self.pointsRead),None))
        self.stop_channel()
        return self.data


