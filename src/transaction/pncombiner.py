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
    # FIXME: Refactoring.
    _noise = 'noise'
    _tf = 'tf'
    def __init__(self):
        self._ndb = NoiseDataBase()
        self._tfdb = TransferfuncDataBase()
        self._cldb = CloseLoopDataBase()
        self.mlu = MagLogUtil()
        self.opn_prm = OpenLoopParameter()
        self._total_out_prm = TotalOutParameter()
        self._noise_tf_pairs = NoiseTransfuncPairsManager()
        
    def execute(self):
        self._get_data()
        self._do_calc()
    
    def _get_data(self):
        self._data_names = self._noise_tf_pairs.get_pair_names()
        self._input_data= {}
        for name, db in {self._noise:self._ndb, self._tf:self._tfdb}.items():
            self._input_data[name] = self._get_datalist(db)
        self._noises = self._get_datalist(self._ndb)        
        self._tfs = self._get_datalist(self._tfdb)
        self._opnlp = self._tfdb.get_data(self.opn_prm.name)
    
    def _get_datalist(self, database):
        return {name: database.get_data(name) for name in self._data_names}
    
    def _do_calc(self):
        '''
        Output noise = Transfer func from 
        '''
        self._calc_closed_loop()
        self._calc_compressed_data()
        self._combine_each_pn()
    
    def _calc_closed_loop(self):
        self._closelp =1/(1+self._opnlp[self._tfdb.index_val])
        self._closed_pn = {}
        
    def __calc_compressed_data(self):
        for name in self._data_names:
            compressed_mag = self._closelp*self._tfs[name][self._tfdb.index_val]
            compressed_log = self.mlu.mag2log(abs(compressed_mag),20)
            self._closed_pn[name] = self._noises[name][self._ndb.index_val]\
            + compressed_log
    
    def _calc_compressed_data(self):
        for name in self._data_names:
            compressed_mag = self._closelp*self._tfs[name][self._tfdb.index_val]
            compressed_log = self.mlu.mag2log(abs(compressed_mag),20)
            self._closed_pn[name] = self._noises[name][self._ndb.index_val]\
            + compressed_log
    
    def _combine_each_pn(self):
        total_pn_val = np.array([-1e10 for _ in range(len(self._closelp))])
        # Initialize data is set to small value to be ignored.
        for pn in self._closed_pn.values():
            add_pn =  self.mlu.log2mag(pn, N = 10)
            tota_pn_buf = self.mlu.log2mag(total_pn_val, 10)
            total_pn_val = self.mlu.mag2log(add_pn+tota_pn_buf, N = 10)
        total_pn = pd.concat([self._opnlp[self._tfdb.index_freq], total_pn_val],
                              axis = 1)
        self._cldb.set_data(self._total_out_prm.name, total_pn)

class PhaseNoiseCalculator():
    # Add comment of open loop gain sign.
    def __init__(self):
        self.mlu = MagLogUtil()
        self._read_column_name()
    
    def _read_column_name(self):
        self._freq_column = CommonParameter().index_freq
        self._noise_column = NoiseDataBase().index_val
        self._tf_column = TransferfuncDataBase().index_val
        self._clsd_columns = [self._freq_column, 
                              CloseLoopDataBase().index_val]        
    
    def set_open_loop(self, open_loop_dataframe):
        # Open loop data must be greater than 0.
        # Open loop unit is freq: Hz, Transfer fuction: complex.
        self._olp = open_loop_dataframe
        
    def set_noise(self, noise_dataframe):
        self._noise = noise_dataframe
    
    def set_tf(self, transfer_function_dataframe):
        self._tf = transfer_function_dataframe
        
    def get_compressed_noise(self):
        return self._calc()
    
    def _calc(self):
        freq = self._olp.loc[:, self._freq_column]
        olp_tf = self._olp.loc[:, self._tf_column]
        out_tf = self._tf.loc[:, self._tf_column]
        noise = self._noise.loc[:, self._noise_column]
        
        clsdlp = abs(out_tf/(1+olp_tf))
        # Close loop is calculated as T_out/(1+T_total)
        cmprd_noise = self.mlu.mag2log(clsdlp, N=20)+noise        
        return DataFrame([freq, cmprd_noise], index = self._clsd_columns,
                         dtype = 'f8').T
        # self._clsd_columns is set to index because transpositon the dataframe.


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
class CommonParameter():
    # FIXME: Refactoring to delete this class 
    index_freq = 'frequency'

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

@read_only_getter_decorator({'index_freq':CommonParameter.index_freq, 
                             'index_val':'Noise'})
class NoiseDataBase(IndivDataBase):
    _getter_attr_for_pndb = 'get_noise'
    _setter_attr_for_pndb = 'set_noise'
    _getname_attr_for_pndb = 'get_noise_names'


@read_only_getter_decorator({'index_freq':CommonParameter.index_freq, 
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
        (freq[Hz], amplitude[mag], angular[deg])
        '''
        freq = data.iloc[:, 0]
        amplitude = data.iloc[:, 1]
        degree = data.iloc[:, 2]
        
        transferfunc = self.mlu.magdeg2comp(amplitude, degree)
        new_data = pd.concat([freq, transferfunc], axis = 1)
        self.set_data(name, new_data)


@read_only_getter_decorator({'index_freq':CommonParameter.index_freq, 
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

#@read_only_getter_decorator({'name':'open_loop_gain'})
@read_only_getter_decorator({'name':'open loop gain'})
class OpenLoopParameter(ParameterManager):
    #_message = 'open loop of PLL'
    _acceptable_databases = [TransferfuncDataBase]

@read_only_getter_decorator({'name':'reference'})
class RefParameter(ParameterManager):
    _acceptable_databases = [NoiseDataBase, TransferfuncDataBase]

@read_only_getter_decorator({'name':'VCO'})
class VCOParameter(ParameterManager):
    _acceptable_databases = [NoiseDataBase, TransferfuncDataBase]
    
#@read_only_getter_decorator({'name':'total_data'})
@read_only_getter_decorator({'name':'total out'})
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
    # Fixme: refactoring to use DataWriter.
    def __init__(self):
        pass
    
    def execute(self):
        for pairs in self._DataBase_Writer_pair:
            self._datawriter = DataWriter(*pairs)
            self._datawriter.execute()