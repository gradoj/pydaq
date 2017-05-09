import pydaqtools as pdt
pdt.daqfind()

do = pdt.digital_output(daqid=0,channel=[0,1])
di = pdt.digital_input(daqid=0,channel=[2,3])

do.output([0,0])
print di.get(1)

do.output([0,1])
print di.get(10)

do.output([1,0])
print di.get(10)

do.output([1,1])
print di.get(1)

do.output([0,0])
print di.get(1)