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
    pass

class TimeDomainConv():
    def set_tf(self, transfer_function):
        self.tf=transfer_function
        
    def set_time_arry(self, t):
        self._t = t
        
    def get_td_data(self):
        # If signal.impulse2 is used. Result is numeric calculated. Therfore,
        # there are slite difference to correct value.
        return signal.impulse(self.tf, T = self._t)