# -*- encoding=utf8 -*-


import numpy
from GameHelper.core.helper.images import hex_to_rgb
from GameHelper.core.util.ciede2000 import ciede2000


array = [['#461e00', '#3d3006', '#b2945e', '#ad966d'], ['#855d3a', '#000a0d', '#94655d', '#815c4a']]

array = list(map(tuple, numpy.c_[numpy.array(array[0]), numpy.array(array[1])]))

for clr0, clr1 in array:
    print(ciede2000(lab1=hex_to_rgb(clr0), lab2=hex_to_rgb(clr1)))
