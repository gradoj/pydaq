import unittest  # import unittest for test framework
import doctest
import pydaqtools as pdt
import time
import sys
import numpy
import math

class daq_tests(unittest.TestCase):
    def setUp(self):
        #This gets called before every test is run
        pdt.daqfind()
        pass
    def tearDown(self):
        #This gets called after every test is run
        #logging.shutdown()
        pass

    def testbuiltin(self):
        """
        Print all available built-in modules for python
        """
        
        for name in sys.builtin_module_names:
            pass
            #print name

    def testconterms(self):
        """
        test connect terminals
        """
        ai = pdt.analog_input()
        ao = pdt.analog_output()

        pdt.connect_terms(0,ao,ai)

    def test_speakers_sine(self):
        """
        Outputs a 1kHz sine wave for 2 seconds on speakers
        """
        speakers = pdt.analog_output(daqid=2,
				     channel=(0,1))
        speakers.output_sin(freq=1000)
        time.sleep(2)
        speakers.stop()        
    def testdido_single_channel(self):
        """
        Connect digital line0 to line2
        Connect digital line1 to line3
        """
        do0 = pdt.digital_output(daqid=0, channel=0)
        do1 = pdt.digital_output(daqid=0, channel=1)
        di2 = pdt.digital_input(daqid=0, channel=2)
        di3 = pdt.digital_input(daqid=0, channel=3)
        
        do0.output(0)
        do1.output(0)
        self.assertEqual(0, di2.get(1))
        self.assertEqual(0, di3.get(1))
        
        do0.output(1)
        do1.output(0)
        self.assertEqual(1, di2.get(1))
        self.assertEqual(0, di3.get(1))
        
        do0.output(0)
        do1.output(1)
        self.assertEqual(0, di2.get(1))
        self.assertEqual(1, di3.get(1))

        do0.output(1)
        do1.output(1)
        self.assertEqual(1, di2.get(1))
        self.assertEqual(1, di3.get(1))        

    def testdido_multi_channel(self):
        """
        Connect digital line0 to line2
        Connect digital line1 to line3
        """
        do = pdt.digital_output(daqid=0, channel=[0,1])
        di = pdt.digital_input(daqid=0, channel=[2,3])
        
        x = do.output([0,0])
        self.assertEqual( [0,0],di.get(1).tolist() )
        
        x = do.output([0,1])
        self.assertEqual( [0,1],di.get(1).tolist() )
        
        x = do.output([1,0])
        self.assertEqual( [1,0],di.get(1).tolist() )        

        x = do.output([1,1])
        self.assertEqual( [1,1],di.get(1).tolist() )
        

    def testai_finite_samples(self):
        """
        testai
        """
        ai0 = pdt.analog_input(daqid=0,
                               channel=0,
                               contfin='fin',
                               rsediff='rse',
                               samplerate=1250000)
        a = ai0.acquire(10)
        print a
        ai1 = pdt.analog_input(daqid=0,
                               channel=[1],
                               contfin='fin',
                               rsediff='rse',
                               samplerate=1250000)
        a = ai1.acquire(10)
        print a

        ai0C = pdt.analog_input(daqid=0,
                                channel=[2,3],
                                contfin='fin',
                                rsediff='rse',
                                samplerate=1250000)                                

        a = ai0C.acquire(10)
        print a

        a = ai0.acquire(10)
        print a
    def testai_continuous_samples(self):
        """
        testai continuous sampling
        """
        ai0 = pdt.analog_input(daqid=0,
                               channel=0,
                               contfin='cont',
                               rsediff='rse',
                               samplerate=1000)
        ai0.start()
        for i in range(10):
            a = ai0.acquire(1000)
	    print 'Max:', a.max()
	    print 'Mean: ', a.mean()
	    print 'Min: ', a.min(), '\n'

        ai0.stop()
        
    def testao_outputdc_single_ch(self):
        """
        testao_outputdc_single_ch
        Connect analog-out pin 0 to analog-in pin 0
        Connect analog-out pin 1 to analog-in pin 1        
        """
        ao0 = pdt.analog_output(daqid=0,
                                channel=0)
        ao0.output_dc(0.5)
        ai0 = pdt.analog_input(daqid=0,
                               channel=0,
                               rsediff='rse',
                               samplerate=1250000)
        a = ai0.acquire(10)
        print a
        
        self.assertAlmostEqual(a[0], 0.5, places=2)


        ao1 = pdt.analog_output(daqid=0,
                                channel=1)
        ao1.output_dc(1.0)
        ai1 = pdt.analog_input(daqid=0,
                               channel=1,
                               rsediff='rse',
                               samplerate=50000)
        a = ai1.acquire(10)    
        self.assertAlmostEqual(a[0], 1.0, places=2)
        #raw_input('Press Enter')
        
    def testao_outputdc_multi_ch(self):
        """
        testao_outputdc_multi_ch
        Connect analog-out pin 0 to analog-in pin 0
        Connect analog-out pin 1 to analog-in pin 1
        """
        ao = pdt.analog_output(daqid=0,
                                channel=[0,1])
        ao.output_dc([0.5,1.0])
        ai = pdt.analog_input(daqid=0,
                               channel=[0,1],
                               rsediff='rse',
                               samplerate=50000)
        a = ai.acquire(5)
        print a
        self.assertAlmostEqual(a[0], 0.5, places=2)
        self.assertAlmostEqual(a[5], 1.0, places=2)
        
    def testao_output_waveform(self):
        """
        test counter inputs
        """
	y = numpy.zeros(1000,dtype=numpy.float64)
        # create 1000 evenly spaced values from time=0 to x
        t = numpy.linspace(0,0.01,1000)
        f = 1000
        A = 5

        #y = A*waveforms.square(2*math.pi*f*t,duty=0.5)
        #y = A*waveforms.sawtooth(2*math.pi*f*t,width=0.5)

        
        for i in numpy.arange(1000):
            y[i] = 9.95*math.sin(i*2.0*math.pi*1000.0/16000.0)	
        
        ao = pdt.analog_output(channel=[0],samplerate=10000,contfin='cont')#clock='ai/SampleClock')
	ai = pdt.analog_input(channel=[0],samplerate=1E6)
	ao.output_waveform(y)
	ai.AcquireAndGraph(100000)
	ao.output_waveform(y)
        
    def testci(self):
        """
        test counter inputs
        """
        co = pdt.counter_output(daqid=0,
                                channel=0)
        co.start()
        ci = pdt.counter_input(daqid=0,
                               channel=1)
        
        print ci.get_frequency(num_samples=10)
        co.update_pwm(frequency=120,
                      dutycycle=0.5)
        print ci.get_frequency(num_samples=10)

    def testco(self):
        """
        testco
        Connect default counter 0 output to default counter 1 input
        """
        co0 = pdt.counter_output(daqid=0,
                                 channel=0,
                                 frequency=100,
                                 dutycycle=0.5)
        co0.start()
        # would be really cool if I could internally
        # route an ai channel and measure the output freq
        #raw_input('Press Enter')
        co0.update_pwm(frequency=200, dutycycle=0.25)
        #raw_input('Press Enter')
        co1 = pdt.counter_output(daqid=0,
                                 channel=1,
                                 frequency=1000,
                                 dutycycle=0.8)
        co1.start()
        #raw_input('Press Enter')
        co1.update_pwm(frequency=2000, dutycycle=0.5)
        #raw_input('Press Enter')
        co0.stop()
        co1.stop()        
def run_tests():
    # Finer level of control to run tests
    unittest.TextTestRunner(verbosity=2).run(suite())

def doctsuite():
    return doctest.DocTestSuite(pydaqtools)

# Simpler way
def makedaqTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(daq_tests("testai"))
    return suite

# Make this test module runnable from the command prompt
if __name__ == "__main__":
    unittest.main(defaultTest='doctsuite')
