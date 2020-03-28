# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 00:12:46 2019

@author: LiNaK
"""

# Standard module
import abc

# 3rd party's module

# Original module  

class Transaction(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def execute(self):
        pass

class Reader(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def read(self, message):
        pass
    
class Writer(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def write(self, message, data):
        pass

class PathAsk(metaclass = abc.ABCMeta):
    # FIXME: Change Just get_path method    
    @abc.abstractmethod
    def get_path(self, message):
        pass

class ValueAsk(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def get_value(self, message):
        pass
    
class TF_Maker(metaclass = abc.ABCMeta):
    '''
    This class make the transfer function (scipy.signal.lti).  
    '''
    @abc.abstractmethod
    def get_tf(self):
        '''
        Return the transfer function class (scipy.signal.lti).  
        '''
        return None