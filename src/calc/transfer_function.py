# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 22:23:41 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module
from scipy import signal

# Original module  
from context import src # path setting

# interface
from src.interface.intfc_com import TF_Maker 

class LCRLPF(TF_Maker):
    def __init__(self):
        self._L = None #[uH]
        self._C = None #[pF]
        self._R = None #[Ohm]
    
    def set_parameter(self, L = None, C = None, R = None):
        for key, par in {'L':L, 'C':C, 'R':R}.items():
            self._set_each_par(key, par)
            
    def _set_each_par(self, name, val):
        if val is not None:
            setattr(self, '_' + name, val)
    
    def _set_num_den(self):
        L = self._L*1e-6
        C = self._C*1e-12
        R = self._R
        self._num = [1]
        self._den = [L*C, R*C, 1]
    
    def get_tf(self):
        self._set_num_den()
        return signal.TransferFunction(self._num, self._den)

class TimeDomainConv():
    def set_tf(self, transfer_function):
        self.tf=transfer_function
        
    def set_time_arry(self, t):
        self._t = t
        
    def get_td_data(self):
        # If signal.impulse2 is used. Result is numeric calculated. Therfore,
        # there are slite difference to correct value.
        return signal.impulse(self.tf, T = self._t)