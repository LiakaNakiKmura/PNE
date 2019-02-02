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
        reader = PNDataReader()
        writer = PNDataWriter()
        pnc = PNCalc()
    
    def execute(self):
        pass

class PNDataReader(Reader):
    def read(self):
        pass

class PNDataWriter(Writer):
    def read(self):
        pass
    
class PNCalc(PN_TF_Calc):
    def set_open_loop(self, openloop):
        pass
    
    def set_noise(self, noise):
        pass
    
    def get_total_noise(self, noise):
        pass