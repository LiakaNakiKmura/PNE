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
from src.interface.intfc_com import (Reader, )
from src.dataio.io_com import PathDialog

class CSVIO(Reader):
    def __init__(self):
        self.path_dialog =  PathDialog()
        
    def read(self, message):
        data_path = self.path_dialog.get_path(message)
        return  pd.read_csv(data_path)
    