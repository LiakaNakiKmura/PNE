# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 19:23:30 2019

@author: LiNaK
"""

# Standard module
import numbers 

# 3rd party's module
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
from scipy.interpolate import interp1d

# Original module  

class CalcUtilError(Exception):pass

class MagLogUtil():
    
    def _chk_type_and_apply_func(self, conv_func, data, N):
        dtype =type(data)
        if dtype==list:
            # Change np.ndarray format to calc. Return type is list
            return list(conv_func(np.array(data), N))
        
        elif dtype == np.ndarray or dtype == pd.core.series.Series or\
        isinstance(data, numbers.Number):
            return conv_func(data,N)
        
        else:
            raise TypeError
    
    def log2mag(self, data, N=10):
        def calc(data, N):
            return 10**(data/N)
        return self._chk_type_and_apply_func(calc, data, N)

    def mag2log(self, data, N=10):
        def calc(data, N):
            return N*np.log10(data)
        return self._chk_type_and_apply_func(calc, data, N)
    
    def magdeg2comp(self, mag, deg):
        return mag*np.exp(np.deg2rad(deg)*1j)
    
    def ylogx_interpolite(self, x, y, *args, **kwargs):
        log10x = Series(np.log10(x))
        valid = ~(np.isnan(log10x)|np.isnan(y))
        #pick up non-nan data to drop nan data from log x, y
        
        interpolite = interp1d(log10x[valid], Series(y)[valid], *args, **kwargs)
        return lambda x_new : interpolite(np.log10(x_new))

class RangeAdjuster():
    '''
    Adjust range of data.
    After setting some data, possible range is calculated and get fit data from
    input data.
    '''
    # FIXME: Buf exists. 
    _data_column_number = 1
    
    def __init__(self):
        self._datadict = {}
        self.mlu = MagLogUtil()
        self._column_name = None
        
    def set_column(self, column_name):
        '''
        set the column name as range. This name is used for search range of 
        each data set in set_data.
        column_name: number or string object to be used to column of dataframe.
        '''
        self._column_name = column_name
    
    def set_data(self, target_dataframe, name):
        '''
        set data.
        target_dataframe: DataFrame object. This has 2 length of colmuns.
        '''
        self._datadict[name] = target_dataframe
    
    def get_ranged_data(self, name):
        '''
        Return the interpolated common ranged 'dataframe' data.
        data must be (range, data) pairs. 2nd column is used as data.
        '''
        self._check_setting()
        self._calc_range()
        return self._get_interpolated_range(name)
    
    def get_common_range(self):
        # Return the just common 'range' Series data.
        self._check_setting()
        self._calc_range()
        return self._new_range
    
    def _check_setting(self):
        if self._column_name is None:
            raise CalcUtilError('column_name must be set.')
            
        for df in self._datadict.values():
            if not self._column_name in df.columns:
                raise KeyError(self._column_name)

    def _calc_range(self):
        self._calc_min_max_range()
        self._make_common_range()
        
    def _calc_min_max_range(self):
        '''
        Serach min max of common range of each data.
        self._min_val, self._max_val is in band minimum and maximum of range
        data.
        '''
        self.freq_data = [df.loc[:, self._column_name]\
                          for df in self._datadict.values()]
        self._min_val = max([S.min() for S in self.freq_data])
        # get the maximum data from each minimudata for narrowest range.
        self._max_val = min([S.max() for S in self.freq_data])
        # get the maximum data from each minimudata for narrowest range.
    
    def _make_common_range(self):
        '''
        Common range of all range data. self._new_range is result.
        1. pick up in band data.
        2. Make "Set" of each data.
        3. Sorted
        '''
        extendedS = Series([])
        for dataS in self.freq_data:
            new_range = dataS[(self._min_val <= dataS) &\
                              (dataS <= self._max_val) ]
            extendedS = extendedS.append(new_range)
        
        self._new_range = Series(sorted(extendedS.unique()),
                                 name = self._column_name,
                                 dtype = 'f8')
    

    def _get_interpolated_range(self, name):
        '''
        Return dataframe of interpolated data about self._new_range.
        '''
        
        df = self._datadict[name]
        range_S = df.loc[:,self._column_name]
        data_S = df.iloc[:, self._data_column_number]
        
        inter_politer = self.mlu.ylogx_interpolite(range_S, data_S)
        inter_plited = inter_politer(self._new_range)
        
        return DataFrame([self._new_range, inter_plited],
                         index=df.columns,
                         dtype = 'f8').T