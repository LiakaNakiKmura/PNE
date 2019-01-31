# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 00:12:46 2019

@author: LiNaK
"""

# Standard module
import abc

# 3rd party's module

# Original module  

class Transaction(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def execute(self):
        pass