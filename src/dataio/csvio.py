# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 12:34:50 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module
import pandas as pd

# Original module  
from context import src # path setting

# interface
from src.interface.intfc_com import (Reader, Writer)
from src.dataio.io_com import PathDialog



class CSVIO(Reader, Writer):
    def __init__(self):
        self.path_dialog =  PathDialog()
        
    def read(self, data_name):
        '''
        DataFrame is get from csv.
        '''
        data_path = self.path_dialog.get_path(self._message(data_name))
        return  pd.read_csv(data_path)
    
    def write(self, data_name, data_df):
        '''
        DataFrame is conversed to csv
        NO index.
        '''
        data_path = self.path_dialog.get_path(self._message(data_name))
        data_df.to_csv(data_path, index = False)
    
    def _message(self, data_name):
        return 'Please select the file for {}'.format(data_name)
    
    
