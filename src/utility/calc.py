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
from pandas import Series
from scipy.interpolate import interp1d

# Original module  

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
    
    def __init__(self):
        self._datadict = {}
        
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
        self._calc_min_max_range()
        return self._get_interpolated_range(self._datadict[name])
    
    def get_common_range(self):
        self._calc_min_max_range()
        self._make_common_range()
        return self._new_range
    
    def _calc_min_max_range(self):
        self.freq_data = [df.loc[:, self._column_name]\
                          for df in self._datadict.values()]
        self._min_val = max([S.min() for S in self.freq_data])
        # get the maximum data from each minimudata for narrowest range.
        self._max_val = min([S.max() for S in self.freq_data])
        # get the maximum data from each minimudata for narrowest range.
    
    def _make_common_range(self):
        extendedS = Series([])
        for dataS in self.freq_data:
            new_range = dataS[(self._min_val <= dataS) &\
                              (dataS <= self._max_val) ]
            extendedS = extendedS.append(new_range)
        
        self._new_range = Series(sorted(extendedS.unique()),
                                 name = self._column_name,
                                 dtype = 'f8')
    
    def _get_interpolated_range(self, df):
        S_range = df.loc[:, self._column_name]
        new_range_bool = (self._min_val <= S_range) &\
        (S_range <= self._max_val)
        return df.loc[new_range_bool,:].reset_index(drop = True)