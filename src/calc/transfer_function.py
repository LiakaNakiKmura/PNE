# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 22:23:41 2019

@author: LiNaK
"""

# Standard module
import abc

# 3rd party's module
from scipy import signal

# Original module  
from context import src # path setting

# interface
from src.interface.intfc_com import TF_Maker 

class FilterTF(TF_Maker):
    def _set_each_par(self, name, val):
        if val is not None:
            setattr(self, '_' + name, val)

    @abc.abstractmethod
    def _set_num_den(self):
        pass
    
    def get_tf(self):
        self._set_num_den()
        return signal.TransferFunction(self._num, self._den)

#class LCRLPF(TF_Maker):
class LCRLPF(FilterTF):
    def __init__(self):
        self._L = None #[uH]
        self._C = None #[pF]
        self._R = None #[Ohm]
    
    def set_parameter(self, L = None, C = None, R = None):
        for key, par in {'L':L, 'C':C, 'R':R}.items():
            self._set_each_par(key, par)
    
    def _set_num_den(self):
        L = self._L*1e-6
        C = self._C*1e-12
        R = self._R
        self._num = [1]
        self._den = [L*C, R*C, 1]

class UnitManger():
    _kinds_num_pairs = {'R':1, 'L':1e-6, 'C':1e-12}
    _prefix = {'y': 1e-24,  # yocto
               'z': 1e-21,  # zepto
               'a': 1e-18,  # att
               'f': 1e-15,  # femto
               'p': 1e-12,  # pico
               'n': 1e-9,   # nano
               'u': 1e-6,   # micro
               'm': 1e-3,   # mili
               'c': 1e-2,   # centi
               'd': 1e-1,   # deci
               'k': 1e3,    # kilo
               'M': 1e6,    # mega
               'G': 1e9,    # giga
               'T': 1e12,   # tera
               'P': 1e15,   # pet
               'E': 1e18,   # exa
               'Z': 1e21,   # zetta
               'Y': 1e24,   # yotta
               }
    def get_prefix_num(self, kinds):
        return self._kinds_num_pairs[kinds]

class TimeDomainConv():
    def set_tf(self, transfer_function):
        self.tf=transfer_function
        
    def set_time_arry(self, t):
        self._t = t
        
    def get_td_data(self):
        # If signal.impulse2 is used. Result is numeric calculated. Therfore,
        # there are slite difference to correct value.
        return signal.impulse(self.tf, T = self._t)