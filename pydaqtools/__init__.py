#!/usr/bin/python 

VERSION = '0.1.3'
from pydaqtools import *
import sys

if sys.platform == 'cli':
    pass
    #from  import *
else:
    import os
    # chose an implementation, depending on os
    if os.name == 'nt': #sys.platform == 'win32':
        pass
        #from asdfwin32 import *
    elif os.name == 'posix':
        pass
        #from asdfposix import *
    elif os.name == 'java':
        pass
        #from asdfjava import *
    else:
        raise Exception("Sorry: no implementation for your platform ('%s') available" % os.name)



