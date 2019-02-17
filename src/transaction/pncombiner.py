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
            data = self.csvio.read(self.prmtr_mng.get_message(
                    self.prmtr_mng.read_setting, parameter))
            
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
    
    read_setting = 'r'
    write_setting = 'w'
    
    def __init__(self):
        self._make_message_dict()

    def get_message(self, usage, parameter_name):
        return self._message_dict[usage][parameter_name]

    def _make_message_dict(self):
        # Make dictironaly of {usage:{parameter str: message}}.
        self._message_dict = {}
        usage_name_msg_pairs =\
        {self.read_setting: self._reading_param_message_pairs,
         self.write_setting: self._writing_param_message_pairs
         }

        for usage, msg_pairs in usage_name_msg_pairs.items():
            self._message_dict[usage]=\
            {getattr(self, name): msg for name, msg in msg_pairs.items()}