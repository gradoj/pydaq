import sys

daqclasses = []

def create_classes():
    global daqclasses
    nidaqs = []
    nibasedaqs = []
    sounddaqs = []
    ljdaqs = []

    # blank out the array in case this is called more than once
    daqclasses = [] 
    
    #get list of handles for each daq type
    try:
        import pynidaq

        nihandles = pynidaq.daqfind()
        for i in range(0, len(nihandles)):
            nidaqs.append(pynidaq.pynidaq(nihandles[i]))
    except:
        pass
        #print "Unexpected error in pynidaq:", sys.exc_info()
        #raise

    #get list of handles for each daq type
    try:
        import pynidaqbase

        nibasehandles = pynidaqbase.daqfind()
        for i in range(0, len(nibasehandles)):
            nibasedaqs.append(pynidaqbase.pynidaqbase(nibasehandles[i]))
    except:
        pass
        #print "Unexpected error in pynidaqbase:", sys.exc_info()
        #raise

    try:
        import pysounddaq
        soundhandles = pysounddaq.daqfind()
        for i in range(0, len(soundhandles)):
            sounddaqs.append(pysounddaq.pysounddaq(soundhandles[i]))
    except:
        module = sys.exc_info()
        module = str(module[1])
        if module.find('pyaudio') >= 0:
            #print 'pyaudionot found'
            pass
        else:
            pass
            #print "Unexpected error:", sys.exc_info()[0:2]
        #raise
    try:
        import pylabjack
        
        ljhandles = pylabjack.daqfind()
        for i in range(0, len(ljhandles)):
            ljdaqs.append(pylabjack.pylabjack(ljhandles[i]))
    except:
        pass
        #print "Unexpected error:", sys.exc_info()[0:2]
        #raise
    
    
    daqclasses.extend(nidaqs)
    daqclasses.extend(nibasedaqs)
    daqclasses.extend(sounddaqs)
    daqclasses.extend(ljdaqs)

    for i in range(0, len(daqclasses)):
        daqclasses[i].id = i


def get_classes():
    global daqclasses
    return daqclasses
