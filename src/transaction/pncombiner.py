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
        self.pndb = PNDataBase()
        self.prmtr_mng = PNPrmtrMng()
    
    def execute(self):
        self._readint_targets_list()
    
    def _readint_targets_list(self):
        reading_target=['ref', 'vco', 'pd', 'open_loop_gain']
        for name in reading_target:
            parameter = getattr(self.prmtr_mng, name)
            data = self.csvio.read(self.prmtr_mng.get_reading_message(parameter))
            self.pndb.set_noise(parameter, data)

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
        self._combined_noise = {}
    
    def set_noise(self, name, data):
        self._noise[name] = data
    
    def get_noise(self, name):
        return self._noise[name]
    
    def set_transfer_func(self):
        pass
    
    def get_transfer_func(self):
        pass
    
    def set_combined_noise(self, name, data):
        self._combined_noise[name] = data
    
    def get_combined_noise(self, name):
        return self._combined_noise[name]


@read_only_getter_decorator({'ref':'reference', 'vco':'VCO', 
                             'pd':'phase_detector', 
                             'open_loop_gain': 'open_loop_gain',
                             'total': 'total_data'})
class PNPrmtrMng():
    _reading_param_message_pairs = {
            'ref':'Please input reference phase noise.', 
            'vco':'Please input VCO phase noise.',
            'pd':'Please input phase detector phase noise.',
            'open_loop_gain':'Please input open loop gain data.'
            }
    _writing_param_message_pairs = {
            'total':'Please write the total data'
            }
    
    def __init__(self):
        #self._set_property()
        self._make_read_message_dict()
        self._make_write_message_dict()
    
    def get_reading_message(self, parameter_name):
        return self._read_message_dict[parameter_name]
 
    def get_writing_message(self, parameter_name):
        return self._write_message_dict[parameter_name]
    
    def _make_read_message_dict(self):
        # Make dictironaly of {parameter str: message}.
        self._read_message_dict = {}
        for n, msg in self._reading_param_message_pairs.items():
            self._read_message_dict[getattr(self, n)] = msg

    def _make_write_message_dict(self):
        # Make dictironaly of {parameter str: message}.
        self._write_message_dict = {}
        for n, msg in self._writing_param_message_pairs.items():
            self._write_message_dict[getattr(self, n)] = msg