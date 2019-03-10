# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 21:45:21 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module

# Original module  
from src.interface.intfc_com import (ValueAsk)

class ValueAskCUI(ValueAsk):
    def get_value(self, message):
        return input(message+'\n')
