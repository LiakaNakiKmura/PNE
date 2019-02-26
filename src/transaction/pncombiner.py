# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 20:43:04 2019

@author: LiNaK
"""

# Standard module
import abc

# 3rd party's module


# Original module  

#interfaces
from src.interface.intfc_com import Transaction

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


class _PNDataIOCommon(Transaction):
    '''
    This is the base class to read or write data that is listed in '_target'
    from or to output.
    '''
    _target = []
    
    def __init__(self):
        self.csvio = CSVIO()
        self.pndb = PNDataBase()
        self.pnpm = PNPrmtrMng()
        self._set_io_setting()

    def execute(self):
        for name in self._target:
            parameter, message = self._get_parameter_msg(name)
            self._do_io(parameter, message)
    
    @abc.abstractmethod
    def _set_io_setting(self):
        '''
        Subclass is needed to overwrite this method to set the _io_setting as
        reding or writing defined in PNPrmtrMng. This setting will be used for
        choosing the message reading or writing.
        '''
        self._io_setting = None
    
    def _get_parameter_msg(self, name):
        parameter = getattr(self.pnpm, name)
        message = self.pnpm.get_message(self._io_setting, parameter)
        return (parameter, message)
    
    @abc.abstractmethod
    def _do_io(self, parameter, message):
        '''
        Subclass is needed to overwrite to set the reading or writing.
        '''
        pass

class PNDataReader(_PNDataIOCommon):
    _target = ['ref', 'vco', 'pd', 'open_loop_gain']
    
    def _set_io_setting(self):
        self._io_setting = self.pnpm.read_setting
    
    def _do_io(self, parameter, message):
        data = self.csvio.read(message)
        self.pndb.set_noise(parameter, data)


class PNDataWriter(_PNDataIOCommon):
    _target=['total']
    
    def _set_io_setting(self):
        self._io_setting = self.pnpm.write_setting
    
    def _do_io(self, parameter, message):
        data = self.pndb.get_combined_noise(parameter)     
        self.csvio.write(message, data)

class PNCalc(Transaction):
    def __init__(self):
        self._pndb = PNDataBase()
        pass
        
    def execute(self):
        pass
    
    def _get_data(self):
        
        pass

@singleton_decorator
class PNDataBase():
    def __init__(self):
        self.reflesh_all()
    
    def set_noise(self, name, data):
        self._noise[name] = data
    
    def get_noise(self, name):
        return self._noise[name]
    
    def get_noise_names(self):
        return self._noise.keys()
    
    def set_transfer_func(self, name, data):
        self._tf[name] = data
    
    def get_transfer_func(self, name):
        return self._tf[name]
    
    def set_combined_noise(self, name, data):
        self._combined_noise[name] = data
    
    def get_combined_noise(self, name):
        return self._combined_noise[name]
    
    def reflesh_all(self):
        self._noise = {}
        self._tf = {}
        self._combined_noise = {}


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