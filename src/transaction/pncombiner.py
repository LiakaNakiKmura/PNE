# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 20:43:04 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module

# Original module  
from src.interface.common import Transaction
from src.interface.common import (Reader, Writer)
from src.interface.calc_data import (PN_TF_Calc)

class PNCombiner(Transaction):
    def __init__(self):
        self._reader = PNDataReader()
        self._writer = PNDataWriter()
        self._pnc = PNCalc()
    
    def execute(self):
        pass

class PNDataReader(Reader):
    def read(self):
        pass

class PNDataWriter(Writer):
    def write(self):
        pass
    
class PNCalc(PN_TF_Calc):
    def calc(self):
        pass

class PNDataBase():
    def set_noise(self):
        pass
    
    def get_noise(self):
        pass
    
    def set_transfer_func(self):
        pass
    
    def get_transfer_func(self):
        pass
    
    def set_pn(self):
        pass
    
    def get_pn(self):
        pass