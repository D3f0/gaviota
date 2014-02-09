#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import functools
utfopen = functools.partial(codecs.open, encoding = 'utf-8')
import glob
from os import path

def _get_data(filename):
    pass



def get_nombres(sexo = None):
    '''
    Retorna una lista de nombres dado un sexo
    'masculino' -> [xxx, xxx, xxx,]
    'masculino' -> [xxx, xxx, xxx,]
     None ->{ s: [x, y, z], s2: [x, y, z]}

    '''
    pwd = path.abspath(__file__)
    
    if sexo:
        return _get_data(filename)
    else
        return 
    
