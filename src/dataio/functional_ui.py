# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 21:04:29 2019

@author: LiNaK
"""

# Standard module

# 3rd party's module

# Original module  
from context import src # path setting

# interface
from src.interface.intfc_com import PathAsk

class FixPathAskGenerater():
    '''
    return the class which return the fixed path defined in this class.
    '''
    def __init__(self, dummypath = ''):
        self._dummypath = dummypath
    
    def set_fixpath(self, dummypath):
        self._dummypath = dummypath
    
    def generate_class(self):
        class DummyDataFixedPathClass(_FixedPathClass):
            _dummy_path=self._dummypath
        return DummyDataFixedPathClass

class _FixedPathClass(PathAsk):
    '''
    This class return fixed path: self._dummy_path.
    This class is used in FixPathAskGenerater which return class that return
    fixed path. class returned by FixPathAskGenerater inherit this class.
    FixPathAskGenerater change _dummy_path.
    '''
    _dummy_path = ''
    def get_path(self, *args, **kwargs):
        return self._dummy_path 