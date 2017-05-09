# setup.py
try:
    from setuptools import setup
except ImportError:
    #print "standard distutils"
    from distutils.core import setup
else:
    pass
import sys
import os


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()



setup(name='pydaqtools',
      version='0.2.0',
      description='Python Data Acquisition Tools',
      long_description=read('README'),
      author='Joe Grado',
      author_email='gradoj@gmail.com',
      license = 'BSD',
      keywords = 'data acquisition nidaqmx nidaq national instruments daq',
      url='http://www.pydaqtools.org/',
      classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',

      ],

      #packages=find_packages(exclude=['tests', 'examples']),
      packages=['pydaqtools'],
      package_dir={'pydaqtools': 'pydaqtools'},
      package_data={'pydaqtools':['data/*.dat']},
      include_package_data = True,
      download_url = 'https://sourceforge.net/projects/pydaqtools/files/0.2.0/',
      install_requires=[
         'numpy',
         'scipy',
      ],

      )



