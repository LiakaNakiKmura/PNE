# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 22:58:00 2019

@author: LiNaK
"""

"""
Tests of pncombiner callables.
because import 
"""

# Standard module
import unittest
from unittest.mock import patch

# 3rd party's module
from pandas import Series, DataFrame
from pandas.testing import assert_series_equal, assert_frame_equal
import numpy as np

# Original module

# utlities.
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg
from test_utility import (Signletone_test_base, Inheration_test_base)

# Target class

from src.transaction.pncombiner import (PNCombiner,PNDataReader, PNDataWriter, 
                                        PNCalc, PNDataBase, PNPrmtrMng)

# interface
from src.interface.intfc_com import (Transaction, Reader, Writer)
import src.interface.intfc_com as intfc_com
#from src.interface.calc_data import (PN_TF_Calc)

# tool class
from src.dataio.csvio import (CSVIO)

@add_msg
class TestCombinePNInterfaces(Inheration_test_base,unittest.TestCase):
    # Test inheration of interfaces.
    _sub_sup_class_pairs = ((PNCombiner, Transaction),
                               (PNDataReader, Transaction),
                               (PNDataWriter, Transaction),
                               (PNCalc, Transaction)
                               )

@add_msg
class TestCombinePN(unittest.TestCase):
    """
    Test for combining phase noise from each component data.
    """
    
    def test_class_structure(self):
        """
        Test those classes is called in transaction class.
        """

        with patch('src.transaction.pncombiner.PNDataReader') as Reader_Mock,\
        patch('src.transaction.pncombiner.PNDataWriter') as Writer_Mock,\
        patch('src.transaction.pncombiner.PNCalc') as PNCalc_Mock:
            
            # Make instance. 
            pnc = PNCombiner()
            pnc.execute()
            
            # Following class is called when above instance is made.
            Reader_Mock.assert_called()
            Writer_Mock.assert_called()
            PNCalc_Mock.assert_called()
            del Reader_Mock
            
    def test_database_method(self):
        # Test interface has abstract method.
        method_names=('set_noise','get_noise', 'set_transfer_func',
                      'get_transfer_func', 'set_pn', 'get_pn')
        for  mth in method_names:
            self.assertTrue(callable(getattr(PNDataBase, mth)))

@add_msg
class TestPNparameter(unittest.TestCase):
    def test_parameter_exist(self):
        '''
        Parameter class testing.
        Parameter is property, is string that is greater than 0 length and 
        cannot be changed.
        '''
        pnpm = PNPrmtrMng()
        
        pn = Parameter_Names()
        attrnames = pn.get_parameter_names()
        for n in attrnames:
            prmtr = getattr(pnpm,n)
            self.assertTrue(isinstance(prmtr, str))
            self.assertTrue(0<len(prmtr))
            self.assertRaises(AttributeError, setattr, *(pnpm, n, 'a'))
            # Raise error if property value is changed.

    def test_read_file_message_exist(self):
        '''
        Test of Parameter message for reading data.
        Parameter class testing.
        Parameter is property, is string that is greater than 0 length and 
        cannot be changed.
        '''
        pnpm = PNPrmtrMng()
        
        pn = Parameter_Names()
        msg_parameters = pn.get_read_msg_parameters()
        for n in msg_parameters:
            prmtr = getattr(pnpm,n)
            
            prmtr_msg = pnpm.get_message(prmtr)
            self.assertTrue(isinstance(prmtr_msg, str))
            self.assertTrue(0<len(prmtr_msg))

class Parameter_Names():
    _names = ['ref', 'vco', 'pd']
    _msg_names = ['ref', 'vco', 'pd', 'open_loop_gain']
    _reading_lists = ['ref', 'vco', 'pd', 'open_loop_gain']
    _writing_lists = ['total']
    
    def __init__(self):
        self.pnpm = PNPrmtrMng()
    
    def get_parameter_names(self):
        return self._names
    
    def get_read_msg_parameters(self):
        return self._msg_names
    
    def get_read_msg_dict(self):
        prmtrs = [getattr(self.pnpm, n) for n in self._msg_names]
        return {prmtr: self.pnpm.get_message(prmtr) for prmtr in prmtrs}
    
    def get_reading_list(self):
        return [getattr(self.pnpm, name) for name in self._reading_lists]
 
    def get_write_msg_dict(self):
        prmtrs = [getattr(self.pnpm, n) for n in self._msg_names]
        return {prmtr: self.pnpm.get_message(prmtr) for prmtr in prmtrs}
    
    def get_writing_list(self):
        return [getattr(self.pnpm, name) for name in self._writing_lists]        

@add_msg
class Test_database_as_singleton(Signletone_test_base, unittest.TestCase):
    """
    Test PNDataBase is singleton.
    """
    _cls = PNDataBase


@add_msg  
class Test_database_detail(unittest.TestCase):
    def setUp(self):
        self.pndb = PNDataBase()
    
    def tearDown(self):
        del self.pndb
        '''
        Kill PNDataBase instance to reflesh data on each test because 
        pndatabase is singleton.
        '''
    def test_database_inputput(self):
        inputdatas = {'noise0':DataFrame(np.zeros((5,2))),
                      'noise1':DataFrame(np.ones((5,2))),
                      'noise2':DataFrame([[],[]]),
                  }
        addv = 2 #add value
        
        for n, d in inputdatas.items():
            self.pndb.set_noise(n,d)
        
        for n, d in inputdatas.items():
            assert_frame_equal(self.pndb.get_noise(n), d)
            #check the input data = output data
            
            self.pndb.set_noise(n,d+addv)
            #rewrite the data
        
        for n, d in inputdatas.items():
            assert_frame_equal(self.pndb.get_noise(n), d+addv)
            # check the rewrite data
            
            
@add_msg
class TestCombineRead(unittest.TestCase):
    """
    This is the test for reading data of transfer function, phasenoise dadta,
    noise data.
    """
    # Message of calling to read the data.
    
    def setUp(self):        
        self.pndb = PNDataBase()
        self.pnpm = PNPrmtrMng()
        self._set_ask_word()
        self._make_dummy_inputs()
    
    def tearDown(self):
        self._del_dummy_inputs()
        del self.pndb
        """
        Kill PNDataBase instance to reflesh data on each test because 
        pndatabase is singleton.
        """
        
    def _set_ask_word(self):
        pn = Parameter_Names()
        self._reading_message_dict = pn.get_read_msg_dict()  
        self._reading_list = pn.get_reading_list()
        # Message of calling to read the data.
        
    def _make_dummy_inputs(self):
        '''
        Make dummy data which match the message of reader is passed.
        '''
        
        self._msg_and_input ={}
        self._msg_para = dict((v,k) for k,v in 
                              self._reading_message_dict.items())
        self._inputdata = {}
        for i, parameter in enumerate(self._reading_list):
            self._inputdata[parameter] = DataFrame([[4*1,4*i+1],[4*i+2,4*i+3]])
    
    def _del_dummy_inputs(self):
        del self._msg_and_input
            
    def _input_side_effect_generator(self):
        """
        Generate the side_effect function which return the value match input
        message of reader.
        """
        
        def _side_effect(message):
            '''
            return the dummy data of self._inputdata. The data is chosen by 
            message. message is transformed into parameter in self._msg_para.
            '''
            return self._inputdata[self._msg_para[message]]
        return _side_effect
    
    def test_readdata(self):           
        with patch('src.transaction.pncombiner.CSVIO.read') as read_mock:
            read_mock.side_effect =self._input_side_effect_generator()
            
            pndata = PNDataReader()
            pndata.execute()
            
            for prmtr in self._reading_list:
                assert_frame_equal(self.pndb.get_noise(prmtr), 
                                   self._inputdata[prmtr])

@add_msg
class TestCombineWrite(unittest.TestCase):
    """
    This is the test for reading data of transfer function, phasenoise dadta,
    noise data.
    """
    # Message of calling to read the data.
    
    def setUp(self):        
        self.pndb = PNDataBase()
        self.pnpm = PNPrmtrMng()
        self._set_ask_word()
        self._make_dummy_inputs()
    
    def tearDown(self):
        self._del_dummy_inputs()
        del self.pndb
        """
        Kill PNDataBase instance to reflesh data on each test because 
        pndatabase is singleton.
        """
        
    def _set_ask_word(self):
        pn = Parameter_Names()
        self._reading_message_dict = pn.get_write_msg_dict()  
        self._reading_list = pn.get_reading_list()
        # Message of calling to read the data.
        
    def _make_dummy_inputs(self):
        """
        Make dummy data which match the message of reader is passed.
        """
        self._msg_and_input ={}
        for i, parameter in enumerate(self._reading_message_dict.values()):
            self._msg_and_input[parameter] = DataFrame([[4*1,4*i+1],[4*i+2,4*i+3]])
    
    def _del_dummy_inputs(self):
        del self._msg_and_input

    def _test_savedata(self):      
        '''
        Test data is saved correctry.
        '''
        
        with patch('src.transaction.pncombiner.CSVIO.write') as write_mock:
            
            pndata = PNDataWriter()
            pndata.execute()
            
            outputdata = [(k, v) for k, v in self._msg_and_input.items()]
            print(write_mock.call_args_list)
            self.assertTrue(write_mock.call_args_list == outputdata)
            
if __name__=='__main__':
    unittest.main()