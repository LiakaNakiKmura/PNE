# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 00:12:46 2019

@author: LiNaK
"""

# Standard module
import abc

# 3rd party's module

# Original module  

class Parts(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def get_data(self):
        pass
    
    @abc.abstractmethod
    def set_data(self):
        pass
    
    @abc.abstractmethod
    def get_parameter_name(self):
        pass
