
C:\Python26\python.exe setup.py bdist_egg
C:\Python26\python.exe setup.py bdist_wininst --plat-name=win-amd64
C:\Python26\python.exe setup.py bdist_wininst --plat-name=win32
C:\Python26\python.exe setup.py sdist 
python2.6 setup.py bdist --formats=gztar
python2.6 setup.py bdist_rpm

