# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 20:43:04 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module

# Original module  

#interfaces
from src.interface.intfc_com import Transaction
#from src.interface.calc_data import (PN_TF_Calc)

#utilities
from src.utility.utility import singleton_decorator, read_only_getter_decorator
from src.dataio.csvio import CSVIO


class PNCombiner(Transaction):
    def __init__(self):
        self._reader = PNDataReader()
        self._writer = PNDataWriter()
        self._pnc = PNCalc()
    
    def execute(self):
        pass

class PNDataReader(Transaction):
    def __init__(self):
        self.csvio = CSVIO()
        self.pnpm = PNPrmtrMng()
        self.pndb = PNDataBase()
        self.prmtr_mng = PNPrmtrMng()
    
    def execute(self):
        data = self.csvio.read(self.prmtr_mng.get_message(self.pnpm.ref))
        self.pndb.set_noise(self.pnpm.ref, data)

class PNDataWriter(Transaction):
    def execute(self):
        pass

class PNCalc(Transaction):
    def execute(self):
        pass

@singleton_decorator
class PNDataBase():
    def __init__(self):
        self._noise = {}
    
    def set_noise(self, name, data):
        self._noise[name] = data
    
    def get_noise(self, name):
        return self._noise[name]
    
    def set_transfer_func(self):
        pass
    
    def get_transfer_func(self):
        pass
    
    def set_pn(self):
        pass
    
    def get_pn(self):
        pass


@read_only_getter_decorator({'ref':'reference', 'vco':'VCO', 
                             'pd':'phase_detector', 
                             'open_loop_gain': 'open_loop_gain'})
class PNPrmtrMng():
    _reading_param_message_pairs = {
            'ref':'Please input reference phase noise.', 
            'vco':'Please input VCO phase noise.',
            'pd':'Please input phase detector phase noise.',
            'open_loop_gain':'Please input open loop gain data.'
            }
    
    def __init__(self):
        #self._set_property()
        self._make_read_message_dict()
    
    def get_message(self, parameter_name):
        return self._read_message_dict[parameter_name]
    
    def _make_read_message_dict(self):
        # Make dictironaly of {parameter str: message}.
        self._read_message_dict = {}
        for n, msg in self._reading_param_message_pairs.items():
            self._read_message_dict[getattr(self, n)] = msg
