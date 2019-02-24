# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 19:23:30 2019

@author: LiNaK
"""

# Standard module
import numbers 

# 3rd party's module
import numpy as np
import pandas as pd

# Original module  

class MagLogUtil():
    
    def _chk_type_and_apply_func(self, conv_func, data, N):
        dtype =type(data)
        if dtype==list:
            # Change np.ndarray format to calc. Return type is list
            return list(conv_func(np.array(data), N))
        
        elif dtype == np.ndarray or dtype == pd.core.series.Series or\
        isinstance(data, numbers.Number):
            return conv_func(data,N)
        
        else:
            raise TypeError
    
    def log2mag(self, data, N=10):
        def calc(data, N):
            return 10**(data/N)
        return self._chk_type_and_apply_func(calc, data, N)

    def mag2log(self, data, N=10):
        def calc(data, N):
            return N*np.log10(data)
        return self._chk_type_and_apply_func(calc, data, N)
    
    def magdeg2comp(self, mag, deg):
        return mag*np.exp(np.deg2rad(deg)*1j)
        