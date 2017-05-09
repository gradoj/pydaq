
class daq:
    """ Generic daq class

    This can be 
    """
    
    def __init__(self):
        """ abstract skeleton class for a daq

        """
        class_name = self.__class__.__name__
        #print "class", class_name, "created"

        self.bus = ''
        self.dll = ''
        self.id = ''
        self.numai = ''
        self.ainame = ''
        self.numao = ''
        self.ainame = ''
        self.numdi = ''
        self.numdo = ''
        self.numco = ''
        self.numci = ''
        self.model = ''
        self.handle = ''
        
        self.simulated = ''
        self.serial_number = ''
        self.category = ''
        self.atrigger = ''
        self.dtrigger = ''
        self.aichannels = ''
        self.maxSchRate = ''
        self.maxMchRate = ''
        self.minSamplingRate = ''
        self.simSampling = ''
        self.aochannels = ''
        self.dils = ''
        self.dips = ''
        self.dols = ''
        self.dops = ''
        self.cichannels = ''
        self.cochannels = ''

    def __del__(self):
        class_name = self.__class__.__name__
        #logger.debug('class', class_name, 'destroyed')
        
    def daqhwinfo(self):
        #logger.warn('Method not supported(or implemented) for this device')
        pass
    class analog_output:
        def __init__(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def output_dc(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def output_sin(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def output_waveform(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
    class analog_input:
        def __init__(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def acquire(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
    class counter_input:
        def __init__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "created"            
            #logger.warn('Method not supported(or implemented) for this device')
    

        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"
            #logger.warn('Method not supported(or implemented) for this device')
        def start(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def stop(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def get_frequency(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass


    class counter_output:
        def __init__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "created"
            #logger.warn('Method not supported(or implemented) for this device')


        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"
            #logger.warn('Method not supported(or implemented) for this device')
        def start(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def stop(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def update_pwm(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
    class digital_output:
        def __init__(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"
            #logger.warn('Method not supported(or implemented) for this device')

        def output(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
    class digital_input:
        def __init__(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
        def __del__(self):
            class_name = self.__class__.__name__
            #print "class", class_name, "destroyed"
            #logger.warn('Method not supported(or implemented) for this device')

        def get(self):
            #logger.warn('Method not supported(or implemented) for this device')
            pass
