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
from pandas import Series
from pandas.testing import assert_series_equal

# Original module
from context import src # path setting
from testing_utility.unittest_util import cls_startstop_msg as add_msg
from test_utility import Signletone_test_base

# Target class
from src.transaction.pncombiner import (PNCombiner,PNDataReader, PNDataWriter, 
                                        PNCalc, PNDataBase, PNPrmtrMng)

# interface
from src.interface.common import (Transaction, Reader, Writer)
from src.interface.calc_data import (PN_TF_Calc)

# tool class
from src.dataio.csvio import (CSVIO)

@add_msg
class TestCombinePN(unittest.TestCase):
    """
    Test for combining phase noise from each small data.
    """
    
    def test_interfacre(self):
        # Check using class has interface.
        sub_par_class_pairs = ((PNCombiner, Transaction),
                               (PNDataReader, Reader),
                               (PNDataWriter, Writer),
                               (PNCalc, PN_TF_Calc)
                               )
        for subc, parc in sub_par_class_pairs:
            self.assertTrue(issubclass(subc, parc))    
    
    def test_class_structure(self):
        """
        Test those classes is called in transaction class.
        """

        with patch('src.transaction.pncombiner.PNDataReader') as Reader_Mock,\
        patch('src.transaction.pncombiner.PNDataWriter') as Wruter_Mock,\
        patch('src.transaction.pncombiner.PNCalc') as PNCalc_Mock:
            
            # Make instance. 
            pnc = PNCombiner()
            pnc.execute()
            
            # Following class is called when above instance is made.
            Reader_Mock.assert_called()
            Wruter_Mock.assert_called()
            PNCalc_Mock.assert_called()
            
    def test_database_method(self):
        # Test interface has abstract method.
        method_names=('set_noise','get_noise', 'set_transfer_func',
                      'get_transfer_func', 'set_pn', 'get_pn')
        for  mth in method_names:
            self.assertTrue(callable(getattr(PNDataBase, mth)))
    
    def test_parameter_exist(self):
        """
        Parameter class testing.
        Parameter is property, is string that is greater than 0 length and 
        cannot be changed.
        """
        pnpm = PNPrmtrMng()
        attrnames = ['ref']
        for n in attrnames:
            prmtr = getattr(pnpm,n)
            self.assertTrue(isinstance(prmtr, str))
            self.assertTrue(0<len(prmtr))
            self.assertRaises(AttributeError, setattr, *(pnpm, n, 'a'))
            # Raise error if property value is changed.

class Test_database_as_singleton(Signletone_test_base, unittest.TestCase):
    """
    Test PNDataBase is singleton.
    """
    _cls = PNDataBase


class TestCombineRead(unittest.TestCase):
    """
    This is the test for reading data of transfer function, phasenoise dadta,
    noise data.
    """
    
    _reading_messages = ["Please input reference phase noise"]
    # Message of calling to read the data.
    
    def setUp(self):
        self.pndb = PNDataBase()
    
    def tearDown(self):
        del self.pndb
        """
        Kill PNDataBase instance to reflesh data on each test because 
        pndatabase is singleton.
        """
    def _make_dummy_inputs(self):
        """
        Make dummy data which match the message of reader is passed.
        """
        self._msg_and_input =[]
        for i, msg in enumerate(self._reading_messages):
            self._msg_and_input.append(
                    [msg, Series([[4*1,4*i+1],[4*i+2,4*i+3]])]
                    )
            
    def _input_side_effect_generator(self):
        """
        Generate the side_effect function which return the value match input
        message of reader.
        """
        
        self._make_dummy_inputs()
        def _side_effect(message):
            for msg, data in self._msg_and_input:
                if message == msg:
                    print((msg, data))
                    return data
        return _side_effect
    
    def test_readdata(self):
        self.assertTrue(issubclass(CSVIO, Reader))
        with patch('src.dataio.csvio.CSVIO.read') as read_data_mock:
            read_data_mock.side_effect =self._input_side_effect_generator()
            pndata = PNDataReader()
            pndata.read()
            #self.pndb.get_noise()

            

if __name__=='__main__':
    unittest.main()