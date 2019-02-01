# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 21:50:20 2019

@author: LiNaK
"""

# Standard module
import abc

# 3rd party's module

# Original module  

class PN_TF_Calc(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def set_open_loop(self, openloop):
        """
        openloop: pair of openloop and offsetfrequency
        """
        pass
    
    @abc.abstractmethod
    def set_noise(self, noise, output_transfer_func):
        pass

    @abc.abstractmethod
    def get_total_noise(self, freq):
        pass 