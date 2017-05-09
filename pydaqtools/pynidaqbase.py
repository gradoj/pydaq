"""
National Instruments USB-6218 32-Input, 16-bit DAQ
"""
try:
    import pkgutil
    import ctypes
    from ctypes.util import find_library
    import numpy
    import math
    import sys
    import pickle
    import time
    import os
    import ni_consts as c
    import daq
except:
    raise
#nidaq = ctypes.windll.nicaiu # load the DLL
#>>> find_library('nidaqmxbase')
#'/Library/Frameworks/nidaqmxbase.framework/nidaqmxbase'
# chose an implementation, depending on os
if os.name == 'nt': #sys.platform == 'win32':
    #nidaq = ctypes.windll.nicaiu # load the DLL
    nidaq = ctypes.cdll.nidaqmxbase
    #from serialwin32 import *
elif os.name == 'posix':
    ctypes.CDLL("/usr/local/lib/liblvrtdark.so.10.0" , mode=ctypes.RTLD_GLOBAL)
    nidaq = ctypes.cdll.LoadLibrary("/usr/local/lib/libnidaqmxbase.so")

    #nidaq = ctypes.cdll.LoadLibrary('/Library/Frameworks/nidaqmxbase.framework/nidaqmxbase')
    #from serialposix import *
elif os.name == 'java':
    pass
    #from serialjava import *
else:
    raise Exception("Sorry: no implementation for your platform ('%s') available" % os.name)


#import matplotlib.pyplot as plt
#import scipy.signal.waveforms as waveforms
#import scipy


int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
written = int32()
pointsRead = uInt32()


class nicotask:
    def __init__(self):
        self.coTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(self.coTaskHandle)))
        
        self.numch = 0
        self.ch = {}
        self.dataout = []
       
    def create_channel(self, channel, frequency, dutycycle, delay, idlestate):


        nidaq.DAQmxBaseStopTask(self.coTaskHandle)
        CHK(nidaq.DAQmxBaseCreateCOPulseChanFreq(self.coTaskHandle,channel,"",
                                              c.DAQmx_Val_Hz,
                                              idlestate,
                                              float64(delay), # delay
                                              float64(frequency), # frequency
                                              float64(dutycycle))) # duty cycle
        CHK(nidaq.DAQmxBaseCfgImplicitTiming(self.coTaskHandle,c.DAQmx_Val_ContSamps,uInt64(1000)))        
        #CHK(nidaq.DAQmxBaseStartTask(self.coTaskHandle))

        freq = numpy.zeros(1,dtype=numpy.float64)
        duty = numpy.zeros(1,dtype=numpy.float64)
        freq = frequency
        duty = dutycycle
        self.ch[str(channel)] = self.numch
        #self.dataout.append((freq,duty,idlestate,delay))
        self.dataout.append((freq,duty))
        self.numch = self.numch + 1
        self.idlestate = idlestate
        self.delay = delay

    def update_pwm(self, channel, frequency, dutycycle):
        index = self.ch[str(channel)]
        self.dataout[index] = (frequency, dutycycle)

        frequency = self.get_task_frequency()
        print frequency
        dutycycle = self.get_task_dutycycle()
        print dutycycle
        self.sampsWritten = uInt32()
        
        self.stop_channel(channel)
	nidaq.DAQmxBaseClearTask(self.coTaskHandle) 
        CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(self.coTaskHandle)))
        
        CHK(nidaq.DAQmxBaseCreateCOPulseChanFreq(self.coTaskHandle,channel,"",
                                              c.DAQmx_Val_Hz,
                                              self.idlestate,  # this doesn't work properly for multiple tasks
                                              float64(self.delay), # delay
                                              float64(frequency), # frequency
                                              float64(dutycycle))) # duty cycle
        CHK(nidaq.DAQmxBaseCfgImplicitTiming(self.coTaskHandle,c.DAQmx_Val_ContSamps,uInt64(1000))) 
        self.start_channel(channel)
        """CHK(nidaq.DAQmxBaseWriteCtrFreq(self.coTaskHandle,
                                          uInt32(1), #numSampsPerChan
                                          uInt32(1), #autostart task
                                          c.DAQmx_Val_WaitInfinitely,
                                          c.DAQmx_Val_GroupByChannel,
                                          frequency.ctypes.data,
                                          dutycycle.ctypes.data,
                                          ctypes.byref(self.sampsWritten),
                                          None))
        """
        
    def stop_channel(self, channel):
        CHK(nidaq.DAQmxBaseStopTask(self.coTaskHandle))


    def start_channel(self, channel):
        CHK(nidaq.DAQmxBaseStartTask(self.coTaskHandle))
        
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
        CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(self.ciTaskHandle)))
        
        self.numch = 0
        self.ch = {}
        self.dataout = []
       
    def create_channel(self, channel, min_val, max_val, edge, meas_method, meas_time, divisor):


        #nidaq.DAQmxBaseStopTask(self.ciTaskHandle)
        CHK(nidaq.DAQmxBaseCreateCIPeriodChan(self.ciTaskHandle,
                                        channel,
                                        '', # name to assign to virtual channel
                                        float64(min_val), #min val
                                        float64(max_val), #max val
                                        c.DAQmx_Val_Seconds,
                                        edge,
                                        c.DAQmx_Val_LowFreq1Ctr,
                                        float64(0),   #measure time always pass zero
                                        uInt32(1),    #divisor always pass one
                                        ''))
        """int32 DAQmxBaseCreateCIFreqChan (TaskHandle taskHandle,
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
        
        CHK(nidaq.DAQmxBaseCreateCIFreqChan(self.ciTaskHandle,
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
                                        
        """
                                        
        CHK(nidaq.DAQmxBaseCfgImplicitTiming(self.ciTaskHandle,c.DAQmx_Val_FiniteSamps,uInt64(1000)))       
        #CHK(nidaq.DAQmxBaseStartTask(self.ciTaskHandle))
        
    def stop_channel(self):
        CHK(nidaq.DAQmxBaseStopTask(self.ciTaskHandle))


    def start_channel(self):
        CHK(nidaq.DAQmxBaseStartTask(self.ciTaskHandle))

    def get_frequency(self, num_samples):
        """int32 DAQmxBaseReadCounterF64 (TaskHandle taskHandle,
                                    int32 numSampsPerChan,
                                    float64 timeout,
                                    float64 readArray[],
                                    uInt32 arraySizeInSamps,
                                    int32 *sampsPerChanRead,
                                    bool32 *reserved);
        """


        self.data = numpy.zeros((num_samples,),dtype=numpy.float64)
        self.pointsRead = uInt32()
        CHK(nidaq.DAQmxBaseReadCounterF64(self.ciTaskHandle,
                                      num_samples,
                                      float64(10.0), #self.timeout,
                                      self.data.ctypes.data,
                                      uInt32(num_samples),
                                      ctypes.byref(self.pointsRead),None))
        self.stop_channel()
        return self.data

class nidotask:
    def __init__(self):
        self.doTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(self.doTaskHandle)))
        self.numch = 0
        self.ch = {}
        self.dataout = []
    def create_channel(self, channel):

        # The channel is a list but NI requires the channels to be Dev1/ai0,Dev1/ai1,etc
	chan = ''
        for ch in channel:
            chan = chan + ch + ','
        chan = ctypes.create_string_buffer(chan)
        print chan.value    
        
        CHK(nidaq.DAQmxBaseCreateDOChan(self.doTaskHandle,
                                        chan,
                                        "",
                                        c.DAQmx_Val_ChanForAllLines))

    def set_vals(self, channel, output):
        
        #self.data = numpy.array(output,dtype=numpy.uint8)
        
        #self.sampleswritten = uInt32()        
        self.stop()
        CHK(nidaq.DAQmxBaseWriteDigitalScalarU32(self.doTaskHandle,
                                           uInt32(0),            # auto start
                                           float64(10.0),        # timeout
                                           uInt32(output[0]),    # this is only going to work for one sample for now
                                           None))
        self.start()
        """CHK(nidaq.DAQmxBaseWriteDigitalLines(self.doTaskHandle,
                                         uInt32(len(output)/len(channel)),            # samples per channel
                                         uInt32(1),            # auto start
                                         float64(10.0),        # timeout
                                         c.DAQmx_Val_GroupByChannel,
                                         self.data.ctypes.data,
                                         ctypes.byref(self.sampleswritten),
                                         None))
        """
        #print 'Samples Written per Channel:', self.sampleswritten
    def start(self):
        CHK(nidaq.DAQmxBaseStartTask(self.doTaskHandle))
    def stop(self):
        if self.doTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(self.doTaskHandle)   



class niditask:
    def __init__(self):
        self.diTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(self.diTaskHandle)))
        self.numch = 0
        self.ch = {}
        self.datain = []
        
      
        
    def create_channel(self, channel):
        
        # The channel is a list but NI requires the channels to be Dev1/ai0,Dev1/ai1,etc
	chan = ''
        for ch in channel:
            chan = chan + ch + ','
        chan = ctypes.create_string_buffer(chan)
        print chan.value       

        CHK(nidaq.DAQmxBaseCreateDIChan(self.diTaskHandle,
                                        chan,
                                        "",
                                        c.DAQmx_Val_GroupByChannel))
        
    def get(self, channel, points):
        
        self.stop()
        #bufferSize=uInt32(points*len(channel))

        samples = uInt32()
        #bytes_per_sample = uInt32()
        #self.data = numpy.zeros((points*len(channel),),dtype=numpy.uint8)

        CHK(nidaq.DAQmxBaseReadDigitalScalarU32(self.diTaskHandle,
                                          float64(10.0), #timeout
                                          "", #unused
                                          ctypes.byref(samples)))
        """CHK(nidaq.DAQmxBaseReadDigitalLines(self.diTaskHandle,
                                        uInt32(points), #c.DAQmx_Val_Auto,  # samples per channel
                                        float64(10.0),     # timeout
                                        c.DAQmx_Val_GroupByChannel,    # fill mode
                                        self.data.ctypes.data,    # read array
                                        uInt32(bufferSize.value), # size of read array
                                        ctypes.byref(samps_read),    # actual num of samples read
                                        ctypes.byref(bytes_per_sample),     # actual number of bytes per sample
                                        None))
        """
        self.start()
        #print 'Samples read: ', samps_read
        #print 'Bytes per Sample: ', bytes_per_sample
        return samples

    def start(self):
        CHK(nidaq.DAQmxBaseStartTask(self.diTaskHandle))
    def stop(self):
        if self.diTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(self.diTaskHandle)

class niaotask:
    def __init__(self):
        self.aoTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(self.aoTaskHandle)))
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

        # The channel is a list but NI requires the channels to be Dev1/ai0,Dev1/ai1,etc
	chan = ''
        for ch in channel:
            chan = chan + ch + ','
        chan = ctypes.create_string_buffer(chan)
        print chan.value

            
            
        CHK(nidaq.DAQmxBaseCreateAOVoltageChan(self.aoTaskHandle,
                                               chan,
                                               "",
                                               minimum,
                                               maximum,
                                               c.DAQmx_Val_Volts,None))
               
        self.pointsToWrite = samplesperchannel
        CHK(nidaq.DAQmxBaseCfgSampClkTiming(self.aoTaskHandle,
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

        print data[:]
        sampsPerChanWritten = int32()
        self.stop()
        CHK(nidaq.DAQmxBaseWriteAnalogF64(self.aoTaskHandle,
                                      uInt32(len(data)),  #number of samples per channel
                                      uInt32(0),  #autostart task always false for nidaqmxbase
                                      float64(10.0), #timeout
                                      c.DAQmx_Val_GroupByChannel,
                                      data.ctypes.data,
                                      None,
                                      ctypes.byref(sampsPerChanWritten)))
        print 'Samples Written per channel: ', sampsPerChanWritten.value
	self.start()

    def start(self):
        CHK(nidaq.DAQmxBaseStartTask(self.aoTaskHandle))
    def stop(self):
        if self.aoTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(self.aoTaskHandle)
            



class niaitask:
    def __init__(self):
        self.aiTaskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(self.aiTaskHandle)))

        
    def create_channel(self, 
                       channel, 
                       rsediff, 
                       contfin, 
                       minimum, 
                       maximum, 
                       samplerate, 
                       samplesperchannel, 
                       clocksource):


        # The channel is a list but NI requires the channels to be Dev1/ai0,Dev1/ai1,etc
	chan = ''
        for ch in channel:
            chan = chan + ch + ','
        chan = ctypes.create_string_buffer(chan)
        print chan.value

        CHK(nidaq.DAQmxBaseCreateAIVoltageChan(self.aiTaskHandle,chan,"",rsediff,minimum,maximum,
            c.DAQmx_Val_Volts,None))

        self.pointsToRead = samplesperchannel
        CHK(nidaq.DAQmxBaseCfgSampClkTiming(self.aiTaskHandle,
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
        CHK(nidaq.DAQmxBaseStartTask(self.aiTaskHandle))
    def stop(self):
        if self.aiTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(self.aiTaskHandle)
            #nidaq.DAQmxClearTask(self.aiTaskHandle)       
        
    def get_data(self, channel, points):        
        # with multiple channels in the task the buffer needs to
        # be increased (bufferSize = pointsToRead * numchannelsInTask)
        self.bufferSize = uInt32(int(points*len(channel)))

        

        #this data array as well needs to be scaled by the number of channels in task
        self.data = numpy.zeros((points*len(channel),),dtype=numpy.float64)
        self.pointsRead = uInt32()
        #istaskdone = uInt32() 
        
        self.start()
        #CHK(nidaq.DAQmxBaseIsTaskDone(self.aiTaskHandle,ctypes.byref(istaskdone)))
	#print istaskdone
        CHK(nidaq.DAQmxBaseReadAnalogF64(self.aiTaskHandle,
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





##############################
def CHK(err):
    #a simple error checking routine
    if err < 0:
        buf_size = 1000
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxBaseGetExtendedErrorInfo(ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error: %s'%(repr(buf.value)))
        
class pynidaqbase(daq.daq):
    """
    Tested with National Instruments USB-6218 32-Input, 16-bit DAQ
    """
    
    def __init__(self, handle='Dev1'):
        """
        DAQ Device ID in the form Dev1, Dev2, etc.

        If you are unsure run something like LabView Signal Express
        and take a look what is there.
        """
        daq.daq.__init__(self)
        class_name = self.__class__.__name__
        #print "class", class_name, "created"
        self.__fillhwinfo(handle=handle)

        

        self.bus = getproductbus(handle)
        self.dll = 'nidaqmxbase'
        self.model = getdevicenumber(handle)
        self.handle = handle

        self.dotask = nidotask()
        #self.aitask = niaitask()
        self.aotask = niaotask()
        self.cotask = nicotask()
        self.citask = nicitask()
        self.ditask = niditask()
        
        #self.dosactive = []
        
    def __fillhwinfo(self,
                handle='Dev1'):
        deviceunplugged = 0

        """self.simulated = numpy.zeros(1,dtype=numpy.uint32)
        CHK(nidaq.DAQmxBaseGetDevIsSimulated(handle, self.simulated.ctypes.data))
        if(self.simulated):
            #print 'Simulated daq detected.\n'
            #logger.info('Simulated daq detected')
            pass
            
        else:
            #print 'Hardware daq detected.\n'
            #logger.info('Hardware daq detected.')
            pass
        """

        self.serialnumber = numpy.zeros(1,dtype=numpy.uint32)
        nidaq.DAQmxBaseGetDevSerialNum(handle, self.serialnumber.ctypes.data)
        self.serial_number = hex(self.serialnumber)

        #if (self.serialnumber == 0):
        #    print 'Device Not Connected.\n'
        #    deviceunplugged = 1
                    
        
        self.category = getproductcategory(handle=handle)
        #print 'Product Category:', ni_cat # returns 14643 or M Series DAQ for the USB6218
        #print ''

        #documentation missing for this
        #producttype = numpy.zeros(10,dtype=numpy.uint32)
        #CHK(nidaq.DAQmxBaseGetDevProductType('Dev2', producttype.ctypes.data, uInt32(10)))
        #print producttype


        #self.cserialnumber = numpy.zeros(1,dtype=numpy.uint32)
        #don't run this through CHK just fail and move on
        #if(nidaq.DAQmxBaseGetCarrierSerialNum(handle, self.cserialnumber.ctypes.data) == 0):
            #pass
            #print 'Carrier Serial Number:', hex(cserialnumber)         
            #print ""   

            #not sure what this is just returns nothing
            #print 'Chassis Modules:'
            #modules = numpy.zeros(1000,dtype=numpy.str_)
            #CHK(nidaq.DAQmxBaseGetDevChassisModuleDevNames(daq, modules.ctypes.data, uInt32(1000)))
            #modules = ''.join(list(modules))
            #print modules + '\n'        
     
        #if (deviceunplugged):
        #    return
        
        #self.atrigger = numpy.zeros(1,dtype=numpy.uint32)
        #nidaq.DAQmxBaseGetDevAnlgTrigSupported(handle, self.atrigger.ctypes.data)
        #if(self.atrigger):
        #    pass
            #print 'Analog trigger supported.\n'


            
        #self.dtrigger = numpy.zeros(1,dtype=numpy.uint32)
        #nidaq.DAQmxBaseGetDevDigTrigSupported(handle, self.dtrigger.ctypes.data)
        #if(self.dtrigger):
        #    pass
            #print 'Digital trigger supported.\n' 


        
        #self.maxSchRate = numpy.zeros(1,dtype=numpy.float64)
        #if(nidaq.DAQmxBaseGetDevAIMaxSingleChanRate(handle, self.maxSchRate.ctypes.data)):
        #    pass
        #else:
        #    pass
            #print 'Max Single Channel Sample Rate:', maxSchRate
            #print ""

        
        #self.maxMchRate = numpy.zeros(1,dtype=numpy.float64)
        #if(nidaq.DAQmxBaseGetDevAIMaxMultiChanRate(handle, self.maxMchRate.ctypes.data)):
        #    pass
        #else:
        #    pass
            #print 'Max Multi Channel Sample Rate:', maxMchRate
            #print ""

        
        #self.minSamplingRate = numpy.zeros(1,dtype=numpy.float64)
        #if(nidaq.DAQmxBaseGetDevAIMinRate(handle, self.minSamplingRate.ctypes.data)):
        #    pass
        #else:
        #    pass
            #print 'Minimum Sample Rate:', minSamplingRate
            #print ""


        #self.simSampling = numpy.zeros(1,dtype=numpy.uint32)
        #if(nidaq.DAQmxBaseGetDevAISimultaneousSamplingSupported(handle, self.simSampling.ctypes.data)):
        #    pass
        #else:
        #    if(self.simSampling):
        #        pass
                #print 'Simultaneous sampling supported\n'

        #print 'Analog In Channels:'
        self.numai, self.aichannels = getnumai(handle)

        #print 'Analog Out Channels:'
	self.numao, self.aochannels = getnumao(handle)

        #print 'Digital In Lines:'
        #print 'Digital In Ports:'
        self.numdi, self.dips, self.dils = getnumdi(handle)

        #print 'Digital Out Lines:'
        #print 'Digital Out Ports:'
        self.numdo, self.dops, self.dols = getnumdo(handle)

        #print 'Counter Input Channels:'
        self.numci, self.cichannels = getnumci(handle)

        #print 'Counter Output Channels:'
	self.numco, self.cochannels = getnumco(handle)
   




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
            #    nidaq.DAQmxBaseStopTask(self.taskHandle)
            #return data
        def output_waveform(self, waveform):
            self.aotask.write_data(self.channel, waveform)
        def start(self):
            self.aotask.start()
        def stop(self):
            self.aotask.stop()


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
                     channel='Dev1/ctr0',
                     frequency=100,
                     dutycycle=0.5,
                     delay=0,
                     idlestate=c.DAQmx_Val_Low):
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
                     channel='Dev1/ctr0',
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
            
            self.citask = nicitask()
            self.cichan = channel
            print self.cichan
            self.cichan = ctypes.create_string_buffer(self.cichan)
            #self.parentdaq = daqclass
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
                nidaq.DAQmxBaseStopTask(self.dotask.doTaskHandle)
                nidaq.DAQmxBaseClearTask(self.dotask.doTaskHandle)
            

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
                nidaq.DAQmxBaseStopTask(self.ditask.diTaskHandle)
                nidaq.DAQmxBaseClearTask(self.ditask.diTaskHandle)
            

        def get(self,num_points=1):
                   
            
            return self.ditask.get(self.dichan,
                                   points=num_points)
   
                
                  



def daqfind():
    """ Searches for NI Daqs Dev(0-127), cDAQN(0-127), Mod(0-7) 

    Returns a list of valid handles for devices currently
    found on system.
    """

    nd = 0 # number of daqs
    print "Enter daqfind ", time.asctime( time.localtime(time.time()) )
    # load the ni device category dictionary file(translate device
    # category number to human readable words)

    #ni_cat = pkgutil.get_data('pydaqtools', 'data/ni_cat.dat')
    #cat = pickle.loads(ni_cat)
 

    category = numpy.zeros(1,dtype=numpy.uint32)
    #simulated = numpy.zeros(1,dtype=numpy.uint32)
    handles = []

    for i in range(0,16):
        #print i, time.asctime( time.localtime(time.time()) )
        # first look for ni instruments with Dev1 or Dev2 etc. Brute force but
        # I don't see any documentation to help.         
        handle = 'Dev' + str(i)

        serialnumber = numpy.zeros(1,dtype=numpy.uint32)
        nidaq.DAQmxBaseGetDevSerialNum(handle, serialnumber.ctypes.data)
        # this seems to be ni's recommended method. If serial number is
        # zero then device was installed on the system at one time but
        # it is not currently. I'm just going to ignore it.
        if (serialnumber == 0):
            pass
        # finally, a valid, installed ni hardware daq 
        elif (serialnumber > 0):
            # add the newly found valid handle to the list
            handles.append(handle)
            nd = nd + 1 # inc the number of valid daqs counter

        # next look for compact chassis'
        handle = 'cDAQ' + str(i)
        serialnumber = numpy.zeros(1,dtype=numpy.uint32)
        nidaq.DAQmxBaseGetDevSerialNum(handle, serialnumber.ctypes.data)
        # this seems to be ni's recommended method. If serial number is
        # zero then device was installed on the system at one time byt
        # it is not currently. I'm just going to ignore it.
        if (serialnumber == 0):
            pass
        # finally, a valid, installed ni hardware daq 
        elif (serialnumber > 0):
            # add the newly found valid handle to the list it's just a
            # chassis but add it anyways
            handles.append(handle)
            nd = nd + 1

            # found the chassis so search for modules installed              
            for j in range(0,7):
                handle = 'cDAQ' + str(i) + 'Mod' + str(j)

                # we've found a valid hardware module
                handles.append(handle)
                nd = nd + 1
    print "Exit daqfind ",time.asctime( time.localtime(time.time()) )
    return handles



def getproductcategory(handle='Dev1'):
    """file = open('ni_cat.dat', 'rb')
    ni_cat = pickle.load(file)
    file.close()

    category = numpy.zeros(1,dtype=numpy.uint32)
    nidaq.DAQmxBaseGetDevProductCategory(handle, category.ctypes.data)
    return ni_cat[str(category[0])]
    """
    return 0


def getproductbus(handle='Dev1'):
    #ni_bus = resource_filename(__name__, 'data/ni_bus.dat')
    #ni_bus = pkgutil.get_data('pydaqtools', 'data/ni_bus.dat')
    #ni_bus = pickle.loads(ni_bus)


    #bus = numpy.zeros(1,dtype=numpy.uint32)
    #nidaq.DAQmxBaseGetDevBusType(handle, bus.ctypes.data)
    return 0#ni_bus[str(bus[0])]

def getdevicenumber(handle='Dev1'):
    #ni_dev = resource_filename(__name__, 'data/ni_dev.dat')
    #ni_dev = pkgutil.get_data('pydaqtools', 'data/ni_dev.dat')
    #ni_dev = pickle.loads(ni_dev)


    #device = numpy.zeros(1,dtype=numpy.uint32)
    #nidaq.DAQmxBaseGetDevProductNum(handle, device.ctypes.data)
    return 0#ni_dev[str(device[0])]

def getnumai(handle='Dev1'):
    aiTaskHandle = TaskHandle(0)
    CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(aiTaskHandle)))

    rsediff = c.DAQmx_Val_RSE
    contfin = c.DAQmx_Val_FiniteSamps
    minimum = float64(-5)
    maximum = float64(5)
    i = 0
    channels = []
    while i < 128:
        ch = ctypes.create_string_buffer(handle + '/ai' + str(i))
        
        #print 'CH:', ch[:]
        result = nidaq.DAQmxBaseCreateAIVoltageChan(aiTaskHandle,ch,"",uInt32(-1),minimum,maximum,c.DAQmx_Val_Volts,None)
        #print 'Results:', result
        # result of zero is a success so anything but means there are no more analog inputs
	if result != 0:
            #if aiTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(aiTaskHandle)
            nidaq.DAQmxBaseClearTask(aiTaskHandle)  	
            return i,channels
        else:
	    channels.append(handle + '/ai' + str(i))
            i = i + 1

def getnumao(handle='Dev1'):
    aoTaskHandle = TaskHandle(0)
    CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(aoTaskHandle)))

    rsediff = c.DAQmx_Val_RSE
    contfin = c.DAQmx_Val_FiniteSamps
    minimum = float64(-5)
    maximum = float64(5)
    i = 0
    channels = []
    while i < 128:
        ch = ctypes.create_string_buffer(handle + '/ao' + str(i))
        #print 'CH:', ch[:]
        result = nidaq.DAQmxBaseCreateAOVoltageChan(aoTaskHandle,
                                                    ch,
                                                    "",
                                                    minimum,maximum,c.DAQmx_Val_Volts,None)
        #print 'Results:', result
        # result of zero is a success so anything but means there are no more analog inputs
	if result != 0:
            #if aoTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(aoTaskHandle)
            nidaq.DAQmxBaseClearTask(aoTaskHandle)  	
            return i,channels
        else:
	    channels.append(handle + '/ao' + str(i))
            i = i + 1

def getnumdi(handle='Dev1'):
    diTaskHandle = TaskHandle(0)
    CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(diTaskHandle)))

    port = 0
    line = 0
    channels = []
    ports = []
    while port < 128:
        while line < 8:
            ch = ctypes.create_string_buffer(handle + '/port' + str(port) + '/line' + str(line))
            #print 'CH:', ch[:]
            result = nidaq.DAQmxBaseCreateDIChan(diTaskHandle,ch,"",c.DAQmx_Val_ChanForAllLines)

            #print 'Results:', result
            # result of zero is a success so anything but means there are no more analog inputs
	    if result != 0:
                #if aoTaskHandle.value != 0:
                nidaq.DAQmxBaseStopTask(diTaskHandle)
                nidaq.DAQmxBaseClearTask(diTaskHandle)  
                break	
            #return i,channels
            else:
	        channels.append(handle + '/port' + str(port) + '/line' + str(line))
                line = line + 1

        if line == 0:
            return len(channels), ports, channels
        else:
            ports.append(handle + '/port' + str(port))
            port = port + 1 
            line = 0

def getnumdo(handle='Dev1'):
    doTaskHandle = TaskHandle(0)
    CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(doTaskHandle)))

    port = 0
    line = 0
    channels = []
    ports = []
    while port < 128:
        while line < 8:
            ch = ctypes.create_string_buffer(handle + '/port' + str(port) + '/line' + str(line))
            #print 'CH:', ch[:]
            result = nidaq.DAQmxBaseCreateDOChan(doTaskHandle,ch,"",c.DAQmx_Val_ChanForAllLines)

            #print 'Results:', result
            # result of zero is a success so anything but means there are no more analog inputs
	    if result != 0:
                #if aoTaskHandle.value != 0:
                nidaq.DAQmxBaseStopTask(doTaskHandle)
                nidaq.DAQmxBaseClearTask(doTaskHandle)  
                break	
            #return i,channels
            else:
	        channels.append(handle + '/port' + str(port) + '/line' + str(line))
                line = line + 1

        if line == 0:
            return len(channels), ports, channels
        else:
            ports.append(handle + '/port' + str(port))
            port = port + 1 
            line = 0

def getnumco(handle='Dev1'):
    coTaskHandle = TaskHandle(0)
    CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(coTaskHandle)))

    i = 0
    channels = []
    while i < 128:
        ch = ctypes.create_string_buffer(handle + '/ctr' + str(i))
        #print 'CH:', ch[:]
        result = nidaq.DAQmxBaseCreateCOPulseChanFreq(coTaskHandle,ch,"",
                                              c.DAQmx_Val_Hz,
                                              int32(c.DAQmx_Val_Low), #idlestate
                                              float64(0), # delay
                                              float64(100), # frequency
                                              float64(0.5)) # duty cycle

        #print 'Results:', result
        # result of zero is a success so anything but means there are no more analog inputs
	if result != 0:
            #if aoTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(coTaskHandle)
            nidaq.DAQmxBaseClearTask(coTaskHandle)  	
            return i,channels
        else:
	    channels.append(handle + '/ctr' + str(i))
            i = i + 1


def getnumci(handle='Dev1'):
    ciTaskHandle = TaskHandle(0)
    CHK(nidaq.DAQmxBaseCreateTask("",ctypes.byref(ciTaskHandle)))

    i = 0
    channels = []
    while i < 128:
        ch = ctypes.create_string_buffer(handle + '/ctr' + str(i))
        #print 'CH:', ch[:]
        result = nidaq.DAQmxBaseCreateCIPeriodChan(ciTaskHandle,
                                        ch,
                                        '', # name to assign to virtual channel
                                        float64(100), #min val
                                        float64(200), #max val
                                        c.DAQmx_Val_Seconds,
                                        c.DAQmx_Val_Rising,
                                        c.DAQmx_Val_LowFreq1Ctr,
                                        float64(0),   #measure time
                                        uInt32(1), 
                                        '')

        #print 'Results:', result
        # result of zero is a success so anything but means there are no more analog inputs
	if result != 0:
            #if aoTaskHandle.value != 0:
            nidaq.DAQmxBaseStopTask(ciTaskHandle)
            nidaq.DAQmxBaseClearTask(ciTaskHandle)  	
            return i,channels
        else:
	    channels.append(handle + '/ctr' + str(i))
            i = i + 1   

    


    


