#!/usr/bin/python

from pprint import pprint
#import logging
#import logging.config
#logging.config.fileConfig("logging.conf")
#logger = logging.getLogger("daqLog")

import sys
import daq
import find_daqs

# list of modules to be visible
#__all__ = []
  

def daqhwinfo(daqid=0):
    """ returns detailed hardware information collected
    from the daqid hardware.   
    """
    alldaqs = find_daqs.get_classes()

    
    print ('daqid:', alldaqs[daqid].id)
    print ('Bus:', alldaqs[daqid].bus)
    print ('Handle:', alldaqs[daqid].handle)
    if(alldaqs[daqid].simulated):
        print ('DAQ is simulated\n')   
    print ('Model:', alldaqs[daqid].model)
    if(alldaqs[daqid].category):
        print ('Category:', alldaqs[daqid].category)
    if(alldaqs[daqid].serial_number):
        print ('Serial Number:', alldaqs[daqid].serial_number)        
    print ('')    

    print ('Number of Pins:')
    print ('daqid aIn    aOut   dIn    dOut   cntIn  cntOut ')
    #alldaqs[daqid]['id'] = daqid
    print ('%-7s%-7s%-7s%-7s%-7s%-7s%-7s'% (alldaqs[daqid].id,
                                           alldaqs[daqid].numai,
                                           alldaqs[daqid].numao,
                                           alldaqs[daqid].numdi,
                                           alldaqs[daqid].numdo,
                                           alldaqs[daqid].numci,
                                           alldaqs[daqid].numco))
    print ('')


    if(alldaqs[daqid].atrigger):
        print ('Analog Trigger Supported\n')
    if(alldaqs[daqid].dtrigger):
        print ('Digital Trigger Supported\n')
    if(alldaqs[daqid].aichannels):
        print ('Analog Input Channels:')
        pprint (alldaqs[daqid].aichannels)
        print ('')
        if(alldaqs[daqid].maxSchRate):
            print ('Maximum Single Channel Sample Rate:', alldaqs[daqid].maxSchRate)
            print ('')
        if(alldaqs[daqid].maxMchRate):
            print ('Maximum Muliple Channel Sample Rate:', alldaqs[daqid].maxMchRate)
            print ('')
        if(alldaqs[daqid].minSamplingRate):
            print ('Minimum Sample Rate:', alldaqs[daqid].minSamplingRate)
            print ('')
        if(alldaqs[daqid].simSampling):
            print ('Simultaneous Sampling Supported\n')
    if(alldaqs[daqid].aochannels):
        print ('Analog Output Channels:')
        pprint (alldaqs[daqid].aochannels)
        print ('')
    if(alldaqs[daqid].dils):
        print ('Digital Input Lines Channels:')
        print (alldaqs[daqid].dils)
        print ('')
    if(alldaqs[daqid].dips):
        print ('Digital Input Ports:')
        print (alldaqs[daqid].dips)
        print ('')
    if(alldaqs[daqid].dols):
        print ('Digital Output Lines:')
        print (alldaqs[daqid].dols)
        print ('')
    if(alldaqs[daqid].dops):
        print ('Digital Output Ports:')
        print (alldaqs[daqid].dops)
        print ('')
    if(alldaqs[daqid].cichannels):
        print ('Counter Input Channels:')
        print (alldaqs[daqid].cichannels)
        print ('')
    if(alldaqs[daqid].cochannels):
        print ('Counter Output Channels:')
        print (alldaqs[daqid].cochannels)
        print ('')

def daqfind():
    find_daqs.create_classes()
    alldaqs = find_daqs.get_classes()
    nd = len(alldaqs)
    print ('DAQid     Bus                      Handle       Model           ')
    for i in range(0,nd):
        print ('%-10s%-25s%-13s%-25s' %(alldaqs[i].id, alldaqs[i].bus, alldaqs[i].handle, alldaqs[i].model))
    print ('')

def connect_terms(daqid, source_channel,
                  dest_channel):

    alldaqs = find_daqs.get_classes()
    print (source_channel.channel)
    print (dest_channel.channel)
    alldaqs[daqid].connect_terms(source_channel.channel,
                                        dest_channel.channel)
    
def analog_output(daqid=0,
                  channel=[0],
                  contfin='fin',
                  samplerate=44100,
                  clock='OnboardClock'):

    try:
        alldaqs = find_daqs.get_classes()
        channels = []        
        if(isinstance(channel,int)):
            channels.append(alldaqs[daqid].aochannels[channel])
        else:
            for ch in channel:
                channels.append(alldaqs[daqid].aochannels[ch])

        return alldaqs[daqid].analog_output(daqclass=alldaqs[daqid],
                                            channel=channels,
                                            contfin=contfin,
                                            samplerate=samplerate,
                                            clock=clock)
    
    except IndexError:
        print ('DAQ not found. Invalid daqid.')
    except:
        raise
    
def analog_input(daqid=0,
                 channel=[0],
                 rsediff='rse',
                 contfin='fin',
                 samplerate=10000):

    try:
        alldaqs = find_daqs.get_classes()
        channels = []
        
        if(isinstance(channel,int)):
            channels.append(alldaqs[daqid].aichannels[channel])
        else:
            for ch in channel:
                channels.append(alldaqs[daqid].aichannels[ch])

        return alldaqs[daqid].analog_input(daqclass=alldaqs[daqid],
                                             channel=channels,
                                             rsediff=rsediff,
                                             contfin=contfin,
                                             samplerate=samplerate)
    except IndexError:
        print ('DAQ not found. Invalid daqid.')
    except:
        raise
    
def counter_output(daqid=0,
                   channel=0,
                   frequency=100,
                   dutycycle=0.5):
    try:
        alldaqs = find_daqs.get_classes() 
        return alldaqs[daqid].counter_output(daqclass=alldaqs[daqid],
                                             channel=alldaqs[daqid].cochannels[channel],
                                             frequency=frequency,
                                             dutycycle=dutycycle)
    except IndexError:
        print ('DAQ not found. Invalid daqid.')
    except:
        raise
    
def counter_input(daqid=0,
                  channel=0,
                  min_val=1.0,
                  max_val=1000.0,
                  edge='rising',
                  meas_method='low_freq_1_ctr',
                  meas_time=1.0,
                  divisor=1):
    try:
        alldaqs = find_daqs.get_classes()
        return alldaqs[daqid].counter_input (daqclass=alldaqs[daqid],
                                             channel=alldaqs[daqid].cichannels[channel])
    except IndexError:
        print ('DAQ not found. Invalid daqid.')
    except:
        raise
    
def digital_output(daqid=0,
                   channel=[0]):
    try:
        alldaqs = find_daqs.get_classes() 
        
        channels = []
        if(isinstance(channel,int)):
            channels.append(alldaqs[daqid].dols[channel])
        else:
            for ch in channel:
                channels.append(alldaqs[daqid].dols[ch])
                
        return alldaqs[daqid].digital_output(daqclass=alldaqs[daqid],
                                             channel=channels)
    except IndexError:
        print ('DAQ not found. Invalid daqid.')
    except:
        raise
    
def digital_input(daqid=0,
                  channel=0):
    try:
        alldaqs = find_daqs.get_classes()
        channels = []
        if(isinstance(channel,int)):
            channels.append(alldaqs[daqid].dils[channel])
        else:
            for ch in channel:
                channels.append(alldaqs[daqid].dils[ch])        
        
        return alldaqs[daqid].digital_input(daqclass=alldaqs[daqid],
                                            channel=channels)
    except IndexError:
        print ('DAQ not found. Invalid daqid.')
    except:
        raise

def sound(waveform,samplerate=44100):
    try:
        import pysounddaq
        pysounddaq.sound(waveform,samplerate)
    except:
        print ("Unexpected error:", sys.exc_info()[0:2])
        #raise
        
                                                                
if __name__ == "__main__":
    #print sys.argv[1:]
    pass

    
