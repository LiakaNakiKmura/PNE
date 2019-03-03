# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 20:43:04 2019

@author: LiNaK
"""

# Standard module
import abc

# 3rd party's module
import numpy as np
import pandas as pd

# Original module  

#interfaces
from src.interface.intfc_com import Transaction

#utilities
from src.utility.utility import singleton_decorator, read_only_getter_decorator
from src.utility.calc import MagLogUtil
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
        data = self.pndb.get_closeloop_noise(parameter)     
        self.csvio.write(message, data)

class PNCalc(Transaction):
    def __init__(self):
        self._ndb = NoiseDataBase()
        self._tfdb = TransferfuncDataBase()
        self._cldb = CloseLoopDataBase()
        self.mlu = MagLogUtil()
        self.pnpm = PNPrmtrMng()
        
    def execute(self):
        self._get_data()
        self._do_calc()
    
    def _get_data(self):
        self._noise_names = self._ndb.get_names()
        self._noises = self._get_datalist(self._ndb)
        self._tfs = self._get_datalist(self._tfdb)
        self._opnlp = self._tfdb.get_data(self.pnpm.open_loop_gain)
    
    def _get_datalist(self, database):
        return {name: database.get_data(name) for name in self._noise_names}
    
    def _do_calc(self):
        '''
        Output noise = Transfer func from 
        '''
        self._closelp =1/(1+self._opnlp[self._tfdb.index_val])
        self._closed_pn = {}
        for name in self._noise_names:
            
            filter_compression_mag = self._closelp*self._tfs[name][self._tfdb.index_val]
            filter_compression_log = self.mlu.mag2log(abs(filter_compression_mag),20)
            self._closed_pn[name] = self._noises[name][self._ndb.index_val]\
            + filter_compression_log
        
        total_pn_val = np.array([-1e10 for _ in range(len(self._closelp))])
        for pn in self._closed_pn.values():
            add_pn =  self.mlu.log2mag(pn, N = 10)
            tota_pn_buf = self.mlu.log2mag(total_pn_val, 10)
            total_pn_val = self.mlu.mag2log(add_pn+tota_pn_buf, N = 10)
        total_pn = pd.concat([self._opnlp[self._tfdb.index_freq], total_pn_val],
                              axis = 1)
        self._cldb.set_data(self.pnpm.total, total_pn)
        

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
    
    def set_closeloop_noise(self, name, data):
        self._combined_noise[name] = data
    
    def get_closeloop_noise(self, name):
        return self._combined_noise[name]
    
    def reflesh_all(self):
        self._noise = {}
        self._tf = {}
        self._combined_noise = {}


@read_only_getter_decorator({'ref':'reference', 'vco':'VCO', 
                             'pd':'phase_detector', 
                             'open_loop_gain': 'open_loop_gain',
                             'total': 'total_data'})
@read_only_getter_decorator({'noise':'Noise', 'tf':'TransferFunction', 
                             'combpn':'Combined Phase Noise'})
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
    index_freq = 'frequency'
    
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

class IndivDataBase(metaclass = abc.ABCMeta):
    '''
    Data Base interface for each data. Ex noise, transfer function...
    This has index name variables. 
    getter and setter is get_data and set_data.
    '''
    index_freq = ''
    index_val = ''
    _getter_attr_for_pndb = 'get_data'
    _setter_attr_for_pndb = 'set_data'
    _index_max_length = 2
    
    def __init__(self):
        self.pndb = PNDataBase()
        self._getter = getattr(self.pndb, self._getter_attr_for_pndb)
        self._setter = getattr(self.pndb, self._setter_attr_for_pndb)
    
    def get_data(self, name):
        return self._getter(name)
    
    def set_data(self, name, data):
        new_name, new_data = self._validation(name, data)
        return self._setter(new_name, new_data)
    
    def _validation(self, name, data):
        if len(data.columns) > self._index_max_length:
            return (name, data.iloc[:, :self._index_max_length])
        return (name, data)
    
@read_only_getter_decorator({'index_freq':PNPrmtrMng.index_freq, 
                             'index_val':'Noise'})
class NoiseDataBase(IndivDataBase):
    _getter_attr_for_pndb = 'get_noise'
    _setter_attr_for_pndb = 'set_noise'
    
    def get_names(self):
        return self.pndb.get_noise_names()

@read_only_getter_decorator({'index_freq':PNPrmtrMng.index_freq, 
                             'index_val':'Transfer function'})
class TransferfuncDataBase(IndivDataBase):  
    _getter_attr_for_pndb = 'get_transfer_func' 
    _setter_attr_for_pndb = 'set_transfer_func' 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mlu = MagLogUtil()
    
    def set_mag_deg_data(self, name, data):
        '''
        data has following columns.
        (freq, amplitude, angular)
        '''
        freq = data.iloc[:, 0]
        amplitude = data.iloc[:, 1]
        degree = data.iloc[:, 2]
        transferfunc = self.mlu.magdeg2comp(amplitude, degree)
        new_data = pd.concat([freq, transferfunc], axis = 1)
        self.set_data(name, new_data)

@read_only_getter_decorator({'index_freq':PNPrmtrMng.index_freq, 
                             'index_val':'Close loop data'})
class CloseLoopDataBase(IndivDataBase):
    _getter_attr_for_pndb = 'get_closeloop_noise'
    _setter_attr_for_pndb = 'set_closeloop_noise'
