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
from pandas import DataFrame, Series
from scipy.interpolate import interp1d

# Original module  

#interfaces
from src.interface.intfc_com import Transaction, Reader

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
    
    def get_transfer_func_names(self):
        return self._tf.keys()
    
    def set_closeloop_noise(self, name, data):
        self._combined_noise[name] = data
    
    def get_closeloop_noise(self, name):
        return self._combined_noise[name]
    
    def get_closeloop_noise_names(self):
        return self._combined_noise.keys()
    
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
    # getter attribute name of pndb method.
    _setter_attr_for_pndb = 'set_data'
    # setter attribute name of pndb method.
    _getname_attr_for_pndb = 'get_names'
    # getter attribute to get names of set to database.
    _index_length = 2
    
    def __init__(self):
        self.pndb = PNDataBase()
        self._getter = getattr(self.pndb, self._getter_attr_for_pndb)
        self._setter = getattr(self.pndb, self._setter_attr_for_pndb)
        self._get_name = getattr(self.pndb, self._getname_attr_for_pndb)
        self._mlu = MagLogUtil()
    
    def get_data(self, name, freq_range = None):
        if freq_range is None:
            return self._getter(name)
        return self._vlogf_interpolation(self._getter(name), freq_range)
        
    def set_data(self, name, data):
        new_name, new_data = self._validation(name, data)
        return self._setter(new_name, new_data)
    
    def get_names(self):
        return list(self._get_name())
    
    
    def _vlogf_interpolation(self, data, freq_new):        
        func = self._mlu.ylogx_interpolite(data.loc[:, self.index_freq], 
                                           data.loc[:, self.index_val],
                                           bounds_error = False)
        
        data_new = DataFrame([freq_new, func(freq_new)]).T
        data_new.columns = [self.index_freq, self.index_val]
        
        return data_new
    
    def _validation(self, name, data):
        if type(data) != type(DataFrame([])):
            raise TypeError('data type must be pandas dataframe.')

        if len(data.columns) < self._index_length:
            # if number of columns is short, value error 
            raise ValueError('data index length must be {}'\
                             .format(self._index_length))
        
        # limit the length of columns.
        new_data = data.iloc[:, :self._index_length]
        # rename the columns for fit data.
        new_data.columns = [self.index_freq, self.index_val]
        return (name, new_data)

@read_only_getter_decorator({'index_freq':PNPrmtrMng.index_freq, 
                             'index_val':'Noise'})
class NoiseDataBase(IndivDataBase):
    _getter_attr_for_pndb = 'get_noise'
    _setter_attr_for_pndb = 'set_noise'
    _getname_attr_for_pndb = 'get_noise_names'


@read_only_getter_decorator({'index_freq':PNPrmtrMng.index_freq, 
                             'index_val':'Transfer function'})
class TransferfuncDataBase(IndivDataBase):  
    _getter_attr_for_pndb = 'get_transfer_func' 
    _setter_attr_for_pndb = 'set_transfer_func' 
    _getname_attr_for_pndb = 'get_transfer_func_names'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mlu = MagLogUtil()
    
    def set_mag_deg_data(self, name, data):
        '''
        transform data from amplitude and angular data to complex number and
        set to database.
        
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
    _getname_attr_for_pndb = 'get_closeloop_noise_names'

class NoiseTransfuncPairsManager():
    def __init__(self):
        self.ndb = NoiseDataBase()
        self.tfdb = TransferfuncDataBase()
        
        # self.pndb = PNDataBase()
        
    def get_pair_names(self):
        noise_names = self.ndb.get_names()
        tf_names = self.tfdb.get_names()
        return list(set(noise_names) & set(tf_names))

@read_only_getter_decorator({'name':'parameter name'})
#name must be overwrite in inhirated class.
class ParameterManager(metaclass = abc.ABCMeta):
    _acceptable_databases = []
    def __init__(self):
        self._make_datanames_dict()
    
    def get_dataname(self):
        '''
        Data name refers to what type of data(noise, transferfuntion...) and
        Prameter.
        '''
        return self._datanames[self._data_type]
    
    def set_type(self, new_type):
        if new_type in self._datanames.keys():
            self._data_type = new_type
        else:
            raise ValueError('{} is invalid type to be set'.format(new_type))
    
    def _make_datanames_dict(self):
        # Dataname is made from database and parameter name.
        self._datanames = {}
        for DB in self._acceptable_databases:
            db =DB()
            self._datanames[db.index_val] = '{} of {}'.format(\
                         db.index_val, self.name)
        
        self._data_type = self._acceptable_databases[0]().index_val
        # init data_type is first database in self._acceptable_databases.

@read_only_getter_decorator({'name':'open loop'})
class OpenLoopParameter(ParameterManager):
    #_message = 'open loop of PLL'
    _acceptable_databases = [TransferfuncDataBase]

@read_only_getter_decorator({'name':'reference'})
class RefParameter(ParameterManager):
    _acceptable_databases = [NoiseDataBase, TransferfuncDataBase]

@read_only_getter_decorator({'name':'VCO'})
class VCOParameter(ParameterManager):
    _acceptable_databases = [NoiseDataBase, TransferfuncDataBase]

@read_only_getter_decorator({'name':'Total Out'})
class TotalOutParameter(ParameterManager):
    _acceptable_databases = [CloseLoopDataBase]

class DataReader(Transaction):
    '''
    DataReader set data of ParameterManager from Reder to Database.
    ReaderClass: subclass of Reader
    DataBaseClass: subclass of IndivDataBase
    ParameterManagerClass: subclass of ParameterManager
    
    Combination of command pattern, Factory pattern, Staratagy pattern.
    '''
    
    def __init__(self, ReaderClass, DatBaseClass,  ParameterManagerClass):
        self.check_inherited(ReaderClass, DatBaseClass,  ParameterManagerClass)
        
        self._reader = ReaderClass()
        self._database = DatBaseClass()
        self._pr_mng = ParameterManagerClass()
        self._pr_mng.set_type(self._database.index_val)
        # prameter manager needed to know what kind of database.
    
    def execute(self):
        data = self._reader.read(self._pr_mng.get_dataname())
        self._database.set_data(self._pr_mng.name, data)
        
    def check_inherited(self, ReaderClass, DatBaseClass,  
                        ParameterManagerClass):
        inheritance_pair = {ReaderClass: Reader,
                            DatBaseClass: IndivDataBase,
                            ParameterManagerClass: ParameterManager}
        
        for Class in (ReaderClass, DatBaseClass,  ParameterManagerClass):
            parent = inheritance_pair[Class]
            assert issubclass(Class, parent),\
            '{} must be subclass of Reader'.format(parent)
            
#TODO: Make DataWriter.
class DataWriter(Transaction):
    def __init__(self, WriterClass, DatBaseClass,  ParameterManagerClass):
        self._writer = WriterClass()
        self._database = DatBaseClass()
        self._pr_mng = ParameterManagerClass()
        self._pr_mng.set_type(self._database.index_val)
    
    def execute(self):
        data = self._database.get_data(self._pr_mng.name)
        self._writer.write(self._pr_mng.get_dataname(), data)

class PNDataReader(Transaction):
    _DataBase_Reader_pair = [[CSVIO, NoiseDataBase, RefParameter],
                             [CSVIO, TransferfuncDataBase, RefParameter],
                             [CSVIO, NoiseDataBase, VCOParameter],
                             [CSVIO, TransferfuncDataBase, VCOParameter],
                             [CSVIO, TransferfuncDataBase, OpenLoopParameter]
                             ]
    
    def __init__(self):
        self._set_datareader()
    
    def execute(self):
        for datareader in self.datareaders:
            datareader.execute()
    
    def _set_datareader(self):
        self.datareaders = []
        for pair in self._DataBase_Reader_pair:
            self.datareaders.append(DataReader(*pair))

class PNDataWriter(Transaction):
    _DataBase_Writer_pair = [[CSVIO, CloseLoopDataBase, TotalOutParameter]
                             ]
    # TODO: Make DataWriter class 
    
    def execute(self):
        for pairs in self._DataBase_Writer_pair:
            self._write_data(*pairs)
    
    def _write_data(self, WriterClass, DataBaseClass, ParameterManagerClass):
        db = DataBaseClass()
        pm = ParameterManagerClass()
        pm.set_type(db.index_val)
        data = db.get_data(pm.get_dataname())
        writer = WriterClass()
        writer.write(pm.get_dataname(), data)